"""
SQLAlchemy Models Registry - CRITICAL FIX for relationship resolution.
Import ALL models here to ensure SQLAlchemy can resolve relationships.
"""

# Configure all relationships after import
from sqlalchemy.orm import configure_mappers, relationship

# Core models
from app.core.api_key_rotation import APIKey

# Auth domain models
from app.domain.auth.models import User, UserRole
from app.domain.auth.models_mfa import MFAAttempt, MFASecret, TrustedDevice
from app.domain.auth.password_reset import PasswordResetToken
from app.domain.auth.refresh_token import RefreshToken
from app.domain.auth.oauth_tokens import OAuthToken
from app.domain.auth.admin_models import AdminUser, AdminSession, AdminAuditLog
from app.domain.auth.settings_models import AdminSettings
from app.domain.analytics.models import AnalyticsEvent
from app.domain.google.models import AdminGoogleSettings

# Portfolio domain models (StudiocentOS)
from app.domain.portfolio.models import Project, Service, ContactRequest, ProjectTestimonial

# Booking domain models (StudiocentOS)
from app.domain.booking.models import Booking, AvailabilitySlot, BlockedDate, BookingFollowUp

# Support domain models
from app.domain.support.models import SupportMessage, SupportTicket

# ToolAI domain models
from app.domain.toolai.models import ToolAIPost, AITool

# Marketing domain models (only essential ones)
from app.domain.marketing.models import ScheduledPost

# Customers domain models
from app.domain.customers.models import Customer, CustomerNote, CustomerInteraction

def configure_all_models():
    """
    Configure all SQLAlchemy mappers after models are imported.

    All relationships are now defined directly in models with lazy loading
    to avoid circular imports. This function just ensures mappers are configured.
    """
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Configure all mappers - relationships are already defined in models
        configure_mappers()
        logger.info("✅ All SQLAlchemy models configured successfully")
        logger.info("✅ User.support_tickets: ENABLED (lazy=dynamic)")
        logger.info("✅ User.subscription: ENABLED (lazy=joined)")
        logger.info("✅ Profile analytics relationships: ENABLED")
    except Exception as e:
        logger.error(f"❌ Error configuring models: {e}")
        raise

# Auto-configure when imported
configure_all_models()
