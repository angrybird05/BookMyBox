"""WebSocket connection manager for real-time slot availability updates."""

from typing import Dict, List
from fastapi import WebSocket
from app.core.logging import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """Manages active WebSocket connections grouped by ground_id and date."""

    def __init__(self):
        # Maps "ground_id:date" -> List of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, key: str) -> None:
        """Accept connection and register under key."""
        await websocket.accept()
        if key not in self.active_connections:
            self.active_connections[key] = []
        self.active_connections[key].append(websocket)
        logger.info("websocket_connected", key=key, total_listeners=len(self.active_connections[key]))

    def disconnect(self, websocket: WebSocket, key: str) -> None:
        """Deregister a connection from a key."""
        if key in self.active_connections:
            if websocket in self.active_connections[key]:
                self.active_connections[key].remove(websocket)
            if not self.active_connections[key]:
                del self.active_connections[key]
        logger.info("websocket_disconnected", key=key)

    async def broadcast(self, key: str, message: dict) -> None:
        """Broadcast JSON message to all listeners of a key."""
        if key in self.active_connections:
            # Create a copy of list to prevent modification during iteration
            for connection in list(self.active_connections[key]):
                try:
                    await connection.send_json(message)
                except Exception as exc:
                    logger.warning("websocket_broadcast_failed_removing_stale", key=key, error=str(exc))
                    self.disconnect(connection, key)


# Global connection manager instance
slot_ws_manager = WebSocketManager()


async def broadcast_slot_updates(db, ground_id, target_date) -> None:
    """Retrieve current slots status and broadcast to WebSocket subscribers."""
    from sqlalchemy import select
    from app.models.slot import Slot
    
    stmt = (
        select(Slot)
        .where(Slot.ground_id == ground_id, Slot.date == target_date)
        .order_by(Slot.start_time.asc())
    )
    res = await db.execute(stmt)
    slots = res.scalars().all()
    
    slots_data = []
    for s in slots:
        slots_data.append({
            "id": str(s.id),
            "ground_id": str(s.ground_id),
            "date": s.date.isoformat(),
            "start_time": s.start_time.strftime("%H:%M"),
            "end_time": s.end_time.strftime("%H:%M"),
            "price": s.price,
            "status": s.status.value,
            "duration_minutes": s.duration_minutes
        })
    
    key = f"{str(ground_id)}:{target_date.isoformat()}"
    await slot_ws_manager.broadcast(key, {"event": "slot_updates", "slots": slots_data})

