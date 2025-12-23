"""
MARKETTINA v2.0 - Identity Context
Account, SocialAccount, Permissions for multi-tenancy
"""

from .models import (
    Account,
    PlanTier,
    SocialAccount,
    SocialAccountHealth,
    SocialPlatform,
    SyncStatus,
    UserPermission,
)
from .routers import admin_router, router
from .schemas import (
    AccountCreate,
    AccountRead,
    AccountSettings,
    AccountSummary,
    AccountUpdate,
    HealthStatus,
    PermissionType,
    SocialAccountCreate,
    SocialAccountHealthCreate,
    SocialAccountHealthRead,
    SocialAccountMetricsUpdate,
    SocialAccountRead,
    SocialAccountSummary,
    SocialAccountUpdate,
    UserPermissionBulkCreate,
    UserPermissionCheck,
    UserPermissionCheckResult,
    UserPermissionCreate,
    UserPermissionRead,
)
from .services import (
    AccountService,
    SocialAccountService,
    UserPermissionService,
    get_account_service,
    get_permission_service,
    get_social_account_service,
)

__all__ = [
    # Models
    "Account",
    "PlanTier",
    "SocialAccount",
    "SocialPlatform",
    "SyncStatus",
    "SocialAccountHealth",
    "UserPermission",
    # Schemas
    "AccountCreate",
    "AccountUpdate",
    "AccountRead",
    "AccountSummary",
    "AccountSettings",
    "SocialAccountCreate",
    "SocialAccountUpdate",
    "SocialAccountRead",
    "SocialAccountSummary",
    "SocialAccountMetricsUpdate",
    "SocialAccountHealthCreate",
    "SocialAccountHealthRead",
    "UserPermissionCreate",
    "UserPermissionRead",
    "UserPermissionCheck",
    "UserPermissionCheckResult",
    "UserPermissionBulkCreate",
    "HealthStatus",
    "PermissionType",
    # Services
    "AccountService",
    "SocialAccountService",
    "UserPermissionService",
    "get_account_service",
    "get_social_account_service",
    "get_permission_service",
    # Routers
    "router",
    "admin_router",
]
