"""
Competitor Monitoring Service.

Features:
- Tracciamento competitor
- Monitoraggio social
- Analisi contenuti
- Alert su attività
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


# ============================================================================
# MODELS
# ============================================================================

class CompetitorStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class SocialPlatform(str, Enum):
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    YOUTUBE = "youtube"


class Competitor(BaseModel):
    """Definizione competitor."""
    id: str
    name: str
    website: str = ""
    description: str = ""
    social_profiles: Dict[str, str] = Field(default_factory=dict)  # platform -> url
    keywords: List[str] = Field(default_factory=list)
    status: CompetitorStatus = CompetitorStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_checked: Optional[datetime] = None
    notes: str = ""


class CompetitorMetrics(BaseModel):
    """Metriche competitor."""
    competitor_id: str
    platform: str
    followers: int = 0
    engagement_rate: float = 0.0
    posts_per_week: float = 0.0
    avg_likes: int = 0
    avg_comments: int = 0
    growth_rate: float = 0.0  # % crescita followers
    recorded_at: datetime = Field(default_factory=datetime.utcnow)


class CompetitorContent(BaseModel):
    """Contenuto competitor rilevato."""
    id: str
    competitor_id: str
    platform: str
    content_type: str  # post, article, video, story
    title: str = ""
    content_preview: str = ""
    url: str = ""
    engagement: int = 0
    published_at: datetime
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    keywords_matched: List[str] = Field(default_factory=list)


class CompetitorAlert(BaseModel):
    """Alert attività competitor."""
    id: str
    competitor_id: str
    alert_type: str  # new_content, growth_spike, keyword_match
    title: str
    description: str
    severity: str = "info"  # info, warning, important
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read: bool = False


# ============================================================================
# COMPETITOR SERVICE
# ============================================================================

class CompetitorMonitoringService:
    """
    Service per monitoraggio competitor.
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

        self._competitors: Dict[str, Competitor] = {}
        self._metrics: Dict[str, List[CompetitorMetrics]] = {}
        self._content: Dict[str, List[CompetitorContent]] = {}
        self._alerts: List[CompetitorAlert] = []
        self._initialized = True
        logger.info("competitor_service_initialized")

    # ========================================================================
    # COMPETITOR CRUD
    # ========================================================================

    def create_competitor(self, competitor: Competitor) -> Competitor:
        """Crea nuovo competitor."""
        self._competitors[competitor.id] = competitor
        self._metrics[competitor.id] = []
        self._content[competitor.id] = []
        logger.info(f"competitor_created: {competitor.id} - {competitor.name}")
        return competitor

    def get_competitor(self, competitor_id: str) -> Optional[Competitor]:
        return self._competitors.get(competitor_id)

    def list_competitors(self, status: Optional[CompetitorStatus] = None) -> List[Competitor]:
        competitors = list(self._competitors.values())
        if status:
            competitors = [c for c in competitors if c.status == status]
        return competitors

    def update_competitor(self, competitor_id: str, updates: Dict[str, Any]) -> Optional[Competitor]:
        competitor = self._competitors.get(competitor_id)
        if not competitor:
            return None

        for key, value in updates.items():
            if hasattr(competitor, key) and key not in ['id', 'created_at']:
                setattr(competitor, key, value)

        self._competitors[competitor_id] = competitor
        return competitor

    def delete_competitor(self, competitor_id: str) -> bool:
        if competitor_id in self._competitors:
            del self._competitors[competitor_id]
            if competitor_id in self._metrics:
                del self._metrics[competitor_id]
            if competitor_id in self._content:
                del self._content[competitor_id]
            return True
        return False

    # ========================================================================
    # METRICS
    # ========================================================================

    def add_metrics(self, metrics: CompetitorMetrics):
        """Aggiungi metriche per competitor."""
        if metrics.competitor_id not in self._metrics:
            self._metrics[metrics.competitor_id] = []

        self._metrics[metrics.competitor_id].append(metrics)

        # Update last_checked
        competitor = self._competitors.get(metrics.competitor_id)
        if competitor:
            competitor.last_checked = datetime.utcnow()

    def get_metrics(self, competitor_id: str, platform: Optional[str] = None, days: int = 30) -> List[CompetitorMetrics]:
        """Ottieni metriche competitor."""
        if competitor_id not in self._metrics:
            return []

        cutoff = datetime.utcnow() - timedelta(days=days)
        metrics = [m for m in self._metrics[competitor_id] if m.recorded_at >= cutoff]

        if platform:
            metrics = [m for m in metrics if m.platform == platform]

        return sorted(metrics, key=lambda m: m.recorded_at, reverse=True)

    def get_latest_metrics(self, competitor_id: str) -> Dict[str, CompetitorMetrics]:
        """Ottieni ultime metriche per ogni piattaforma."""
        if competitor_id not in self._metrics:
            return {}

        latest = {}
        for m in sorted(self._metrics[competitor_id], key=lambda x: x.recorded_at, reverse=True):
            if m.platform not in latest:
                latest[m.platform] = m

        return latest

    # ========================================================================
    # CONTENT TRACKING
    # ========================================================================

    def add_content(self, content: CompetitorContent):
        """Aggiungi contenuto rilevato."""
        if content.competitor_id not in self._content:
            self._content[content.competitor_id] = []

        self._content[content.competitor_id].append(content)

        # Genera alert se match keywords
        if content.keywords_matched:
            self._create_alert(
                competitor_id=content.competitor_id,
                alert_type="keyword_match",
                title=f"Keyword match: {', '.join(content.keywords_matched[:3])}",
                description=f"Nuovo contenuto con keywords rilevanti: {content.title or content.content_preview[:50]}",
                severity="info"
            )

    def get_content(self, competitor_id: str, platform: Optional[str] = None, limit: int = 20) -> List[CompetitorContent]:
        """Ottieni contenuti competitor."""
        if competitor_id not in self._content:
            return []

        content = self._content[competitor_id]

        if platform:
            content = [c for c in content if c.platform == platform]

        return sorted(content, key=lambda c: c.detected_at, reverse=True)[:limit]

    def get_all_recent_content(self, days: int = 7, limit: int = 50) -> List[CompetitorContent]:
        """Ottieni tutti i contenuti recenti di tutti i competitor."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        all_content = []

        for content_list in self._content.values():
            for c in content_list:
                if c.detected_at >= cutoff:
                    all_content.append(c)

        return sorted(all_content, key=lambda c: c.detected_at, reverse=True)[:limit]

    # ========================================================================
    # ALERTS
    # ========================================================================

    def _create_alert(self, competitor_id: str, alert_type: str, title: str, description: str, severity: str = "info"):
        """Crea nuovo alert."""
        alert = CompetitorAlert(
            id=f"alert_{uuid.uuid4().hex[:12]}",
            competitor_id=competitor_id,
            alert_type=alert_type,
            title=title,
            description=description,
            severity=severity
        )
        self._alerts.append(alert)

    def get_alerts(self, unread_only: bool = False, limit: int = 50) -> List[CompetitorAlert]:
        """Ottieni alerts."""
        alerts = self._alerts
        if unread_only:
            alerts = [a for a in alerts if not a.read]
        return sorted(alerts, key=lambda a: a.created_at, reverse=True)[:limit]

    def mark_alert_read(self, alert_id: str) -> bool:
        """Marca alert come letto."""
        for alert in self._alerts:
            if alert.id == alert_id:
                alert.read = True
                return True
        return False

    def mark_all_alerts_read(self):
        """Marca tutti gli alert come letti."""
        for alert in self._alerts:
            alert.read = True

    # ========================================================================
    # COMPARISON
    # ========================================================================

    def get_comparison(self, competitor_ids: List[str] = None) -> Dict[str, Any]:
        """Confronta metriche tra competitor."""
        if not competitor_ids:
            competitor_ids = list(self._competitors.keys())

        comparison = {
            "competitors": [],
            "platforms": {}
        }

        for comp_id in competitor_ids:
            competitor = self._competitors.get(comp_id)
            if not competitor:
                continue

            latest = self.get_latest_metrics(comp_id)

            comp_data = {
                "id": comp_id,
                "name": competitor.name,
                "metrics": {}
            }

            for platform, metrics in latest.items():
                comp_data["metrics"][platform] = {
                    "followers": metrics.followers,
                    "engagement_rate": metrics.engagement_rate,
                    "posts_per_week": metrics.posts_per_week
                }

                # Aggregate by platform
                if platform not in comparison["platforms"]:
                    comparison["platforms"][platform] = []
                comparison["platforms"][platform].append({
                    "name": competitor.name,
                    "followers": metrics.followers,
                    "engagement": metrics.engagement_rate
                })

            comparison["competitors"].append(comp_data)

        return comparison

    def get_summary(self) -> Dict[str, Any]:
        """Sommario monitoraggio competitor."""
        active = len([c for c in self._competitors.values() if c.status == CompetitorStatus.ACTIVE])
        unread_alerts = len([a for a in self._alerts if not a.read])
        recent_content = len(self.get_all_recent_content(days=7))

        return {
            "total_competitors": len(self._competitors),
            "active_competitors": active,
            "unread_alerts": unread_alerts,
            "recent_content_count": recent_content,
            "last_updated": datetime.utcnow().isoformat()
        }


# Singleton instance
competitor_service = CompetitorMonitoringService()
