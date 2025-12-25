"""Tests for Usage-Based Billing and Invoice Generation."""

import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.domain.billing.usage_service import UsageBillingService
from app.domain.billing.usage_models import UsageType, UsageRecord, Invoice, InvoiceStatus, UsageLimit
from app.domain.billing.models import Subscription, SubscriptionStatus, Plan, PlanType


@pytest.fixture
def test_plan(db_session):
    """Create a test plan."""
    plan = Plan(
        tenant_id="test_tenant",
        name="Pro Plan",
        plan_type=PlanType.PRO_MONTHLY,
        price_monthly=Decimal("29.99"),
        max_portfolios=10,
        max_projects=50,
        ai_credits=1000
    )
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)
    return plan


@pytest.fixture
def test_subscription(db_session, test_user, test_plan):
    """Create a test subscription."""
    now = datetime.now(timezone.utc)
    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.ACTIVE,
        current_period_start=now,
        current_period_end=now + timedelta(days=30)
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    return subscription


@pytest.fixture
def test_usage_limit(db_session, test_plan):
    """Create usage limit for plan."""
    limit = UsageLimit(
        plan_id=test_plan.id,
        usage_type=UsageType.AI_GENERATION,
        included_quantity=100,
        overage_price=Decimal("0.10"),
        hard_limit=500,
        reset_period="monthly"
    )
    db_session.add(limit)
    db_session.commit()
    db_session.refresh(limit)
    return limit


class TestUsageTracking:
    """Test suite for usage tracking."""
    
    def test_track_usage_basic(self, db_session, test_user, test_subscription):
        """Test basic usage tracking."""
        record = UsageBillingService.track_usage(
            db=db_session,
            user_id=test_user.id,
            usage_type=UsageType.CV_EXPORT,
            quantity=1
        )
        
        assert record.id is not None
        assert record.user_id == test_user.id
        assert record.subscription_id == test_subscription.id
        assert record.usage_type == UsageType.CV_EXPORT
        assert record.quantity == 1
        assert record.billed is False
    
    def test_track_usage_with_metadata(self, db_session, test_user):
        """Test usage tracking with metadata."""
        metadata = '{"format": "pdf", "pages": 3}'
        
        record = UsageBillingService.track_usage(
            db=db_session,
            user_id=test_user.id,
            usage_type=UsageType.CV_EXPORT,
            quantity=1,
            metadata=metadata
        )
        
        assert record.metadata == metadata
    
    def test_track_usage_overage_billing(self, db_session, test_user, test_subscription, test_usage_limit):
        """Test usage tracking with overage pricing."""
        # Track usage beyond included quantity
        for _ in range(105):  # 5 over the limit of 100
            UsageBillingService.track_usage(
                db=db_session,
                user_id=test_user.id,
                usage_type=UsageType.AI_GENERATION,
                quantity=1
            )
        
        # Get last 5 records (overage)
        overage_records = db_session.query(UsageRecord).filter(
            UsageRecord.user_id == test_user.id,
            UsageRecord.usage_type == UsageType.AI_GENERATION,
            UsageRecord.total_cost.isnot(None)
        ).all()
        
        # Should have charged for overage
        assert len(overage_records) == 5
        for record in overage_records:
            assert record.unit_price == Decimal("0.10")
            assert record.total_cost == Decimal("0.10")
    
    def test_get_period_usage(self, db_session, test_user):
        """Test getting usage count for period."""
        # Track some usage
        for _ in range(3):
            UsageBillingService.track_usage(
                db=db_session,
                user_id=test_user.id,
                usage_type=UsageType.AI_GENERATION,
                quantity=2
            )
        
        period_start = datetime.now(timezone.utc) - timedelta(days=1)
        total = UsageBillingService.get_period_usage(
            db=db_session,
            user_id=test_user.id,
            usage_type=UsageType.AI_GENERATION,
            period_start=period_start
        )
        
        assert total == 6  # 3 records * 2 quantity


class TestUsageLimits:
    """Test suite for usage limits."""
    
    def test_check_usage_limit_within_limit(self, db_session, test_user, test_subscription, test_usage_limit):
        """Test usage limit check when within limit."""
        # Track 50 usage (below 100 limit)
        for _ in range(50):
            UsageBillingService.track_usage(
                db=db_session,
                user_id=test_user.id,
                usage_type=UsageType.AI_GENERATION,
                quantity=1
            )
        
        result = UsageBillingService.check_usage_limit(
            db=db_session,
            user_id=test_user.id,
            usage_type=UsageType.AI_GENERATION,
            requested_quantity=1
        )
        
        assert result["allowed"] is True
        assert result["current_usage"] == 50
        assert result["included_quantity"] == 100
        assert result["will_charge"] is False
    
    def test_check_usage_limit_overage_allowed(self, db_session, test_user, test_subscription, test_usage_limit):
        """Test usage limit check when in overage zone."""
        # Track 110 usage (10 over 100 limit)
        for _ in range(110):
            UsageBillingService.track_usage(
                db=db_session,
                user_id=test_user.id,
                usage_type=UsageType.AI_GENERATION,
                quantity=1
            )
        
        result = UsageBillingService.check_usage_limit(
            db=db_session,
            user_id=test_user.id,
            usage_type=UsageType.AI_GENERATION,
            requested_quantity=1
        )
        
        assert result["allowed"] is True
        assert result["will_charge"] is True
        assert result["overage_price"] == 0.10
    
    def test_check_usage_limit_hard_limit_reached(self, db_session, test_user, test_subscription, test_usage_limit):
        """Test usage limit check when hard limit reached."""
        # Track 500 usage (at hard limit)
        for _ in range(500):
            UsageBillingService.track_usage(
                db=db_session,
                user_id=test_user.id,
                usage_type=UsageType.AI_GENERATION,
                quantity=1
            )
        
        result = UsageBillingService.check_usage_limit(
            db=db_session,
            user_id=test_user.id,
            usage_type=UsageType.AI_GENERATION,
            requested_quantity=1
        )
        
        assert result["allowed"] is False
        assert result["reason"] == "Hard limit reached"
        assert result["limit"] == 500


class TestInvoiceGeneration:
    """Test suite for invoice generation."""
    
    def test_generate_invoice_basic(self, db_session, test_user, test_subscription, test_usage_limit):
        """Test basic invoice generation."""
        # Track some billable overage usage
        for _ in range(110):  # 10 overage units
            UsageBillingService.track_usage(
                db=db_session,
                user_id=test_user.id,
                usage_type=UsageType.AI_GENERATION,
                quantity=1
            )
        
        # Generate invoice
        now = datetime.now(timezone.utc)
        period_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        if now.month == 12:
            period_end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            period_end = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
        
        invoice = UsageBillingService.generate_invoice(
            db=db_session,
            user_id=test_user.id,
            period_start=period_start,
            period_end=period_end,
            tax_rate=Decimal("22.00")  # 22% VAT
        )
        
        assert invoice is not None
        assert invoice.user_id == test_user.id
        assert invoice.status == InvoiceStatus.DRAFT
        assert invoice.subtotal == Decimal("1.00")  # 10 * 0.10
        assert invoice.tax_rate == Decimal("22.00")
        assert invoice.tax_amount == Decimal("0.22")  # 22% of 1.00
        assert invoice.total == Decimal("1.22")  # 1.00 + 0.22
    
    def test_generate_invoice_no_billable_usage(self, db_session, test_user, test_subscription):
        """Test invoice generation with no billable usage."""
        now = datetime.now(timezone.utc)
        period_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        if now.month == 12:
            period_end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            period_end = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
        
        invoice = UsageBillingService.generate_invoice(
            db=db_session,
            user_id=test_user.id,
            period_start=period_start,
            period_end=period_end
        )
        
        assert invoice is None  # No invoice created
    
    def test_generate_invoice_marks_usage_as_billed(self, db_session, test_user, test_subscription, test_usage_limit):
        """Test that invoice generation marks usage as billed."""
        # Track billable usage
        for _ in range(110):
            UsageBillingService.track_usage(
                db=db_session,
                user_id=test_user.id,
                usage_type=UsageType.AI_GENERATION,
                quantity=1
            )
        
        # Generate invoice
        now = datetime.now(timezone.utc)
        period_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        if now.month == 12:
            period_end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            period_end = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
        
        invoice = UsageBillingService.generate_invoice(
            db=db_session,
            user_id=test_user.id,
            period_start=period_start,
            period_end=period_end
        )
        
        # Check that usage is marked as billed
        billed_records = db_session.query(UsageRecord).filter(
            UsageRecord.user_id == test_user.id,
            UsageRecord.billed == True,
            UsageRecord.invoice_id == invoice.id
        ).count()
        
        assert billed_records == 10  # 10 overage records
    
    def test_invoice_has_line_items(self, db_session, test_user, test_subscription, test_usage_limit):
        """Test that generated invoice has line items."""
        # Track different types of usage
        for _ in range(110):
            UsageBillingService.track_usage(
                db=db_session,
                user_id=test_user.id,
                usage_type=UsageType.AI_GENERATION,
                quantity=1
            )
        
        # Generate invoice
        now = datetime.now(timezone.utc)
        period_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        if now.month == 12:
            period_end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            period_end = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
        
        invoice = UsageBillingService.generate_invoice(
            db=db_session,
            user_id=test_user.id,
            period_start=period_start,
            period_end=period_end
        )
        
        assert len(invoice.line_items) == 1
        line_item = invoice.line_items[0]
        assert line_item.usage_type == UsageType.AI_GENERATION
        assert line_item.quantity == 10
        assert line_item.amount == Decimal("1.00")
    
    def test_mark_invoice_paid(self, db_session, test_user, test_subscription, test_usage_limit):
        """Test marking invoice as paid."""
        # Create invoice
        for _ in range(110):
            UsageBillingService.track_usage(
                db=db_session,
                user_id=test_user.id,
                usage_type=UsageType.AI_GENERATION,
                quantity=1
            )
        
        now = datetime.now(timezone.utc)
        period_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        if now.month == 12:
            period_end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            period_end = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
        
        invoice = UsageBillingService.generate_invoice(
            db=db_session,
            user_id=test_user.id,
            period_start=period_start,
            period_end=period_end
        )
        
        # Mark as paid
        paid_invoice = UsageBillingService.mark_invoice_paid(
            db=db_session,
            invoice_id=invoice.id,
            payment_intent_id="pi_test_123"
        )
        
        assert paid_invoice.status == InvoiceStatus.PAID
        assert paid_invoice.paid_at is not None
        assert paid_invoice.payment_intent_id == "pi_test_123"
    
    def test_void_invoice(self, db_session, test_user, test_subscription, test_usage_limit):
        """Test voiding an invoice."""
        # Create invoice
        for _ in range(110):
            UsageBillingService.track_usage(
                db=db_session,
                user_id=test_user.id,
                usage_type=UsageType.AI_GENERATION,
                quantity=1
            )
        
        now = datetime.now(timezone.utc)
        period_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        if now.month == 12:
            period_end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            period_end = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
        
        invoice = UsageBillingService.generate_invoice(
            db=db_session,
            user_id=test_user.id,
            period_start=period_start,
            period_end=period_end
        )
        
        # Void invoice
        voided = UsageBillingService.void_invoice(
            db=db_session,
            invoice_id=invoice.id,
            reason="Test void"
        )
        
        assert voided.status == InvoiceStatus.VOID
        assert voided.voided_at is not None
        
        # Check that usage is un-billed
        unbilled_count = db_session.query(UsageRecord).filter(
            UsageRecord.user_id == test_user.id,
            UsageRecord.billed == False
        ).count()
        
        assert unbilled_count > 0


class TestUsageSummary:
    """Test suite for usage summary."""
    
    def test_get_usage_summary(self, db_session, test_user):
        """Test getting usage summary."""
        # Track various usage
        UsageBillingService.track_usage(
            db=db_session,
            user_id=test_user.id,
            usage_type=UsageType.AI_GENERATION,
            quantity=5
        )
        
        UsageBillingService.track_usage(
            db=db_session,
            user_id=test_user.id,
            usage_type=UsageType.CV_EXPORT,
            quantity=3
        )
        
        # Get summary
        summary = UsageBillingService.get_usage_summary(
            db=db_session,
            user_id=test_user.id
        )
        
        assert "ai_generation" in summary
        assert summary["ai_generation"]["quantity"] == 5
        assert "cv_export" in summary
        assert summary["cv_export"]["quantity"] == 3
