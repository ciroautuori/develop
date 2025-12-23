"""Billing & Subscription Constants"""

from typing import Final


class SubscriptionConstants:
    """Subscription and billing constants."""

    # Plan types
    PLAN_TYPE_TRIAL: Final[str] = "trial"
    PLAN_TYPE_MONTHLY: Final[str] = "monthly"
    PLAN_TYPE_YEARLY: Final[str] = "yearly"

    # Trial periods (days)
    TRIAL_DURATION_DAYS: Final[int] = 30
    TRIAL_WITH_CARD_DURATION_DAYS: Final[int] = 14

    # Trial notifications (days before expiry)
    TRIAL_EXPIRY_WARNING_DAYS: Final[int] = 3
    TRIAL_EXPIRY_URGENT_DAYS: Final[int] = 1

    # Pricing (USD)
    MONTHLY_PRICE: Final[float] = 9.99
    YEARLY_PRICE: Final[float] = 99.99
    YEARLY_DISCOUNT_PERCENT: Final[int] = 17

    # Subscription status
    STATUS_ACTIVE: Final[str] = "active"
    STATUS_CANCELED: Final[str] = "canceled"
    STATUS_EXPIRED: Final[str] = "expired"
    STATUS_PAST_DUE: Final[str] = "past_due"
    STATUS_TRIALING: Final[str] = "trialing"

    # Payment status
    PAYMENT_STATUS_PENDING: Final[str] = "pending"
    PAYMENT_STATUS_SUCCEEDED: Final[str] = "succeeded"
    PAYMENT_STATUS_FAILED: Final[str] = "failed"
    PAYMENT_STATUS_REFUNDED: Final[str] = "refunded"


class UsageLimits:
    """Usage limits for different subscription plans."""

    # Trial plan limits
    TRIAL_MAX_EXPERIENCES: Final[int] = 3
    TRIAL_MAX_EDUCATION: Final[int] = 2
    TRIAL_MAX_PROJECTS: Final[int] = 3
    TRIAL_MAX_SKILLS: Final[int] = 10
    TRIAL_MAX_STORAGE_MB: Final[int] = 5
    TRIAL_MAX_THEMES: Final[int] = 1

    # Monthly plan limits
    MONTHLY_MAX_EXPERIENCES: Final[int] = 10
    MONTHLY_MAX_EDUCATION: Final[int] = 5
    MONTHLY_MAX_PROJECTS: Final[int] = 10
    MONTHLY_MAX_SKILLS: Final[int] = 50
    MONTHLY_MAX_STORAGE_MB: Final[int] = 50
    MONTHLY_MAX_THEMES: Final[int] = 5

    # Yearly plan limits (unlimited for most)
    YEARLY_MAX_EXPERIENCES: Final[int] = 999
    YEARLY_MAX_EDUCATION: Final[int] = 999
    YEARLY_MAX_PROJECTS: Final[int] = 999
    YEARLY_MAX_SKILLS: Final[int] = 999
    YEARLY_MAX_STORAGE_MB: Final[int] = 500
    YEARLY_MAX_THEMES: Final[int] = 999
