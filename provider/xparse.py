import logging
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.parse import ParseTool

logger = logging.getLogger(__name__)


class XparseProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate xparse API credentials by making a test request.
        """
        try:
            x_ti_app_id = credentials.get("x_ti_app_id")
            x_ti_secret_code = credentials.get("x_ti_secret_code")

            if not x_ti_app_id:
                raise ToolProviderCredentialValidationError(
                    "Please input x-ti-app-id"
                )
            if not x_ti_secret_code:
                raise ToolProviderCredentialValidationError(
                    "Please input x-ti-secret-code"
                )

            # Validate credentials by creating a tool instance and checking API access
            instance = ParseTool.from_credentials(credentials)
            assert isinstance(instance, ParseTool)
            instance.validate_api_credentials()
        except ToolProviderCredentialValidationError:
            raise
        except Exception as e:
            logger.exception(f"Validate credentials failed. msg: {e}")
            raise ToolProviderCredentialValidationError(
                f"Validate credentials failed. reason: {e}"
            )