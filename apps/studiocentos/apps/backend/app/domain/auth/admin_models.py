"""
Admin User Models
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .settings_models import AdminSettings
from sqlalchemy import String, Boolean, DateTime, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.session import Base


class AdminUser(Base):
    """
    Amministratore sistema - credenziali separate dagli utenti normali.
    """
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Credenziali
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profilo
    full_name: Mapped[Optional[str]] = mapped_column(String(255))

    # 2FA
    is_2fa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    totp_secret: Mapped[Optional[str]] = mapped_column(String(32))
    backup_codes: Mapped[Optional[str]] = mapped_column(Text)  # JSON array encrypted

    # Password reset
    reset_token: Mapped[Optional[str]] = mapped_column(String(255))
    reset_token_expires: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Setup iniziale
    is_setup_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    setup_token: Mapped[Optional[str]] = mapped_column(String(255))

    # Security
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_password_change: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    settings: Mapped[Optional["AdminSettings"]] = relationship(
        "AdminSettings",
        back_populates="admin",
        uselist=False,
        lazy="joined"
    )


class AdminSession(Base):
    """
    Sessioni admin attive per tracking e revoca.
    """
    __tablename__ = "admin_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    admin_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Token info
    access_token_jti: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    refresh_token_jti: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # Session info
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)

    # Expiry
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Status
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AdminAuditLog(Base):
    """
    Log azioni amministrative per audit trail.
    """
    __tablename__ = "admin_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    admin_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Action info
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100))
    resource_id: Mapped[Optional[str]] = mapped_column(String(255))

    # Details
    details: Mapped[Optional[str]] = mapped_column(Text)  # JSON

    # Request info
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)

    # Status
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
