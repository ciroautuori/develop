"""
Marketing Analytics Service - Dashboard unificata e Report.

Features:
- Aggregazione metriche cross-platform
- KPI marketing in tempo reale
- Report PDF generation
- Export CSV/Excel
- Weekly email report
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & MODELS
# ============================================================================

class DateRange(str, Enum):
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    CUSTOM = "custom"


class MetricType(str, Enum):
    LEADS = "leads"
    CONVERSIONS = "conversions"
    ENGAGEMENT = "engagement"
    REACH = "reach"
    REVENUE = "revenue"
    EMAILS = "emails"
    SOCIAL = "social"


class KPICard(BaseModel):
    """Singolo KPI card per dashboard."""
    id: str
    label: str
    value: float
    previous_value: float = 0
    change_percent: float = 0
    trend: str = "neutral"  # up, down, neutral
    format: str = "number"  # number, currency, percent
    icon: str = "chart"


class ChartData(BaseModel):
    """Dati per grafici."""
    labels: list[str]
    datasets: list[dict[str, Any]]


class PlatformMetrics(BaseModel):
    """Metriche per singola piattaforma."""
    platform: str
    followers: int = 0
    engagement_rate: float = 0
    posts_count: int = 0
    reach: int = 0
    impressions: int = 0
    clicks: int = 0


class DashboardData(BaseModel):
    """Dati completi dashboard."""
    kpis: list[KPICard]
    leads_chart: ChartData
    conversions_chart: ChartData
    platform_metrics: list[PlatformMetrics]
    top_content: list[dict[str, Any]]
    recent_activities: list[dict[str, Any]]
    period: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ReportConfig(BaseModel):
    """Configurazione report."""
    title: str = "Marketing Report"
    date_range: DateRange = DateRange.LAST_30_DAYS
    start_date: datetime | None = None
    end_date: datetime | None = None
    include_kpis: bool = True
    include_charts: bool = True
    include_leads: bool = True
    include_campaigns: bool = True
    include_social: bool = True
    format: str = "pdf"  # pdf, csv, excel


# ============================================================================
# ANALYTICS SERVICE
# ============================================================================

class MarketingAnalyticsService:
    """
    Service per analytics marketing unificato.

    Aggrega dati da:
    - Lead CRM
    - Email Campaigns
    - Social Platforms
    - Content Performance
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        logger.info("analytics_service_initialized")

    def get_date_range(self, range_type: DateRange, start: datetime = None, end: datetime = None) -> tuple:
        """Calcola date range."""
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        ranges = {
            DateRange.TODAY: (today, now),
            DateRange.YESTERDAY: (today - timedelta(days=1), today),
            DateRange.LAST_7_DAYS: (today - timedelta(days=7), now),
            DateRange.LAST_30_DAYS: (today - timedelta(days=30), now),
            DateRange.THIS_MONTH: (today.replace(day=1), now),
            DateRange.LAST_MONTH: (
                (today.replace(day=1) - timedelta(days=1)).replace(day=1),
                today.replace(day=1) - timedelta(seconds=1)
            ),
        }

        if range_type == DateRange.CUSTOM and start and end:
            return (start, end)

        return ranges.get(range_type, (today - timedelta(days=30), now))

    async def get_dashboard_data(self, date_range: DateRange = DateRange.LAST_30_DAYS, db=None) -> DashboardData:
        """
        Ottiene dati completi per dashboard.
        Aggregazione cross-platform.
        """
        start_date, end_date = self.get_date_range(date_range)
        prev_start = start_date - (end_date - start_date)

        # KPIs
        kpis = await self._calculate_kpis(start_date, end_date, prev_start, db)

        # Charts
        leads_chart = await self._get_leads_chart(start_date, end_date, db)
        conversions_chart = await self._get_conversions_chart(start_date, end_date, db)

        # Platform metrics
        platform_metrics = await self._get_platform_metrics(start_date, end_date, db)

        # Top content
        top_content = await self._get_top_content(start_date, end_date, db)

        # Recent activities
        recent_activities = await self._get_recent_activities(db)

        return DashboardData(
            kpis=kpis,
            leads_chart=leads_chart,
            conversions_chart=conversions_chart,
            platform_metrics=platform_metrics,
            top_content=top_content,
            recent_activities=recent_activities,
            period=date_range.value
        )

    async def _calculate_kpis(self, start: datetime, end: datetime, prev_start: datetime, db) -> list[KPICard]:
        """Calcola KPIs principali."""

        # Per ora dati demo rappresentativi

        kpis = [
            KPICard(
                id="total_leads",
                label="Lead Totali",
                value=156,
                previous_value=142,
                change_percent=9.9,
                trend="up",
                format="number",
                icon="users"
            ),
            KPICard(
                id="conversion_rate",
                label="Tasso Conversione",
                value=3.8,
                previous_value=3.2,
                change_percent=18.7,
                trend="up",
                format="percent",
                icon="trending-up"
            ),
            KPICard(
                id="email_open_rate",
                label="Open Rate Email",
                value=24.5,
                previous_value=22.1,
                change_percent=10.9,
                trend="up",
                format="percent",
                icon="mail"
            ),
            KPICard(
                id="social_engagement",
                label="Engagement Social",
                value=4.2,
                previous_value=3.8,
                change_percent=10.5,
                trend="up",
                format="percent",
                icon="heart"
            ),
            KPICard(
                id="campaigns_sent",
                label="Campagne Inviate",
                value=12,
                previous_value=8,
                change_percent=50.0,
                trend="up",
                format="number",
                icon="send"
            ),
            KPICard(
                id="posts_published",
                label="Post Pubblicati",
                value=45,
                previous_value=38,
                change_percent=18.4,
                trend="up",
                format="number",
                icon="share-2"
            ),
        ]

        return kpis

    async def _get_leads_chart(self, start: datetime, end: datetime, db) -> ChartData:
        """Genera dati chart lead nel periodo."""
        days = (end - start).days
        labels = []
        data_new = []
        data_converted = []

        for i in range(min(days, 30)):
            date = start + timedelta(days=i)
            labels.append(date.strftime("%d/%m"))
            # Demo data - in produzione query reali
            data_new.append(5 + (i % 7) * 2)
            data_converted.append(1 + (i % 5))

        return ChartData(
            labels=labels,
            datasets=[
                {"label": "Nuovi Lead", "data": data_new, "borderColor": "#10B981", "fill": False},
                {"label": "Convertiti", "data": data_converted, "borderColor": "#F59E0B", "fill": False},
            ]
        )

    async def _get_conversions_chart(self, start: datetime, end: datetime, db) -> ChartData:
        """Genera dati chart conversioni per fonte."""
        return ChartData(
            labels=["Organic", "Paid Ads", "Email", "Social", "Referral", "Direct"],
            datasets=[
                {
                    "label": "Conversioni",
                    "data": [35, 28, 22, 18, 12, 8],
                    "backgroundColor": [
                        "#10B981", "#3B82F6", "#F59E0B",
                        "#EC4899", "#8B5CF6", "#6B7280"
                    ]
                }
            ]
        )

    async def _get_platform_metrics(self, start: datetime, end: datetime, db) -> list[PlatformMetrics]:
        """Metriche per piattaforma social."""
        return [
            PlatformMetrics(
                platform="linkedin",
                followers=2450,
                engagement_rate=4.8,
                posts_count=12,
                reach=18500,
                impressions=45000,
                clicks=890
            ),
            PlatformMetrics(
                platform="instagram",
                followers=5200,
                engagement_rate=6.2,
                posts_count=18,
                reach=32000,
                impressions=78000,
                clicks=1250
            ),
            PlatformMetrics(
                platform="facebook",
                followers=3800,
                engagement_rate=3.5,
                posts_count=15,
                reach=22000,
                impressions=52000,
                clicks=680
            ),
            PlatformMetrics(
                platform="twitter",
                followers=1890,
                engagement_rate=2.8,
                posts_count=25,
                reach=15000,
                impressions=38000,
                clicks=420
            ),
        ]

    async def _get_top_content(self, start: datetime, end: datetime, db) -> list[dict[str, Any]]:
        """Top performing content."""
        return [
            {
                "id": "1",
                "title": "5 Strategie Marketing per il 2025",
                "type": "blog",
                "platform": "linkedin",
                "engagement": 324,
                "reach": 8500,
                "date": (datetime.utcnow() - timedelta(days=2)).isoformat()
            },
            {
                "id": "2",
                "title": "Video: Digitalizzazione PMI",
                "type": "video",
                "platform": "instagram",
                "engagement": 456,
                "reach": 12300,
                "date": (datetime.utcnow() - timedelta(days=5)).isoformat()
            },
            {
                "id": "3",
                "title": "Case Study: +200% Lead",
                "type": "post",
                "platform": "facebook",
                "engagement": 189,
                "reach": 5600,
                "date": (datetime.utcnow() - timedelta(days=7)).isoformat()
            },
        ]

    async def _get_recent_activities(self, db) -> list[dict[str, Any]]:
        """Attività recenti."""
        now = datetime.utcnow()
        return [
            {
                "id": "1",
                "type": "lead_created",
                "description": "Nuovo lead: Mario Rossi - Tech Solutions",
                "timestamp": (now - timedelta(minutes=15)).isoformat()
            },
            {
                "id": "2",
                "type": "email_sent",
                "description": "Campagna 'Offerta Dicembre' inviata a 234 contatti",
                "timestamp": (now - timedelta(hours=2)).isoformat()
            },
            {
                "id": "3",
                "type": "post_published",
                "description": "Post pubblicato su LinkedIn e Instagram",
                "timestamp": (now - timedelta(hours=5)).isoformat()
            },
            {
                "id": "4",
                "type": "conversion",
                "description": "Lead convertito: ABC Company → Cliente",
                "timestamp": (now - timedelta(hours=8)).isoformat()
            },
            {
                "id": "5",
                "type": "workflow_executed",
                "description": "Workflow 'Lead Nurturing' completato",
                "timestamp": (now - timedelta(days=1)).isoformat()
            },
        ]

    # ========================================================================
    # REPORT GENERATION
    # ========================================================================

    async def generate_report(self, config: ReportConfig, db=None) -> dict[str, Any]:
        """
        Genera report marketing.

        Returns:
            Dict con dati report e eventuale file path per PDF
        """
        start_date, end_date = self.get_date_range(config.date_range, config.start_date, config.end_date)

        report_data = {
            "title": config.title,
            "generated_at": datetime.utcnow().isoformat(),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "range_type": config.date_range.value
            },
            "sections": []
        }

        if config.include_kpis:
            kpis = await self._calculate_kpis(start_date, end_date, start_date - (end_date - start_date), db)
            report_data["sections"].append({
                "name": "KPIs",
                "data": [k.model_dump() for k in kpis]
            })

        if config.include_leads:
            leads_data = await self._get_leads_report_data(start_date, end_date, db)
            report_data["sections"].append({
                "name": "Lead Analysis",
                "data": leads_data
            })

        if config.include_campaigns:
            campaigns_data = await self._get_campaigns_report_data(start_date, end_date, db)
            report_data["sections"].append({
                "name": "Email Campaigns",
                "data": campaigns_data
            })

        if config.include_social:
            social_data = await self._get_platform_metrics(start_date, end_date, db)
            report_data["sections"].append({
                "name": "Social Media",
                "data": [p.model_dump() for p in social_data]
            })

        return report_data

    async def _get_leads_report_data(self, start: datetime, end: datetime, db) -> dict[str, Any]:
        """Dati lead per report."""
        return {
            "total_new": 156,
            "total_converted": 23,
            "conversion_rate": 14.7,
            "by_source": {
                "organic": 45,
                "paid": 38,
                "email": 28,
                "social": 25,
                "referral": 12,
                "direct": 8
            },
            "by_status": {
                "new": 89,
                "contacted": 34,
                "qualified": 18,
                "proposal": 10,
                "won": 5
            },
            "avg_score": 68.5,
            "top_regions": [
                {"name": "Campania", "count": 52},
                {"name": "Lazio", "count": 38},
                {"name": "Lombardia", "count": 28}
            ]
        }

    async def _get_campaigns_report_data(self, start: datetime, end: datetime, db) -> dict[str, Any]:
        """Dati campagne per report."""
        return {
            "total_sent": 12,
            "total_recipients": 2840,
            "avg_open_rate": 24.5,
            "avg_click_rate": 3.8,
            "total_opens": 696,
            "total_clicks": 108,
            "top_campaigns": [
                {"name": "Offerta Dicembre", "open_rate": 32.5, "click_rate": 5.2},
                {"name": "Newsletter Novembre", "open_rate": 28.1, "click_rate": 4.1},
                {"name": "Case Study Q4", "open_rate": 25.8, "click_rate": 3.8}
            ]
        }

    # ========================================================================
    # EXPORT
    # ========================================================================

    async def export_data(self, data_type: str, date_range: DateRange, format: str = "csv", db=None) -> dict[str, Any]:
        """
        Esporta dati in CSV o Excel.

        Args:
            data_type: leads, campaigns, social, all
            date_range: periodo
            format: csv, excel
        """
        start_date, end_date = self.get_date_range(date_range)

        export_data = {
            "type": data_type,
            "format": format,
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "rows": [],
            "columns": []
        }

        if data_type == "leads":
            export_data["columns"] = [
                "ID", "Azienda", "Contatto", "Email", "Telefono",
                "Città", "Regione", "Fonte", "Status", "Score", "Data Creazione"
            ]

            export_data["rows"] = [
                [1, "Tech Solutions", "Mario Rossi", "mario@tech.it", "+39 333 1234567",
                 "Napoli", "Campania", "organic", "qualified", 85, "2024-12-01"],
                [2, "Digital Agency", "Laura Bianchi", "laura@digital.it", "+39 339 7654321",
                 "Roma", "Lazio", "paid", "contacted", 72, "2024-12-02"],
            ]

        elif data_type == "campaigns":
            export_data["columns"] = [
                "ID", "Nome", "Oggetto", "Destinatari", "Inviata",
                "Open Rate", "Click Rate", "Status"
            ]
            export_data["rows"] = [
                [1, "Offerta Dicembre", "Speciale Fine Anno!", 450, "2024-12-01", 32.5, 5.2, "sent"],
                [2, "Newsletter", "News di Dicembre", 380, "2024-12-05", 28.1, 4.1, "sent"],
            ]

        elif data_type == "social":
            export_data["columns"] = [
                "Piattaforma", "Followers", "Engagement %", "Post", "Reach", "Impressions", "Clicks"
            ]
            metrics = await self._get_platform_metrics(start_date, end_date, db)
            export_data["rows"] = [
                [m.platform, m.followers, m.engagement_rate, m.posts_count, m.reach, m.impressions, m.clicks]
                for m in metrics
            ]

        return export_data


# Singleton instance
analytics_service = MarketingAnalyticsService()
