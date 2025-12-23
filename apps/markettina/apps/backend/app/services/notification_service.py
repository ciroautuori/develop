"""
Notification Service - Real-time notifications via WebSocket
"""
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Tipi di notifiche."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    BOOKING_CREATED = "booking_created"
    BOOKING_UPDATED = "booking_updated"
    BOOKING_CANCELLED = "booking_cancelled"
    MESSAGE_RECEIVED = "message_received"
    ADMIN_ALERT = "admin_alert"


class ConnectionManager:
    """Gestisce connessioni WebSocket attive."""

    def __init__(self):
        # user_id -> Set[WebSocket]
        self.active_connections: dict[str, set[WebSocket]] = {}
        # admin connections
        self.admin_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, user_id: str | None = None, is_admin: bool = False):
        """Connetti un client WebSocket."""
        await websocket.accept()

        if is_admin:
            self.admin_connections.add(websocket)
            logger.info(f"Admin connected. Total admins: {len(self.admin_connections)}")
        elif user_id:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)
            logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str | None = None, is_admin: bool = False):
        """Disconnetti un client WebSocket."""
        if is_admin and websocket in self.admin_connections:
            self.admin_connections.remove(websocket)
            logger.info(f"Admin disconnected. Total admins: {len(self.admin_connections)}")
        elif user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Invia messaggio a una specifica connessione."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def send_to_user(self, user_id: str, message: dict[str, Any]):
        """Invia messaggio a tutte le connessioni di un utente."""
        if user_id not in self.active_connections:
            logger.warning(f"User {user_id} not connected")
            return

        message_json = json.dumps(message)
        disconnected = set()

        for connection in self.active_connections[user_id]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                disconnected.add(connection)

        # Rimuovi connessioni morte
        for conn in disconnected:
            self.active_connections[user_id].discard(conn)

    async def broadcast_to_admins(self, message: dict[str, Any]):
        """Broadcast messaggio a tutti gli admin."""
        if not self.admin_connections:
            logger.warning("No admin connections available")
            return

        message_json = json.dumps(message)
        disconnected = set()

        for connection in self.admin_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error broadcasting to admin: {e}")
                disconnected.add(connection)

        # Rimuovi connessioni morte
        for conn in disconnected:
            self.admin_connections.discard(conn)

    async def broadcast(self, message: dict[str, Any]):
        """Broadcast messaggio a tutti gli utenti connessi."""
        message_json = json.dumps(message)

        for user_id, connections in self.active_connections.items():
            disconnected = set()
            for connection in connections:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id}: {e}")
                    disconnected.add(connection)

            # Rimuovi connessioni morte
            for conn in disconnected:
                connections.discard(conn)

    def get_connected_users(self) -> list[str]:
        """Ottieni lista user_id connessi."""
        return list(self.active_connections.keys())

    def get_connection_count(self, user_id: str | None = None) -> int:
        """Ottieni numero connessioni."""
        if user_id:
            return len(self.active_connections.get(user_id, set()))
        return sum(len(conns) for conns in self.active_connections.values())


class NotificationService:
    """Servizio per gestione notifiche real-time."""

    def __init__(self):
        self.manager = ConnectionManager()

    async def notify_user(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: dict[str, Any] | None = None
    ):
        """Invia notifica a un utente specifico."""
        notification = {
            "type": notification_type.value,
            "title": title,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.manager.send_to_user(user_id, notification)
        logger.info(f"Notification sent to user {user_id}: {notification_type.value}")

    async def notify_admins(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: dict[str, Any] | None = None
    ):
        """Invia notifica a tutti gli admin."""
        notification = {
            "type": notification_type.value,
            "title": title,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.manager.broadcast_to_admins(notification)
        logger.info(f"Admin notification sent: {notification_type.value}")

    async def broadcast_notification(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: dict[str, Any] | None = None
    ):
        """Broadcast notifica a tutti gli utenti."""
        notification = {
            "type": notification_type.value,
            "title": title,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.manager.broadcast(notification)
        logger.info(f"Broadcast notification sent: {notification_type.value}")

    # ========================================================================
    # NOTIFICATION HELPERS - Metodi specifici per eventi
    # ========================================================================

    async def notify_booking_created(
        self,
        user_id: str,
        booking_data: dict[str, Any]
    ):
        """Notifica creazione booking."""
        await self.notify_user(
            user_id=user_id,
            notification_type=NotificationType.BOOKING_CREATED,
            title="Prenotazione Confermata",
            message=f"La tua prenotazione per il {booking_data.get('scheduled_date')} è stata confermata",
            data=booking_data
        )

        # Notifica anche admin
        await self.notify_admins(
            notification_type=NotificationType.BOOKING_CREATED,
            title="Nuova Prenotazione",
            message=f"Nuova prenotazione da {booking_data.get('client_name')}",
            data=booking_data
        )

    async def notify_booking_updated(
        self,
        user_id: str,
        booking_data: dict[str, Any]
    ):
        """Notifica aggiornamento booking."""
        await self.notify_user(
            user_id=user_id,
            notification_type=NotificationType.BOOKING_UPDATED,
            title="Prenotazione Aggiornata",
            message="La tua prenotazione è stata modificata",
            data=booking_data
        )

    async def notify_booking_cancelled(
        self,
        user_id: str,
        booking_data: dict[str, Any]
    ):
        """Notifica cancellazione booking."""
        await self.notify_user(
            user_id=user_id,
            notification_type=NotificationType.BOOKING_CANCELLED,
            title="Prenotazione Cancellata",
            message="La tua prenotazione è stata cancellata",
            data=booking_data
        )

    async def notify_message_received(
        self,
        message_data: dict[str, Any]
    ):
        """Notifica nuovo messaggio (agli admin)."""
        await self.notify_admins(
            notification_type=NotificationType.MESSAGE_RECEIVED,
            title="Nuovo Messaggio",
            message=f"Nuovo messaggio da {message_data.get('name')}",
            data=message_data
        )

    async def notify_admin_alert(
        self,
        alert_type: str,
        message: str,
        data: dict[str, Any] | None = None
    ):
        """Notifica alert admin (errori, warning, etc)."""
        await self.notify_admins(
            notification_type=NotificationType.ADMIN_ALERT,
            title=f"Alert: {alert_type}",
            message=message,
            data=data
        )


# Singleton instance
notification_service = NotificationService()
