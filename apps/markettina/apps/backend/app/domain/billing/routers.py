"""
MARKETTINA v2.0 - Billing Context Routers
FastAPI endpoints for billing operations.
"""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.dependencies.auth_deps import get_current_user
from app.domain.auth.models import User
from app.infrastructure.database.session import get_async_db

from .schemas import (
    # Invoice
    InvoiceCreate,
    InvoiceRead,
    InvoiceStatus,
    InvoiceSummary,
    InvoiceUpdate,
    # Promo Code
    PromoCodeCreate,
    PromoCodeRead,
    PromoCodeValidate,
    PromoCodeValidationResult,
    ReferralCodeApply,
    # Referral
    ReferralProgramCreate,
    ReferralProgramRead,
    ReferralResult,
    # Service Pricing
    ServicePricingCreate,
    ServicePricingRead,
    ServicePricingUpdate,
    ServiceType,
    TokenBalanceRead,
    # Token
    TokenConsumptionRequest,
    TokenConsumptionResult,
    UsageStatsPeriod,
    UsageStatsRead,
)
from .services import BillingService, TokenConsumptionService

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])
admin_router = APIRouter(prefix="/api/v1/admin/billing", tags=["admin-billing"])


# ============================================================================
# DEPENDENCIES
# ============================================================================

async def get_billing_service(db: AsyncSession = Depends(get_async_db)) -> BillingService:
    """Get billing service instance."""
    return BillingService(db)


async def get_token_service(db: AsyncSession = Depends(get_async_db)) -> TokenConsumptionService:
    """Get token consumption service instance."""
    return TokenConsumptionService(db)


# ============================================================================
# STRIPE CHECKOUT ENDPOINT
# ============================================================================

# Token packages configuration (matches frontend)
TOKEN_PACKAGES = {
    "starter": {"name": "Starter", "tokens": 2500, "price_cents": 4999},
    "growth": {"name": "Growth", "tokens": 5000, "price_cents": 9999},
    "pro": {"name": "Pro", "tokens": 7500, "price_cents": 14999},
    "agency": {"name": "Agency", "tokens": 15000, "price_cents": 24999},
}


@router.post("/checkout")
async def create_checkout_session(
    data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Create Stripe Checkout Session for token purchase.

    Returns checkout_url for redirect.
    """
    import stripe
    from app.core.config import settings

    package_id = data.get("package_id")
    if not package_id or package_id not in TOKEN_PACKAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid package_id. Valid: {list(TOKEN_PACKAGES.keys())}"
        )

    package = TOKEN_PACKAGES[package_id]

    # Check if Stripe is configured
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system not configured. Contact support."
        )

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": f"MARKETTINA {package['name']} - {package['tokens']:,} Token",
                        "description": f"Pacchetto {package['name']}: {package['tokens']:,} token per AI Marketing",
                    },
                    "unit_amount": package["price_cents"],
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{settings.FRONTEND_URL}/customer/tokens?success=true&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/customer/tokens?canceled=true",
            client_reference_id=str(current_user.id),
            metadata={
                "user_id": str(current_user.id),
                "package_id": package_id,
                "tokens": str(package["tokens"]),
            },
        )

        return {"checkout_url": checkout_session.url}

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment error: {str(e)}"
        )


# ============================================================================
# SERVICE PRICING ENDPOINTS (Admin only)
# ============================================================================

@admin_router.get("/pricing", response_model=list[ServicePricingRead])
async def list_service_pricing(
    active_only: bool = Query(True, description="Show only active pricing"),
    service: BillingService = Depends(get_billing_service),
    current_user: User = Depends(get_current_user)
):
    """
    List all service pricing entries.

    Returns pricing configuration for all AI services.
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return await service.list_service_pricing(active_only=active_only)


@admin_router.post("/pricing", response_model=ServicePricingRead, status_code=status.HTTP_201_CREATED)
async def create_service_pricing(
    data: ServicePricingCreate,
    service: BillingService = Depends(get_billing_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create new service pricing entry.

    Defines token cost for a specific AI service type.
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return await service.create_service_pricing(data)


@admin_router.put("/pricing/{pricing_id}", response_model=ServicePricingRead)
async def update_service_pricing(
    pricing_id: UUID = Path(..., description="Pricing entry ID"),
    data: ServicePricingUpdate = ...,
    service: BillingService = Depends(get_billing_service),
    current_user: User = Depends(get_current_user)
):
    """Update existing service pricing entry."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return await service.update_service_pricing(pricing_id, data)


# ============================================================================
# PUBLIC PRICING ENDPOINT
# ============================================================================

@router.get("/pricing", response_model=list[ServicePricingRead])
async def get_public_pricing(
    service: BillingService = Depends(get_billing_service)
):
    """
    Get current service pricing.

    Returns active pricing for all AI services (public endpoint).
    """
    return await service.list_service_pricing(active_only=True)


@router.get("/pricing/{service_type}", response_model=ServicePricingRead)
async def get_service_price(
    service_type: ServiceType = Path(..., description="Service type"),
    service_subtype: str | None = Query(None, description="Service subtype (e.g., gpt-4)"),
    billing_service: BillingService = Depends(get_billing_service)
):
    """Get pricing for specific service type."""
    pricing = await billing_service.get_service_pricing(service_type, service_subtype)
    if not pricing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pricing not found for {service_type.value}"
        )
    return pricing


# ============================================================================
# INVOICE ENDPOINTS
# ============================================================================

@router.post("/invoices", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    data: InvoiceCreate,
    service: BillingService = Depends(get_billing_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create new invoice.

    Creates invoice with items and applies promo code if provided.
    """
    # Verify user can create invoice for this account
    # TODO: Add account ownership verification
    return await service.create_invoice(data)


@router.get("/invoices", response_model=list[InvoiceSummary])
async def list_invoices(
    account_id: UUID = Query(..., description="Account ID"),
    status_filter: InvoiceStatus | None = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    service: BillingService = Depends(get_billing_service),
    current_user: User = Depends(get_current_user)
):
    """
    List invoices for account.

    Returns paginated list of invoices with summary info.
    """
    invoices = await service.list_invoices(account_id, status_filter, limit, offset)
    return [InvoiceSummary.model_validate(inv) for inv in invoices]


@router.get("/invoices/{invoice_id}", response_model=InvoiceRead)
async def get_invoice(
    invoice_id: UUID = Path(..., description="Invoice ID"),
    service: BillingService = Depends(get_billing_service),
    current_user: User = Depends(get_current_user)
):
    """Get invoice details with items."""
    invoice = await service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return invoice


@router.get("/invoices/by-number/{invoice_number}", response_model=InvoiceRead)
async def get_invoice_by_number(
    invoice_number: str = Path(..., description="Invoice number"),
    service: BillingService = Depends(get_billing_service),
    current_user: User = Depends(get_current_user)
):
    """Get invoice by invoice number."""
    invoice = await service.get_invoice_by_number(invoice_number)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return invoice


@router.patch("/invoices/{invoice_id}", response_model=InvoiceRead)
async def update_invoice(
    invoice_id: UUID = Path(..., description="Invoice ID"),
    data: InvoiceUpdate = ...,
    service: BillingService = Depends(get_billing_service),
    current_user: User = Depends(get_current_user)
):
    """Update invoice (only draft/pending status)."""
    return await service.update_invoice(invoice_id, data)


@router.post("/invoices/{invoice_id}/pay", response_model=InvoiceRead)
async def mark_invoice_paid(
    invoice_id: UUID = Path(..., description="Invoice ID"),
    stripe_payment_intent_id: str | None = Query(None, description="Stripe payment intent"),
    service: BillingService = Depends(get_billing_service),
    current_user: User = Depends(get_current_user)
):
    """
    Mark invoice as paid.

    Called after successful payment confirmation.
    """
    return await service.mark_invoice_paid(invoice_id, stripe_payment_intent_id)


# ============================================================================
# PROMO CODE ENDPOINTS
# ============================================================================

@admin_router.post("/promo-codes", response_model=PromoCodeRead, status_code=status.HTTP_201_CREATED)
async def create_promo_code(
    data: PromoCodeCreate,
    service: BillingService = Depends(get_billing_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create new promo code (Admin only).

    Supports percentage, fixed amount, or bonus tokens discounts.
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return await service.create_promo_code(data)


@router.post("/promo-codes/validate", response_model=PromoCodeValidationResult)
async def validate_promo_code(
    data: PromoCodeValidate,
    service: BillingService = Depends(get_billing_service),
    current_user: User = Depends(get_current_user)
):
    """
    Validate promo code for account and purchase.

    Checks validity, usage limits, and calculates discount.
    """
    return await service.validate_promo_code(data)


# ============================================================================
# REFERRAL PROGRAM ENDPOINTS
# ============================================================================

@router.post("/referral", response_model=ReferralProgramRead, status_code=status.HTTP_201_CREATED)
async def create_referral_program(
    data: ReferralProgramCreate,
    service: BillingService = Depends(get_billing_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create referral program for account.

    Each account can have one referral program with unique code.
    """
    return await service.create_referral_program(data)


@router.get("/referral/{account_id}", response_model=ReferralProgramRead)
async def get_referral_program(
    account_id: UUID = Path(..., description="Account ID"),
    service: BillingService = Depends(get_billing_service),
    current_user: User = Depends(get_current_user)
):
    """Get referral program for account."""
    program = await service.get_referral_program(account_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral program not found"
        )
    return program


@router.post("/referral/apply", response_model=ReferralResult)
async def apply_referral_code(
    data: ReferralCodeApply,
    service: BillingService = Depends(get_billing_service),
    current_user: User = Depends(get_current_user)
):
    """
    Apply referral code for new account.

    Awards bonus tokens to both referrer and referee.
    """
    return await service.apply_referral_code(data)


# ============================================================================
# TOKEN CONSUMPTION ENDPOINTS
# ============================================================================

@router.post("/tokens/consume", response_model=TokenConsumptionResult)
async def consume_tokens(
    request: TokenConsumptionRequest,
    service: TokenConsumptionService = Depends(get_token_service),
    current_user: User = Depends(get_current_user)
):
    """
    Consume tokens for AI service operation.

    Validates balance and records consumption.
    """
    return await service.consume_tokens(request)


@router.get("/tokens/balance/{account_id}", response_model=TokenBalanceRead)
async def get_token_balance(
    account_id: UUID = Path(..., description="Account ID"),
    current_user: User = Depends(get_current_user)
):
    """
    Get token balance for account.

    Returns current balance and usage statistics.
    """
    # TODO: Implement when TokenWallet is available
    return TokenBalanceRead(
        account_id=account_id,
        balance=0,
        total_purchased=0,
        total_bonus=0,
        total_used=0
    )


@router.get("/tokens/cost/{service_type}")
async def get_token_cost(
    service_type: ServiceType = Path(..., description="Service type"),
    service_subtype: str | None = Query(None, description="Service subtype"),
    service: TokenConsumptionService = Depends(get_token_service)
):
    """
    Get token cost for specific service.

    Returns number of tokens required for one operation.
    """
    cost = await service.get_token_cost(service_type, service_subtype)
    return {"service_type": service_type.value, "service_subtype": service_subtype, "token_cost": cost}


# ============================================================================
# USAGE STATS ENDPOINTS
# ============================================================================

@router.get("/usage/{account_id}", response_model=UsageStatsRead)
async def get_usage_stats(
    account_id: UUID = Path(..., description="Account ID"),
    period: UsageStatsPeriod = Query(UsageStatsPeriod.MONTH, description="Stats period"),
    service_type: ServiceType | None = Query(None, description="Filter by service"),
    current_user: User = Depends(get_current_user)
):
    """
    Get token usage statistics for account.

    Returns usage breakdown by service for specified period.
    """
    # TODO: Implement when transaction history is available
    today = date.today()
    return UsageStatsRead(
        account_id=account_id,
        period=period,
        start_date=today.replace(day=1),
        end_date=today,
        total_tokens_used=0,
        services=[]
    )
