"""
MARKETTINA v3.0 - Token Economy Schemas
Pydantic models for Token API
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.billing.token_models import AIProvider, TransactionType, UsageContext

# ============================================================================
# TOKEN WALLET SCHEMAS
# ============================================================================

class TokenWalletBase(BaseModel):
    """Base schema for token wallet."""
    balance: int = Field(ge=0, description="Current token balance")


class TokenWalletRead(TokenWalletBase):
    """Schema for reading wallet data."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: int
    account_id: UUID
    total_purchased: int
    total_used: int
    total_bonus: int
    total_refunded: int
    total_spent_usd: Decimal
    last_purchase_at: datetime | None
    last_usage_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TokenBalanceResponse(BaseModel):
    """Simple balance response."""
    balance: int
    total_used_today: int = 0
    estimated_remaining_days: int | None = None


# ============================================================================
# TOKEN PACKAGE SCHEMAS
# ============================================================================

class TokenPackageBase(BaseModel):
    """Base schema for token packages."""
    name: str = Field(max_length=100)
    slug: str = Field(max_length=100)
    description: str | None = None
    tokens: int = Field(gt=0)
    bonus_tokens: int = Field(ge=0, default=0)
    price_usd: Decimal = Field(ge=0)
    badge: str | None = None


class TokenPackageCreate(TokenPackageBase):
    """Schema for creating a token package."""
    id: str = Field(max_length=50, pattern=r"^[a-z0-9_]+$")
    is_active: bool = True
    sort_order: int = 0


class TokenPackageRead(TokenPackageBase):
    """Schema for reading token package data."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    @property
    def total_tokens(self) -> int:
        """Total tokens including bonus."""
        return self.tokens + self.bonus_tokens

    @property
    def price_per_1k_tokens(self) -> float:
        """Price per 1000 tokens."""
        total = self.tokens + self.bonus_tokens
        if total == 0:
            return 0.0
        return float(self.price_usd) / (total / 1000)


class TokenPackageList(BaseModel):
    """List of token packages."""
    packages: list[TokenPackageRead]
    count: int


# ============================================================================
# TOKEN TRANSACTION SCHEMAS
# ============================================================================

class TokenTransactionBase(BaseModel):
    """Base schema for transactions."""
    type: TransactionType
    amount: int
    description: str | None = None


class TokenTransactionCreate(TokenTransactionBase):
    """Schema for creating a transaction."""
    usage_context: UsageContext | None = None
    ai_provider: AIProvider | None = None
    ai_model: str | None = None
    related_resource_id: UUID | None = None
    related_resource_type: str | None = None


class TokenTransactionRead(TokenTransactionBase):
    """Schema for reading transaction data."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    wallet_id: UUID
    user_id: int
    account_id: UUID
    balance_before: int
    balance_after: int
    package_id: str | None
    price_usd: Decimal | None
    usage_context: UsageContext | None
    ai_provider: AIProvider | None
    ai_model: str | None
    related_resource_id: UUID | None
    related_resource_type: str | None
    created_at: datetime


class TokenTransactionList(BaseModel):
    """Paginated list of transactions."""
    transactions: list[TokenTransactionRead]
    total: int
    page: int
    page_size: int
    has_more: bool


# ============================================================================
# TOKEN OPERATIONS SCHEMAS
# ============================================================================

class TokenPurchaseRequest(BaseModel):
    """Request to purchase tokens."""
    package_id: str = Field(description="ID of the token package to purchase")
    payment_method_id: str | None = Field(None, description="Stripe payment method ID")


class TokenPurchaseResponse(BaseModel):
    """Response after token purchase."""
    success: bool
    transaction_id: UUID
    tokens_added: int
    new_balance: int
    stripe_payment_intent_id: str | None = None


class TokenUsageRequest(BaseModel):
    """Request to consume tokens."""
    amount: int = Field(gt=0, description="Number of tokens to consume")
    usage_context: UsageContext = Field(description="What the tokens are used for")
    ai_provider: AIProvider | None = None
    ai_model: str | None = None
    related_resource_id: UUID | None = None
    related_resource_type: str | None = None
    description: str | None = None


class TokenUsageResponse(BaseModel):
    """Response after token consumption."""
    success: bool
    tokens_consumed: int
    new_balance: int
    transaction_id: UUID


class TokenRefundRequest(BaseModel):
    """Request to refund tokens."""
    amount: int = Field(gt=0)
    reason: str = Field(max_length=500)
    original_transaction_id: UUID | None = None


class InsufficientTokensError(BaseModel):
    """Error response for insufficient tokens."""
    error: str = "insufficient_tokens"
    required: int
    available: int
    deficit: int


# ============================================================================
# SUBSCRIPTION PLAN SCHEMAS
# ============================================================================

class SubscriptionPlanRead(BaseModel):
    """Schema for reading subscription plan data."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    billing_interval: str
    price_cents: int
    included_users: int
    included_tokens: int
    max_social_accounts: int | None
    max_campaigns: int | None
    features: dict
    limits: dict | None
    trial_days: int | None
    is_active: bool


class SubscriptionPlanList(BaseModel):
    """List of subscription plans."""
    plans: list[SubscriptionPlanRead]


# ============================================================================
# USAGE ANALYTICS SCHEMAS
# ============================================================================

class TokenUsageStats(BaseModel):
    """Token usage statistics."""
    period: str  # "day", "week", "month"
    total_used: int
    total_purchased: int
    total_bonus: int
    average_daily_usage: float
    top_contexts: list[dict]  # [{context: "ai_generation", count: 100}]
    top_providers: list[dict]  # [{provider: "openai", count: 50}]
