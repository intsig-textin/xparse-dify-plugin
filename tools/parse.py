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
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

logger = logging.getLogger(__name__)

XPARSE_API_URL = "https://api.textin.com/api/xparse/pipeline"


@dataclass
class Credentials:
    x_ti_app_id: str
    x_ti_secret_code: str


class ParseTool(Tool):
    def _get_credentials(self) -> Credentials:
        """Get and validate credentials."""
        x_ti_app_id = self.runtime.credentials.get("x_ti_app_id")
        x_ti_secret_code = self.runtime.credentials.get("x_ti_secret_code")

        if not x_ti_app_id:
            logger.exception("Missing x_ti_app_id in credentials")
            raise ToolProviderCredentialValidationError(
                "Please input x-ti-app-id"
            )
        if not x_ti_secret_code:
            logger.exception("Missing x_ti_secret_code in credentials")
            raise ToolProviderCredentialValidationError(
                "Please input x-ti-secret-code"
            )

        return Credentials(
            x_ti_app_id=x_ti_app_id, x_ti_secret_code=x_ti_secret_code
        )

    def validate_api_credentials(self) -> None:
        """Validate API credentials by making a simple request."""
        credentials = self._get_credentials()
        try:
            headers = {
                "x-ti-app-id": credentials.x_ti_app_id,
                "x-ti-secret-code": credentials.x_ti_secret_code,
            }
            # Try to make a simple request to validate credentials
            # Note: xparse doesn't have a healthcheck endpoint, so we'll validate during actual usage
            # For now, just check that credentials are not empty
            if not credentials.x_ti_app_id or not credentials.x_ti_secret_code:
                raise ToolProviderCredentialValidationError(
                    "Invalid credentials"
                )
        except Exception as e:
            logger.exception(f"Validate API credentials failed. msg: {e}")
            raise ToolProviderCredentialValidationError(
                f"Validate API credentials failed. reason: {e}"
            )

    def _build_parse_config(self, tool_parameters: dict[str, Any]) -> dict[str, Any]:
        """Build parse configuration from tool parameters."""
        config: dict[str, Any] = {
            "provider": tool_parameters.get("provider", "textin"),
        }

        # Add optional parameters if provided
        if tool_parameters.get("pdf_pwd"):
            config["pdf_pwd"] = tool_parameters["pdf_pwd"]

        if tool_parameters.get("page_ranges"):
            config["page_ranges"] = tool_parameters["page_ranges"]

        # select 类型通常传 "0"/"1"，"0" 在 Python 中也是真值；这里用 is not None 更稳妥
        if tool_parameters.get("crop_dewarp") is not None:
            config["crop_dewarp"] = int(tool_parameters["crop_dewarp"])

        if tool_parameters.get("remove_watermark") is not None:
            config["remove_watermark"] = int(tool_parameters["remove_watermark"])

        if tool_parameters.get("get_page_image") is not None:
            config["get_page_image"] = tool_parameters["get_page_image"]

        if tool_parameters.get("get_sub_image") is not None:
            config["get_sub_image"] = tool_parameters["get_sub_image"]

        # Textin-specific parameters (only apply when provider is textin)
        provider = config.get("provider", "textin")
        if provider == "textin":
            if tool_parameters.get("parse_mode"):
                config["parse_mode"] = tool_parameters["parse_mode"]

            if tool_parameters.get("underline_level") is not None:
                config["underline_level"] = int(tool_parameters["underline_level"])

            if tool_parameters.get("apply_chart") is not None:
                config["apply_chart"] = int(tool_parameters["apply_chart"])

        # Image storage config (optional JSON string)
        if tool_parameters.get("image_storage_config"):
            try:
                image_storage_config = json.loads(
                    tool_parameters["image_storage_config"]
                )
                config["image_storage_config"] = image_storage_config
            except json.JSONDecodeError as e:
                logger.warning(
                    f"Invalid image_storage_config JSON, ignoring: {e}"
                )

        return config

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Invoke the parse tool to extract structured content from documents."""
        credentials = self._get_credentials()

        # Get file from parameters
        file = tool_parameters.get("file")
        if not file:
            raise ValueError("File parameter is required")

        # Build parse configuration
        parse_config = self._build_parse_config(tool_parameters)

        # Build stages configuration
        stages = [{"type": "parse", "config": parse_config}]

        # Prepare request
        headers = {
            "x-ti-app-id": credentials.x_ti_app_id,
            "x-ti-secret-code": credentials.x_ti_secret_code,
        }

        # OpenAPI: multipart/form-data，其中 stages 字段虽然是 string，但编码为 application/json
        # 实测如果不按 application/json 发送，可能出现 code=200 但 elements 为空。
        stages_json = json.dumps(stages, ensure_ascii=False)
        files = {
            "file": (file.filename, file.blob, file.mime_type),
            "stages": (None, stages_json, "application/json"),
        }

        try:
            # Call xparse Pipeline API
            response = requests.post(
                XPARSE_API_URL, headers=headers, files=files, timeout=300
            )
            response.raise_for_status()

            result = response.json()

            # Check for API errors
            if result.get("code") != 200:
                error_msg = result.get("message", "Unknown error")
                logger.error(f"xparse API error: {error_msg}")
                raise Exception(f"xparse API error: {error_msg}")

            # Extract elements from response
            elements = result.get("data", {}).get("elements", [])
            # Process elements and extract text/images
            text = ""
            images = []

            for element in elements:
                element_type = element.get("type", "")
                element_text = element.get("text", "")
                metadata = element.get("metadata", {})

                # Handle images
                if element_type == "Image" and metadata.get("image_base64"):
                    try:
                        base64_data = metadata["image_base64"]
                        image_bytes = base64.b64decode(base64_data)
                        mime_type = metadata.get("image_mime_type", "image/png")
                        extension = guess_extension(mime_type) or ".png"
                        image_name = f"image_{element.get('element_id', 'unknown')}{extension}"

                        # Upload image to Dify file system
                        file_res = self.session.file.upload(
                            element.get("element_id", image_name),
                            image_bytes,
                            mimetype=mime_type,
                        )
                        images.append(file_res)

                        # Update metadata
                        metadata["preview_url"] = file_res.preview_url
                        metadata["dify_file_id"] = file_res.id
                        metadata.pop("image_base64", None)

                        # Add image to text output
                        if file_res.preview_url:
                            text += f"![]({file_res.preview_url})\n"
                        else:
                            # If no preview URL, send as blob
                            yield self.create_blob_message(
                                image_bytes,
                                meta={"filename": image_name, "mime_type": mime_type},
                            )
                    except Exception as e:
                        logger.warning(f"Failed to process image: {e}")

                # Handle page images (if get_page_image is enabled)
                if metadata.get("page_image_url"):
                    # Page images are already URLs, no need to decode
                    text += f"![Page Image]({metadata['page_image_url']})\n"

                # Add element text
                if element_text:
                    text += f"\n{element_text}"

            # Return results
            yield self.create_text_message(text)
            yield self.create_variable_message("elements", elements)
            if images:
                yield self.create_variable_message("images", images)

        except requests.exceptions.RequestException as e:
            logger.exception(f"xparse API request failed. msg: {e}")
            raise Exception(f"xparse API request failed: {e}")
        except Exception as e:
            logger.exception(f"Parse request failed. msg: {e}")
            raise Exception(f"Parse request failed: {e}")
