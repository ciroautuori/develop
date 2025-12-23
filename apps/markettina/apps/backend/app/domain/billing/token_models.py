"""
MARKETTINA v3.0 - Token Economy Models
TokenWallet, TokenPackage, TokenTransaction
"""

import enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.domain.shared.base_model import TimestampMixin, VersionMixin
from app.infrastructure.database import Base


class TransactionType(str, enum.Enum):
    """Token transaction types."""
    PURCHASE = "purchase"  # Purchased a token package
    USAGE = "usage"  # Consumed tokens for AI service
    BONUS = "bonus"  # Awarded bonus tokens (referral, promo)
    REFUND = "refund"  # Refugee usage or purchase
    ADJUSTMENT = "adjustment"  # Admin correction
    SUBSCRIPTION_RENEWAL = "subscription_renewal"  # Monthly allowance


class UsageContext(str, enum.Enum):
    """Context for token usage."""
    AI_GENERATION = "ai_generation"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    ANALYTICS = "analytics"
    STORAGE = "storage"
    OTHER = "other"


class AIProvider(str, enum.Enum):
    """AI Providers for tracking costs."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    STABILITY = "stability"
    REPLICATE = "replicate"
    GOOGLE = "google"
    QWEN = "qwen"
    LLAMA = "llama"
    OTHER = "other"


class TokenWallet(Base, TimestampMixin, VersionMixin):
    """
    TokenWallet - Stores the token balance for a user/account.
    One wallet per user per account.
    """
    __tablename__ = "token_wallets"
    __table_args__ = (
        UniqueConstraint("user_id", "account_id", name="uq_user_account_wallet"),
        CheckConstraint("balance >= 0", name="ck_wallet_balance_positive"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Ownership
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Balance
    balance = Column(Integer, nullable=False, default=0)

    # Lifetime Aggregate Stats (for analytics/gamification)
    total_purchased = Column(Integer, nullable=False, default=0)
    total_used = Column(Integer, nullable=False, default=0)
    total_bonus = Column(Integer, nullable=False, default=0)
    total_refunded = Column(Integer, nullable=False, default=0)

    # Financial aggregate
    total_spent_usd = Column(Numeric(10, 2), nullable=False, default=0.00)

    # Activity tracking
    last_purchase_at = Column(DateTime(timezone=True), nullable=True)
    last_usage_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    transactions = relationship("TokenTransaction", back_populates="wallet", lazy="dynamic", cascade="all, delete-orphan")
    account = relationship("Account", backref="token_wallets")
    user = relationship("User", backref="token_wallet")

    def __repr__(self):
        return f"<TokenWallet User:{self.user_id} Balance:{self.balance}>"


class TokenPackage(Base, TimestampMixin):
    """
    TokenPackage - Purchasable bundles of tokens.
    e.g. "Starter Pack" - 50,000 Tokens - $10.00
    """
    __tablename__ = "token_packages"

    id = Column(String(50), primary_key=True)  # e.g., "pack_starter_50k"

    # Display info
    name = Column(String(100), nullable=False)  # "Starter Pack"
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    badge = Column(String(50), nullable=True)  # "POPULAR", "BEST VALUE"

    # Value
    tokens = Column(Integer, nullable=False)
    bonus_tokens = Column(Integer, nullable=False, default=0)

    # Price
    price_usd = Column(Numeric(8, 2), nullable=False)

    # Configuration
    is_active = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<TokenPackage {self.slug}: {self.tokens} tokens>"


class TokenTransaction(Base, TimestampMixin):
    """
    TokenTransaction - Immutable ledger of all token movements.
    """
    __tablename__ = "token_transactions"
    __table_args__ = (
        Index("ix_token_tx_wallet_created", "wallet_id", "created_at"),
        Index("ix_token_tx_account_type", "account_id", "type"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Ownership
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("token_wallets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)

    # Transaction Details
    type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Integer, nullable=False)  # Positive for credit, Negative for debit

    # Snapshot of balance (for audit integrity)
    balance_before = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)

    # Financial / Commercial Link
    package_id = Column(String(50), ForeignKey("token_packages.id"), nullable=True)
    price_usd = Column(Numeric(10, 2), nullable=True)
    stripe_payment_intent_id = Column(String(255), nullable=True)

    # Usage Details (if type == USAGE)
    usage_context = Column(SQLEnum(UsageContext), nullable=True)
    ai_provider = Column(SQLEnum(AIProvider), nullable=True)
    ai_model = Column(String(100), nullable=True)  # e.g. "gpt-4-turbo"

    # Resource Link (what was created?)
    related_resource_id = Column(UUID(as_uuid=True), nullable=True)
    related_resource_type = Column(String(100), nullable=True)  # "post", "image", "analysis"

    # Metadata
    description = Column(Text, nullable=True)

    # Relationships
    wallet = relationship("TokenWallet", back_populates="transactions")
    package = relationship("TokenPackage")

    def __repr__(self):
        return f"<TokenTransaction {self.type} {self.amount} (Wal:{self.wallet_id})>"
