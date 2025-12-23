"""Support Ticket Repository
Data access layer for support tickets and messages.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.support.models import SupportMessage, SupportTicket, TicketStatus


class SupportTicketRepository:
    """Repository for SupportTicket and SupportMessage data access."""

    @staticmethod
    def get_by_id(db: Session, ticket_id: int) -> Optional[SupportTicket]:
        """
        Get ticket by ID.

        Args:
            db: Database session
            ticket_id: Ticket ID

        Returns:
            SupportTicket if found, None otherwise
        """
        return db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()

    @staticmethod
    def get_by_id_and_user(
        db: Session, ticket_id: int, user_id: int
    ) -> Optional[SupportTicket]:
        """
        Get ticket by ID with user ownership check.

        Args:
            db: Database session
            ticket_id: Ticket ID
            user_id: User ID for ownership verification

        Returns:
            SupportTicket if found and owned by user, None otherwise
        """
        return (
            db.query(SupportTicket)
            .filter(SupportTicket.id == ticket_id, SupportTicket.user_id == user_id)
            .first()
        )

    @staticmethod
    def get_user_tickets(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[TicketStatus] = None,
    ) -> tuple[List[SupportTicket], int]:
        """
        Get user's support tickets with pagination and optional status filter.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            status: Optional status filter

        Returns:
            Tuple of (tickets list, total count)
        """
        query = db.query(SupportTicket).filter(SupportTicket.user_id == user_id)

        if status:
            query = query.filter(SupportTicket.status == status)

        total = query.count()
        tickets = query.order_by(SupportTicket.created_at.desc()).offset(skip).limit(limit).all()

        return tickets, total

    @staticmethod
    def create_ticket(db: Session, ticket: SupportTicket) -> SupportTicket:
        """
        Create new support ticket.

        Args:
            db: Database session
            ticket: SupportTicket instance to create

        Returns:
            Created SupportTicket with ID assigned
        """
        db.add(ticket)
        db.flush()
        return ticket

    @staticmethod
    def create_message(db: Session, message: SupportMessage) -> SupportMessage:
        """
        Create new support message.

        Args:
            db: Database session
            message: SupportMessage instance to create

        Returns:
            Created SupportMessage
        """
        db.add(message)
        return message

    @staticmethod
    def update_ticket(db: Session, ticket: SupportTicket) -> SupportTicket:
        """
        Update existing ticket.

        Args:
            db: Database session
            ticket: SupportTicket instance with updates

        Returns:
            Updated SupportTicket
        """
        # SQLAlchemy tracks changes automatically
        db.flush()
        return ticket
