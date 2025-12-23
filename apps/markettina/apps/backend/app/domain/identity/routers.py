"""
MARKETTINA v2.0 - Identity Context Routers
FastAPI endpoints for account and social account operations.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.dependencies.auth_deps import get_current_user
from app.domain.auth.models import User
from app.infrastructure.database.session import get_async_db

from .schemas import (
    # Account
    AccountCreate,
    AccountRead,
    AccountSummary,
    AccountUpdate,
    PlanTier,
    # Social Account
    SocialAccountCreate,
    SocialAccountMetricsUpdate,
    SocialAccountRead,
    SocialAccountSummary,
    SocialAccountUpdate,
    SocialPlatform,
    UserPermissionBulkCreate,
    UserPermissionCheck,
    UserPermissionCheckResult,
    # Permissions
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

router = APIRouter(prefix="/api/v1/identity", tags=["identity"])
admin_router = APIRouter(prefix="/api/v1/admin/identity", tags=["admin-identity"])


# ============================================================================
# DEPENDENCIES
# ============================================================================

async def get_account_svc(db: AsyncSession = Depends(get_async_db)) -> AccountService:
    """Get account service instance."""
    return get_account_service(db)


async def get_social_svc(db: AsyncSession = Depends(get_async_db)) -> SocialAccountService:
    """Get social account service instance."""
    return get_social_account_service(db)


async def get_perm_svc(db: AsyncSession = Depends(get_async_db)) -> UserPermissionService:
    """Get permission service instance."""
    return get_permission_service(db)


# ============================================================================
# ACCOUNT ENDPOINTS
# ============================================================================

@admin_router.post("/accounts", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccountCreate,
    service: AccountService = Depends(get_account_svc),
    current_user: User = Depends(get_current_user)
):
    """Create new account (Admin only)."""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return await service.create_account(data)


@admin_router.get("/accounts", response_model=list[AccountSummary])
async def list_accounts(
    plan_tier: PlanTier | None = Query(None),
    is_active: bool | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: AccountService = Depends(get_account_svc),
    current_user: User = Depends(get_current_user)
):
    """List all accounts (Admin only)."""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    accounts = await service.list_accounts(plan_tier, is_active, limit, offset)
    return [AccountSummary.model_validate(a) for a in accounts]


@router.get("/accounts/{account_id}", response_model=AccountRead)
async def get_account(
    account_id: UUID = Path(...),
    service: AccountService = Depends(get_account_svc),
    current_user: User = Depends(get_current_user)
):
    """Get account details."""
    account = await service.get_account(account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account


@router.get("/accounts/by-slug/{slug}", response_model=AccountRead)
async def get_account_by_slug(
    slug: str = Path(..., min_length=3),
    service: AccountService = Depends(get_account_svc),
    current_user: User = Depends(get_current_user)
):
    """Get account by slug."""
    account = await service.get_account_by_slug(slug)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account


@router.patch("/accounts/{account_id}", response_model=AccountRead)
async def update_account(
    account_id: UUID = Path(...),
    data: AccountUpdate = ...,
    service: AccountService = Depends(get_account_svc),
    current_user: User = Depends(get_current_user)
):
    """Update account."""
    return await service.update_account(account_id, data)


@admin_router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: UUID = Path(...),
    service: AccountService = Depends(get_account_svc),
    current_user: User = Depends(get_current_user)
):
    """Delete account (Admin only, soft delete)."""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    success = await service.delete_account(account_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return {"message": "Account deleted"}


@router.post("/accounts/{account_id}/upgrade", response_model=AccountRead)
async def upgrade_account_plan(
    account_id: UUID = Path(...),
    plan: PlanTier = Query(...),
    stripe_customer_id: str | None = Query(None),
    service: AccountService = Depends(get_account_svc),
    current_user: User = Depends(get_current_user)
):
    """Upgrade account plan."""
    return await service.upgrade_plan(account_id, plan, stripe_customer_id)


# ============================================================================
# SOCIAL ACCOUNT ENDPOINTS
# ============================================================================

@router.post("/social-accounts", response_model=SocialAccountRead, status_code=status.HTTP_201_CREATED)
async def connect_social_account(
    data: SocialAccountCreate,
    service: SocialAccountService = Depends(get_social_svc),
    current_user: User = Depends(get_current_user)
):
    """Connect new social account."""
    return await service.create_social_account(data)


@router.get("/accounts/{account_id}/social-accounts", response_model=list[SocialAccountSummary])
async def list_social_accounts(
    account_id: UUID = Path(...),
    platform: SocialPlatform | None = Query(None),
    is_active: bool | None = Query(None),
    service: SocialAccountService = Depends(get_social_svc),
    current_user: User = Depends(get_current_user)
):
    """List social accounts for an account."""
    accounts = await service.list_social_accounts(account_id, platform, is_active)
    return [SocialAccountSummary.model_validate(a) for a in accounts]


@router.get("/social-accounts/{social_account_id}", response_model=SocialAccountRead)
async def get_social_account(
    social_account_id: UUID = Path(...),
    service: SocialAccountService = Depends(get_social_svc),
    current_user: User = Depends(get_current_user)
):
    """Get social account details."""
    account = await service.get_social_account(social_account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Social account not found")
    return account


@router.patch("/social-accounts/{social_account_id}", response_model=SocialAccountRead)
async def update_social_account(
    social_account_id: UUID = Path(...),
    data: SocialAccountUpdate = ...,
    service: SocialAccountService = Depends(get_social_svc),
    current_user: User = Depends(get_current_user)
):
    """Update social account."""
    return await service.update_social_account(social_account_id, data)


@router.post("/social-accounts/{social_account_id}/metrics", response_model=SocialAccountRead)
async def update_social_metrics(
    social_account_id: UUID = Path(...),
    data: SocialAccountMetricsUpdate = ...,
    service: SocialAccountService = Depends(get_social_svc),
    current_user: User = Depends(get_current_user)
):
    """Update social account metrics from sync."""
    return await service.update_metrics(social_account_id, data)


@router.delete("/social-accounts/{social_account_id}")
async def disconnect_social_account(
    social_account_id: UUID = Path(...),
    service: SocialAccountService = Depends(get_social_svc),
    current_user: User = Depends(get_current_user)
):
    """Disconnect social account."""
    success = await service.disconnect_social_account(social_account_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Social account not found")
    return {"message": "Social account disconnected"}


# ============================================================================
# PERMISSION ENDPOINTS
# ============================================================================

@router.post("/permissions", response_model=UserPermissionRead, status_code=status.HTTP_201_CREATED)
async def grant_permission(
    data: UserPermissionCreate,
    service: UserPermissionService = Depends(get_perm_svc),
    current_user: User = Depends(get_current_user)
):
    """Grant permission to user."""
    return await service.grant_permission(data)


@router.post("/permissions/bulk", response_model=list[UserPermissionRead], status_code=status.HTTP_201_CREATED)
async def grant_bulk_permissions(
    data: UserPermissionBulkCreate,
    service: UserPermissionService = Depends(get_perm_svc),
    current_user: User = Depends(get_current_user)
):
    """Grant multiple permissions to user."""
    return await service.grant_bulk_permissions(data)


@router.post("/permissions/check", response_model=UserPermissionCheckResult)
async def check_permission(
    data: UserPermissionCheck,
    service: UserPermissionService = Depends(get_perm_svc),
    current_user: User = Depends(get_current_user)
):
    """Check if user has specific permission."""
    return await service.check_permission(data)


@router.get("/accounts/{account_id}/users/{user_id}/permissions", response_model=list[UserPermissionRead])
async def list_user_permissions(
    account_id: UUID = Path(...),
    user_id: int = Path(...),
    service: UserPermissionService = Depends(get_perm_svc),
    current_user: User = Depends(get_current_user)
):
    """List all permissions for a user in an account."""
    return await service.list_user_permissions(account_id, user_id)


@router.delete("/permissions/{permission_id}")
async def revoke_permission(
    permission_id: UUID = Path(...),
    service: UserPermissionService = Depends(get_perm_svc),
    current_user: User = Depends(get_current_user)
):
    """Revoke specific permission."""
    success = await service.revoke_permission(permission_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return {"message": "Permission revoked"}


@router.delete("/accounts/{account_id}/users/{user_id}/permissions")
async def revoke_all_user_permissions(
    account_id: UUID = Path(...),
    user_id: int = Path(...),
    service: UserPermissionService = Depends(get_perm_svc),
    current_user: User = Depends(get_current_user)
):
    """Revoke all permissions for user in account."""
    count = await service.revoke_all_permissions(account_id, user_id)
    return {"message": f"Revoked {count} permissions"}
