"""
HTTP Request Logging Middleware.
Logs incoming requests and outgoing responses with performance metrics and tracking context.
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request information and execution time."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Get request ID if set by request_id middleware
        request_id = getattr(request.state, "request_id", "unknown")
        
        start_time = time.perf_counter()
        
        # Log request receipt
        logger.info(
            "http_request_started",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
            request_id=request_id,
        )
        
        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            
            # Log successful response
            logger.info(
                "http_request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(process_time * 1000, 2),
                request_id=request_id,
            )
            return response
            
        except Exception as exc:
            process_time = time.perf_counter() - start_time
            # Log uncaught exceptions but NEVER re-raise — returning a Response
            # ensures the outer CORSMiddleware can still attach CORS headers.
            # Re-raising causes BaseHTTPMiddleware to emit a bare 500 with no CORS headers.
            logger.exception(
                "http_request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=round(process_time * 1000, 2),
                request_id=request_id,
                error=str(exc),
            )
            # Manually add CORS headers — CORSMiddleware won't get a chance to
            # attach them when exceptions escape BaseHTTPMiddleware.
            origin = request.headers.get("origin", "")
            cors_headers = {}
            if origin:
                cors_headers["Access-Control-Allow-Origin"] = origin
                cors_headers["Access-Control-Allow-Credentials"] = "true"
                cors_headers["Vary"] = "Origin"
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Internal server error", "request_id": request_id},
                headers=cors_headers,
            )
