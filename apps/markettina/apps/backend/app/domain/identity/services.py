"""
MARKETTINA v2.0 - Identity Context Services
Business logic for account and social account operations.
"""

import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.identity.models import (
    Account,
    PlanTier,
    SocialAccount,
    SocialPlatform,
    SyncStatus,
    UserPermission,
)
from app.domain.identity.schemas import (
    AccountCreate,
    AccountUpdate,
    SocialAccountCreate,
    SocialAccountMetricsUpdate,
    SocialAccountUpdate,
    UserPermissionBulkCreate,
    UserPermissionCheck,
    UserPermissionCheckResult,
    UserPermissionCreate,
)

logger = logging.getLogger(__name__)


class AccountService:
    """Service for account operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    async def create_account(self, data: AccountCreate) -> Account:
        """Create new account."""
        # Check if slug is unique
        existing = await self.db.execute(
            select(Account).where(
                and_(Account.slug == data.slug, Account.deleted_at.is_(None))
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account slug already exists"
            )

        account = Account(
            name=data.name,
            slug=data.slug.lower(),
            plan_tier=data.plan_tier,
            is_active=data.is_active,
            settings=data.settings.model_dump() if data.settings else {}
        )
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        logger.info(f"Created account: {account}")
        return account

    async def get_account(self, account_id: UUID) -> Account | None:
        """Get account by ID."""
        query = select(Account).where(
            and_(Account.id == account_id, Account.deleted_at.is_(None))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_account_by_slug(self, slug: str) -> Account | None:
        """Get account by slug."""
        query = select(Account).where(
            and_(Account.slug == slug.lower(), Account.deleted_at.is_(None))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_accounts(
        self,
        plan_tier: PlanTier | None = None,
        is_active: bool | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[Account]:
        """List accounts with filters."""
        query = select(Account).where(Account.deleted_at.is_(None))

        if plan_tier:
            query = query.where(Account.plan_tier == plan_tier)
        if is_active is not None:
            query = query.where(Account.is_active == is_active)

        query = query.order_by(Account.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_account(
        self,
        account_id: UUID,
        data: AccountUpdate
    ) -> Account:
        """Update account."""
        account = await self.get_account(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        update_data = data.model_dump(exclude_unset=True)
        if update_data.get("settings"):
            update_data["settings"] = update_data["settings"].model_dump()

        for field, value in update_data.items():
            setattr(account, field, value)

        account.version += 1
        await self.db.commit()
        await self.db.refresh(account)
        logger.info(f"Updated account: {account}")
        return account

    async def delete_account(self, account_id: UUID) -> bool:
        """Soft delete account."""
        account = await self.get_account(account_id)
        if not account:
            return False

        account.deleted_at = datetime.now(UTC)
        account.is_active = False
        await self.db.commit()
        logger.info(f"Deleted account: {account_id}")
        return True

    async def upgrade_plan(
        self,
        account_id: UUID,
        new_plan: PlanTier,
        stripe_customer_id: str | None = None
    ) -> Account:
        """Upgrade account plan."""
        account = await self.get_account(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )

        account.plan_tier = new_plan
        if stripe_customer_id:
            account.stripe_customer_id = stripe_customer_id
        account.version += 1

        await self.db.commit()
        await self.db.refresh(account)
        logger.info(f"Upgraded account {account_id} to {new_plan.value}")
        return account


class SocialAccountService:
    """Service for social account operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    async def create_social_account(self, data: SocialAccountCreate) -> SocialAccount:
        """Create new social account connection."""
        # Check for duplicate
        existing = await self.db.execute(
            select(SocialAccount).where(
                and_(
                    SocialAccount.account_id == data.account_id,
                    SocialAccount.platform == data.platform,
                    SocialAccount.platform_user_id == data.platform_user_id,
                    SocialAccount.deleted_at.is_(None)
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Social account already connected"
            )

        social_account = SocialAccount(
            account_id=data.account_id,
            platform=data.platform,
            platform_user_id=data.platform_user_id,
            display_name=data.display_name,
            handle=data.handle,
            profile_url=data.profile_url,
            avatar_url=data.avatar_url,
            access_token=data.access_token,
            refresh_token=data.refresh_token,
            token_expires_at=data.token_expires_at,
            is_primary=data.is_primary,
            sync_status=SyncStatus.ACTIVE
        )

        # If first account of this platform, make it primary
        if data.is_primary:
            await self._clear_primary(data.account_id, data.platform)

        self.db.add(social_account)
        await self.db.commit()
        await self.db.refresh(social_account)
        logger.info(f"Created social account: {social_account}")
        return social_account

    async def _clear_primary(self, account_id: UUID, platform: SocialPlatform) -> None:
        """Clear primary flag for platform."""
        await self.db.execute(
            update(SocialAccount)
            .where(
                and_(
                    SocialAccount.account_id == account_id,
                    SocialAccount.platform == platform,
                    SocialAccount.is_primary == True
                )
            )
            .values(is_primary=False)
        )

    async def get_social_account(self, social_account_id: UUID) -> SocialAccount | None:
        """Get social account by ID."""
        query = select(SocialAccount).where(
            and_(SocialAccount.id == social_account_id, SocialAccount.deleted_at.is_(None))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_social_accounts(
        self,
        account_id: UUID,
        platform: SocialPlatform | None = None,
        is_active: bool | None = None
    ) -> list[SocialAccount]:
        """List social accounts for an account."""
        query = select(SocialAccount).where(
            and_(
                SocialAccount.account_id == account_id,
                SocialAccount.deleted_at.is_(None)
            )
        )

        if platform:
            query = query.where(SocialAccount.platform == platform)
        if is_active is not None:
            query = query.where(SocialAccount.is_active == is_active)

        query = query.order_by(SocialAccount.is_primary.desc(), SocialAccount.created_at)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_social_account(
        self,
        social_account_id: UUID,
        data: SocialAccountUpdate
    ) -> SocialAccount:
        """Update social account."""
        social_account = await self.get_social_account(social_account_id)
        if not social_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social account not found"
            )

        update_data = data.model_dump(exclude_unset=True)

        # Handle primary flag
        if update_data.get("is_primary"):
            await self._clear_primary(social_account.account_id, social_account.platform)

        for field, value in update_data.items():
            setattr(social_account, field, value)

        social_account.version += 1
        await self.db.commit()
        await self.db.refresh(social_account)
        return social_account

    async def update_metrics(
        self,
        social_account_id: UUID,
        data: SocialAccountMetricsUpdate
    ) -> SocialAccount:
        """Update social account metrics."""
        social_account = await self.get_social_account(social_account_id)
        if not social_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social account not found"
            )

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(social_account, field, value)

        social_account.last_sync_at = datetime.now(UTC)
        social_account.sync_status = SyncStatus.ACTIVE

        await self.db.commit()
        await self.db.refresh(social_account)
        return social_account

    async def set_sync_error(
        self,
        social_account_id: UUID,
        error_message: str
    ) -> SocialAccount:
        """Set sync error for social account."""
        social_account = await self.get_social_account(social_account_id)
        if not social_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social account not found"
            )

        social_account.sync_status = SyncStatus.ERROR
        social_account.last_error = error_message
        social_account.last_sync_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(social_account)
        return social_account

    async def disconnect_social_account(self, social_account_id: UUID) -> bool:
        """Disconnect (soft delete) social account."""
        social_account = await self.get_social_account(social_account_id)
        if not social_account:
            return False

        social_account.deleted_at = datetime.now(UTC)
        social_account.is_active = False
        social_account.sync_status = SyncStatus.DISCONNECTED
        social_account.access_token = None
        social_account.refresh_token = None

        await self.db.commit()
        logger.info(f"Disconnected social account: {social_account_id}")
        return True


class UserPermissionService:
    """Service for user permission operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    async def grant_permission(self, data: UserPermissionCreate) -> UserPermission:
        """Grant permission to user."""
        # Check for existing permission
        existing = await self.db.execute(
            select(UserPermission).where(
                and_(
                    UserPermission.account_id == data.account_id,
                    UserPermission.user_id == data.user_id,
                    UserPermission.resource_type == data.resource_type,
                    UserPermission.resource_id == data.resource_id,
                    UserPermission.permission == data.permission
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already granted"
            )

        permission = UserPermission(
            account_id=data.account_id,
            user_id=data.user_id,
            resource_type=data.resource_type,
            resource_id=data.resource_id,
            permission=data.permission.value,
            expires_at=data.expires_at
        )
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)
        return permission

    async def grant_bulk_permissions(
        self,
        data: UserPermissionBulkCreate
    ) -> list[UserPermission]:
        """Grant multiple permissions to user."""
        permissions = []
        for perm_data in data.permissions:
            perm = UserPermission(
                account_id=data.account_id,
                user_id=data.user_id,
                resource_type=perm_data.resource_type,
                resource_id=perm_data.resource_id,
                permission=perm_data.permission.value
            )
            self.db.add(perm)
            permissions.append(perm)

        await self.db.commit()
        for perm in permissions:
            await self.db.refresh(perm)
        return permissions

    async def check_permission(self, data: UserPermissionCheck) -> UserPermissionCheckResult:
        """Check if user has specific permission."""
        now = datetime.now(UTC)

        # Build query - check for specific resource or wildcard
        base_conditions = [
            UserPermission.account_id == data.account_id,
            UserPermission.user_id == data.user_id,
            UserPermission.resource_type == data.resource_type,
            UserPermission.permission == data.permission.value,
            (UserPermission.expires_at.is_(None) | (UserPermission.expires_at > now))
        ]

        # Check specific resource permission
        if data.resource_id:
            query = select(UserPermission).where(
                and_(
                    *base_conditions,
                    (UserPermission.resource_id == data.resource_id) | UserPermission.resource_id.is_(None)
                )
            )
        else:
            query = select(UserPermission).where(and_(*base_conditions))

        result = await self.db.execute(query.limit(1))
        permission = result.scalar_one_or_none()

        if permission:
            return UserPermissionCheckResult(
                has_permission=True,
                permission_id=permission.id,
                expires_at=permission.expires_at
            )
        return UserPermissionCheckResult(has_permission=False)

    async def list_user_permissions(
        self,
        account_id: UUID,
        user_id: int
    ) -> list[UserPermission]:
        """List all permissions for a user in an account."""
        query = select(UserPermission).where(
            and_(
                UserPermission.account_id == account_id,
                UserPermission.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def revoke_permission(self, permission_id: UUID) -> bool:
        """Revoke a specific permission."""
        permission = await self.db.get(UserPermission, permission_id)
        if not permission:
            return False

        await self.db.delete(permission)
        await self.db.commit()
        return True

    async def revoke_all_permissions(self, account_id: UUID, user_id: int) -> int:
        """Revoke all permissions for a user in an account."""
        query = select(UserPermission).where(
            and_(
                UserPermission.account_id == account_id,
                UserPermission.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        permissions = list(result.scalars().all())

        for perm in permissions:
            await self.db.delete(perm)

        await self.db.commit()
        return len(permissions)


def get_account_service(db: AsyncSession) -> AccountService:
    """Dependency injector for AccountService."""
    return AccountService(db)


def get_social_account_service(db: AsyncSession) -> SocialAccountService:
    """Dependency injector for SocialAccountService."""
    return SocialAccountService(db)


def get_permission_service(db: AsyncSession) -> UserPermissionService:
    """Dependency injector for UserPermissionService."""
    return UserPermissionService(db)
