"""
Google Integration Models - Database models for Google settings
"""
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.infrastructure.database.session import Base


class AdminGoogleSettings(Base):
    """Store admin Google integration settings."""
    __tablename__ = "admin_google_settings"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, nullable=False, unique=True, index=True)

    # Google User Info
    google_user_id = Column(String(100), nullable=True, unique=True, index=True)  # Google OAuth user ID

    # GA4 Settings
    ga4_property_id = Column(String(100), nullable=True)
    ga4_account_id = Column(String(100), nullable=True)

    # GMB Settings
    gmb_account_id = Column(String(100), nullable=True)
    gmb_location_id = Column(String(100), nullable=True)

    # OAuth
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    scopes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
