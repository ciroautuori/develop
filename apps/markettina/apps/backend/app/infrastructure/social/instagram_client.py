"""
Instagram Graph API Client - Production-ready Instagram Business integration.

Features:
- Media publishing (images, carousels, reels)
- Stories publishing
- Post insights and metrics
- Comment management
- Account insights
- Hashtag research

API Reference: https://developers.facebook.com/docs/instagram-api
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


class InstagramClient(BaseSocialClient):
    """
    Instagram Graph API client for Business accounts.

    Requirements:
    - Instagram Business or Creator Account
    - Connected Facebook Page
    - Valid access token with instagram_basic, instagram_content_publish permissions

    Rate Limits:
    - Content publishing: 25 posts per 24 hours
    - API calls: Shares Facebook limits

    Usage:
        client = InstagramClient()
        post = await client.publish_post("Hello Instagram!", media_urls=["https://..."])
        metrics = await client.get_post_metrics(post.post_id)
    """

    API_VERSION = "v19.0"
    BASE_URL = "https://graph.facebook.com"

    def __init__(
        self,
        account_id: str | None = None,
        access_token: str | None = None,
    ):
        super().__init__(
            rate_limit_config=RateLimitConfig(
                requests_per_window=200,
                window_seconds=3600,
            ),
            timeout=60.0,  # Media uploads can be slow
            max_retries=3,
        )

        self._account_id = account_id or settings.INSTAGRAM_ACCOUNT_ID
        self._access_token = access_token or settings.META_ACCESS_TOKEN

    def _get_platform(self) -> SocialPlatform:
        return SocialPlatform.INSTAGRAM

    def _get_base_url(self) -> str:
        return f"{self.BASE_URL}/{self.API_VERSION}"

    def _get_auth_headers(self) -> dict[str, str]:
        return {}

    def _get_auth_params(self) -> dict[str, str]:
        if not self._access_token:
            raise SocialAPIError(
                "Instagram Access Token not configured",
                SocialPlatform.INSTAGRAM,
            )
        return {"access_token": self._access_token}

    def is_configured(self) -> bool:
        return bool(self._account_id and self._access_token)

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
        params = {**(params or {}), **self._get_auth_params()}
        return await super()._request(
            method, endpoint, json=json, data=data, params=params, extra_headers=extra_headers
        )

    async def publish_post(
        self,
        content: str,
        media_urls: list[str] | None = None,
        media_type: str = "IMAGE",
        **kwargs: Any,
    ) -> SocialMediaPost:
        """
        Publish a post to Instagram.

        Instagram requires media for all posts. This is a two-step process:
        1. Create media container
        2. Publish the container

        Args:
            content: Caption text
            media_urls: Required media URLs (images or video)
            media_type: IMAGE, VIDEO, or CAROUSEL_ALBUM

        Returns:
            SocialMediaPost with created post data
        """
        if not self._account_id:
            raise SocialAPIError("Instagram Account ID not configured", SocialPlatform.INSTAGRAM)

        if not media_urls:
            raise SocialAPIError(
                "Instagram requires at least one media URL",
                SocialPlatform.INSTAGRAM,
            )

        # Determine media type and create appropriate container
        if len(media_urls) > 1:
            # Carousel post
            container_id = await self._create_carousel_container(content, media_urls)
        elif media_type == "VIDEO" or media_urls[0].endswith(('.mp4', '.mov')):
            # Video/Reel post
            container_id = await self._create_video_container(content, media_urls[0])
        else:
            # Single image post
            container_id = await self._create_image_container(content, media_urls[0])

        # Publish the container
        response = await self._post(
            f"/{self._account_id}/media_publish",
            data={"creation_id": container_id},
        )

        post_id = response.get("id", "")

        return SocialMediaPost(
            post_id=post_id,
            platform=SocialPlatform.INSTAGRAM,
            content=content,
            media_urls=media_urls,
            permalink=await self._get_permalink(post_id) if post_id else None,
            created_at=datetime.utcnow(),
        )

    async def _create_image_container(
        self,
        caption: str,
        image_url: str,
    ) -> str:
        """Create single image container."""
        response = await self._post(
            f"/{self._account_id}/media",
            data={
                "image_url": image_url,
                "caption": caption,
            },
        )
        return response.get("id", "")

    async def _create_video_container(
        self,
        caption: str,
        video_url: str,
        media_type: str = "REELS",
    ) -> str:
        """Create video/reel container."""
        response = await self._post(
            f"/{self._account_id}/media",
            data={
                "video_url": video_url,
                "caption": caption,
                "media_type": media_type,
            },
        )

        container_id = response.get("id", "")

        # Wait for video processing
        await self._wait_for_container_ready(container_id)

        return container_id

    async def _create_carousel_container(
        self,
        caption: str,
        media_urls: list[str],
    ) -> str:
        """Create carousel container with multiple images/videos."""
        # First, create individual media containers
        children_ids = []

        for url in media_urls[:10]:  # Max 10 items in carousel
            if url.endswith(('.mp4', '.mov')):
                response = await self._post(
                    f"/{self._account_id}/media",
                    data={"video_url": url, "is_carousel_item": True},
                )
            else:
                response = await self._post(
                    f"/{self._account_id}/media",
                    data={"image_url": url, "is_carousel_item": True},
                )
            children_ids.append(response.get("id", ""))

        # Create carousel container
        response = await self._post(
            f"/{self._account_id}/media",
            data={
                "media_type": "CAROUSEL",
                "caption": caption,
                "children": ",".join(children_ids),
            },
        )

        return response.get("id", "")

    async def _wait_for_container_ready(
        self,
        container_id: str,
        max_attempts: int = 30,
        interval: float = 2.0,
    ) -> None:
        """Wait for video container to finish processing."""
        import asyncio

        for _ in range(max_attempts):
            response = await self._get(
                f"/{container_id}",
                params={"fields": "status_code,status"},
            )

            status = response.get("status_code")
            if status == "FINISHED":
                return
            if status == "ERROR":
                error_msg = response.get("status", "Unknown error")
                raise SocialAPIError(
                    f"Video processing failed: {error_msg}",
                    SocialPlatform.INSTAGRAM,
                )

            await asyncio.sleep(interval)

        raise SocialAPIError(
            "Video processing timeout",
            SocialPlatform.INSTAGRAM,
        )

    async def _get_permalink(self, post_id: str) -> str | None:
        """Get permalink for a post."""
        try:
            response = await self._get(
                f"/{post_id}",
                params={"fields": "permalink"},
            )
            return response.get("permalink")
        except SocialAPIError:
            return None

    async def get_post_metrics(self, post_id: str) -> PostMetrics:
        """
        Get engagement metrics for a post.

        Args:
            post_id: Instagram media ID

        Returns:
            PostMetrics with engagement data
        """
        # Get basic metrics
        response = await self._get(
            f"/{post_id}",
            params={"fields": "like_count,comments_count,timestamp,media_type"},
        )

        likes = response.get("like_count", 0)
        comments = response.get("comments_count", 0)

        # Get insights (requires business account)
        try:
            insights_response = await self._get(
                f"/{post_id}/insights",
                params={"metric": "impressions,reach,saved,shares"},
            )

            insights = {}
            for item in insights_response.get("data", []):
                insights[item["name"]] = item["values"][0]["value"]

            impressions = insights.get("impressions", 0)
            reach = insights.get("reach", 0)
            saves = insights.get("saved", 0)
            shares = insights.get("shares", 0)
        except SocialAPIError:
            impressions = reach = saves = shares = 0

        total_engagement = likes + comments + saves + shares
        engagement_rate = (total_engagement / reach * 100) if reach > 0 else 0.0

        return PostMetrics(
            post_id=post_id,
            platform=SocialPlatform.INSTAGRAM,
            impressions=impressions,
            reach=reach,
            likes=likes,
            comments=comments,
            shares=shares,
            saves=saves,
            engagement_rate=round(engagement_rate, 2),
        )

    async def get_account_insights(
        self,
        period: str = "day",
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Get account-level insights.

        Args:
            period: Aggregation period (day, week, days_28, lifetime)
            since: Start date
            until: End date

        Returns:
            Account insights data
        """
        metrics = [
            "impressions",
            "reach",
            "profile_views",
            "website_clicks",
            "follower_count",
            "email_contacts",
        ]

        params: dict[str, Any] = {
            "metric": ",".join(metrics),
            "period": period,
        }

        if since:
            params["since"] = int(since.timestamp())
        if until:
            params["until"] = int(until.timestamp())

        response = await self._get(f"/{self._account_id}/insights", params=params)

        insights = {}
        for item in response.get("data", []):
            name = item.get("name", "")
            values = item.get("values", [])
            insights[name] = [v.get("value", 0) for v in values]

        return insights

    async def get_recent_media(
        self,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """
        Get recent media posts.

        Args:
            limit: Max posts to return

        Returns:
            List of media data
        """
        response = await self._get(
            f"/{self._account_id}/media",
            params={
                "fields": "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count",
                "limit": min(limit, 100),
            },
        )

        return response.get("data", [])

    async def get_comments(
        self,
        media_id: str,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """
        Get comments on a media post.

        Args:
            media_id: Media ID
            limit: Max comments to return

        Returns:
            List of comments
        """
        response = await self._get(
            f"/{media_id}/comments",
            params={
                "fields": "id,text,username,timestamp,like_count",
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
            Created reply data
        """
        response = await self._post(
            f"/{comment_id}/replies",
            data={"message": message},
        )

        return response

    async def get_hashtag_search(
        self,
        hashtag: str,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """
        Search for recent media with a hashtag.

        Args:
            hashtag: Hashtag to search (without #)
            limit: Max results

        Returns:
            List of media with hashtag
        """
        # First, get hashtag ID
        search_response = await self._get(
            "/ig_hashtag_search",
            params={
                "user_id": self._account_id,
                "q": hashtag.lstrip("#"),
            },
        )

        hashtag_data = search_response.get("data", [])
        if not hashtag_data:
            return []

        hashtag_id = hashtag_data[0].get("id")

        # Get recent media
        response = await self._get(
            f"/{hashtag_id}/recent_media",
            params={
                "user_id": self._account_id,
                "fields": "id,caption,media_type,permalink,like_count,comments_count",
                "limit": min(limit, 50),
            },
        )

        return response.get("data", [])

    async def publish_story(
        self,
        media_url: str,
        media_type: str = "IMAGE",
    ) -> SocialMediaPost:
        """
        Publish a story.

        Args:
            media_url: Image or video URL
            media_type: IMAGE or VIDEO

        Returns:
            SocialMediaPost with story data
        """
        # Create story container
        data: dict[str, Any] = {"media_type": "STORIES"}

        if media_type == "VIDEO":
            data["video_url"] = media_url
        else:
            data["image_url"] = media_url

        response = await self._post(
            f"/{self._account_id}/media",
            data=data,
        )

        container_id = response.get("id", "")

        if media_type == "VIDEO":
            await self._wait_for_container_ready(container_id)

        # Publish story
        publish_response = await self._post(
            f"/{self._account_id}/media_publish",
            data={"creation_id": container_id},
        )

        story_id = publish_response.get("id", "")

        return SocialMediaPost(
            post_id=story_id,
            platform=SocialPlatform.INSTAGRAM,
            content="",
            media_urls=[media_url],
            created_at=datetime.utcnow(),
        )
