"""
Twitter/X API v2 Client.

Production-ready client for Twitter API v2 with:
- OAuth 2.0 User Context
- Tweet posting with media
- Engagement metrics
- Comment management
- Rate limit handling

API Reference: https://developer.twitter.com/en/docs/twitter-api
"""

import base64
import hashlib
import hmac
import logging
import os
import time
import urllib.parse
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


class TwitterClient(BaseSocialClient):
    """
    Twitter/X API v2 Client.

    Supports:
    - OAuth 2.0 with PKCE (User Context)
    - OAuth 1.0a (App Context for media upload)
    - Tweet creation with media attachments
    - Engagement metrics via Twitter API v2
    - Reply and mention handling

    Example:
        >>> tokens = OAuthTokens(access_token="...", refresh_token="...")
        >>> async with TwitterClient(tokens=tokens) as client:
        ...     result = await client.post("Hello Twitter!")
        ...     print(result["id"])
    """

    PLATFORM_NAME = "twitter"
    API_BASE = "https://api.twitter.com/2"
    UPLOAD_BASE = "https://upload.twitter.com/1.1"
    OAUTH2_TOKEN_URL = "https://api.twitter.com/2/oauth2/token"

    # Twitter rate limits (per 15 min window)
    DEFAULT_RATE_LIMITS = {
        "tweets": RateLimiter(max_requests=200, window_seconds=900),
        "users": RateLimiter(max_requests=300, window_seconds=900),
        "media": RateLimiter(max_requests=30, window_seconds=900),
    }

    def __init__(
        self,
        tokens: Optional[OAuthTokens] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
    ):
        """
        Initialize Twitter client.

        Args:
            tokens: OAuth 2.0 tokens for user context
            client_id: OAuth 2.0 client ID
            client_secret: OAuth 2.0 client secret
            api_key: OAuth 1.0a API key (for media upload)
            api_secret: OAuth 1.0a API secret
            access_token: OAuth 1.0a access token
            access_token_secret: OAuth 1.0a access token secret
        """
        super().__init__(tokens=tokens, rate_limits=self.DEFAULT_RATE_LIMITS.copy())

        # OAuth 2.0 credentials
        self.client_id = client_id or os.getenv("TWITTER_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("TWITTER_CLIENT_SECRET", "")

        # OAuth 1.0a credentials (for media upload)
        self.api_key = api_key or os.getenv("TWITTER_API_KEY", "")
        self.api_secret = api_secret or os.getenv("TWITTER_API_SECRET", "")
        self.oauth1_access_token = access_token or os.getenv("TWITTER_ACCESS_TOKEN", "")
        self.oauth1_access_secret = access_token_secret or os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

    def _parse_error_message(self, error_data: Dict[str, Any]) -> str:
        """Parse Twitter API error message."""
        if "errors" in error_data and error_data["errors"]:
            return error_data["errors"][0].get("message", "Unknown error")
        if "detail" in error_data:
            return error_data["detail"]
        if "error" in error_data:
            return error_data["error"]
        return "Unknown Twitter API error"

    def _parse_error_code(self, error_data: Dict[str, Any]) -> Optional[str]:
        """Parse Twitter API error code."""
        if "errors" in error_data and error_data["errors"]:
            return str(error_data["errors"][0].get("code", ""))
        return error_data.get("error_code")

    def _generate_oauth1_signature(
        self,
        method: str,
        url: str,
        params: Dict[str, str],
    ) -> str:
        """Generate OAuth 1.0a signature for media upload."""
        # Create signature base string
        sorted_params = sorted(params.items())
        param_string = "&".join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in sorted_params)

        base_string = "&".join([
            method.upper(),
            urllib.parse.quote(url, safe=""),
            urllib.parse.quote(param_string, safe=""),
        ])

        # Create signing key
        signing_key = "&".join([
            urllib.parse.quote(self.api_secret, safe=""),
            urllib.parse.quote(self.oauth1_access_secret, safe=""),
        ])

        # Generate signature
        signature = hmac.new(
            signing_key.encode(),
            base_string.encode(),
            hashlib.sha1,
        ).digest()

        return base64.b64encode(signature).decode()

    def _get_oauth1_header(self, method: str, url: str) -> str:
        """Generate OAuth 1.0a Authorization header for media upload."""
        oauth_params = {
            "oauth_consumer_key": self.api_key,
            "oauth_token": self.oauth1_access_token,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_nonce": base64.b64encode(os.urandom(32)).decode().replace("=", ""),
            "oauth_version": "1.0",
        }

        # Generate signature
        oauth_params["oauth_signature"] = self._generate_oauth1_signature(
            method, url, oauth_params
        )

        # Build header
        header_parts = [f'{k}="{urllib.parse.quote(str(v), safe="")}"' for k, v in sorted(oauth_params.items())]
        return "OAuth " + ", ".join(header_parts)

    async def refresh_access_token(self) -> OAuthTokens:
        """Refresh OAuth 2.0 access token."""
        if not self.tokens or not self.tokens.refresh_token:
            raise AuthenticationError(
                "No refresh token available",
                platform=self.PLATFORM_NAME,
            )

        # Prepare credentials
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        response = await self.client.post(
            self.OAUTH2_TOKEN_URL,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.tokens.refresh_token,
            },
        )

        if response.status_code != 200:
            raise AuthenticationError(
                f"Token refresh failed: {response.text}",
                platform=self.PLATFORM_NAME,
                status_code=response.status_code,
            )

        return OAuthTokens.from_response(response.json())

    async def post(
        self,
        content: str,
        media_ids: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        quote_tweet_id: Optional[str] = None,
        poll_options: Optional[List[str]] = None,
        poll_duration_minutes: int = 1440,
    ) -> Dict[str, Any]:
        """
        Create a tweet.

        Args:
            content: Tweet text (max 280 chars for free tier, 25000 for premium)
            media_ids: List of uploaded media IDs
            reply_to: Tweet ID to reply to
            quote_tweet_id: Tweet ID to quote
            poll_options: Poll options (2-4 options)
            poll_duration_minutes: Poll duration (5-10080 minutes)

        Returns:
            Tweet data including ID
        """
        await self.ensure_valid_token()

        payload: Dict[str, Any] = {"text": content}

        if media_ids:
            payload["media"] = {"media_ids": media_ids}

        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}

        if quote_tweet_id:
            payload["quote_tweet_id"] = quote_tweet_id

        if poll_options and len(poll_options) >= 2:
            payload["poll"] = {
                "options": [{"label": opt} for opt in poll_options[:4]],
                "duration_minutes": poll_duration_minutes,
            }

        result = await self._request(
            "POST",
            f"{self.API_BASE}/tweets",
            endpoint="tweets",
            json=payload,
        )

        logger.info(f"Twitter: Posted tweet {result.get('data', {}).get('id')}")
        return result.get("data", result)

    async def delete_post(self, post_id: str) -> bool:
        """Delete a tweet."""
        await self.ensure_valid_token()

        result = await self._request(
            "DELETE",
            f"{self.API_BASE}/tweets/{post_id}",
            endpoint="tweets",
        )

        return result.get("data", {}).get("deleted", False)

    async def get_metrics(self, post_id: str) -> Dict[str, Any]:
        """
        Get tweet metrics.

        Returns engagement metrics including:
        - impressions
        - likes
        - retweets
        - replies
        - quote_tweets
        - url_clicks
        - profile_clicks
        """
        await self.ensure_valid_token()

        result = await self._request(
            "GET",
            f"{self.API_BASE}/tweets/{post_id}",
            endpoint="tweets",
            params={
                "tweet.fields": "public_metrics,non_public_metrics,organic_metrics",
            },
        )

        data = result.get("data", {})
        metrics = {
            "post_id": post_id,
            "platform": "twitter",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Public metrics (always available)
        public = data.get("public_metrics", {})
        metrics.update({
            "likes": public.get("like_count", 0),
            "retweets": public.get("retweet_count", 0),
            "replies": public.get("reply_count", 0),
            "quotes": public.get("quote_count", 0),
            "bookmarks": public.get("bookmark_count", 0),
        })

        # Non-public metrics (requires user context)
        non_public = data.get("non_public_metrics", {})
        metrics.update({
            "impressions": non_public.get("impression_count", 0),
            "url_clicks": non_public.get("url_link_clicks", 0),
            "profile_clicks": non_public.get("user_profile_clicks", 0),
        })

        # Organic metrics
        organic = data.get("organic_metrics", {})
        metrics.update({
            "organic_impressions": organic.get("impression_count", 0),
            "organic_likes": organic.get("like_count", 0),
            "organic_retweets": organic.get("retweet_count", 0),
        })

        # Calculate engagement rate
        impressions = metrics.get("impressions", 0) or metrics.get("organic_impressions", 0)
        engagements = metrics["likes"] + metrics["retweets"] + metrics["replies"]
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
        media_category: str = "tweet_image",
    ) -> str:
        """
        Upload media using Twitter's chunked upload.

        Args:
            media_bytes: Media file bytes
            media_type: MIME type (image/jpeg, image/png, video/mp4, image/gif)
            alt_text: Accessibility text
            media_category: tweet_image, tweet_gif, tweet_video

        Returns:
            Media ID string
        """
        upload_url = f"{self.UPLOAD_BASE}/media/upload.json"
        total_bytes = len(media_bytes)

        # INIT
        init_params = {
            "command": "INIT",
            "total_bytes": total_bytes,
            "media_type": media_type,
            "media_category": media_category,
        }

        response = await self.client.post(
            upload_url,
            headers={"Authorization": self._get_oauth1_header("POST", upload_url)},
            data=init_params,
        )

        if response.status_code != 202 and response.status_code != 200:
            raise MediaUploadError(
                f"Media init failed: {response.text}",
                platform=self.PLATFORM_NAME,
                status_code=response.status_code,
            )

        media_id = response.json()["media_id_string"]

        # APPEND (chunk upload)
        chunk_size = 5 * 1024 * 1024  # 5MB chunks
        for segment, i in enumerate(range(0, total_bytes, chunk_size)):
            chunk = media_bytes[i:i + chunk_size]

            append_data = {
                "command": "APPEND",
                "media_id": media_id,
                "segment_index": segment,
            }

            response = await self.client.post(
                upload_url,
                headers={"Authorization": self._get_oauth1_header("POST", upload_url)},
                data=append_data,
                files={"media": chunk},
            )

            if response.status_code not in (200, 204):
                raise MediaUploadError(
                    f"Media append failed: {response.text}",
                    platform=self.PLATFORM_NAME,
                    status_code=response.status_code,
                )

        # FINALIZE
        finalize_params = {
            "command": "FINALIZE",
            "media_id": media_id,
        }

        response = await self.client.post(
            upload_url,
            headers={"Authorization": self._get_oauth1_header("POST", upload_url)},
            data=finalize_params,
        )

        if response.status_code not in (200, 201):
            raise MediaUploadError(
                f"Media finalize failed: {response.text}",
                platform=self.PLATFORM_NAME,
                status_code=response.status_code,
            )

        result = response.json()

        # Check for async processing (video)
        if "processing_info" in result:
            media_id = await self._wait_for_processing(media_id)

        # Add alt text if provided
        if alt_text:
            await self._set_alt_text(media_id, alt_text)

        logger.info(f"Twitter: Uploaded media {media_id}")
        return media_id

    async def _wait_for_processing(self, media_id: str, max_wait: int = 120) -> str:
        """Wait for async media processing."""
        import asyncio

        check_url = f"{self.UPLOAD_BASE}/media/upload.json"
        start_time = time.time()

        while time.time() - start_time < max_wait:
            response = await self.client.get(
                check_url,
                headers={"Authorization": self._get_oauth1_header("GET", check_url)},
                params={"command": "STATUS", "media_id": media_id},
            )

            if response.status_code != 200:
                raise MediaUploadError(
                    f"Media status check failed: {response.text}",
                    platform=self.PLATFORM_NAME,
                )

            result = response.json()
            state = result.get("processing_info", {}).get("state")

            if state == "succeeded":
                return media_id
            elif state == "failed":
                error = result.get("processing_info", {}).get("error", {})
                raise MediaUploadError(
                    f"Media processing failed: {error.get('message', 'Unknown error')}",
                    platform=self.PLATFORM_NAME,
                )

            check_after = result.get("processing_info", {}).get("check_after_secs", 5)
            await asyncio.sleep(check_after)

        raise MediaUploadError(
            "Media processing timeout",
            platform=self.PLATFORM_NAME,
        )

    async def _set_alt_text(self, media_id: str, alt_text: str) -> None:
        """Set alt text for uploaded media."""
        url = f"{self.UPLOAD_BASE}/media/metadata/create.json"

        await self.client.post(
            url,
            headers={
                "Authorization": self._get_oauth1_header("POST", url),
                "Content-Type": "application/json",
            },
            json={
                "media_id": media_id,
                "alt_text": {"text": alt_text[:1000]},
            },
        )

    async def get_comments(
        self,
        post_id: str,
        limit: int = 100,
        pagination_token: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get replies to a tweet.

        Uses search API to find replies.
        """
        await self.ensure_valid_token()

        params = {
            "query": f"conversation_id:{post_id}",
            "tweet.fields": "author_id,created_at,public_metrics,text",
            "user.fields": "name,username,profile_image_url",
            "expansions": "author_id",
            "max_results": min(limit, 100),
        }

        if pagination_token:
            params["pagination_token"] = pagination_token

        result = await self._request(
            "GET",
            f"{self.API_BASE}/tweets/search/recent",
            endpoint="tweets",
            params=params,
        )

        tweets = result.get("data", [])
        users = {u["id"]: u for u in result.get("includes", {}).get("users", [])}

        comments = []
        for tweet in tweets:
            author = users.get(tweet["author_id"], {})
            comments.append({
                "id": tweet["id"],
                "text": tweet["text"],
                "author_id": tweet["author_id"],
                "author_name": author.get("name", ""),
                "author_username": author.get("username", ""),
                "created_at": tweet.get("created_at"),
                "likes": tweet.get("public_metrics", {}).get("like_count", 0),
            })

        return comments

    async def reply_to_comment(
        self,
        comment_id: str,
        content: str,
    ) -> Dict[str, Any]:
        """Reply to a tweet/comment."""
        return await self.post(content, reply_to=comment_id)

    async def get_user_timeline(
        self,
        user_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get user's recent tweets."""
        await self.ensure_valid_token()

        if not user_id:
            # Get authenticated user's ID
            me_result = await self._request(
                "GET",
                f"{self.API_BASE}/users/me",
                endpoint="users",
            )
            user_id = me_result.get("data", {}).get("id")

        result = await self._request(
            "GET",
            f"{self.API_BASE}/users/{user_id}/tweets",
            endpoint="tweets",
            params={
                "tweet.fields": "created_at,public_metrics",
                "max_results": min(limit, 100),
            },
        )

        return result.get("data", [])

    async def get_mentions(
        self,
        user_id: Optional[str] = None,
        since_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get mentions of the user."""
        await self.ensure_valid_token()

        if not user_id:
            me_result = await self._request(
                "GET",
                f"{self.API_BASE}/users/me",
                endpoint="users",
            )
            user_id = me_result.get("data", {}).get("id")

        params = {
            "tweet.fields": "author_id,created_at,public_metrics,text",
            "user.fields": "name,username",
            "expansions": "author_id",
            "max_results": min(limit, 100),
        }

        if since_id:
            params["since_id"] = since_id

        result = await self._request(
            "GET",
            f"{self.API_BASE}/users/{user_id}/mentions",
            endpoint="tweets",
            params=params,
        )

        return result.get("data", [])
