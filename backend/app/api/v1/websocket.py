"""WebSocket routes for real-time updates."""

from datetime import date
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket import slot_ws_manager
from app.services.slot import SlotService
from app.database.session import get_db_context
from app.schemas.slot import SlotResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSockets"])


@router.websocket("/slots/{ground_id}/{date_str}")
async def slot_websocket_endpoint(websocket: WebSocket, ground_id: uuid.UUID, date_str: str):
    """WebSocket connection handler for a specific ground date."""
    key = f"{ground_id}:{date_str}"
    await slot_ws_manager.connect(websocket, key)
    
    try:
        # Send initial slot status list immediately upon connection
        target_date = date.fromisoformat(date_str)
        async with get_db_context() as db:
            slot_service = SlotService(db)
            slots = await slot_service.get_slots_for_date(ground_id, target_date)
            # Serialize
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
            await websocket.send_json({"event": "initial_state", "slots": slots_data})
            
        # Keep connection open
        while True:
            # We don't expect messages from clients, but we receive text to detect disconnection
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        slot_ws_manager.disconnect(websocket, key)
    except Exception as exc:
        logger.error("websocket_handler_error", key=key, error=str(exc))
        slot_ws_manager.disconnect(websocket, key)
