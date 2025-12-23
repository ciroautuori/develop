"""
LinkedIn Marketing API Client - Production-ready LinkedIn integration.

Features:
- Post publishing (text, images, articles, documents)
- Company page posting
- Post analytics
- Share statistics
- Organization insights

API Reference: https://learn.microsoft.com/en-us/linkedin/marketing/
API Version: v2
"""

import logging
from datetime import datetime
from typing import Any
from urllib.parse import urlencode

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


class LinkedInClient(BaseSocialClient):
    """
    LinkedIn Marketing API client.

    Features:
    - Personal profile posting
    - Company page posting
    - Image and document uploads
    - Post analytics
    - OAuth 2.0 authentication

    Rate Limits:
    - 100 share requests per day
    - 600 API calls per day

    Usage:
        client = LinkedInClient()
        post = await client.publish_post("Hello LinkedIn!")
        metrics = await client.get_post_metrics(post.post_id)
    """

    API_VERSION = "v2"
    BASE_URL = "https://api.linkedin.com"

    def __init__(
        self,
        access_token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
    ):
        super().__init__(
            rate_limit_config=RateLimitConfig(
                requests_per_window=100,
                window_seconds=86400,  # 24 hours
            ),
            timeout=30.0,
            max_retries=3,
        )

        self._access_token = access_token or settings.LINKEDIN_ACCESS_TOKEN
        self._client_id = client_id or settings.LINKEDIN_CLIENT_ID
        self._client_secret = client_secret or settings.LINKEDIN_CLIENT_SECRET
        self._redirect_uri = redirect_uri or settings.LINKEDIN_REDIRECT_URI

        self._person_urn: str | None = None

    def _get_platform(self) -> SocialPlatform:
        return SocialPlatform.LINKEDIN

    def _get_base_url(self) -> str:
        return self.BASE_URL

    def _get_auth_headers(self) -> dict[str, str]:
        if not self._access_token:
            raise SocialAPIError(
                "LinkedIn Access Token not configured",
                SocialPlatform.LINKEDIN,
            )
        return {
            "Authorization": f"Bearer {self._access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202401",
        }

    def is_configured(self) -> bool:
        return bool(self._access_token)

    def get_authorization_url(self, state: str = "linkedin_auth") -> str:
        """
        Generate OAuth authorization URL.

        Args:
            state: State parameter for CSRF protection

        Returns:
            Authorization URL for user redirect
        """
        params = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "state": state,
            "scope": "openid profile email w_member_social",
        }
        return f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> dict[str, Any]:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Token data including access_token and expires_in
        """
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "redirect_uri": self._redirect_uri,
                },
            )

            if response.status_code != 200:
                raise SocialAPIError(
                    f"Token exchange failed: {response.text}",
                    SocialPlatform.LINKEDIN,
                    status_code=response.status_code,
                )

            return response.json()

    async def get_profile(self) -> dict[str, Any]:
        """
        Get authenticated user's profile.

        Returns:
            Profile data including URN, name, etc.
        """
        response = await self._get(
            "/v2/userinfo",
        )

        return response

    async def _get_person_urn(self) -> str:
        """Get the authenticated user's URN for posting."""
        if self._person_urn:
            return self._person_urn

        profile = await self.get_profile()
        sub = profile.get("sub", "")
        self._person_urn = f"urn:li:person:{sub}"
        return self._person_urn

    async def publish_post(
        self,
        content: str,
        media_urls: list[str] | None = None,
        article_url: str | None = None,
        visibility: str = "PUBLIC",
        **kwargs: Any,
    ) -> SocialMediaPost:
        """
        Publish a post to LinkedIn.

        Args:
            content: Post text
            media_urls: Optional image URLs
            article_url: Optional article link to share
            visibility: PUBLIC or CONNECTIONS

        Returns:
            SocialMediaPost with created post data
        """
        author_urn = await self._get_person_urn()

        # Build share content
        share_commentary = {
            "text": content,
        }

        # Build the share request
        payload: dict[str, Any] = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility,
            },
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": share_commentary,
                    "shareMediaCategory": "NONE",
                },
            },
        }

        specific_content = payload["specificContent"]["com.linkedin.ugc.ShareContent"]

        # Handle article share
        if article_url:
            specific_content["shareMediaCategory"] = "ARTICLE"
            specific_content["media"] = [
                {
                    "status": "READY",
                    "originalUrl": article_url,
                }
            ]

        # Handle image upload
        elif media_urls:
            # Upload images first
            media_assets = await self._upload_images(author_urn, media_urls)

            if media_assets:
                specific_content["shareMediaCategory"] = "IMAGE"
                specific_content["media"] = media_assets

        # Create the post
        response = await self._post(
            "/v2/ugcPosts",
            json=payload,
        )

        post_id = response.get("id", "")

        # Extract share ID from URN
        share_id = post_id.split(":")[-1] if ":" in post_id else post_id

        return SocialMediaPost(
            post_id=post_id,
            platform=SocialPlatform.LINKEDIN,
            content=content,
            media_urls=media_urls or [],
            permalink=f"https://www.linkedin.com/feed/update/{post_id}" if post_id else None,
            created_at=datetime.utcnow(),
        )

    async def _upload_images(
        self,
        owner_urn: str,
        image_urls: list[str],
    ) -> list[dict[str, Any]]:
        """
        Upload images to LinkedIn.

        Args:
            owner_urn: Owner URN (person or organization)
            image_urls: List of image URLs to upload

        Returns:
            List of media assets for sharing
        """
        import httpx

        media_assets = []

        for image_url in image_urls[:20]:  # Max 20 images
            # Step 1: Register upload
            register_response = await self._post(
                "/v2/assets?action=registerUpload",
                json={
                    "registerUploadRequest": {
                        "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                        "owner": owner_urn,
                        "serviceRelationships": [
                            {
                                "relationshipType": "OWNER",
                                "identifier": "urn:li:userGeneratedContent",
                            }
                        ],
                    }
                },
            )

            upload_data = register_response.get("value", {})
            asset = upload_data.get("asset", "")
            upload_mechanism = upload_data.get("uploadMechanism", {})
            upload_url = (
                upload_mechanism.get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {})
                .get("uploadUrl", "")
            )

            if not upload_url:
                continue

            # Step 2: Download image from URL
            async with httpx.AsyncClient() as client:
                img_response = await client.get(image_url)
                if img_response.status_code != 200:
                    continue

                image_data = img_response.content

                # Step 3: Upload to LinkedIn
                upload_response = await client.put(
                    upload_url,
                    content=image_data,
                    headers={
                        "Authorization": f"Bearer {self._access_token}",
                        "Content-Type": "application/octet-stream",
                    },
                )

                if upload_response.status_code in (200, 201):
                    media_assets.append({
                        "status": "READY",
                        "media": asset,
                    })

        return media_assets

    async def get_post_metrics(self, post_id: str) -> PostMetrics:
        """
        Get engagement metrics for a post.

        Args:
            post_id: LinkedIn post URN

        Returns:
            PostMetrics with engagement data
        """
        # Get share statistics
        response = await self._get(
            f"/v2/socialActions/{post_id}",
        )

        likes_summary = response.get("likesSummary", {})
        comments_summary = response.get("commentsSummary", {})

        likes = likes_summary.get("totalLikes", 0)
        comments = comments_summary.get("totalFirstLevelComments", 0)

        # Try to get share statistics (requires additional permissions)
        try:
            stats_response = await self._get(
                f"/v2/shares/{post_id.split(':')[-1]}/statistics",
            )
            impressions = stats_response.get("totalShareStatistics", {}).get("impressionCount", 0)
            shares = stats_response.get("totalShareStatistics", {}).get("shareCount", 0)
            clicks = stats_response.get("totalShareStatistics", {}).get("clickCount", 0)
        except SocialAPIError:
            impressions = shares = clicks = 0

        total_engagement = likes + comments + shares
        engagement_rate = (total_engagement / impressions * 100) if impressions > 0 else 0.0

        return PostMetrics(
            post_id=post_id,
            platform=SocialPlatform.LINKEDIN,
            impressions=impressions,
            reach=impressions,  # LinkedIn doesn't separate reach
            likes=likes,
            comments=comments,
            shares=shares,
            clicks=clicks,
            engagement_rate=round(engagement_rate, 2),
        )

    async def get_company_posts(
        self,
        organization_urn: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Get recent posts from a company page.

        Args:
            organization_urn: Organization URN (urn:li:organization:ID)
            limit: Max posts to return

        Returns:
            List of post data
        """
        response = await self._get(
            "/v2/ugcPosts",
            params={
                "q": "authors",
                "authors": f"List({organization_urn})",
                "count": min(limit, 100),
            },
        )

        return response.get("elements", [])

    async def delete_post(self, post_id: str) -> bool:
        """
        Delete a post.

        Args:
            post_id: Post URN to delete

        Returns:
            True if deleted successfully
        """
        try:
            await self._delete(f"/v2/ugcPosts/{post_id}")
            return True
        except SocialAPIError:
            return False

    async def get_organization_followers(
        self,
        organization_id: str,
    ) -> dict[str, Any]:
        """
        Get organization follower statistics.

        Args:
            organization_id: Organization ID (without URN prefix)

        Returns:
            Follower statistics
        """
        response = await self._get(
            f"/v2/organizationalEntityFollowerStatistics",
            params={
                "q": "organizationalEntity",
                "organizationalEntity": f"urn:li:organization:{organization_id}",
            },
        )

        elements = response.get("elements", [])
        if elements:
            return elements[0].get("followerCounts", {})

        return {}

    async def get_organization_share_statistics(
        self,
        organization_id: str,
    ) -> dict[str, Any]:
        """
        Get organization share statistics (impressions, engagement).

        Args:
            organization_id: Organization ID

        Returns:
            Share statistics
        """
        response = await self._get(
            f"/v2/organizationalEntityShareStatistics",
            params={
                "q": "organizationalEntity",
                "organizationalEntity": f"urn:li:organization:{organization_id}",
            },
        )

        elements = response.get("elements", [])
        if elements:
            return elements[0].get("totalShareStatistics", {})

        return {}
