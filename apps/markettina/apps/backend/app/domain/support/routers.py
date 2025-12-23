"""
Support Domain Routers
API endpoints for AI Customer Support
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.api.dependencies.auth_deps import get_current_user
from app.domain.auth.models import User
from app.infrastructure.database.session import get_db

from .ai_proxy import AICustomerSupport  # Proxy to AI Microservice
from .dependencies import get_support_ticket_service
from .schemas import (
    ChatRequest,
    ChatResponse,
    SupportTicketSchema,
    TicketCreateRequest,
    TicketListResponse,
    TicketStatusEnum,
)
from .services import SupportTicketService

router = APIRouter(prefix="/support", tags=["Support"])


@router.post("/chat/public", response_model=ChatResponse)
async def public_chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """
    Public chat with AI assistant (no authentication required)
    For landing page visitors - creates anonymous tickets
    """
    try:
        ai_service = AICustomerSupport()

        # Generate AI response without user context
        ai_response = await ai_service.generate_response(
            message=request.message,
            context=request.context or "MARKETTINA Landing Page Support",
            provider=request.provider or "gemini",
        )

        # Create anonymous ticket (user_id = None for public)
        # Note: This creates a guest/anonymous ticket that can be claimed later
        ticket_data = TicketCreateRequest(
            title=(
                request.message[:100] + "..." if len(request.message) > 100 else request.message
            ),
            message=request.message,
        )

        # For public chat, we don't save to database unless explicitly needed
        # Return response with temporary ticket_id for conversation continuity
        import hashlib
        import time
        temp_ticket_id = int(hashlib.md5(f"{request.message}{time.time()}".encode()).hexdigest()[:8], 16)

        return ChatResponse(
            response=ai_response["response"],
            confidence=ai_response["confidence"],
            provider=ai_response["provider"],
            ticket_id=temp_ticket_id,  # Temporary ID for session
            sentiment=ai_response.get("sentiment"),
            processing_time=ai_response.get("processing_time"),
        )

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Public chat failed: {e}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service temporarily unavailable. Please try again or contact info@markettina.it"
        )


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: Annotated[SupportTicketService, Depends(get_support_ticket_service)] = None,
):
    """
    Chat with AI assistant
    Creates new ticket or continues existing conversation
    """
    try:
        ai_service = AICustomerSupport()

        # Get conversation context if ticket exists
        context = None
        if request.ticket_id:
            ticket = service.get_ticket_by_id(db, request.ticket_id, current_user.id)
            if not ticket:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
                )
            context = service.get_ticket_context(db, request.ticket_id)

        # Generate AI response
        ai_response = await ai_service.generate_response(
            message=request.message,
            context=context or request.context,
            provider=request.provider or "gemini",
        )

        # Create or update ticket
        if request.ticket_id:
            # Add user message
            service.add_message_to_ticket(
                db=db, ticket_id=request.ticket_id, content=request.message, is_ai=False
            )

            # Add AI response
            service.add_message_to_ticket(
                db=db,
                ticket_id=request.ticket_id,
                content=ai_response["response"],
                is_ai=True,
                ai_metadata=ai_response,
            )

            ticket_id = request.ticket_id
        else:
            # Create new ticket
            ticket_data = TicketCreateRequest(
                title=(
                    request.message[:100] + "..." if len(request.message) > 100 else request.message
                ),
                message=request.message,
            )

            ticket = service.create_ticket(
                db=db, user_id=current_user.id, ticket_data=ticket_data, ai_response=ai_response
            )

            ticket_id = ticket.id

        return ChatResponse(
            response=ai_response["response"],
            confidence=ai_response["confidence"],
            provider=ai_response["provider"],
            ticket_id=ticket_id,
            sentiment=ai_response.get("sentiment"),
            processing_time=ai_response.get("processing_time"),
        )

    except Exception:


        import logging


        logger = logging.getLogger(__name__)


        logger.error("Operation failed", exc_info=True)


        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Operation failed. Please try again later."
        )

@router.post("/tickets", response_model=SupportTicketSchema)
async def create_ticket(
    ticket_data: TicketCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: Annotated[SupportTicketService, Depends(get_support_ticket_service)] = None,
):
    """Create a new support ticket"""
    try:
        # Generate AI response for initial message
        ai_service = AICustomerSupport()
        ai_response = await ai_service.generate_response(
            message=ticket_data.message, provider="gemini"
        )

        ticket = service.create_ticket(
            db=db, user_id=current_user.id, ticket_data=ticket_data, ai_response=ai_response
        )

        return ticket

    except Exception:


        import logging


        logger = logging.getLogger(__name__)


        logger.error("Operation failed", exc_info=True)


        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Operation failed. Please try again later.",
        )


@router.get("/tickets", response_model=TicketListResponse)
async def get_my_tickets(
    skip: int = 0,
    limit: int = 20,
    status: TicketStatusEnum = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: Annotated[SupportTicketService, Depends(get_support_ticket_service)] = None,
):
    """Get current user's support tickets"""
    from .models import TicketStatus as TicketStatusModel

    status_filter = None
    if status:
        status_filter = TicketStatusModel(status.value)

    tickets, total = service.get_user_tickets(
        db=db, user_id=current_user.id, skip=skip, limit=limit, status=status_filter
    )

    return TicketListResponse(
        tickets=tickets, total=total, page=skip // limit + 1 if limit > 0 else 1, page_size=limit
    )


@router.get("/tickets/{ticket_id}", response_model=SupportTicketSchema)
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: Annotated[SupportTicketService, Depends(get_support_ticket_service)] = None,
):
    """Get specific ticket by ID"""
    ticket = service.get_ticket_by_id(db, ticket_id, current_user.id)

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    return ticket


@router.patch("/tickets/{ticket_id}/status", response_model=SupportTicketSchema)
async def update_ticket_status(
    ticket_id: int,
    status: TicketStatusEnum,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: Annotated[SupportTicketService, Depends(get_support_ticket_service)] = None,
):
    """Update ticket status"""
    from .models import TicketStatus as TicketStatusModel

    ticket = service.update_ticket_status(
        db=db, ticket_id=ticket_id, status=TicketStatusModel(status.value), user_id=current_user.id
    )

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    return ticket
