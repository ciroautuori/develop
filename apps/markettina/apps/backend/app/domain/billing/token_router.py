"""
MARKETTINA v3.0 - Token Router
API endpoints for Token Wallet operations
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.dependencies.auth_deps import get_current_admin_user, get_current_user
from app.domain.auth.models import User
from app.domain.billing.token_models import TransactionType
from app.domain.billing.token_schemas import (
    InsufficientTokensError,
    TokenBalanceResponse,
    TokenPackageList,
    TokenPurchaseRequest,
    TokenPurchaseResponse,
    TokenTransactionList,
    TokenUsageRequest,
    TokenUsageResponse,
)
from app.domain.billing.token_service import (
    InsufficientTokensException,
    TokenService,
    TokenServiceError,
)
from app.infrastructure.database import get_async_db

router = APIRouter(prefix="/tokens", tags=["Tokens"])
admin_router = APIRouter(prefix="/admin/tokens", tags=["Admin Tokens"])


# =============================================================================
# USER ENDPOINTS
# =============================================================================

@router.get("/balance", response_model=TokenBalanceResponse)
async def get_token_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get current token balance for the authenticated user."""
    service = TokenService(db)
    # Assuming user has a default account_id - adjust based on your auth
    account_id = current_user.default_account_id
    if not account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no associated account"
        )
    return await service.get_balance(current_user.id, account_id)


@router.get("/packages", response_model=TokenPackageList)
async def list_token_packages(
    db: AsyncSession = Depends(get_async_db)
):
    """Get all available token packages for purchase."""
    service = TokenService(db)
    packages = await service.get_active_packages()
    return TokenPackageList(packages=packages, count=len(packages))


@router.post("/purchase", response_model=TokenPurchaseResponse)
async def purchase_tokens(
    request: TokenPurchaseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Purchase a token package."""
    service = TokenService(db)
    account_id = current_user.default_account_id
    if not account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no associated account"
        )

    try:
        return await service.purchase_package(
            user_id=current_user.id,
            account_id=account_id,
            package_id=request.package_id,
            stripe_payment_intent_id=request.payment_method_id
        )
    except TokenServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/consume",
    response_model=TokenUsageResponse,
    responses={402: {"model": InsufficientTokensError}}
)
async def consume_tokens(
    request: TokenUsageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Consume tokens for AI service usage."""
    service = TokenService(db)
    account_id = current_user.default_account_id
    if not account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no associated account"
        )

    try:
        return await service.consume_for_ai(
            user_id=current_user.id,
            account_id=account_id,
            request=request
        )
    except InsufficientTokensException as e:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "insufficient_tokens",
                "required": e.required,
                "available": e.available,
                "deficit": e.deficit
            }
        )


@router.get("/transactions", response_model=TokenTransactionList)
async def get_transaction_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    transaction_type: TransactionType | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get token transaction history."""
    service = TokenService(db)
    account_id = current_user.default_account_id
    if not account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no associated account"
        )

    return await service.get_transactions(
        user_id=current_user.id,
        account_id=account_id,
        page=page,
        page_size=page_size,
        transaction_type=transaction_type
    )


@router.get("/check/{required_tokens}")
async def check_token_availability(
    required_tokens: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Check if user has enough tokens for an operation."""
    service = TokenService(db)
    account_id = current_user.default_account_id
    if not account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no associated account"
        )

    has_enough = await service.check_and_reserve(
        user_id=current_user.id,
        account_id=account_id,
        required_tokens=required_tokens
    )
    return {"has_enough": has_enough, "required": required_tokens}


# =============================================================================
# ADMIN ENDPOINTS
# =============================================================================

@admin_router.post("/credit/{user_id}")
async def admin_credit_tokens(
    user_id: int,
    account_id: UUID,
    amount: int = Query(gt=0),
    reason: str = Query(max_length=500),
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Admin: Credit tokens to a user (bonus/adjustment)."""
    service = TokenService(db)
    wallet = await service.get_or_create_wallet(user_id, account_id)

    transaction = await service.credit_tokens(
        wallet=wallet,
        amount=amount,
        transaction_type=TransactionType.BONUS,
        description=f"Admin credit by {admin.email}: {reason}"
    )
    await db.commit()

    return {
        "success": True,
        "transaction_id": str(transaction.id),
        "new_balance": wallet.balance
    }


@admin_router.post("/refund/{transaction_id}")
async def admin_refund_transaction(
    transaction_id: UUID,
    reason: str = Query(max_length=500),
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Admin: Refund a specific transaction."""
    # Implementation would look up the original transaction
    # and create a refund transaction
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refund functionality coming soon"
    )


@admin_router.get("/wallet/{user_id}/{account_id}")
async def admin_get_user_wallet(
    user_id: int,
    account_id: UUID,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Admin: Get detailed wallet info for a user."""
    service = TokenService(db)
    wallet = await service.get_or_create_wallet(user_id, account_id)

    return {
        "wallet_id": str(wallet.id),
        "user_id": wallet.user_id,
        "account_id": str(wallet.account_id),
        "balance": wallet.balance,
        "total_purchased": wallet.total_purchased,
        "total_used": wallet.total_used,
        "total_bonus": wallet.total_bonus,
        "total_refunded": wallet.total_refunded,
        "total_spent_usd": float(wallet.total_spent_usd),
        "last_purchase_at": wallet.last_purchase_at,
        "last_usage_at": wallet.last_usage_at
    }
