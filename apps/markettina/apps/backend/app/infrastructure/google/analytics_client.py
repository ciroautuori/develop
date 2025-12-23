"""
Google Analytics 4 Data API Client - Production-ready GA4 integration.

Features:
- Traffic and session data
- Real-time users
- Page views and performance
- Traffic sources and channels
- Conversion tracking
- Audience demographics

API Reference: https://developers.google.com/analytics/devguides/reporting/data/v1
"""

import logging
from datetime import datetime, timedelta
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class GA4Client:
    """
    Google Analytics 4 Data API client.

    Authentication:
    - Service account with Analytics Data API enabled
    - Property access required

    Rate Limits:
    - Core reporting: 10,000 requests per day
    - Real-time: 1,000 requests per day

    Usage:
        client = GA4Client(property_id="properties/123456")
        overview = await client.get_traffic_overview(days=30)
    """

    BASE_URL = "https://analyticsdata.googleapis.com/v1beta"

    def __init__(
        self,
        property_id: str | None = None,
        credentials_json: str | None = None,
    ):
        self._property_id = property_id or settings.GA4_PROPERTY_ID
        self._credentials_json = credentials_json or getattr(settings, "GA4_CREDENTIALS", "") or getattr(settings, "GOOGLE_CREDENTIALS_JSON", "")
        self._access_token: str | None = None
        self._token_expires: datetime | None = None
        self._client: httpx.AsyncClient | None = None

    def is_configured(self) -> bool:
        """Check if client is properly configured."""
        return bool(self._property_id and self._credentials_json)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _get_access_token(self) -> str:
        """Get OAuth 2.0 access token using service account credentials."""
        import json
        import time
        import jwt

        if self._access_token and self._token_expires:
            if datetime.utcnow() < self._token_expires:
                return self._access_token

        if not self._credentials_json:
            raise ValueError("Google credentials not configured")

        creds = json.loads(self._credentials_json)

        now = int(time.time())
        payload = {
            "iss": creds["client_email"],
            "scope": "https://www.googleapis.com/auth/analytics.readonly",
            "aud": "https://oauth2.googleapis.com/token",
            "iat": now,
            "exp": now + 3600,
        }

        signed_jwt = jwt.encode(
            payload,
            creds["private_key"],
            algorithm="RS256",
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "assertion": signed_jwt,
                },
            )

            if response.status_code != 200:
                raise ValueError(f"Token exchange failed: {response.text}")

            token_data = response.json()
            self._access_token = token_data["access_token"]
            self._token_expires = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600) - 60)

            return self._access_token

    async def _request(
        self,
        method: str,
        endpoint: str,
        json: dict | None = None,
    ) -> dict[str, Any]:
        """Make authenticated API request."""
        token = await self._get_access_token()
        client = await self._get_client()

        response = await client.request(
            method,
            endpoint,
            headers={"Authorization": f"Bearer {token}"},
            json=json,
        )

        if response.status_code >= 400:
            logger.error(f"GA4 API error: {response.status_code} - {response.text}")
            raise ValueError(f"API Error: {response.status_code}")

        return response.json() if response.content else {}

    def _format_property(self) -> str:
        """Format property ID for API."""
        if self._property_id.startswith("properties/"):
            return self._property_id
        return f"properties/{self._property_id}"

    async def run_report(
        self,
        dimensions: list[str],
        metrics: list[str],
        start_date: str = "28daysAgo",
        end_date: str = "today",
        limit: int = 100,
        dimension_filter: dict | None = None,
    ) -> list[dict[str, Any]]:
        """
        Run a GA4 report.

        Args:
            dimensions: List of dimension names
            metrics: List of metric names
            start_date: Start date (YYYY-MM-DD or relative like "28daysAgo")
            end_date: End date
            limit: Max rows
            dimension_filter: Optional filter expression

        Returns:
            List of report rows
        """
        request_body: dict[str, Any] = {
            "dateRanges": [{"startDate": start_date, "endDate": end_date}],
            "dimensions": [{"name": d} for d in dimensions],
            "metrics": [{"name": m} for m in metrics],
            "limit": limit,
        }

        if dimension_filter:
            request_body["dimensionFilter"] = dimension_filter

        response = await self._request(
            "POST",
            f"/{self._format_property()}:runReport",
            json=request_body,
        )

        rows = response.get("rows", [])
        dimension_headers = [h["name"] for h in response.get("dimensionHeaders", [])]
        metric_headers = [h["name"] for h in response.get("metricHeaders", [])]

        result = []
        for row in rows:
            row_data = {}

            for i, dim_value in enumerate(row.get("dimensionValues", [])):
                row_data[dimension_headers[i]] = dim_value.get("value", "")

            for i, metric_value in enumerate(row.get("metricValues", [])):
                value = metric_value.get("value", "0")
                # Convert to appropriate type
                try:
                    row_data[metric_headers[i]] = int(value) if "." not in value else float(value)
                except ValueError:
                    row_data[metric_headers[i]] = value

            result.append(row_data)

        return result

    async def get_traffic_overview(
        self,
        days: int = 28,
    ) -> dict[str, Any]:
        """
        Get traffic overview metrics.

        Args:
            days: Number of days to analyze

        Returns:
            Overview with sessions, users, pageviews, etc.
        """
        rows = await self.run_report(
            dimensions=[],
            metrics=[
                "sessions",
                "totalUsers",
                "newUsers",
                "screenPageViews",
                "bounceRate",
                "averageSessionDuration",
                "engagementRate",
                "eventCount",
            ],
            start_date=f"{days}daysAgo",
            end_date="today",
        )

        if not rows:
            return {
                "sessions": 0,
                "users": 0,
                "new_users": 0,
                "pageviews": 0,
                "bounce_rate": 0.0,
                "avg_session_duration": 0.0,
                "engagement_rate": 0.0,
                "events": 0,
            }

        data = rows[0]

        return {
            "sessions": data.get("sessions", 0),
            "users": data.get("totalUsers", 0),
            "new_users": data.get("newUsers", 0),
            "pageviews": data.get("screenPageViews", 0),
            "bounce_rate": round(float(data.get("bounceRate", 0)) * 100, 2),
            "avg_session_duration": round(float(data.get("averageSessionDuration", 0)), 1),
            "engagement_rate": round(float(data.get("engagementRate", 0)) * 100, 2),
            "events": data.get("eventCount", 0),
        }

    async def get_top_pages(
        self,
        days: int = 28,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Get top performing pages.

        Args:
            days: Days to analyze
            limit: Max pages

        Returns:
            List of pages with metrics
        """
        rows = await self.run_report(
            dimensions=["pagePath", "pageTitle"],
            metrics=["screenPageViews", "averageSessionDuration", "bounceRate"],
            start_date=f"{days}daysAgo",
            end_date="today",
            limit=limit,
        )

        return [
            {
                "path": row.get("pagePath", ""),
                "title": row.get("pageTitle", ""),
                "pageviews": row.get("screenPageViews", 0),
                "avg_time": round(float(row.get("averageSessionDuration", 0)), 1),
                "bounce_rate": round(float(row.get("bounceRate", 0)) * 100, 2),
            }
            for row in rows
        ]

    async def get_traffic_sources(
        self,
        days: int = 28,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Get traffic sources breakdown.

        Args:
            days: Days to analyze
            limit: Max sources

        Returns:
            List of sources with session counts
        """
        rows = await self.run_report(
            dimensions=["sessionDefaultChannelGroup"],
            metrics=["sessions", "totalUsers", "newUsers", "engagementRate"],
            start_date=f"{days}daysAgo",
            end_date="today",
            limit=limit,
        )

        return [
            {
                "channel": row.get("sessionDefaultChannelGroup", ""),
                "sessions": row.get("sessions", 0),
                "users": row.get("totalUsers", 0),
                "new_users": row.get("newUsers", 0),
                "engagement_rate": round(float(row.get("engagementRate", 0)) * 100, 2),
            }
            for row in rows
        ]

    async def get_traffic_by_source_medium(
        self,
        days: int = 28,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Get traffic by source/medium.

        Args:
            days: Days to analyze
            limit: Max rows

        Returns:
            Source/medium breakdown
        """
        rows = await self.run_report(
            dimensions=["sessionSource", "sessionMedium"],
            metrics=["sessions", "totalUsers", "bounceRate", "averageSessionDuration"],
            start_date=f"{days}daysAgo",
            end_date="today",
            limit=limit,
        )

        return [
            {
                "source": row.get("sessionSource", ""),
                "medium": row.get("sessionMedium", ""),
                "sessions": row.get("sessions", 0),
                "users": row.get("totalUsers", 0),
                "bounce_rate": round(float(row.get("bounceRate", 0)) * 100, 2),
                "avg_duration": round(float(row.get("averageSessionDuration", 0)), 1),
            }
            for row in rows
        ]

    async def get_real_time_users(self) -> dict[str, Any]:
        """
        Get real-time active users.

        Returns:
            Real-time user count and breakdown
        """
        response = await self._request(
            "POST",
            f"/{self._format_property()}:runRealtimeReport",
            json={
                "dimensions": [{"name": "deviceCategory"}],
                "metrics": [{"name": "activeUsers"}],
            },
        )

        rows = response.get("rows", [])
        total = 0
        by_device = {}

        for row in rows:
            device = row.get("dimensionValues", [{}])[0].get("value", "unknown")
            users = int(row.get("metricValues", [{}])[0].get("value", 0))
            by_device[device] = users
            total += users

        return {
            "total": total,
            "by_device": by_device,
        }

    async def get_conversions(
        self,
        days: int = 28,
        conversion_events: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get conversion data.

        Args:
            days: Days to analyze
            conversion_events: Specific events to track (default: all conversion events)

        Returns:
            Conversion data by event
        """
        rows = await self.run_report(
            dimensions=["eventName"],
            metrics=["conversions", "eventValue"],
            start_date=f"{days}daysAgo",
            end_date="today",
            limit=50,
        )

        conversions = []
        for row in rows:
            event_name = row.get("eventName", "")

            if conversion_events and event_name not in conversion_events:
                continue

            conversions.append({
                "event": event_name,
                "count": row.get("conversions", 0),
                "value": float(row.get("eventValue", 0)),
            })

        return conversions

    async def get_user_demographics(
        self,
        days: int = 28,
    ) -> dict[str, Any]:
        """
        Get user demographics (requires demographic data collection).

        Args:
            days: Days to analyze

        Returns:
            Demographics breakdown
        """
        # Get by country
        country_rows = await self.run_report(
            dimensions=["country"],
            metrics=["totalUsers"],
            start_date=f"{days}daysAgo",
            end_date="today",
            limit=10,
        )

        # Get by device
        device_rows = await self.run_report(
            dimensions=["deviceCategory"],
            metrics=["totalUsers"],
            start_date=f"{days}daysAgo",
            end_date="today",
            limit=10,
        )

        # Get by browser
        browser_rows = await self.run_report(
            dimensions=["browser"],
            metrics=["totalUsers"],
            start_date=f"{days}daysAgo",
            end_date="today",
            limit=10,
        )

        return {
            "top_countries": [
                {"country": r.get("country", ""), "users": r.get("totalUsers", 0)}
                for r in country_rows
            ],
            "devices": [
                {"device": r.get("deviceCategory", ""), "users": r.get("totalUsers", 0)}
                for r in device_rows
            ],
            "browsers": [
                {"browser": r.get("browser", ""), "users": r.get("totalUsers", 0)}
                for r in browser_rows
            ],
        }

    async def get_landing_pages(
        self,
        days: int = 28,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Get top landing pages.

        Args:
            days: Days to analyze
            limit: Max pages

        Returns:
            Landing pages with metrics
        """
        rows = await self.run_report(
            dimensions=["landingPage"],
            metrics=["sessions", "totalUsers", "bounceRate", "averageSessionDuration"],
            start_date=f"{days}daysAgo",
            end_date="today",
            limit=limit,
        )

        return [
            {
                "landing_page": row.get("landingPage", ""),
                "sessions": row.get("sessions", 0),
                "users": row.get("totalUsers", 0),
                "bounce_rate": round(float(row.get("bounceRate", 0)) * 100, 2),
                "avg_duration": round(float(row.get("averageSessionDuration", 0)), 1),
            }
            for row in rows
        ]

    async def get_campaign_performance(
        self,
        days: int = 28,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Get campaign performance (UTM tracking).

        Args:
            days: Days to analyze
            limit: Max campaigns

        Returns:
            Campaign performance data
        """
        rows = await self.run_report(
            dimensions=["sessionCampaignName"],
            metrics=["sessions", "totalUsers", "conversions", "engagementRate"],
            start_date=f"{days}daysAgo",
            end_date="today",
            limit=limit,
        )

        return [
            {
                "campaign": row.get("sessionCampaignName", "(not set)"),
                "sessions": row.get("sessions", 0),
                "users": row.get("totalUsers", 0),
                "conversions": row.get("conversions", 0),
                "engagement_rate": round(float(row.get("engagementRate", 0)) * 100, 2),
            }
            for row in rows
            if row.get("sessionCampaignName") != "(not set)"
        ]
