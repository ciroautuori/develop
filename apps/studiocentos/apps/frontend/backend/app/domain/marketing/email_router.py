"""
Email Marketing Router
Endpoints for email campaign management and sending
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.api.dependencies.database import get_db
from app.core.api.dependencies.auth_deps import get_current_admin_user
from .email_service import email_service, EmailMessage, EmailRecipient


router = APIRouter(prefix="/email", tags=["Email Marketing"])


# ============================================================================
# SCHEMAS
# ============================================================================

class SendEmailRequest(BaseModel):
    """Single email send request."""
    to_email: EmailStr
    to_name: Optional[str] = None
    subject: str
    html_content: str
    text_content: Optional[str] = None
    reply_to: Optional[EmailStr] = None


class SendBulkEmailRequest(BaseModel):
    """Bulk email send request."""
    recipients: List[dict]  # List of {email, name, custom_data}
    subject: str
    html_content: str
    text_content: Optional[str] = None
    campaign_name: Optional[str] = None


class SendCampaignRequest(BaseModel):
    """Send existing campaign request."""
    campaign_id: int
    batch_size: int = 50
    delay_seconds: float = 1.0


class CreateCampaignRequest(BaseModel):
    """Create campaign request."""
    name: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    target_region: Optional[str] = None
    target_industry: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    ai_generated: bool = False
    ai_model: Optional[str] = None


class CampaignResponse(BaseModel):
    """Campaign response."""
    id: int
    name: str
    subject: str
    target_region: Optional[str]
    target_industry: Optional[str]
    is_sent: bool
    total_sent: int
    total_opened: int
    total_clicked: int
    open_rate: float
    click_rate: float
    created_at: datetime
    sent_date: Optional[datetime]


class SendResultResponse(BaseModel):
    """Send result response."""
    success: bool
    total_sent: int
    total_failed: int
    provider: str
    details: Optional[List[dict]] = None


class StatsResponse(BaseModel):
    """Campaign statistics response."""
    campaign_id: int
    total_sent: int
    total_delivered: int
    total_opened: int
    total_clicked: int
    total_bounced: int
    total_unsubscribed: int
    open_rate: float
    click_rate: float
    bounce_rate: float


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/send", response_model=SendResultResponse)
async def send_single_email(
    request: SendEmailRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_admin_user)
):
    """
    Send a single email.
    Uses configured provider (SendGrid/Mailgun/SMTP).
    """
    message = EmailMessage(
        to=[EmailRecipient(email=request.to_email, name=request.to_name)],
        subject=request.subject,
        html_content=request.html_content,
        text_content=request.text_content,
        reply_to=request.reply_to
    )

    results = await email_service.send(message)

    success_count = sum(1 for r in results if r.success)
    failed_count = sum(1 for r in results if not r.success)

    return SendResultResponse(
        success=success_count > 0,
        total_sent=success_count,
        total_failed=failed_count,
        provider=results[0].provider if results else "unknown",
        details=[
            {
                "email": r.recipient_email,
                "success": r.success,
                "message_id": r.message_id,
                "error": r.error
            }
            for r in results
        ]
    )


@router.post("/send-bulk", response_model=SendResultResponse)
async def send_bulk_email(
    request: SendBulkEmailRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_admin_user)
):
    """
    Send email to multiple recipients.
    Implements batching for large sends.
    """
    recipients = [
        EmailRecipient(
            email=r.get("email"),
            name=r.get("name"),
            custom_data=r.get("custom_data", {})
        )
        for r in request.recipients
        if r.get("email")
    ]

    if not recipients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid recipients provided"
        )

    message = EmailMessage(
        to=recipients,
        subject=request.subject,
        html_content=request.html_content,
        text_content=request.text_content,
        tags=[request.campaign_name] if request.campaign_name else []
    )

    results = await email_service.send(message)

    success_count = sum(1 for r in results if r.success)
    failed_count = sum(1 for r in results if not r.success)

    return SendResultResponse(
        success=success_count > 0,
        total_sent=success_count,
        total_failed=failed_count,
        provider=results[0].provider if results else "unknown",
        details=[
            {
                "email": r.recipient_email,
                "success": r.success,
                "message_id": r.message_id,
                "error": r.error
            }
            for r in results
        ]
    )


@router.post("/campaigns", response_model=CampaignResponse)
async def create_campaign(
    request: CreateCampaignRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_admin_user)
):
    """Create a new email campaign."""
    insert_query = text("""
        INSERT INTO email_campaigns (
            name, subject, html_content, text_content,
            target_region, target_industry,
            scheduled_date, ai_generated, ai_model,
            is_active, is_sent, total_sent, total_opened, total_clicked,
            created_at, updated_at
        ) VALUES (
            :name, :subject, :html_content, :text_content,
            :target_region, :target_industry,
            :scheduled_date, :ai_generated, :ai_model,
            true, false, 0, 0, 0,
            NOW(), NOW()
        ) RETURNING id
    """)

    result = db.execute(insert_query, {
        "name": request.name,
        "subject": request.subject,
        "html_content": request.html_content,
        "text_content": request.text_content,
        "target_region": request.target_region,
        "target_industry": request.target_industry,
        "scheduled_date": request.scheduled_date,
        "ai_generated": request.ai_generated,
        "ai_model": request.ai_model
    })

    campaign_id = result.scalar()
    db.commit()

    # Get created campaign
    query = text("""
        SELECT id, name, subject, target_region, target_industry,
               is_sent, total_sent, total_opened, total_clicked,
               created_at, sent_date
        FROM email_campaigns WHERE id = :id
    """)
    row = db.execute(query, {"id": campaign_id}).fetchone()

    total_sent = row[6] or 0
    total_opened = row[7] or 0
    total_clicked = row[8] or 0

    return CampaignResponse(
        id=row[0],
        name=row[1],
        subject=row[2],
        target_region=row[3],
        target_industry=row[4],
        is_sent=row[5],
        total_sent=total_sent,
        total_opened=total_opened,
        total_clicked=total_clicked,
        open_rate=round((total_opened / total_sent * 100), 2) if total_sent > 0 else 0,
        click_rate=round((total_clicked / total_sent * 100), 2) if total_sent > 0 else 0,
        created_at=row[9],
        sent_date=row[10]
    )


@router.get("/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    is_sent: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_admin_user)
):
    """List email campaigns."""
    where_clause = ""
    params = {"limit": limit, "offset": offset}

    if is_sent is not None:
        where_clause = "WHERE is_sent = :is_sent"
        params["is_sent"] = is_sent

    query = text(f"""
        SELECT id, name, subject, target_region, target_industry,
               is_sent, total_sent, total_opened, total_clicked,
               created_at, sent_date
        FROM email_campaigns
        {where_clause}
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """)

    rows = db.execute(query, params).fetchall()

    campaigns = []
    for row in rows:
        total_sent = row[6] or 0
        total_opened = row[7] or 0
        total_clicked = row[8] or 0

        campaigns.append(CampaignResponse(
            id=row[0],
            name=row[1],
            subject=row[2],
            target_region=row[3],
            target_industry=row[4],
            is_sent=row[5],
            total_sent=total_sent,
            total_opened=total_opened,
            total_clicked=total_clicked,
            open_rate=round((total_opened / total_sent * 100), 2) if total_sent > 0 else 0,
            click_rate=round((total_clicked / total_sent * 100), 2) if total_sent > 0 else 0,
            created_at=row[9],
            sent_date=row[10]
        ))

    return campaigns


@router.post("/campaigns/{campaign_id}/send")
async def send_campaign(
    campaign_id: int,
    request: Optional[SendCampaignRequest] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_admin_user)
):
    """
    Send email campaign to all targeted leads.
    Runs in background for large campaigns.
    """
    batch_size = request.batch_size if request else 50
    delay_seconds = request.delay_seconds if request else 1.0

    # For now, send synchronously (could be moved to background)
    result = await email_service.send_campaign(
        db=db,
        campaign_id=campaign_id,
        batch_size=batch_size,
        delay_between_batches=delay_seconds
    )

    return result


@router.get("/campaigns/{campaign_id}/stats", response_model=StatsResponse)
async def get_campaign_stats(
    campaign_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_admin_user)
):
    """Get campaign statistics."""
    stats = await email_service.get_campaign_stats(db, campaign_id)

    return StatsResponse(
        campaign_id=stats.campaign_id,
        total_sent=stats.total_sent,
        total_delivered=stats.total_delivered,
        total_opened=stats.total_opened,
        total_clicked=stats.total_clicked,
        total_bounced=stats.total_bounced,
        total_unsubscribed=stats.total_unsubscribed,
        open_rate=stats.open_rate,
        click_rate=stats.click_rate,
        bounce_rate=stats.bounce_rate
    )


@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_admin_user)
):
    """Delete a campaign (soft delete)."""
    update_query = text("""
        UPDATE email_campaigns
        SET is_active = false, updated_at = NOW()
        WHERE id = :campaign_id
    """)
    db.execute(update_query, {"campaign_id": campaign_id})
    db.commit()

    return {"success": True, "message": "Campaign deleted"}


# ============================================================================
# TRACKING ENDPOINTS (PUBLIC - No Auth)
# ============================================================================

@router.get("/track/open/{tracking_id}")
async def track_email_open(
    tracking_id: str,
    db: Session = Depends(get_db)
):
    """
    Track email open event.
    Returns 1x1 transparent pixel.
    """
    await email_service.track_open(db, tracking_id)

    # Return 1x1 transparent GIF
    pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'

    return Response(
        content=pixel,
        media_type="image/gif",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@router.get("/track/click/{tracking_id}")
async def track_email_click(
    tracking_id: str,
    url: str,
    db: Session = Depends(get_db)
):
    """
    Track email click event and redirect to destination URL.
    """
    await email_service.track_click(db, tracking_id, url)

    # Redirect to actual URL
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=url, status_code=302)


@router.post("/unsubscribe/{email}")
async def unsubscribe(
    email: str,
    db: Session = Depends(get_db)
):
    """Unsubscribe email from marketing communications."""
    update_query = text("""
        UPDATE leads
        SET status = 'unsubscribed', updated_at = NOW()
        WHERE email = :email
    """)
    db.execute(update_query, {"email": email})
    db.commit()

    return {"success": True, "message": f"{email} unsubscribed"}


# ============================================================================
# TEST ENDPOINT
# ============================================================================

@router.post("/test")
async def send_test_email(
    to_email: EmailStr,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_admin_user)
):
    """
    Send a test email to verify configuration.
    """
    message = EmailMessage(
        to=[EmailRecipient(email=to_email, name="Test User")],
        subject="🧪 Test Email da StudioCentOS",
        html_content="""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1 style="color: #D4AF37;">✅ Email Test Riuscito!</h1>
            <p>Se stai leggendo questa email, la configurazione è corretta.</p>
            <p><strong>Provider:</strong> Configurato correttamente</p>
            <p><strong>Timestamp:</strong> {timestamp}</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                StudioCentOS - Email Marketing System
            </p>
        </body>
        </html>
        """.format(timestamp=datetime.utcnow().isoformat()),
        text_content="Test email inviata con successo! Timestamp: " + datetime.utcnow().isoformat()
    )

    results = await email_service.send(message)

    return {
        "success": results[0].success if results else False,
        "provider": email_service.provider.value,
        "message_id": results[0].message_id if results and results[0].success else None,
        "error": results[0].error if results and not results[0].success else None
    }
