"""
Google APIs Infrastructure.

Production-ready clients for Google Marketing integrations:
- Google Search Console API
- Google Analytics 4 Data API

Features:
- Service account authentication
- Rate limiting and retry logic
- Comprehensive metrics retrieval
"""

from app.infrastructure.google.search_console_client import SearchConsoleClient
from app.infrastructure.google.analytics_client import GA4Client

__all__ = [
    "SearchConsoleClient",
    "GA4Client",
]
