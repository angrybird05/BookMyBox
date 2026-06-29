"""
HTTP Request Logging Middleware.
Logs incoming requests and outgoing responses with performance metrics and tracking context.
Pure ASGI middleware — exceptions flow through naturally so outer middleware (e.g. CORS)
always gets to process the final response.
"""

import time
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware:
    """ASGI middleware to log request information and execution time."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        state = getattr(scope, "state", {})
        request_id = state.get("request_id", "unknown")

        client = scope.get("client")
        client_ip = f"{client[0]}:{client[1]}" if client else "unknown"
        method = scope["method"]
        path = scope["path"]

        logger.info(
            "http_request_started",
            method=method,
            path=path,
            client_ip=client_ip,
            request_id=request_id,
        )

        start_time = time.perf_counter()
        status_code = 500  # default if something goes wrong before response

        async def send_with_logging(message: dict) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 500)
            await send(message)

        try:
            await self.app(scope, receive, send_with_logging)
        except Exception as exc:
            process_time = time.perf_counter() - start_time
            logger.exception(
                "http_request_failed",
                method=method,
                path=path,
                duration_ms=round(process_time * 1000, 2),
                request_id=request_id,
                error=str(exc),
            )
            raise  # Let exception propagate so outer middleware can handle it

        process_time = time.perf_counter() - start_time
        logger.info(
            "http_request_completed",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round(process_time * 1000, 2),
            request_id=request_id,
        )
