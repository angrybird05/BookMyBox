"""Pytest configuration and global mock fixtures."""

import asyncio
from unittest.mock import AsyncMock, MagicMock
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(autouse=True)
def setup_event_loop():
    """Ensure there is a valid running event loop for each test case."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    yield loop


@pytest.fixture
def mock_db() -> MagicMock:
    """Fixture to mock AsyncSession."""
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest_asyncio.fixture
async def mock_redis(monkeypatch):
    """Fixture to mock Redis connection client."""
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=None)
    mock_client.set = AsyncMock()
    mock_client.delete = AsyncMock()

    async def get_redis_mock():
        return mock_client

    monkeypatch.setattr("app.services.booking.get_redis", get_redis_mock)
    return mock_client


@pytest.fixture(scope="session", autouse=True)
def configure_celery():
    """Configure Celery to run tasks eagerly (synchronously) during tests."""
    from app.workers.celery_app import celery_app
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )

