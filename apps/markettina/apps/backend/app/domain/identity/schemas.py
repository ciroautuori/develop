"""
MARKETTINA v2.0 - Identity Context Schemas
Pydantic models for account and social account operations.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ============================================================================
# ENUMS
# ============================================================================

class PlanTier(str, Enum):
    """Account plan tiers."""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class SocialPlatform(str, Enum):
    """Supported social platforms."""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    THREADS = "threads"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"


class SyncStatus(str, Enum):
    """Social account sync status."""
    ACTIVE = "active"
    SYNCING = "syncing"
    ERROR = "error"
    EXPIRED = "expired"
    DISCONNECTED = "disconnected"


class HealthStatus(str, Enum):
    """Social account health status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"


class PermissionType(str, Enum):
    """Permission types."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


# ============================================================================
# ACCOUNT SCHEMAS
# ============================================================================

class AccountSettings(BaseModel):
    """Account settings value object."""
    timezone: str = "Europe/Rome"
    language: str = "it"
    currency: str = "EUR"
    notifications_enabled: bool = True
    two_factor_required: bool = False
    allowed_domains: list[str] | None = None


class AccountBase(BaseModel):
    """Base schema for accounts."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-z0-9-]+$")
    plan_tier: PlanTier = PlanTier.FREE
    is_active: bool = True
    settings: AccountSettings | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Ensure slug is lowercase and valid."""
        return v.lower().strip()


class AccountCreate(AccountBase):
    """Schema for creating accounts."""


class AccountUpdate(BaseModel):
    """Schema for updating accounts."""
    name: str | None = Field(None, min_length=1, max_length=255)
    plan_tier: PlanTier | None = None
    is_active: bool | None = None
    settings: AccountSettings | None = None
    stripe_customer_id: str | None = None


class AccountRead(AccountBase):
    """Schema for reading accounts."""
    id: UUID
    stripe_customer_id: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    version: int = 1

    model_config = ConfigDict(from_attributes=True)


class AccountSummary(BaseModel):
    """Summary schema for account lists."""
    id: UUID
    name: str
    slug: str
    plan_tier: PlanTier
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# SOCIAL ACCOUNT SCHEMAS
# ============================================================================

class SocialAccountBase(BaseModel):
    """Base schema for social accounts."""
    platform: SocialPlatform
    display_name: str | None = Field(None, max_length=255)
    handle: str | None = Field(None, max_length=255)
    profile_url: str | None = None
    avatar_url: str | None = None
    is_primary: bool = False


class SocialAccountCreate(SocialAccountBase):
    """Schema for creating social accounts."""
    account_id: UUID
    platform_user_id: str = Field(..., min_length=1, max_length=255)
    access_token: str | None = None
    refresh_token: str | None = None
    token_expires_at: datetime | None = None


class SocialAccountUpdate(BaseModel):
    """Schema for updating social accounts."""
    display_name: str | None = Field(None, max_length=255)
    handle: str | None = Field(None, max_length=255)
    profile_url: str | None = None
    avatar_url: str | None = None
    is_active: bool | None = None
    is_primary: bool | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    token_expires_at: datetime | None = None


class SocialAccountRead(SocialAccountBase):
    """Schema for reading social accounts."""
    id: UUID
    account_id: UUID
    user_id: int | None = None
    platform_user_id: str
    is_active: bool
    sync_status: SyncStatus
    followers_count: int | None = None
    following_count: int | None = None
    posts_count: int | None = None
    last_sync_at: datetime | None = None
    last_error: str | None = None
    token_expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    version: int = 1

    model_config = ConfigDict(from_attributes=True)


class SocialAccountSummary(BaseModel):
    """Summary schema for social account lists."""
    id: UUID
    platform: SocialPlatform
    display_name: str | None = None
    handle: str | None = None
    is_active: bool
    is_primary: bool
    sync_status: SyncStatus
    followers_count: int | None = None

    model_config = ConfigDict(from_attributes=True)


class SocialAccountMetricsUpdate(BaseModel):
    """Schema for updating social account metrics."""
    followers_count: int | None = None
    following_count: int | None = None
    posts_count: int | None = None


# ============================================================================
# SOCIAL ACCOUNT HEALTH SCHEMAS
# ============================================================================

class SocialAccountHealthCreate(BaseModel):
    """Schema for creating health check record."""
    social_account_id: UUID
    status: HealthStatus = HealthStatus.HEALTHY
    status_message: str | None = None


class SocialAccountHealthRead(BaseModel):
    """Schema for reading health check records."""
    id: UUID
    social_account_id: UUID
    status: str
    status_message: str | None = None
    last_check_at: datetime | None = None
    consecutive_failures: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# USER PERMISSION SCHEMAS
# ============================================================================

class UserPermissionBase(BaseModel):
    """Base schema for user permissions."""
    resource_type: str = Field(..., max_length=100)
    resource_id: UUID | None = None
    permission: PermissionType


class UserPermissionCreate(UserPermissionBase):
    """Schema for creating user permissions."""
    account_id: UUID
    user_id: int
    expires_at: datetime | None = None


class UserPermissionRead(UserPermissionBase):
    """Schema for reading user permissions."""
    id: UUID
    account_id: UUID
    user_id: int
    granted_at: datetime
    granted_by: int | None = None
    expires_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserPermissionBulkCreate(BaseModel):
    """Schema for bulk permission creation."""
    account_id: UUID
    user_id: int
    permissions: list[UserPermissionBase]


class UserPermissionCheck(BaseModel):
    """Schema for permission check request."""
    account_id: UUID
    user_id: int
    resource_type: str
    resource_id: UUID | None = None
    permission: PermissionType


class UserPermissionCheckResult(BaseModel):
    """Schema for permission check result."""
    has_permission: bool
    permission_id: UUID | None = None
    expires_at: datetime | None = None


# ============================================================================
# ACCOUNT MEMBERSHIP SCHEMAS
# ============================================================================

class AccountMember(BaseModel):
    """Schema for account member."""
    user_id: int
    email: str
    username: str | None = None
    full_name: str | None = None
    role: str
    joined_at: datetime
    permissions: list[UserPermissionRead] = []


class AccountMembersList(BaseModel):
    """Schema for account members list."""
    account_id: UUID
    members: list[AccountMember]
    total: int


class InviteUserRequest(BaseModel):
    """Schema for inviting user to account."""
    email: str
    role: str = "member"
    permissions: list[UserPermissionBase] | None = None


class InviteUserResult(BaseModel):
    """Schema for invite result."""
    success: bool
    user_id: int | None = None
    invitation_sent: bool = False
    error_message: str | None = None


# ============================================================================
# TOKEN REFRESH SCHEMAS
# ============================================================================

class TokenRefreshRequest(BaseModel):
    """Schema for token refresh request."""
    social_account_id: UUID


class TokenRefreshResult(BaseModel):
    """Schema for token refresh result."""
    success: bool
    new_token_expires_at: datetime | None = None
    error_message: str | None = None
