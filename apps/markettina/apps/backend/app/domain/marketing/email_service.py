"""
Email Marketing Service - Real SMTP Integration
Supports SendGrid, Mailgun, and standard SMTP
Production-ready email delivery with tracking
"""

import asyncio
import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings


class EmailProvider(str, Enum):
    """Supported email providers."""
    SENDGRID = "sendgrid"
    MAILGUN = "mailgun"
    SMTP = "smtp"


@dataclass
class EmailRecipient:
    """Email recipient data."""
    email: str
    name: str | None = None
    lead_id: int | None = None
    custom_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class EmailMessage:
    """Email message data."""
    to: list[EmailRecipient]
    subject: str
    html_content: str
    text_content: str | None = None
    from_email: str = "noreply@markettina.it"
    from_name: str = "MARKETTINA"
    reply_to: str | None = None
    campaign_id: int | None = None
    track_opens: bool = True
    track_clicks: bool = True
    tags: list[str] = field(default_factory=list)
    custom_headers: dict[str, str] = field(default_factory=dict)


@dataclass
class SendResult:
    """Result of email send operation."""
    success: bool
    message_id: str | None = None
    provider: str | None = None
    error: str | None = None
    recipient_email: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CampaignStats:
    """Campaign statistics."""
    campaign_id: int
    total_sent: int = 0
    total_delivered: int = 0
    total_opened: int = 0
    total_clicked: int = 0
    total_bounced: int = 0
    total_unsubscribed: int = 0
    open_rate: float = 0.0
    click_rate: float = 0.0
    bounce_rate: float = 0.0


class EmailMarketingService:
    """
    Production email marketing service.
    Integrates with SendGrid, Mailgun, or standard SMTP.
    """

    def __init__(self):
        self.provider = self._detect_provider()
        self.sendgrid_api_key = getattr(settings, "SENDGRID_API_KEY", None)
        self.mailgun_api_key = getattr(settings, "MAILGUN_API_KEY", None)
        self.mailgun_domain = getattr(settings, "MAILGUN_DOMAIN", None)
        self.smtp_host = getattr(settings, "SMTP_HOST", None)
        self.smtp_port = getattr(settings, "SMTP_PORT", 587)
        self.smtp_user = getattr(settings, "SMTP_USER", None)
        self.smtp_password = getattr(settings, "SMTP_PASSWORD", None)
        self.tracking_domain = getattr(settings, "EMAIL_TRACKING_DOMAIN", "https://markettina.it")

    def _detect_provider(self) -> EmailProvider:
        """Detect which email provider is configured."""
        if getattr(settings, "SENDGRID_API_KEY", None):
            return EmailProvider.SENDGRID
        if getattr(settings, "MAILGUN_API_KEY", None):
            return EmailProvider.MAILGUN
        return EmailProvider.SMTP

    # =========================================================================
    # SENDGRID INTEGRATION
    # =========================================================================

    async def _send_via_sendgrid(self, message: EmailMessage) -> list[SendResult]:
        """Send email via SendGrid API."""
        results = []

        for recipient in message.to:
            try:
                # Build personalization with merge tags
                personalization = {
                    "to": [{"email": recipient.email, "name": recipient.name or ""}],
                    "subject": self._apply_merge_tags(message.subject, recipient),
                }

                # Add custom data as merge tags
                if recipient.custom_data:
                    personalization["dynamic_template_data"] = recipient.custom_data

                payload = {
                    "personalizations": [personalization],
                    "from": {
                        "email": message.from_email,
                        "name": message.from_name
                    },
                    "content": [
                        {"type": "text/plain", "value": message.text_content or self._strip_html(message.html_content)},
                        {"type": "text/html", "value": self._inject_tracking(message.html_content, recipient, message.campaign_id)}
                    ],
                    "tracking_settings": {
                        "click_tracking": {"enable": message.track_clicks},
                        "open_tracking": {"enable": message.track_opens}
                    }
                }

                if message.reply_to:
                    payload["reply_to"] = {"email": message.reply_to}

                if message.tags:
                    payload["categories"] = message.tags[:10]  # SendGrid max 10 categories

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.sendgrid.com/v3/mail/send",
                        headers={
                            "Authorization": f"Bearer {self.sendgrid_api_key}",
                            "Content-Type": "application/json"
                        },
                        json=payload,
                        timeout=30.0
                    )

                    if response.status_code in [200, 202]:
                        message_id = response.headers.get("X-Message-Id", str(uuid.uuid4()))
                        results.append(SendResult(
                            success=True,
                            message_id=message_id,
                            provider="sendgrid",
                            recipient_email=recipient.email
                        ))
                    else:
                        results.append(SendResult(
                            success=False,
                            provider="sendgrid",
                            error=f"SendGrid error: {response.status_code} - {response.text}",
                            recipient_email=recipient.email
                        ))

            except Exception as e:
                results.append(SendResult(
                    success=False,
                    provider="sendgrid",
                    error=str(e),
                    recipient_email=recipient.email
                ))

        return results

    # =========================================================================
    # MAILGUN INTEGRATION
    # =========================================================================

    async def _send_via_mailgun(self, message: EmailMessage) -> list[SendResult]:
        """Send email via Mailgun API."""
        results = []

        for recipient in message.to:
            try:
                form_data = {
                    "from": f"{message.from_name} <{message.from_email}>",
                    "to": f"{recipient.name or ''} <{recipient.email}>".strip(),
                    "subject": self._apply_merge_tags(message.subject, recipient),
                    "html": self._inject_tracking(message.html_content, recipient, message.campaign_id),
                    "text": message.text_content or self._strip_html(message.html_content),
                    "o:tracking": "yes" if message.track_clicks or message.track_opens else "no",
                    "o:tracking-clicks": "htmlonly" if message.track_clicks else "no",
                    "o:tracking-opens": "yes" if message.track_opens else "no"
                }

                if message.reply_to:
                    form_data["h:Reply-To"] = message.reply_to

                for tag in message.tags[:3]:  # Mailgun max 3 tags
                    form_data["o:tag"] = tag

                # Custom headers
                for key, value in message.custom_headers.items():
                    form_data[f"h:{key}"] = value

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages",
                        auth=("api", self.mailgun_api_key),
                        data=form_data,
                        timeout=30.0
                    )

                    if response.status_code == 200:
                        data = response.json()
                        results.append(SendResult(
                            success=True,
                            message_id=data.get("id", str(uuid.uuid4())),
                            provider="mailgun",
                            recipient_email=recipient.email
                        ))
                    else:
                        results.append(SendResult(
                            success=False,
                            provider="mailgun",
                            error=f"Mailgun error: {response.status_code} - {response.text}",
                            recipient_email=recipient.email
                        ))

            except Exception as e:
                results.append(SendResult(
                    success=False,
                    provider="mailgun",
                    error=str(e),
                    recipient_email=recipient.email
                ))

        return results

    # =========================================================================
    # SMTP INTEGRATION
    # =========================================================================

    async def _send_via_smtp(self, message: EmailMessage) -> list[SendResult]:
        """Send email via standard SMTP."""
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        results = []

        for recipient in message.to:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = self._apply_merge_tags(message.subject, recipient)
                msg["From"] = f"{message.from_name} <{message.from_email}>"
                msg["To"] = f"{recipient.name or ''} <{recipient.email}>".strip()

                if message.reply_to:
                    msg["Reply-To"] = message.reply_to

                # Add text part
                text_content = message.text_content or self._strip_html(message.html_content)
                msg.attach(MIMEText(text_content, "plain", "utf-8"))

                # Add HTML part with tracking
                html_content = self._inject_tracking(message.html_content, recipient, message.campaign_id)
                msg.attach(MIMEText(html_content, "html", "utf-8"))

                # Custom headers
                for key, value in message.custom_headers.items():
                    msg[key] = value

                # Send via SMTP in thread pool
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    self._smtp_send,
                    msg,
                    recipient.email
                )

                results.append(SendResult(
                    success=True,
                    message_id=str(uuid.uuid4()),
                    provider="smtp",
                    recipient_email=recipient.email
                ))

            except Exception as e:
                results.append(SendResult(
                    success=False,
                    provider="smtp",
                    error=str(e),
                    recipient_email=recipient.email
                ))

        return results

    def _smtp_send(self, msg, recipient_email: str):
        """Blocking SMTP send for thread pool."""
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)

    # =========================================================================
    # MAIN SEND METHOD
    # =========================================================================

    async def send(self, message: EmailMessage) -> list[SendResult]:
        """
        Send email using configured provider.
        Automatically selects SendGrid, Mailgun, or SMTP.
        """
        if self.provider == EmailProvider.SENDGRID and self.sendgrid_api_key:
            return await self._send_via_sendgrid(message)
        if self.provider == EmailProvider.MAILGUN and self.mailgun_api_key:
            return await self._send_via_mailgun(message)
        return await self._send_via_smtp(message)

    async def send_campaign(
        self,
        db: Session,
        campaign_id: int,
        batch_size: int = 50,
        delay_between_batches: float = 1.0
    ) -> dict[str, Any]:
        """
        Send email campaign to all targeted leads.
        Implements batching and rate limiting.
        """
        # Get campaign
        campaign_query = text("""
            SELECT id, name, subject, html_content, text_content,
                   target_region, target_industry, target_tags
            FROM email_campaigns
            WHERE id = :campaign_id AND is_active = true AND is_sent = false
        """)
        campaign = db.execute(campaign_query, {"campaign_id": campaign_id}).fetchone()

        if not campaign:
            return {"success": False, "error": "Campaign not found or already sent"}

        # Get targeted leads
        leads_query = text("""
            SELECT id, email, contact_name, company_name, city, industry
            FROM leads
            WHERE status != 'lost'
            AND (
                (:region IS NULL OR region ILIKE '%' || :region || '%' OR city ILIKE '%' || :region || '%')
                AND (:industry IS NULL OR industry ILIKE '%' || :industry || '%')
            )
            AND email IS NOT NULL
            AND email != ''
            ORDER BY score DESC
        """)

        leads = db.execute(leads_query, {
            "region": campaign[5],
            "industry": campaign[6]
        }).fetchall()

        if not leads:
            return {"success": False, "error": "No leads match campaign criteria"}

        # Prepare recipients
        recipients = [
            EmailRecipient(
                email=lead[1],
                name=lead[2],
                lead_id=lead[0],
                custom_data={
                    "contact_name": lead[2] or "Gentile Cliente",
                    "company_name": lead[3] or "",
                    "city": lead[4] or "",
                    "industry": lead[5] or ""
                }
            )
            for lead in leads
        ]

        # Send in batches
        total_sent = 0
        total_failed = 0
        all_results = []

        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]

            message = EmailMessage(
                to=batch,
                subject=campaign[2],
                html_content=campaign[3],
                text_content=campaign[4],
                campaign_id=campaign_id,
                tags=[f"campaign-{campaign_id}", campaign[1]]
            )

            results = await self.send(message)
            all_results.extend(results)

            for result in results:
                if result.success:
                    total_sent += 1
                    # Log successful send
                    await self._log_email_send(db, campaign_id, result)
                else:
                    total_failed += 1

            # Rate limiting
            if i + batch_size < len(recipients):
                await asyncio.sleep(delay_between_batches)

        # Update campaign status
        update_query = text("""
            UPDATE email_campaigns
            SET is_sent = true,
                sent_date = NOW(),
                total_sent = :total_sent,
                updated_at = NOW()
            WHERE id = :campaign_id
        """)
        db.execute(update_query, {"campaign_id": campaign_id, "total_sent": total_sent})
        db.commit()

        return {
            "success": True,
            "campaign_id": campaign_id,
            "total_recipients": len(recipients),
            "total_sent": total_sent,
            "total_failed": total_failed,
            "provider": self.provider.value
        }

    # =========================================================================
    # TRACKING & ANALYTICS
    # =========================================================================

    def _inject_tracking(
        self,
        html_content: str,
        recipient: EmailRecipient,
        campaign_id: int | None
    ) -> str:
        """Inject tracking pixel and link tracking into HTML."""
        if not campaign_id:
            return html_content

        # Generate unique tracking ID
        tracking_id = hashlib.md5(
            f"{campaign_id}:{recipient.email}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]

        # Add open tracking pixel
        tracking_pixel = f'<img src="{self.tracking_domain}/api/v1/marketing/email/track/open/{tracking_id}" width="1" height="1" style="display:none;" alt="" />'

        # Insert before closing body tag
        if "</body>" in html_content:
            html_content = html_content.replace("</body>", f"{tracking_pixel}</body>")
        else:
            html_content += tracking_pixel

        # Link tracking to be implemented in future version

        return html_content

    async def _log_email_send(
        self,
        db: Session,
        campaign_id: int,
        result: SendResult
    ):
        """Log email send event to database."""
        try:
            insert_query = text("""
                INSERT INTO email_logs (
                    campaign_id, recipient_email, message_id,
                    provider, status, sent_at
                ) VALUES (
                    :campaign_id, :email, :message_id,
                    :provider, 'sent', NOW()
                )
            """)
            db.execute(insert_query, {
                "campaign_id": campaign_id,
                "email": result.recipient_email,
                "message_id": result.message_id,
                "provider": result.provider
            })
        except Exception:
            pass  # Don't fail send on logging error

    async def track_open(self, db: Session, tracking_id: str) -> bool:
        """Track email open event."""
        try:
            update_query = text("""
                UPDATE email_logs
                SET opened_at = COALESCE(opened_at, NOW()),
                    open_count = COALESCE(open_count, 0) + 1
                WHERE message_id = :tracking_id
            """)
            db.execute(update_query, {"tracking_id": tracking_id})

            # Update campaign stats
            update_campaign = text("""
                UPDATE email_campaigns
                SET total_opened = total_opened + 1
                WHERE id = (
                    SELECT campaign_id FROM email_logs WHERE message_id = :tracking_id
                )
            """)
            db.execute(update_campaign, {"tracking_id": tracking_id})
            db.commit()
            return True
        except Exception:
            return False

    async def track_click(self, db: Session, tracking_id: str, link_url: str) -> bool:
        """Track email click event."""
        try:
            update_query = text("""
                UPDATE email_logs
                SET clicked_at = COALESCE(clicked_at, NOW()),
                    click_count = COALESCE(click_count, 0) + 1,
                    clicked_links = COALESCE(clicked_links, '[]'::jsonb) || :link::jsonb
                WHERE message_id = :tracking_id
            """)
            db.execute(update_query, {
                "tracking_id": tracking_id,
                "link": f'["{link_url}"]'
            })

            # Update campaign stats
            update_campaign = text("""
                UPDATE email_campaigns
                SET total_clicked = total_clicked + 1
                WHERE id = (
                    SELECT campaign_id FROM email_logs WHERE message_id = :tracking_id
                )
            """)
            db.execute(update_campaign, {"tracking_id": tracking_id})
            db.commit()
            return True
        except Exception:
            return False

    async def get_campaign_stats(self, db: Session, campaign_id: int) -> CampaignStats:
        """Get campaign statistics."""
        query = text("""
            SELECT
                total_sent,
                total_opened,
                total_clicked,
                COALESCE(
                    (SELECT COUNT(*) FROM email_logs WHERE campaign_id = :id AND status = 'bounced'),
                    0
                ) as total_bounced,
                COALESCE(
                    (SELECT COUNT(*) FROM email_logs WHERE campaign_id = :id AND unsubscribed = true),
                    0
                ) as total_unsubscribed
            FROM email_campaigns
            WHERE id = :id
        """)
        row = db.execute(query, {"id": campaign_id}).fetchone()

        if not row:
            return CampaignStats(campaign_id=campaign_id)

        total_sent = row[0] or 0
        total_opened = row[1] or 0
        total_clicked = row[2] or 0
        total_bounced = row[3] or 0

        return CampaignStats(
            campaign_id=campaign_id,
            total_sent=total_sent,
            total_delivered=total_sent - total_bounced,
            total_opened=total_opened,
            total_clicked=total_clicked,
            total_bounced=total_bounced,
            total_unsubscribed=row[4] or 0,
            open_rate=round((total_opened / total_sent * 100), 2) if total_sent > 0 else 0,
            click_rate=round((total_clicked / total_sent * 100), 2) if total_sent > 0 else 0,
            bounce_rate=round((total_bounced / total_sent * 100), 2) if total_sent > 0 else 0
        )

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def _apply_merge_tags(self, text: str, recipient: EmailRecipient) -> str:
        """Replace merge tags with recipient data."""
        replacements = {
            "{{email}}": recipient.email,
            "{{name}}": recipient.name or "",
            "{{first_name}}": (recipient.name or "").split()[0] if recipient.name else "",
        }

        for key, value in (recipient.custom_data or {}).items():
            replacements[f"{{{{{key}}}}}"] = str(value)

        for tag, value in replacements.items():
            text = text.replace(tag, value)

        return text

    def _strip_html(self, html: str) -> str:
        """Convert HTML to plain text."""
        import re
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", html)
        # Decode HTML entities
        text = text.replace("&nbsp;", " ")
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&quot;", '"')
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()


# Singleton instance
email_service = EmailMarketingService()


# =============================================================================
# LIQUID OUTREACH ENGINE - Intelligent Email Sequences
# =============================================================================

class SequenceAction(str, Enum):
    """Actions to take based on email engagement."""
    SEND_EMAIL = "send_email"
    WAIT = "wait"
    NOTIFY_ADMIN = "notify_admin"
    UPDATE_LEAD_STATUS = "update_lead_status"
    ADD_TO_CAMPAIGN = "add_to_campaign"
    STOP_SEQUENCE = "stop_sequence"


@dataclass
class SequenceStep:
    """Single step in an email sequence."""
    step_id: int
    action: SequenceAction
    wait_days: int = 0
    email_template_id: int | None = None
    condition: str | None = None  # "opened", "clicked", "not_opened", "not_clicked"
    next_step_if_true: int | None = None
    next_step_if_false: int | None = None
    new_status: str | None = None  # For UPDATE_LEAD_STATUS
    notification_message: str | None = None  # For NOTIFY_ADMIN


@dataclass
class SequenceConfig:
    """Configuration for a Liquid Sequence."""
    sequence_id: int
    name: str
    steps: list[SequenceStep]
    auto_stop_on_reply: bool = True
    max_emails_per_lead: int = 5


class LiquidSequenceEngine:
    """
    Intelligent email sequence engine with branching logic.

    Implements the "Liquid Outreach" pattern:
    - Conditional branching based on opens/clicks
    - Automatic status updates
    - Admin notifications for hot leads
    - Reply detection and sequence stopping
    """

    def __init__(self, db: Session):
        self.db = db
        self.email_service = email_service

    async def create_sequence(self, name: str, steps_config: list[dict]) -> int:
        """
        Create a new email sequence.

        Args:
            name: Sequence name
            steps_config: List of step configurations

        Returns:
            Sequence ID
        """
        result = self.db.execute(
            text("""
                INSERT INTO email_sequences (name, steps_json, is_active, created_at)
                VALUES (:name, :steps, true, NOW())
                RETURNING id
            """),
            {"name": name, "steps": str(steps_config)}
        )
        sequence_id = result.scalar()
        self.db.commit()
        return sequence_id

    async def enroll_lead(self, lead_id: int, sequence_id: int) -> bool:
        """
        Enroll a lead in a sequence.

        Args:
            lead_id: Lead to enroll
            sequence_id: Sequence to enroll in

        Returns:
            Success status
        """
        # Check if already enrolled
        existing = self.db.execute(
            text("""
                SELECT id FROM sequence_enrollments
                WHERE lead_id = :lead_id AND sequence_id = :sequence_id AND status = 'active'
            """),
            {"lead_id": lead_id, "sequence_id": sequence_id}
        ).fetchone()

        if existing:
            return False  # Already enrolled

        self.db.execute(
            text("""
                INSERT INTO sequence_enrollments (
                    lead_id, sequence_id, current_step, status, enrolled_at
                ) VALUES (
                    :lead_id, :sequence_id, 1, 'active', NOW()
                )
            """),
            {"lead_id": lead_id, "sequence_id": sequence_id}
        )
        self.db.commit()
        return True

    async def process_engagement(
        self,
        lead_id: int,
        engagement_type: str,  # "opened", "clicked", "replied"
        email_id: str | None = None
    ):
        """
        Process an email engagement event and potentially advance the sequence.

        This is the core of the Liquid Outreach logic.
        """
        # Get active enrollment
        enrollment = self.db.execute(
            text("""
                SELECT se.id, se.sequence_id, se.current_step, es.steps_json
                FROM sequence_enrollments se
                JOIN email_sequences es ON es.id = se.sequence_id
                WHERE se.lead_id = :lead_id AND se.status = 'active'
                ORDER BY se.enrolled_at DESC
                LIMIT 1
            """),
            {"lead_id": lead_id}
        ).fetchone()

        if not enrollment:
            return  # Not in any sequence

        enrollment_id, sequence_id, current_step, steps_json = enrollment

        # Handle reply (stop sequence)
        if engagement_type == "replied":
            self.db.execute(
                text("""
                    UPDATE sequence_enrollments
                    SET status = 'completed', completed_at = NOW()
                    WHERE id = :id
                """),
                {"id": enrollment_id}
            )
            # Notify admin of hot lead
            self.db.execute(
                text("""
                    INSERT INTO admin_notifications (
                        type, title, message, lead_id, created_at
                    ) VALUES (
                        'hot_lead', '🔥 Lead Replied!',
                        :message, :lead_id, NOW()
                    )
                """),
                {
                    "message": f"Lead {lead_id} replied to sequence email!",
                    "lead_id": lead_id
                }
            )
            # Update lead status to QUALIFIED
            self.db.execute(
                text("UPDATE leads SET status = 'QUALIFIED' WHERE id = :id"),
                {"id": lead_id}
            )
            self.db.commit()
            return

        # Record engagement
        self.db.execute(
            text("""
                INSERT INTO email_engagements (
                    lead_id, enrollment_id, engagement_type, email_id, recorded_at
                ) VALUES (
                    :lead_id, :enrollment_id, :type, :email_id, NOW()
                )
            """),
            {
                "lead_id": lead_id,
                "enrollment_id": enrollment_id,
                "type": engagement_type,
                "email_id": email_id
            }
        )

        # Update lead score based on engagement
        score_delta = 10 if engagement_type == "clicked" else 5
        self.db.execute(
            text("UPDATE leads SET score = LEAST(score + :delta, 100) WHERE id = :id"),
            {"delta": score_delta, "id": lead_id}
        )

        self.db.commit()

    async def advance_sequences(self):
        """
        Batch process: Check all active enrollments and advance those that are ready.

        This should be called by a scheduler (e.g., Celery beat, cron).
        """
        # Get enrollments ready to advance (wait time elapsed)
        ready = self.db.execute(
            text("""
                SELECT se.id, se.lead_id, se.current_step, se.sequence_id, es.steps_json
                FROM sequence_enrollments se
                JOIN email_sequences es ON es.id = se.sequence_id
                WHERE se.status = 'active'
                AND se.next_step_at <= NOW()
            """)
        ).fetchall()

        for enrollment in ready:
            await self._process_step(
                enrollment_id=enrollment[0],
                lead_id=enrollment[1],
                current_step=enrollment[2],
                sequence_id=enrollment[3],
                steps_json=enrollment[4]
            )

    async def _process_step(
        self,
        enrollment_id: int,
        lead_id: int,
        current_step: int,
        sequence_id: int,
        steps_json: str
    ):
        """Process a single sequence step for a lead."""
        import json

        try:
            steps = json.loads(steps_json.replace("'", '"'))
        except:
            return

        if current_step > len(steps):
            # Sequence complete
            self.db.execute(
                text("""
                    UPDATE sequence_enrollments
                    SET status = 'completed', completed_at = NOW()
                    WHERE id = :id
                """),
                {"id": enrollment_id}
            )
            self.db.commit()
            return

        step_config = steps[current_step - 1]
        action = step_config.get("action", "send_email")

        # Check condition if present
        condition = step_config.get("condition")
        condition_met = True

        if condition:
            # Check if lead has the expected engagement
            engagement = self.db.execute(
                text("""
                    SELECT id FROM email_engagements
                    WHERE lead_id = :lead_id AND enrollment_id = :enrollment_id
                    AND engagement_type = :type
                """),
                {
                    "lead_id": lead_id,
                    "enrollment_id": enrollment_id,
                    "type": condition.replace("not_", "")
                }
            ).fetchone()

            if condition.startswith("not_"):
                condition_met = engagement is None
            else:
                condition_met = engagement is not None

        # Determine next step based on condition
        if condition_met:
            next_step = step_config.get("next_step_if_true", current_step + 1)
        else:
            next_step = step_config.get("next_step_if_false", current_step + 1)

        # Execute action
        if action == "send_email" and condition_met:
            # Get lead email
            lead = self.db.execute(
                text("SELECT email, company_name FROM leads WHERE id = :id"),
                {"id": lead_id}
            ).fetchone()

            if lead and lead[0]:
                # Get email template
                template_id = step_config.get("email_template_id")
                # For now, use dynamic subject/body from step config
                subject = step_config.get("subject", "Follow-up from MARKETTINA")
                body = step_config.get("body", "")

                await self.email_service.send(EmailMessage(
                    to=[EmailRecipient(email=lead[0], name=lead[1])],
                    subject=subject,
                    html_content=body,
                    campaign_id=sequence_id,
                    track_opens=True,
                    track_clicks=True
                ))

        elif action == "notify_admin":
            self.db.execute(
                text("""
                    INSERT INTO admin_notifications (type, title, message, lead_id, created_at)
                    VALUES ('sequence', :title, :message, :lead_id, NOW())
                """),
                {
                    "title": step_config.get("notification_title", "Sequence Alert"),
                    "message": step_config.get("notification_message", f"Lead {lead_id} reached step {current_step}"),
                    "lead_id": lead_id
                }
            )

        elif action == "update_lead_status":
            new_status = step_config.get("new_status", "CONTACTED")
            self.db.execute(
                text("UPDATE leads SET status = :status WHERE id = :id"),
                {"status": new_status, "id": lead_id}
            )

        elif action == "stop_sequence":
            self.db.execute(
                text("""
                    UPDATE sequence_enrollments
                    SET status = 'stopped', completed_at = NOW()
                    WHERE id = :id
                """),
                {"id": enrollment_id}
            )
            self.db.commit()
            return

        # Update enrollment for next step
        wait_days = step_config.get("wait_days", 2)
        self.db.execute(
            text("""
                UPDATE sequence_enrollments
                SET current_step = :next_step,
                    next_step_at = NOW() + INTERVAL ':days days'
                WHERE id = :id
            """),
            {"next_step": next_step, "days": wait_days, "id": enrollment_id}
        )
        self.db.commit()
