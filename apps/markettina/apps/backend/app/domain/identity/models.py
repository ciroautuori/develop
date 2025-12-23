"""
MARKETTINA v2.0 - Identity Context Models
Account, SocialAccount, Permissions
"""

import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.domain.shared.base_model import SoftDeleteMixin, TimestampMixin, VersionMixin
from app.infrastructure.database import Base


class PlanTier(str, enum.Enum):
    """Account plan tiers."""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class SocialPlatform(str, enum.Enum):
    """Supported social platforms."""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    THREADS = "threads"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"


class SyncStatus(str, enum.Enum):
    """Social account sync status."""
    ACTIVE = "active"
    SYNCING = "syncing"
    ERROR = "error"
    EXPIRED = "expired"
    DISCONNECTED = "disconnected"


class Account(Base, TimestampMixin, SoftDeleteMixin, VersionMixin):
    """
    Account - Multi-tenancy root entity.
    All resources belong to an account.
    """
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Account info
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)

    # Plan & Status
    plan_tier = Column(SQLEnum(PlanTier), nullable=False, default=PlanTier.FREE)
    is_active = Column(Boolean, nullable=False, default=True)

    # Settings (JSONB for flexibility)
    settings = Column(JSONB, nullable=False, default=dict)

    # Billing
    stripe_customer_id = Column(String(255), unique=True, nullable=True)

    # Relationships
    social_accounts = relationship("SocialAccount", back_populates="account", lazy="dynamic")
    subscription = relationship("Subscription", back_populates="account", uselist=False)

    def __repr__(self):
        return f"<Account {self.name} ({self.plan_tier.value})>"


class SocialAccount(Base, TimestampMixin, SoftDeleteMixin, VersionMixin):
    """
    SocialAccount - Connected social media accounts.
    Stores OAuth tokens and platform-specific data.
    """
    __tablename__ = "social_accounts"
    __table_args__ = (
        UniqueConstraint("account_id", "platform", "platform_user_id", name="uq_social_account_platform"),
        Index("ix_social_accounts_account_platform", "account_id", "platform"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Foreign keys
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Platform info
    platform = Column(SQLEnum(SocialPlatform), nullable=False)
    platform_user_id = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    handle = Column(String(255), nullable=True)  # @username
    profile_url = Column(Text, nullable=True)
    avatar_url = Column(Text, nullable=True)

    # OAuth tokens (encrypted in production)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    is_primary = Column(Boolean, nullable=False, default=False)
    sync_status = Column(SQLEnum(SyncStatus), nullable=False, default=SyncStatus.ACTIVE)

    # Metrics
    followers_count = Column(Integer, nullable=True)
    following_count = Column(Integer, nullable=True)
    posts_count = Column(Integer, nullable=True)

    # Sync tracking
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)

    # Relationships
    account = relationship("Account", back_populates="social_accounts")
    health_checks = relationship("SocialAccountHealth", back_populates="social_account", lazy="dynamic")

    def __repr__(self):
        return f"<SocialAccount {self.platform.value}:{self.handle}>"


class SocialAccountHealth(Base, TimestampMixin):
    """
    SocialAccountHealth - Health monitoring for social accounts.
    Tracks token validity and API connectivity.
    """
    __tablename__ = "social_account_health"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Foreign key
    social_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("social_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Health status
    status = Column(String(50), nullable=False, default="healthy")  # healthy, warning, error
    status_message = Column(Text, nullable=True)

    # Check details
    last_check_at = Column(DateTime(timezone=True), nullable=True)
    consecutive_failures = Column(Integer, nullable=False, default=0)

    # Relationships
    social_account = relationship("SocialAccount", back_populates="health_checks")


class UserPermission(Base, TimestampMixin):
    """
    UserPermission - Fine-grained permissions for users.
    Supports resource-level access control.
    """
    __tablename__ = "user_permissions"
    __table_args__ = (
        UniqueConstraint("account_id", "user_id", "resource_type", "resource_id", "permission", name="uq_user_permission"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Foreign keys
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Permission scope
    resource_type = Column(String(100), nullable=False)  # campaign, post, lead, etc.
    resource_id = Column(UUID(as_uuid=True), nullable=True)  # null = all resources of type
    permission = Column(String(50), nullable=False)  # read, write, delete, admin

    # Validity
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
