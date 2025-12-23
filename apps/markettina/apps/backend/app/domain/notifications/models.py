"""
Notifications Models - Sistema notifiche admin.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.session import Base


class NotificationType(str, Enum):
    """Tipi di notifiche."""
    BOOKING = "booking"
    CONTACT = "contact"
    PROJECT = "project"
    SYSTEM = "system"
    SECURITY = "security"


class NotificationPriority(str, Enum):
    """Priorità notifiche."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """
    Notifiche sistema per admin.
    """
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    admin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("admin_users.id", ondelete="CASCADE")
    )

    # Tipo e priorità
    type: Mapped[str] = mapped_column(
        String(50),
        default=NotificationType.SYSTEM.value
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        default=NotificationPriority.MEDIUM.value
    )

    # Contenuto
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Link azione (opzionale)
    action_url: Mapped[str | None] = mapped_column(String(500))
    action_text: Mapped[str | None] = mapped_column(String(100))

    # Extra data (JSON flexible per dati extra)
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict)
    # Esempio: {"booking_id": 123, "contact_email": "test@example.com"}

    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
