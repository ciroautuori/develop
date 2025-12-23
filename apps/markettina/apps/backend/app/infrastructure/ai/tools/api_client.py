"""HTTP client for external API integrations.

Provides standardized HTTP client with retry logic, rate limiting,
and error handling for integrating with external services.
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, Field


class HTTPMethod(str, Enum):
    """HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class APIResponse(BaseModel):
    """Response from API call.
    
    Attributes:
        status_code: HTTP status code
        data: Response data
        headers: Response headers
        elapsed: Request duration in seconds
        error: Error message if request failed
    """

    status_code: int
    data: Any = None
    headers: dict[str, str] = Field(default_factory=dict)
    elapsed: float = 0.0
    error: str | None = None

    @property
    def is_success(self) -> bool:
        """Check if request was successful (2xx status code)."""
        return 200 <= self.status_code < 300

    @property
    def is_error(self) -> bool:
        """Check if request had an error."""
        return self.error is not None or not self.is_success


class RateLimiter:
    """Simple token bucket rate limiter.
    
    Attributes:
        max_requests: Maximum requests per period
        period: Time period in seconds
    """

    def __init__(self, max_requests: int, period: float = 60.0) -> None:
        """Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per period
            period: Time period in seconds
        """
        self.max_requests = max_requests
        self.period = period
        self._tokens = max_requests
        self._last_update = datetime.utcnow()

    async def acquire(self) -> None:
        """Acquire token for request (blocks if rate limit exceeded)."""
        # Refill tokens based on time passed
        now = datetime.utcnow()
        elapsed = (now - self._last_update).total_seconds()

        # Add tokens proportional to time passed
        tokens_to_add = (elapsed / self.period) * self.max_requests
        self._tokens = min(self.max_requests, self._tokens + tokens_to_add)
        self._last_update = now

        # Wait if no tokens available
        while self._tokens < 1:
            await asyncio.sleep(0.1)

            # Refill again
            now = datetime.utcnow()
            elapsed = (now - self._last_update).total_seconds()
            tokens_to_add = (elapsed / self.period) * self.max_requests
            self._tokens = min(self.max_requests, self._tokens + tokens_to_add)
            self._last_update = now

        # Consume one token
        self._tokens -= 1


class ExternalAPIClient:
    """HTTP client for external API integrations.
    
    Provides retry logic, rate limiting, and standardized error handling.
    
    Attributes:
        base_url: Base URL for API
        headers: Default headers for requests
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        rate_limiter: Optional rate limiter
    """

    def __init__(
        self,
        base_url: str,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        rate_limit: int | None = None,
        rate_limit_period: float = 60.0
    ) -> None:
        """Initialize API client.
        
        Args:
            base_url: Base URL for API
            headers: Default headers
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            rate_limit: Maximum requests per period (None = no limit)
            rate_limit_period: Rate limit period in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self.max_retries = max_retries

        # Rate limiter
        self.rate_limiter = (
            RateLimiter(rate_limit, rate_limit_period)
            if rate_limit
            else None
        )

        # HTTP client
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "ExternalAPIClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    async def request(
        self,
        method: HTTPMethod,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        retry_count: int = 0
    ) -> APIResponse:
        """Make HTTP request to API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (relative to base_url)
            params: Query parameters
            data: Form data
            json: JSON data
            headers: Additional headers
            retry_count: Current retry attempt (internal)
            
        Returns:
            API response
        """
        # Apply rate limiting
        if self.rate_limiter:
            await self.rate_limiter.acquire()

        # Ensure client is initialized
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self.timeout
            )

        # Merge headers
        request_headers = {**self.headers, **(headers or {})}

        # Build URL
        url = endpoint if endpoint.startswith("http") else urljoin(self.base_url + "/", endpoint.lstrip("/"))

        try:
            start_time = datetime.utcnow()

            # Make request
            response = await self._client.request(
                method=method.value,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=request_headers
            )

            elapsed = (datetime.utcnow() - start_time).total_seconds()

            # Parse response
            try:
                response_data = response.json()
            except Exception:
                response_data = response.text

            return APIResponse(
                status_code=response.status_code,
                data=response_data,
                headers=dict(response.headers),
                elapsed=elapsed
            )

        except httpx.HTTPError as e:
            # Retry logic
            if retry_count < self.max_retries:
                # Exponential backoff
                wait_time = 2 ** retry_count
                await asyncio.sleep(wait_time)

                return await self.request(
                    method=method,
                    endpoint=endpoint,
                    params=params,
                    data=data,
                    json=json,
                    headers=headers,
                    retry_count=retry_count + 1
                )

            # Max retries exceeded
            return APIResponse(
                status_code=500,
                error=f"{type(e).__name__}: {e!s}"
            )

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any
    ) -> APIResponse:
        """Make GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            **kwargs: Additional request arguments
            
        Returns:
            API response
        """
        return await self.request(
            HTTPMethod.GET,
            endpoint,
            params=params,
            **kwargs
        )

    async def post(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        **kwargs: Any
    ) -> APIResponse:
        """Make POST request.
        
        Args:
            endpoint: API endpoint
            json: JSON data
            data: Form data
            **kwargs: Additional request arguments
            
        Returns:
            API response
        """
        return await self.request(
            HTTPMethod.POST,
            endpoint,
            json=json,
            data=data,
            **kwargs
        )

    async def put(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        **kwargs: Any
    ) -> APIResponse:
        """Make PUT request.
        
        Args:
            endpoint: API endpoint
            json: JSON data
            **kwargs: Additional request arguments
            
        Returns:
            API response
        """
        return await self.request(
            HTTPMethod.PUT,
            endpoint,
            json=json,
            **kwargs
        )

    async def delete(
        self,
        endpoint: str,
        **kwargs: Any
    ) -> APIResponse:
        """Make DELETE request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional request arguments
            
        Returns:
            API response
        """
        return await self.request(
            HTTPMethod.DELETE,
            endpoint,
            **kwargs
        )

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
