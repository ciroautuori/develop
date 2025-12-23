"""
Google Search Console Service - SEO Analytics
Manages Search Console API integration for SEO metrics and insights
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session

from .models import AdminGoogleSettings

logger = logging.getLogger(__name__)


class GoogleSearchConsoleService:
    """Service for Google Search Console API operations."""

    SITE_URL = "https://markettina.it"

    def __init__(self, credentials: Credentials):
        """Initialize Search Console service with credentials."""
        self.credentials = credentials
        self.service = build("searchconsole", "v1", credentials=credentials)

    @classmethod
    def from_admin_token(cls, db: Session, admin_id: int) -> Optional["GoogleSearchConsoleService"]:
        """Create service from admin's stored Google token."""
        from app.core.config import settings

        google_settings = db.query(AdminGoogleSettings).filter(
            AdminGoogleSettings.admin_id == admin_id
        ).first()

        if not google_settings or not google_settings.access_token:
            return None

        # Check if webmasters scope is present
        scopes = google_settings.scopes or ""
        if "webmasters" not in scopes.lower():
            return None

        # Create credentials using app's OAuth client credentials
        credentials = Credentials(
            token=google_settings.access_token,
            refresh_token=google_settings.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=google_settings.scopes.split() if google_settings.scopes else []
        )

        return cls(credentials)

    def list_sites(self) -> list[dict[str, Any]]:
        """List all verified sites in Search Console."""
        try:
            response = self.service.sites().list().execute()
            return response.get("siteEntry", [])
        except HttpError as e:
            logger.error(f"Error listing Search Console sites: {e}")
            return []

    def get_full_seo_dashboard(self, days: int = 30) -> dict[str, Any]:
        """Get complete SEO dashboard with all metrics."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # Get overview metrics
        overview = self.get_overview_metrics(days)

        # Get top queries
        top_queries = self.get_top_queries(days, limit=50)

        # Get top pages
        top_pages = self.get_top_pages(days, limit=50)

        # Get daily performance
        daily_data = self.get_daily_performance(days)

        # Get device breakdown
        devices = self.get_device_breakdown(days)

        # Get country breakdown
        countries = self.get_country_breakdown(days)

        # Get ToolAI specific performance
        toolai_performance = self.get_toolai_performance(days)

        # Get keyword opportunities
        opportunities = self.get_keyword_opportunities(days)

        return {
            "overview": overview,
            "top_queries": top_queries,
            "top_pages": top_pages,
            "daily_data": daily_data,
            "devices": devices,
            "countries": countries,
            "toolai_performance": toolai_performance,
            "keyword_opportunities": opportunities
        }

    def get_overview_metrics(self, days: int = 30) -> dict[str, Any]:
        """Get overview metrics with comparison to previous period."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # Current period
        current_metrics = self._query_analytics(start_date, end_date)

        # Previous period (same length)
        prev_end_date = start_date - timedelta(days=1)
        prev_start_date = prev_end_date - timedelta(days=days)
        previous_metrics = self._query_analytics(prev_start_date, prev_end_date)

        # Calculate changes
        changes = {
            "clicks": self._calculate_change(current_metrics["clicks"], previous_metrics["clicks"]),
            "impressions": self._calculate_change(current_metrics["impressions"], previous_metrics["impressions"]),
            "ctr": self._calculate_change(current_metrics["ctr"], previous_metrics["ctr"]),
            "position": self._calculate_change(current_metrics["position"], previous_metrics["position"], inverse=True)
        }

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "metrics": current_metrics,
            "previous": previous_metrics,
            "changes": changes
        }

    def get_top_queries(self, days: int = 30, limit: int = 50) -> list[dict[str, Any]]:
        """Get top performing search queries."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        try:
            request = {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "dimensions": ["query"],
                "rowLimit": limit,
                "dataState": "final"
            }

            response = self.service.searchanalytics().query(
                siteUrl=self.SITE_URL,
                body=request
            ).execute()

            rows = response.get("rows", [])
            return [
                {
                    "query": row["keys"][0],
                    "clicks": row["clicks"],
                    "impressions": row["impressions"],
                    "ctr": row["ctr"] * 100,
                    "position": row["position"]
                }
                for row in rows
            ]
        except HttpError as e:
            logger.error(f"Error fetching top queries: {e}")
            return []

    def get_top_pages(self, days: int = 30, limit: int = 50) -> list[dict[str, Any]]:
        """Get top performing pages."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        try:
            request = {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "dimensions": ["page"],
                "rowLimit": limit,
                "dataState": "final"
            }

            response = self.service.searchanalytics().query(
                siteUrl=self.SITE_URL,
                body=request
            ).execute()

            rows = response.get("rows", [])
            return [
                {
                    "page": row["keys"][0],
                    "clicks": row["clicks"],
                    "impressions": row["impressions"],
                    "ctr": row["ctr"] * 100,
                    "position": row["position"]
                }
                for row in rows
            ]
        except HttpError as e:
            logger.error(f"Error fetching top pages: {e}")
            return []

    def get_daily_performance(self, days: int = 30) -> list[dict[str, Any]]:
        """Get daily performance metrics."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        try:
            request = {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "dimensions": ["date"],
                "dataState": "final"
            }

            response = self.service.searchanalytics().query(
                siteUrl=self.SITE_URL,
                body=request
            ).execute()

            rows = response.get("rows", [])
            return [
                {
                    "date": row["keys"][0],
                    "clicks": row["clicks"],
                    "impressions": row["impressions"],
                    "ctr": row["ctr"] * 100,
                    "position": row["position"]
                }
                for row in rows
            ]
        except HttpError as e:
            logger.error(f"Error fetching daily performance: {e}")
            return []

    def get_device_breakdown(self, days: int = 30) -> list[dict[str, Any]]:
        """Get performance breakdown by device type."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        try:
            request = {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "dimensions": ["device"],
                "dataState": "final"
            }

            response = self.service.searchanalytics().query(
                siteUrl=self.SITE_URL,
                body=request
            ).execute()

            rows = response.get("rows", [])
            return [
                {
                    "device": row["keys"][0],
                    "clicks": row["clicks"],
                    "impressions": row["impressions"],
                    "ctr": row["ctr"] * 100,
                    "position": row["position"]
                }
                for row in rows
            ]
        except HttpError as e:
            logger.error(f"Error fetching device breakdown: {e}")
            return []

    def get_country_breakdown(self, days: int = 30) -> list[dict[str, Any]]:
        """Get performance breakdown by country."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        try:
            request = {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "dimensions": ["country"],
                "rowLimit": 10,
                "dataState": "final"
            }

            response = self.service.searchanalytics().query(
                siteUrl=self.SITE_URL,
                body=request
            ).execute()

            rows = response.get("rows", [])
            return [
                {
                    "country": row["keys"][0],
                    "clicks": row["clicks"],
                    "impressions": row["impressions"],
                    "ctr": row["ctr"] * 100,
                    "position": row["position"]
                }
                for row in rows
            ]
        except HttpError as e:
            logger.error(f"Error fetching country breakdown: {e}")
            return []

    def get_toolai_performance(self, days: int = 30) -> dict[str, Any]:
        """Get performance metrics specifically for ToolAI pages."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        try:
            request = {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "dimensions": ["page"],
                "dimensionFilterGroups": [{
                    "filters": [{
                        "dimension": "page",
                        "operator": "contains",
                        "expression": "/toolai/"
                    }]
                }],
                "rowLimit": 100,
                "dataState": "final"
            }

            response = self.service.searchanalytics().query(
                siteUrl=self.SITE_URL,
                body=request
            ).execute()

            rows = response.get("rows", [])

            # Calculate totals
            total_clicks = sum(row["clicks"] for row in rows)
            total_impressions = sum(row["impressions"] for row in rows)
            avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            avg_position = sum(row["position"] for row in rows) / len(rows) if rows else 0

            # Top ToolAI pages
            top_pages = [
                {
                    "page": row["keys"][0],
                    "clicks": row["clicks"],
                    "impressions": row["impressions"],
                    "ctr": row["ctr"] * 100,
                    "position": row["position"]
                }
                for row in rows[:10]
            ]

            return {
                "total_clicks": total_clicks,
                "total_impressions": total_impressions,
                "avg_ctr": avg_ctr,
                "avg_position": avg_position,
                "pages_count": len(rows),
                "top_pages": top_pages
            }
        except HttpError as e:
            logger.error(f"Error fetching ToolAI performance: {e}")
            return {
                "total_clicks": 0,
                "total_impressions": 0,
                "avg_ctr": 0,
                "avg_position": 0,
                "pages_count": 0,
                "top_pages": []
            }

    def get_keyword_opportunities(self, days: int = 30) -> list[dict[str, Any]]:
        """Find keyword opportunities (high impressions, low CTR, position 11-20)."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        try:
            request = {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "dimensions": ["query"],
                "rowLimit": 500,
                "dataState": "final"
            }

            response = self.service.searchanalytics().query(
                siteUrl=self.SITE_URL,
                body=request
            ).execute()

            rows = response.get("rows", [])

            # Filter opportunities: position 11-20, high impressions, low CTR
            opportunities = []
            for row in rows:
                position = row["position"]
                ctr = row["ctr"] * 100
                impressions = row["impressions"]
                clicks = row["clicks"]

                # Opportunity criteria
                if 11 <= position <= 20 and impressions >= 50 and ctr < 5:
                    # Calculate potential clicks if position improves to ~5
                    potential_ctr = 8.0  # Average CTR for position 5
                    potential_clicks = int(impressions * potential_ctr / 100)

                    opportunities.append({
                        "query": row["keys"][0],
                        "impressions": impressions,
                        "clicks": clicks,
                        "ctr": ctr,
                        "position": position,
                        "potential_clicks": potential_clicks
                    })

            # Sort by potential clicks descending
            opportunities.sort(key=lambda x: x["potential_clicks"], reverse=True)

            return opportunities[:20]  # Top 20 opportunities
        except HttpError as e:
            logger.error(f"Error fetching keyword opportunities: {e}")
            return []

    def _query_analytics(self, start_date, end_date) -> dict[str, float]:
        """Execute a Search Console analytics query."""
        try:
            request = {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "dataState": "final"
            }

            response = self.service.searchanalytics().query(
                siteUrl=self.SITE_URL,
                body=request
            ).execute()

            rows = response.get("rows", [])
            if not rows:
                return {"clicks": 0, "impressions": 0, "ctr": 0, "position": 0}

            # Sum all metrics
            total_clicks = sum(row.get("clicks", 0) for row in rows)
            total_impressions = sum(row.get("impressions", 0) for row in rows)
            avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            avg_position = sum(row.get("position", 0) for row in rows) / len(rows)

            return {
                "clicks": total_clicks,
                "impressions": total_impressions,
                "ctr": avg_ctr,
                "position": avg_position
            }
        except HttpError as e:
            logger.error(f"Error querying Search Console analytics: {e}")
            return {"clicks": 0, "impressions": 0, "ctr": 0, "position": 0}

    def _calculate_change(self, current: float, previous: float, inverse: bool = False) -> float:
        """Calculate percentage change between two values."""
        if previous == 0:
            return 0.0

        change = ((current - previous) / previous) * 100

        # For metrics where lower is better (like position), invert the sign
        if inverse:
            change = -change

        return round(change, 1)
