import base64
import json
import logging
from collections.abc import Generator
from dataclasses import dataclass
from mimetypes import guess_extension
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

logger = logging.getLogger(__name__)

PAID_API_URL = "https://api.textin.com/api/v1/xparse/parse/sync"
FREE_API_URL = "https://api.textin.com/api/v1/agent/parse/sync"


@dataclass
class Credentials:
    x_ti_app_id: str
    x_ti_secret_code: str
    is_free_api: bool


class ParseTool(Tool):
    def _get_credentials(self, tool_parameters: dict[str, Any]) -> Credentials:
        """Get credentials from tool parameters. Returns free API mode if empty."""
        x_ti_app_id = tool_parameters.get("x_ti_app_id", "")
        x_ti_secret_code = tool_parameters.get("x_ti_secret_code", "")

        if x_ti_app_id and x_ti_secret_code:
            return Credentials(
                x_ti_app_id=x_ti_app_id,
                x_ti_secret_code=x_ti_secret_code,
                is_free_api=False,
            )

        return Credentials(
            x_ti_app_id="",
            x_ti_secret_code="",
            is_free_api=True,
        )

    def _build_parse_config(self, tool_parameters: dict[str, Any]) -> dict[str, Any]:
        """Build parse configuration from tool parameters for Parse Sync API v1.3.0."""
        config: dict[str, Any] = {}

        # document section (optional)
        if tool_parameters.get("pdf_pwd"):
            config["document"] = {"password": tool_parameters["pdf_pwd"]}

        # capabilities section (always present)
        config["capabilities"] = {
            "include_hierarchy": tool_parameters.get("include_hierarchy", True),
            "include_inline_objects": tool_parameters.get("include_inline_objects", False),
            "include_char_details": tool_parameters.get("include_char_details", False),
            "include_image_data": tool_parameters.get("include_image_data", False),
            "include_table_structure": tool_parameters.get("include_table_structure", False),
            "pages": tool_parameters.get("pages", False),
            "title_tree": tool_parameters.get("title_tree", False),
            "table_view": tool_parameters.get("table_view", "html"),
        }

        # scope section (optional)
        if tool_parameters.get("page_ranges"):
            config["scope"] = {"page_range": tool_parameters["page_ranges"]}

        return config

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Invoke the parse tool to extract structured content from documents."""
        credentials = self._get_credentials(tool_parameters)

        # Get file from parameters
        file = tool_parameters.get("file")
        if not file:
            raise ValueError("File parameter is required")

        # Build parse configuration
        parse_config = self._build_parse_config(tool_parameters)

        # Select API URL and headers based on credentials
        if credentials.is_free_api:
            api_url = FREE_API_URL
            headers = {"X-From": "dify"}
        else:
            api_url = PAID_API_URL
            headers = {
                "x-ti-app-id": credentials.x_ti_app_id,
                "x-ti-secret-code": credentials.x_ti_secret_code,
                "X-From": "dify",
            }

        # Prepare multipart/form-data with config as JSON
        config_json = json.dumps(parse_config, ensure_ascii=False)
        files = {
            "file": (file.filename, file.blob, file.mime_type),
            "config": (None, config_json, "application/json"),
        }

        try:
            # Call xparse Parse Sync API
            response = requests.post(
                api_url, headers=headers, files=files, timeout=300
            )
            response.raise_for_status()

            result = response.json()

            # Check for API errors
            if result.get("code") != 200:
                error_msg = result.get("message", "Unknown error")
                logger.error(f"xparse API error: {error_msg}")
                raise Exception(f"xparse API error: {error_msg}")

            # Extract data from response
            data = result.get("data", {})
            markdown = data.get("markdown", "")
            elements = data.get("elements", [])
            pages = data.get("pages", [])
            title_tree = data.get("title_tree", [])

            # Process images if include_image_data is enabled
            images = []
            for element in elements:
                element_type = element.get("type", "")
                image_data = element.get("image_data", {})

                # Handle images with base64 data
                if element_type == "Image" and image_data.get("base64"):
                    try:
                        base64_data = image_data["base64"]
                        image_bytes = base64.b64decode(base64_data)
                        mime_type = image_data.get("mime_type", "image/png")
                        extension = guess_extension(mime_type) or ".png"
                        image_name = f"image_{element.get('element_id', 'unknown')}{extension}"

                        # Upload image to Dify file system
                        file_res = self.session.file.upload(
                            element.get("element_id", image_name),
                            image_bytes,
                            mimetype=mime_type,
                        )
                        images.append(file_res)

                        # Update image_data with preview info
                        image_data["preview_url"] = file_res.preview_url
                        image_data["dify_file_id"] = file_res.id
                        # Remove base64 to reduce response size
                        del image_data["base64"]
                    except Exception as e:
                        logger.warning(f"Failed to process image: {e}")

            # Return results
            yield self.create_text_message(markdown)
            yield self.create_variable_message("elements", elements)
            if pages:
                yield self.create_variable_message("pages", pages)
            if title_tree:
                yield self.create_variable_message("title_tree", title_tree)
            if images:
                yield self.create_variable_message("images", images)

        except requests.exceptions.RequestException as e:
            logger.exception(f"xparse API request failed. msg: {e}")
            raise Exception(f"xparse API request failed: {e}")
        except Exception as e:
            logger.exception(f"Parse request failed. msg: {e}")
            raise Exception(f"Parse request failed: {e}")
