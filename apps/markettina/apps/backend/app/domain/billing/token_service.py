"""
MARKETTINA v3.0 - Token Service
Business logic for Token Wallet operations
"""

import logging
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.billing.token_models import (
    AIProvider,
    TokenPackage,
    TokenTransaction,
    TokenWallet,
    TransactionType,
    UsageContext,
)
from app.domain.billing.token_schemas import (
    TokenBalanceResponse,
    TokenPackageRead,
    TokenPurchaseResponse,
    TokenTransactionList,
    TokenTransactionRead,
    TokenUsageRequest,
    TokenUsageResponse,
)

logger = logging.getLogger(__name__)


class TokenServiceError(Exception):
    """Base exception for token service."""


class InsufficientTokensException(TokenServiceError):
    """Raised when user doesn't have enough tokens."""
    def __init__(self, required: int, available: int):
        self.required = required
        self.available = available
        self.deficit = required - available
        super().__init__(f"Insufficient tokens: need {required}, have {available}")


class TokenService:
    """
    Service for managing token wallets and transactions.
    Implements credit/debit operations with full audit trail.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================================================================
    # WALLET OPERATIONS
    # =========================================================================

    async def get_or_create_wallet(
        self,
        user_id: int,
        account_id: UUID
    ) -> TokenWallet:
        """Get existing wallet or create a new one."""
        stmt = select(TokenWallet).where(
            and_(
                TokenWallet.user_id == user_id,
                TokenWallet.account_id == account_id
            )
        )
        result = await self.db.execute(stmt)
        wallet = result.scalar_one_or_none()

        if not wallet:
            wallet = TokenWallet(
                user_id=user_id,
                account_id=account_id,
                balance=0
            )
            self.db.add(wallet)
            await self.db.flush()
            logger.info(f"Created new wallet for user {user_id} in account {account_id}")

        return wallet

    async def get_balance(
        self,
        user_id: int,
        account_id: UUID
    ) -> TokenBalanceResponse:
        """Get current token balance for a user."""
        wallet = await self.get_or_create_wallet(user_id, account_id)

        # Calculate today's usage
        today_start = datetime.now(UTC).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        stmt = select(func.coalesce(func.sum(TokenTransaction.amount), 0)).where(
            and_(
                TokenTransaction.wallet_id == wallet.id,
                TokenTransaction.type == TransactionType.USAGE,
                TokenTransaction.created_at >= today_start
            )
        )
        result = await self.db.execute(stmt)
        today_usage = abs(result.scalar() or 0)

        # Estimate remaining days based on average usage
        estimated_days = None
        if today_usage > 0 and wallet.balance > 0:
            estimated_days = int(wallet.balance / today_usage)

        return TokenBalanceResponse(
            balance=wallet.balance,
            total_used_today=today_usage,
            estimated_remaining_days=estimated_days
        )

    # =========================================================================
    # CREDIT OPERATIONS (Add tokens)
    # =========================================================================

    async def credit_tokens(
        self,
        wallet: TokenWallet,
        amount: int,
        transaction_type: TransactionType,
        description: str | None = None,
        package_id: str | None = None,
        price_usd: Decimal | None = None,
        stripe_payment_intent_id: str | None = None
    ) -> TokenTransaction:
        """Add tokens to wallet with full audit trail."""
        if amount <= 0:
            raise ValueError("Credit amount must be positive")

        balance_before = wallet.balance
        wallet.balance += amount
        balance_after = wallet.balance

        # Update aggregates
        if transaction_type == TransactionType.PURCHASE:
            wallet.total_purchased += amount
            wallet.last_purchase_at = datetime.now(UTC)
            if price_usd:
                wallet.total_spent_usd += price_usd
        elif transaction_type == TransactionType.BONUS:
            wallet.total_bonus += amount
        elif transaction_type == TransactionType.REFUND:
            wallet.total_refunded += amount

        # Create transaction record
        transaction = TokenTransaction(
            wallet_id=wallet.id,
            user_id=wallet.user_id,
            account_id=wallet.account_id,
            type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            package_id=package_id,
            price_usd=price_usd,
            stripe_payment_intent_id=stripe_payment_intent_id,
            description=description
        )
        self.db.add(transaction)
        await self.db.flush()

        logger.info(
            f"Credited {amount} tokens to wallet {wallet.id}. "
            f"Balance: {balance_before} -> {balance_after}"
        )
        return transaction

    async def purchase_package(
        self,
        user_id: int,
        account_id: UUID,
        package_id: str,
        stripe_payment_intent_id: str | None = None
    ) -> TokenPurchaseResponse:
        """Purchase a token package."""
        # Get package
        stmt = select(TokenPackage).where(
            and_(
                TokenPackage.id == package_id,
                TokenPackage.is_active == True
            )
        )
        result = await self.db.execute(stmt)
        package = result.scalar_one_or_none()

        if not package:
            raise TokenServiceError(f"Package {package_id} not found or inactive")

        # Get or create wallet
        wallet = await self.get_or_create_wallet(user_id, account_id)

        # Credit tokens (base + bonus)
        total_tokens = package.tokens + package.bonus_tokens
        transaction = await self.credit_tokens(
            wallet=wallet,
            amount=total_tokens,
            transaction_type=TransactionType.PURCHASE,
            description=f"Purchased {package.name}",
            package_id=package_id,
            price_usd=package.price_usd,
            stripe_payment_intent_id=stripe_payment_intent_id
        )

        await self.db.commit()

        return TokenPurchaseResponse(
            success=True,
            transaction_id=transaction.id,
            tokens_added=total_tokens,
            new_balance=wallet.balance,
            stripe_payment_intent_id=stripe_payment_intent_id
        )

    # =========================================================================
    # DEBIT OPERATIONS (Consume tokens)
    # =========================================================================

    async def debit_tokens(
        self,
        wallet: TokenWallet,
        amount: int,
        usage_context: UsageContext,
        ai_provider: AIProvider | None = None,
        ai_model: str | None = None,
        related_resource_id: UUID | None = None,
        related_resource_type: str | None = None,
        description: str | None = None
    ) -> TokenTransaction:
        """Consume tokens from wallet with full audit trail."""
        if amount <= 0:
            raise ValueError("Debit amount must be positive")

        if wallet.balance < amount:
            raise InsufficientTokensException(
                required=amount,
                available=wallet.balance
            )

        balance_before = wallet.balance
        wallet.balance -= amount
        balance_after = wallet.balance

        # Update aggregates
        wallet.total_used += amount
        wallet.last_usage_at = datetime.now(UTC)

        # Create transaction record (negative amount for debit)
        transaction = TokenTransaction(
            wallet_id=wallet.id,
            user_id=wallet.user_id,
            account_id=wallet.account_id,
            type=TransactionType.USAGE,
            amount=-amount,  # Negative for debit
            balance_before=balance_before,
            balance_after=balance_after,
            usage_context=usage_context,
            ai_provider=ai_provider,
            ai_model=ai_model,
            related_resource_id=related_resource_id,
            related_resource_type=related_resource_type,
            description=description
        )
        self.db.add(transaction)
        await self.db.flush()

        logger.info(
            f"Debited {amount} tokens from wallet {wallet.id}. "
            f"Balance: {balance_before} -> {balance_after}"
        )
        return transaction

    async def consume_for_ai(
        self,
        user_id: int,
        account_id: UUID,
        request: TokenUsageRequest
    ) -> TokenUsageResponse:
        """Consume tokens for AI service usage."""
        wallet = await self.get_or_create_wallet(user_id, account_id)

        # Check balance first
        if wallet.balance < request.amount:
            raise InsufficientTokensException(
                required=request.amount,
                available=wallet.balance
            )

        transaction = await self.debit_tokens(
            wallet=wallet,
            amount=request.amount,
            usage_context=request.usage_context,
            ai_provider=request.ai_provider,
            ai_model=request.ai_model,
            related_resource_id=request.related_resource_id,
            related_resource_type=request.related_resource_type,
            description=request.description
        )

        await self.db.commit()

        return TokenUsageResponse(
            success=True,
            tokens_consumed=request.amount,
            new_balance=wallet.balance,
            transaction_id=transaction.id
        )

    async def check_and_reserve(
        self,
        user_id: int,
        account_id: UUID,
        required_tokens: int
    ) -> bool:
        """Check if user has enough tokens (pre-check before expensive operation)."""
        wallet = await self.get_or_create_wallet(user_id, account_id)
        return wallet.balance >= required_tokens

    # =========================================================================
    # TRANSACTION HISTORY
    # =========================================================================

    async def get_transactions(
        self,
        user_id: int,
        account_id: UUID,
        page: int = 1,
        page_size: int = 20,
        transaction_type: TransactionType | None = None
    ) -> TokenTransactionList:
        """Get paginated transaction history."""
        wallet = await self.get_or_create_wallet(user_id, account_id)

        # Build query
        stmt = select(TokenTransaction).where(
            TokenTransaction.wallet_id == wallet.id
        )
        if transaction_type:
            stmt = stmt.where(TokenTransaction.type == transaction_type)

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0

        # Paginate
        stmt = stmt.order_by(TokenTransaction.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(stmt)
        transactions = result.scalars().all()

        return TokenTransactionList(
            transactions=[TokenTransactionRead.model_validate(t) for t in transactions],
            total=total,
            page=page,
            page_size=page_size,
            has_more=(page * page_size) < total
        )

    # =========================================================================
    # PACKAGES
    # =========================================================================

    async def get_active_packages(self) -> list[TokenPackageRead]:
        """Get all active token packages."""
        stmt = select(TokenPackage).where(
            TokenPackage.is_active == True
        ).order_by(TokenPackage.sort_order)

        result = await self.db.execute(stmt)
        packages = result.scalars().all()

        return [TokenPackageRead.model_validate(p) for p in packages]


# =========================================================================
# DEPENDENCY INJECTION
# =========================================================================

async def get_token_service(db: AsyncSession) -> TokenService:
    """Dependency for FastAPI routes."""
    return TokenService(db)
