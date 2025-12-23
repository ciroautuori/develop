"""
Webhook API Router.

Gestione webhook per integrazioni esterne.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
import uuid

from app.domain.marketing.webhook_service import (
    webhook_service,
    Webhook,
    WebhookEvent,
    WebhookStatus,
)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class WebhookCreate(BaseModel):
    name: str
    url: str
    events: List[WebhookEvent]
    headers: dict = Field(default_factory=dict)


class WebhookUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    events: Optional[List[WebhookEvent]] = None
    headers: Optional[dict] = None


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/")
async def list_webhooks(status: Optional[str] = None):
    """Lista tutti i webhook."""
    status_enum = WebhookStatus(status) if status else None
    webhooks = webhook_service.list_webhooks(status_enum)
    return [
        {
            "id": w.id,
            "name": w.name,
            "url": w.url,
            "events": [e.value for e in w.events],
            "status": w.status.value,
            "success_count": w.success_count,
            "failure_count": w.failure_count,
            "last_triggered": w.last_triggered.isoformat() if w.last_triggered else None,
            "created_at": w.created_at.isoformat()
        }
        for w in webhooks
    ]


@router.post("/")
async def create_webhook(data: WebhookCreate):
    """Crea nuovo webhook."""
    webhook = Webhook(
        id=f"wh_{uuid.uuid4().hex[:12]}",
        name=data.name,
        url=data.url,
        events=data.events,
        headers=data.headers
    )

    created = webhook_service.create_webhook(webhook)
    return {
        "id": created.id,
        "name": created.name,
        "url": created.url,
        "events": [e.value for e in created.events],
        "secret": created.secret,  # Mostra solo alla creazione
        "status": created.status.value
    }


@router.get("/{webhook_id}")
async def get_webhook(webhook_id: str):
    """Ottieni dettagli webhook."""
    webhook = webhook_service.get_webhook(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return {
        "id": webhook.id,
        "name": webhook.name,
        "url": webhook.url,
        "events": [e.value for e in webhook.events],
        "headers": webhook.headers,
        "status": webhook.status.value,
        "success_count": webhook.success_count,
        "failure_count": webhook.failure_count,
        "consecutive_failures": webhook.consecutive_failures,
        "last_triggered": webhook.last_triggered.isoformat() if webhook.last_triggered else None,
        "created_at": webhook.created_at.isoformat()
    }


@router.put("/{webhook_id}")
async def update_webhook(webhook_id: str, data: WebhookUpdate):
    """Aggiorna webhook."""
    updates = data.model_dump(exclude_unset=True)
    webhook = webhook_service.update_webhook(webhook_id, updates)

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return {"status": "updated", "id": webhook_id}


@router.delete("/{webhook_id}")
async def delete_webhook(webhook_id: str):
    """Elimina webhook."""
    if not webhook_service.delete_webhook(webhook_id):
        raise HTTPException(status_code=404, detail="Webhook not found")
    return {"status": "deleted", "id": webhook_id}


@router.post("/{webhook_id}/toggle")
async def toggle_webhook(webhook_id: str):
    """Attiva/disattiva webhook."""
    webhook = webhook_service.toggle_webhook(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return {"status": webhook.status.value, "id": webhook_id}


@router.post("/{webhook_id}/test")
async def test_webhook(webhook_id: str):
    """Testa webhook con payload di prova."""
    try:
        delivery = await webhook_service.test_webhook(webhook_id)
        return {
            "success": delivery.success,
            "response_status": delivery.response_status,
            "response_body": delivery.response_body,
            "duration_ms": delivery.duration_ms,
            "error": delivery.error
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{webhook_id}/deliveries")
async def get_deliveries(webhook_id: str, limit: int = Query(20, ge=1, le=100)):
    """Ottieni log invii per webhook."""
    deliveries = webhook_service.get_deliveries(webhook_id, limit)
    return [
        {
            "id": d.id,
            "event": d.event.value,
            "success": d.success,
            "response_status": d.response_status,
            "duration_ms": d.duration_ms,
            "created_at": d.created_at.isoformat(),
            "error": d.error
        }
        for d in deliveries
    ]


# ============================================================================
# EVENTS INFO
# ============================================================================

@router.get("/meta/events")
async def get_available_events():
    """Lista eventi disponibili per webhook."""
    return [
        {"value": "lead.created", "label": "Lead Creato"},
        {"value": "lead.updated", "label": "Lead Aggiornato"},
        {"value": "lead.converted", "label": "Lead Convertito"},
        {"value": "campaign.sent", "label": "Campagna Inviata"},
        {"value": "email.opened", "label": "Email Aperta"},
        {"value": "email.clicked", "label": "Email Cliccata"},
        {"value": "post.published", "label": "Post Pubblicato"},
        {"value": "workflow.completed", "label": "Workflow Completato"},
        {"value": "ab_test.completed", "label": "A/B Test Completato"},
    ]
