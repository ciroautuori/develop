"""
Marketing API Routers - Calendario Editoriale & Social Media

Endpoints per:
- Gestione post programmati (CRUD)
- Vista calendario (giorno/settimana/mese)
- Pubblicazione immediata
- Bulk scheduling

🔒 TUTTI GLI ENDPOINT RICHIEDONO AUTENTICAZIONE ADMIN!
"""

from datetime import datetime, timedelta

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.domain.marketing.models import PostStatus, ScheduledPost
from app.domain.marketing.schemas import (
    BulkScheduleRequest,
    BulkScheduleResponse,
    CalendarViewResponse,
    ScheduledPostCreate,
    ScheduledPostListResponse,
    ScheduledPostResponse,
    ScheduledPostUpdate,
)
from app.infrastructure.database import get_db
from app.infrastructure.scheduler import post_scheduler

logger = structlog.get_logger(__name__)

# 🔒 Router con autenticazione ADMIN obbligatoria per tutti gli endpoint
router = APIRouter(
    prefix="/marketing/calendar",
    tags=["Marketing Calendar"],
    dependencies=[Depends(get_current_admin_user)]  # 🔐 RICHIEDE ADMIN AUTH
)


# ============================================================================
# SCHEDULED POSTS CRUD
# ============================================================================

@router.post("/posts", response_model=ScheduledPostResponse)
async def create_scheduled_post(
    data: ScheduledPostCreate,
    db: Session = Depends(get_db)
):
    """Crea un nuovo post programmato."""
    try:
        post = ScheduledPost(
            content=data.content,
            title=data.title,
            hashtags=data.hashtags,
            mentions=data.mentions,
            media_urls=data.media_urls,
            media_type=data.media_type,
            platforms=data.platforms,
            scheduled_at=data.scheduled_at,
            status=PostStatus.SCHEDULED,
            ai_generated=data.ai_generated,
            ai_prompt=data.ai_prompt,
            ai_model=data.ai_model,
            campaign_id=data.campaign_id,
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        # Schedula pubblicazione
        await post_scheduler.schedule_post(post.id, post.scheduled_at)

        logger.info("scheduled_post_created", post_id=post.id, scheduled_at=post.scheduled_at.isoformat())

        return post

    except Exception as e:
        db.rollback()
        logger.error("create_post_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts", response_model=ScheduledPostListResponse)
def list_scheduled_posts(
    status: PostStatus | None = None,
    platform: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Lista post programmati con filtri."""
    try:
        query = db.query(ScheduledPost)

        # Filtri
        if status:
            query = query.filter(ScheduledPost.status == status)
        if start_date:
            query = query.filter(ScheduledPost.scheduled_at >= start_date)
        if end_date:
            query = query.filter(ScheduledPost.scheduled_at <= end_date)

        # Count totale
        total = query.count()

        # Paginazione
        posts = query.order_by(ScheduledPost.scheduled_at.asc())\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()

        return ScheduledPostListResponse(
            items=posts,
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error("list_posts_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts/{post_id}", response_model=ScheduledPostResponse)
def get_scheduled_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Ottieni dettagli singolo post."""
    post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@router.put("/posts/{post_id}", response_model=ScheduledPostResponse)
async def update_scheduled_post(
    post_id: int,
    data: ScheduledPostUpdate,
    db: Session = Depends(get_db)
):
    """Aggiorna post programmato."""
    post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.status == PostStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Cannot modify published post")

    # Aggiorna campi
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)

    # Reschedula se data cambiata
    if data.scheduled_at:
        await post_scheduler.cancel_post(post_id)
        await post_scheduler.schedule_post(post_id, post.scheduled_at)

    logger.info("scheduled_post_updated", post_id=post_id)

    return post


@router.delete("/posts/{post_id}")
async def delete_scheduled_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Elimina post programmato."""
    post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Cancella job schedulato
    await post_scheduler.cancel_post(post_id)

    db.delete(post)
    db.commit()

    logger.info("scheduled_post_deleted", post_id=post_id)

    return {"status": "deleted", "post_id": post_id}


# ============================================================================
# CALENDAR VIEWS
# ============================================================================

@router.get("/view/week", response_model=CalendarViewResponse)
def get_week_view(
    date: datetime | None = None,
    db: Session = Depends(get_db)
):
    """Vista settimanale del calendario."""
    if not date:
        date = datetime.utcnow()

    start_of_week = date - timedelta(days=date.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=7)

    return _get_calendar_view(db, start_of_week, end_of_week)


@router.get("/view/month", response_model=CalendarViewResponse)
def get_month_view(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Vista mensile del calendario."""
    start_of_month = datetime(year, month, 1)

    if month == 12:
        end_of_month = datetime(year + 1, 1, 1)
    else:
        end_of_month = datetime(year, month + 1, 1)

    return _get_calendar_view(db, start_of_month, end_of_month)


@router.get("/view/range", response_model=CalendarViewResponse)
def get_range_view(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """Vista per range personalizzato."""
    if end_date <= start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    return _get_calendar_view(db, start_date, end_date)


def _get_calendar_view(
    db: Session,
    start_date: datetime,
    end_date: datetime
) -> CalendarViewResponse:
    """Helper per costruire vista calendario."""
    posts = db.query(ScheduledPost).filter(
        and_(
            ScheduledPost.scheduled_at >= start_date,
            ScheduledPost.scheduled_at < end_date
        )
    ).order_by(ScheduledPost.scheduled_at.asc()).all()

    total_scheduled = sum(1 for p in posts if p.status == PostStatus.SCHEDULED)
    total_published = sum(1 for p in posts if p.status == PostStatus.PUBLISHED)
    total_failed = sum(1 for p in posts if p.status == PostStatus.FAILED)

    platforms_stats = {}
    for post in posts:
        for platform in post.platforms:
            platforms_stats[platform] = platforms_stats.get(platform, 0) + 1

    return CalendarViewResponse(
        posts=posts,
        start_date=start_date,
        end_date=end_date,
        total_scheduled=total_scheduled,
        total_published=total_published,
        total_failed=total_failed,
        platforms_stats=platforms_stats
    )


# ============================================================================
# ACTIONS
# ============================================================================

@router.post("/posts/{post_id}/publish-now")
async def publish_post_now(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Pubblica immediatamente un post."""
    post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.status == PostStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Post already published")

    await post_scheduler.cancel_post(post_id)
    await post_scheduler._publish_post(post_id)

    db.refresh(post)

    return {
        "status": "published",
        "post_id": post_id,
        "platform_results": post.platform_results
    }


@router.post("/posts/{post_id}/cancel")
async def cancel_scheduled_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Annulla post programmato."""
    post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.status == PostStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Post already published")

    await post_scheduler.cancel_post(post_id)

    post.status = PostStatus.CANCELLED
    db.commit()

    logger.info("scheduled_post_cancelled", post_id=post_id)

    return {"status": "cancelled", "post_id": post_id}


@router.post("/posts/{post_id}/reschedule")
async def reschedule_post(
    post_id: int,
    new_scheduled_at: datetime,
    db: Session = Depends(get_db)
):
    """Riprogramma un post a nuova data."""
    post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.status == PostStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Cannot reschedule published post")

    await post_scheduler.cancel_post(post_id)

    post.scheduled_at = new_scheduled_at
    post.status = PostStatus.SCHEDULED
    post.retry_count = 0
    post.error_message = None
    db.commit()

    await post_scheduler.schedule_post(post_id, new_scheduled_at)

    logger.info("scheduled_post_rescheduled", post_id=post_id, new_date=new_scheduled_at.isoformat())

    return {
        "status": "rescheduled",
        "post_id": post_id,
        "new_scheduled_at": new_scheduled_at.isoformat()
    }


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@router.post("/bulk/schedule", response_model=BulkScheduleResponse)
async def bulk_schedule_posts(
    data: BulkScheduleRequest,
    db: Session = Depends(get_db)
):
    """Scheduling bulk di più post."""
    created = 0
    failed = 0
    errors = []

    for post_data in data.posts:
        try:
            post = ScheduledPost(
                content=post_data.content,
                title=post_data.title,
                hashtags=post_data.hashtags,
                mentions=post_data.mentions,
                media_urls=post_data.media_urls,
                media_type=post_data.media_type,
                platforms=post_data.platforms,
                scheduled_at=post_data.scheduled_at,
                status=PostStatus.SCHEDULED,
                ai_generated=post_data.ai_generated,
                ai_prompt=post_data.ai_prompt,
                ai_model=post_data.ai_model,
            )

            db.add(post)
            db.flush()

            await post_scheduler.schedule_post(post.id, post.scheduled_at)
            created += 1

        except Exception as e:
            failed += 1
            errors.append(str(e))

    db.commit()

    logger.info("bulk_schedule_completed", created=created, failed=failed)

    return BulkScheduleResponse(
        created=created,
        failed=failed,
        errors=errors
    )


# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/stats")
def get_calendar_stats(
    db: Session = Depends(get_db)
):
    """Statistiche generali del calendario."""
    now = datetime.utcnow()

    # Post per status
    status_results = db.query(
        ScheduledPost.status, func.count(ScheduledPost.id)
    ).group_by(ScheduledPost.status).all()

    status_counts = {row[0].value: row[1] for row in status_results}

    # Post prossima settimana
    next_week = now + timedelta(days=7)
    upcoming_week = db.query(func.count(ScheduledPost.id)).filter(
        and_(
            ScheduledPost.scheduled_at >= now,
            ScheduledPost.scheduled_at <= next_week,
            ScheduledPost.status == PostStatus.SCHEDULED
        )
    ).scalar() or 0

    # Post per piattaforma (ultimi 30 giorni)
    last_month = now - timedelta(days=30)
    posts = db.query(ScheduledPost).filter(
        and_(
            ScheduledPost.published_at >= last_month,
            ScheduledPost.status == PostStatus.PUBLISHED
        )
    ).all()

    platform_stats = {}
    for post in posts:
        for platform in post.platforms:
            platform_stats[platform] = platform_stats.get(platform, 0) + 1

    return {
        "status_counts": status_counts,
        "upcoming_week": upcoming_week,
        "platform_stats_last_30_days": platform_stats,
        "total_posts": sum(status_counts.values())
    }


# ============================================================================
# AI CONTENT GENERATION - GLI AGENTI FANNO TUTTO DA SOLI!
# ============================================================================

import os

import httpx
from pydantic import BaseModel, Field


class AIGenerateCampaignRequest(BaseModel):
    """Request per far generare all'AI un'intera campagna social."""
    campaign_name: str = Field(..., description="Nome campagna")
    campaign_description: str = Field(..., description="Descrizione dettagliata della campagna, obiettivi, prodotto")
    platforms: list[str] = Field(default=["instagram", "facebook", "linkedin"], description="Piattaforme target")
    start_date: datetime = Field(..., description="Data inizio campagna")
    end_date: datetime = Field(..., description="Data fine campagna - estrazione/chiusura")
    posts_per_week: int = Field(default=5, ge=1, le=14, description="Post a settimana")
    tone: str = Field(default="exciting", description="Tono: exciting, professional, casual, urgent")
    language: str = Field(default="it", description="Lingua: it, en, es")
    hashtags: list[str] = Field(default_factory=list, description="Hashtag obbligatori")

class AIGenerateCampaignResponse(BaseModel):
    """Response campagna generata dall'AI."""
    campaign_name: str
    posts_generated: int
    posts_scheduled: int
    total_days: int
    platforms: list[str]
    ai_model: str
    posts: list[dict]


@router.post("/ai/generate-campaign", response_model=AIGenerateCampaignResponse)
async def ai_generate_campaign(
    data: AIGenerateCampaignRequest,
    db: Session = Depends(get_db)
):
    """
    🤖 GLI AGENTI AI GENERANO UN'INTERA CAMPAGNA SOCIAL!

    L'AI microservice genera automaticamente tutti i post per la campagna,
    li schedula nel calendario editoriale, e li prepara per la pubblicazione.

    Flusso:
    1. Calcola le date di pubblicazione
    2. Chiama AI microservice per generare ogni post
    3. Salva i post nel DB
    4. Schedula la pubblicazione automatica
    """
    ai_url = os.getenv("AI_SERVICE_URL", "http://ai_microservice:8001")
    ai_api_key = os.getenv("AI_SERVICE_API_KEY", "dev-api-key-change-in-production")

    # Calcola numero totale di post
    total_days = (data.end_date - data.start_date).days + 1
    total_posts = (total_days // 7) * data.posts_per_week + min(total_days % 7, data.posts_per_week)

    logger.info("ai_campaign_start",
                campaign=data.campaign_name,
                total_days=total_days,
                expected_posts=total_posts)

    generated_posts = []
    scheduled_posts = []

    # Calcola le date di pubblicazione
    posting_dates = []
    current_date = data.start_date
    posts_this_week = 0
    week_start = current_date

    while current_date <= data.end_date:
        if posts_this_week < data.posts_per_week:
            posting_dates.append(current_date.replace(hour=12, minute=0, second=0))
            posts_this_week += 1

        current_date += timedelta(days=1)

        # Reset counter ogni settimana
        if (current_date - week_start).days >= 7:
            week_start = current_date
            posts_this_week = 0

    # Temi per variazione contenuti
    themes = [
        "lancio_giveaway",
        "feature_highlight",
        "social_proof",
        "tutorial",
        "urgenza",
        "testimonial",
        "behind_scenes",
        "tip_trick",
        "countdown",
        "reminder"
    ]

    async with httpx.AsyncClient(timeout=120.0) as client:
        for i, post_date in enumerate(posting_dates):
            theme = themes[i % len(themes)]
            days_remaining = (data.end_date - post_date).days

            # Costruisci prompt dettagliato per l'AI
            if theme == "lancio_giveaway":
                topic = f"🎁 LANCIO GIVEAWAY: {data.campaign_description}. Data estrazione: {data.end_date.strftime('%d %B %Y')} alle 12:00!"
            elif theme == "urgenza" and days_remaining <= 3:
                topic = f"⚠️ ULTIMISSIMI GIORNI! Solo {days_remaining} giorni per partecipare al giveaway. {data.campaign_description}"
            elif theme == "countdown":
                topic = f"⏰ COUNTDOWN: Mancano {days_remaining} giorni all'estrazione! {data.campaign_description}"
            elif theme == "feature_highlight":
                topic = f"✨ FEATURE SPOTLIGHT: Scopri le funzionalità incredibili. {data.campaign_description}"
            elif theme == "social_proof":
                topic = f"🔥 I numeri parlano chiaro! Migliaia di utenti hanno già scelto questa soluzione. {data.campaign_description}"
            elif theme == "tutorial":
                topic = f"💡 TUTORIAL: Come funziona in 3 semplici step. {data.campaign_description}"
            elif theme == "testimonial":
                topic = f"⭐ STORIA DI SUCCESSO: Un utente racconta la sua esperienza. {data.campaign_description}"
            elif theme == "reminder":
                topic = f"📢 REMINDER: Non dimenticare di partecipare! {data.campaign_description}"
            else:
                topic = f"{data.campaign_description}. Tema del giorno: {theme.replace('_', ' ')}"

            # Genera contenuto con AI
            try:
                response = await client.post(
                    f"{ai_url}/api/v1/marketing/content/generate",
                    json={
                        "type": "social",
                        "topic": topic,
                        "tone": data.tone,
                        "platform": data.platforms[i % len(data.platforms)]  # Ruota piattaforme
                    },
                    headers={"Authorization": f"Bearer {ai_api_key}"}
                )

                if response.status_code == 200:
                    ai_response = response.json()
                    content = ai_response.get("content", "")

                    # Aggiungi hashtag obbligatori se non presenti
                    for hashtag in data.hashtags:
                        if hashtag not in content:
                            content += f" {hashtag}"

                    # 🍌 GENERA IMMAGINE CON NANO BANANA / BRANDING
                    image_url = None
                    try:
                        # Brand identity context - COLORI REALI markettina (NO BLU!)
                        BRAND_STYLE = "markettina brand, GOLD (#D4AF37) and BLACK (#0A0A0A) colors, premium luxury aesthetic, modern tech Italian excellence, NO BLUE"

                        # Crea prompt immagine basato sul tema CON BRAND CORRETTO
                        image_prompts = {
                            "lancio_giveaway": f"Exciting giveaway announcement for digital marketing agency, elegant gift boxes with golden ribbons on dark black background, celebration confetti in gold, luxury premium feel, {BRAND_STYLE}",
                            "feature_highlight": f"AI-powered digital marketing feature showcase, futuristic tech interface on dark background, holographic displays with golden accents, premium tech aesthetic, {BRAND_STYLE}",
                            "social_proof": f"Business success celebration, growing chart with golden bars on dark background, digital transformation visual, gold trophy, luxury corporate, {BRAND_STYLE}",
                            "tutorial": f"Step by step AI marketing tutorial, numbered golden steps on black background, elegant tech infographic, clean modern design, {BRAND_STYLE}",
                            "urgenza": f"Urgent limited time offer, elegant countdown clock with golden hands on dark background, premium urgency visual, luxury feel, {BRAND_STYLE}",
                            "testimonial": f"Happy business owner success story, professional portrait, golden rating stars on dark elegant background, corporate setting, {BRAND_STYLE}",
                            "behind_scenes": f"Modern tech office behind the scenes, team working on AI projects, dark elegant environment with golden light accents, {BRAND_STYLE}",
                            "tip_trick": f"Pro marketing tips, golden lightbulb innovation idea on black background, AI brain concept, elegant helpful advice visual, {BRAND_STYLE}",
                            "countdown": f"Exciting countdown timer, elegant golden numbers on dark background, anticipation building visual, premium event approaching, {BRAND_STYLE}",
                            "reminder": f"Friendly digital reminder, elegant golden bell notification on dark background, modern calendar with gold accents, {BRAND_STYLE}"
                        }
                        image_prompt = image_prompts.get(theme, f"Professional AI marketing visual, digital transformation concept, dark elegant theme with golden accents, {BRAND_STYLE}")

                        # Aggiungi contesto specifico della campagna
                        image_prompt += f". Campaign context: {data.campaign_description[:100]}. NO TEXT OR LOGOS IN IMAGE. Focus on visual metaphors for AI-powered business growth."

                        logger.info("generating_campaign_image", theme=theme, prompt=image_prompt[:100])

                        image_response = await client.post(
                            f"{ai_url}/api/v1/marketing/image/generate",
                            json={
                                "prompt": image_prompt,
                                "style": "professional",
                                "platform": data.platforms[i % len(data.platforms)],
                                "apply_branding": True,
                                "provider": "auto"
                            },
                            headers={"Authorization": f"Bearer {ai_api_key}"},
                            timeout=90.0  # Image generation può essere lenta
                        )

                        if image_response.status_code == 200:
                            image_data = image_response.json()
                            image_url = image_data.get("image_url")
                            logger.info("campaign_image_generated",
                                       post_index=i+1,
                                       theme=theme,
                                       image_url=image_url,
                                       provider=image_data.get("metadata", {}).get("provider", "unknown"))
                        else:
                            logger.warning("image_generation_failed",
                                          status=image_response.status_code,
                                          theme=theme)
                    except Exception as img_error:
                        logger.warning("image_generation_error", error=str(img_error), theme=theme)

                    # Crea post nel DB CON IMMAGINE
                    post = ScheduledPost(
                        content=content,
                        title=f"{data.campaign_name} - {theme.replace('_', ' ').title()} - Day {i+1}",
                        hashtags=data.hashtags,
                        platforms=data.platforms,
                        scheduled_at=post_date,
                        status=PostStatus.SCHEDULED,
                        ai_generated=True,
                        ai_prompt=topic,
                        ai_model=ai_response.get("provider", "huggingface"),
                        media_urls=[image_url] if image_url else [],  # 🖼️ IMMAGINE GENERATA!
                        media_type=PostType.IMAGE if image_url else PostType.TEXT,
                    )

                    db.add(post)
                    db.flush()

                    # Schedula pubblicazione
                    await post_scheduler.schedule_post(post.id, post.scheduled_at)

                    generated_posts.append({
                        "id": post.id,
                        "date": post_date.isoformat(),
                        "theme": theme,
                        "platform": data.platforms[i % len(data.platforms)],
                        "content_preview": content[:200] + "..." if len(content) > 200 else content,
                        "image_url": image_url  # 🖼️ Include image URL in response
                    })
                    scheduled_posts.append(post)

                    logger.info("ai_post_generated",
                               post_id=post.id,
                               theme=theme,
                               has_image=bool(image_url),
                               date=post_date.isoformat())
                else:
                    logger.error("ai_generation_failed",
                                status=response.status_code,
                                theme=theme)

            except Exception as e:
                logger.error("ai_generation_error", error=str(e), theme=theme)
                continue

    db.commit()

    logger.info("ai_campaign_completed",
               campaign=data.campaign_name,
               posts_generated=len(generated_posts),
               posts_scheduled=len(scheduled_posts))

    return AIGenerateCampaignResponse(
        campaign_name=data.campaign_name,
        posts_generated=len(generated_posts),
        posts_scheduled=len(scheduled_posts),
        total_days=total_days,
        platforms=data.platforms,
        ai_model="huggingface",
        posts=generated_posts
    )
