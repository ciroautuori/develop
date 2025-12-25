"""
Marketing Event Bus - The Omni-Brain
Unified event system for reactive lead lifecycle management.

Triggers:
- EMAIL_OPENED → UPDATE_LEAD_SCORE(+5)
- EMAIL_CLICKED → UPDATE_LEAD_SCORE(+10), NOTIFY_ADMIN
- EMAIL_REPLIED → UPDATE_STATUS(QUALIFIED), NOTIFY_ADMIN, STOP_SEQUENCE
- LEAD_SAVED → FIND_LINKEDIN, START_SEQUENCE
- LEAD_QUALIFIED → SCHEDULE_CALL, SEND_WELCOME_PACK
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from sqlalchemy import text
import structlog
import asyncio

logger = structlog.get_logger(__name__)


class EventType(str, Enum):
    """Marketing event types."""
    # Email events
    EMAIL_SENT = "email_sent"
    EMAIL_OPENED = "email_opened"
    EMAIL_CLICKED = "email_clicked"
    EMAIL_REPLIED = "email_replied"
    EMAIL_BOUNCED = "email_bounced"
    EMAIL_UNSUBSCRIBED = "email_unsubscribed"

    # Lead lifecycle events
    LEAD_CREATED = "lead_created"
    LEAD_SAVED = "lead_saved"
    LEAD_ENRICHED = "lead_enriched"
    LEAD_SCORED = "lead_scored"
    LEAD_STATUS_CHANGED = "lead_status_changed"
    LEAD_QUALIFIED = "lead_qualified"
    LEAD_CONVERTED = "lead_converted"

    # Sequence events
    SEQUENCE_STARTED = "sequence_started"
    SEQUENCE_STEP_COMPLETED = "sequence_step_completed"
    SEQUENCE_COMPLETED = "sequence_completed"

    # Campaign events
    CAMPAIGN_LAUNCHED = "campaign_launched"
    CAMPAIGN_COMPLETED = "campaign_completed"


@dataclass
class MarketingEvent:
    """Base event structure."""
    event_type: EventType
    lead_id: Optional[int] = None
    campaign_id: Optional[int] = None
    sequence_id: Optional[int] = None
    email_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class MarketingEventBus:
    """
    Unified marketing event bus - The Omni-Brain.

    Cross-system reactive trigger engine.
    Every action in the marketing system emits an event,
    and handlers react to create cascading effects.
    """

    def __init__(self, db: Session):
        self.db = db
        self._handlers: Dict[EventType, List[Callable]] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default event handlers."""
        # Email engagement handlers
        self.on(EventType.EMAIL_OPENED, self._handle_email_opened)
        self.on(EventType.EMAIL_CLICKED, self._handle_email_clicked)
        self.on(EventType.EMAIL_REPLIED, self._handle_email_replied)

        # Lead lifecycle handlers
        self.on(EventType.LEAD_SAVED, self._handle_lead_saved)
        self.on(EventType.LEAD_QUALIFIED, self._handle_lead_qualified)
        self.on(EventType.LEAD_CONVERTED, self._handle_lead_converted)

    def on(self, event_type: EventType, handler: Callable):
        """Register an event handler."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def emit(self, event: MarketingEvent):
        """
        Emit an event and trigger all registered handlers.

        This is the core of the Omni-Brain.
        """
        logger.info(
            "event_emitted",
            event_type=event.event_type.value,
            lead_id=event.lead_id,
            data=event.data
        )

        # Log event to database
        self._log_event(event)

        # Execute handlers
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(
                    "handler_error",
                    event_type=event.event_type.value,
                    handler=handler.__name__,
                    error=str(e)
                )

    def _log_event(self, event: MarketingEvent):
        """Log event to database for analytics."""
        try:
            self.db.execute(
                text("""
                    INSERT INTO marketing_events (
                        event_type, lead_id, campaign_id, sequence_id,
                        email_id, event_data, created_at
                    ) VALUES (
                        :event_type, :lead_id, :campaign_id, :sequence_id,
                        :email_id, :data, :timestamp
                    )
                """),
                {
                    "event_type": event.event_type.value,
                    "lead_id": event.lead_id,
                    "campaign_id": event.campaign_id,
                    "sequence_id": event.sequence_id,
                    "email_id": event.email_id,
                    "data": str(event.data),
                    "timestamp": event.timestamp
                }
            )
            self.db.commit()
        except Exception as e:
            logger.warning("event_log_failed", error=str(e))

    # =========================================================================
    # DEFAULT HANDLERS
    # =========================================================================

    async def _handle_email_opened(self, event: MarketingEvent):
        """Handle email opened event."""
        if not event.lead_id:
            return

        # Update lead score (+5)
        self.db.execute(
            text("UPDATE leads SET score = LEAST(score + 5, 100) WHERE id = :id"),
            {"id": event.lead_id}
        )

        # Log activity
        self.db.execute(
            text("""
                INSERT INTO lead_activities (lead_id, activity_type, description, created_at)
                VALUES (:lead_id, 'email_opened', :description, NOW())
            """),
            {
                "lead_id": event.lead_id,
                "description": f"Opened email {event.email_id or 'unknown'}"
            }
        )
        self.db.commit()

        logger.info("email_open_processed", lead_id=event.lead_id)

    async def _handle_email_clicked(self, event: MarketingEvent):
        """Handle email clicked event - Hot lead signal!"""
        if not event.lead_id:
            return

        # Update lead score (+10)
        self.db.execute(
            text("UPDATE leads SET score = LEAST(score + 10, 100) WHERE id = :id"),
            {"id": event.lead_id}
        )

        # Get lead info for notification
        lead = self.db.execute(
            text("SELECT company_name, email FROM leads WHERE id = :id"),
            {"id": event.lead_id}
        ).fetchone()

        # Notify admin
        if lead:
            self.db.execute(
                text("""
                    INSERT INTO admin_notifications (type, title, message, lead_id, created_at)
                    VALUES ('hot_lead', :title, :message, :lead_id, NOW())
                """),
                {
                    "title": "🔥 Email Link Clicked!",
                    "message": f"{lead[0]} clicked a link in your email. Score increased to reflect high interest.",
                    "lead_id": event.lead_id
                }
            )

        # Log activity
        self.db.execute(
            text("""
                INSERT INTO lead_activities (lead_id, activity_type, description, created_at)
                VALUES (:lead_id, 'email_clicked', :description, NOW())
            """),
            {
                "lead_id": event.lead_id,
                "description": f"Clicked link in email {event.email_id or 'unknown'}"
            }
        )
        self.db.commit()

        logger.info("email_click_processed", lead_id=event.lead_id)

    async def _handle_email_replied(self, event: MarketingEvent):
        """Handle email replied event - Convert to qualified!"""
        if not event.lead_id:
            return

        # Update status to QUALIFIED
        self.db.execute(
            text("UPDATE leads SET status = 'QUALIFIED', score = 100 WHERE id = :id"),
            {"id": event.lead_id}
        )

        # Stop any active sequences
        self.db.execute(
            text("""
                UPDATE sequence_enrollments
                SET status = 'completed', completed_at = NOW()
                WHERE lead_id = :lead_id AND status = 'active'
            """),
            {"lead_id": event.lead_id}
        )

        # Get lead info
        lead = self.db.execute(
            text("SELECT company_name, email FROM leads WHERE id = :id"),
            {"id": event.lead_id}
        ).fetchone()

        # Notify admin with high priority
        if lead:
            self.db.execute(
                text("""
                    INSERT INTO admin_notifications (type, title, message, lead_id, priority, created_at)
                    VALUES ('hot_lead', :title, :message, :lead_id, 'high', NOW())
                """),
                {
                    "title": "🎉 LEAD REPLIED!",
                    "message": f"{lead[0]} ({lead[1]}) replied to your email! Status updated to QUALIFIED. Call them NOW!",
                    "lead_id": event.lead_id
                }
            )

        self.db.commit()
        logger.info("email_reply_processed", lead_id=event.lead_id)

    async def _handle_lead_saved(self, event: MarketingEvent):
        """Handle new lead saved - Start onboarding workflow."""
        if not event.lead_id:
            return

        # Find welcome sequence
        welcome_seq = self.db.execute(
            text("SELECT id FROM email_sequences WHERE name ILIKE '%welcome%' AND is_active = true LIMIT 1")
        ).fetchone()

        if welcome_seq:
            # Enroll in welcome sequence
            self.db.execute(
                text("""
                    INSERT INTO sequence_enrollments (
                        lead_id, sequence_id, current_step, status, enrolled_at, next_step_at
                    ) VALUES (
                        :lead_id, :sequence_id, 1, 'active', NOW(), NOW() + INTERVAL '1 hour'
                    ) ON CONFLICT DO NOTHING
                """),
                {"lead_id": event.lead_id, "sequence_id": welcome_seq[0]}
            )

        # Trigger LinkedIn lookup (background task)
        self.db.execute(
            text("""
                INSERT INTO background_tasks (task_type, lead_id, status, created_at)
                VALUES ('find_linkedin', :lead_id, 'pending', NOW())
            """),
            {"lead_id": event.lead_id}
        )

        self.db.commit()
        logger.info("lead_saved_processed", lead_id=event.lead_id)

    async def _handle_lead_qualified(self, event: MarketingEvent):
        """Handle lead qualified - Schedule follow-up."""
        if not event.lead_id:
            return

        # Schedule call reminder for tomorrow
        self.db.execute(
            text("""
                INSERT INTO lead_activities (
                    lead_id, activity_type, description, scheduled_at, created_at
                ) VALUES (
                    :lead_id, 'call_scheduled',
                    'Qualified lead - Priority call reminder',
                    NOW() + INTERVAL '1 day', NOW()
                )
            """),
            {"lead_id": event.lead_id}
        )

        # Add to priority list
        self.db.execute(
            text("""
                UPDATE leads
                SET tags = COALESCE(tags, '[]'::jsonb) || '["qualified", "priority"]'::jsonb
                WHERE id = :id
            """),
            {"id": event.lead_id}
        )

        self.db.commit()
        logger.info("lead_qualified_processed", lead_id=event.lead_id)

    async def _handle_lead_converted(self, event: MarketingEvent):
        """Handle lead converted to customer."""
        if not event.lead_id:
            return

        # Update status
        self.db.execute(
            text("UPDATE leads SET status = 'WON' WHERE id = :id"),
            {"id": event.lead_id}
        )

        # Stop all sequences
        self.db.execute(
            text("""
                UPDATE sequence_enrollments
                SET status = 'completed', completed_at = NOW()
                WHERE lead_id = :lead_id
            """),
            {"lead_id": event.lead_id}
        )

        # Celebratory notification
        lead = self.db.execute(
            text("SELECT company_name FROM leads WHERE id = :id"),
            {"id": event.lead_id}
        ).fetchone()

        if lead:
            self.db.execute(
                text("""
                    INSERT INTO admin_notifications (type, title, message, lead_id, created_at)
                    VALUES ('conversion', :title, :message, :lead_id, NOW())
                """),
                {
                    "title": "🎊 NEW CUSTOMER!",
                    "message": f"Congratulations! {lead[0]} has been converted to a customer!",
                    "lead_id": event.lead_id
                }
            )

        self.db.commit()
        logger.info("lead_conversion_processed", lead_id=event.lead_id)


# Convenience function for emitting events
async def emit_marketing_event(
    db: Session,
    event_type: EventType,
    lead_id: Optional[int] = None,
    campaign_id: Optional[int] = None,
    **kwargs
):
    """Helper to emit marketing events."""
    bus = MarketingEventBus(db)
    event = MarketingEvent(
        event_type=event_type,
        lead_id=lead_id,
        campaign_id=campaign_id,
        data=kwargs
    )
    await bus.emit(event)
