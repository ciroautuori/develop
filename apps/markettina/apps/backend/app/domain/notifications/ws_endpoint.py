"""
WebSocket Endpoint - Real-time notifications for admin.
"""

import json
import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.domain.auth.dependencies import get_current_admin_ws
from app.infrastructure.database.session import get_db

from .websocket import MessageType, manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/notifications")
async def websocket_notifications_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time notifications.
    
    Usage:
        ws://localhost:8000/api/v1/admin/ws/notifications?token=<JWT_TOKEN>
    """
    # Authenticate admin
    try:
        admin = await get_current_admin_ws(token, db)
    except Exception as e:
        logger.error(f"WebSocket auth failed: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Connect
    await manager.connect(websocket, admin.id)

    # Send welcome message
    await websocket.send_json({
        "type": "connected",
        "data": {
            "message": "Connected to notification stream",
            "admin_id": admin.id
        }
    })

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                message_type = message.get("type")

                # Handle ping
                if message_type == MessageType.PING:
                    await websocket.send_json({
                        "type": MessageType.PONG,
                        "timestamp": message.get("timestamp")
                    })

                # Handle other message types as needed
                else:
                    logger.info(f"Received message from admin {admin.id}: {message_type}")

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from admin {admin.id}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, admin.id)
        logger.info(f"Admin {admin.id} disconnected")

    except Exception as e:
        logger.error(f"WebSocket error for admin {admin.id}: {e}")
        manager.disconnect(websocket, admin.id)
