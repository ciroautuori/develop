"""
Google Analytics 4 Data API Client.

Production-ready client for GA4 with:
- Real-time reports
- Standard reports
- Custom metrics and dimensions
- Audience data

API Reference: https://developers.google.com/analytics/devguides/reporting/data/v1
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class GA4Error(Exception):
    """Google Analytics 4 API error."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class GA4Client:
    """
    Google Analytics 4 Data API Client.

    Provides access to:
    - Real-time user data
    - Session and pageview metrics
    - Conversion tracking
    - Custom reports
    - Audience analytics

    Authentication:
    - Service Account JSON credentials
    - OAuth 2.0 access token

    Example:
        >>> client = GA4Client(
        ...     credentials_json=os.getenv("GA4_CREDENTIALS"),
        ...     property_id="123456789"
        ... )
        >>> data = await client.run_report(dimensions=["pagePath"], metrics=["sessions"])
    """

    API_BASE = "https://analyticsdata.googleapis.com/v1beta"
    SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]

    def __init__(
        self,
        credentials_json: Optional[str] = None,
        access_token: Optional[str] = None,
        property_id: Optional[str] = None,
    ):
        """
        Initialize GA4 client.

        Args:
            credentials_json: Service account JSON string or path
            access_token: OAuth 2.0 access token
            property_id: GA4 Property ID (numeric, without "properties/" prefix)
        """
        self.credentials_json = credentials_json or os.getenv("GA4_CREDENTIALS", "")
        self.access_token = access_token
        self.property_id = property_id or os.getenv("GA4_PROPERTY_ID", "")

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

    @property
    def property_path(self) -> str:
        """Get full property path."""
        return f"properties/{self.property_id}"

    async def _get_access_token(self) -> str:
        """Get valid access token, refreshing if needed."""
        if self.access_token:
            return self.access_token

        if self._token and self._token_expires and datetime.utcnow() < self._token_expires:
            return self._token

        if not self.credentials_json:
            raise GA4Error("No credentials provided")

        try:
            if os.path.isfile(self.credentials_json):
                with open(self.credentials_json) as f:
                    creds = json.load(f)
            else:
                creds = json.loads(self.credentials_json)

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

            response = await self.client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "assertion": signed_jwt,
                },
            )

            if response.status_code != 200:
                raise GA4Error(
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
            raise GA4Error("Invalid credentials JSON")
        except ImportError:
            raise GA4Error("PyJWT required: pip install PyJWT")
        except Exception as e:
            raise GA4Error(f"Failed to get access token: {str(e)}")

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
            self._token = None
            self._token_expires = None
            token = await self._get_access_token()
            headers["Authorization"] = f"Bearer {token}"
            response = await self.client.request(
                method, url, headers=headers, **kwargs
            )

        if response.status_code >= 400:
            raise GA4Error(
                f"API error: {response.text}",
                status_code=response.status_code,
            )

        return response.json() if response.content else {}

    async def run_report(
        self,
        dimensions: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: int = 28,
        limit: int = 1000,
        dimension_filter: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Run a GA4 report.

        Args:
            dimensions: Dimension names (e.g., ["pagePath", "country"])
            metrics: Metric names (e.g., ["sessions", "activeUsers"])
            start_date: Start date (YYYY-MM-DD or "7daysAgo", "yesterday", etc.)
            end_date: End date (YYYY-MM-DD or "today", "yesterday")
            days: Days ago for start_date if not specified
            limit: Maximum rows
            dimension_filter: Filter expression
            order_by: Order specifications

        Returns:
            Report data with rows and metadata
        """
        if not self.property_id:
            raise GA4Error("Property ID required")

        if not dimensions:
            dimensions = ["pagePath"]
        if not metrics:
            metrics = ["sessions", "activeUsers"]

        if not start_date:
            start_date = f"{days}daysAgo"
        if not end_date:
            end_date = "today"

        payload: Dict[str, Any] = {
            "dateRanges": [
                {
                    "startDate": start_date,
                    "endDate": end_date,
                }
            ],
            "dimensions": [{"name": d} for d in dimensions],
            "metrics": [{"name": m} for m in metrics],
            "limit": limit,
        }

        if dimension_filter:
            payload["dimensionFilter"] = dimension_filter

        if order_by:
            payload["orderBys"] = order_by

        result = await self._request(
            "POST",
            f"{self.property_path}:runReport",
            json=payload,
        )

        return result

    async def run_realtime_report(
        self,
        dimensions: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Run a real-time report.

        Shows data from the last 30 minutes.

        Args:
            dimensions: Real-time dimensions (e.g., ["country", "city"])
            metrics: Real-time metrics (e.g., ["activeUsers"])
            limit: Maximum rows

        Returns:
            Real-time report data
        """
        if not self.property_id:
            raise GA4Error("Property ID required")

        if not dimensions:
            dimensions = ["country"]
        if not metrics:
            metrics = ["activeUsers"]

        payload = {
            "dimensions": [{"name": d} for d in dimensions],
            "metrics": [{"name": m} for m in metrics],
            "limit": limit,
        }

        result = await self._request(
            "POST",
            f"{self.property_path}:runRealtimeReport",
            json=payload,
        )

        return result

    async def get_active_users(self) -> int:
        """Get current active users (real-time)."""
        result = await self.run_realtime_report(
            dimensions=[],
            metrics=["activeUsers"],
        )

        rows = result.get("rows", [])
        if rows:
            return int(rows[0].get("metricValues", [{}])[0].get("value", 0))
        return 0

    async def get_traffic_overview(
        self,
        days: int = 28,
    ) -> Dict[str, Any]:
        """
        Get traffic overview metrics.

        Returns:
            Overview with sessions, users, pageviews, bounce rate, etc.
        """
        result = await self.run_report(
            dimensions=[],
            metrics=[
                "sessions",
                "activeUsers",
                "newUsers",
                "screenPageViews",
                "bounceRate",
                "averageSessionDuration",
                "engagedSessions",
                "engagementRate",
                "conversions",
            ],
            days=days,
        )

        rows = result.get("rows", [])
        if not rows:
            return {}

        metric_headers = result.get("metricHeaders", [])
        values = rows[0].get("metricValues", [])

        overview = {}
        for i, header in enumerate(metric_headers):
            name = header.get("name", f"metric_{i}")
            value = values[i].get("value", "0") if i < len(values) else "0"

            # Parse based on type
            metric_type = header.get("type", "TYPE_INTEGER")
            if metric_type == "TYPE_FLOAT":
                overview[name] = round(float(value), 2)
            else:
                overview[name] = int(float(value))

        return overview

    async def get_top_pages(
        self,
        days: int = 28,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Get top performing pages.

        Returns list of pages with metrics.
        """
        result = await self.run_report(
            dimensions=["pagePath", "pageTitle"],
            metrics=["screenPageViews", "activeUsers", "bounceRate", "averageSessionDuration"],
            days=days,
            limit=limit,
            order_by=[{"metric": {"metricName": "screenPageViews"}, "desc": True}],
        )

        pages = []
        dimension_headers = result.get("dimensionHeaders", [])
        metric_headers = result.get("metricHeaders", [])

        for row in result.get("rows", []):
            dim_values = row.get("dimensionValues", [])
            metric_values = row.get("metricValues", [])

            page = {}
            for i, header in enumerate(dimension_headers):
                page[header.get("name", f"dim_{i}")] = dim_values[i].get("value", "") if i < len(dim_values) else ""

            for i, header in enumerate(metric_headers):
                name = header.get("name", f"metric_{i}")
                value = metric_values[i].get("value", "0") if i < len(metric_values) else "0"
                metric_type = header.get("type", "TYPE_INTEGER")

                if metric_type == "TYPE_FLOAT":
                    page[name] = round(float(value), 2)
                else:
                    page[name] = int(float(value))

            pages.append(page)

        return pages

    async def get_traffic_sources(
        self,
        days: int = 28,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Get traffic source breakdown.

        Returns list of sources with metrics.
        """
        result = await self.run_report(
            dimensions=["sessionSource", "sessionMedium"],
            metrics=["sessions", "activeUsers", "conversions", "engagementRate"],
            days=days,
            limit=limit,
            order_by=[{"metric": {"metricName": "sessions"}, "desc": True}],
        )

        sources = []
        for row in result.get("rows", []):
            dim_values = row.get("dimensionValues", [])
            metric_values = row.get("metricValues", [])

            sources.append({
                "source": dim_values[0].get("value", "(direct)") if dim_values else "(direct)",
                "medium": dim_values[1].get("value", "(none)") if len(dim_values) > 1 else "(none)",
                "sessions": int(metric_values[0].get("value", 0)) if metric_values else 0,
                "users": int(metric_values[1].get("value", 0)) if len(metric_values) > 1 else 0,
                "conversions": int(metric_values[2].get("value", 0)) if len(metric_values) > 2 else 0,
                "engagement_rate": round(float(metric_values[3].get("value", 0)) * 100, 2) if len(metric_values) > 3 else 0,
            })

        return sources

    async def get_device_breakdown(
        self,
        days: int = 28,
    ) -> List[Dict[str, Any]]:
        """
        Get device category breakdown.

        Returns list with desktop, mobile, tablet splits.
        """
        result = await self.run_report(
            dimensions=["deviceCategory"],
            metrics=["sessions", "activeUsers", "bounceRate"],
            days=days,
        )

        devices = []
        for row in result.get("rows", []):
            dim_values = row.get("dimensionValues", [])
            metric_values = row.get("metricValues", [])

            devices.append({
                "device": dim_values[0].get("value", "unknown") if dim_values else "unknown",
                "sessions": int(metric_values[0].get("value", 0)) if metric_values else 0,
                "users": int(metric_values[1].get("value", 0)) if len(metric_values) > 1 else 0,
                "bounce_rate": round(float(metric_values[2].get("value", 0)) * 100, 2) if len(metric_values) > 2 else 0,
            })

        return devices

    async def get_geographic_breakdown(
        self,
        days: int = 28,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Get geographic breakdown by country.

        Returns list of countries with metrics.
        """
        result = await self.run_report(
            dimensions=["country"],
            metrics=["sessions", "activeUsers", "conversions"],
            days=days,
            limit=limit,
            order_by=[{"metric": {"metricName": "sessions"}, "desc": True}],
        )

        countries = []
        for row in result.get("rows", []):
            dim_values = row.get("dimensionValues", [])
            metric_values = row.get("metricValues", [])

            countries.append({
                "country": dim_values[0].get("value", "unknown") if dim_values else "unknown",
                "sessions": int(metric_values[0].get("value", 0)) if metric_values else 0,
                "users": int(metric_values[1].get("value", 0)) if len(metric_values) > 1 else 0,
                "conversions": int(metric_values[2].get("value", 0)) if len(metric_values) > 2 else 0,
            })

        return countries

    async def get_conversion_data(
        self,
        days: int = 28,
    ) -> Dict[str, Any]:
        """
        Get conversion/goal data.

        Returns conversion metrics and event data.
        """
        result = await self.run_report(
            dimensions=["eventName"],
            metrics=["eventCount", "conversions", "totalRevenue"],
            days=days,
            limit=50,
            order_by=[{"metric": {"metricName": "eventCount"}, "desc": True}],
        )

        events = []
        total_conversions = 0
        total_revenue = 0

        for row in result.get("rows", []):
            dim_values = row.get("dimensionValues", [])
            metric_values = row.get("metricValues", [])

            event_name = dim_values[0].get("value", "") if dim_values else ""
            conversions = int(metric_values[1].get("value", 0)) if len(metric_values) > 1 else 0
            revenue = float(metric_values[2].get("value", 0)) if len(metric_values) > 2 else 0

            total_conversions += conversions
            total_revenue += revenue

            events.append({
                "event": event_name,
                "count": int(metric_values[0].get("value", 0)) if metric_values else 0,
                "conversions": conversions,
                "revenue": round(revenue, 2),
            })

        return {
            "total_conversions": total_conversions,
            "total_revenue": round(total_revenue, 2),
            "events": events,
        }
