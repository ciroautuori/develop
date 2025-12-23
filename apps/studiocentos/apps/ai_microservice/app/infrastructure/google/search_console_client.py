"""
Google Search Console API Client.

Production-ready client for Google Search Console with:
- Search analytics queries
- URL inspection
- Sitemap management
- Keyword ranking data

API Reference: https://developers.google.com/webmaster-tools/search-console-api-original
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class SearchConsoleError(Exception):
    """Google Search Console API error."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class SearchConsoleClient:
    """
    Google Search Console API Client.

    Provides access to:
    - Search performance data (clicks, impressions, CTR, position)
    - Keyword rankings
    - Page-level analytics
    - URL inspection
    - Sitemap management

    Authentication:
    - Service Account JSON credentials
    - OAuth 2.0 access token

    Example:
        >>> client = SearchConsoleClient(
        ...     credentials_json=os.getenv("GOOGLE_SEARCH_CONSOLE_CREDENTIALS"),
        ...     site_url="https://studiocentos.it"
        ... )
        >>> data = await client.get_search_analytics(days=30)
    """

    API_BASE = "https://searchconsole.googleapis.com/webmasters/v3"
    SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

    def __init__(
        self,
        credentials_json: Optional[str] = None,
        access_token: Optional[str] = None,
        site_url: Optional[str] = None,
    ):
        """
        Initialize Search Console client.

        Args:
            credentials_json: Service account JSON string or path
            access_token: OAuth 2.0 access token
            site_url: Site URL (e.g., "https://studiocentos.it" or "sc-domain:studiocentos.it")
        """
        self.credentials_json = credentials_json or os.getenv("GOOGLE_SEARCH_CONSOLE_CREDENTIALS", "")
        self.access_token = access_token
        self.site_url = site_url or os.getenv("GOOGLE_SITE_URL", "")

        self._client: Optional[httpx.AsyncClient] = None
        self._token: Optional[str] = None
        self._token_expires: Optional[datetime] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get HTTP client."""
        if not self._client:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def _get_access_token(self) -> str:
        """Get valid access token, refreshing if needed."""
        if self.access_token:
            return self.access_token

        # Check if cached token is still valid
        if self._token and self._token_expires and datetime.utcnow() < self._token_expires:
            return self._token

        # Get token from service account
        if not self.credentials_json:
            raise SearchConsoleError("No credentials provided")

        try:
            # Parse credentials
            if os.path.isfile(self.credentials_json):
                with open(self.credentials_json) as f:
                    creds = json.load(f)
            else:
                creds = json.loads(self.credentials_json)

            # Create JWT for service account
            import jwt
            import time

            now = int(time.time())
            claims = {
                "iss": creds["client_email"],
                "scope": " ".join(self.SCOPES),
                "aud": "https://oauth2.googleapis.com/token",
                "iat": now,
                "exp": now + 3600,
            }

            signed_jwt = jwt.encode(
                claims,
                creds["private_key"],
                algorithm="RS256",
            )

            # Exchange JWT for access token
            response = await self.client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "assertion": signed_jwt,
                },
            )

            if response.status_code != 200:
                raise SearchConsoleError(
                    f"Token exchange failed: {response.text}",
                    status_code=response.status_code,
                )

            token_data = response.json()
            self._token = token_data["access_token"]
            self._token_expires = datetime.utcnow() + timedelta(
                seconds=token_data.get("expires_in", 3600) - 60
            )

            return self._token

        except json.JSONDecodeError:
            raise SearchConsoleError("Invalid credentials JSON")
        except ImportError:
            raise SearchConsoleError("PyJWT required for service account auth: pip install PyJWT")
        except Exception as e:
            raise SearchConsoleError(f"Failed to get access token: {str(e)}")

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make authenticated API request."""
        token = await self._get_access_token()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"

        url = f"{self.API_BASE}/{endpoint}"

        response = await self.client.request(
            method, url, headers=headers, **kwargs
        )

        if response.status_code == 401:
            # Token expired, clear and retry
            self._token = None
            self._token_expires = None
            token = await self._get_access_token()
            headers["Authorization"] = f"Bearer {token}"
            response = await self.client.request(
                method, url, headers=headers, **kwargs
            )

        if response.status_code >= 400:
            raise SearchConsoleError(
                f"API error: {response.text}",
                status_code=response.status_code,
            )

        return response.json() if response.content else {}

    async def get_search_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 28,
        dimensions: Optional[List[str]] = None,
        row_limit: int = 1000,
        data_state: str = "final",
    ) -> Dict[str, Any]:
        """
        Get search analytics data.

        Args:
            start_date: Start date (default: days ago)
            end_date: End date (default: today)
            days: Number of days if start_date not specified
            dimensions: Dimensions to group by (query, page, country, device, date)
            row_limit: Maximum rows to return
            data_state: 'all' or 'final'

        Returns:
            Search analytics data with clicks, impressions, CTR, position
        """
        if not self.site_url:
            raise SearchConsoleError("Site URL required")

        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=days)

        if not dimensions:
            dimensions = ["query", "page"]

        payload = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "dimensions": dimensions,
            "rowLimit": row_limit,
            "dataState": data_state,
        }

        # URL encode the site URL
        import urllib.parse
        encoded_site = urllib.parse.quote(self.site_url, safe="")

        result = await self._request(
            "POST",
            f"sites/{encoded_site}/searchAnalytics/query",
            json=payload,
        )

        return result

    async def get_keyword_rankings(
        self,
        days: int = 28,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get keyword ranking data.

        Returns list of keywords with:
        - query: Search query
        - clicks: Total clicks
        - impressions: Total impressions
        - ctr: Click-through rate
        - position: Average position
        """
        data = await self.get_search_analytics(
            days=days,
            dimensions=["query"],
            row_limit=limit,
        )

        keywords = []
        for row in data.get("rows", []):
            keywords.append({
                "query": row["keys"][0],
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": round(row.get("ctr", 0) * 100, 2),
                "position": round(row.get("position", 0), 1),
            })

        # Sort by clicks
        keywords.sort(key=lambda x: x["clicks"], reverse=True)

        return keywords

    async def get_page_performance(
        self,
        days: int = 28,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get page-level performance data.

        Returns list of pages with metrics.
        """
        data = await self.get_search_analytics(
            days=days,
            dimensions=["page"],
            row_limit=limit,
        )

        pages = []
        for row in data.get("rows", []):
            pages.append({
                "page": row["keys"][0],
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": round(row.get("ctr", 0) * 100, 2),
                "position": round(row.get("position", 0), 1),
            })

        pages.sort(key=lambda x: x["clicks"], reverse=True)

        return pages

    async def get_ranking_changes(
        self,
        days_current: int = 7,
        days_previous: int = 7,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Compare ranking changes between two periods.

        Returns keywords with position changes.
        """
        end_date = datetime.utcnow()
        mid_date = end_date - timedelta(days=days_current)
        start_date = mid_date - timedelta(days=days_previous)

        # Current period
        current_data = await self.get_search_analytics(
            start_date=mid_date,
            end_date=end_date,
            dimensions=["query"],
            row_limit=limit * 2,
        )

        # Previous period
        previous_data = await self.get_search_analytics(
            start_date=start_date,
            end_date=mid_date,
            dimensions=["query"],
            row_limit=limit * 2,
        )

        # Build previous period lookup
        previous_positions = {
            row["keys"][0]: row.get("position", 0)
            for row in previous_data.get("rows", [])
        }

        # Calculate changes
        changes = []
        for row in current_data.get("rows", []):
            query = row["keys"][0]
            current_pos = row.get("position", 0)
            previous_pos = previous_positions.get(query, 0)

            change = 0
            if previous_pos > 0:
                change = previous_pos - current_pos  # Positive = improved

            changes.append({
                "query": query,
                "current_position": round(current_pos, 1),
                "previous_position": round(previous_pos, 1),
                "change": round(change, 1),
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
            })

        # Sort by absolute change
        changes.sort(key=lambda x: abs(x["change"]), reverse=True)

        return changes[:limit]

    async def inspect_url(
        self,
        url: str,
    ) -> Dict[str, Any]:
        """
        Inspect a URL's index status.

        Note: Requires URL Inspection API access.
        """
        if not self.site_url:
            raise SearchConsoleError("Site URL required")

        # URL Inspection API is v1
        endpoint = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"

        token = await self._get_access_token()

        response = await self.client.post(
            endpoint,
            headers={"Authorization": f"Bearer {token}"},
            json={
                "inspectionUrl": url,
                "siteUrl": self.site_url,
            },
        )

        if response.status_code >= 400:
            raise SearchConsoleError(
                f"URL inspection failed: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    async def list_sitemaps(self) -> List[Dict[str, Any]]:
        """List submitted sitemaps."""
        if not self.site_url:
            raise SearchConsoleError("Site URL required")

        import urllib.parse
        encoded_site = urllib.parse.quote(self.site_url, safe="")

        result = await self._request(
            "GET",
            f"sites/{encoded_site}/sitemaps",
        )

        return result.get("sitemap", [])

    async def submit_sitemap(self, sitemap_url: str) -> bool:
        """Submit a sitemap."""
        if not self.site_url:
            raise SearchConsoleError("Site URL required")

        import urllib.parse
        encoded_site = urllib.parse.quote(self.site_url, safe="")
        encoded_sitemap = urllib.parse.quote(sitemap_url, safe="")

        await self._request(
            "PUT",
            f"sites/{encoded_site}/sitemaps/{encoded_sitemap}",
        )

        return True

    async def get_crawl_errors(self) -> Dict[str, Any]:
        """
        Get crawl error statistics.

        Note: This endpoint is deprecated in v3 API.
        Use URL Inspection API for individual URLs.
        """
        logger.warning("Crawl errors API is deprecated, use URL Inspection instead")
        return {}
