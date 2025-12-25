"""
Marketing Scheduler Management API - Manual controls and monitoring.

Endpoints per gestire lo scheduler automatico di generazione contenuti marketing.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.domain.auth.admin_models import AdminUser
from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.infrastructure.scheduler import (
    marketing_content_scheduler,
    trigger_marketing_generation
)

import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/scheduler", tags=["Marketing Scheduler"])


class SchedulerStatusResponse(BaseModel):
    """Status dello scheduler marketing."""
    is_running: bool
    enabled: bool
    schedule: str
    platforms: list[str]
    post_count: int
    story_count: int
    video_count: int
    use_pro_quality: bool
    auto_publish: bool
    next_run: Optional[str] = None
    topics_count: int


class TriggerGenerationRequest(BaseModel):
    """Request per trigger manuale generazione."""
    custom_topic: Optional[str] = Field(None, description="Topic personalizzato per la generazione")


class TriggerGenerationResponse(BaseModel):
    """Response trigger generazione."""
    success: bool
    message: str
    campaign_id: Optional[str] = None
    posts_created: Optional[int] = None
    topic: Optional[str] = None
    generation_time: Optional[int] = None
    cost: Optional[float] = None
    scheduled_posts: Optional[list] = None


@router.get("/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Ottieni lo status corrente dello scheduler marketing.

    Mostra:
    - Se è attivo
    - Configurazione (schedule, platforms, quality)
    - Prossima esecuzione schedulata
    """
    scheduler = marketing_content_scheduler

    # Get next run time
    next_run = None
    if scheduler._is_running and scheduler.scheduler.get_job('marketing_daily_generation'):
        job = scheduler.scheduler.get_job('marketing_daily_generation')
        if job.next_run_time:
            next_run = job.next_run_time.isoformat()

    return SchedulerStatusResponse(
        is_running=scheduler._is_running,
        enabled=scheduler.enabled,
        schedule=f"{scheduler.schedule_hour:02d}:{scheduler.schedule_minute:02d} CET",
        platforms=scheduler.platforms,
        post_count=scheduler.post_count,
        story_count=scheduler.story_count,
        video_count=scheduler.video_count,
        use_pro_quality=scheduler.use_pro_quality,
        auto_publish=scheduler.auto_publish,
        next_run=next_run,
        topics_count=len(scheduler.topics)
    )


@router.post("/trigger", response_model=TriggerGenerationResponse)
async def trigger_generation(
    request: TriggerGenerationRequest = None,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Trigger manuale della generazione batch content.

    Utile per:
    - Testing
    - Generazione extra oltre la schedulazione quotidiana
    - Topic personalizzati per eventi/campagne speciali

    Genera immediatamente:
    - 4 post (1 per platform: Instagram, Facebook, TikTok, LinkedIn)
    - 3 stories (Instagram/Facebook)
    - 1 video (15s Reel/TikTok)
    """
    logger.info("manual_generation_triggered",
               user_id=current_user.id,
               custom_topic=request.custom_topic)

    try:
        result = await trigger_marketing_generation(custom_topic=request.custom_topic)

        return TriggerGenerationResponse(
            success=result.get("success", False),
            message=result.get("message", ""),
            campaign_id=result.get("campaign_id"),
            posts_created=result.get("posts_created"),
            topic=result.get("topic"),
            generation_time=result.get("generation_time"),
            cost=result.get("cost"),
            scheduled_posts=result.get("scheduled_posts", [])
        )

    except Exception as e:
        logger.error("trigger_generation_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


@router.post("/start")
async def start_scheduler(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Avvia lo scheduler marketing (se disabilitato).
    """
    scheduler = marketing_content_scheduler

    if scheduler._is_running:
        return {"success": False, "message": "Scheduler already running"}

    try:
        await scheduler.start()
        logger.info("scheduler_started_manually", user_id=current_user.id)
        return {"success": True, "message": "Scheduler started successfully"}
    except Exception as e:
        logger.error("scheduler_start_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start scheduler: {str(e)}"
        )


@router.post("/stop")
async def stop_scheduler(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Ferma lo scheduler marketing.
    """
    scheduler = marketing_content_scheduler

    if not scheduler._is_running:
        return {"success": False, "message": "Scheduler not running"}

    try:
        await scheduler.stop()
        logger.info("scheduler_stopped_manually", user_id=current_user.id)
        return {"success": True, "message": "Scheduler stopped successfully"}
    except Exception as e:
        logger.error("scheduler_stop_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop scheduler: {str(e)}"
        )


@router.get("/topics")
async def get_topics(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Ottieni i topic configurati per la rotazione automatica.
    """
    scheduler = marketing_content_scheduler

    return {
        "topics": scheduler.topics,
        "count": len(scheduler.topics),
        "current_day": datetime.utcnow().weekday(),
        "today_topic_index": datetime.utcnow().weekday() % len(scheduler.topics)
    }


# ============================================================================
# WEEK CALENDAR ENDPOINT
# ============================================================================

class ScheduledItemResponse(BaseModel):
    """Item schedulato per il calendario."""
    id: str
    title: str
    type: str  # 'post', 'email', 'video'
    time: str  # HH:MM format
    platforms: Optional[list[str]] = None
    scheduled_date: Optional[str] = None


@router.get("/week", response_model=list[ScheduledItemResponse])
async def get_week_schedule(
    start: str,
    end: str,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Ottieni gli item schedulati per un range di date.

    Args:
        start: Data inizio (YYYY-MM-DD)
        end: Data fine (YYYY-MM-DD)

    Returns:
        Lista di item schedulati nel range
    """
    from sqlalchemy import text
    from app.core.api.dependencies.database import get_db
    from sqlalchemy.orm import Session

    # Get database session - usa dependency injection corretta se possibile, altrimenti fallback
    from app.infrastructure.database import SessionLocal
    db = SessionLocal()

    try:
        # Parse dates
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")

        items = []

        # Try to fetch from scheduled_posts table
        try:
            result = db.execute(
                text("""
                    SELECT id, content, media_type, scheduled_at, platforms
                    FROM scheduled_posts
                    WHERE scheduled_at >= :start_date
                      AND scheduled_at <= :end_date
                      AND status IN ('scheduled', 'publishing')
                    ORDER BY scheduled_at ASC
                    LIMIT 50
                """),
                {"start_date": start_date, "end_date": end_date}
            ).fetchall()

            for row in result:
                post_id, content, media_type, scheduled_at, platforms = row
                items.append(ScheduledItemResponse(
                    id=str(post_id),
                    title=content[:50] if content else "Post",
                    type="video" if media_type in ("video", "reel") else "post",
                    time=scheduled_at.strftime("%H:%M") if scheduled_at else "09:00",
                    platforms=platforms if isinstance(platforms, list) else [],
                    scheduled_date=scheduled_at.strftime("%Y-%m-%d") if scheduled_at else None
                ))
        except Exception as e:
            logger.warning("scheduled_posts_query_failed", error=str(e))

        # Try to fetch from email_campaigns table
        try:
            result = db.execute(
                text("""
                    SELECT id, name, scheduled_date
                    FROM email_campaigns
                    WHERE scheduled_date >= :start_date
                      AND scheduled_date <= :end_date
                      AND is_sent = false
                    ORDER BY scheduled_date ASC
                    LIMIT 20
                """),
                {"start_date": start_date, "end_date": end_date}
            ).fetchall()

            for row in result:
                campaign_id, name, scheduled_date = row
                items.append(ScheduledItemResponse(
                    id=f"email-{campaign_id}",
                    title=name[:50] if name else "Email Campaign",
                    type="email",
                    time=scheduled_date.strftime("%H:%M") if scheduled_date else "10:00",
                    platforms=None,
                    scheduled_date=scheduled_date.strftime("%Y-%m-%d") if scheduled_date else None
                ))
        except Exception as e:
            logger.warning("email_campaigns_query_failed", error=str(e))
            db.rollback()

        # If no items found, return empty list (frontend shows mock data)
        return items

    except Exception as e:
        logger.error("get_week_schedule_error", error=str(e))
        return []  # Return empty instead of error, frontend has fallback
    finally:
        db.close()
