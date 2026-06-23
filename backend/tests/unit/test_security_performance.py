"""Unit tests for rate limit, security headers middlewares, and caching."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from starlette.datastructures import Headers
from fastapi import Request
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.core.exceptions import RateLimitException


@pytest.mark.asyncio
async def test_security_headers_middleware():
    """Test that SecurityHeadersMiddleware adds the expected security headers."""
    middleware = SecurityHeadersMiddleware(MagicMock())
    
    # Mock request and next call
    req = MagicMock(spec=Request)
    req.url = MagicMock()
    req.url.path = "/api/v1/grounds"
    
    res = MagicMock()
    res.headers = {}
    
    async def call_next(request):
        return res

    result = await middleware.dispatch(req, call_next)
    
    # Verify expected defense headers are present
    assert result.headers["X-Frame-Options"] == "DENY"
    assert result.headers["X-Content-Type-Options"] == "nosniff"
    assert result.headers["X-XSS-Protection"] == "1; mode=block"
    assert "Strict-Transport-Security" in result.headers
    assert "Referrer-Policy" in result.headers
    assert "Content-Security-Policy" in result.headers


@pytest.mark.asyncio
@patch("app.middleware.rate_limit.get_redis")
async def test_rate_limit_middleware_success(mock_get_redis):
    """Test rate limit middleware passes through when below threshold."""
    # Mock Redis Cache incr
    mock_redis_client = MagicMock()
    mock_get_redis.return_value = mock_redis_client
    
    # We mock RedisCache.incr via monkeypatch or direct mock
    mock_incr = AsyncMock(return_value=5)  # below default limit (60)
    
    with patch("app.middleware.rate_limit.RedisCache.incr", mock_incr):
        middleware = RateLimitMiddleware(MagicMock())
        req = MagicMock(spec=Request)
        req.url = MagicMock()
        req.url.path = "/api/v1/grounds"
        req.client = MagicMock()
        req.client.host = "127.0.0.1"
        
        res = MagicMock()
        async def call_next(request):
            return res

        result = await middleware.dispatch(req, call_next)
        assert result == res
        mock_incr.assert_called_once()


@pytest.mark.asyncio
@patch("app.middleware.rate_limit.get_redis")
async def test_rate_limit_middleware_exceeded(mock_get_redis):
    """Test rate limit middleware raises RateLimitException when limit exceeded."""
    mock_redis_client = MagicMock()
    mock_get_redis.return_value = mock_redis_client
    
    mock_incr = AsyncMock(return_value=100)  # above default limit (60)
    
    with patch("app.middleware.rate_limit.RedisCache.incr", mock_incr):
        middleware = RateLimitMiddleware(MagicMock())
        req = MagicMock(spec=Request)
        req.url = MagicMock()
        req.url.path = "/api/v1/grounds"
        req.client = MagicMock()
        req.client.host = "127.0.0.1"
        
        async def call_next(request):
            return MagicMock()

        with pytest.raises(RateLimitException):
            await middleware.dispatch(req, call_next)
