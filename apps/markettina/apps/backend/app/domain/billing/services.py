"""
MARKETTINA v2.0 - Billing Context Services
Business logic for billing operations.
"""

import logging
import secrets
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.billing.models import (
    DiscountType,
    Invoice,
    InvoiceItem,
    InvoiceStatus,
    PromoCode,
    PromoRedemption,
    ReferralProgram,
    ServicePricing,
    ServiceType,
)
from app.domain.billing.schemas import (
    InvoiceCreate,
    InvoiceUpdate,
    PromoCodeCreate,
    PromoCodeValidate,
    PromoCodeValidationResult,
    ReferralCodeApply,
    ReferralProgramCreate,
    ReferralResult,
    ServicePricingCreate,
    ServicePricingUpdate,
    TokenConsumptionRequest,
    TokenConsumptionResult,
)

logger = logging.getLogger(__name__)


class BillingService:
    """Service for billing operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    # ========================================================================
    # SERVICE PRICING OPERATIONS
    # ========================================================================

    async def get_service_pricing(
        self,
        service_type: ServiceType,
        service_subtype: str | None = None
    ) -> ServicePricing | None:
        """Get active pricing for a service."""
        today = date.today()
        query = select(ServicePricing).where(
            and_(
                ServicePricing.service_type == service_type,
                ServicePricing.is_active == True,
                ServicePricing.effective_from <= today,
                (ServicePricing.effective_to.is_(None) | (ServicePricing.effective_to >= today)),
                ServicePricing.deleted_at.is_(None)
            )
        )
        if service_subtype:
            query = query.where(ServicePricing.service_subtype == service_subtype)

        result = await self.db.execute(query.order_by(ServicePricing.effective_from.desc()).limit(1))
        return result.scalar_one_or_none()

    async def list_service_pricing(self, active_only: bool = True) -> list[ServicePricing]:
        """List all service pricing entries."""
        query = select(ServicePricing).where(ServicePricing.deleted_at.is_(None))
        if active_only:
            today = date.today()
            query = query.where(
                and_(
                    ServicePricing.is_active == True,
                    ServicePricing.effective_from <= today,
                    (ServicePricing.effective_to.is_(None) | (ServicePricing.effective_to >= today))
                )
            )
        result = await self.db.execute(query.order_by(ServicePricing.service_type))
        return list(result.scalars().all())

    async def create_service_pricing(self, data: ServicePricingCreate) -> ServicePricing:
        """Create new service pricing entry."""
        pricing = ServicePricing(
            service_type=data.service_type,
            service_subtype=data.service_subtype,
            token_cost=data.token_cost,
            name=data.name,
            description=data.description,
            is_active=data.is_active,
            effective_from=data.effective_from,
            effective_to=data.effective_to
        )
        self.db.add(pricing)
        await self.db.commit()
        await self.db.refresh(pricing)
        logger.info(f"Created service pricing: {pricing}")
        return pricing

    async def update_service_pricing(
        self,
        pricing_id: UUID,
        data: ServicePricingUpdate
    ) -> ServicePricing:
        """Update service pricing entry."""
        pricing = await self.db.get(ServicePricing, pricing_id)
        if not pricing or pricing.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service pricing not found"
            )

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(pricing, field, value)

        await self.db.commit()
        await self.db.refresh(pricing)
        logger.info(f"Updated service pricing: {pricing}")
        return pricing

    # ========================================================================
    # INVOICE OPERATIONS
    # ========================================================================

    async def _generate_invoice_number(self) -> str:
        """Generate unique invoice number."""
        year = datetime.now().year
        prefix = f"MKT-{year}"

        query = select(func.count()).select_from(Invoice).where(
            Invoice.invoice_number.like(f"{prefix}%")
        )
        result = await self.db.execute(query)
        count = result.scalar() or 0

        return f"{prefix}-{count + 1:06d}"

    async def create_invoice(self, data: InvoiceCreate) -> Invoice:
        """Create new invoice with items."""
        invoice_number = await self._generate_invoice_number()

        # Calculate totals
        subtotal_cents = sum(
            item.unit_price_cents * item.quantity for item in data.items
        )
        discount_cents = 0
        tax_rate = Decimal("0.22")  # 22% IVA

        # Apply promo code if provided
        if data.promo_code:
            validation = await self.validate_promo_code(PromoCodeValidate(
                code=data.promo_code,
                account_id=data.account_id,
                purchase_cents=subtotal_cents
            ))
            if validation.is_valid and validation.discount_cents:
                discount_cents = validation.discount_cents

        # Calculate tax and total
        taxable_amount = subtotal_cents - discount_cents
        tax_cents = int(taxable_amount * tax_rate)
        total_cents = taxable_amount + tax_cents

        # Create invoice
        invoice = Invoice(
            account_id=data.account_id,
            invoice_number=invoice_number,
            subtotal_cents=subtotal_cents,
            discount_cents=discount_cents,
            tax_cents=tax_cents,
            total_cents=total_cents,
            currency=data.currency,
            status=InvoiceStatus.DRAFT,
            issue_date=date.today(),
            due_date=data.due_date,
            billing_name=data.billing_name,
            billing_email=data.billing_email,
            billing_address=data.billing_address.model_dump() if data.billing_address else None,
            notes=data.notes
        )
        self.db.add(invoice)
        await self.db.flush()

        # Create invoice items
        for item_data in data.items:
            item = InvoiceItem(
                invoice_id=invoice.id,
                description=item_data.description,
                quantity=item_data.quantity,
                unit_price_cents=item_data.unit_price_cents,
                total_cents=item_data.unit_price_cents * item_data.quantity,
                token_package_id=item_data.token_package_id,
                tokens_amount=item_data.tokens_amount
            )
            self.db.add(item)

        await self.db.commit()
        await self.db.refresh(invoice)

        logger.info(f"Created invoice: {invoice}")
        return invoice

    async def get_invoice(self, invoice_id: UUID) -> Invoice | None:
        """Get invoice by ID with items."""
        query = select(Invoice).where(
            and_(Invoice.id == invoice_id, Invoice.deleted_at.is_(None))
        ).options(selectinload(Invoice.items))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_invoice_by_number(self, invoice_number: str) -> Invoice | None:
        """Get invoice by invoice number."""
        query = select(Invoice).where(
            and_(Invoice.invoice_number == invoice_number, Invoice.deleted_at.is_(None))
        ).options(selectinload(Invoice.items))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_invoices(
        self,
        account_id: UUID,
        status_filter: InvoiceStatus | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[Invoice]:
        """List invoices for account."""
        query = select(Invoice).where(
            and_(Invoice.account_id == account_id, Invoice.deleted_at.is_(None))
        )
        if status_filter:
            query = query.where(Invoice.status == status_filter)

        query = query.order_by(Invoice.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_invoice(
        self,
        invoice_id: UUID,
        data: InvoiceUpdate
    ) -> Invoice:
        """Update invoice."""
        invoice = await self.get_invoice(invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )

        # Cannot update paid invoices
        if invoice.status in [InvoiceStatus.PAID, InvoiceStatus.REFUNDED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update paid or refunded invoice"
            )

        for field, value in data.model_dump(exclude_unset=True).items():
            if field == "billing_address" and value:
                value = value.model_dump()
            setattr(invoice, field, value)

        invoice.version += 1
        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice

    async def mark_invoice_paid(
        self,
        invoice_id: UUID,
        stripe_payment_intent_id: str | None = None
    ) -> Invoice:
        """Mark invoice as paid."""
        invoice = await self.get_invoice(invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )

        invoice.status = InvoiceStatus.PAID
        invoice.paid_at = datetime.now(UTC)
        if stripe_payment_intent_id:
            invoice.stripe_payment_intent_id = stripe_payment_intent_id
        invoice.version += 1

        await self.db.commit()
        await self.db.refresh(invoice)
        logger.info(f"Invoice marked as paid: {invoice}")
        return invoice

    # ========================================================================
    # PROMO CODE OPERATIONS
    # ========================================================================

    async def create_promo_code(self, data: PromoCodeCreate) -> PromoCode:
        """Create new promo code."""
        # Check if code already exists
        existing = await self.db.execute(
            select(PromoCode).where(PromoCode.code == data.code.upper())
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Promo code already exists"
            )

        promo = PromoCode(
            code=data.code.upper(),
            discount_type=data.discount_type,
            discount_value=data.discount_value,
            is_active=data.is_active,
            valid_from=data.valid_from,
            valid_until=data.valid_until,
            max_uses=data.max_uses,
            max_uses_per_account=data.max_uses_per_account,
            min_purchase_cents=data.min_purchase_cents,
            applicable_packages=data.applicable_packages,
            description=data.description,
            campaign_name=data.campaign_name
        )
        self.db.add(promo)
        await self.db.commit()
        await self.db.refresh(promo)
        logger.info(f"Created promo code: {promo}")
        return promo

    async def validate_promo_code(self, data: PromoCodeValidate) -> PromoCodeValidationResult:
        """Validate promo code for account and purchase."""
        # Find promo code
        query = select(PromoCode).where(
            and_(
                PromoCode.code == data.code.upper(),
                PromoCode.is_active == True,
                PromoCode.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(query)
        promo = result.scalar_one_or_none()

        if not promo:
            return PromoCodeValidationResult(
                is_valid=False,
                error_message="Promo code not found or inactive"
            )

        now = datetime.now(UTC)

        # Check validity period
        if promo.valid_from > now:
            return PromoCodeValidationResult(
                is_valid=False,
                error_message="Promo code not yet valid"
            )
        if promo.valid_until and promo.valid_until < now:
            return PromoCodeValidationResult(
                is_valid=False,
                error_message="Promo code has expired"
            )

        # Check usage limits
        if promo.max_uses and promo.current_uses >= promo.max_uses:
            return PromoCodeValidationResult(
                is_valid=False,
                error_message="Promo code usage limit reached"
            )

        # Check per-account usage
        if promo.max_uses_per_account:
            account_uses_query = select(func.count()).select_from(PromoRedemption).where(
                and_(
                    PromoRedemption.promo_code_id == promo.id,
                    PromoRedemption.account_id == data.account_id
                )
            )
            account_uses_result = await self.db.execute(account_uses_query)
            account_uses = account_uses_result.scalar() or 0
            if account_uses >= promo.max_uses_per_account:
                return PromoCodeValidationResult(
                    is_valid=False,
                    error_message="You have already used this promo code"
                )

        # Check minimum purchase
        if promo.min_purchase_cents and data.purchase_cents < promo.min_purchase_cents:
            return PromoCodeValidationResult(
                is_valid=False,
                error_message=f"Minimum purchase of {promo.min_purchase_cents / 100:.2f} EUR required"
            )

        # Check applicable packages
        if promo.applicable_packages and data.package_id:
            if data.package_id not in promo.applicable_packages:
                return PromoCodeValidationResult(
                    is_valid=False,
                    error_message="Promo code not valid for this package"
                )

        # Calculate discount
        discount_cents = 0
        bonus_tokens = 0

        if promo.discount_type == DiscountType.PERCENTAGE:
            discount_cents = int(data.purchase_cents * float(promo.discount_value) / 100)
        elif promo.discount_type == DiscountType.FIXED_AMOUNT:
            discount_cents = int(float(promo.discount_value) * 100)
        elif promo.discount_type == DiscountType.BONUS_TOKENS:
            bonus_tokens = int(promo.discount_value)

        return PromoCodeValidationResult(
            is_valid=True,
            discount_type=promo.discount_type,
            discount_value=promo.discount_value,
            discount_cents=discount_cents if discount_cents > 0 else None,
            bonus_tokens=bonus_tokens if bonus_tokens > 0 else None
        )

    async def redeem_promo_code(
        self,
        promo_code_id: UUID,
        account_id: UUID,
        invoice_id: UUID | None,
        discount_applied_cents: int
    ) -> PromoRedemption:
        """Record promo code redemption."""
        redemption = PromoRedemption(
            promo_code_id=promo_code_id,
            account_id=account_id,
            invoice_id=invoice_id,
            discount_applied_cents=discount_applied_cents
        )
        self.db.add(redemption)

        # Increment usage counter
        promo = await self.db.get(PromoCode, promo_code_id)
        if promo:
            promo.current_uses += 1

        await self.db.commit()
        await self.db.refresh(redemption)
        return redemption

    # ========================================================================
    # REFERRAL PROGRAM OPERATIONS
    # ========================================================================

    async def create_referral_program(self, data: ReferralProgramCreate) -> ReferralProgram:
        """Create referral program for account."""
        # Check if account already has referral program
        existing = await self.db.execute(
            select(ReferralProgram).where(
                and_(
                    ReferralProgram.referrer_account_id == data.referrer_account_id,
                    ReferralProgram.deleted_at.is_(None)
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account already has a referral program"
            )

        # Generate unique referral code
        referral_code = f"REF-{secrets.token_urlsafe(6).upper()}"

        program = ReferralProgram(
            referrer_account_id=data.referrer_account_id,
            referral_code=referral_code,
            referrer_bonus_tokens=data.referrer_bonus_tokens,
            referee_bonus_tokens=data.referee_bonus_tokens
        )
        self.db.add(program)
        await self.db.commit()
        await self.db.refresh(program)
        logger.info(f"Created referral program: {program}")
        return program

    async def get_referral_program(self, account_id: UUID) -> ReferralProgram | None:
        """Get referral program for account."""
        query = select(ReferralProgram).where(
            and_(
                ReferralProgram.referrer_account_id == account_id,
                ReferralProgram.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def apply_referral_code(self, data: ReferralCodeApply) -> ReferralResult:
        """Apply referral code for new account."""
        # Find referral program
        query = select(ReferralProgram).where(
            and_(
                ReferralProgram.referral_code == data.referral_code.upper(),
                ReferralProgram.is_active == True,
                ReferralProgram.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(query)
        program = result.scalar_one_or_none()

        if not program:
            return ReferralResult(
                success=False,
                error_message="Referral code not found or inactive"
            )

        # Cannot refer yourself
        if program.referrer_account_id == data.referred_account_id:
            return ReferralResult(
                success=False,
                error_message="Cannot use your own referral code"
            )

        # Update program stats
        program.total_referrals += 1
        program.successful_referrals += 1
        program.total_tokens_earned += program.referrer_bonus_tokens

        await self.db.commit()

        return ReferralResult(
            success=True,
            referrer_tokens_awarded=program.referrer_bonus_tokens,
            referee_tokens_awarded=program.referee_bonus_tokens
        )


class TokenConsumptionService:
    """Service for token consumption tracking."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db
        self.billing_service = BillingService(db)

    async def get_token_cost(
        self,
        service_type: ServiceType,
        service_subtype: str | None = None
    ) -> int:
        """Get token cost for a service."""
        pricing = await self.billing_service.get_service_pricing(
            service_type, service_subtype
        )
        if not pricing:
            # Default costs if not configured
            default_costs = {
                ServiceType.CONTENT_GENERATION: 10,
                ServiceType.IMAGE_GENERATION: 50,
                ServiceType.VIDEO_GENERATION: 200,
                ServiceType.SENTIMENT_ANALYSIS: 5,
                ServiceType.COMPETITOR_ANALYSIS: 20,
                ServiceType.LEAD_ENRICHMENT: 15,
                ServiceType.EMAIL_CAMPAIGN: 25,
                ServiceType.SOCIAL_POST: 10
            }
            return default_costs.get(service_type, 10)
        return pricing.token_cost

    async def check_balance(self, account_id: UUID, required_tokens: int) -> bool:
        """Check if account has sufficient token balance.

        Note: This requires TokenWallet integration.
        For now, returns True to allow operations.
        TODO: Integrate with actual TokenWallet when available.
        """
        # Placeholder - integrate with TokenWallet
        logger.warning(f"Token balance check not yet integrated for account {account_id}")
        return True

    async def consume_tokens(self, request: TokenConsumptionRequest) -> TokenConsumptionResult:
        """Consume tokens for a service operation.

        Note: This requires TokenWallet integration.
        TODO: Integrate with actual TokenWallet when available.
        """
        token_cost = await self.get_token_cost(
            request.service_type,
            request.service_subtype
        )
        total_cost = token_cost * request.quantity

        # Check balance
        has_balance = await self.check_balance(request.account_id, total_cost)
        if not has_balance:
            return TokenConsumptionResult(
                success=False,
                error_message="Insufficient token balance"
            )

        # TODO: Create TokenTransaction and update TokenWallet
        logger.info(
            f"Token consumption: account={request.account_id}, "
            f"service={request.service_type.value}, tokens={total_cost}"
        )

        return TokenConsumptionResult(
            success=True,
            tokens_consumed=total_cost,
            remaining_balance=0  # TODO: Get actual balance
        )


def get_billing_service(db: AsyncSession) -> BillingService:
    """Dependency injector for BillingService."""
    return BillingService(db)


def get_token_consumption_service(db: AsyncSession) -> TokenConsumptionService:
    """Dependency injector for TokenConsumptionService."""
    return TokenConsumptionService(db)
