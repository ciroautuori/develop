"""
Base Social Media Client - Abstract foundation for all social platform clients.

Features:
- Rate limiting with configurable windows
- Automatic retry with exponential backoff
- Token refresh management
- Comprehensive error handling
- Request/response logging
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class SocialPlatform(str, Enum):
    """Supported social media platforms."""

    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    THREADS = "threads"
    TIKTOK = "tiktok"


class SocialAPIError(Exception):
    """Base exception for social API errors."""

    def __init__(
        self,
        message: str,
        platform: SocialPlatform,
        status_code: int | None = None,
        response_data: dict | None = None,
    ):
        self.message = message
        self.platform = platform
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(f"[{platform.value}] {message}")


class RateLimitError(SocialAPIError):
    """Rate limit exceeded error."""

    def __init__(
        self,
        platform: SocialPlatform,
        retry_after: float = 60.0,
        message: str = "Rate limit exceeded",
    ):
        self.retry_after = retry_after
        super().__init__(message, platform, status_code=429)


class AuthenticationError(SocialAPIError):
    """Authentication/authorization error."""

    def __init__(self, platform: SocialPlatform, message: str = "Authentication failed"):
        super().__init__(message, platform, status_code=401)


class TokenExpiredError(AuthenticationError):
    """Token expired and needs refresh."""

    def __init__(self, platform: SocialPlatform):
        super().__init__(platform, "Token expired - refresh required")


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""

    requests_per_window: int
    window_seconds: int
    burst_limit: int | None = None
    retry_after_seconds: float = 60.0


@dataclass
class RateLimitState:
    """Rate limit tracking state."""

    requests_made: int = 0
    window_start: datetime = field(default_factory=datetime.utcnow)
    last_request: datetime | None = None

    def reset_if_expired(self, window_seconds: int) -> None:
        """Reset counter if window expired."""
        now = datetime.utcnow()
        if (now - self.window_start).total_seconds() >= window_seconds:
            self.requests_made = 0
            self.window_start = now


@dataclass
class SocialMediaPost:
    """Standardized post data across platforms."""

    post_id: str
    platform: SocialPlatform
    content: str
    media_urls: list[str] = field(default_factory=list)
    permalink: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class PostMetrics:
    """Standardized engagement metrics."""

    post_id: str
    platform: SocialPlatform
    impressions: int = 0
    reach: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    clicks: int = 0
    engagement_rate: float = 0.0
    fetched_at: datetime = field(default_factory=datetime.utcnow)


class BaseSocialClient(ABC):
    """
    Abstract base class for social media API clients.

    Provides:
    - Rate limiting with automatic retry
    - Token refresh management
    - Error handling and logging
    - Request/response interceptors

    Subclasses must implement:
    - _get_platform(): Return platform enum
    - _get_base_url(): Return API base URL
    - _get_auth_headers(): Return authorization headers
    - publish_post(): Publish content to platform
    - get_post_metrics(): Get engagement metrics
    """

    def __init__(
        self,
        rate_limit_config: RateLimitConfig | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        self._rate_limit_config = rate_limit_config or RateLimitConfig(
            requests_per_window=100,
            window_seconds=900,  # 15 minutes
        )
        self._rate_limit_state = RateLimitState()
        self._timeout = timeout
        self._max_retries = max_retries
        self._client: httpx.AsyncClient | None = None

    @property
    def platform(self) -> SocialPlatform:
        """Get the platform this client handles."""
        return self._get_platform()

    @abstractmethod
    def _get_platform(self) -> SocialPlatform:
        """Return the platform enum for this client."""
        pass

    @abstractmethod
    def _get_base_url(self) -> str:
        """Return the API base URL."""
        pass

    @abstractmethod
    def _get_auth_headers(self) -> dict[str, str]:
        """Return authorization headers for requests."""
        pass

    @abstractmethod
    async def publish_post(
        self,
        content: str,
        media_urls: list[str] | None = None,
        **kwargs: Any,
    ) -> SocialMediaPost:
        """
        Publish a post to the platform.

        Args:
            content: Post text content
            media_urls: Optional list of media URLs
            **kwargs: Platform-specific options

        Returns:
            SocialMediaPost with the created post data
        """
        pass

    @abstractmethod
    async def get_post_metrics(self, post_id: str) -> PostMetrics:
        """
        Get engagement metrics for a post.

        Args:
            post_id: Platform post ID

        Returns:
            PostMetrics with engagement data
        """
        pass

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._get_base_url(),
                timeout=self._timeout,
                headers={"User-Agent": "MARKETTINA/2.1.0"},
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting."""
        config = self._rate_limit_config
        state = self._rate_limit_state

        state.reset_if_expired(config.window_seconds)

        if state.requests_made >= config.requests_per_window:
            wait_time = config.window_seconds - (
                datetime.utcnow() - state.window_start
            ).total_seconds()
            if wait_time > 0:
                logger.warning(
                    f"[{self.platform.value}] Rate limit reached, waiting {wait_time:.1f}s"
                )
                await asyncio.sleep(wait_time)
                state.reset_if_expired(config.window_seconds)

    def _update_rate_limit(self) -> None:
        """Update rate limit counter after request."""
        self._rate_limit_state.requests_made += 1
        self._rate_limit_state.last_request = datetime.utcnow()

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
        """
        Make authenticated API request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json: JSON body data
            data: Form data
            params: Query parameters
            extra_headers: Additional headers

        Returns:
            Response JSON data

        Raises:
            SocialAPIError: On API errors
            RateLimitError: On rate limit exceeded
        """
        await self._check_rate_limit()

        client = await self.get_client()
        headers = {**self._get_auth_headers(), **(extra_headers or {})}

        last_error: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                response = await client.request(
                    method,
                    endpoint,
                    headers=headers,
                    json=json,
                    data=data,
                    params=params,
                )

                self._update_rate_limit()

                if response.status_code == 429:
                    retry_after = float(response.headers.get("Retry-After", 60))
                    raise RateLimitError(self.platform, retry_after=retry_after)

                if response.status_code == 401:
                    raise AuthenticationError(self.platform)

                if response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    raise SocialAPIError(
                        message=error_data.get("error", {}).get("message", "API Error"),
                        platform=self.platform,
                        status_code=response.status_code,
                        response_data=error_data,
                    )

                return response.json() if response.content else {}

            except RateLimitError as e:
                logger.warning(
                    f"[{self.platform.value}] Rate limited, waiting {e.retry_after}s"
                )
                await asyncio.sleep(e.retry_after)
                last_error = e

            except httpx.TimeoutException as e:
                logger.warning(
                    f"[{self.platform.value}] Timeout on attempt {attempt + 1}/{self._max_retries}"
                )
                last_error = SocialAPIError(
                    f"Request timeout: {e}", self.platform, status_code=408
                )
                await asyncio.sleep(2 ** attempt)

            except httpx.RequestError as e:
                logger.error(f"[{self.platform.value}] Request error: {e}")
                last_error = SocialAPIError(
                    f"Request failed: {e}", self.platform
                )
                await asyncio.sleep(2 ** attempt)

        if last_error:
            raise last_error
        raise SocialAPIError("Max retries exceeded", self.platform)

    async def _get(
        self, endpoint: str, params: dict | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Convenience method for GET requests."""
        return await self._request("GET", endpoint, params=params, **kwargs)

    async def _post(
        self,
        endpoint: str,
        json: dict | None = None,
        data: dict | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Convenience method for POST requests."""
        return await self._request("POST", endpoint, json=json, data=data, **kwargs)

    async def _delete(
        self, endpoint: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Convenience method for DELETE requests."""
        return await self._request("DELETE", endpoint, **kwargs)

    def is_configured(self) -> bool:
        """Check if client has required configuration."""
        try:
            headers = self._get_auth_headers()
            return bool(headers.get("Authorization"))
        except Exception:
            return False

    async def health_check(self) -> dict[str, Any]:
        """
        Perform health check on API connection.

        Returns:
            Dict with status and configuration info
        """
        return {
            "platform": self.platform.value,
            "configured": self.is_configured(),
            "rate_limit": {
                "requests_made": self._rate_limit_state.requests_made,
                "limit": self._rate_limit_config.requests_per_window,
                "window_seconds": self._rate_limit_config.window_seconds,
            },
        }
