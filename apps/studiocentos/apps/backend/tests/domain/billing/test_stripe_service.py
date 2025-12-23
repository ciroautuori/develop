"""
Test suite for Stripe service integration.
All Stripe API calls are mocked for testing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.domain.billing.stripe_service import StripeService


class TestStripeCheckoutSession:
    """Test Stripe checkout session creation."""
    
    @patch('app.domain.billing.stripe_service.stripe.checkout.Session.create')
    @patch('app.domain.billing.stripe_service.settings')
    def test_create_checkout_session_success(self, mock_settings, mock_create):
        """Should create valid checkout session."""
        # Setup settings mock
        mock_settings.STRIPE_PRICE_ID_MONTHLY = "price_123"
        mock_settings.STRIPE_PRICE_ID_YEARLY = "price_456"
        
        # Mock Stripe response
        mock_session = Mock()
        mock_session.id = "cs_test_123456"
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_123456"
        mock_create.return_value = mock_session
        
        # Call service
        result = StripeService.create_checkout_session(
            plan_type="PRO_MONTHLY",
            user_email="test@example.com",
            user_id=1,
            success_url="https://app.com/success",
            cancel_url="https://app.com/cancel"
        )
        
        # Assertions
        assert result["session_id"] == "cs_test_123456"
        assert result["checkout_url"] == "https://checkout.stripe.com/pay/cs_test_123456"
        assert result["payment_status"] == "pending"
        
        # Verify Stripe was called with correct parameters
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["customer_email"] == "test@example.com"
        assert call_kwargs["mode"] == "subscription"
        assert call_kwargs["metadata"]["user_id"] == "1"
    
    @patch('app.domain.billing.stripe_service.stripe.checkout.Session.create')
    @patch('app.domain.billing.stripe_service.settings')
    def test_create_checkout_with_yearly_plan(self, mock_settings, mock_create):
        """Should handle yearly plan correctly."""
        # Setup settings mock
        mock_settings.STRIPE_PRICE_ID_MONTHLY = "price_123"
        mock_settings.STRIPE_PRICE_ID_YEARLY = "price_456"
        
        mock_session = Mock()
        mock_session.id = "cs_yearly_789"
        mock_session.url = "https://checkout.stripe.com/pay/cs_yearly_789"
        mock_create.return_value = mock_session
        
        result = StripeService.create_checkout_session(
            plan_type="PRO_YEARLY",
            user_email="yearly@test.com",
            user_id=2,
            success_url="https://app.com/success",
            cancel_url="https://app.com/cancel"
        )
        
        assert result["session_id"] == "cs_yearly_789"
        assert "checkout.stripe.com" in result["checkout_url"]
    
    def test_create_checkout_invalid_plan_fails(self):
        """Should raise error for invalid plan type."""
        with pytest.raises(ValueError, match="non supportato"):
            StripeService.create_checkout_session(
                plan_type="INVALID_PLAN",
                user_email="test@example.com",
                user_id=1,
                success_url="https://app.com/success",
                cancel_url="https://app.com/cancel"
            )
    
    @patch('app.domain.billing.stripe_service.stripe.checkout.Session.create')
    @patch('app.domain.billing.stripe_service.settings')
    def test_stripe_error_handling(self, mock_settings, mock_create):
        """Should handle Stripe API errors gracefully."""
        # Setup settings mock
        mock_settings.STRIPE_PRICE_ID_MONTHLY = "price_123"
        
        # Mock a generic exception that Stripe raises
        mock_create.side_effect = Exception("Stripe API Error")
        
        # Should catch exception and re-raise with custom message
        with pytest.raises(Exception):
            StripeService.create_checkout_session(
                plan_type="PRO_MONTHLY",
                user_email="test@example.com",
                user_id=1,
                success_url="https://app.com/success",
                cancel_url="https://app.com/cancel"
            )


class TestStripeCustomerManagement:
    """Test Stripe customer creation and management."""
    
    @patch('app.domain.billing.stripe_service.stripe.Customer.create')
    def test_create_customer_success(self, mock_create):
        """Should create Stripe customer successfully."""
        mock_customer = Mock()
        mock_customer.id = "cus_test_123"
        mock_create.return_value = mock_customer
        
        customer_id = StripeService.create_customer(
            user_email="customer@test.com",
            user_name="Test Customer"
        )
        
        assert customer_id == "cus_test_123"
        mock_create.assert_called_once_with(
            email="customer@test.com",
            name="Test Customer"
        )
    
    @patch('app.domain.billing.stripe_service.stripe.Customer.create')
    def test_create_customer_handles_errors(self, mock_create):
        """Should handle customer creation errors."""
        # Mock a generic exception
        mock_create.side_effect = Exception("Customer creation failed")
        
        # Should catch and re-raise with custom message
        with pytest.raises(Exception):
            StripeService.create_customer(
                user_email="error@test.com",
                user_name="Error User"
            )


class TestStripeSubscriptionRetrieval:
    """Test retrieving subscription details."""
    
    @patch('app.domain.billing.stripe_service.stripe.Subscription.retrieve')
    def test_get_subscription_success(self, mock_retrieve):
        """Should retrieve subscription details."""
        from datetime import datetime
        
        mock_sub = Mock()
        mock_sub.id = "sub_123"
        mock_sub.status = "active"
        mock_sub.current_period_start = 1700000000
        mock_sub.current_period_end = 1702592000
        mock_retrieve.return_value = mock_sub
        
        result = StripeService.get_subscription("sub_123")
        
        assert result["id"] == "sub_123"
        assert result["status"] == "active"
        assert isinstance(result["current_period_start"], datetime)
        assert isinstance(result["current_period_end"], datetime)
    
    @patch('app.domain.billing.stripe_service.stripe.Subscription.retrieve')
    def test_get_subscription_not_found(self, mock_retrieve):
        """Should return None for non-existent subscription."""
        # Mock exception for not found
        mock_retrieve.side_effect = Exception("No such subscription")
        
        result = StripeService.get_subscription("invalid_sub_id")
        
        # Service should handle exception and return None
        assert result is None
