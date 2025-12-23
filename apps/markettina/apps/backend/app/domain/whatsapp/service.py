"""
WhatsApp Cloud API Service - Integration with Meta Graph API.

Pattern based on EmailMarketingService for consistency.
Supports:
- Template messages (pre-approved)
- Text messages (24h window only)
- Status tracking via webhooks
"""

from dataclasses import dataclass
from datetime import datetime

import httpx
import structlog
from sqlalchemy.orm import Session

from app.core.config import settings

from .models import WhatsAppMessage, WhatsAppMessageStatus, WhatsAppMessageType
from .schemas import (
    SendTemplateRequest,
    SendTextRequest,
    TemplateComponent,
    TemplateInfo,
)

logger = structlog.get_logger(__name__)


@dataclass
class SendResult:
    """Result of WhatsApp send operation."""
    success: bool
    message_id: str | None = None
    phone: str = ""
    error: str | None = None
    error_code: str | None = None


class WhatsAppService:
    """
    WhatsApp Cloud API Service.

    Integrates with Meta Graph API for sending messages
    and tracking delivery status.
    """

    # Meta Graph API base URL
    BASE_URL = "https://graph.facebook.com"

    def __init__(self, db: Session | None = None):
        self.db = db
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.business_account_id = settings.WHATSAPP_BUSINESS_ACCOUNT_ID
        self.api_version = settings.WHATSAPP_API_VERSION
        self._client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        """Check if WhatsApp is properly configured."""
        return bool(self.phone_number_id and self.access_token)

    @property
    def messages_url(self) -> str:
        """Get messages API endpoint."""
        return f"{self.BASE_URL}/{self.api_version}/{self.phone_number_id}/messages"

    @property
    def templates_url(self) -> str:
        """Get templates API endpoint."""
        return f"{self.BASE_URL}/{self.api_version}/{self.business_account_id}/message_templates"

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
            )
        return self._client

    async def close(self):
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # =========================================================================
    # SEND METHODS
    # =========================================================================

    async def send_template_message(
        self,
        request: SendTemplateRequest
    ) -> SendResult:
        """
        Send a pre-approved template message.

        Templates must be approved by WhatsApp before use.
        This is the primary method for initiating conversations.
        """
        if not self.is_configured:
            return SendResult(
                success=False,
                phone=request.phone,
                error="WhatsApp not configured. Set WHATSAPP_PHONE_NUMBER_ID and WHATSAPP_ACCESS_TOKEN."
            )

        # Build template payload
        payload = {
            "messaging_product": "whatsapp",
            "to": request.phone.replace("+", ""),  # API expects without +
            "type": "template",
            "template": {
                "name": request.template_name,
                "language": {
                    "code": request.language
                }
            }
        }

        # Add components if provided
        if request.components:
            payload["template"]["components"] = [
                {
                    "type": comp.type,
                    "parameters": [
                        {"type": p.type, "text": p.text}
                        for p in comp.parameters
                    ]
                }
                for comp in request.components
            ]

        logger.info(
            "whatsapp_send_template",
            phone=request.phone,
            template=request.template_name
        )

        try:
            client = await self._get_client()
            response = await client.post(self.messages_url, json=payload)

            if response.status_code == 200:
                data = response.json()
                message_id = data.get("messages", [{}])[0].get("id")

                # Save to database if available
                if self.db and message_id:
                    self._save_message(
                        waba_id=message_id,
                        phone=request.phone,
                        template_name=request.template_name,
                        language=request.language,
                        lead_id=request.lead_id,
                        campaign_id=request.campaign_id,
                        status=WhatsAppMessageStatus.SENT
                    )

                logger.info(
                    "whatsapp_send_success",
                    message_id=message_id,
                    phone=request.phone
                )

                return SendResult(
                    success=True,
                    message_id=message_id,
                    phone=request.phone
                )
            error_data = response.json().get("error", {})
            error_msg = error_data.get("message", "Unknown error")
            error_code = str(error_data.get("code", ""))

            logger.error(
                "whatsapp_send_failed",
                phone=request.phone,
                error=error_msg,
                code=error_code,
                status_code=response.status_code
            )

            # Save failed attempt
            if self.db:
                self._save_message(
                    waba_id=None,
                    phone=request.phone,
                    template_name=request.template_name,
                    language=request.language,
                    lead_id=request.lead_id,
                    campaign_id=request.campaign_id,
                    status=WhatsAppMessageStatus.FAILED,
                    error_code=error_code,
                    error_message=error_msg
                )

            return SendResult(
                success=False,
                phone=request.phone,
                error=error_msg,
                error_code=error_code
            )

        except httpx.RequestError as e:
            logger.error("whatsapp_request_error", error=str(e))
            return SendResult(
                success=False,
                phone=request.phone,
                error=f"Request failed: {e!s}"
            )

    async def send_text_message(
        self,
        request: SendTextRequest
    ) -> SendResult:
        """
        Send a text message.

        NOTE: Text messages can only be sent within 24 hours
        of the last user message (conversation window).
        """
        if not self.is_configured:
            return SendResult(
                success=False,
                phone=request.phone,
                error="WhatsApp not configured"
            )

        payload = {
            "messaging_product": "whatsapp",
            "to": request.phone.replace("+", ""),
            "type": "text",
            "text": {
                "preview_url": False,
                "body": request.message
            }
        }

        try:
            client = await self._get_client()
            response = await client.post(self.messages_url, json=payload)

            if response.status_code == 200:
                data = response.json()
                message_id = data.get("messages", [{}])[0].get("id")

                if self.db and message_id:
                    self._save_message(
                        waba_id=message_id,
                        phone=request.phone,
                        message_text=request.message,
                        lead_id=request.lead_id,
                        message_type=WhatsAppMessageType.TEXT,
                        status=WhatsAppMessageStatus.SENT
                    )

                return SendResult(
                    success=True,
                    message_id=message_id,
                    phone=request.phone
                )
            error_data = response.json().get("error", {})
            return SendResult(
                success=False,
                phone=request.phone,
                error=error_data.get("message", "Unknown error"),
                error_code=str(error_data.get("code", ""))
            )

        except httpx.RequestError as e:
            return SendResult(
                success=False,
                phone=request.phone,
                error=f"Request failed: {e!s}"
            )

    async def send_bulk_template(
        self,
        phones: list[str],
        template_name: str,
        language: str = "it",
        components: list[TemplateComponent] = [],
        campaign_id: str | None = None
    ) -> list[SendResult]:
        """
        Send template message to multiple recipients.

        Implements basic rate limiting (1 per 100ms).
        """
        import asyncio

        results = []
        for phone in phones:
            request = SendTemplateRequest(
                phone=phone,
                template_name=template_name,
                language=language,
                components=components,
                campaign_id=campaign_id
            )
            result = await self.send_template_message(request)
            results.append(result)

            # Basic rate limiting
            await asyncio.sleep(0.1)

        return results

    # =========================================================================
    # TEMPLATE MANAGEMENT
    # =========================================================================

    async def get_templates(self) -> list[TemplateInfo]:
        """
        Get list of approved message templates.
        """
        if not self.is_configured or not self.business_account_id:
            logger.warning("whatsapp_templates_not_configured")
            return []

        try:
            client = await self._get_client()
            response = await client.get(
                self.templates_url,
                params={"limit": 100}
            )

            if response.status_code == 200:
                data = response.json()
                templates = []

                for t in data.get("data", []):
                    templates.append(TemplateInfo(
                        name=t.get("name", ""),
                        language=t.get("language", ""),
                        status=t.get("status", ""),
                        category=t.get("category", ""),
                        components=t.get("components", [])
                    ))

                return templates
            logger.error(
                "whatsapp_templates_fetch_error",
                status=response.status_code
            )
            return []

        except httpx.RequestError as e:
            logger.error("whatsapp_templates_error", error=str(e))
            return []

    # =========================================================================
    # STATUS TRACKING (Webhook updates)
    # =========================================================================

    def update_message_status(
        self,
        waba_message_id: str,
        status: str,
        timestamp: datetime | None = None,
        error_code: str | None = None,
        error_message: str | None = None
    ) -> bool:
        """
        Update message status from webhook callback.

        Called by webhook handler when receiving status updates.
        """
        if not self.db:
            return False

        try:
            message = self.db.query(WhatsAppMessage).filter(
                WhatsAppMessage.waba_message_id == waba_message_id
            ).first()

            if not message:
                logger.warning(
                    "whatsapp_status_update_message_not_found",
                    waba_id=waba_message_id
                )
                return False

            # Map WhatsApp status to our enum
            status_map = {
                "sent": WhatsAppMessageStatus.SENT,
                "delivered": WhatsAppMessageStatus.DELIVERED,
                "read": WhatsAppMessageStatus.READ,
                "failed": WhatsAppMessageStatus.FAILED,
            }

            new_status = status_map.get(status.lower())
            if new_status:
                message.status = new_status.value

                # Update timestamp fields
                ts = timestamp or datetime.utcnow()
                if new_status == WhatsAppMessageStatus.SENT:
                    message.sent_at = ts
                elif new_status == WhatsAppMessageStatus.DELIVERED:
                    message.delivered_at = ts
                elif new_status == WhatsAppMessageStatus.READ:
                    message.read_at = ts
                elif new_status == WhatsAppMessageStatus.FAILED:
                    message.error_code = error_code
                    message.error_message = error_message

                self.db.commit()

                logger.info(
                    "whatsapp_status_updated",
                    waba_id=waba_message_id,
                    status=new_status.value
                )
                return True

            return False

        except Exception as e:
            logger.error("whatsapp_status_update_error", error=str(e))
            self.db.rollback()
            return False

    # =========================================================================
    # DATABASE HELPERS
    # =========================================================================

    def _save_message(
        self,
        phone: str,
        waba_id: str | None = None,
        template_name: str | None = None,
        language: str | None = None,
        message_text: str | None = None,
        message_type: WhatsAppMessageType = WhatsAppMessageType.TEMPLATE,
        lead_id: int | None = None,
        campaign_id: str | None = None,
        status: WhatsAppMessageStatus = WhatsAppMessageStatus.PENDING,
        error_code: str | None = None,
        error_message: str | None = None
    ) -> WhatsAppMessage | None:
        """Save message to database."""
        if not self.db:
            return None

        try:
            message = WhatsAppMessage(
                waba_message_id=waba_id,
                phone_number=phone,
                template_name=template_name,
                template_language=language,
                message_text=message_text,
                message_type=message_type.value,
                lead_id=lead_id,
                campaign_id=campaign_id,
                status=status.value,
                error_code=error_code,
                error_message=error_message,
                sent_at=datetime.utcnow() if status == WhatsAppMessageStatus.SENT else None
            )

            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)

            return message

        except Exception as e:
            logger.error("whatsapp_save_message_error", error=str(e))
            self.db.rollback()
            return None

    def get_messages(
        self,
        lead_id: int | None = None,
        campaign_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[WhatsAppMessage]:
        """Get messages with optional filters."""
        if not self.db:
            return []

        query = self.db.query(WhatsAppMessage)

        if lead_id:
            query = query.filter(WhatsAppMessage.lead_id == lead_id)
        if campaign_id:
            query = query.filter(WhatsAppMessage.campaign_id == campaign_id)
        if status:
            query = query.filter(WhatsAppMessage.status == status)

        return query.order_by(
            WhatsAppMessage.created_at.desc()
        ).limit(limit).offset(offset).all()

    def get_stats(self, campaign_id: str | None = None) -> dict[str, int]:
        """Get message statistics."""
        if not self.db:
            return {}

        try:
            query = self.db.query(WhatsAppMessage)
            if campaign_id:
                query = query.filter(WhatsAppMessage.campaign_id == campaign_id)

            total = query.count()
            sent = query.filter(WhatsAppMessage.status.in_([
                WhatsAppMessageStatus.SENT.value,
                WhatsAppMessageStatus.DELIVERED.value,
                WhatsAppMessageStatus.READ.value
            ])).count()
            delivered = query.filter(WhatsAppMessage.status.in_([
                WhatsAppMessageStatus.DELIVERED.value,
                WhatsAppMessageStatus.READ.value
            ])).count()
            read = query.filter(
                WhatsAppMessage.status == WhatsAppMessageStatus.READ.value
            ).count()
            failed = query.filter(
                WhatsAppMessage.status == WhatsAppMessageStatus.FAILED.value
            ).count()

            return {
                "total": total,
                "sent": sent,
                "delivered": delivered,
                "read": read,
                "failed": failed,
                "delivery_rate": round(delivered / sent * 100, 1) if sent > 0 else 0,
                "read_rate": round(read / delivered * 100, 1) if delivered > 0 else 0
            }

        except Exception as e:
            logger.error("whatsapp_stats_error", error=str(e))
            return {}


# Singleton-like factory function
def get_whatsapp_service(db: Session) -> WhatsAppService:
    """Factory function to create WhatsAppService with DB session."""
    return WhatsAppService(db)
