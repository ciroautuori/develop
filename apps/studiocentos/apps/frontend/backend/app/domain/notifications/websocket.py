"""
WebSocket Manager - Real-time notifications for admin.
FastAPI WebSocket integration.
"""

from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket connection manager for real-time notifications.
    
    Manages active connections per admin user.
    """
    
    def __init__(self):
        # admin_id -> set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, admin_id: int):
        """Accept and register new WebSocket connection."""
        await websocket.accept()
        
        if admin_id not in self.active_connections:
            self.active_connections[admin_id] = set()
        
        self.active_connections[admin_id].add(websocket)
        logger.info(f"Admin {admin_id} connected. Total connections: {len(self.active_connections[admin_id])}")
    
    def disconnect(self, websocket: WebSocket, admin_id: int):
        """Remove WebSocket connection."""
        if admin_id in self.active_connections:
            self.active_connections[admin_id].discard(websocket)
            
            # Clean up empty sets
            if not self.active_connections[admin_id]:
                del self.active_connections[admin_id]
            
            logger.info(f"Admin {admin_id} disconnected")
    
    async def send_personal_message(self, message: dict, admin_id: int):
        """Send message to specific admin (all their connections)."""
        if admin_id not in self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = set()
        
        for websocket in self.active_connections[admin_id]:
            try:
                await websocket.send_text(message_json)
            except WebSocketDisconnect:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"Error sending message to admin {admin_id}: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            self.disconnect(ws, admin_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected admins."""
        message_json = json.dumps(message)
        
        for admin_id, connections in list(self.active_connections.items()):
            disconnected = set()
            
            for websocket in connections:
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error broadcasting to admin {admin_id}: {e}")
                    disconnected.add(websocket)
            
            for ws in disconnected:
                self.disconnect(ws, admin_id)
    
    def get_connected_admins(self) -> Set[int]:
        """Get set of currently connected admin IDs."""
        return set(self.active_connections.keys())
    
    def is_admin_online(self, admin_id: int) -> bool:
        """Check if admin has any active connections."""
        return admin_id in self.active_connections and len(self.active_connections[admin_id]) > 0


# Global connection manager instance
manager = ConnectionManager()


# Message types
class MessageType:
    """WebSocket message types."""
    NOTIFICATION = "notification"
    BOOKING_CREATED = "booking_created"
    CONTACT_REQUEST = "contact_request"
    PROJECT_UPDATED = "project_updated"
    SYSTEM_ALERT = "system_alert"
    PING = "ping"
    PONG = "pong"


async def send_notification_ws(admin_id: int, notification_data: dict):
    """
    Send notification via WebSocket.
    
    Args:
        admin_id: Admin user ID
        notification_data: Notification data (id, title, message, type, etc.)
    """
    message = {
        "type": MessageType.NOTIFICATION,
        "data": notification_data
    }
    await manager.send_personal_message(message, admin_id)


async def broadcast_system_alert(alert_message: str, severity: str = "info"):
    """
    Broadcast system alert to all connected admins.
    
    Args:
        alert_message: Alert message
        severity: Alert severity (info, warning, error)
    """
    message = {
        "type": MessageType.SYSTEM_ALERT,
        "data": {
            "message": alert_message,
            "severity": severity,
            "timestamp": "now"  # Will be replaced with actual timestamp
        }
    }
    await manager.broadcast(message)
