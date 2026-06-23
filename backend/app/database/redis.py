"""
Redis connection manager for caching, sessions, and rate limiting.
Falls back to a robust in-memory mock if Redis is unreachable.
"""

from typing import Optional, Any
import json
import fnmatch
from datetime import datetime, timezone, timedelta
import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class InMemoryPipeline:
    """Mock pipeline supporting incr, expire, and execute."""

    def __init__(self, in_memory_redis: "InMemoryRedis"):
        self._redis = in_memory_redis
        self._commands = []

    def incr(self, key: str) -> None:
        self._commands.append(("incr", key, None))

    def expire(self, key: str, ttl: int) -> None:
        self._commands.append(("expire", key, ttl))

    async def execute(self) -> list[Any]:
        results = []
        for cmd, key, val in self._commands:
            if cmd == "incr":
                curr = await self._redis.get(key)
                if curr is None:
                    new_val = 1
                else:
                    try:
                        new_val = int(curr) + 1
                    except ValueError:
                        new_val = 1
                await self._redis.set(key, str(new_val))
                results.append(new_val)
            elif cmd == "expire":
                if key in self._redis._data:
                    self._redis._ttls[key] = datetime.now(timezone.utc) + timedelta(seconds=val)
        return results


class InMemoryRedis:
    """In-memory Redis mock client that mimics basic redis.Redis operations."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self._ttls: dict[str, datetime] = {}

    def _clean_expired(self) -> None:
        now = datetime.now(timezone.utc)
        expired = [k for k, exp in self._ttls.items() if now > exp]
        for k in expired:
            self._data.pop(k, None)
            self._ttls.pop(k, None)

    async def get(self, key: str) -> Optional[str]:
        self._clean_expired()
        return self._data.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> None:
        self._clean_expired()
        self._data[key] = str(value)
        if ex:
            self._ttls[key] = datetime.now(timezone.utc) + timedelta(seconds=ex)
        else:
            self._ttls.pop(key, None)

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)
        self._ttls.pop(key, None)

    async def scan_iter(self, match: str, count: int = 100):
        self._clean_expired()
        for key in list(self._data.keys()):
            if fnmatch.fnmatch(key, match):
                yield key

    async def exists(self, key: str) -> int:
        self._clean_expired()
        return 1 if key in self._data else 0

    def pipeline(self) -> InMemoryPipeline:
        return InMemoryPipeline(self)

    async def close(self) -> None:
        pass

    async def ping(self) -> bool:
        return True


# Global client instance (could be redis.Redis or InMemoryRedis)
_redis_pool: Optional[Any] = None
_using_mock_redis: bool = False


async def get_redis() -> Any:
    """Get the shared async Redis connection, falling back to InMemoryRedis if offline."""
    global _redis_pool, _using_mock_redis
    if _redis_pool is None:
        try:
            # Attempt to connect to real Redis
            real_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=10,
                socket_connect_timeout=2,
                socket_timeout=2,
                socket_keepalive=True,
                retry_on_timeout=False,
            )
            # Ping to verify actual connection
            await real_client.ping()
            _redis_pool = real_client
            _using_mock_redis = False
            logger.info("redis_connected_successfully", url=settings.REDIS_URL)
        except (ConnectionError, TimeoutError, OSError) as exc:
            logger.warning("redis_offline_falling_back_to_in_memory", error=str(exc))
            _redis_pool = InMemoryRedis()
            _using_mock_redis = True
    return _redis_pool


async def close_redis() -> None:
    """Close the Redis connection pool on shutdown."""
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.close()
        _redis_pool = None


async def init_redis_pool() -> Any:
    """Initialize and return the global Redis connection pool."""
    return await get_redis()


async def close_redis_pool() -> None:
    """Alias to close the Redis pool on shutdown."""
    await close_redis()


class RedisCache:
    """High-level caching operations backed by Redis or InMemoryRedis fallback."""

    def __init__(self, redis_client: Any):
        self._redis = redis_client
        self._default_ttl = settings.REDIS_CACHE_TTL

    async def get(self, key: str) -> Optional[str]:
        """Get a cached value by key."""
        return await self._redis.get(key)

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set a cached value with TTL."""
        await self._redis.set(key, value, ex=ttl or self._default_ttl)

    async def delete(self, key: str) -> None:
        """Delete a cached value."""
        await self._redis.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching a pattern."""
        async for key in self._redis.scan_iter(match=pattern, count=100):
            await self._redis.delete(key)

    async def incr(self, key: str, ttl: Optional[int] = None) -> int:
        """Increment a counter. Sets TTL on first call."""
        pipe = self._redis.pipeline()
        pipe.incr(key)
        if ttl:
            pipe.expire(key, ttl)
        results = await pipe.execute()
        return results[0]

    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        return bool(await self._redis.exists(key))

