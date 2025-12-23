"""
Social Media API Clients Infrastructure.

This module provides real API integrations for social media platforms:
- Twitter/X API v2
- Facebook Graph API
- LinkedIn API
- Instagram Graph API (via Facebook)
- TikTok API

All clients are production-ready with proper error handling,
rate limiting, and OAuth management.
"""

from app.infrastructure.social.twitter_client import TwitterClient
from app.infrastructure.social.facebook_client import FacebookClient
from app.infrastructure.social.linkedin_client import LinkedInClient
from app.infrastructure.social.instagram_client import InstagramClient
from app.infrastructure.social.base_client import BaseSocialClient, SocialAPIError

__all__ = [
    "TwitterClient",
    "FacebookClient",
    "LinkedInClient",
    "InstagramClient",
    "BaseSocialClient",
    "SocialAPIError",
]
