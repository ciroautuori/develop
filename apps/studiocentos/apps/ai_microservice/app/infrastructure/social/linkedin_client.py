"""
LinkedIn API Client.

Production-ready client for LinkedIn API with:
- UGC Post creation
- Image/Video upload
- Analytics and insights
- Comment management
- Organization page support

API Reference: https://learn.microsoft.com/en-us/linkedin/
"""

import base64
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


class LinkedInClient(BaseSocialClient):
    """
    LinkedIn API Client.

    Supports:
    - UGC Post creation (text, images, videos, articles)
    - Organization (company) page posting
    - Share statistics and analytics
    - Comment management
    - OAuth 2.0 token refresh

    Note: Uses LinkedIn Marketing API for organization pages
    and Community Management API for comments.

    Example:
        >>> tokens = OAuthTokens(access_token="...")
        >>> async with LinkedInClient(tokens=tokens) as client:
        ...     result = await client.post("Hello LinkedIn!")
    """

    PLATFORM_NAME = "linkedin"
    API_BASE = "https://api.linkedin.com/v2"
    REST_API_BASE = "https://api.linkedin.com/rest"
    OAUTH_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

    # LinkedIn rate limits (varies by endpoint)
    DEFAULT_RATE_LIMITS = {
        "shares": RateLimiter(max_requests=100, window_seconds=86400),  # 100/day
        "media": RateLimiter(max_requests=50, window_seconds=86400),
        "analytics": RateLimiter(max_requests=100, window_seconds=86400),
    }

    def __init__(
        self,
        tokens: Optional[OAuthTokens] = None,
        organization_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """
        Initialize LinkedIn client.

        Args:
            tokens: OAuth 2.0 access tokens
            organization_id: LinkedIn Organization (company) URN
            client_id: LinkedIn App Client ID
            client_secret: LinkedIn App Client Secret
        """
        super().__init__(tokens=tokens, rate_limits=self.DEFAULT_RATE_LIMITS.copy())

        self.organization_id = organization_id or os.getenv("LINKEDIN_ORGANIZATION_ID", "")
        self.client_id = client_id or os.getenv("LINKEDIN_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("LINKEDIN_CLIENT_SECRET", "")

        self._person_id: Optional[str] = None

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get LinkedIn authorization headers."""
        headers = super()._get_auth_headers()
        headers.update({
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202401",
        })
        return headers

    def _parse_error_message(self, error_data: Dict[str, Any]) -> str:
        """Parse LinkedIn API error message."""
        if "message" in error_data:
            return error_data["message"]
        if "serviceErrorCode" in error_data:
            return f"Error {error_data['serviceErrorCode']}: {error_data.get('message', 'Unknown error')}"
        return "Unknown LinkedIn API error"

    def _parse_error_code(self, error_data: Dict[str, Any]) -> Optional[str]:
        """Parse LinkedIn API error code."""
        return str(error_data.get("serviceErrorCode", error_data.get("code", "")))

    async def refresh_access_token(self) -> OAuthTokens:
        """Refresh OAuth 2.0 access token."""
        if not self.tokens or not self.tokens.refresh_token:
            raise AuthenticationError(
                "No refresh token available",
                platform=self.PLATFORM_NAME,
            )

        response = await self.client.post(
            self.OAUTH_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.tokens.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )

        if response.status_code != 200:
            raise AuthenticationError(
                f"Token refresh failed: {response.text}",
                platform=self.PLATFORM_NAME,
                status_code=response.status_code,
            )

        return OAuthTokens.from_response(response.json())

    async def get_person_id(self) -> str:
        """Get the authenticated user's person URN."""
        if self._person_id:
            return self._person_id

        await self.ensure_valid_token()

        response = await self.client.get(
            f"{self.API_BASE}/userinfo",
            headers=self._get_auth_headers(),
        )

        if response.status_code != 200:
            raise AuthenticationError(
                f"Failed to get user info: {response.text}",
                platform=self.PLATFORM_NAME,
            )

        data = response.json()
        self._person_id = data.get("sub")  # OpenID Connect subject
        return self._person_id

    async def post(
        self,
        content: str,
        media_ids: Optional[List[str]] = None,
        link: Optional[str] = None,
        link_title: Optional[str] = None,
        link_description: Optional[str] = None,
        as_organization: bool = False,
        visibility: str = "PUBLIC",
    ) -> Dict[str, Any]:
        """
        Create a LinkedIn post using UGC API.

        Args:
            content: Post text (up to 3000 characters)
            media_ids: List of uploaded media URNs
            link: URL to share as article
            link_title: Title for shared link
            link_description: Description for shared link
            as_organization: Post as organization page
            visibility: 'PUBLIC', 'CONNECTIONS', or 'LOGGED_IN'

        Returns:
            Post data including URN
        """
        await self.ensure_valid_token()

        # Determine author
        if as_organization and self.organization_id:
            author = f"urn:li:organization:{self.organization_id}"
        else:
            person_id = await self.get_person_id()
            author = f"urn:li:person:{person_id}"

        # Build post payload
        payload: Dict[str, Any] = {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility,
            },
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content,
                    },
                    "shareMediaCategory": "NONE",
                },
            },
        }

        share_content = payload["specificContent"]["com.linkedin.ugc.ShareContent"]

        # Add media
        if media_ids:
            share_content["shareMediaCategory"] = "IMAGE"
            share_content["media"] = [
                {
                    "status": "READY",
                    "media": media_urn,
                }
                for media_urn in media_ids
            ]

        # Add article/link
        elif link:
            share_content["shareMediaCategory"] = "ARTICLE"
            share_content["media"] = [
                {
                    "status": "READY",
                    "originalUrl": link,
                    "title": {"text": link_title or ""},
                    "description": {"text": link_description or ""},
                }
            ]

        response = await self.client.post(
            f"{self.API_BASE}/ugcPosts",
            headers={
                **self._get_auth_headers(),
                "Content-Type": "application/json",
            },
            json=payload,
        )

        result = await self._handle_response(response, "shares")

        logger.info(f"LinkedIn: Posted as {author}, id={result.get('id')}")
        return result

    async def delete_post(self, post_id: str) -> bool:
        """Delete a post."""
        await self.ensure_valid_token()

        # URL-encode the URN
        encoded_id = post_id.replace(":", "%3A")

        response = await self.client.delete(
            f"{self.API_BASE}/ugcPosts/{encoded_id}",
            headers=self._get_auth_headers(),
        )

        return response.status_code == 204

    async def get_metrics(self, post_id: str) -> Dict[str, Any]:
        """
        Get post share statistics.

        Returns metrics including:
        - impressions (unique + total)
        - clicks
        - engagement
        - shares
        - comments
        - likes
        """
        await self.ensure_valid_token()

        # URL-encode the URN
        encoded_id = post_id.replace(":", "%3A")

        # Get share statistics
        response = await self.client.get(
            f"{self.API_BASE}/socialActions/{encoded_id}",
            headers=self._get_auth_headers(),
        )

        data = await self._handle_response(response, "analytics")

        metrics = {
            "post_id": post_id,
            "platform": "linkedin",
            "timestamp": datetime.utcnow().isoformat(),
            "likes": data.get("likesSummary", {}).get("totalLikes", 0),
            "comments": data.get("commentsSummary", {}).get("totalFirstLevelComments", 0),
        }

        # Get share statistics (organization posts only)
        if self.organization_id and "organization" in post_id:
            try:
                stats_response = await self.client.get(
                    f"{self.API_BASE}/organizationalEntityShareStatistics",
                    headers=self._get_auth_headers(),
                    params={
                        "q": "organizationalEntity",
                        "organizationalEntity": f"urn:li:organization:{self.organization_id}",
                        "shares[0]": post_id,
                    },
                )

                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    elements = stats_data.get("elements", [])
                    if elements:
                        stats = elements[0].get("totalShareStatistics", {})
                        metrics.update({
                            "impressions": stats.get("impressionCount", 0),
                            "unique_impressions": stats.get("uniqueImpressionsCount", 0),
                            "clicks": stats.get("clickCount", 0),
                            "shares": stats.get("shareCount", 0),
                            "engagement": stats.get("engagement", 0),
                        })
            except Exception as e:
                logger.warning(f"Failed to get share statistics: {e}")

        # Calculate engagement rate
        impressions = metrics.get("impressions", 0)
        engagements = metrics["likes"] + metrics["comments"] + metrics.get("shares", 0)
        if impressions > 0:
            metrics["engagement_rate"] = round((engagements / impressions) * 100, 2)
        else:
            metrics["engagement_rate"] = 0.0

        return metrics

    async def upload_media(
        self,
        media_bytes: bytes,
        media_type: str,
        alt_text: Optional[str] = None,
        as_organization: bool = False,
    ) -> str:
        """
        Upload image to LinkedIn.

        Args:
            media_bytes: Image bytes
            media_type: MIME type (image/jpeg, image/png, image/gif)
            alt_text: Alt text for accessibility
            as_organization: Upload for organization page

        Returns:
            Media URN
        """
        await self.ensure_valid_token()

        # Determine owner
        if as_organization and self.organization_id:
            owner = f"urn:li:organization:{self.organization_id}"
        else:
            person_id = await self.get_person_id()
            owner = f"urn:li:person:{person_id}"

        # Step 1: Register upload
        register_payload = {
            "registerUploadRequest": {
                "owner": owner,
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "serviceRelationships": [
                    {
                        "identifier": "urn:li:userGeneratedContent",
                        "relationshipType": "OWNER",
                    }
                ],
            }
        }

        register_response = await self.client.post(
            f"{self.API_BASE}/assets?action=registerUpload",
            headers={
                **self._get_auth_headers(),
                "Content-Type": "application/json",
            },
            json=register_payload,
        )

        register_data = await self._handle_response(register_response, "media")

        upload_mechanism = register_data.get("value", {}).get("uploadMechanism", {})
        upload_url = upload_mechanism.get(
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}
        ).get("uploadUrl")

        asset = register_data.get("value", {}).get("asset")

        if not upload_url or not asset:
            raise MediaUploadError(
                "Failed to get upload URL",
                platform=self.PLATFORM_NAME,
            )

        # Step 2: Upload image binary
        upload_response = await self.client.put(
            upload_url,
            headers={
                "Authorization": f"Bearer {self.tokens.access_token}",
                "Content-Type": media_type,
            },
            content=media_bytes,
        )

        if upload_response.status_code not in (200, 201):
            raise MediaUploadError(
                f"Upload failed: {upload_response.text}",
                platform=self.PLATFORM_NAME,
                status_code=upload_response.status_code,
            )

        logger.info(f"LinkedIn: Uploaded media {asset}")
        return asset

    async def get_comments(
        self,
        post_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get comments on a post."""
        await self.ensure_valid_token()

        encoded_id = post_id.replace(":", "%3A")

        response = await self.client.get(
            f"{self.API_BASE}/socialActions/{encoded_id}/comments",
            headers=self._get_auth_headers(),
            params={
                "count": min(limit, 100),
            },
        )

        result = await self._handle_response(response, "analytics")

        comments = []
        for element in result.get("elements", []):
            actor = element.get("actor", "")
            comments.append({
                "id": element.get("$URN", ""),
                "text": element.get("message", {}).get("text", ""),
                "author_id": actor,
                "author_name": "",  # Would need separate API call
                "created_at": element.get("created", {}).get("time"),
                "likes": element.get("likesSummary", {}).get("totalLikes", 0),
            })

        return comments

    async def reply_to_comment(
        self,
        comment_id: str,
        content: str,
        post_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Reply to a comment."""
        await self.ensure_valid_token()

        if not post_id:
            raise SocialAPIError(
                "Post ID required for replying",
                platform=self.PLATFORM_NAME,
            )

        person_id = await self.get_person_id()

        payload = {
            "actor": f"urn:li:person:{person_id}",
            "message": {
                "text": content,
            },
            "parentComment": comment_id,
        }

        encoded_post_id = post_id.replace(":", "%3A")

        response = await self.client.post(
            f"{self.API_BASE}/socialActions/{encoded_post_id}/comments",
            headers={
                **self._get_auth_headers(),
                "Content-Type": "application/json",
            },
            json=payload,
        )

        result = await self._handle_response(response, "shares")

        logger.info(f"LinkedIn: Replied to comment {comment_id}")
        return result

    async def get_organization_followers(self) -> Dict[str, Any]:
        """Get organization follower statistics."""
        if not self.organization_id:
            raise SocialAPIError(
                "Organization ID required",
                platform=self.PLATFORM_NAME,
            )

        await self.ensure_valid_token()

        response = await self.client.get(
            f"{self.API_BASE}/organizationalEntityFollowerStatistics",
            headers=self._get_auth_headers(),
            params={
                "q": "organizationalEntity",
                "organizationalEntity": f"urn:li:organization:{self.organization_id}",
            },
        )

        result = await self._handle_response(response, "analytics")

        elements = result.get("elements", [])
        if elements:
            stats = elements[0]
            return {
                "total_followers": stats.get("followerCounts", {}).get("organicFollowerCount", 0),
                "paid_followers": stats.get("followerCounts", {}).get("paidFollowerCount", 0),
            }

        return {"total_followers": 0, "paid_followers": 0}
