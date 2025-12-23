"""
Google APIs Infrastructure.

Provides real API integrations for:
- Google Search Console API
- Google Analytics 4 Data API
- Google Ads API (future)

All clients are production-ready with proper authentication,
error handling, and rate limiting.
"""

from app.infrastructure.google.search_console_client import SearchConsoleClient
from app.infrastructure.google.analytics_client import GA4Client, GA4Error

__all__ = [
    "SearchConsoleClient",
    "GA4Client",
    "GA4Error",
]
