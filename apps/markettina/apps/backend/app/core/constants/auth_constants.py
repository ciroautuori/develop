"""Authentication Constants"""

from enum import Enum
from typing import Final, List


class Permission(str, Enum):
    """Granular API permissions for RBAC."""

    # Admin - Full access
    ADMIN_FULL = "admin:full"
    ADMIN_READ = "admin:read"

    # User Management
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    USERS_DELETE = "users:delete"

    # Content Management (AI Marketing, Posts, Calendar)
    CONTENT_READ = "content:read"
    CONTENT_WRITE = "content:write"
    CONTENT_PUBLISH = "content:publish"
    CONTENT_DELETE = "content:delete"

    # Finance (Billing, Tokens, Transactions)
    FINANCE_READ = "finance:read"
    FINANCE_WRITE = "finance:write"

    # Analytics & Reports
    ANALYTICS_READ = "analytics:read"

    # Settings & Configuration
    SETTINGS_READ = "settings:read"
    SETTINGS_WRITE = "settings:write"

    # Integrations (Google, Meta, Stripe)
    INTEGRATIONS_READ = "integrations:read"
    INTEGRATIONS_WRITE = "integrations:write"

    # CRM (Customers, Leads)
    CRM_READ = "crm:read"
    CRM_WRITE = "crm:write"


class Role(str, Enum):
    """User roles for the platform."""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    CUSTOMER = "customer"


# Role to Permissions Mapping
ROLE_PERMISSIONS: dict[str, List[Permission]] = {
    Role.ADMIN.value: [Permission.ADMIN_FULL],  # Admin has ALL permissions

    Role.EDITOR.value: [
        Permission.CONTENT_READ,
        Permission.CONTENT_WRITE,
        Permission.CONTENT_PUBLISH,
        Permission.ANALYTICS_READ,
        Permission.CRM_READ,
        Permission.CRM_WRITE,
        Permission.SETTINGS_READ,
    ],

    Role.VIEWER.value: [
        Permission.CONTENT_READ,
        Permission.ANALYTICS_READ,
        Permission.FINANCE_READ,
        Permission.CRM_READ,
        Permission.SETTINGS_READ,
    ],

    Role.CUSTOMER.value: [
        Permission.CONTENT_READ,
    ],
}


def has_permission(user_role: str, required_permission: Permission) -> bool:
    """Check if a role has a specific permission.

    Args:
        user_role: The user's role (admin, editor, viewer, customer)
        required_permission: The permission to check

    Returns:
        True if the role has the permission, False otherwise
    """
    permissions = ROLE_PERMISSIONS.get(user_role, [])

    # Admin with ADMIN_FULL has all permissions
    if Permission.ADMIN_FULL in permissions:
        return True

    return required_permission in permissions


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
