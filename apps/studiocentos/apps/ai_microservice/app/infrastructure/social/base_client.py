"""
Base Social Media Client.

Abstract base class for all social media API clients with common functionality:
- Rate limiting
- Error handling
- Token refresh
- Retry logic
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum

import httpx

logger = logging.getLogger(__name__)


class SocialAPIError(Exception):
    """Base exception for social media API errors."""

    def __init__(
        self,
        message: str,
        platform: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        retry_after: Optional[int] = None,
    ):
        super().__init__(message)
        self.platform = platform
        self.status_code = status_code
        self.error_code = error_code
        self.retry_after = retry_after


class RateLimitError(SocialAPIError):
    """Rate limit exceeded error."""
    pass


class AuthenticationError(SocialAPIError):
    """Authentication/authorization error."""
    pass


class MediaUploadError(SocialAPIError):
    """Media upload error."""
    pass


class PostingError(SocialAPIError):
    """Error posting content."""
    pass


@dataclass
class RateLimiter:
    """Token bucket rate limiter for API calls."""

    max_requests: int
    window_seconds: int
    requests: List[float] = field(default_factory=list)

    def can_proceed(self) -> bool:
        """Check if request can proceed."""
        now = time.time()
        # Remove old requests outside window
        self.requests = [t for t in self.requests if now - t < self.window_seconds]
        return len(self.requests) < self.max_requests

    def record_request(self) -> None:
        """Record a request."""
        self.requests.append(time.time())

    def wait_time(self) -> float:
        """Get seconds to wait before next request."""
        if self.can_proceed():
            return 0.0
        oldest = min(self.requests)
        return max(0.0, self.window_seconds - (time.time() - oldest))


@dataclass
class OAuthTokens:
    """OAuth tokens with expiry management."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None
    scope: Optional[str] = None

    def is_expired(self, buffer_seconds: int = 300) -> bool:
        """Check if token is expired or will expire soon."""
        if not self.expires_at:
            return False
        return datetime.utcnow() >= self.expires_at - timedelta(seconds=buffer_seconds)

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "OAuthTokens":
        """Create from API response."""
        expires_in = data.get("expires_in")
        expires_at = None
        if expires_in:
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        return cls(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            token_type=data.get("token_type", "Bearer"),
            expires_at=expires_at,
            scope=data.get("scope"),
        )


class BaseSocialClient(ABC):
    """
    Abstract base class for social media API clients.

    Provides:
    - HTTP client management with retries
    - Rate limiting per endpoint
    - Token refresh handling
    - Standardized error handling
    """

    PLATFORM_NAME: str = "base"
    DEFAULT_TIMEOUT: float = 30.0
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0

    def __init__(
        self,
        tokens: Optional[OAuthTokens] = None,
        rate_limits: Optional[Dict[str, RateLimiter]] = None,
    ):
        self.tokens = tokens
        self.rate_limiters = rate_limits or {}
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get HTTP client, creating if needed."""
        if not self._client:
            self._client = httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT)
        return self._client

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        if not self.tokens:
            return {}
        return {
            "Authorization": f"{self.tokens.token_type} {self.tokens.access_token}"
        }

    async def _check_rate_limit(self, endpoint: str) -> None:
        """Check and wait for rate limit if needed."""
        limiter = self.rate_limiters.get(endpoint)
        if not limiter:
            return

        wait_time = limiter.wait_time()
        if wait_time > 0:
            logger.warning(
                f"{self.PLATFORM_NAME}: Rate limited on {endpoint}, waiting {wait_time:.1f}s"
            )
            await asyncio.sleep(wait_time)

        limiter.record_request()

    async def _handle_response(
        self,
        response: httpx.Response,
        endpoint: str,
    ) -> Dict[str, Any]:
        """Handle API response with error parsing."""
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(
                f"Rate limit exceeded on {endpoint}",
                platform=self.PLATFORM_NAME,
                status_code=429,
                retry_after=retry_after,
            )

        if response.status_code == 401:
            raise AuthenticationError(
                "Authentication failed - token may be expired",
                platform=self.PLATFORM_NAME,
                status_code=401,
            )

        if response.status_code == 403:
            raise AuthenticationError(
                "Access forbidden - insufficient permissions",
                platform=self.PLATFORM_NAME,
                status_code=403,
            )

        if response.status_code >= 400:
            error_data = response.json() if response.content else {}
            error_message = self._parse_error_message(error_data)
            raise SocialAPIError(
                error_message,
                platform=self.PLATFORM_NAME,
                status_code=response.status_code,
                error_code=self._parse_error_code(error_data),
            )

        if response.status_code == 204:
            return {"success": True}

        return response.json()

    async def _request(
        self,
        method: str,
        url: str,
        endpoint: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make API request with retries and rate limiting."""
        await self._check_rate_limit(endpoint)

        # Add auth headers
        headers = kwargs.pop("headers", {})
        headers.update(self._get_auth_headers())

        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.client.request(
                    method, url, headers=headers, **kwargs
                )
                return await self._handle_response(response, endpoint)

            except RateLimitError as e:
                if e.retry_after and attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(min(e.retry_after, 60))
                    continue
                raise

            except httpx.RequestError as e:
                last_error = SocialAPIError(
                    f"Request failed: {str(e)}",
                    platform=self.PLATFORM_NAME,
                )
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue

        raise last_error or SocialAPIError(
            "Max retries exceeded",
            platform=self.PLATFORM_NAME,
        )

    @abstractmethod
    def _parse_error_message(self, error_data: Dict[str, Any]) -> str:
        """Parse platform-specific error message."""
        pass

    @abstractmethod
    def _parse_error_code(self, error_data: Dict[str, Any]) -> Optional[str]:
        """Parse platform-specific error code."""
        pass

    @abstractmethod
    async def refresh_access_token(self) -> OAuthTokens:
        """Refresh access token using refresh token."""
        pass

    @abstractmethod
    async def post(
        self,
        content: str,
        media_ids: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a post."""
        pass

    @abstractmethod
    async def delete_post(self, post_id: str) -> bool:
        """Delete a post."""
        pass

    @abstractmethod
    async def get_metrics(self, post_id: str) -> Dict[str, Any]:
        """Get post metrics/analytics."""
        pass

    @abstractmethod
    async def upload_media(
        self,
        media_bytes: bytes,
        media_type: str,
        alt_text: Optional[str] = None,
    ) -> str:
        """Upload media and return media ID."""
        pass

    @abstractmethod
    async def get_comments(
        self,
        post_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get comments on a post."""
        pass

    @abstractmethod
    async def reply_to_comment(
        self,
        comment_id: str,
        content: str,
    ) -> Dict[str, Any]:
        """Reply to a comment."""
        pass

    async def ensure_valid_token(self) -> None:
        """Ensure access token is valid, refreshing if needed."""
        if self.tokens and self.tokens.is_expired():
            if self.tokens.refresh_token:
                self.tokens = await self.refresh_access_token()
            else:
                raise AuthenticationError(
                    "Access token expired and no refresh token available",
                    platform=self.PLATFORM_NAME,
                )
