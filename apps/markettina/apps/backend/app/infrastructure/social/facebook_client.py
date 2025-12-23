"""
Facebook Graph API Client - Production-ready Facebook Page integration.

Features:
- Page post publishing with media
- Scheduled posts
- Post insights and metrics
- Comment management
- Page insights

API Reference: https://developers.facebook.com/docs/graph-api
API Version: v19.0
"""

import logging
from datetime import datetime
from typing import Any

from app.core.config import settings
from app.infrastructure.social.base_client import (
    BaseSocialClient,
    PostMetrics,
    RateLimitConfig,
    SocialAPIError,
    SocialMediaPost,
    SocialPlatform,
)

logger = logging.getLogger(__name__)


class FacebookClient(BaseSocialClient):
    """
    Facebook Graph API client for Page management.

    Rate Limits:
    - Application-level: 200 calls/hour per user
    - Page-level: Varies by endpoint
    - Post creation: 24 posts per day recommended

    Usage:
        client = FacebookClient()
        post = await client.publish_post("Hello Facebook!")
        metrics = await client.get_post_metrics(post.post_id)
    """

    API_VERSION = "v19.0"
    BASE_URL = "https://graph.facebook.com"

    def __init__(
        self,
        page_id: str | None = None,
        page_access_token: str | None = None,
        app_id: str | None = None,
        app_secret: str | None = None,
    ):
        super().__init__(
            rate_limit_config=RateLimitConfig(
                requests_per_window=200,
                window_seconds=3600,  # 1 hour
            ),
            timeout=30.0,
            max_retries=3,
        )

        self._page_id = page_id or settings.FACEBOOK_PAGE_ID
        self._page_access_token = page_access_token or settings.META_ACCESS_TOKEN
        self._app_id = app_id or settings.META_APP_ID
        self._app_secret = app_secret or settings.META_APP_SECRET

    def _get_platform(self) -> SocialPlatform:
        return SocialPlatform.FACEBOOK

    def _get_base_url(self) -> str:
        return f"{self.BASE_URL}/{self.API_VERSION}"

    def _get_auth_headers(self) -> dict[str, str]:
        """Return empty headers - Facebook uses access_token in params."""
        return {}

    def _get_auth_params(self) -> dict[str, str]:
        """Return access token as query parameter."""
        if not self._page_access_token:
            raise SocialAPIError(
                "Facebook Page Access Token not configured",
                SocialPlatform.FACEBOOK,
            )
        return {"access_token": self._page_access_token}

    def is_configured(self) -> bool:
        """Check if Facebook credentials are configured."""
        return bool(self._page_id and self._page_access_token)

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json: dict | None = None,
        data: dict | None = None,
        params: dict | None = None,
        extra_headers: dict | None = None,
    ) -> dict[str, Any]:
        """Override to add access token to all requests."""
        params = {**(params or {}), **self._get_auth_params()}
        return await super()._request(
            method, endpoint, json=json, data=data, params=params, extra_headers=extra_headers
        )

    async def publish_post(
        self,
        content: str,
        media_urls: list[str] | None = None,
        link: str | None = None,
        scheduled_time: datetime | None = None,
        **kwargs: Any,
    ) -> SocialMediaPost:
        """
        Publish a post to the Facebook Page.

        Args:
            content: Post message
            media_urls: Optional photo URLs (first one used for single photo)
            link: Optional link to share
            scheduled_time: Optional future publish time

        Returns:
            SocialMediaPost with created post data
        """
        if not self._page_id:
            raise SocialAPIError("Page ID not configured", SocialPlatform.FACEBOOK)

        payload: dict[str, Any] = {"message": content}

        if link:
            payload["link"] = link

        if scheduled_time:
            # Unix timestamp for scheduled posts
            payload["published"] = False
            payload["scheduled_publish_time"] = int(scheduled_time.timestamp())

        # Handle media
        if media_urls:
            if len(media_urls) == 1:
                # Single photo post
                payload["url"] = media_urls[0]
                endpoint = f"/{self._page_id}/photos"
            else:
                # Multiple photos - create photo objects first, then multi-photo post
                photo_ids = await self._upload_photos(media_urls)
                payload["attached_media"] = [
                    {"media_fbid": pid} for pid in photo_ids
                ]
                endpoint = f"/{self._page_id}/feed"
        else:
            endpoint = f"/{self._page_id}/feed"

        response = await self._post(endpoint, data=payload)

        post_id = response.get("id", response.get("post_id", ""))

        return SocialMediaPost(
            post_id=post_id,
            platform=SocialPlatform.FACEBOOK,
            content=content,
            media_urls=media_urls or [],
            permalink=f"https://facebook.com/{post_id}" if post_id else None,
            created_at=scheduled_time or datetime.utcnow(),
        )

    async def _upload_photos(self, media_urls: list[str]) -> list[str]:
        """Upload multiple photos and return their IDs."""
        photo_ids = []

        for url in media_urls:
            response = await self._post(
                f"/{self._page_id}/photos",
                data={
                    "url": url,
                    "published": False,  # Create unpublished photo object
                },
            )
            if pid := response.get("id"):
                photo_ids.append(pid)

        return photo_ids

    async def get_post_metrics(self, post_id: str) -> PostMetrics:
        """
        Get engagement metrics for a post.

        Args:
            post_id: Facebook post ID

        Returns:
            PostMetrics with engagement data
        """
        # Get post insights
        response = await self._get(
            f"/{post_id}/insights",
            params={
                "metric": "post_impressions,post_impressions_unique,post_engaged_users,post_clicks",
            },
        )

        insights = {}
        for item in response.get("data", []):
            name = item.get("name", "")
            values = item.get("values", [])
            if values:
                insights[name] = values[0].get("value", 0)

        # Get reaction counts
        reactions_response = await self._get(
            f"/{post_id}",
            params={
                "fields": "reactions.summary(true),comments.summary(true),shares",
            },
        )

        reactions = reactions_response.get("reactions", {}).get("summary", {})
        comments = reactions_response.get("comments", {}).get("summary", {})
        shares = reactions_response.get("shares", {})

        impressions = insights.get("post_impressions", 0)
        reach = insights.get("post_impressions_unique", 0)
        engaged_users = insights.get("post_engaged_users", 0)
        clicks = insights.get("post_clicks", 0)
        likes = reactions.get("total_count", 0)
        comment_count = comments.get("total_count", 0)
        share_count = shares.get("count", 0)

        engagement_rate = (engaged_users / reach * 100) if reach > 0 else 0.0

        return PostMetrics(
            post_id=post_id,
            platform=SocialPlatform.FACEBOOK,
            impressions=impressions,
            reach=reach,
            likes=likes,
            comments=comment_count,
            shares=share_count,
            clicks=clicks,
            engagement_rate=round(engagement_rate, 2),
        )

    async def get_page_posts(
        self,
        limit: int = 10,
        since: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get recent page posts.

        Args:
            limit: Max posts to return
            since: Only return posts after this date

        Returns:
            List of post data
        """
        params: dict[str, Any] = {
            "fields": "id,message,created_time,permalink_url,shares,reactions.summary(true)",
            "limit": min(limit, 100),
        }

        if since:
            params["since"] = int(since.timestamp())

        response = await self._get(f"/{self._page_id}/posts", params=params)

        return response.get("data", [])

    async def get_comments(
        self,
        post_id: str,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """
        Get comments on a post.

        Args:
            post_id: Post ID
            limit: Max comments to return

        Returns:
            List of comments
        """
        response = await self._get(
            f"/{post_id}/comments",
            params={
                "fields": "id,message,from,created_time,like_count",
                "order": "reverse_chronological",
                "limit": min(limit, 100),
            },
        )

        return response.get("data", [])

    async def reply_to_comment(
        self,
        comment_id: str,
        message: str,
    ) -> dict[str, Any]:
        """
        Reply to a comment.

        Args:
            comment_id: Comment ID to reply to
            message: Reply text

        Returns:
            Created comment data
        """
        response = await self._post(
            f"/{comment_id}/comments",
            data={"message": message},
        )

        return response

    async def get_page_insights(
        self,
        period: str = "day",
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Get page-level insights.

        Args:
            period: Aggregation period (day, week, days_28)
            since: Start date
            until: End date

        Returns:
            Page insights data
        """
        params: dict[str, Any] = {
            "metric": "page_impressions,page_impressions_unique,page_engaged_users,page_post_engagements,page_fans",
            "period": period,
        }

        if since:
            params["since"] = int(since.timestamp())
        if until:
            params["until"] = int(until.timestamp())

        response = await self._get(f"/{self._page_id}/insights", params=params)

        insights = {}
        for item in response.get("data", []):
            name = item.get("name", "")
            values = item.get("values", [])
            insights[name] = [v.get("value", 0) for v in values]

        return insights

    async def delete_post(self, post_id: str) -> bool:
        """
        Delete a post.

        Args:
            post_id: Post ID to delete

        Returns:
            True if deleted successfully
        """
        try:
            response = await self._delete(f"/{post_id}")
            return response.get("success", False)
        except SocialAPIError:
            return False

    async def schedule_post(
        self,
        content: str,
        scheduled_time: datetime,
        media_urls: list[str] | None = None,
        link: str | None = None,
    ) -> SocialMediaPost:
        """
        Schedule a post for future publication.

        Args:
            content: Post message
            scheduled_time: When to publish (must be 10 min to 6 months in future)
            media_urls: Optional media
            link: Optional link

        Returns:
            SocialMediaPost with scheduled post data
        """
        return await self.publish_post(
            content=content,
            media_urls=media_urls,
            link=link,
            scheduled_time=scheduled_time,
        )

    async def get_scheduled_posts(self) -> list[dict[str, Any]]:
        """
        Get scheduled (unpublished) posts.

        Returns:
            List of scheduled posts
        """
        response = await self._get(
            f"/{self._page_id}/scheduled_posts",
            params={
                "fields": "id,message,scheduled_publish_time,created_time",
            },
        )

        return response.get("data", [])
