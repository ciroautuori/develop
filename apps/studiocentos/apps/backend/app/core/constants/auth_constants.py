"""Authentication Constants"""

from typing import Final


class AuthConstants:
    """Authentication-related constants."""

    # Rate limiting
    MAX_LOGIN_ATTEMPTS: Final[int] = 5
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: Final[int] = 60
    MAX_REGISTRATION_PER_HOUR: Final[int] = 3
    MAX_PASSWORD_RESET_PER_HOUR: Final[int] = 3

    # Password requirements
    PASSWORD_MIN_LENGTH: Final[int] = 8
    PASSWORD_MAX_LENGTH: Final[int] = 128
    PASSWORD_REQUIRE_UPPERCASE: Final[bool] = True
    PASSWORD_REQUIRE_LOWERCASE: Final[bool] = True
    PASSWORD_REQUIRE_DIGIT: Final[bool] = True
    PASSWORD_REQUIRE_SPECIAL: Final[bool] = False

    # Token expiration (minutes) - 7 days for better UX
    ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 10080  # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: Final[int] = 30  # 30 days for refresh
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: Final[int] = 60
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: Final[int] = 24

    # Account lockout
    ACCOUNT_LOCKOUT_DURATION_MINUTES: Final[int] = 30
    FAILED_LOGIN_ATTEMPTS_BEFORE_LOCKOUT: Final[int] = 5

    # MFA
    MFA_CODE_LENGTH: Final[int] = 6
    MFA_CODE_EXPIRE_MINUTES: Final[int] = 5
