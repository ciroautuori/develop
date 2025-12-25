"""
Quotes Domain API Routes - RESTful endpoints.

Espone tutti gli endpoint API per la gestione preventivi.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.infrastructure.database.session import get_db
from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.domain.auth.admin_models import AdminUser

from .schemas import (
    QuoteCreate,
    QuoteUpdate,
    QuoteResponse,
    QuoteListItem,
    QuoteLineItemCreate,
    QuoteLineItemUpdate,
    QuoteLineItemResponse,
    QuoteStats,
    QuoteFilters,
    QuoteSendRequest,
    QuoteAcceptRequest,
    QuoteRejectRequest,
    QuoteDuplicateRequest,
)
from .services import QuoteService


router = APIRouter(
    prefix="/api/v1/admin/quotes",
    tags=["quotes"],
    dependencies=[Depends(get_current_admin_user)]
)


# ============================================================================
# QUOTE CRUD ENDPOINTS
# ============================================================================

@router.post(
    "/",
    response_model=QuoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new quote",
    description="Create a new quote with line items. Automatically calculates totals."
)
async def create_quote(
    data: QuoteCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Create a new quote.

    - **title**: Quote title (required)
    - **customer_id**: Customer ID (required)
    - **line_items**: List of line items (required, min 1)
    - Automatically generates quote_number (QUOTE-YYYY-NNNN)
    - Automatically calculates subtotal, tax, discount, total

    Returns the created quote with ID and calculated totals.
    """
    service = QuoteService(db)

    try:
        quote = service.create_quote(
            data=data,
            created_by=current_user.id
        )
        return quote
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=List[QuoteListItem],
    summary="List quotes",
    description="Get paginated list of quotes with optional filters"
)
async def list_quotes(
    customer_id: int = Query(None, description="Filter by customer ID"),
    status_filter: str = Query(None, alias="status", description="Filter by status"),
    currency: str = Query(None, description="Filter by currency"),
    is_latest: bool = Query(None, description="Only latest versions"),
    from_date: str = Query(None, description="From issue date (YYYY-MM-DD)"),
    to_date: str = Query(None, description="To issue date (YYYY-MM-DD)"),
    min_value: float = Query(None, ge=0, description="Min total value"),
    max_value: float = Query(None, ge=0, description="Max total value"),
    search: str = Query(None, description="Search in title, quote_number"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    List quotes with filters and pagination.

    Returns lightweight quote list items.
    """
    service = QuoteService(db)

    filters = QuoteFilters(
        customer_id=customer_id,
        status=status_filter,
        currency=currency,
        is_latest=is_latest,
        from_date=from_date,
        to_date=to_date,
        min_value=min_value,
        max_value=max_value,
        search=search,
        skip=skip,
        limit=limit
    )

    quotes = service.list_quotes(filters=filters)

    return quotes


@router.get(
    "/count",
    response_model=dict,
    summary="Count quotes",
    description="Get total count of quotes matching filters"
)
async def count_quotes(
    customer_id: int = Query(None),
    status_filter: str = Query(None, alias="status"),
    currency: str = Query(None),
    is_latest: bool = Query(None),
    from_date: str = Query(None),
    to_date: str = Query(None),
    min_value: float = Query(None, ge=0),
    max_value: float = Query(None, ge=0),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Get count of quotes matching filters."""
    service = QuoteService(db)

    filters = QuoteFilters(
        customer_id=customer_id,
        status=status_filter,
        currency=currency,
        is_latest=is_latest,
        from_date=from_date,
        to_date=to_date,
        min_value=min_value,
        max_value=max_value,
        search=search
    )

    total = service.count_quotes(filters=filters)

    return {"total": total}


@router.get(
    "/{quote_id}",
    response_model=QuoteResponse,
    summary="Get quote details",
    description="Get full quote details by ID including line items"
)
async def get_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Get quote by ID with full details.

    Returns complete quote information including all line items.
    """
    service = QuoteService(db)

    quote = service.get_quote(quote_id)

    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quote {quote_id} not found"
        )

    return quote


@router.put(
    "/{quote_id}",
    response_model=QuoteResponse,
    summary="Update quote",
    description="Update quote details (only DRAFT quotes can be updated)"
)
async def update_quote(
    quote_id: int,
    data: QuoteUpdate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Update quote.

    Can only update DRAFT quotes. For SENT/VIEWED quotes, create a new version instead.
    """
    service = QuoteService(db)

    try:
        quote = service.update_quote(quote_id, data)

        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote {quote_id} not found"
            )

        return quote
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{quote_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete quote",
    description="Soft delete a quote"
)
async def delete_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Soft delete a quote."""
    service = QuoteService(db)

    success = service.delete_quote(quote_id, deleted_by=current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quote {quote_id} not found"
        )

    return None


# ============================================================================
# LINE ITEMS ENDPOINTS
# ============================================================================

@router.post(
    "/{quote_id}/line-items",
    response_model=QuoteLineItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add line item to quote",
    description="Add a new line item to a DRAFT quote"
)
async def add_line_item(
    quote_id: int,
    data: QuoteLineItemCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Add a line item to quote. Quote totals will be recalculated."""
    service = QuoteService(db)

    try:
        line_item = service.add_line_item(quote_id, data)

        if not line_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote {quote_id} not found"
            )

        return line_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/line-items/{line_item_id}",
    response_model=QuoteLineItemResponse,
    summary="Update line item",
    description="Update a line item (only in DRAFT quotes)"
)
async def update_line_item(
    line_item_id: int,
    data: QuoteLineItemUpdate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Update a line item. Quote totals will be recalculated."""
    service = QuoteService(db)

    try:
        line_item = service.update_line_item(line_item_id, data)

        if not line_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Line item {line_item_id} not found"
            )

        return line_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/line-items/{line_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete line item",
    description="Delete a line item from a quote"
)
async def delete_line_item(
    line_item_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Delete a line item. Quote totals will be recalculated."""
    service = QuoteService(db)

    try:
        success = service.delete_line_item(line_item_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Line item {line_item_id} not found"
            )

        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# QUOTE ACTIONS ENDPOINTS
# ============================================================================

@router.post(
    "/{quote_id}/send",
    response_model=QuoteResponse,
    summary="Send quote to customer",
    description="Mark quote as SENT and trigger email to customer"
)
async def send_quote(
    quote_id: int,
    request: QuoteSendRequest = None,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Send quote to customer.

    This will:
    - Mark quote as SENT
    - Generate PDF if not exists
    - Send email to customer (via email_service)
    """
    service = QuoteService(db)

    try:
        quote = service.send_quote(quote_id, request)

        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote {quote_id} not found"
            )

        return quote
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{quote_id}/viewed",
    response_model=QuoteResponse,
    summary="Mark quote as viewed",
    description="Mark that customer has viewed the quote"
)
async def mark_quote_viewed(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Mark quote as viewed by customer."""
    service = QuoteService(db)

    quote = service.mark_viewed(quote_id)

    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quote {quote_id} not found"
        )

    return quote


@router.post(
    "/{quote_id}/accept",
    response_model=QuoteResponse,
    summary="Accept quote",
    description="Mark quote as accepted by customer"
)
async def accept_quote(
    quote_id: int,
    request: QuoteAcceptRequest,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Accept a quote.

    This will:
    - Mark quote as ACCEPTED
    - Record acceptance details
    - Update customer LTV (via CustomerService)
    - Create project/contract (Phase 2)
    """
    service = QuoteService(db)

    try:
        quote = service.accept_quote(quote_id, request)

        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote {quote_id} not found"
            )

        return quote
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{quote_id}/reject",
    response_model=QuoteResponse,
    summary="Reject quote",
    description="Mark quote as rejected by customer"
)
async def reject_quote(
    quote_id: int,
    request: QuoteRejectRequest,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Reject a quote with reason."""
    service = QuoteService(db)

    try:
        quote = service.reject_quote(quote_id, request)

        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote {quote_id} not found"
            )

        return quote
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# VERSIONING ENDPOINTS
# ============================================================================

@router.post(
    "/{quote_id}/duplicate",
    response_model=QuoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new quote version",
    description="Duplicate quote to create a new version (for negotiations)"
)
async def duplicate_quote(
    quote_id: int,
    request: QuoteDuplicateRequest,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Create a new version of a quote.

    This will:
    - Mark original quote as not latest
    - Create new quote with incremented version number
    - Copy all line items
    - Set status to DRAFT
    - Create version record for audit
    """
    service = QuoteService(db)

    try:
        new_quote = service.duplicate_quote(
            quote_id=quote_id,
            request=request,
            created_by=current_user.id
        )

        if not new_quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quote {quote_id} not found"
            )

        return new_quote
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get(
    "/stats/overview",
    response_model=QuoteStats,
    summary="Get quote statistics",
    description="Get aggregated quote statistics for dashboard"
)
async def get_quote_stats(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Get quote statistics:
    - Total quotes (latest versions)
    - Breakdown by status
    - Total and accepted value
    - Conversion rate
    - Average quote value
    - Average time to accept
    """
    service = QuoteService(db)

    stats = service.get_quote_stats()

    return stats
