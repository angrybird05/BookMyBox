"""Redis-backed rate limiting middleware for FastAPI.
Pure ASGI middleware — exceptions flow through naturally so outer middleware (e.g. CORS)
always gets to process the final response.
"""

from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import RateLimitException
from app.core.logging import get_logger
from app.database.redis import get_redis, RedisCache

settings = get_settings()
logger = get_logger(__name__)


class RateLimitMiddleware:
    """ASGI middleware enforcing sliding-window rate limits per client IP via Redis."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope["path"]
        if scope["method"] == "OPTIONS":
            await self.app(scope, receive, send)
            return
        if path in ("/health", "/docs", "/openapi.json", "/redoc") or path.startswith("/ws"):
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        client_ip = client[0] if client else "unknown-ip"

        is_auth = path.startswith(f"{settings.API_PREFIX}/auth")
        limit = settings.RATE_LIMIT_AUTH_PER_MINUTE if is_auth else settings.RATE_LIMIT_PER_MINUTE
        window = 60  # 1 minute window

        try:
            redis_client = await get_redis()
            cache = RedisCache(redis_client)

            rate_limit_key = f"rate_limit:{client_ip}:{'auth' if is_auth else 'api'}"
            current_count = await cache.incr(rate_limit_key, ttl=window)

            if current_count > limit:
                logger.warning(
                    "rate_limit_exceeded",
                    client_ip=client_ip,
                    path=path,
                    count=current_count,
                    limit=limit,
                )
                response = JSONResponse(
                    status_code=429,
                    content={"success": False, "message": "Too many requests. Please slow down."},
                    headers={"Retry-After": str(window)},
                )
                await response(scope, receive, send)
                return

        except RateLimitException:
            response = JSONResponse(
                status_code=429,
                content={"success": False, "message": "Too many requests. Please slow down."},
            )
            await response(scope, receive, send)
            return
        except Exception as exc:
            logger.error("rate_limit_middleware_error", error=str(exc))

        await self.app(scope, receive, send)
