"""
Request ID middleware.
Generates or extracts a X-Request-ID header to trace requests across systems and logs.
Pure ASGI middleware — exceptions flow through naturally so outer middleware (e.g. CORS)
always gets to process the final response.
"""

import uuid
from starlette.types import ASGIApp, Receive, Scope, Send


class RequestIdMiddleware:
    """ASGI middleware to assign a unique ID to every request."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        request_id = headers.get(b"x-request-id", str(uuid.uuid4()).encode()).decode()

        # Store in ASGI scope so downstream middleware / routes can access it.
        scope["state"] = getattr(scope, "state", {})
        scope["state"]["request_id"] = request_id

        # Wrap send to inject X-Request-ID into the response.
        async def send_with_request_id(message: dict) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode()))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_request_id)
