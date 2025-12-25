"""
Google Analytics Data API Service (GA4)
Real implementation using Google Analytics Data API v1
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.domain.auth.oauth_tokens import OAuthTokenService, OAuthProvider
from .schemas import (
    GAOverviewMetrics,
    GATrafficSource,
    GATopPage,
    GADeviceBreakdown,
    GAGeographicData,
    GADashboardResponse,
    GAReportResponse,
    GAReportRow,
    GAMetricValue,
    GADimensionValue,
)

logger = logging.getLogger(__name__)

# GA4 Data API Base URL
GA4_DATA_API_BASE = "https://analyticsdata.googleapis.com/v1beta"

# Default GA4 Property ID from environment
DEFAULT_GA4_PROPERTY_ID = settings.GA4_PROPERTY_ID if hasattr(settings, 'GA4_PROPERTY_ID') else "properties/467399370"


class GoogleAnalyticsService:
    """Service for Google Analytics Data API (GA4)."""

    def __init__(self, access_token: str, property_id: Optional[str] = None):
        """
        Initialize GA4 service.

        Args:
            access_token: Valid Google OAuth access token with analytics.readonly scope
            property_id: GA4 property ID (format: properties/XXXXXX)
        """
        self.access_token = access_token
        self.property_id = property_id or DEFAULT_GA4_PROPERTY_ID
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    @classmethod
    def from_admin_token(cls, db: Session, admin_id: int, property_id: Optional[str] = None) -> Optional["GoogleAnalyticsService"]:
        """
        Create service instance from admin's stored OAuth token.

        Args:
            db: Database session
            admin_id: Admin user ID
            property_id: Optional GA4 property ID

        Returns:
            GoogleAnalyticsService instance or None if no valid token
        """
        token = OAuthTokenService.get_valid_token(db, admin_id, OAuthProvider.GOOGLE)
        if not token:
            logger.warning(f"No valid Google OAuth token for admin {admin_id}")
            return None
        return cls(access_token=token, property_id=property_id)

    async def run_report(
        self,
        metrics: List[str],
        dimensions: Optional[List[str]] = None,
        date_ranges: Optional[List[Dict[str, str]]] = None,
        limit: int = 100,
        order_by: Optional[str] = None,
        descending: bool = True
    ) -> GAReportResponse:
        """
        Run a GA4 report.

        Args:
            metrics: List of metric names (e.g., ["activeUsers", "sessions"])
            dimensions: Optional list of dimension names
            date_ranges: Date ranges (default: last 30 days)
            limit: Max rows to return
            order_by: Metric or dimension to order by
            descending: Sort descending if True

        Returns:
            GAReportResponse with report data
        """
        if not date_ranges:
            date_ranges = [{"startDate": "30daysAgo", "endDate": "today"}]

        # Build request body
        body = {
            "dateRanges": date_ranges,
            "metrics": [{"name": m} for m in metrics],
            "limit": str(limit),
        }

        if dimensions:
            body["dimensions"] = [{"name": d} for d in dimensions]

        if order_by:
            body["orderBys"] = [{
                "metric" if order_by in metrics else "dimension": {"metricName" if order_by in metrics else "dimensionName": order_by},
                "desc": descending
            }]

        url = f"{GA4_DATA_API_BASE}/{self.property_id}:runReport"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=body,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"GA4 API error: {response.status_code} - {response.text}")
                    return GAReportResponse(rows=[], row_count=0)

                data = response.json()
                return self._parse_report_response(data, metrics, dimensions or [])

        except Exception as e:
            logger.error(f"Error running GA4 report: {e}", exc_info=True)
            return GAReportResponse(rows=[], row_count=0)

    def _parse_report_response(
        self,
        data: Dict[str, Any],
        metrics: List[str],
        dimensions: List[str]
    ) -> GAReportResponse:
        """Parse GA4 API response into structured format."""
        rows = []

        for row in data.get("rows", []):
            dimension_values = []
            metric_values = []

            # Parse dimensions
            for i, dim_value in enumerate(row.get("dimensionValues", [])):
                dim_name = dimensions[i] if i < len(dimensions) else f"dimension{i}"
                dimension_values.append(GADimensionValue(
                    name=dim_name,
                    value=dim_value.get("value", "")
                ))

            # Parse metrics
            for i, met_value in enumerate(row.get("metricValues", [])):
                met_name = metrics[i] if i < len(metrics) else f"metric{i}"
                metric_values.append(GAMetricValue(
                    name=met_name,
                    value=met_value.get("value", "0")
                ))

            rows.append(GAReportRow(
                dimension_values=dimension_values,
                metric_values=metric_values
            ))

        return GAReportResponse(
            rows=rows,
            row_count=data.get("rowCount", len(rows)),
            metadata=data.get("metadata", {})
        )

    async def get_overview_metrics(self, days: int = 30) -> GAOverviewMetrics:
        """
        Get overview metrics for dashboard.

        Args:
            days: Number of days to look back

        Returns:
            GAOverviewMetrics with key metrics
        """
        date_ranges = [{"startDate": f"{days}daysAgo", "endDate": "today"}]

        metrics = [
            "activeUsers",
            "newUsers",
            "sessions",
            "screenPageViews",
            "bounceRate",
            "averageSessionDuration",
            "conversions"
        ]

        report = await self.run_report(metrics=metrics, date_ranges=date_ranges)

        # Extract values from first row
        values = {}
        if report.rows:
            for mv in report.rows[0].metric_values:
                values[mv.name] = mv.value

        return GAOverviewMetrics(
            active_users=int(float(values.get("activeUsers", 0))),
            new_users=int(float(values.get("newUsers", 0))),
            sessions=int(float(values.get("sessions", 0))),
            page_views=int(float(values.get("screenPageViews", 0))),
            bounce_rate=round(float(values.get("bounceRate", 0)) * 100, 2),
            avg_session_duration=round(float(values.get("averageSessionDuration", 0)), 2),
            conversions=int(float(values.get("conversions", 0))),
            period=f"{days}d"
        )

    async def get_traffic_sources(self, days: int = 30, limit: int = 10) -> List[GATrafficSource]:
        """Get traffic sources breakdown."""
        report = await self.run_report(
            metrics=["activeUsers", "sessions"],
            dimensions=["sessionSource", "sessionMedium"],
            date_ranges=[{"startDate": f"{days}daysAgo", "endDate": "today"}],
            limit=limit,
            order_by="sessions",
            descending=True
        )

        sources = []
        total_sessions = sum(
            int(float(row.metric_values[1].value))
            for row in report.rows
        ) or 1

        for row in report.rows:
            source = row.dimension_values[0].value if row.dimension_values else "direct"
            medium = row.dimension_values[1].value if len(row.dimension_values) > 1 else "(none)"
            users = int(float(row.metric_values[0].value))
            sessions = int(float(row.metric_values[1].value))

            sources.append(GATrafficSource(
                source=source,
                medium=medium,
                users=users,
                sessions=sessions,
                percentage=round((sessions / total_sessions) * 100, 2)
            ))

        return sources

    async def get_top_pages(self, days: int = 30, limit: int = 10) -> List[GATopPage]:
        """Get top pages by views."""
        report = await self.run_report(
            metrics=["screenPageViews", "activeUsers", "averageSessionDuration"],
            dimensions=["pagePath"],
            date_ranges=[{"startDate": f"{days}daysAgo", "endDate": "today"}],
            limit=limit,
            order_by="screenPageViews",
            descending=True
        )

        pages = []
        for row in report.rows:
            path = row.dimension_values[0].value if row.dimension_values else "/"
            page_views = int(float(row.metric_values[0].value))
            unique_views = int(float(row.metric_values[1].value))
            avg_time = float(row.metric_values[2].value)

            pages.append(GATopPage(
                path=path,
                page_views=page_views,
                unique_views=unique_views,
                avg_time_on_page=round(avg_time, 2)
            ))

        return pages

    async def get_device_breakdown(self, days: int = 30) -> List[GADeviceBreakdown]:
        """Get device category breakdown."""
        report = await self.run_report(
            metrics=["activeUsers", "sessions"],
            dimensions=["deviceCategory"],
            date_ranges=[{"startDate": f"{days}daysAgo", "endDate": "today"}],
            limit=10
        )

        devices = []
        total_sessions = sum(
            int(float(row.metric_values[1].value))
            for row in report.rows
        ) or 1

        for row in report.rows:
            device = row.dimension_values[0].value if row.dimension_values else "unknown"
            users = int(float(row.metric_values[0].value))
            sessions = int(float(row.metric_values[1].value))

            devices.append(GADeviceBreakdown(
                device=device,
                users=users,
                sessions=sessions,
                percentage=round((sessions / total_sessions) * 100, 2)
            ))

        return devices

    async def get_geographic_data(self, days: int = 30, limit: int = 10) -> List[GAGeographicData]:
        """Get geographic breakdown."""
        report = await self.run_report(
            metrics=["activeUsers", "sessions"],
            dimensions=["country", "city"],
            date_ranges=[{"startDate": f"{days}daysAgo", "endDate": "today"}],
            limit=limit,
            order_by="sessions",
            descending=True
        )

        geo_data = []
        for row in report.rows:
            country = row.dimension_values[0].value if row.dimension_values else "Unknown"
            city = row.dimension_values[1].value if len(row.dimension_values) > 1 else None
            users = int(float(row.metric_values[0].value))
            sessions = int(float(row.metric_values[1].value))

            geo_data.append(GAGeographicData(
                country=country,
                city=city if city != "(not set)" else None,
                users=users,
                sessions=sessions
            ))

        return geo_data

    async def get_daily_traffic(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily traffic over time."""
        report = await self.run_report(
            metrics=["activeUsers", "sessions", "screenPageViews"],
            dimensions=["date"],
            date_ranges=[{"startDate": f"{days}daysAgo", "endDate": "today"}],
            limit=days + 1,
            order_by="date",
            descending=False
        )

        daily_data = []
        for row in report.rows:
            date_str = row.dimension_values[0].value if row.dimension_values else ""

            # Parse date (format: YYYYMMDD)
            try:
                date_obj = datetime.strptime(date_str, "%Y%m%d")
                formatted_date = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                formatted_date = date_str

            daily_data.append({
                "date": formatted_date,
                "users": int(float(row.metric_values[0].value)),
                "sessions": int(float(row.metric_values[1].value)),
                "pageViews": int(float(row.metric_values[2].value))
            })

        return daily_data

    async def get_full_dashboard(self, days: int = 30) -> GADashboardResponse:
        """
        Get complete dashboard data in a single call.

        Args:
            days: Number of days to look back

        Returns:
            GADashboardResponse with all dashboard data
        """
        # Run all queries concurrently
        import asyncio

        overview, sources, pages, devices, geo, daily = await asyncio.gather(
            self.get_overview_metrics(days),
            self.get_traffic_sources(days),
            self.get_top_pages(days),
            self.get_device_breakdown(days),
            self.get_geographic_data(days),
            self.get_daily_traffic(days),
            return_exceptions=True
        )

        # Handle any exceptions
        if isinstance(overview, Exception):
            logger.error(f"Error getting overview: {overview}")
            overview = GAOverviewMetrics(period=f"{days}d")
        if isinstance(sources, Exception):
            logger.error(f"Error getting sources: {sources}")
            sources = []
        if isinstance(pages, Exception):
            logger.error(f"Error getting pages: {pages}")
            pages = []
        if isinstance(devices, Exception):
            logger.error(f"Error getting devices: {devices}")
            devices = []
        if isinstance(geo, Exception):
            logger.error(f"Error getting geo: {geo}")
            geo = []
        if isinstance(daily, Exception):
            logger.error(f"Error getting daily: {daily}")
            daily = []

        return GADashboardResponse(
            overview=overview,
            traffic_sources=sources,
            top_pages=pages,
            device_breakdown=devices,
            geographic_data=geo,
            daily_traffic=daily,
            last_updated=datetime.utcnow()
        )

    async def list_accounts(self) -> List[Dict[str, Any]]:
        """List available GA4 accounts."""
        url = "https://analyticsadmin.googleapis.com/v1beta/accounts"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=30.0)

                if response.status_code != 200:
                    logger.error(f"Error listing GA4 accounts: {response.text}")
                    return []

                data = response.json()
                return data.get("accounts", [])

        except Exception as e:
            logger.error(f"Error listing GA4 accounts: {e}", exc_info=True)
            return []

    async def list_properties(self, account_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List GA4 properties for an account."""
        url = "https://analyticsadmin.googleapis.com/v1beta/properties"
        params = {}

        if account_id:
            params["filter"] = f"parent:accounts/{account_id}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Error listing GA4 properties: {response.text}")
                    return []

                data = response.json()
                return data.get("properties", [])

        except Exception as e:
            logger.error(f"Error listing GA4 properties: {e}", exc_info=True)
            return []
