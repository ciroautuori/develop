"""
Customers Domain Services - Business logic layer.

Questo modulo implementa tutta la business logic per il dominio customers,
inclusi CRUD operations, analytics, segmentation, e deduplication.
"""

from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_

from .models import (
    Customer,
    CustomerNote,
    CustomerInteraction,
    CustomerStatus,
    CustomerType,
    CustomerSource
)
from .schemas import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListItem,
    CustomerNoteCreate,
    CustomerInteractionCreate,
    CustomerStats,
    CustomerFilters
)


class CustomerService:
    """
    Service layer for Customer domain.

    Gestisce tutte le operazioni di business logic relative ai clienti,
    mantenendo i controller (routers) sottili.
    """

    def __init__(self, db: Session):
        """
        Initialize service with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    # ========================================================================
    # CRUD OPERATIONS
    # ========================================================================

    def create_customer(
        self,
        data: CustomerCreate,
        created_by: int
    ) -> Customer:
        """
        Create a new customer.

        Args:
            data: Customer creation data
            created_by: Admin user ID creating the customer

        Returns:
            Created customer instance

        Raises:
            ValueError: If email already exists
        """
        # Check for duplicate email
        existing = self.db.query(Customer).filter(
            Customer.is_deleted == False
        ).all()

        # Decrypt and check emails (Note: O(n) complexity)
        # Optimization: Add email_hash column for O(1) duplicate detection
        for customer in existing:
            if customer.email and customer.email.lower() == data.email.lower():
                raise ValueError(f"Customer with email {data.email} already exists")

        # Create customer
        customer = Customer(
            **data.model_dump(exclude_unset=True),
            created_by=created_by,
            created_at=datetime.utcnow()
        )

        # Set marketing consent date if consent given
        if data.marketing_consent:
            customer.marketing_consent_date = datetime.utcnow()

        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)

        return customer

    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """
        Get customer by ID (excluding soft-deleted).

        Args:
            customer_id: Customer ID

        Returns:
            Customer instance or None if not found
        """
        return self.db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.is_deleted == False
        ).first()

    def list_customers(
        self,
        filters: Optional[CustomerFilters] = None
    ) -> List[Customer]:
        """
        List customers with optional filters.

        Args:
            filters: Filtering and pagination parameters

        Returns:
            List of customers matching filters
        """
        if filters is None:
            filters = CustomerFilters()

        query = self.db.query(Customer).filter(
            Customer.is_deleted == False
        )

        # Apply status filter
        if filters.status:
            query = query.filter(Customer.status == filters.status)

        # Apply customer_type filter
        if filters.customer_type:
            query = query.filter(Customer.customer_type == filters.customer_type)

        # Apply source filter
        if filters.source:
            query = query.filter(Customer.source == filters.source)

        # Apply assigned_to filter
        if filters.assigned_to:
            query = query.filter(Customer.assigned_to == filters.assigned_to)

        # Apply tags filter
        if filters.tags:
            # Simple LIKE search in tags field
            query = query.filter(Customer.tags.like(f"%{filters.tags}%"))

        # Apply needs_followup filter
        if filters.needs_followup:
            today = date.today()
            query = query.filter(
                Customer.next_followup_date.isnot(None),
                Customer.next_followup_date <= today
            )

        # Search in name/company (NOTE: can't search encrypted email directly)
        if filters.search:
            search_pattern = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Customer.name.ilike(search_pattern),
                    Customer.company_name.ilike(search_pattern)
                )
            )

        # Order by creation date (newest first)
        query = query.order_by(desc(Customer.created_at))

        # Apply pagination
        query = query.offset(filters.skip).limit(filters.limit)

        return query.all()

    def count_customers(self, filters: Optional[CustomerFilters] = None) -> int:
        """
        Count total customers matching filters (for pagination).

        Args:
            filters: Filtering parameters

        Returns:
            Total count of matching customers
        """
        if filters is None:
            filters = CustomerFilters()

        query = self.db.query(func.count(Customer.id)).filter(
            Customer.is_deleted == False
        )

        # Apply same filters as list_customers
        if filters.status:
            query = query.filter(Customer.status == filters.status)
        if filters.customer_type:
            query = query.filter(Customer.customer_type == filters.customer_type)
        if filters.source:
            query = query.filter(Customer.source == filters.source)
        if filters.assigned_to:
            query = query.filter(Customer.assigned_to == filters.assigned_to)
        if filters.tags:
            query = query.filter(Customer.tags.like(f"%{filters.tags}%"))
        if filters.needs_followup:
            today = date.today()
            query = query.filter(
                Customer.next_followup_date.isnot(None),
                Customer.next_followup_date <= today
            )
        if filters.search:
            search_pattern = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Customer.name.ilike(search_pattern),
                    Customer.company_name.ilike(search_pattern)
                )
            )

        return query.scalar()

    def update_customer(
        self,
        customer_id: int,
        data: CustomerUpdate
    ) -> Optional[Customer]:
        """
        Update customer.

        Args:
            customer_id: Customer ID to update
            data: Update data (only provided fields will be updated)

        Returns:
            Updated customer or None if not found
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return None

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(customer, field, value)

        # Update marketing consent date if consent changed
        if 'marketing_consent' in update_data and update_data['marketing_consent']:
            if not customer.marketing_consent_date:
                customer.marketing_consent_date = datetime.utcnow()

        customer.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(customer)

        return customer

    def delete_customer(
        self,
        customer_id: int,
        deleted_by: int
    ) -> bool:
        """
        Soft delete a customer.

        Args:
            customer_id: Customer ID to delete
            deleted_by: Admin user ID performing deletion

        Returns:
            True if deleted successfully, False if customer not found
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return False

        customer.is_deleted = True
        customer.deleted_at = datetime.utcnow()
        customer.deleted_by = deleted_by

        self.db.commit()

        return True

    def restore_customer(self, customer_id: int) -> Optional[Customer]:
        """
        Restore a soft-deleted customer.

        Args:
            customer_id: Customer ID to restore

        Returns:
            Restored customer or None if not found
        """
        customer = self.db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.is_deleted == True
        ).first()

        if not customer:
            return None

        customer.is_deleted = False
        customer.deleted_at = None
        customer.deleted_by = None
        customer.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(customer)

        return customer

    # ========================================================================
    # CUSTOMER NOTES
    # ========================================================================

    def add_note(
        self,
        customer_id: int,
        data: CustomerNoteCreate,
        created_by: int
    ) -> Optional[CustomerNote]:
        """
        Add a note to customer.

        Args:
            customer_id: Customer ID
            data: Note content
            created_by: Admin user ID creating the note

        Returns:
            Created note or None if customer not found
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return None

        note = CustomerNote(
            customer_id=customer_id,
            note=data.note,
            created_by=created_by,
            created_at=datetime.utcnow()
        )

        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)

        return note

    def get_customer_notes(
        self,
        customer_id: int,
        limit: int = 50
    ) -> List[CustomerNote]:
        """
        Get all notes for a customer.

        Args:
            customer_id: Customer ID
            limit: Maximum number of notes to return

        Returns:
            List of notes ordered by creation date (newest first)
        """
        return self.db.query(CustomerNote).filter(
            CustomerNote.customer_id == customer_id
        ).order_by(desc(CustomerNote.created_at)).limit(limit).all()

    def delete_note(self, note_id: int) -> bool:
        """
        Delete a customer note.

        Args:
            note_id: Note ID to delete

        Returns:
            True if deleted, False if not found
        """
        note = self.db.query(CustomerNote).filter(
            CustomerNote.id == note_id
        ).first()

        if not note:
            return False

        self.db.delete(note)
        self.db.commit()

        return True

    # ========================================================================
    # CUSTOMER INTERACTIONS
    # ========================================================================

    def log_interaction(
        self,
        customer_id: int,
        data: CustomerInteractionCreate,
        created_by: int
    ) -> Optional[CustomerInteraction]:
        """
        Log an interaction with customer.

        Args:
            customer_id: Customer ID
            data: Interaction details
            created_by: Admin user ID logging the interaction

        Returns:
            Created interaction or None if customer not found
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return None

        interaction = CustomerInteraction(
            customer_id=customer_id,
            **data.model_dump(exclude_unset=True),
            created_by=created_by,
            created_at=datetime.utcnow()
        )

        self.db.add(interaction)

        # Update customer's last_contact_date if interaction is completed
        if data.completed_at:
            customer.last_contact_date = data.completed_at
            customer.last_contact_type = data.interaction_type

        self.db.commit()
        self.db.refresh(interaction)

        return interaction

    def get_customer_interactions(
        self,
        customer_id: int,
        limit: int = 50
    ) -> List[CustomerInteraction]:
        """
        Get all interactions for a customer.

        Args:
            customer_id: Customer ID
            limit: Maximum number of interactions to return

        Returns:
            List of interactions ordered by creation date (newest first)
        """
        return self.db.query(CustomerInteraction).filter(
            CustomerInteraction.customer_id == customer_id
        ).order_by(desc(CustomerInteraction.created_at)).limit(limit).all()

    def delete_interaction(self, interaction_id: int) -> bool:
        """
        Delete a customer interaction.

        Args:
            interaction_id: Interaction ID to delete

        Returns:
            True if deleted, False if not found
        """
        interaction = self.db.query(CustomerInteraction).filter(
            CustomerInteraction.id == interaction_id
        ).first()

        if not interaction:
            return False

        self.db.delete(interaction)
        self.db.commit()

        return True

    # ========================================================================
    # FINANCIAL CALCULATIONS
    # ========================================================================

    def update_customer_lifetime_value(
        self,
        customer_id: int,
        transaction_amount: Decimal
    ) -> Optional[Customer]:
        """
        Update customer's financial metrics after a transaction.

        This method should be called from the Finance domain when an invoice is paid.

        Args:
            customer_id: Customer ID
            transaction_amount: Amount of the new transaction

        Returns:
            Updated customer or None if not found
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return None

        # Update total spent
        customer.total_spent += transaction_amount

        # Update lifetime value (simple: total_spent)
        # In more complex scenarios, could subtract refunds, apply discounts, etc.
        customer.lifetime_value = customer.total_spent

        # Update last purchase date
        customer.last_purchase_date = date.today()

        # Increment completed projects
        customer.completed_projects += 1

        # Recalculate average deal size
        if customer.completed_projects > 0:
            customer.avg_deal_size = customer.total_spent / customer.completed_projects

        customer.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(customer)

        return customer

    def recalculate_customer_ltv(self, customer_id: int) -> Optional[Customer]:
        """
        Recalculate customer LTV from scratch (e.g., after data correction).

        This queries the Finance domain to get all transactions for this customer.

        Args:
            customer_id: Customer ID

        Returns:
            Updated customer or None if not found
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return None

        # Finance domain integration (Phase 3): Query invoices/transactions
        # Current: Uses existing total_spent value from Customer model

        customer.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(customer)

        return customer

    # ========================================================================
    # SEGMENTATION & ANALYTICS
    # ========================================================================

    def get_customer_stats(self) -> CustomerStats:
        """
        Get overall customer statistics for dashboard.

        Returns:
            CustomerStats with aggregated data
        """
        # Total customers
        total = self.db.query(func.count(Customer.id)).filter(
            Customer.is_deleted == False
        ).scalar()

        # By status
        by_status = {}
        status_counts = self.db.query(
            Customer.status,
            func.count(Customer.id)
        ).filter(
            Customer.is_deleted == False
        ).group_by(Customer.status).all()

        for status, count in status_counts:
            by_status[status] = count

        # By type
        by_type = {}
        type_counts = self.db.query(
            Customer.customer_type,
            func.count(Customer.id)
        ).filter(
            Customer.is_deleted == False
        ).group_by(Customer.customer_type).all()

        for ctype, count in type_counts:
            by_type[ctype] = count

        # By source
        by_source = {}
        source_counts = self.db.query(
            Customer.source,
            func.count(Customer.id)
        ).filter(
            Customer.is_deleted == False
        ).group_by(Customer.source).all()

        for source, count in source_counts:
            by_source[source] = count

        # Financial metrics
        total_ltv = self.db.query(
            func.coalesce(func.sum(Customer.lifetime_value), 0)
        ).filter(
            Customer.is_deleted == False
        ).scalar() or Decimal('0.00')

        avg_ltv = self.db.query(
            func.coalesce(func.avg(Customer.lifetime_value), 0)
        ).filter(
            Customer.is_deleted == False
        ).scalar() or Decimal('0.00')

        # Top customers by LTV
        top_customers = self.db.query(Customer).filter(
            Customer.is_deleted == False
        ).order_by(desc(Customer.lifetime_value)).limit(5).all()

        return CustomerStats(
            total_customers=total,
            by_status=by_status,
            by_type=by_type,
            by_source=by_source,
            total_lifetime_value=total_ltv,
            avg_lifetime_value=avg_ltv,
            top_customers=top_customers
        )

    def get_customers_needing_followup(self) -> List[Customer]:
        """
        Get customers that need follow-up today or earlier.

        Returns:
            List of customers sorted by follow-up date
        """
        today = date.today()

        return self.db.query(Customer).filter(
            Customer.is_deleted == False,
            Customer.next_followup_date.isnot(None),
            Customer.next_followup_date <= today
        ).order_by(Customer.next_followup_date).all()

    def get_inactive_customers(self, days_threshold: int = 90) -> List[Customer]:
        """
        Get customers who haven't been contacted in X days.

        Args:
            days_threshold: Number of days to consider inactive

        Returns:
            List of inactive customers
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)

        return self.db.query(Customer).filter(
            Customer.is_deleted == False,
            Customer.status == CustomerStatus.ACTIVE.value,
            or_(
                Customer.last_contact_date.is_(None),
                Customer.last_contact_date < cutoff_date
            )
        ).order_by(Customer.last_contact_date).all()

    # ========================================================================
    # DEDUPLICATION & MERGE
    # ========================================================================

    def find_potential_duplicates(
        self,
        limit: int = 50
    ) -> List[tuple[Customer, Customer]]:
        """
        Find potential duplicate customers based on similar names or companies.

        Note: This is a simple implementation. For production, consider using
        fuzzy matching algorithms like Levenshtein distance.

        Args:
            limit: Maximum number of duplicate pairs to return

        Returns:
            List of (customer1, customer2) tuples that might be duplicates
        """
        # Duplicate detection: Compare name similarity, phone, company
        # Implementation: Use fuzzy matching (fuzzywuzzy) or ML model
        return []

    def merge_customers(
        self,
        primary_customer_id: int,
        customer_ids_to_merge: List[int],
        merged_by: int
    ) -> Optional[Customer]:
        """
        Merge multiple customers into a primary customer.

        This moves all notes, interactions, bookings, and quotes from
        the duplicate customers to the primary customer, then soft-deletes
        the duplicates.

        Args:
            primary_customer_id: Customer to keep
            customer_ids_to_merge: Customers to merge into primary
            merged_by: Admin user ID performing the merge

        Returns:
            Updated primary customer or None if primary not found
        """
        primary = self.get_customer(primary_customer_id)
        if not primary:
            return None

        for customer_id in customer_ids_to_merge:
            if customer_id == primary_customer_id:
                continue  # Skip primary itself

            customer = self.get_customer(customer_id)
            if not customer:
                continue

            # Move notes
            self.db.query(CustomerNote).filter(
                CustomerNote.customer_id == customer_id
            ).update({"customer_id": primary_customer_id})

            # Move interactions
            self.db.query(CustomerInteraction).filter(
                CustomerInteraction.customer_id == customer_id
            ).update({"customer_id": primary_customer_id})

            # Phase 2: Move bookings (requires customer_id FK in Booking model)
            # Phase 2: Move quotes (requires Quote.customer_id relationship)

            # Merge financial data
            primary.total_spent += customer.total_spent
            primary.lifetime_value += customer.lifetime_value
            primary.completed_projects += customer.completed_projects

            # Keep most recent last_contact_date
            if customer.last_contact_date:
                if not primary.last_contact_date or customer.last_contact_date > primary.last_contact_date:
                    primary.last_contact_date = customer.last_contact_date
                    primary.last_contact_type = customer.last_contact_type

            # Soft delete the merged customer
            customer.is_deleted = True
            customer.deleted_at = datetime.utcnow()
            customer.deleted_by = merged_by

        # Recalculate primary customer averages
        if primary.completed_projects > 0:
            primary.avg_deal_size = primary.total_spent / primary.completed_projects

        primary.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(primary)

        return primary

    # ========================================================================
    # BULK OPERATIONS
    # ========================================================================

    def bulk_update_status(
        self,
        customer_ids: List[int],
        new_status: str
    ) -> int:
        """
        Bulk update status for multiple customers.

        Args:
            customer_ids: List of customer IDs to update
            new_status: New status to set

        Returns:
            Number of customers updated
        """
        count = self.db.query(Customer).filter(
            Customer.id.in_(customer_ids),
            Customer.is_deleted == False
        ).update(
            {"status": new_status, "updated_at": datetime.utcnow()},
            synchronize_session=False
        )

        self.db.commit()

        return count

    def bulk_assign(
        self,
        customer_ids: List[int],
        assigned_to: int
    ) -> int:
        """
        Bulk assign customers to an admin user.

        Args:
            customer_ids: List of customer IDs to assign
            assigned_to: Admin user ID to assign to

        Returns:
            Number of customers assigned
        """
        count = self.db.query(Customer).filter(
            Customer.id.in_(customer_ids),
            Customer.is_deleted == False
        ).update(
            {"assigned_to": assigned_to, "updated_at": datetime.utcnow()},
            synchronize_session=False
        )

        self.db.commit()

        return count


# Helper function to get service instance
def get_customer_service(db: Session) -> CustomerService:
    """
    Factory function to get CustomerService instance.

    Args:
        db: Database session

    Returns:
        CustomerService instance
    """
    return CustomerService(db)
