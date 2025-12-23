"""MFA Database Models."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class MFASecret(Base):
    """Multi-Factor Authentication Secrets table."""

    __tablename__ = "mfa_secrets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    # TOTP secret (encrypted at rest)
    secret = Column(String(32), nullable=False)

    # Backup codes (hashed)
    backup_codes = Column(JSON, nullable=True)

    # Status
    is_active = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    activated_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)

    # Recovery info
    recovery_email = Column(String(255), nullable=True)
    recovery_phone = Column(String(20), nullable=True)

    # Relationship
    user = relationship("User", back_populates="mfa_secret")

class MFAAttempt(Base):
    """Track MFA verification attempts for security monitoring."""

    __tablename__ = "mfa_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Attempt details
    success = Column(Boolean, nullable=False)
    method = Column(String(20), nullable=False)  # 'totp', 'backup_code', 'sms'

    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Timestamp
    attempted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", back_populates="mfa_attempts")

class TrustedDevice(Base):
    """Remember trusted devices for 30 days."""

    __tablename__ = "trusted_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Device fingerprint
    device_fingerprint = Column(String(64), nullable=False, unique=True)
    device_name = Column(String(255), nullable=True)

    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    # Relationship
    user = relationship("User", back_populates="trusted_devices")
