"""
Competitor Monitoring API Router.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

from app.domain.marketing.competitor_service import (
    competitor_service,
    Competitor,
    CompetitorStatus,
    CompetitorMetrics,
    CompetitorContent,
)

router = APIRouter(prefix="/competitors", tags=["Competitor Monitoring"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class CompetitorCreate(BaseModel):
    name: str
    website: str = ""
    description: str = ""
    social_profiles: dict = Field(default_factory=dict)
    keywords: List[str] = Field(default_factory=list)


class CompetitorUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    social_profiles: Optional[dict] = None
    keywords: Optional[List[str]] = None
    notes: Optional[str] = None


class MetricsInput(BaseModel):
    platform: str
    followers: int = 0
    engagement_rate: float = 0.0
    posts_per_week: float = 0.0
    avg_likes: int = 0
    avg_comments: int = 0


class ContentInput(BaseModel):
    platform: str
    content_type: str
    title: str = ""
    content_preview: str = ""
    url: str = ""
    engagement: int = 0
    published_at: datetime


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/")
async def list_competitors(status: Optional[str] = None):
    """Lista tutti i competitor."""
    status_enum = CompetitorStatus(status) if status else None
    competitors = competitor_service.list_competitors(status_enum)

    result = []
    for c in competitors:
        latest = competitor_service.get_latest_metrics(c.id)
        result.append({
            "id": c.id,
            "name": c.name,
            "website": c.website,
            "status": c.status.value,
            "social_profiles": c.social_profiles,
            "keywords": c.keywords,
            "last_checked": c.last_checked.isoformat() if c.last_checked else None,
            "metrics_summary": {
                platform: {"followers": m.followers, "engagement": m.engagement_rate}
                for platform, m in latest.items()
            }
        })

    return result


@router.get("/summary")
async def get_summary():
    """Ottieni sommario monitoraggio."""
    return competitor_service.get_summary()


@router.post("/")
async def create_competitor(data: CompetitorCreate):
    """Crea nuovo competitor da monitorare."""
    competitor = Competitor(
        id=f"comp_{uuid.uuid4().hex[:12]}",
        name=data.name,
        website=data.website,
        description=data.description,
        social_profiles=data.social_profiles,
        keywords=data.keywords
    )

    created = competitor_service.create_competitor(competitor)
    return {
        "id": created.id,
        "name": created.name,
        "status": created.status.value
    }


@router.get("/{competitor_id}")
async def get_competitor(competitor_id: str):
    """Ottieni dettagli competitor."""
    competitor = competitor_service.get_competitor(competitor_id)
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    latest = competitor_service.get_latest_metrics(competitor_id)
    recent_content = competitor_service.get_content(competitor_id, limit=5)

    return {
        "id": competitor.id,
        "name": competitor.name,
        "website": competitor.website,
        "description": competitor.description,
        "social_profiles": competitor.social_profiles,
        "keywords": competitor.keywords,
        "status": competitor.status.value,
        "notes": competitor.notes,
        "last_checked": competitor.last_checked.isoformat() if competitor.last_checked else None,
        "created_at": competitor.created_at.isoformat(),
        "latest_metrics": {
            platform: m.model_dump() for platform, m in latest.items()
        },
        "recent_content": [
            {
                "id": c.id,
                "platform": c.platform,
                "type": c.content_type,
                "title": c.title,
                "preview": c.content_preview[:100],
                "engagement": c.engagement,
                "published_at": c.published_at.isoformat()
            }
            for c in recent_content
        ]
    }


@router.put("/{competitor_id}")
async def update_competitor(competitor_id: str, data: CompetitorUpdate):
    """Aggiorna competitor."""
    updates = data.model_dump(exclude_unset=True)
    competitor = competitor_service.update_competitor(competitor_id, updates)

    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    return {"status": "updated", "id": competitor_id}


@router.delete("/{competitor_id}")
async def delete_competitor(competitor_id: str):
    """Elimina competitor."""
    if not competitor_service.delete_competitor(competitor_id):
        raise HTTPException(status_code=404, detail="Competitor not found")
    return {"status": "deleted", "id": competitor_id}


# ============================================================================
# METRICS
# ============================================================================

@router.post("/{competitor_id}/metrics")
async def add_metrics(competitor_id: str, data: MetricsInput):
    """Aggiungi metriche per competitor."""
    if not competitor_service.get_competitor(competitor_id):
        raise HTTPException(status_code=404, detail="Competitor not found")

    metrics = CompetitorMetrics(
        competitor_id=competitor_id,
        platform=data.platform,
        followers=data.followers,
        engagement_rate=data.engagement_rate,
        posts_per_week=data.posts_per_week,
        avg_likes=data.avg_likes,
        avg_comments=data.avg_comments
    )

    competitor_service.add_metrics(metrics)
    return {"status": "added"}


@router.get("/{competitor_id}/metrics")
async def get_metrics(
    competitor_id: str,
    platform: Optional[str] = None,
    days: int = Query(30, ge=1, le=365)
):
    """Ottieni metriche competitor."""
    metrics = competitor_service.get_metrics(competitor_id, platform, days)
    return [m.model_dump() for m in metrics]


# ============================================================================
# CONTENT
# ============================================================================

@router.post("/{competitor_id}/content")
async def add_content(competitor_id: str, data: ContentInput):
    """Aggiungi contenuto rilevato."""
    if not competitor_service.get_competitor(competitor_id):
        raise HTTPException(status_code=404, detail="Competitor not found")

    competitor = competitor_service.get_competitor(competitor_id)

    # Check keyword matches
    keywords_matched = []
    content_text = f"{data.title} {data.content_preview}".lower()
    for kw in competitor.keywords:
        if kw.lower() in content_text:
            keywords_matched.append(kw)

    content = CompetitorContent(
        id=f"cnt_{uuid.uuid4().hex[:12]}",
        competitor_id=competitor_id,
        platform=data.platform,
        content_type=data.content_type,
        title=data.title,
        content_preview=data.content_preview,
        url=data.url,
        engagement=data.engagement,
        published_at=data.published_at,
        keywords_matched=keywords_matched
    )

    competitor_service.add_content(content)
    return {"status": "added", "keywords_matched": keywords_matched}


@router.get("/{competitor_id}/content")
async def get_content(
    competitor_id: str,
    platform: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100)
):
    """Ottieni contenuti competitor."""
    content = competitor_service.get_content(competitor_id, platform, limit)
    return [
        {
            "id": c.id,
            "platform": c.platform,
            "type": c.content_type,
            "title": c.title,
            "preview": c.content_preview,
            "url": c.url,
            "engagement": c.engagement,
            "published_at": c.published_at.isoformat(),
            "keywords_matched": c.keywords_matched
        }
        for c in content
    ]


@router.get("/content/recent")
async def get_recent_content(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(50, ge=1, le=100)
):
    """Ottieni contenuti recenti di tutti i competitor."""
    content = competitor_service.get_all_recent_content(days, limit)
    return [
        {
            "id": c.id,
            "competitor_id": c.competitor_id,
            "platform": c.platform,
            "type": c.content_type,
            "title": c.title,
            "preview": c.content_preview[:100],
            "engagement": c.engagement,
            "detected_at": c.detected_at.isoformat()
        }
        for c in content
    ]


# ============================================================================
# ALERTS
# ============================================================================

@router.get("/alerts/")
async def get_alerts(
    unread_only: bool = False,
    limit: int = Query(50, ge=1, le=100)
):
    """Ottieni alert competitor."""
    alerts = competitor_service.get_alerts(unread_only, limit)
    return [
        {
            "id": a.id,
            "competitor_id": a.competitor_id,
            "type": a.alert_type,
            "title": a.title,
            "description": a.description,
            "severity": a.severity,
            "read": a.read,
            "created_at": a.created_at.isoformat()
        }
        for a in alerts
    ]


@router.post("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str):
    """Marca alert come letto."""
    if not competitor_service.mark_alert_read(alert_id):
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "read"}


@router.post("/alerts/read-all")
async def mark_all_read():
    """Marca tutti gli alert come letti."""
    competitor_service.mark_all_alerts_read()
    return {"status": "all_read"}


# ============================================================================
# COMPARISON
# ============================================================================

@router.get("/compare")
async def compare_competitors(ids: str = Query(None, description="Comma-separated competitor IDs")):
    """Confronta metriche tra competitor."""
    competitor_ids = ids.split(",") if ids else None
    return competitor_service.get_comparison(competitor_ids)
