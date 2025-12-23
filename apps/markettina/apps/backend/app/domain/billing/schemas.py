"""
MARKETTINA v2.0 - Billing Context Schemas
Pydantic models for billing operations.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ============================================================================
# ENUMS
# ============================================================================

class InvoiceStatus(str, Enum):
    """Invoice status enumeration."""
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class ServiceType(str, Enum):
    """AI service types for pricing."""
    CONTENT_GENERATION = "content_generation"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    LEAD_ENRICHMENT = "lead_enrichment"
    EMAIL_CAMPAIGN = "email_campaign"
    SOCIAL_POST = "social_post"


class DiscountType(str, Enum):
    """Promo code discount types."""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    BONUS_TOKENS = "bonus_tokens"


# ============================================================================
# SERVICE PRICING SCHEMAS
# ============================================================================

class ServicePricingBase(BaseModel):
    """Base schema for service pricing."""
    service_type: ServiceType
    service_subtype: str | None = Field(None, max_length=100)
    token_cost: int = Field(..., gt=0)
    name: str = Field(..., max_length=255)
    description: str | None = None
    is_active: bool = True
    effective_from: date = Field(default_factory=date.today)
    effective_to: date | None = None

    @field_validator("effective_to")
    @classmethod
    def validate_date_range(cls, v: date | None, info) -> date | None:
        """Ensure effective_to is after effective_from."""
        if v and "effective_from" in info.data:
            if v <= info.data["effective_from"]:
                raise ValueError("effective_to must be after effective_from")
        return v


class ServicePricingCreate(ServicePricingBase):
    """Schema for creating service pricing."""


class ServicePricingUpdate(BaseModel):
    """Schema for updating service pricing."""
    service_subtype: str | None = Field(None, max_length=100)
    token_cost: int | None = Field(None, gt=0)
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    is_active: bool | None = None
    effective_to: date | None = None


class ServicePricingRead(ServicePricingBase):
    """Schema for reading service pricing."""
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# INVOICE SCHEMAS
# ============================================================================

class BillingAddress(BaseModel):
    """Billing address value object."""
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str = "IT"


class InvoiceItemBase(BaseModel):
    """Base schema for invoice items."""
    description: str = Field(..., max_length=500)
    quantity: int = Field(1, gt=0)
    unit_price_cents: int = Field(..., ge=0)
    tokens_amount: int | None = Field(None, ge=0)


class InvoiceItemCreate(InvoiceItemBase):
    """Schema for creating invoice items."""
    token_package_id: int | None = None


class InvoiceItemRead(InvoiceItemBase):
    """Schema for reading invoice items."""
    id: UUID
    invoice_id: UUID
    total_cents: int
    token_package_id: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceBase(BaseModel):
    """Base schema for invoices."""
    billing_name: str | None = Field(None, max_length=255)
    billing_email: str | None = Field(None, max_length=255)
    billing_address: BillingAddress | None = None
    notes: str | None = None
    currency: str = Field("EUR", max_length=3)
    due_date: date | None = None


class InvoiceCreate(InvoiceBase):
    """Schema for creating invoices."""
    account_id: UUID
    items: list[InvoiceItemCreate] = Field(..., min_length=1)
    promo_code: str | None = None


class InvoiceUpdate(BaseModel):
    """Schema for updating invoices."""
    billing_name: str | None = Field(None, max_length=255)
    billing_email: str | None = Field(None, max_length=255)
    billing_address: BillingAddress | None = None
    notes: str | None = None
    status: InvoiceStatus | None = None
    due_date: date | None = None


class InvoiceRead(InvoiceBase):
    """Schema for reading invoices."""
    id: UUID
    account_id: UUID
    invoice_number: str
    subtotal_cents: int
    discount_cents: int
    tax_cents: int
    total_cents: int
    status: InvoiceStatus
    issue_date: date
    paid_at: datetime | None = None
    stripe_invoice_id: str | None = None
    items: list[InvoiceItemRead] = []
    created_at: datetime
    updated_at: datetime | None = None
    version: int = 1

    model_config = ConfigDict(from_attributes=True)


class InvoiceSummary(BaseModel):
    """Summary schema for invoice lists."""
    id: UUID
    invoice_number: str
    total_cents: int
    currency: str
    status: InvoiceStatus
    issue_date: date
    billing_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# PROMO CODE SCHEMAS
# ============================================================================

class PromoCodeBase(BaseModel):
    """Base schema for promo codes."""
    code: str = Field(..., min_length=3, max_length=50)
    discount_type: DiscountType
    discount_value: Decimal = Field(..., gt=0)
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_until: datetime | None = None
    max_uses: int | None = Field(None, ge=1)
    max_uses_per_account: int | None = Field(1, ge=1)
    min_purchase_cents: int | None = Field(None, ge=0)
    applicable_packages: list[int] | None = None
    description: str | None = None
    campaign_name: str | None = Field(None, max_length=255)

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Normalize promo code to uppercase."""
        return v.upper().strip()

    @field_validator("discount_value")
    @classmethod
    def validate_discount(cls, v: Decimal, info) -> Decimal:
        """Validate discount value based on type."""
        if "discount_type" in info.data:
            if info.data["discount_type"] == DiscountType.PERCENTAGE:
                if v > 100:
                    raise ValueError("Percentage discount cannot exceed 100%")
        return v


class PromoCodeCreate(PromoCodeBase):
    """Schema for creating promo codes."""
    is_active: bool = True


class PromoCodeUpdate(BaseModel):
    """Schema for updating promo codes."""
    discount_value: Decimal | None = Field(None, gt=0)
    valid_until: datetime | None = None
    max_uses: int | None = Field(None, ge=1)
    is_active: bool | None = None
    description: str | None = None
    campaign_name: str | None = Field(None, max_length=255)


class PromoCodeRead(PromoCodeBase):
    """Schema for reading promo codes."""
    id: UUID
    is_active: bool
    current_uses: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PromoCodeValidate(BaseModel):
    """Schema for promo code validation request."""
    code: str
    account_id: UUID
    purchase_cents: int = Field(..., gt=0)
    package_id: int | None = None


class PromoCodeValidationResult(BaseModel):
    """Schema for promo code validation response."""
    is_valid: bool
    discount_type: DiscountType | None = None
    discount_value: Decimal | None = None
    discount_cents: int | None = None
    bonus_tokens: int | None = None
    error_message: str | None = None


# ============================================================================
# REFERRAL PROGRAM SCHEMAS
# ============================================================================

class ReferralProgramBase(BaseModel):
    """Base schema for referral program."""
    referrer_bonus_tokens: int = Field(100, ge=0)
    referee_bonus_tokens: int = Field(50, ge=0)


class ReferralProgramCreate(ReferralProgramBase):
    """Schema for creating referral program."""
    referrer_account_id: UUID


class ReferralProgramRead(ReferralProgramBase):
    """Schema for reading referral program."""
    id: UUID
    referrer_account_id: UUID
    referral_code: str
    total_referrals: int
    successful_referrals: int
    total_tokens_earned: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ReferralCodeApply(BaseModel):
    """Schema for applying referral code."""
    referral_code: str = Field(..., min_length=3, max_length=50)
    referred_account_id: UUID


class ReferralResult(BaseModel):
    """Schema for referral application result."""
    success: bool
    referrer_tokens_awarded: int = 0
    referee_tokens_awarded: int = 0
    error_message: str | None = None


# ============================================================================
# TOKEN CONSUMPTION SCHEMAS
# ============================================================================

class TokenConsumptionRequest(BaseModel):
    """Schema for token consumption request."""
    account_id: UUID
    service_type: ServiceType
    service_subtype: str | None = None
    quantity: int = Field(1, ge=1)
    metadata: dict | None = None


class TokenConsumptionResult(BaseModel):
    """Schema for token consumption result."""
    success: bool
    tokens_consumed: int = 0
    remaining_balance: int = 0
    transaction_id: UUID | None = None
    error_message: str | None = None


class TokenBalanceRead(BaseModel):
    """Schema for reading token balance."""
    account_id: UUID
    balance: int
    total_purchased: int
    total_bonus: int
    total_used: int
    last_transaction_at: datetime | None = None


# ============================================================================
# USAGE STATS SCHEMAS
# ============================================================================

class UsageStatsPeriod(str, Enum):
    """Usage stats period."""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class UsageStatsRequest(BaseModel):
    """Schema for usage stats request."""
    account_id: UUID
    period: UsageStatsPeriod = UsageStatsPeriod.MONTH
    service_type: ServiceType | None = None


class ServiceUsageStat(BaseModel):
    """Schema for per-service usage stat."""
    service_type: ServiceType
    service_subtype: str | None = None
    total_tokens: int
    request_count: int


class UsageStatsRead(BaseModel):
    """Schema for reading usage stats."""
    account_id: UUID
    period: UsageStatsPeriod
    start_date: date
    end_date: date
    total_tokens_used: int
    services: list[ServiceUsageStat]
