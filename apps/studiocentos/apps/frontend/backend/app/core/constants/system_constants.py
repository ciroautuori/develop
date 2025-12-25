"""System-wide Constants (Cache, Rate Limiting, Pagination)"""

from typing import Final


class CacheConstants:
    """Cache TTL and keys."""

    # TTL (seconds)
    PORTFOLIO_CACHE_TTL: Final[int] = 300  # 5 minutes
    USER_PROFILE_CACHE_TTL: Final[int] = 600  # 10 minutes
    PLAN_CACHE_TTL: Final[int] = 3600  # 1 hour
    THEME_CACHE_TTL: Final[int] = 1800  # 30 minutes
    SKILL_CATALOG_CACHE_TTL: Final[int] = 86400  # 24 hours

    # Cache key prefixes
    PORTFOLIO_KEY_PREFIX: Final[str] = "portfolio:"
    USER_KEY_PREFIX: Final[str] = "user:"
    PLAN_KEY_PREFIX: Final[str] = "plan:"
    THEME_KEY_PREFIX: Final[str] = "theme:"


class RateLimitConstants:
    """Rate limiting configuration."""

    # API endpoints rate limits (requests per minute)
    PUBLIC_API_RATE_LIMIT: Final[int] = 60
    AUTHENTICATED_API_RATE_LIMIT: Final[int] = 120
    ADMIN_API_RATE_LIMIT: Final[int] = 300

    # Specific endpoint limits
    LOGIN_RATE_LIMIT: Final[int] = 5
    REGISTER_RATE_LIMIT: Final[int] = 3
    PASSWORD_RESET_RATE_LIMIT: Final[int] = 3
    FILE_UPLOAD_RATE_LIMIT: Final[int] = 10

    # Window duration (seconds)
    RATE_LIMIT_WINDOW: Final[int] = 60


class PaginationConstants:
    """Pagination defaults."""

    DEFAULT_PAGE_SIZE: Final[int] = 20
    MAX_PAGE_SIZE: Final[int] = 100
    MIN_PAGE_SIZE: Final[int] = 1
