"""
Quotes Domain Services - Business logic layer.

Gestisce tutta la business logic per il dominio quotes, inclusi:
- CRUD operations con automatic calculations
- Quote versioning
- Status workflow management
- Financial calculations
- PDF generation integration
- Email sending
"""

from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, and_

from .models import Quote, QuoteLineItem, QuoteVersion, QuoteStatus
from .schemas import (
    QuoteCreate,
    QuoteUpdate,
    QuoteResponse,
    QuoteListItem,
    QuoteLineItemCreate,
    QuoteLineItemUpdate,
    QuoteStats,
    QuoteFilters,
    QuoteSendRequest,
    QuoteAcceptRequest,
    QuoteRejectRequest,
    QuoteDuplicateRequest
)


class QuoteService:
    """
    Service layer for Quote domain.

    Gestisce tutte le operazioni di business logic relative ai preventivi.
    """

    def __init__(self, db: Session):
        """
        Initialize service with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    # ========================================================================
    # QUOTE NUMBER GENERATION
    # ========================================================================

    def _generate_quote_number(self, year: Optional[int] = None) -> str:
        """
        Generate unique quote number (format: QUOTE-YYYY-NNNN).

        Args:
            year: Year for quote number (default: current year)

        Returns:
            Generated quote number
        """
        if year is None:
            year = datetime.utcnow().year

        # Get last quote number for this year
        last_quote = self.db.query(Quote).filter(
            Quote.quote_number.like(f"QUOTE-{year}-%")
        ).order_by(desc(Quote.quote_number)).first()

        if last_quote:
            # Extract number and increment
            last_number = int(last_quote.quote_number.split('-')[-1])
            next_number = last_number + 1
        else:
            next_number = 1

        return f"QUOTE-{year}-{next_number:04d}"

    # ========================================================================
    # FINANCIAL CALCULATIONS
    # ========================================================================

    def _calculate_line_item_totals(self, line_item: QuoteLineItemCreate) -> dict:
        """
        Calculate totals for a line item.

        Args:
            line_item: Line item data

        Returns:
            Dict with discount_amount and subtotal
        """
        # Calculate base amount
        base_amount = line_item.quantity * line_item.unit_price

        # Calculate discount
        discount_amount = base_amount * (line_item.discount_percentage / Decimal('100'))

        # Calculate subtotal
        subtotal = base_amount - discount_amount

        return {
            'discount_amount': discount_amount,
            'subtotal': subtotal
        }

    def _calculate_quote_totals(self, quote: Quote) -> dict:
        """
        Calculate totals for a quote based on its line items.

        Args:
            quote: Quote instance with line_items loaded

        Returns:
            Dict with subtotal, tax_amount, discount_amount, total
        """
        # Sum line items subtotals
        items_subtotal = sum(
            (item.subtotal for item in quote.line_items),
            Decimal('0.00')
        )

        # Apply quote-level discount
        quote_discount = items_subtotal * (quote.discount_percentage / Decimal('100'))

        # Subtotal after discount
        subtotal_after_discount = items_subtotal - quote_discount

        # Calculate tax
        tax_amount = subtotal_after_discount * (quote.tax_rate / Decimal('100'))

        # Calculate total
        total = subtotal_after_discount + tax_amount

        return {
            'subtotal': items_subtotal,
            'discount_amount': quote_discount,
            'tax_amount': tax_amount,
            'total': total
        }

    # ========================================================================
    # CRUD OPERATIONS
    # ========================================================================

    def create_quote(
        self,
        data: QuoteCreate,
        created_by: int
    ) -> Quote:
        """
        Create a new quote with line items.

        Args:
            data: Quote creation data
            created_by: Admin user ID creating the quote

        Returns:
            Created quote instance
        """
        # Generate quote number
        quote_number = self._generate_quote_number()

        # Create quote
        quote_dict = data.model_dump(exclude={'line_items'})
        quote = Quote(
            **quote_dict,
            quote_number=quote_number,
            created_by=created_by,
            status=QuoteStatus.DRAFT.value,
            version=1,
            is_latest=True
        )

        self.db.add(quote)
        self.db.flush()  # Get quote.id

        # Add line items
        for idx, item_data in enumerate(data.line_items):
            # Calculate line item totals
            totals = self._calculate_line_item_totals(item_data)

            line_item = QuoteLineItem(
                quote_id=quote.id,
                **item_data.model_dump(),
                discount_amount=totals['discount_amount'],
                subtotal=totals['subtotal'],
                position=idx
            )
            self.db.add(line_item)

        self.db.flush()  # Load line items
        self.db.refresh(quote)

        # Calculate quote totals
        totals = self._calculate_quote_totals(quote)
        quote.subtotal = totals['subtotal']
        quote.discount_amount = totals['discount_amount']
        quote.tax_amount = totals['tax_amount']
        quote.total = totals['total']

        self.db.commit()
        self.db.refresh(quote)

        return quote

    def get_quote(self, quote_id: int) -> Optional[Quote]:
        """Get quote by ID (excluding soft-deleted)."""
        return self.db.query(Quote).filter(
            Quote.id == quote_id,
            Quote.is_deleted == False
        ).first()

    def list_quotes(
        self,
        filters: Optional[QuoteFilters] = None
    ) -> List[Quote]:
        """
        List quotes with optional filters.

        Args:
            filters: Filtering and pagination parameters

        Returns:
            List of quotes matching filters
        """
        if filters is None:
            filters = QuoteFilters()

        query = self.db.query(Quote).filter(
            Quote.is_deleted == False
        )

        # Apply customer filter
        if filters.customer_id:
            query = query.filter(Quote.customer_id == filters.customer_id)

        # Apply status filter
        if filters.status:
            query = query.filter(Quote.status == filters.status)

        # Apply currency filter
        if filters.currency:
            query = query.filter(Quote.currency == filters.currency)

        # Apply is_latest filter
        if filters.is_latest is not None:
            query = query.filter(Quote.is_latest == filters.is_latest)

        # Apply date range filters
        if filters.from_date:
            query = query.filter(Quote.issue_date >= filters.from_date)
        if filters.to_date:
            query = query.filter(Quote.issue_date <= filters.to_date)

        # Apply value range filters
        if filters.min_value:
            query = query.filter(Quote.total >= filters.min_value)
        if filters.max_value:
            query = query.filter(Quote.total <= filters.max_value)

        # Search in title/quote_number
        if filters.search:
            search_pattern = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Quote.title.ilike(search_pattern),
                    Quote.quote_number.ilike(search_pattern)
                )
            )

        # Order by creation date (newest first)
        query = query.order_by(desc(Quote.created_at))

        # Apply pagination
        query = query.offset(filters.skip).limit(filters.limit)

        return query.all()

    def count_quotes(self, filters: Optional[QuoteFilters] = None) -> int:
        """Count total quotes matching filters."""
        if filters is None:
            filters = QuoteFilters()

        query = self.db.query(func.count(Quote.id)).filter(
            Quote.is_deleted == False
        )

        # Apply same filters as list_quotes
        if filters.customer_id:
            query = query.filter(Quote.customer_id == filters.customer_id)
        if filters.status:
            query = query.filter(Quote.status == filters.status)
        if filters.currency:
            query = query.filter(Quote.currency == filters.currency)
        if filters.is_latest is not None:
            query = query.filter(Quote.is_latest == filters.is_latest)
        if filters.from_date:
            query = query.filter(Quote.issue_date >= filters.from_date)
        if filters.to_date:
            query = query.filter(Quote.issue_date <= filters.to_date)
        if filters.min_value:
            query = query.filter(Quote.total >= filters.min_value)
        if filters.max_value:
            query = query.filter(Quote.total <= filters.max_value)
        if filters.search:
            search_pattern = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Quote.title.ilike(search_pattern),
                    Quote.quote_number.ilike(search_pattern)
                )
            )

        return query.scalar()

    def update_quote(
        self,
        quote_id: int,
        data: QuoteUpdate
    ) -> Optional[Quote]:
        """
        Update quote (can only update DRAFT quotes).

        Args:
            quote_id: Quote ID to update
            data: Update data

        Returns:
            Updated quote or None if not found

        Raises:
            ValueError: If quote is not in DRAFT status
        """
        quote = self.get_quote(quote_id)
        if not quote:
            return None

        # Only allow updates to draft quotes
        if quote.status != QuoteStatus.DRAFT.value:
            raise ValueError("Can only update quotes in DRAFT status")

        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(quote, field, value)

        # Recalculate totals
        totals = self._calculate_quote_totals(quote)
        quote.subtotal = totals['subtotal']
        quote.discount_amount = totals['discount_amount']
        quote.tax_amount = totals['tax_amount']
        quote.total = totals['total']

        quote.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(quote)

        return quote

    def delete_quote(
        self,
        quote_id: int,
        deleted_by: int
    ) -> bool:
        """
        Soft delete a quote.

        Args:
            quote_id: Quote ID to delete
            deleted_by: Admin user ID performing deletion

        Returns:
            True if deleted, False if not found
        """
        quote = self.get_quote(quote_id)
        if not quote:
            return False

        quote.is_deleted = True
        quote.deleted_at = datetime.utcnow()
        quote.deleted_by = deleted_by

        self.db.commit()

        return True

    # ========================================================================
    # LINE ITEMS MANAGEMENT
    # ========================================================================

    def add_line_item(
        self,
        quote_id: int,
        data: QuoteLineItemCreate
    ) -> Optional[QuoteLineItem]:
        """
        Add a line item to a quote.

        Can only add to DRAFT quotes.
        """
        quote = self.get_quote(quote_id)
        if not quote:
            return None

        if quote.status != QuoteStatus.DRAFT.value:
            raise ValueError("Can only add line items to DRAFT quotes")

        # Calculate line item totals
        totals = self._calculate_line_item_totals(data)

        # Get next position
        max_position = self.db.query(func.max(QuoteLineItem.position)).filter(
            QuoteLineItem.quote_id == quote_id
        ).scalar() or 0

        line_item = QuoteLineItem(
            quote_id=quote_id,
            **data.model_dump(),
            discount_amount=totals['discount_amount'],
            subtotal=totals['subtotal'],
            position=max_position + 1
        )

        self.db.add(line_item)
        self.db.commit()
        self.db.refresh(line_item)

        # Recalculate quote totals
        self._recalculate_quote_totals(quote_id)

        return line_item

    def update_line_item(
        self,
        line_item_id: int,
        data: QuoteLineItemUpdate
    ) -> Optional[QuoteLineItem]:
        """Update a line item."""
        line_item = self.db.query(QuoteLineItem).filter(
            QuoteLineItem.id == line_item_id
        ).first()

        if not line_item:
            return None

        # Check quote status
        quote = self.get_quote(line_item.quote_id)
        if quote.status != QuoteStatus.DRAFT.value:
            raise ValueError("Can only update line items in DRAFT quotes")

        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(line_item, field, value)

        # Recalculate line item totals
        base_amount = line_item.quantity * line_item.unit_price
        line_item.discount_amount = base_amount * (line_item.discount_percentage / Decimal('100'))
        line_item.subtotal = base_amount - line_item.discount_amount

        self.db.commit()
        self.db.refresh(line_item)

        # Recalculate quote totals
        self._recalculate_quote_totals(line_item.quote_id)

        return line_item

    def delete_line_item(self, line_item_id: int) -> bool:
        """Delete a line item."""
        line_item = self.db.query(QuoteLineItem).filter(
            QuoteLineItem.id == line_item_id
        ).first()

        if not line_item:
            return False

        # Check quote status
        quote = self.get_quote(line_item.quote_id)
        if quote.status != QuoteStatus.DRAFT.value:
            raise ValueError("Can only delete line items from DRAFT quotes")

        quote_id = line_item.quote_id

        self.db.delete(line_item)
        self.db.commit()

        # Recalculate quote totals
        self._recalculate_quote_totals(quote_id)

        return True

    def _recalculate_quote_totals(self, quote_id: int):
        """Recalculate and update quote totals after line item changes."""
        quote = self.get_quote(quote_id)
        if not quote:
            return

        totals = self._calculate_quote_totals(quote)
        quote.subtotal = totals['subtotal']
        quote.discount_amount = totals['discount_amount']
        quote.tax_amount = totals['tax_amount']
        quote.total = totals['total']
        quote.updated_at = datetime.utcnow()

        self.db.commit()

    # ========================================================================
    # STATUS WORKFLOW
    # ========================================================================

    def send_quote(
        self,
        quote_id: int,
        request: Optional[QuoteSendRequest] = None
    ) -> Optional[Quote]:
        """
        Mark quote as sent and trigger email.

        Args:
            quote_id: Quote ID to send
            request: Optional send request with email overrides

        Returns:
            Updated quote or None if not found
        """
        quote = self.get_quote(quote_id)
        if not quote:
            return None

        # Only send DRAFT quotes
        if quote.status != QuoteStatus.DRAFT.value:
            raise ValueError("Can only send DRAFT quotes")

        # Generate PDF if not exists
        from .pdf_generator import generate_quote_pdf

        if not quote.pdf_file_path:
            pdf_path = generate_quote_pdf(quote)
            quote.pdf_file_path = pdf_path
            quote.pdf_generated_at = datetime.utcnow()

        # Send email
        from .email_service import send_quote_email

        to_email = request.customer_email if request and request.customer_email else quote.customer.email
        cc_emails = request.cc_emails if request else None
        custom_message = request.custom_message if request else None

        email_sent = send_quote_email(
            quote,
            to_email,
            cc_emails,
            custom_message
        )

        if not email_sent:
            raise ValueError("Failed to send quote email")

        # Update quote status
        quote.status = QuoteStatus.SENT.value
        quote.sent_at = datetime.utcnow()
        quote.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(quote)

        return quote

    def mark_viewed(self, quote_id: int) -> Optional[Quote]:
        """Mark quote as viewed by customer."""
        quote = self.get_quote(quote_id)
        if not quote:
            return None

        if quote.status == QuoteStatus.SENT.value and not quote.viewed_at:
            quote.status = QuoteStatus.VIEWED.value
            quote.viewed_at = datetime.utcnow()
            quote.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(quote)

        return quote

    def accept_quote(
        self,
        quote_id: int,
        request: QuoteAcceptRequest
    ) -> Optional[Quote]:
        """
        Accept a quote.

        Args:
            quote_id: Quote ID to accept
            request: Acceptance details

        Returns:
            Updated quote or None if not found
        """
        quote = self.get_quote(quote_id)
        if not quote:
            return None

        # Can accept SENT or VIEWED quotes
        if quote.status not in [QuoteStatus.SENT.value, QuoteStatus.VIEWED.value]:
            raise ValueError("Can only accept SENT or VIEWED quotes")

        quote.status = QuoteStatus.ACCEPTED.value
        quote.accepted_at = datetime.utcnow()
        quote.accepted_by_name = request.accepted_by_name
        quote.accepted_by_email = request.accepted_by_email
        quote.updated_at = datetime.utcnow()

        # Phase 2: Create project/contract from accepted quote
        # Phase 2: Update customer LTV via CustomerService.update_ltv()

        self.db.commit()
        self.db.refresh(quote)

        return quote

    def reject_quote(
        self,
        quote_id: int,
        request: QuoteRejectRequest
    ) -> Optional[Quote]:
        """Reject a quote."""
        quote = self.get_quote(quote_id)
        if not quote:
            return None

        if quote.status not in [QuoteStatus.SENT.value, QuoteStatus.VIEWED.value]:
            raise ValueError("Can only reject SENT or VIEWED quotes")

        quote.status = QuoteStatus.REJECTED.value
        quote.rejected_at = datetime.utcnow()
        quote.rejection_reason = request.rejection_reason
        quote.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(quote)

        return quote

    # ========================================================================
    # VERSIONING
    # ========================================================================

    def duplicate_quote(
        self,
        quote_id: int,
        request: QuoteDuplicateRequest,
        created_by: int
    ) -> Optional[Quote]:
        """
        Create a new version of a quote.

        Args:
            quote_id: Original quote ID
            request: Duplication request
            created_by: Admin user creating new version

        Returns:
            New quote version
        """
        original_quote = self.get_quote(quote_id)
        if not original_quote:
            return None

        # Mark original as not latest
        original_quote.is_latest = False

        # Create new quote (new version)
        new_version = original_quote.version + 1
        new_quote_number = self._generate_quote_number()

        new_quote = Quote(
            quote_number=new_quote_number,
            title=original_quote.title,
            description=original_quote.description,
            customer_id=original_quote.customer_id,
            version=new_version,
            is_latest=True,
            parent_quote_id=original_quote.id,
            currency=original_quote.currency,
            tax_rate=original_quote.tax_rate,
            discount_percentage=original_quote.discount_percentage,
            issue_date=date.today(),
            valid_until=date.today() + timedelta(days=30),
            payment_terms_days=original_quote.payment_terms_days,
            delivery_date=original_quote.delivery_date,
            payment_terms=original_quote.payment_terms,
            terms_and_conditions=original_quote.terms_and_conditions,
            notes_to_customer=original_quote.notes_to_customer,
            internal_notes = original_quote.internal_notes,
            status=QuoteStatus.DRAFT.value,
            created_by=created_by
        )

        self.db.add(new_quote)
        self.db.flush()

        # Copy line items
        for idx, item in enumerate(original_quote.line_items):
            new_item = QuoteLineItem(
                quote_id=new_quote.id,
                name=item.name,
                description=item.description,
                sku=item.sku,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount_percentage=item.discount_percentage,
                discount_amount=item.discount_amount,
                subtotal=item.subtotal,
                position=idx
            )
            self.db.add(new_item)

        self.db.flush()
        self.db.refresh(new_quote)

        # Recalculate totals
        totals = self._calculate_quote_totals(new_quote)
        new_quote.subtotal = totals['subtotal']
        new_quote.discount_amount = totals['discount_amount']
        new_quote.tax_amount = totals['tax_amount']
        new_quote.total = totals['total']

        # Create version record
        version_record = QuoteVersion(
            original_quote_id=original_quote.id,
            new_quote_id=new_quote.id,
            version_number=new_version,
            changes_summary=request.changes_summary,
            reason=request.reason,
            created_by=created_by
        )
        self.db.add(version_record)

        self.db.commit()
        self.db.refresh(new_quote)

        return new_quote

    # ========================================================================
    # ANALYTICS & STATS
    # ========================================================================

    def get_quote_stats(self) -> QuoteStats:
        """Get quote statistics."""
        # Total quotes (latest versions only, non-deleted)
        total = self.db.query(func.count(Quote.id)).filter(
            Quote.is_deleted == False,
            Quote.is_latest == True
        ).scalar()

        # By status
        by_status = {}
        status_counts = self.db.query(
            Quote.status,
            func.count(Quote.id)
        ).filter(
            Quote.is_deleted == False,
            Quote.is_latest == True
        ).group_by(Quote.status).all()

        for status, count in status_counts:
            by_status[status] = count

        # Total value
        total_value = self.db.query(
            func.coalesce(func.sum(Quote.total), 0)
        ).filter(
            Quote.is_deleted == False,
            Quote.is_latest == True
        ).scalar() or Decimal('0.00')

        # Accepted value
        accepted_value = self.db.query(
            func.coalesce(func.sum(Quote.total), 0)
        ).filter(
            Quote.is_deleted == False,
            Quote.status == QuoteStatus.ACCEPTED.value
        ).scalar() or Decimal('0.00')

        # Conversion rate
        total_sent = by_status.get(QuoteStatus.SENT.value, 0) + \
                     by_status.get(QuoteStatus.VIEWED.value, 0) + \
                     by_status.get(QuoteStatus.ACCEPTED.value, 0) + \
                     by_status.get(QuoteStatus.REJECTED.value, 0)

        conversion_rate = Decimal('0.00')
        if total_sent > 0:
            conversion_rate = (Decimal(by_status.get(QuoteStatus.ACCEPTED.value, 0)) / Decimal(total_sent)) * Decimal('100')

        # Average quote value
        avg_value = Decimal('0.00')
        if total > 0:
            avg_value = total_value / Decimal(total)

        # Average conversion time
        avg_conversion_time = self.db.query(
            func.avg(
                func.extract('epoch', Quote.accepted_at - Quote.sent_at) / 86400
            )
        ).filter(
            Quote.is_deleted == False,
            Quote.status == QuoteStatus.ACCEPTED.value,
            Quote.sent_at.isnot(None),
            Quote.accepted_at.isnot(None)
        ).scalar()

        return QuoteStats(
            total_quotes=total,
            by_status=by_status,
            total_value=total_value,
            accepted_value=accepted_value,
            conversion_rate=conversion_rate,
            avg_quote_value=avg_value,
            avg_conversion_time_days=Decimal(str(avg_conversion_time)) if avg_conversion_time else None
        )


# Helper function to get service instance
def get_quote_service(db: Session) -> QuoteService:
    """
    Factory function to get QuoteService instance.

    Args:
        db: Database session

    Returns:
        QuoteService instance
    """
    return QuoteService(db)
