"""
WhatsApp API Router - Endpoints for WhatsApp messaging.
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
import structlog

from app.core.api.dependencies.database import get_db
from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.core.config import settings

from .service import WhatsAppService, get_whatsapp_service
from .models import WhatsAppMessage, WhatsAppMessageStatus
from .schemas import (
    SendTemplateRequest,
    SendTextRequest,
    SendBulkRequest,
    SendTemplateResponse,
    BulkSendResponse,
    MessageResponse,
    MessagesListResponse,
    MessageStatusResponse,
    TemplatesListResponse,
    WebhookPayload
)

logger = structlog.get_logger(__name__)

router = APIRouter(
    prefix="/whatsapp",
    tags=["WhatsApp"],
    dependencies=[Depends(get_current_admin_user)]
)


# =============================================================================
# HEALTH CHECK (no auth required)
# =============================================================================

@router.get("/health", include_in_schema=False)
async def whatsapp_health():
    """Check if WhatsApp is configured."""
    return {
        "configured": bool(
            settings.WHATSAPP_PHONE_NUMBER_ID and
            settings.WHATSAPP_ACCESS_TOKEN
        ),
        "api_version": settings.WHATSAPP_API_VERSION
    }


# =============================================================================
# SEND ENDPOINTS
# =============================================================================

@router.post("/send", response_model=SendTemplateResponse)
async def send_template_message(
    request: SendTemplateRequest,
    db: Session = Depends(get_db)
):
    """
    📤 Send a WhatsApp template message.

    Template messages are pre-approved by WhatsApp and can be
    sent at any time (no 24h window restriction).

    Use this for:
    - Welcome messages
    - Appointment confirmations
    - Marketing campaigns
    - Follow-up notifications
    """
    service = get_whatsapp_service(db)

    try:
        result = await service.send_template_message(request)

        return SendTemplateResponse(
            success=result.success,
            data=MessageResponse(
                success=result.success,
                message_id=result.message_id,
                phone=result.phone,
                status="sent" if result.success else "failed",
                error=result.error
            )
        )
    finally:
        await service.close()


@router.post("/send-text", response_model=SendTemplateResponse)
async def send_text_message(
    request: SendTextRequest,
    db: Session = Depends(get_db)
):
    """
    📝 Send a text message (24h window only).

    Text messages can only be sent within 24 hours of
    receiving a message from the user.

    For initiating conversations, use template messages instead.
    """
    service = get_whatsapp_service(db)

    try:
        result = await service.send_text_message(request)

        return SendTemplateResponse(
            success=result.success,
            data=MessageResponse(
                success=result.success,
                message_id=result.message_id,
                phone=result.phone,
                status="sent" if result.success else "failed",
                error=result.error
            )
        )
    finally:
        await service.close()


@router.post("/send-bulk", response_model=BulkSendResponse)
async def send_bulk_messages(
    request: SendBulkRequest,
    db: Session = Depends(get_db)
):
    """
    📤📤 Send template message to multiple recipients.

    Rate limited to prevent API throttling.
    Maximum 100 recipients per request.
    """
    service = get_whatsapp_service(db)

    try:
        results = await service.send_bulk_template(
            phones=request.phones,
            template_name=request.template_name,
            language=request.language,
            components=request.components,
            campaign_id=request.campaign_id
        )

        sent = sum(1 for r in results if r.success)
        failed = len(results) - sent

        return BulkSendResponse(
            success=sent > 0,
            total=len(results),
            sent=sent,
            failed=failed,
            results=[
                MessageResponse(
                    success=r.success,
                    message_id=r.message_id,
                    phone=r.phone,
                    status="sent" if r.success else "failed",
                    error=r.error
                )
                for r in results
            ]
        )
    finally:
        await service.close()


# =============================================================================
# TEMPLATES
# =============================================================================

@router.get("/templates", response_model=TemplatesListResponse)
async def get_templates(
    db: Session = Depends(get_db)
):
    """
    📋 Get list of approved WhatsApp message templates.

    Only templates with 'APPROVED' status can be used for sending.
    """
    service = get_whatsapp_service(db)

    try:
        templates = await service.get_templates()

        return TemplatesListResponse(
            success=True,
            data=templates
        )
    finally:
        await service.close()


# =============================================================================
# MESSAGE HISTORY
# =============================================================================

@router.get("/messages", response_model=MessagesListResponse)
async def get_messages(
    lead_id: Optional[int] = None,
    campaign_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    📜 Get WhatsApp message history.

    Filter by lead, campaign, or status.
    """
    service = get_whatsapp_service(db)
    offset = (page - 1) * page_size

    messages = service.get_messages(
        lead_id=lead_id,
        campaign_id=campaign_id,
        status=status,
        limit=page_size,
        offset=offset
    )

    # Get total count for pagination
    total_query = db.query(WhatsAppMessage)
    if lead_id:
        total_query = total_query.filter(WhatsAppMessage.lead_id == lead_id)
    if campaign_id:
        total_query = total_query.filter(WhatsAppMessage.campaign_id == campaign_id)
    if status:
        total_query = total_query.filter(WhatsAppMessage.status == status)
    total = total_query.count()

    return MessagesListResponse(
        success=True,
        data=[
            MessageStatusResponse(
                id=m.id,
                waba_message_id=m.waba_message_id,
                phone=m.phone_number,
                template_name=m.template_name,
                status=m.status,
                sent_at=m.sent_at,
                delivered_at=m.delivered_at,
                read_at=m.read_at,
                error=m.error_message
            )
            for m in messages
        ],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/stats")
async def get_stats(
    campaign_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    📊 Get WhatsApp messaging statistics.
    """
    service = get_whatsapp_service(db)
    stats = service.get_stats(campaign_id)

    return {
        "success": True,
        "data": stats
    }


# =============================================================================
# WEBHOOK (No auth - verified by token)
# =============================================================================

# Create separate router for webhook (no auth)
webhook_router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Webhook"])


@webhook_router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """
    🔐 Webhook verification endpoint.

    Called by Meta when setting up webhook subscription.
    Must return the challenge token if verification succeeds.
    """
    if hub_mode == "subscribe":
        if hub_verify_token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
            logger.info("whatsapp_webhook_verified")
            return int(hub_challenge)
        else:
            logger.warning("whatsapp_webhook_verification_failed")
            raise HTTPException(status_code=403, detail="Verification failed")

    raise HTTPException(status_code=400, detail="Invalid request")


@webhook_router.post("/webhook")
async def handle_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    📥 Receive webhook events from WhatsApp.

    Handles:
    - Message status updates (sent, delivered, read, failed)
    - Incoming messages (future: for chatbot)
    """
    try:
        payload = await request.json()

        logger.info("whatsapp_webhook_received", payload_object=payload.get("object"))

        # Process message status updates
        service = get_whatsapp_service(db)

        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                # Handle status updates
                statuses = value.get("statuses", [])
                for status_update in statuses:
                    message_id = status_update.get("id")
                    status = status_update.get("status")
                    timestamp_str = status_update.get("timestamp")

                    # Parse timestamp
                    timestamp = None
                    if timestamp_str:
                        try:
                            timestamp = datetime.fromtimestamp(int(timestamp_str))
                        except (ValueError, TypeError):
                            pass

                    # Get error info if failed
                    error_code = None
                    error_message = None
                    errors = status_update.get("errors", [])
                    if errors:
                        error_code = str(errors[0].get("code", ""))
                        error_message = errors[0].get("title", "")

                    service.update_message_status(
                        waba_message_id=message_id,
                        status=status,
                        timestamp=timestamp,
                        error_code=error_code,
                        error_message=error_message
                    )

                # Chatbot message handling (Phase 3)
                # Process incoming messages: value.get("messages", [])

        return {"status": "ok"}

    except Exception as e:
        logger.error("whatsapp_webhook_error", error=str(e))
        # Always return 200 to acknowledge receipt
        return {"status": "error", "message": str(e)}
