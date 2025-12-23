"""
Support Domain Services
Business logic for support tickets and AI interactions
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from .ai_proxy import AICustomerSupport
from .models import SupportMessage, SupportTicket, TicketPriority, TicketStatus
from .repository import SupportTicketRepository
from .schemas import ChatRequest, TicketCreateRequest


class SupportTicketService:
    """Support Ticket Service with repository pattern."""

    def __init__(self, repository: SupportTicketRepository):
        """
        Initialize service with repository dependency.

        Args:
            repository: SupportTicketRepository instance
        """
        self.repository = repository

    def create_ticket(
        self,
        db: Session,
        user_id: int,
        ticket_data: TicketCreateRequest,
        ai_response: Optional[dict] = None,
    ) -> SupportTicket:
        """Create a new support ticket"""
        ticket = SupportTicket(
            user_id=user_id,
            tenant_id=f"tenant_{user_id}",  # Set tenant_id for multi-tenancy
            title=ticket_data.title,
            priority=ticket_data.priority,
            status=TicketStatus.OPEN,
            ai_handled=True if ai_response else False,
            ai_confidence=ai_response.get("confidence") if ai_response else None,
            ai_provider=ai_response.get("provider") if ai_response else None,
            sentiment=ai_response.get("sentiment") if ai_response else None,
        )

        ticket = self.repository.create_ticket(db, ticket)

        # Add initial user message
        user_message = SupportMessage(
            ticket_id=ticket.id,
            tenant_id=f"tenant_{user_id}",
            content=ticket_data.message,
            is_ai=False,
            is_staff=False
        )
        self.repository.create_message(db, user_message)

        # Add AI response if available
        if ai_response:
            ai_message = SupportMessage(
                ticket_id=ticket.id,
                tenant_id=f"tenant_{user_id}",
                content=ai_response.get("response", ""),
                is_ai=True,
                is_staff=False,
                ai_confidence=ai_response.get("confidence"),
                ai_provider=ai_response.get("provider"),
                processing_time=ai_response.get("processing_time"),
            )
            self.repository.create_message(db, ai_message)

        db.commit()
        db.refresh(ticket)

        return ticket

    def add_message_to_ticket(
        self,
        db: Session,
        ticket_id: int,
        content: str,
        is_ai: bool = False,
        is_staff: bool = False,
        ai_metadata: Optional[dict] = None,
    ) -> SupportMessage:
        """Add a message to existing ticket"""
        # Get ticket to extract user_id for tenant_id
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        message = SupportMessage(
            ticket_id=ticket_id,
            tenant_id=f"tenant_{ticket.user_id}",
            content=content,
            is_ai=is_ai,
            is_staff=is_staff,
            ai_confidence=ai_metadata.get("confidence") if ai_metadata else None,
            ai_provider=ai_metadata.get("provider") if ai_metadata else None,
            processing_time=ai_metadata.get("processing_time") if ai_metadata else None,
        )

        self.repository.create_message(db, message)

        # Update ticket metadata
        ticket = self.repository.get_by_id(db, ticket_id)
        if ticket and ai_metadata:
            ticket.ai_confidence = ai_metadata.get("confidence")
            ticket.ai_provider = ai_metadata.get("provider")
            ticket.sentiment = ai_metadata.get("sentiment")
            self.repository.update_ticket(db, ticket)

        db.commit()
        db.refresh(message)

        return message

    def get_user_tickets(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[TicketStatus] = None,
    ) -> tuple[List[SupportTicket], int]:
        """Get user's support tickets"""
        return self.repository.get_user_tickets(db, user_id, skip, limit, status)

    def get_ticket_by_id(self, db: Session, ticket_id: int, user_id: int) -> Optional[SupportTicket]:
        """Get ticket by ID (with user ownership check)"""
        return self.repository.get_by_id_and_user(db, ticket_id, user_id)

    def update_ticket_status(
        self,
        db: Session, ticket_id: int, status: TicketStatus, user_id: Optional[int] = None
    ) -> Optional[SupportTicket]:
        """Update ticket status"""
        if user_id:
            ticket = self.repository.get_by_id_and_user(db, ticket_id, user_id)
        else:
            ticket = self.repository.get_by_id(db, ticket_id)

        if ticket:
            ticket.status = status

            if status == TicketStatus.RESOLVED or status == TicketStatus.CLOSED:
                ticket.resolved_at = datetime.now(timezone.utc)

            self.repository.update_ticket(db, ticket)
            db.commit()
            db.refresh(ticket)

        return ticket

    def get_ticket_context(self, db: Session, ticket_id: int) -> str:
        """Get conversation context for AI"""
        ticket = self.repository.get_by_id(db, ticket_id)

        if not ticket or not ticket.messages:
            return ""

        # Get last 5 messages for context
        recent_messages = ticket.messages[-5:]

        context_parts = []
        for msg in recent_messages:
            sender = "AI" if msg.is_ai else ("Staff" if msg.is_staff else "User")
            context_parts.append(f"{sender}: {msg.content}")

        return "\n".join(context_parts)

    # AI TICKET ROUTING & PRIORITY SYSTEM

    def route_ticket_with_ai(
        self,
        db: Session,
        ticket: SupportTicket
    ) -> Dict[str, str]:
        """Use AI to automatically route ticket to appropriate department/category."""
        from .ai_proxy import AICustomerSupport

        ai_service = AICustomerSupport()

        # Analyze ticket content
        first_message = ticket.messages[0] if ticket.messages else None
        if not first_message:
            return {"category": "general", "department": "support", "confidence": 0.0}

        message_content = first_message.content

        # Use AI to categorize
        try:
            # Keywords mapping for routing
            categories = {
                "billing": ["payment", "invoice", "subscription", "charge", "refund", "pricing"],
                "technical": ["error", "bug", "crash", "broken", "not working", "issue"],
                "account": ["login", "password", "access", "profile", "settings"],
                "feature": ["feature", "request", "suggestion", "improvement"],
                "general": []
            }

            # Simple keyword-based routing (can be enhanced with ML model)
            message_lower = message_content.lower()
            category_scores = {}

            for category, keywords in categories.items():
                score = sum(1 for keyword in keywords if keyword in message_lower)
                category_scores[category] = score

            # Get category with highest score
            best_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[best_category] / max(sum(category_scores.values()), 1)

            # Map to departments
            department_map = {
                "billing": "finance",
                "technical": "engineering",
                "account": "support",
                "feature": "product",
                "general": "support"
            }

            department = department_map.get(best_category, "support")

            logger.info(f"Routed ticket {ticket.id} to {department}/{best_category} (confidence: {confidence:.2f})")

            return {
                "category": best_category,
                "department": department,
                "confidence": confidence,
                "routing_reason": f"Keywords matched for {best_category} category"
            }

        except Exception as e:
            logger.error(f"AI routing failed for ticket {ticket.id}: {e}")
            return {"category": "general", "department": "support", "confidence": 0.0}

    def calculate_ticket_priority(
        self,
        db: Session,
        ticket: SupportTicket
    ) -> TicketPriority:
        """Automatically calculate ticket priority based on multiple factors."""
        from app.domain.auth.models import User, UserRole
        from app.domain.billing.models import Subscription, SubscriptionStatus

        score = 0  # Base priority score

        # Factor 1: Urgency keywords
        if ticket.messages:
            first_message = ticket.messages[0].content.lower()

            urgent_keywords = ["urgent", "critical", "asap", "immediately", "emergency"]
            high_keywords = ["important", "soon", "quickly"]

            if any(keyword in first_message for keyword in urgent_keywords):
                score += 30
            elif any(keyword in first_message for keyword in high_keywords):
                score += 20

        # Factor 2: User subscription level
        user = db.query(User).filter(User.id == ticket.user_id).first()
        if user:
            if user.role == UserRole.PRO:
                score += 25  # PRO users get higher priority
            elif user.role == UserRole.CUSTOMER:
                score += 15
            elif user.role == UserRole.ADMIN:
                score += 20

        # Factor 3: AI sentiment analysis
        if ticket.sentiment:
            sentiment_lower = ticket.sentiment.lower()
            if "negative" in sentiment_lower or "angry" in sentiment_lower:
                score += 15  # Unhappy customers get higher priority

        # Factor 4: Ticket age (older tickets get priority boost)
        from datetime import timezone, timedelta
        if ticket.created_at:
            age = datetime.now(timezone.utc) - ticket.created_at
            if age > timedelta(hours=24):
                score += 10
            if age > timedelta(hours=48):
                score += 15

        # Convert score to priority
        if score >= 50:
            priority = TicketPriority.CRITICAL
        elif score >= 30:
            priority = TicketPriority.HIGH
        elif score >= 15:
            priority = TicketPriority.MEDIUM
        else:
            priority = TicketPriority.LOW

        logger.info(f"Calculated priority for ticket {ticket.id}: {priority.value} (score: {score})")

        return priority

    def auto_assign_priority_and_route(
        self,
        db: Session,
        ticket_id: int
    ) -> Dict[str, Any]:
        """Automatically assign priority and route ticket using AI."""
        ticket = self.repository.get_by_id(db, ticket_id)

        if not ticket:
            return {"error": "Ticket not found"}

        # Calculate priority
        new_priority = self.calculate_ticket_priority(db, ticket)

        # Route ticket
        routing_info = self.route_ticket_with_ai(db, ticket)

        # Update ticket
        ticket.priority = new_priority
        db.commit()
        db.refresh(ticket)

        return {
            "ticket_id": ticket.id,
            "priority": new_priority.value,
            "routing": routing_info,
            "auto_assigned": True
        }
