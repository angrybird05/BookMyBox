"""Unit tests for WebSocket slot updates manager."""

from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest
from fastapi import WebSocket
from app.core.websocket import WebSocketManager


@pytest.mark.asyncio
async def test_websocket_manager_lifecycle():
    """Test connecting, disconnecting, and broadcasting via WebSocketManager."""
    manager = WebSocketManager()
    ws_mock1 = MagicMock(spec=WebSocket)
    ws_mock1.accept = AsyncMock()
    ws_mock1.send_json = AsyncMock()

    ws_mock2 = MagicMock(spec=WebSocket)
    ws_mock2.accept = AsyncMock()
    ws_mock2.send_json = AsyncMock()

    key = "test_ground:2026-06-19"

    # 1. Connect first client
    await manager.connect(ws_mock1, key)
    assert key in manager.active_connections
    assert len(manager.active_connections[key]) == 1
    ws_mock1.accept.assert_called_once()

    # 2. Connect second client
    await manager.connect(ws_mock2, key)
    assert len(manager.active_connections[key]) == 2

    # 3. Broadcast message
    msg = {"status": "updated"}
    await manager.broadcast(key, msg)
    ws_mock1.send_json.assert_called_once_with(msg)
    ws_mock2.send_json.assert_called_once_with(msg)

    # 4. Disconnect one client
    manager.disconnect(ws_mock1, key)
    assert len(manager.active_connections[key]) == 1
    assert ws_mock2 in manager.active_connections[key]

    # 5. Disconnect second client (cleans up key)
    manager.disconnect(ws_mock2, key)
    assert key not in manager.active_connections
