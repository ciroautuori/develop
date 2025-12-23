"""Support dependencies - Dependency injection configuration."""

from app.domain.support.repository import SupportTicketRepository
from app.domain.support.services import SupportTicketService


def get_support_ticket_service() -> SupportTicketService:
    """Dependency injection for SupportTicketService.
    
    Returns:
        SupportTicketService instance with repository dependency
    """
    repository = SupportTicketRepository()
    return SupportTicketService(repository=repository)
