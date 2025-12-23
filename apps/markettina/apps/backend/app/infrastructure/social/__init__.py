"""
Social Media API Infrastructure.

Production-ready clients for social media platform integrations:
- Twitter/X API v2
- Facebook Graph API v19.0
- Instagram Graph API v19.0
- LinkedIn Marketing API v2

All clients implement:
- Rate limiting with automatic retry
- Token refresh and management
- Comprehensive error handling
- Async/await pattern
"""

from app.infrastructure.social.base_client import BaseSocialClient, RateLimitConfig
from app.infrastructure.social.twitter_client import TwitterClient
from app.infrastructure.social.facebook_client import FacebookClient
from app.infrastructure.social.instagram_client import InstagramClient
from app.infrastructure.social.linkedin_client import LinkedInClient

__all__ = [
    "BaseSocialClient",
    "RateLimitConfig",
    "TwitterClient",
    "FacebookClient",
    "InstagramClient",
    "LinkedInClient",
]
