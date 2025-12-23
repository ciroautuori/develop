"""
MARKETTINA v3.0 - Billing Context
Invoices, ServicePricing, PromoCodes, Referrals, Token Economy
"""

from .models import (
    BillingInterval,
    DiscountType,
    Invoice,
    InvoiceItem,
    InvoiceStatus,
    PromoCode,
    PromoRedemption,
    ReferralProgram,
    ServicePricing,
    ServiceType,
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
)
from .routers import admin_router, router
from .schemas import (
    BillingAddress,
    InvoiceCreate,
    InvoiceItemCreate,
    InvoiceItemRead,
    InvoiceRead,
    InvoiceSummary,
    InvoiceUpdate,
    PromoCodeCreate,
    PromoCodeRead,
    PromoCodeUpdate,
    PromoCodeValidate,
    PromoCodeValidationResult,
    ReferralCodeApply,
    ReferralProgramCreate,
    ReferralProgramRead,
    ReferralResult,
    ServicePricingCreate,
    ServicePricingRead,
    ServicePricingUpdate,
    ServiceUsageStat,
    TokenBalanceRead,
    TokenConsumptionRequest,
    TokenConsumptionResult,
    UsageStatsPeriod,
    UsageStatsRead,
    UsageStatsRequest,
)
from .services import (
    BillingService,
    TokenConsumptionService,
    get_billing_service,
    get_token_consumption_service,
)
from .token_models import (
    AIProvider,
    TokenPackage,
    TokenTransaction,
    TokenWallet,
    TransactionType,
    UsageContext,
)
from .token_router import admin_router as token_admin_router, router as token_router
from .token_schemas import (
    InsufficientTokensError,
    SubscriptionPlanList,
    SubscriptionPlanRead,
    TokenBalanceResponse,
    TokenPackageList,
    TokenPackageRead,
    TokenPurchaseRequest,
    TokenPurchaseResponse,
    TokenTransactionList,
    TokenTransactionRead,
    TokenUsageRequest,
    TokenUsageResponse,
    TokenUsageStats,
    TokenWalletRead,
)
from .token_service import TokenService, get_token_service

__all__ = [
    # Models
    "Invoice", "InvoiceItem", "InvoiceStatus",
    "ServicePricing", "ServiceType",
    "PromoCode", "PromoRedemption", "DiscountType",
    "ReferralProgram",
    "Subscription", "SubscriptionPlan", "SubscriptionStatus", "BillingInterval",
    "TokenWallet", "TokenPackage", "TokenTransaction", "TransactionType", "UsageContext", "AIProvider",
    # Schemas (legacy)
    "ServicePricingCreate", "ServicePricingUpdate", "ServicePricingRead",
    "InvoiceCreate", "InvoiceUpdate", "InvoiceRead", "InvoiceSummary",
    "InvoiceItemCreate", "InvoiceItemRead", "BillingAddress",
    "PromoCodeCreate", "PromoCodeUpdate", "PromoCodeRead",
    "PromoCodeValidate", "PromoCodeValidationResult",
    "ReferralProgramCreate", "ReferralProgramRead", "ReferralCodeApply", "ReferralResult",
    "TokenConsumptionRequest", "TokenConsumptionResult", "TokenBalanceRead",
    "UsageStatsRequest", "UsageStatsRead", "UsageStatsPeriod", "ServiceUsageStat",
    # Schemas (v3.0)
    "TokenWalletRead", "TokenBalanceResponse", "TokenPackageRead", "TokenPackageList",
    "TokenTransactionRead", "TokenTransactionList",
    "TokenPurchaseRequest", "TokenPurchaseResponse",
    "TokenUsageRequest", "TokenUsageResponse",
    "InsufficientTokensError", "TokenUsageStats",
    "SubscriptionPlanRead", "SubscriptionPlanList",
    # Services
    "BillingService", "TokenConsumptionService",
    "get_billing_service", "get_token_consumption_service",
    "TokenService", "get_token_service",
    # Routers
    "router", "admin_router",
    "token_router", "token_admin_router",
]
