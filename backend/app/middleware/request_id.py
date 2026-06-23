"""
Request ID middleware.
Generates or extracts a X-Request-ID header to trace requests across systems and logs.
"""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to assign a unique ID to every request."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check if client passed a request ID, otherwise generate one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Store in request state for easy access in logs/controllers
        request.state.request_id = request_id
        
        response = await call_next(request)
        
        # Include request ID in the response headers
        response.headers["X-Request-ID"] = request_id
        return response
