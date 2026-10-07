import logging
from pathlib import Path

from google.adk.cli.fast_api import get_fast_api_app
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)

class CaptureCompletedResponseCancelScopeError:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        response_completed = False

        async def capture_send(message: Message) -> None:
            nonlocal response_completed
            await send(message)
            if (
                message["type"] == "http.response.body"
                and not message.get("more_body", False)
            ):
                response_completed = True

        try:
            await self.app(scope, receive, capture_send)
        except RuntimeError as error:
            message = str(error).lower()
            is_cancel_scope_mismatch = "cancel scope" in message and (
                "current task" in message or "different task" in message
            )
            if scope["type"] == "http" and response_completed and is_cancel_scope_mismatch:
                logger.debug(
                    "Captured AnyIO cancel-scope mismatch after the HTTP response "
                    "was sent."
                )
                return
            raise


agents_dir = Path(__file__).resolve().parent.parent
app = CaptureCompletedResponseCancelScopeError(
    get_fast_api_app(agents_dir=str(agents_dir), web=True)
)