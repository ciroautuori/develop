"""Service Constants (Enrichment, Email, Analytics)"""

from typing import Final


class EnrichmentConstants:
    """Data enrichment configuration."""

    # Cache TTL (seconds)
    COMPANY_ENRICHMENT_CACHE_TTL: Final[int] = 604800  # 7 days
    UNIVERSITY_ENRICHMENT_CACHE_TTL: Final[int] = 2592000  # 30 days
    SKILL_ICON_CACHE_TTL: Final[int] = 86400  # 24 hours

    # API timeouts (seconds)
    ENRICHMENT_API_TIMEOUT: Final[int] = 5
    MAX_RETRY_ATTEMPTS: Final[int] = 2


class EmailConstants:
    """Email-related constants."""

    # Email types
    EMAIL_TYPE_VERIFICATION: Final[str] = "verification"
    EMAIL_TYPE_PASSWORD_RESET: Final[str] = "password_reset"
    EMAIL_TYPE_WELCOME: Final[str] = "welcome"
    EMAIL_TYPE_TRIAL_EXPIRY: Final[str] = "trial_expiry"
    EMAIL_TYPE_SUBSCRIPTION_UPDATE: Final[str] = "subscription_update"

    # Email limits
    MAX_EMAIL_LENGTH: Final[int] = 254


class AnalyticsConstants:
    """Analytics and tracking constants."""

    # Session duration (minutes)
    SESSION_TIMEOUT_MINUTES: Final[int] = 30
    
    # Event types
    EVENT_PAGE_VIEW: Final[str] = "page_view"
    EVENT_CV_DOWNLOAD: Final[str] = "cv_download"
    EVENT_CONTACT_FORM: Final[str] = "contact_form"
