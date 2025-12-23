"""
MARKETTINA v3.0 - AI Token Middleware
Middleware and dependencies for token-gated AI operations
"""

import logging
from collections.abc import Callable
from functools import wraps

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.dependencies.auth_deps import get_current_user
from app.domain.auth.models import User
from app.domain.billing.models import ServicePricing, ServiceType
from app.domain.billing.token_models import AIProvider, UsageContext
from app.domain.billing.token_service import InsufficientTokensException, TokenService
from app.infrastructure.database import get_async_db

logger = logging.getLogger(__name__)


# =============================================================================
# TOKEN COST CONFIGURATION (Based on v3 ERD Service Pricing)
# =============================================================================

# Default token costs per operation (fallback if not in DB)
DEFAULT_TOKEN_COSTS = {
    # Content Generation
    "content_generation_gpt4": 100,
    "content_generation_gpt3": 25,
    "content_generation_claude": 80,
    "content_generation_llama": 10,  # Free tier

    # Image Generation
    "image_generation_dalle3": 500,
    "image_generation_stability": 300,
    "image_generation_replicate": 200,

    # Video Generation
    "video_generation_heygen": 2000,
    "video_generation_runway": 1500,

    # Analytics
    "sentiment_analysis": 50,
    "competitor_analysis": 150,
    "lead_enrichment": 100,

    # Marketing
    "email_campaign": 25,
    "social_post": 15,
}


async def get_token_cost(
    service_type: ServiceType,
    subtype: str | None,
    db: AsyncSession
) -> int:
    """Get token cost from database, fallback to defaults."""
    from sqlalchemy import and_, select

    stmt = select(ServicePricing).where(
        and_(
            ServicePricing.service_type == service_type,
            ServicePricing.is_active == True
        )
    )
    if subtype:
        stmt = stmt.where(ServicePricing.service_subtype == subtype)

    result = await db.execute(stmt)
    pricing = result.scalar_one_or_none()

    if pricing:
        return pricing.token_cost

    # Fallback to default
    key = f"{service_type.value}_{subtype}" if subtype else service_type.value
    return DEFAULT_TOKEN_COSTS.get(key, 50)  # Default 50 if not found


# =============================================================================
# TOKEN GATE DEPENDENCY
# =============================================================================

class TokenGate:
    """
    Dependency for gating API endpoints with token costs.

    Usage:
        @router.post("/generate")
        async def generate_content(
            gate: TokenGate = Depends(TokenGate(ServiceType.CONTENT_GENERATION, "gpt4", 100))
        ):
            # Tokens already deducted if we get here
            ...
    """

    def __init__(
        self,
        service_type: ServiceType,
        subtype: str | None = None,
        fixed_cost: int | None = None,
        ai_provider: AIProvider | None = None,
        ai_model: str | None = None
    ):
        self.service_type = service_type
        self.subtype = subtype
        self.fixed_cost = fixed_cost
        self.ai_provider = ai_provider
        self.ai_model = ai_model

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
    ) -> dict:
        """Check and deduct tokens. Returns transaction info."""
        account_id = current_user.default_account_id
        if not account_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no associated account"
            )

        # Determine cost
        if self.fixed_cost is not None:
            cost = self.fixed_cost
        else:
            cost = await get_token_cost(self.service_type, self.subtype, db)

        # Create service and attempt deduction
        service = TokenService(db)

        try:
            wallet = await service.get_or_create_wallet(current_user.id, account_id)

            # Check balance first
            if wallet.balance < cost:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "error": "insufficient_tokens",
                        "required": cost,
                        "available": wallet.balance,
                        "deficit": cost - wallet.balance,
                        "purchase_url": "/api/v1/tokens/packages"
                    }
                )

            # Deduct tokens
            transaction = await service.debit_tokens(
                wallet=wallet,
                amount=cost,
                usage_context=UsageContext(self._map_service_to_context()),
                ai_provider=self.ai_provider,
                ai_model=self.ai_model or self.subtype,
                description=f"API call: {self.service_type.value}"
            )

            await db.commit()

            logger.info(
                f"Token gate passed: user={current_user.id}, "
                f"cost={cost}, new_balance={wallet.balance}"
            )

            return {
                "tokens_consumed": cost,
                "transaction_id": str(transaction.id),
                "remaining_balance": wallet.balance
            }

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

    def _map_service_to_context(self) -> str:
        """Map service type to usage context."""
        mapping = {
            ServiceType.CONTENT_GENERATION: "ai_generation",
            ServiceType.IMAGE_GENERATION: "image_generation",
            ServiceType.VIDEO_GENERATION: "video_generation",
            ServiceType.SENTIMENT_ANALYSIS: "analytics",
            ServiceType.COMPETITOR_ANALYSIS: "analytics",
            ServiceType.LEAD_ENRICHMENT: "analytics",
            ServiceType.EMAIL_CAMPAIGN: "ai_generation",
            ServiceType.SOCIAL_POST: "ai_generation",
        }
        return mapping.get(self.service_type, "other")


# =============================================================================
# DECORATOR FOR TOKEN-GATED FUNCTIONS
# =============================================================================

def require_tokens(
    cost: int,
    service_type: ServiceType = ServiceType.CONTENT_GENERATION,
    context: UsageContext = UsageContext.AI_GENERATION,
    provider: AIProvider | None = None,
    model: str | None = None
):
    """
    Decorator for service functions that require token deduction.

    Usage:
        @require_tokens(cost=100, service_type=ServiceType.CONTENT_GENERATION)
        async def generate_post(user_id: int, account_id: UUID, prompt: str, db: AsyncSession):
            # Tokens deducted before this runs
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract required params
            user_id = kwargs.get("user_id")
            account_id = kwargs.get("account_id")
            db = kwargs.get("db")

            if not all([user_id, account_id, db]):
                raise ValueError(
                    "require_tokens decorator needs user_id, account_id, and db in kwargs"
                )

            service = TokenService(db)
            wallet = await service.get_or_create_wallet(user_id, account_id)

            # Check and deduct
            if wallet.balance < cost:
                raise InsufficientTokensException(required=cost, available=wallet.balance)

            await service.debit_tokens(
                wallet=wallet,
                amount=cost,
                usage_context=context,
                ai_provider=provider,
                ai_model=model,
                description=f"{func.__name__}"
            )

            # Call the actual function
            result = await func(*args, **kwargs)

            # Commit after successful operation
            await db.commit()

            return result

        return wrapper
    return decorator


# =============================================================================
# FREE TIER CHECK
# =============================================================================

async def is_free_tier_user(user: User, db: AsyncSession) -> bool:
    """Check if user is on free tier (use free models only)."""
    from sqlalchemy import select

    from app.domain.billing.models import Subscription

    account_id = user.default_account_id
    if not account_id:
        return True  # No account = free tier

    stmt = select(Subscription).where(Subscription.account_id == account_id)
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()

    if not subscription:
        return True  # No subscription = free tier

    return subscription.plan_id == "tier_free"


async def get_user_tier_models(user: User, db: AsyncSession) -> dict:
    """Get AI models available for user's tier."""
    is_free = await is_free_tier_user(user, db)

    if is_free:
        return {
            "text": ["llama-3.1-8b", "qwen-2.5"],
            "image": [],  # No image gen for free
            "video": [],  # No video gen for free
        }
    return {
        "text": ["gpt-4-turbo", "claude-3-sonnet", "llama-3.1-70b", "qwen-2.5-72b"],
        "image": ["dall-e-3", "stability-xl"],
        "video": ["heygen-avatar"],
    }
