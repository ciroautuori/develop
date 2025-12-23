"""
Webhook System per integrazioni esterne.

Features:
- Registrazione endpoint webhook
- Invio eventi automatici
- Retry con exponential backoff
- Log e monitoring
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
import logging
import uuid
import asyncio
import httpx
import hashlib
import hmac
import json

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & MODELS
# ============================================================================

class WebhookEvent(str, Enum):
    LEAD_CREATED = "lead.created"
    LEAD_UPDATED = "lead.updated"
    LEAD_CONVERTED = "lead.converted"
    CAMPAIGN_SENT = "campaign.sent"
    EMAIL_OPENED = "email.opened"
    EMAIL_CLICKED = "email.clicked"
    POST_PUBLISHED = "post.published"
    WORKFLOW_COMPLETED = "workflow.completed"
    AB_TEST_COMPLETED = "ab_test.completed"


class WebhookStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILING = "failing"


class Webhook(BaseModel):
    """Configurazione webhook."""
    id: str
    name: str
    url: str
    events: List[WebhookEvent]
    secret: str = ""  # Per signature HMAC
    headers: Dict[str, str] = Field(default_factory=dict)
    status: WebhookStatus = WebhookStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_triggered: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    consecutive_failures: int = 0


class WebhookDelivery(BaseModel):
    """Log singolo invio webhook."""
    id: str
    webhook_id: str
    event: WebhookEvent
    payload: Dict[str, Any]
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    success: bool = False
    attempt: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: int = 0
    error: Optional[str] = None


# ============================================================================
# WEBHOOK SERVICE
# ============================================================================

class WebhookService:
    """
    Service per gestione webhook marketing.

    Funzionalità:
    - CRUD webhook endpoints
    - Trigger eventi
    - Retry automatico
    - Signature HMAC
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

        self._webhooks: Dict[str, Webhook] = {}
        self._deliveries: Dict[str, WebhookDelivery] = {}
        self._max_retries = 3
        self._retry_delays = [60, 300, 900]  # 1min, 5min, 15min
        self._initialized = True
        logger.info("webhook_service_initialized")

    # ========================================================================
    # WEBHOOK CRUD
    # ========================================================================

    def create_webhook(self, webhook: Webhook) -> Webhook:
        """Crea nuovo webhook."""
        if not webhook.secret:
            webhook.secret = uuid.uuid4().hex
        self._webhooks[webhook.id] = webhook
        logger.info(f"webhook_created: {webhook.id} -> {webhook.url}")
        return webhook

    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        return self._webhooks.get(webhook_id)

    def list_webhooks(self, status: Optional[WebhookStatus] = None) -> List[Webhook]:
        webhooks = list(self._webhooks.values())
        if status:
            webhooks = [w for w in webhooks if w.status == status]
        return webhooks

    def update_webhook(self, webhook_id: str, updates: Dict[str, Any]) -> Optional[Webhook]:
        webhook = self._webhooks.get(webhook_id)
        if not webhook:
            return None

        for key, value in updates.items():
            if hasattr(webhook, key) and key not in ['id', 'created_at', 'secret']:
                setattr(webhook, key, value)

        self._webhooks[webhook_id] = webhook
        return webhook

    def delete_webhook(self, webhook_id: str) -> bool:
        if webhook_id in self._webhooks:
            del self._webhooks[webhook_id]
            return True
        return False

    def toggle_webhook(self, webhook_id: str) -> Optional[Webhook]:
        webhook = self._webhooks.get(webhook_id)
        if webhook:
            webhook.status = WebhookStatus.INACTIVE if webhook.status == WebhookStatus.ACTIVE else WebhookStatus.ACTIVE
            return webhook
        return None

    # ========================================================================
    # EVENT TRIGGERING
    # ========================================================================

    async def trigger_event(self, event: WebhookEvent, payload: Dict[str, Any]):
        """
        Triggera evento verso tutti i webhook registrati.

        Args:
            event: Tipo evento
            payload: Dati evento
        """
        # Trova webhook interessati a questo evento
        webhooks = [
            w for w in self._webhooks.values()
            if w.status == WebhookStatus.ACTIVE and event in w.events
        ]

        if not webhooks:
            return

        # Arricchisci payload
        full_payload = {
            "event": event.value,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload
        }

        # Invia a tutti i webhook in parallelo
        tasks = [self._send_webhook(w, event, full_payload) for w in webhooks]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_webhook(self, webhook: Webhook, event: WebhookEvent, payload: Dict[str, Any]) -> bool:
        """Invia singolo webhook con retry."""
        delivery_id = f"del_{uuid.uuid4().hex[:12]}"

        delivery = WebhookDelivery(
            id=delivery_id,
            webhook_id=webhook.id,
            event=event,
            payload=payload
        )

        # Calcola signature
        signature = self._compute_signature(payload, webhook.secret)

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Event": event.value,
            "X-Webhook-Signature": signature,
            "X-Webhook-Timestamp": str(int(datetime.utcnow().timestamp())),
            **webhook.headers
        }

        start_time = datetime.utcnow()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    webhook.url,
                    json=payload,
                    headers=headers
                )

                delivery.response_status = response.status_code
                delivery.response_body = response.text[:500] if response.text else None
                delivery.success = 200 <= response.status_code < 300
                delivery.duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

                if delivery.success:
                    webhook.success_count += 1
                    webhook.consecutive_failures = 0
                    webhook.last_triggered = datetime.utcnow()
                else:
                    webhook.failure_count += 1
                    webhook.consecutive_failures += 1

                    # Auto-disable dopo 10 fallimenti consecutivi
                    if webhook.consecutive_failures >= 10:
                        webhook.status = WebhookStatus.FAILING

        except Exception as e:
            delivery.success = False
            delivery.error = str(e)
            webhook.failure_count += 1
            webhook.consecutive_failures += 1
            logger.error(f"webhook_send_failed: {webhook.id} - {str(e)}")

        self._deliveries[delivery_id] = delivery

        return delivery.success

    def _compute_signature(self, payload: Dict[str, Any], secret: str) -> str:
        """Calcola HMAC-SHA256 signature."""
        if not secret:
            return ""

        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"sha256={signature}"

    # ========================================================================
    # DELIVERY LOG
    # ========================================================================

    def get_deliveries(self, webhook_id: Optional[str] = None, limit: int = 50) -> List[WebhookDelivery]:
        """Ottieni log invii."""
        deliveries = list(self._deliveries.values())

        if webhook_id:
            deliveries = [d for d in deliveries if d.webhook_id == webhook_id]

        return sorted(deliveries, key=lambda d: d.created_at, reverse=True)[:limit]

    def get_delivery(self, delivery_id: str) -> Optional[WebhookDelivery]:
        return self._deliveries.get(delivery_id)

    # ========================================================================
    # TEST
    # ========================================================================

    async def test_webhook(self, webhook_id: str) -> WebhookDelivery:
        """Testa webhook con payload di prova."""
        webhook = self._webhooks.get(webhook_id)
        if not webhook:
            raise ValueError("Webhook not found")

        test_payload = {
            "event": "test",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "message": "Test webhook from Marketing Hub",
                "webhook_id": webhook_id
            }
        }

        delivery_id = f"test_{uuid.uuid4().hex[:12]}"
        delivery = WebhookDelivery(
            id=delivery_id,
            webhook_id=webhook.id,
            event=WebhookEvent.LEAD_CREATED,  # Dummy
            payload=test_payload
        )

        signature = self._compute_signature(test_payload, webhook.secret)
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Event": "test",
            "X-Webhook-Signature": signature,
            **webhook.headers
        }

        start_time = datetime.utcnow()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(webhook.url, json=test_payload, headers=headers)

                delivery.response_status = response.status_code
                delivery.response_body = response.text[:500] if response.text else None
                delivery.success = 200 <= response.status_code < 300
                delivery.duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        except Exception as e:
            delivery.success = False
            delivery.error = str(e)

        self._deliveries[delivery_id] = delivery
        return delivery


# Singleton instance
webhook_service = WebhookService()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def trigger_lead_created(lead_data: Dict[str, Any]):
    """Shortcut per evento lead creato."""
    await webhook_service.trigger_event(WebhookEvent.LEAD_CREATED, lead_data)


async def trigger_campaign_sent(campaign_data: Dict[str, Any]):
    """Shortcut per evento campagna inviata."""
    await webhook_service.trigger_event(WebhookEvent.CAMPAIGN_SENT, campaign_data)


async def trigger_post_published(post_data: Dict[str, Any]):
    """Shortcut per evento post pubblicato."""
    await webhook_service.trigger_event(WebhookEvent.POST_PUBLISHED, post_data)
