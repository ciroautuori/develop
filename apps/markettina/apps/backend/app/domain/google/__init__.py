"""
Google Integrations Domain
- Google Analytics Data API (GA4)
- Google Business Profile API (GMB)
- Google Search Console API
"""

from .analytics_service import GoogleAnalyticsService
from .business_profile_service import GoogleBusinessProfileService
from .router import router as google_router

__all__ = [
    "GoogleAnalyticsService",
    "GoogleBusinessProfileService",
    "google_router",
]
