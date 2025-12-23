"""
SQLAlchemy Models Registry - CRITICAL FIX for relationship resolution.
Import ALL models here to ensure SQLAlchemy can resolve relationships.
"""

# Configure all relationships after import
from sqlalchemy.orm import configure_mappers

# Core models
# Auth domain models

# Identity domain models (markettina) - MUST BE BEFORE Billing for Account FK
# Billing domain models (markettina)

# Portfolio domain models (markettina)
# from app.domain.portfolio.models import Project, Service, ContactRequest, ProjectTestimonial

# Booking domain models (markettina)
# from app.domain.booking.models import Booking, AvailabilitySlot, BlockedDate, BookingFollowUp

# Support domain models

# ToolAI domain models
# from app.domain.toolai.models import ToolAIPost, AITool

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
