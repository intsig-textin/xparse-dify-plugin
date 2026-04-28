import logging
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.parse import ParseTool

logger = logging.getLogger(__name__)


class XparseProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate xparse API credentials.
        If both credentials are empty, free API mode is used (no validation needed).
        If credentials are provided, validate them for paid API mode.
        """
        try:
            x_ti_app_id = credentials.get("x_ti_app_id", "")
            x_ti_secret_code = credentials.get("x_ti_secret_code", "")

            # Free API mode: no credentials needed
            if not x_ti_app_id and not x_ti_secret_code:
                return

            # Paid API mode: both credentials required
            if not x_ti_app_id or not x_ti_secret_code:
                raise ToolProviderCredentialValidationError(
                    "Both x-ti-app-id and x-ti-secret-code are required for paid API. "
                    "Leave both empty to use the free API."
                )

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
