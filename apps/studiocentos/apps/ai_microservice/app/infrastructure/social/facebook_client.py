"""
Facebook Graph API Client.

Production-ready client for Facebook Graph API v19.0 with:
- Page posting
- Media upload
- Insights and analytics
- Comment management
- OAuth token management

API Reference: https://developers.facebook.com/docs/graph-api
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from app.infrastructure.social.base_client import (
    BaseSocialClient,
    OAuthTokens,
    RateLimiter,
    SocialAPIError,
    AuthenticationError,
    MediaUploadError,
    PostingError,
)

logger = logging.getLogger(__name__)


class FacebookClient(BaseSocialClient):
    """
    Facebook Graph API Client.

    Supports:
    - Page post creation with media
    - Post scheduling
    - Insights and analytics
    - Comment management
    - Token refresh and validation

    Note: Requires a Page Access Token for page operations.
    User tokens work for user profile operations only.

    Example:
        >>> tokens = OAuthTokens(access_token="...")
        >>> async with FacebookClient(tokens=tokens, page_id="123") as client:
        ...     result = await client.post("Hello Facebook!")
    """

    PLATFORM_NAME = "facebook"
    API_VERSION = "v19.0"
    API_BASE = f"https://graph.facebook.com/{API_VERSION}"

    # Facebook rate limits
    DEFAULT_RATE_LIMITS = {
        "posts": RateLimiter(max_requests=200, window_seconds=3600),
        "reads": RateLimiter(max_requests=200, window_seconds=3600),
        "media": RateLimiter(max_requests=100, window_seconds=3600),
    }

    def __init__(
        self,
        tokens: Optional[OAuthTokens] = None,
        page_id: Optional[str] = None,
        page_access_token: Optional[str] = None,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
    ):
        """
        Initialize Facebook client.

        Args:
            tokens: OAuth tokens (user access token)
            page_id: Facebook Page ID for page operations
            page_access_token: Page-specific access token
            app_id: Facebook App ID
            app_secret: Facebook App Secret
        """
        super().__init__(tokens=tokens, rate_limits=self.DEFAULT_RATE_LIMITS.copy())

        self.page_id = page_id or os.getenv("FACEBOOK_PAGE_ID", "")
        self.page_access_token = page_access_token or os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
        self.app_id = app_id or os.getenv("FACEBOOK_APP_ID", "")
        self.app_secret = app_secret or os.getenv("FACEBOOK_APP_SECRET", "")

    def _get_auth_headers(self) -> Dict[str, str]:
        """Override to use page token when available."""
        token = self.page_access_token
        if not token and self.tokens:
            token = self.tokens.access_token

        if not token:
            return {}

        return {}  # Facebook uses query params for auth

    def _get_access_token(self) -> str:
        """Get the appropriate access token."""
        if self.page_access_token:
            return self.page_access_token
        if self.tokens:
            return self.tokens.access_token
        raise AuthenticationError(
            "No access token available",
            platform=self.PLATFORM_NAME,
        )

    def _parse_error_message(self, error_data: Dict[str, Any]) -> str:
        """Parse Facebook API error message."""
        error = error_data.get("error", {})
        if isinstance(error, dict):
            return error.get("message", "Unknown Facebook API error")
        return str(error) if error else "Unknown Facebook API error"

    def _parse_error_code(self, error_data: Dict[str, Any]) -> Optional[str]:
        """Parse Facebook API error code."""
        error = error_data.get("error", {})
        if isinstance(error, dict):
            return str(error.get("code", ""))
        return None

    async def refresh_access_token(self) -> OAuthTokens:
        """
        Refresh/extend access token.

        Facebook uses token exchange for long-lived tokens.
        """
        if not self.tokens:
            raise AuthenticationError(
                "No token to refresh",
                platform=self.PLATFORM_NAME,
            )

        response = await self.client.get(
            f"{self.API_BASE}/oauth/access_token",
            params={
                "grant_type": "fb_exchange_token",
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "fb_exchange_token": self.tokens.access_token,
            },
        )

        if response.status_code != 200:
            raise AuthenticationError(
                f"Token refresh failed: {response.text}",
                platform=self.PLATFORM_NAME,
                status_code=response.status_code,
            )

        return OAuthTokens.from_response(response.json())

    async def get_page_access_token(self, user_token: str) -> str:
        """
        Get page access token from user access token.

        Requires 'pages_manage_posts' permission.
        """
        response = await self.client.get(
            f"{self.API_BASE}/{self.page_id}",
            params={
                "fields": "access_token",
                "access_token": user_token,
            },
        )

        if response.status_code != 200:
            raise AuthenticationError(
                f"Failed to get page token: {response.text}",
                platform=self.PLATFORM_NAME,
            )

        data = response.json()
        page_token = data.get("access_token")

        if page_token:
            self.page_access_token = page_token

        return page_token

    async def post(
        self,
        content: str,
        media_ids: Optional[List[str]] = None,
        link: Optional[str] = None,
        scheduled_publish_time: Optional[datetime] = None,
        targeting: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a page post.

        Args:
            content: Post message
            media_ids: List of uploaded photo IDs
            link: URL to share
            scheduled_publish_time: Schedule post (min 10 min, max 6 months)
            targeting: Audience targeting options

        Returns:
            Post data including ID
        """
        if not self.page_id:
            raise PostingError(
                "Page ID required for posting",
                platform=self.PLATFORM_NAME,
            )

        endpoint = f"{self.API_BASE}/{self.page_id}/feed"

        params: Dict[str, Any] = {
            "message": content,
            "access_token": self._get_access_token(),
        }

        if link:
            params["link"] = link

        if media_ids and len(media_ids) == 1:
            # Single photo post
            endpoint = f"{self.API_BASE}/{self.page_id}/photos"
            params["photo"] = media_ids[0]
        elif media_ids and len(media_ids) > 1:
            # Multi-photo post
            params["attached_media"] = [
                {"media_fbid": mid} for mid in media_ids
            ]

        if scheduled_publish_time:
            params["published"] = False
            params["scheduled_publish_time"] = int(scheduled_publish_time.timestamp())

        if targeting:
            params["targeting"] = targeting

        response = await self.client.post(
            endpoint,
            data=params,
        )

        result = await self._handle_response(response, "posts")

        logger.info(f"Facebook: Posted to page {self.page_id}, post_id={result.get('id')}")
        return result

    async def delete_post(self, post_id: str) -> bool:
        """Delete a post."""
        response = await self.client.delete(
            f"{self.API_BASE}/{post_id}",
            params={"access_token": self._get_access_token()},
        )

        result = await self._handle_response(response, "posts")
        return result.get("success", False)

    async def get_metrics(self, post_id: str) -> Dict[str, Any]:
        """
        Get post insights/metrics.

        Returns engagement metrics including:
        - impressions
        - reach
        - engagement (likes, comments, shares)
        - clicks
        """
        # Get basic post metrics
        response = await self.client.get(
            f"{self.API_BASE}/{post_id}",
            params={
                "fields": "likes.summary(true),comments.summary(true),shares,reactions.summary(true)",
                "access_token": self._get_access_token(),
            },
        )

        data = await self._handle_response(response, "reads")

        metrics = {
            "post_id": post_id,
            "platform": "facebook",
            "timestamp": datetime.utcnow().isoformat(),
            "likes": data.get("likes", {}).get("summary", {}).get("total_count", 0),
            "comments": data.get("comments", {}).get("summary", {}).get("total_count", 0),
            "shares": data.get("shares", {}).get("count", 0) if data.get("shares") else 0,
            "reactions": data.get("reactions", {}).get("summary", {}).get("total_count", 0),
        }

        # Get post insights (page posts only)
        try:
            insights_response = await self.client.get(
                f"{self.API_BASE}/{post_id}/insights",
                params={
                    "metric": "post_impressions,post_impressions_unique,post_engaged_users,post_clicks",
                    "access_token": self._get_access_token(),
                },
            )

            if insights_response.status_code == 200:
                insights_data = insights_response.json()
                for insight in insights_data.get("data", []):
                    name = insight.get("name", "")
                    value = insight.get("values", [{}])[0].get("value", 0)

                    if name == "post_impressions":
                        metrics["impressions"] = value
                    elif name == "post_impressions_unique":
                        metrics["reach"] = value
                    elif name == "post_engaged_users":
                        metrics["engaged_users"] = value
                    elif name == "post_clicks":
                        metrics["clicks"] = value
        except Exception as e:
            logger.warning(f"Failed to get post insights: {e}")

        # Calculate engagement rate
        reach = metrics.get("reach", 0)
        engagements = metrics["likes"] + metrics["comments"] + metrics["shares"]
        if reach > 0:
            metrics["engagement_rate"] = round((engagements / reach) * 100, 2)
        else:
            metrics["engagement_rate"] = 0.0

        return metrics

    async def upload_media(
        self,
        media_bytes: bytes,
        media_type: str,
        alt_text: Optional[str] = None,
        caption: Optional[str] = None,
    ) -> str:
        """
        Upload photo to Facebook.

        Args:
            media_bytes: Image bytes
            media_type: MIME type (image/jpeg, image/png)
            alt_text: Accessibility text
            caption: Photo caption

        Returns:
            Photo ID
        """
        if not self.page_id:
            raise MediaUploadError(
                "Page ID required for media upload",
                platform=self.PLATFORM_NAME,
            )

        # Upload as unpublished photo
        response = await self.client.post(
            f"{self.API_BASE}/{self.page_id}/photos",
            data={
                "published": "false",
                "access_token": self._get_access_token(),
            },
            files={
                "source": ("image", media_bytes, media_type),
            },
        )

        result = await self._handle_response(response, "media")

        photo_id = result.get("id")
        if not photo_id:
            raise MediaUploadError(
                "No photo ID in upload response",
                platform=self.PLATFORM_NAME,
            )

        logger.info(f"Facebook: Uploaded photo {photo_id}")
        return photo_id

    async def get_comments(
        self,
        post_id: str,
        limit: int = 100,
        order: str = "chronological",
    ) -> List[Dict[str, Any]]:
        """
        Get comments on a post.

        Args:
            post_id: Post ID
            limit: Max comments to return
            order: 'chronological' or 'reverse_chronological'
        """
        response = await self.client.get(
            f"{self.API_BASE}/{post_id}/comments",
            params={
                "fields": "id,message,from,created_time,like_count,comment_count",
                "order": order,
                "limit": min(limit, 100),
                "access_token": self._get_access_token(),
            },
        )

        result = await self._handle_response(response, "reads")

        comments = []
        for comment in result.get("data", []):
            comments.append({
                "id": comment["id"],
                "text": comment.get("message", ""),
                "author_id": comment.get("from", {}).get("id", ""),
                "author_name": comment.get("from", {}).get("name", ""),
                "created_at": comment.get("created_time"),
                "likes": comment.get("like_count", 0),
                "reply_count": comment.get("comment_count", 0),
            })

        return comments

    async def reply_to_comment(
        self,
        comment_id: str,
        content: str,
    ) -> Dict[str, Any]:
        """Reply to a comment."""
        response = await self.client.post(
            f"{self.API_BASE}/{comment_id}/comments",
            data={
                "message": content,
                "access_token": self._get_access_token(),
            },
        )

        result = await self._handle_response(response, "posts")

        logger.info(f"Facebook: Replied to comment {comment_id}")
        return result

    async def get_page_insights(
        self,
        period: str = "day",
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get page-level insights.

        Args:
            period: 'day', 'week', 'days_28'
            metrics: List of metrics to fetch
        """
        if not self.page_id:
            raise SocialAPIError(
                "Page ID required",
                platform=self.PLATFORM_NAME,
            )

        if not metrics:
            metrics = [
                "page_impressions",
                "page_impressions_unique",
                "page_engaged_users",
                "page_post_engagements",
                "page_fans",
                "page_fans_adds",
                "page_views_total",
            ]

        response = await self.client.get(
            f"{self.API_BASE}/{self.page_id}/insights",
            params={
                "metric": ",".join(metrics),
                "period": period,
                "access_token": self._get_access_token(),
            },
        )

        result = await self._handle_response(response, "reads")

        insights = {
            "page_id": self.page_id,
            "period": period,
            "timestamp": datetime.utcnow().isoformat(),
        }

        for item in result.get("data", []):
            name = item.get("name", "")
            values = item.get("values", [])
            if values:
                insights[name] = values[0].get("value", 0)

        return insights

    async def validate_token(self) -> Dict[str, Any]:
        """Validate and debug the current access token."""
        token = self._get_access_token()

        response = await self.client.get(
            f"{self.API_BASE}/debug_token",
            params={
                "input_token": token,
                "access_token": f"{self.app_id}|{self.app_secret}",
            },
        )

        return await self._handle_response(response, "reads")
