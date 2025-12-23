"""Constants Package - Backward Compatibility Exports

All constants are now organized by domain in separate files:
- auth_constants.py: Authentication constants
- billing_constants.py: Subscription and billing
- portfolio_constants.py: Portfolio and file uploads
- system_constants.py: Cache, rate limiting, pagination
- service_constants.py: Enrichment, email, analytics
- api_constants.py: Validation, error codes, HTTP messages

This __init__.py maintains backward compatibility by exporting all classes.
"""

# Auth
# API
from .api_constants import ErrorCodes, HTTPMessages, ValidationConstants
from .auth_constants import AuthConstants

# Billing
from .billing_constants import SubscriptionConstants, UsageLimits

# Portfolio
from .portfolio_constants import FileUploadConstants, PortfolioConstants

# Services
from .service_constants import AnalyticsConstants, EmailConstants, EnrichmentConstants

# System
from .system_constants import CacheConstants, PaginationConstants, RateLimitConstants

__all__ = [
    # Auth
    "AuthConstants",
    # Billing
    "SubscriptionConstants",
    "UsageLimits",
    # Portfolio
    "PortfolioConstants",
    "FileUploadConstants",
    # System
    "CacheConstants",
    "RateLimitConstants",
    "PaginationConstants",
    # Services
    "EnrichmentConstants",
    "EmailConstants",
    "AnalyticsConstants",
    # API
    "ValidationConstants",
    "ErrorCodes",
    "HTTPMessages",
]
