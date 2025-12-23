"""
Acquisition Pipeline Router - Unified Client Acquisition API

Endpoints:
- POST /acquisition/launch - Launch complete acquisition campaign
- GET /acquisition/stats - Real-time conversion statistics
- GET /acquisition/pipeline - Pipeline funnel data
- POST /acquisition/follow-up - Schedule follow-up actions
"""

from datetime import datetime, timedelta

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.core.api.dependencies.database import get_db
from app.domain.marketing.models import Lead, LeadStatus

logger = structlog.get_logger(__name__)

router = APIRouter(
    prefix="/acquisition",
    tags=["Acquisition Pipeline"],
    dependencies=[Depends(get_current_admin_user)]
)


# ============================================================================
# SCHEMAS
# ============================================================================

class AcquisitionTarget(BaseModel):
    """Target configuration for acquisition campaign."""
    sector: str = Field(..., description="Business sector (ristorante, hotel, etc.)")
    city: str = Field(..., description="Target city")
    radius_km: int = Field(default=25, ge=5, le=100)
    budget_level: str = Field(default="organic", description="organic, small, aggressive")
    follow_up_days: list[int] = Field(default=[3, 7])


class LeadData(BaseModel):
    """Lead data from Google Places."""
    place_id: str
    name: str
    address: str
    phone: str | None = None
    website: str | None = None
    email: str | None = None
    rating: float | None = None
    reviews_count: int = 0
    score: int = 0
    grade: str = "C"
    email_subject: str | None = None
    email_body: str | None = None


class LaunchCampaignRequest(BaseModel):
    """Request to launch acquisition campaign."""
    target: AcquisitionTarget
    leads: list[LeadData]
    send_emails: bool = True
    schedule_follow_ups: bool = True


class LaunchCampaignResponse(BaseModel):
    """Response from campaign launch."""
    campaign_id: str
    leads_saved: int
    emails_queued: int
    follow_ups_scheduled: int
    next_follow_up: datetime | None = None


class AcquisitionStats(BaseModel):
    """Real-time acquisition statistics."""
    # Funnel metrics
    total_leads_found: int
    leads_enriched: int
    emails_sent: int
    emails_opened: int
    emails_clicked: int
    meetings_scheduled: int
    customers_converted: int

    # Rates
    enrichment_rate: float
    open_rate: float
    click_rate: float
    conversion_rate: float

    # Time-based
    today_leads: int
    week_leads: int
    month_leads: int

    # Grade distribution
    grade_a_count: int
    grade_b_count: int
    grade_c_count: int

    # Recent activity
    last_campaign: datetime | None = None


class PipelineStage(BaseModel):
    """Single pipeline stage."""
    name: str
    count: int
    percentage: float
    leads: list[dict]


class PipelineResponse(BaseModel):
    """Full pipeline funnel."""
    stages: list[PipelineStage]
    total_value: float
    avg_conversion_time_days: float


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/launch", response_model=LaunchCampaignResponse)
async def launch_acquisition_campaign(
    request: LaunchCampaignRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    🚀 Launch a complete acquisition campaign.

    This endpoint:
    1. Saves all leads to CRM
    2. Queues personalized emails
    3. Schedules follow-up reminders
    4. Tracks everything for analytics
    """
    campaign_id = f"ACQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    leads_saved = 0
    emails_queued = 0
    follow_ups_scheduled = 0

    logger.info(
        "acquisition_campaign_launch",
        campaign_id=campaign_id,
        sector=request.target.sector,
        city=request.target.city,
        leads_count=len(request.leads)
    )

    try:
        for lead_data in request.leads:
            # 1. Save lead to CRM
            try:
                existing = db.execute(
                    text("SELECT id FROM leads WHERE place_id = :pid"),
                    {"pid": lead_data.place_id}
                ).fetchone()

                if not existing:
                    result = db.execute(
                        text("""
                            INSERT INTO leads (
                                company, contact_name, email, phone, address,
                                website, industry, status, lead_score, source,
                                place_id, rating, tags, created_at, updated_at
                            ) VALUES (
                                :company, :contact_name, :email, :phone, :address,
                                :website, :industry, :status, :score, :source,
                                :place_id, :rating, :tags, NOW(), NOW()
                            )
                            RETURNING id
                        """),
                        {
                            "company": lead_data.name,
                            "contact_name": None,
                            "email": lead_data.email,
                            "phone": lead_data.phone,
                            "address": lead_data.address,
                            "website": lead_data.website,
                            "industry": request.target.sector,
                            "status": "new",
                            "score": lead_data.score,
                            "source": "acquisition-wizard",
                            "place_id": lead_data.place_id,
                            "rating": lead_data.rating,
                            "tags": f'["{campaign_id}", "grade-{lead_data.grade}"]'
                        }
                    )
                    lead_id = result.fetchone()[0]
                    leads_saved += 1
                else:
                    lead_id = existing[0]

                # 2. Queue email if provided
                if request.send_emails and lead_data.email_body:
                    # Track email in acquisition_emails table or queue
                    db.execute(
                        text("""
                            INSERT INTO lead_activities (
                                lead_id, activity_type, description, created_at
                            ) VALUES (
                                :lead_id, 'email_queued', :description, NOW()
                            )
                        """),
                        {
                            "lead_id": lead_id,
                            "description": f"Email queued: {lead_data.email_subject}"
                        }
                    )
                    emails_queued += 1

                # 3. Schedule follow-ups
                if request.schedule_follow_ups:
                    for days in request.target.follow_up_days:
                        follow_up_date = datetime.now() + timedelta(days=days)
                        db.execute(
                            text("""
                                INSERT INTO lead_activities (
                                    lead_id, activity_type, description,
                                    scheduled_at, created_at
                                ) VALUES (
                                    :lead_id, 'follow_up_scheduled', :description,
                                    :scheduled_at, NOW()
                                )
                            """),
                            {
                                "lead_id": lead_id,
                                "description": f"Follow-up #{days} days",
                                "scheduled_at": follow_up_date
                            }
                        )
                        follow_ups_scheduled += 1

            except Exception as e:
                logger.error("lead_save_error", error=str(e), lead=lead_data.name)
                continue

        db.commit()

        # Calculate next follow-up
        next_follow_up = None
        if request.target.follow_up_days:
            next_follow_up = datetime.now() + timedelta(days=min(request.target.follow_up_days))

        logger.info(
            "acquisition_campaign_completed",
            campaign_id=campaign_id,
            leads_saved=leads_saved,
            emails_queued=emails_queued
        )

        return LaunchCampaignResponse(
            campaign_id=campaign_id,
            leads_saved=leads_saved,
            emails_queued=emails_queued,
            follow_ups_scheduled=follow_ups_scheduled,
            next_follow_up=next_follow_up
        )

    except Exception as e:
        db.rollback()
        logger.error("acquisition_campaign_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=AcquisitionStats)
async def get_acquisition_stats(
    db: Session = Depends(get_db)
):
    """
    📊 Get real-time acquisition statistics.

    Returns funnel metrics, conversion rates, and grade distribution.
    """
    try:
        # Total leads (all sources)
        total_leads = db.execute(
            text("SELECT COUNT(*) FROM leads")
        ).scalar() or 0

        # Leads by grade (from tags)
        grade_a = db.execute(
            text("SELECT COUNT(*) FROM leads WHERE tags::text LIKE '%grade-A%'")
        ).scalar() or 0
        grade_b = db.execute(
            text("SELECT COUNT(*) FROM leads WHERE tags::text LIKE '%grade-B%'")
        ).scalar() or 0
        grade_c = db.execute(
            text("SELECT COUNT(*) FROM leads WHERE tags::text LIKE '%grade-C%'")
        ).scalar() or 0

        # Time-based counts
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        today_leads = db.execute(
            text("SELECT COUNT(*) FROM leads WHERE DATE(created_at) = :today"),
            {"today": today}
        ).scalar() or 0

        week_leads = db.execute(
            text("SELECT COUNT(*) FROM leads WHERE created_at >= :week_ago"),
            {"week_ago": week_ago}
        ).scalar() or 0

        month_leads = db.execute(
            text("SELECT COUNT(*) FROM leads WHERE created_at >= :month_ago"),
            {"month_ago": month_ago}
        ).scalar() or 0

        # Email stats - use 0 defaults since these columns may not exist
        emails_sent = 0
        emails_opened = 0
        emails_clicked = 0
        try:
            emails_sent = db.execute(
                text("SELECT COUNT(*) FROM email_campaigns WHERE status = 'SENT'")
            ).scalar() or 0
        except Exception:
            db.rollback()  # CRITICAL: Reset transaction state after failed query

        # Customers converted (WON status)
        customers = db.execute(
            text("SELECT COUNT(*) FROM leads WHERE status = 'WON'")
        ).scalar() or 0

        # Calculate rates
        enrichment_rate = (grade_a + grade_b) / total_leads * 100 if total_leads > 0 else 0
        open_rate = emails_opened / emails_sent * 100 if emails_sent > 0 else 0
        click_rate = emails_clicked / emails_opened * 100 if emails_opened > 0 else 0
        conversion_rate = customers / total_leads * 100 if total_leads > 0 else 0

        # Last lead
        last_campaign = db.execute(
            text("""
                SELECT created_at FROM leads
                ORDER BY created_at DESC LIMIT 1
            """)
        ).scalar()

        return AcquisitionStats(
            total_leads_found=total_leads,
            leads_enriched=grade_a + grade_b,
            emails_sent=emails_sent,
            emails_opened=emails_opened,
            emails_clicked=emails_clicked,
            # Meetings: Count leads in CONTACTED or NEGOTIATION phase
            meetings_scheduled=db.query(Lead).filter(
                Lead.status.in_([LeadStatus.CONTACTED, LeadStatus.NEGOTIATION, LeadStatus.PROPOSAL_SENT])
            ).count(),
            customers_converted=customers,
            enrichment_rate=round(enrichment_rate, 1),
            open_rate=round(open_rate, 1),
            click_rate=round(click_rate, 1),
            conversion_rate=round(conversion_rate, 1),
            today_leads=today_leads,
            week_leads=week_leads,
            month_leads=month_leads,
            grade_a_count=grade_a,
            grade_b_count=grade_b,
            grade_c_count=grade_c,
            last_campaign=last_campaign
        )

    except Exception as e:
        logger.error("acquisition_stats_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline", response_model=PipelineResponse)
async def get_acquisition_pipeline(
    db: Session = Depends(get_db)
):
    """
    🔄 Get acquisition pipeline funnel.

    Returns leads organized by stage with conversion metrics.
    """
    try:
        # Define pipeline stages (use correct enum values)
        stages = [
            ("NEW", "Nuovi Lead"),
            ("CONTACTED", "Contattati"),
            ("QUALIFIED", "Qualificati"),
            ("PROPOSAL_SENT", "Proposta Inviata"),
            ("NEGOTIATION", "In Trattativa"),
            ("WON", "Clienti"),
        ]

        pipeline_stages = []
        total_leads = db.execute(text("SELECT COUNT(*) FROM leads")).scalar() or 1

        for status, label in stages:
            count = db.execute(
                text("SELECT COUNT(*) FROM leads WHERE status = :status"),
                {"status": status}
            ).scalar() or 0

            # Get sample leads for this stage
            leads_data = db.execute(
                text("""
                    SELECT id, company_name, score, created_at
                    FROM leads WHERE status = :status
                    ORDER BY created_at DESC LIMIT 5
                """),
                {"status": status}
            ).fetchall()

            leads_list = [
                {
                    "id": row[0],
                    "company": row[1],
                    "score": row[2],
                    "created_at": row[3].isoformat() if row[3] else None
                }
                for row in leads_data
            ]

            pipeline_stages.append(PipelineStage(
                name=label,
                count=count,
                percentage=round(count / total_leads * 100, 1),
                leads=leads_list
            ))

        # Calculate average conversion time
        avg_time = db.execute(
            text("""
                SELECT AVG(EXTRACT(EPOCH FROM (updated_at - created_at)) / 86400)
                FROM leads WHERE status = 'WON'
            """)
        ).scalar() or 0

        return PipelineResponse(
            stages=pipeline_stages,
            # Calculate total value from custom_fields 'value' or default estimate for WON deals
            total_value=0,  # Value calculation requires CRM integration or custom_fields logic
            avg_conversion_time_days=round(float(avg_time), 1)
        )

    except Exception as e:
        logger.error("pipeline_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/follow-up/{lead_id}")
async def schedule_follow_up(
    lead_id: int,
    days: int = 3,
    message: str = "Follow-up reminder",
    db: Session = Depends(get_db)
):
    """
    ⏰ Schedule a follow-up for a specific lead.
    """
    try:
        follow_up_date = datetime.now() + timedelta(days=days)

        db.execute(
            text("""
                INSERT INTO lead_activities (
                    lead_id, activity_type, description, scheduled_at, created_at
                ) VALUES (
                    :lead_id, 'follow_up_scheduled', :message, :scheduled_at, NOW()
                )
            """),
            {
                "lead_id": lead_id,
                "message": message,
                "scheduled_at": follow_up_date
            }
        )
        db.commit()

        return {
            "success": True,
            "lead_id": lead_id,
            "scheduled_at": follow_up_date.isoformat(),
            "message": message
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AUTO-PILOT MODE - The Hunter-Killer Loop
# ============================================================================

class AutoPilotRequest(BaseModel):
    """Request for autonomous acquisition mode."""
    sector: str = Field(..., description="Target sector (ristorante, hotel, etc.)")
    city: str = Field(..., description="Target city")
    min_score: int = Field(default=75, ge=50, le=100, description="Minimum score to auto-save")
    max_results: int = Field(default=20, ge=5, le=50, description="Max leads to process")
    add_to_campaign: str | None = Field(default=None, description="Campaign name to add high-score leads")


class AutoPilotResult(BaseModel):
    """Result of auto-pilot acquisition run."""
    searched: int
    enriched: int
    qualified: int
    saved: int
    campaign_added: int
    leads: list[dict]


@router.post("/auto-pilot", response_model=AutoPilotResult)
async def run_auto_pilot(
    request: AutoPilotRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    🤖 THE HUNTER-KILLER LOOP - Autonomous Lead Acquisition

    This endpoint runs the complete acquisition pipeline automatically:
    1. Search leads by sector/city via Google Places
    2. Enrich each lead (email, social, score)
    3. Auto-save leads with score >= min_score
    4. Optionally add to a welcome campaign

    Perfect for hands-off lead generation.
    """
    from .lead_enrichment_service import LeadEnrichmentService

    service = LeadEnrichmentService(db)
    results = {
        "searched": 0,
        "enriched": 0,
        "qualified": 0,
        "saved": 0,
        "campaign_added": 0,
        "leads": []
    }

    try:
        # 1. SEARCH - Find leads
        query = f"{request.sector} {request.city}"
        logger.info("auto_pilot_search", query=query, max_results=request.max_results)

        places = await service.search_google_places(
            query=query,
            location=f"{request.city}, Italia",
            radius_km=25
        )
        results["searched"] = len(places)

        # 2. ENRICH & SCORE each lead
        for place in places[:request.max_results]:
            try:
                enriched = await service.enrich_place(place)
                results["enriched"] += 1

                score = enriched.get("score", 0)
                lead_data = {
                    "place_id": place.get("place_id"),
                    "name": place.get("name"),
                    "address": place.get("address"),
                    "phone": enriched.get("phone") or place.get("phone"),
                    "website": enriched.get("website") or place.get("website"),
                    "email": enriched.get("email"),
                    "rating": place.get("rating"),
                    "reviews_count": place.get("reviews_count", 0),
                    "score": score,
                    "grade": enriched.get("grade", "C"),
                    "qualified": score >= request.min_score
                }

                # 3. AUTO-SAVE if score meets threshold
                if score >= request.min_score:
                    results["qualified"] += 1

                    # Check if already exists
                    existing = db.execute(
                        text("SELECT id FROM leads WHERE company_name = :name OR email = :email LIMIT 1"),
                        {"name": lead_data["name"], "email": lead_data.get("email") or ""}
                    ).fetchone()

                    if not existing:
                        db.execute(
                            text("""
                                INSERT INTO leads (
                                    company_name, contact_name, email, phone, website,
                                    city, region, source, status, industry, score,
                                    created_at, updated_at
                                ) VALUES (
                                    :company_name, '', :email, :phone, :website,
                                    :city, 'Campania', 'GOOGLE_MAPS', 'NEW', :industry, :score,
                                    NOW(), NOW()
                                )
                            """),
                            {
                                "company_name": lead_data["name"],
                                "email": lead_data.get("email") or "",
                                "phone": lead_data.get("phone") or "",
                                "website": lead_data.get("website") or "",
                                "city": request.city,
                                "industry": request.sector,
                                "score": score
                            }
                        )
                        results["saved"] += 1
                        lead_data["action"] = "SAVED"
                    else:
                        lead_data["action"] = "DUPLICATE"
                else:
                    lead_data["action"] = "SKIPPED_LOW_SCORE"

                results["leads"].append(lead_data)

            except Exception as e:
                logger.warning("auto_pilot_enrich_error", place=place.get("name"), error=str(e))
                continue

        db.commit()

        # 4. Add to campaign if specified (background)
        if request.add_to_campaign and results["saved"] > 0:
            # Queue campaign addition as background task
            background_tasks.add_task(
                _add_leads_to_campaign,
                db,
                [l for l in results["leads"] if l.get("action") == "SAVED"],
                request.add_to_campaign
            )
            results["campaign_added"] = results["saved"]

        logger.info("auto_pilot_complete", **{k: v for k, v in results.items() if k != "leads"})

        return AutoPilotResult(**results)

    except Exception as e:
        logger.error("auto_pilot_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.close()


async def _add_leads_to_campaign(db: Session, leads: list[dict], campaign_name: str):
    """Background task to add leads to a welcome campaign."""
    try:
        # Find or create campaign
        campaign = db.execute(
            text("SELECT id FROM email_campaigns WHERE name = :name LIMIT 1"),
            {"name": campaign_name}
        ).fetchone()

        if not campaign:
            # Create welcome campaign
            result = db.execute(
                text("""
                    INSERT INTO email_campaigns (
                        name, subject, html_content, text_content,
                        target_region, is_active, ai_generated, created_at, updated_at
                    ) VALUES (
                        :name, 'Benvenuto!', '<p>Ciao!</p>', 'Ciao!',
                        'Campania', true, false, NOW(), NOW()
                    ) RETURNING id
                """),
                {"name": campaign_name}
            )
            campaign_id = result.scalar()
        else:
            campaign_id = campaign[0]

        # Log activity for each lead
        for lead in leads:
            db.execute(
                text("""
                    INSERT INTO lead_activities (
                        lead_id, activity_type, description, created_at
                    ) SELECT id, 'campaign_added', :desc, NOW()
                    FROM leads WHERE company_name = :name LIMIT 1
                """),
                {"name": lead["name"], "desc": f"Added to campaign: {campaign_name}"}
            )

        db.commit()
        logger.info("leads_added_to_campaign", campaign=campaign_name, count=len(leads))

    except Exception as e:
        logger.error("campaign_add_error", error=str(e))

