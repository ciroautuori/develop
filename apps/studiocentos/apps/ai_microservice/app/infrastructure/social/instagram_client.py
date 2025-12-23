"""
Instagram Graph API Client.

Production-ready client for Instagram Graph API via Facebook with:
- Media publishing (images, videos, carousels, reels)
- Story publishing
- Insights and analytics
- Comment management
- Hashtag research

API Reference: https://developers.facebook.com/docs/instagram-api
"""

import asyncio
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


class InstagramClient(BaseSocialClient):
    """
    Instagram Graph API Client.

    Supports:
    - Image and video posting
    - Carousel (multi-image) posts
    - Reels publishing
    - Story publishing (via STORIES container)
    - Media insights and analytics
    - Comment management
    - Hashtag research

    Note: Requires Instagram Business/Creator account connected to Facebook Page.
    Uses Facebook Graph API for all operations.

    Example:
        >>> tokens = OAuthTokens(access_token="...")
        >>> async with InstagramClient(tokens=tokens, ig_user_id="123") as client:
        ...     result = await client.post_image(image_url, "Hello Instagram!")
    """

    PLATFORM_NAME = "instagram"
    API_VERSION = "v19.0"
    API_BASE = f"https://graph.facebook.com/{API_VERSION}"

    # Instagram rate limits
    DEFAULT_RATE_LIMITS = {
        "content_publishing": RateLimiter(max_requests=25, window_seconds=86400),  # 25/day
        "reads": RateLimiter(max_requests=200, window_seconds=3600),
        "hashtag": RateLimiter(max_requests=30, window_seconds=604800),  # 30/week
    }

    def __init__(
        self,
        tokens: Optional[OAuthTokens] = None,
        ig_user_id: Optional[str] = None,
        page_access_token: Optional[str] = None,
    ):
        """
        Initialize Instagram client.

        Args:
            tokens: OAuth tokens (Facebook Page access token)
            ig_user_id: Instagram Business Account ID
            page_access_token: Facebook Page access token
        """
        super().__init__(tokens=tokens, rate_limits=self.DEFAULT_RATE_LIMITS.copy())

        self.ig_user_id = ig_user_id or os.getenv("INSTAGRAM_BUSINESS_ID", "")
        self.page_access_token = page_access_token or os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")

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
        """Parse Instagram/Facebook API error message."""
        error = error_data.get("error", {})
        if isinstance(error, dict):
            return error.get("message", "Unknown Instagram API error")
        return str(error) if error else "Unknown Instagram API error"

    def _parse_error_code(self, error_data: Dict[str, Any]) -> Optional[str]:
        """Parse Instagram/Facebook API error code."""
        error = error_data.get("error", {})
        if isinstance(error, dict):
            return str(error.get("code", ""))
        return None

    async def refresh_access_token(self) -> OAuthTokens:
        """Refresh access token via Facebook long-lived token exchange."""
        # Instagram uses Facebook token refresh
        raise AuthenticationError(
            "Use FacebookClient.refresh_access_token() for Instagram tokens",
            platform=self.PLATFORM_NAME,
        )

    async def post(
        self,
        content: str,
        media_ids: Optional[List[str]] = None,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create an Instagram post.

        For images, provide image_url (publicly accessible URL).
        For carousels, provide multiple media_ids from create_media_container.
        """
        if image_url:
            return await self.post_image(image_url, content)
        elif video_url:
            return await self.post_video(video_url, content)
        elif media_ids:
            return await self.post_carousel(media_ids, content)
        else:
            raise PostingError(
                "Instagram requires media (image_url, video_url, or media_ids)",
                platform=self.PLATFORM_NAME,
            )

    async def post_image(
        self,
        image_url: str,
        caption: str,
        location_id: Optional[str] = None,
        user_tags: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Post a single image to Instagram.

        Args:
            image_url: Publicly accessible image URL (JPEG recommended)
            caption: Post caption (up to 2200 characters)
            location_id: Facebook Place ID for location tag
            user_tags: List of user tag positions

        Returns:
            Media object with ID
        """
        if not self.ig_user_id:
            raise PostingError(
                "Instagram Business Account ID required",
                platform=self.PLATFORM_NAME,
            )

        # Step 1: Create media container
        container_params: Dict[str, Any] = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self._get_access_token(),
        }

        if location_id:
            container_params["location_id"] = location_id

        if user_tags:
            container_params["user_tags"] = user_tags

        container_response = await self.client.post(
            f"{self.API_BASE}/{self.ig_user_id}/media",
            data=container_params,
        )

        container_data = await self._handle_response(container_response, "content_publishing")
        container_id = container_data.get("id")

        if not container_id:
            raise PostingError(
                "Failed to create media container",
                platform=self.PLATFORM_NAME,
            )

        # Step 2: Publish the container
        return await self._publish_container(container_id)

    async def post_video(
        self,
        video_url: str,
        caption: str,
        cover_url: Optional[str] = None,
        share_to_feed: bool = True,
        media_type: str = "REELS",
    ) -> Dict[str, Any]:
        """
        Post a video/reel to Instagram.

        Args:
            video_url: Publicly accessible video URL (MP4, max 60s for feed, 90s for reels)
            caption: Post caption
            cover_url: Custom cover image URL
            share_to_feed: Share reel to feed (reels only)
            media_type: 'REELS' or 'VIDEO'

        Returns:
            Media object with ID
        """
        if not self.ig_user_id:
            raise PostingError(
                "Instagram Business Account ID required",
                platform=self.PLATFORM_NAME,
            )

        # Step 1: Create video container
        container_params: Dict[str, Any] = {
            "video_url": video_url,
            "caption": caption,
            "media_type": media_type,
            "access_token": self._get_access_token(),
        }

        if cover_url:
            container_params["cover_url"] = cover_url

        if media_type == "REELS":
            container_params["share_to_feed"] = str(share_to_feed).lower()

        container_response = await self.client.post(
            f"{self.API_BASE}/{self.ig_user_id}/media",
            data=container_params,
        )

        container_data = await self._handle_response(container_response, "content_publishing")
        container_id = container_data.get("id")

        if not container_id:
            raise PostingError(
                "Failed to create video container",
                platform=self.PLATFORM_NAME,
            )

        # Step 2: Wait for video processing
        await self._wait_for_container_ready(container_id)

        # Step 3: Publish
        return await self._publish_container(container_id)

    async def post_carousel(
        self,
        children_ids: List[str],
        caption: str,
    ) -> Dict[str, Any]:
        """
        Post a carousel (multi-image) to Instagram.

        Args:
            children_ids: List of media container IDs (2-10 items)
            caption: Post caption

        Returns:
            Media object with ID
        """
        if not self.ig_user_id:
            raise PostingError(
                "Instagram Business Account ID required",
                platform=self.PLATFORM_NAME,
            )

        if len(children_ids) < 2 or len(children_ids) > 10:
            raise PostingError(
                "Carousel requires 2-10 media items",
                platform=self.PLATFORM_NAME,
            )

        # Create carousel container
        container_params = {
            "media_type": "CAROUSEL",
            "caption": caption,
            "children": ",".join(children_ids),
            "access_token": self._get_access_token(),
        }

        container_response = await self.client.post(
            f"{self.API_BASE}/{self.ig_user_id}/media",
            data=container_params,
        )

        container_data = await self._handle_response(container_response, "content_publishing")
        container_id = container_data.get("id")

        if not container_id:
            raise PostingError(
                "Failed to create carousel container",
                platform=self.PLATFORM_NAME,
            )

        # Publish
        return await self._publish_container(container_id)

    async def create_carousel_item(
        self,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        is_carousel_item: bool = True,
    ) -> str:
        """
        Create a carousel item container.

        Args:
            image_url: Image URL for image item
            video_url: Video URL for video item
            is_carousel_item: Must be True for carousel items

        Returns:
            Container ID
        """
        if not self.ig_user_id:
            raise MediaUploadError(
                "Instagram Business Account ID required",
                platform=self.PLATFORM_NAME,
            )

        params: Dict[str, Any] = {
            "is_carousel_item": "true",
            "access_token": self._get_access_token(),
        }

        if image_url:
            params["image_url"] = image_url
        elif video_url:
            params["video_url"] = video_url
            params["media_type"] = "VIDEO"
        else:
            raise MediaUploadError(
                "Either image_url or video_url required",
                platform=self.PLATFORM_NAME,
            )

        response = await self.client.post(
            f"{self.API_BASE}/{self.ig_user_id}/media",
            data=params,
        )

        result = await self._handle_response(response, "content_publishing")
        container_id = result.get("id")

        if not container_id:
            raise MediaUploadError(
                "Failed to create carousel item",
                platform=self.PLATFORM_NAME,
            )

        # Wait for processing if video
        if video_url:
            await self._wait_for_container_ready(container_id)

        return container_id

    async def _wait_for_container_ready(
        self,
        container_id: str,
        max_wait: int = 300,
    ) -> None:
        """Wait for media container to finish processing."""
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < max_wait:
            response = await self.client.get(
                f"{self.API_BASE}/{container_id}",
                params={
                    "fields": "status_code",
                    "access_token": self._get_access_token(),
                },
            )

            if response.status_code != 200:
                await asyncio.sleep(10)
                continue

            data = response.json()
            status = data.get("status_code")

            if status == "FINISHED":
                return
            elif status == "ERROR":
                raise MediaUploadError(
                    "Media processing failed",
                    platform=self.PLATFORM_NAME,
                )

            await asyncio.sleep(10)

        raise MediaUploadError(
            "Media processing timeout",
            platform=self.PLATFORM_NAME,
        )

    async def _publish_container(self, container_id: str) -> Dict[str, Any]:
        """Publish a media container."""
        response = await self.client.post(
            f"{self.API_BASE}/{self.ig_user_id}/media_publish",
            data={
                "creation_id": container_id,
                "access_token": self._get_access_token(),
            },
        )

        result = await self._handle_response(response, "content_publishing")

        logger.info(f"Instagram: Published media {result.get('id')}")
        return result

    async def delete_post(self, post_id: str) -> bool:
        """
        Delete is not supported by Instagram Graph API.
        Media can only be hidden/archived via the app.
        """
        raise SocialAPIError(
            "Instagram Graph API does not support media deletion",
            platform=self.PLATFORM_NAME,
        )

    async def get_metrics(self, post_id: str) -> Dict[str, Any]:
        """
        Get media insights.

        Returns metrics including:
        - impressions
        - reach
        - engagement (likes, comments, saves, shares)
        - video views (for videos)
        """
        response = await self.client.get(
            f"{self.API_BASE}/{post_id}",
            params={
                "fields": "like_count,comments_count,timestamp,media_type,caption",
                "access_token": self._get_access_token(),
            },
        )

        data = await self._handle_response(response, "reads")

        metrics = {
            "post_id": post_id,
            "platform": "instagram",
            "timestamp": datetime.utcnow().isoformat(),
            "likes": data.get("like_count", 0),
            "comments": data.get("comments_count", 0),
            "media_type": data.get("media_type", ""),
        }

        # Get detailed insights
        try:
            insight_metrics = ["impressions", "reach", "saved"]
            if data.get("media_type") in ("VIDEO", "REELS"):
                insight_metrics.extend(["video_views", "plays"])

            insights_response = await self.client.get(
                f"{self.API_BASE}/{post_id}/insights",
                params={
                    "metric": ",".join(insight_metrics),
                    "access_token": self._get_access_token(),
                },
            )

            if insights_response.status_code == 200:
                insights_data = insights_response.json()
                for insight in insights_data.get("data", []):
                    name = insight.get("name", "")
                    value = insight.get("values", [{}])[0].get("value", 0)
                    metrics[name] = value
        except Exception as e:
            logger.warning(f"Failed to get Instagram insights: {e}")

        # Calculate engagement rate
        reach = metrics.get("reach", 0)
        engagements = metrics["likes"] + metrics["comments"] + metrics.get("saved", 0)
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
    ) -> str:
        """
        Instagram requires publicly accessible URLs, not direct uploads.
        Use your own storage (S3, Cloud Storage) to host the image first.
        """
        raise MediaUploadError(
            "Instagram requires publicly accessible URLs. Host your media first.",
            platform=self.PLATFORM_NAME,
        )

    async def get_comments(
        self,
        post_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get comments on a media post."""
        response = await self.client.get(
            f"{self.API_BASE}/{post_id}/comments",
            params={
                "fields": "id,text,username,timestamp,like_count,replies{id,text,username,timestamp}",
                "limit": min(limit, 50),
                "access_token": self._get_access_token(),
            },
        )

        result = await self._handle_response(response, "reads")

        comments = []
        for comment in result.get("data", []):
            comments.append({
                "id": comment["id"],
                "text": comment.get("text", ""),
                "author_username": comment.get("username", ""),
                "created_at": comment.get("timestamp"),
                "likes": comment.get("like_count", 0),
                "replies": comment.get("replies", {}).get("data", []),
            })

        return comments

    async def reply_to_comment(
        self,
        comment_id: str,
        content: str,
    ) -> Dict[str, Any]:
        """Reply to a comment."""
        response = await self.client.post(
            f"{self.API_BASE}/{comment_id}/replies",
            data={
                "message": content,
                "access_token": self._get_access_token(),
            },
        )

        result = await self._handle_response(response, "content_publishing")

        logger.info(f"Instagram: Replied to comment {comment_id}")
        return result

    async def get_account_insights(
        self,
        period: str = "day",
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get Instagram account insights.

        Args:
            period: 'day', 'week', 'days_28', 'lifetime'
            metrics: List of metrics to fetch
        """
        if not self.ig_user_id:
            raise SocialAPIError(
                "Instagram Business Account ID required",
                platform=self.PLATFORM_NAME,
            )

        if not metrics:
            metrics = [
                "impressions",
                "reach",
                "follower_count",
                "profile_views",
                "website_clicks",
            ]

        # Lifetime metrics
        lifetime_metrics = ["follower_count"]
        daily_metrics = [m for m in metrics if m not in lifetime_metrics]

        insights = {
            "ig_user_id": self.ig_user_id,
            "period": period,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Fetch daily/period metrics
        if daily_metrics:
            response = await self.client.get(
                f"{self.API_BASE}/{self.ig_user_id}/insights",
                params={
                    "metric": ",".join(daily_metrics),
                    "period": period,
                    "access_token": self._get_access_token(),
                },
            )

            if response.status_code == 200:
                data = response.json()
                for item in data.get("data", []):
                    name = item.get("name", "")
                    values = item.get("values", [])
                    if values:
                        insights[name] = values[0].get("value", 0)

        # Fetch lifetime metrics
        if any(m in metrics for m in lifetime_metrics):
            response = await self.client.get(
                f"{self.API_BASE}/{self.ig_user_id}",
                params={
                    "fields": "followers_count,follows_count,media_count",
                    "access_token": self._get_access_token(),
                },
            )

            if response.status_code == 200:
                data = response.json()
                insights["followers"] = data.get("followers_count", 0)
                insights["following"] = data.get("follows_count", 0)
                insights["media_count"] = data.get("media_count", 0)

        return insights

    async def search_hashtag(
        self,
        hashtag: str,
    ) -> Dict[str, Any]:
        """
        Search for a hashtag and get its ID.

        Limited to 30 unique hashtags per 7 days.
        """
        if not self.ig_user_id:
            raise SocialAPIError(
                "Instagram Business Account ID required",
                platform=self.PLATFORM_NAME,
            )

        response = await self.client.get(
            f"{self.API_BASE}/ig_hashtag_search",
            params={
                "user_id": self.ig_user_id,
                "q": hashtag.lstrip("#"),
                "access_token": self._get_access_token(),
            },
        )

        result = await self._handle_response(response, "hashtag")

        data = result.get("data", [])
        if data:
            return {"hashtag": hashtag, "id": data[0].get("id")}

        return {"hashtag": hashtag, "id": None}

    async def get_hashtag_media(
        self,
        hashtag_id: str,
        media_type: str = "recent_media",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get media using a hashtag.

        Args:
            hashtag_id: Hashtag ID from search_hashtag
            media_type: 'recent_media' or 'top_media'
            limit: Max media to return
        """
        if not self.ig_user_id:
            raise SocialAPIError(
                "Instagram Business Account ID required",
                platform=self.PLATFORM_NAME,
            )

        response = await self.client.get(
            f"{self.API_BASE}/{hashtag_id}/{media_type}",
            params={
                "user_id": self.ig_user_id,
                "fields": "id,caption,media_type,like_count,comments_count,timestamp",
                "limit": min(limit, 50),
                "access_token": self._get_access_token(),
            },
        )

        result = await self._handle_response(response, "hashtag")

        return result.get("data", [])
