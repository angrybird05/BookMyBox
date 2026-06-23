"""Redis-backed rate limiting middleware for FastAPI."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings
from app.core.exceptions import RateLimitException
from app.database.redis import get_redis, RedisCache
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing sliding-window rate limits per client IP via Redis."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip rate limiting for OPTIONS preflight requests and internal routes
        path = request.url.path
        if request.method == "OPTIONS":
            return await call_next(request)
        if path in ("/health", "/docs", "/openapi.json", "/redoc") or path.startswith("/ws"):
            return await call_next(request)

        # Get client IP address
        client_ip = request.client.host if request.client else "unknown-ip"
        
        # Determine limits based on path type
        is_auth = path.startswith(f"{settings.API_PREFIX}/auth")
        limit = settings.RATE_LIMIT_AUTH_PER_MINUTE if is_auth else settings.RATE_LIMIT_PER_MINUTE
        window = 60  # 1 minute window

        try:
            redis_client = await get_redis()
            cache = RedisCache(redis_client)
            
            # Simple rate limiting key
            rate_limit_key = f"rate_limit:{client_ip}:{'auth' if is_auth else 'api'}"
            current_count = await cache.incr(rate_limit_key, ttl=window)
            
            if current_count > limit:
                logger.warning("rate_limit_exceeded", client_ip=client_ip, path=path, count=current_count, limit=limit)
                # Return JSONResponse directly — never raise from BaseHTTPMiddleware.
                # Raising bypasses CORSMiddleware and the browser sees no CORS headers.
                return JSONResponse(
                    status_code=429,
                    content={"success": False, "message": "Too many requests. Please slow down."},
                    headers={"Retry-After": str(window)},
                )

        except RateLimitException:
            return JSONResponse(
                status_code=429,
                content={"success": False, "message": "Too many requests. Please slow down."},
            )
        except Exception as exc:
            # Fail-safe: log error but allow request to continue if Redis is down
            logger.error("rate_limit_middleware_error", error=str(exc))
            
        return await call_next(request)
