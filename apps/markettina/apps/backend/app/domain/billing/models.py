"""
MARKETTINA v2.0 - Billing Context Models
Invoices, ServicePricing, PromoCodes, Referrals
"""

import enum
from datetime import date

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.domain.shared.base_model import SoftDeleteMixin, TimestampMixin, VersionMixin
from app.infrastructure.database import Base


class InvoiceStatus(str, enum.Enum):
    """Invoice status."""
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class ServiceType(str, enum.Enum):
    """AI service types for pricing."""
    CONTENT_GENERATION = "content_generation"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    LEAD_ENRICHMENT = "lead_enrichment"
    EMAIL_CAMPAIGN = "email_campaign"
    SOCIAL_POST = "social_post"


class DiscountType(str, enum.Enum):
    """Promo code discount types."""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    BONUS_TOKENS = "bonus_tokens"


class ServicePricing(Base, TimestampMixin, SoftDeleteMixin):
    """
    ServicePricing - Dynamic pricing for AI services.
    Allows different token costs per service type.
    """
    __tablename__ = "service_pricing"
    __table_args__ = (
        UniqueConstraint("service_type", "service_subtype", "effective_from", name="uq_service_pricing"),
        Index("ix_service_pricing_active", "service_type", "is_active"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Service identification
    service_type = Column(SQLEnum(ServiceType), nullable=False)
    service_subtype = Column(String(100), nullable=True)  # e.g., "gpt-4", "dall-e-3"

    # Pricing
    token_cost = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Validity
    is_active = Column(Boolean, nullable=False, default=True)
    effective_from = Column(Date, nullable=False, default=date.today)
    effective_to = Column(Date, nullable=True)

    def __repr__(self):
        return f"<ServicePricing {self.service_type.value}: {self.token_cost} tokens>"


class Invoice(Base, TimestampMixin, SoftDeleteMixin, VersionMixin):
    """
    Invoice - Billing records for token purchases.
    """
    __tablename__ = "invoices"
    __table_args__ = (
        Index("ix_invoices_account_status", "account_id", "status"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Foreign key
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False)

    # Amounts (in cents to avoid floating point issues)
    subtotal_cents = Column(Integer, nullable=False, default=0)
    discount_cents = Column(Integer, nullable=False, default=0)
    tax_cents = Column(Integer, nullable=False, default=0)
    total_cents = Column(Integer, nullable=False, default=0)

    # Currency
    currency = Column(String(3), nullable=False, default="EUR")

    # Status
    status = Column(SQLEnum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT)

    # Dates
    issue_date = Column(Date, nullable=False, default=date.today)
    due_date = Column(Date, nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Payment details
    stripe_invoice_id = Column(String(255), unique=True, nullable=True)
    stripe_payment_intent_id = Column(String(255), nullable=True)

    # Billing info (snapshot at invoice time)
    billing_name = Column(String(255), nullable=True)
    billing_email = Column(String(255), nullable=True)
    billing_address = Column(JSONB, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Relationships
    items = relationship("InvoiceItem", back_populates="invoice", lazy="dynamic")

    def __repr__(self):
        return f"<Invoice {self.invoice_number} ({self.status.value})>"


class InvoiceItem(Base, TimestampMixin):
    """
    InvoiceItem - Line items for invoices.
    """
    __tablename__ = "invoice_items"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Foreign key
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)

    # Item details
    description = Column(String(500), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price_cents = Column(Integer, nullable=False)
    total_cents = Column(Integer, nullable=False)

    # Token package reference (if applicable)
    token_package_id = Column(Integer, ForeignKey("token_packages.id"), nullable=True)
    tokens_amount = Column(Integer, nullable=True)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")


class PromoCode(Base, TimestampMixin, SoftDeleteMixin):
    """
    PromoCode - Discount codes for token purchases.
    """
    __tablename__ = "promo_codes"
    __table_args__ = (
        CheckConstraint("max_uses IS NULL OR current_uses <= max_uses", name="ck_promo_uses"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Code
    code = Column(String(50), unique=True, nullable=False, index=True)

    # Discount
    discount_type = Column(SQLEnum(DiscountType), nullable=False)
    discount_value = Column(Numeric(10, 2), nullable=False)  # percentage or fixed amount

    # Validity
    is_active = Column(Boolean, nullable=False, default=True)
    valid_from = Column(DateTime(timezone=True), nullable=False, default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=True)

    # Usage limits
    max_uses = Column(Integer, nullable=True)  # null = unlimited
    current_uses = Column(Integer, nullable=False, default=0)
    max_uses_per_account = Column(Integer, nullable=True, default=1)

    # Restrictions
    min_purchase_cents = Column(Integer, nullable=True)
    applicable_packages = Column(JSONB, nullable=True)  # list of package IDs

    # Metadata
    description = Column(Text, nullable=True)
    campaign_name = Column(String(255), nullable=True)

    # Relationships
    redemptions = relationship("PromoRedemption", back_populates="promo_code", lazy="dynamic")

    def __repr__(self):
        return f"<PromoCode {self.code} ({self.discount_type.value})>"


class PromoRedemption(Base, TimestampMixin):
    """
    PromoRedemption - Tracks promo code usage.
    """
    __tablename__ = "promo_redemptions"
    __table_args__ = (
        UniqueConstraint("promo_code_id", "account_id", "invoice_id", name="uq_promo_redemption"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Foreign keys
    promo_code_id = Column(UUID(as_uuid=True), ForeignKey("promo_codes.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True)

    # Redemption details
    discount_applied_cents = Column(Integer, nullable=False)
    redeemed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    promo_code = relationship("PromoCode", back_populates="redemptions")


class ReferralProgram(Base, TimestampMixin, SoftDeleteMixin):
    """
    ReferralProgram - Referral tracking for accounts.
    """
    __tablename__ = "referral_programs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Referrer account
    referrer_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Referral code
    referral_code = Column(String(50), unique=True, nullable=False, index=True)

    # Rewards
    referrer_bonus_tokens = Column(Integer, nullable=False, default=100)
    referee_bonus_tokens = Column(Integer, nullable=False, default=50)

    # Stats
    total_referrals = Column(Integer, nullable=False, default=0)
    successful_referrals = Column(Integer, nullable=False, default=0)
    total_tokens_earned = Column(Integer, nullable=False, default=0)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<ReferralProgram {self.referral_code}>"


# ============================================================================
# SUBSCRIPTION & PLANS (v3.0 Dynamic)
# ============================================================================

class BillingInterval(str, enum.Enum):
    """Billing frequency."""
    MONTHLY = "monthly"
    ANNUAL = "annual"


class SubscriptionStatus(str, enum.Enum):
    """Stripe subscription status."""
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"


class SubscriptionPlan(Base, TimestampMixin):
    """
    SubscriptionPlan - Dynamic SaaS plans.
    Replaces hardcoded Enums. Allows creating custom tiers.
    """
    __tablename__ = "subscription_plans"

    id = Column(String(50), primary_key=True)  # e.g., "tier_free", "tier_pro_monthly"

    # Display info
    name = Column(String(100), nullable=False)  # "Free Tier", "Pro"
    description = Column(Text, nullable=True)

    # Billing
    billing_interval = Column(SQLEnum(BillingInterval), nullable=False)
    price_cents = Column(Integer, nullable=False, default=0)

    # Entitlements
    included_users = Column(Integer, nullable=False, default=1)
    included_tokens = Column(Integer, nullable=False, default=0)  # Monthly allowance
    max_social_accounts = Column(Integer, nullable=True)
    max_campaigns = Column(Integer, nullable=True)

    # Feature Flags (JSON)
    features = Column(JSONB, nullable=False, default=dict)
    # e.g., {"api_access": true, "advanced_analytics": false}

    # Limits (JSON)
    limits = Column(JSONB, nullable=True)

    # Configuration
    trial_days = Column(Integer, default=14)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    def __repr__(self):
        return f"<SubscriptionPlan {self.name} - {self.price_cents/100:.2f}>"


class Subscription(Base, TimestampMixin, VersionMixin):
    """
    Subscription - Active link between Account and Plan.
    Manages billing lifecycle and renewal.
    """
    __tablename__ = "subscriptions"
    __table_args__ = (
        Index("ix_subscriptions_status", "status"),
        UniqueConstraint("account_id", name="uq_account_active_subscription"),  # One active sub per account?
        # Actually standard practice is one active plan, but history is kept.
        # Let's enforce uniqueness only if status is active? No, easier to rely on logic.
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Relationships
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    plan_id = Column(String(50), ForeignKey("subscription_plans.id"), nullable=False, index=True)

    # Status
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.TRIALING)
    quantity = Column(Integer, default=1)

    # Period
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)

    # Trial
    trial_start = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)

    # Payment Provider
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)

    # Cancellation
    cancel_at_period_end = Column(Boolean, default=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(String(255), nullable=True)

    # Relationships
    plan = relationship("SubscriptionPlan")
    account = relationship("Account", back_populates="subscription")
    # NOTE: Backref 'subscription' on active account. This might conflict if multiple rows existed.
    # For MVP v3.0, we assume one row per account that Updates, or we SoftDelete old ones.
    # Given the ERD shows "subscriptions" table, usually we keep history.
    # If keeping history, 'account.subscription' should point to the LATEST/ACTIVE one.
    # For now, let's keep it simple: 1 row per account that gets updated.

    def __repr__(self):
        return f"<Subscription {self.account_id} -> {self.plan_id} ({self.status.value})>"
