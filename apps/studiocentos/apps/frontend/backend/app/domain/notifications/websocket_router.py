"""
WebSocket Router - Real-time notifications
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
import logging

from app.infrastructure.database.session import get_db
from app.services.notification_service import notification_service
from app.core.security import decode_token

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint per notifiche real-time utenti.
    
    Connessione:
    ```javascript
    const ws = new WebSocket(`wss://studiocentos.it/ws/notifications?token=${accessToken}`);
    ```
    """
    user_id = None
    
    try:
        # Valida token
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        # Connetti
        await notification_service.manager.connect(websocket, user_id=user_id)
        
        # Invia messaggio di benvenuto
        await notification_service.manager.send_personal_message(
            '{"type":"connected","message":"Connected to notification service"}',
            websocket
        )
        
        # Loop per mantenere connessione attiva
        while True:
            # Ricevi messaggi dal client (ping/pong)
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        if user_id:
            notification_service.manager.disconnect(websocket, user_id=user_id)


@router.websocket("/ws/admin/notifications")
async def websocket_admin_notifications(
    websocket: WebSocket,
    token: str = Query(..., description="JWT admin access token"),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint per notifiche real-time admin.
    
    Connessione:
    ```javascript
    const ws = new WebSocket(`wss://studiocentos.it/ws/admin/notifications?token=${adminToken}`);
    ```
    """
    try:
        # Valida token admin
        payload = decode_token(token)
        token_type = payload.get("type")
        
        if token_type != "admin":
            await websocket.close(code=1008, reason="Admin token required")
            return
        
        # Connetti come admin
        await notification_service.manager.connect(websocket, is_admin=True)
        
        # Invia messaggio di benvenuto
        await notification_service.manager.send_personal_message(
            '{"type":"connected","message":"Connected to admin notification service"}',
            websocket
        )
        
        # Loop per mantenere connessione attiva
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        logger.info("Admin disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for admin: {e}")
    finally:
        notification_service.manager.disconnect(websocket, is_admin=True)


@router.get("/api/v1/notifications/stats")
async def get_notification_stats():
    """
    Ottieni statistiche connessioni WebSocket.
    
    Returns:
        Dict con statistiche connessioni
    """
    return {
        "connected_users": notification_service.manager.get_connected_users(),
        "total_connections": notification_service.manager.get_connection_count(),
        "admin_connections": len(notification_service.manager.admin_connections),
    }
