"""
Admin Settings Models - Configurazioni e preferenze admin.
"""

from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.session import Base


class NotificationChannel(str, Enum):
    """Canali notifica."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class AdminSettings(Base):
    """
    Impostazioni admin - Profilo e preferenze.
    """
    __tablename__ = "admin_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    admin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("admin_users.id", ondelete="CASCADE"),
        unique=True
    )

    # Profile settings
    display_name: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Rome")
    language: Mapped[str] = mapped_column(String(10), default="it")

    # Notification preferences
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    push_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    sms_notifications: Mapped[bool] = mapped_column(Boolean, default=False)

    # Notification types
    notify_new_booking: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_new_contact: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_project_update: Mapped[bool] = mapped_column(Boolean, default=False)
    notify_system_alert: Mapped[bool] = mapped_column(Boolean, default=True)

    # UI preferences
    theme: Mapped[str] = mapped_column(String(20), default="dark")  # dark, light, auto
    sidebar_collapsed: Mapped[bool] = mapped_column(Boolean, default=False)
    items_per_page: Mapped[int] = mapped_column(Integer, default=20)

    # Security settings
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_method: Mapped[Optional[str]] = mapped_column(String(20))  # totp, sms
    session_timeout_minutes: Mapped[int] = mapped_column(Integer, default=120)

    # Custom preferences (JSON flexible)
    custom_preferences: Mapped[dict] = mapped_column(JSON, default=dict)

    # Integration toggles
    meta_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    stripe_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationship
    admin: Mapped["AdminUser"] = relationship("AdminUser", back_populates="settings")


class AdminPasswordHistory(Base):
    """
    Storico password admin - Per prevenire riutilizzo.
    """
    __tablename__ = "admin_password_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    admin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("admin_users.id", ondelete="CASCADE")
    )

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
