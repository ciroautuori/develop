"""
Customers Domain API Routes - RESTful endpoints.

Espone tutti gli endpoint API per la gestione clienti (CRM).
"""


from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.domain.auth.admin_models import AdminUser
from app.infrastructure.database.session import get_db

from .models import Customer
from .schemas import (
    BulkCreateFromLeadsRequest,
    BulkCreateFromLeadsResponse,
    CustomerBulkUpdateStatus,
    CustomerCreate,
    CustomerFilters,
    CustomerInteractionCreate,
    CustomerInteractionResponse,
    CustomerListItem,
    CustomerMergeRequest,
    CustomerNoteCreate,
    CustomerNoteResponse,
    CustomerResponse,
    CustomerStats,
    CustomerUpdate,
)
from .services import CustomerService

router = APIRouter(
    prefix="/api/v1/admin/customers",
    tags=["customers"],
    dependencies=[Depends(get_current_admin_user)]  # All endpoints require admin auth
)


# ============================================================================
# CUSTOMER CRUD ENDPOINTS
# ============================================================================

@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new customer",
    description="Create a new customer in the CRM system. Email will be encrypted."
)
async def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Create a new customer.

    - **name**: Full name or company name (required)
    - **email**: Customer email - will be encrypted (required)
    - **phone**: Phone number - will be encrypted (optional)
    - All other fields as per schema

    Returns the created customer with ID.
    """
    service = CustomerService(db)

    try:
        customer = service.create_customer(
            data=data,
            created_by=current_user.id
        )
        return customer
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=list[CustomerListItem],
    summary="List customers",
    description="Get paginated list of customers with optional filters"
)
async def list_customers(
    status_filter: str = Query(None, alias="status", description="Filter by status"),
    customer_type: str = Query(None, description="Filter by customer type"),
    source: str = Query(None, description="Filter by acquisition source"),
    assigned_to: int = Query(None, description="Filter by assigned admin user ID"),
    search: str = Query(None, description="Search in name and company name"),
    tags: str = Query(None, description="Filter by tags (comma-separated)"),
    needs_followup: bool = Query(None, description="Only customers needing follow-up"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    List customers with filters and pagination.

    Supports filtering by:
    - Status (lead, prospect, active, inactive, churned)
    - Customer type (individual, business, agency, non_profit)
    - Source (website, referral, advertising, etc.)
    - Assigned admin user
    - Tags
    - Follow-up needed
    - Text search in name/company

    Returns lightweight customer list items (not full details).
    """
    service = CustomerService(db)

    filters = CustomerFilters(
        status=status_filter,
        customer_type=customer_type,
        source=source,
        assigned_to=assigned_to,
        search=search,
        tags=tags,
        needs_followup=needs_followup,
        skip=skip,
        limit=limit
    )

    customers = service.list_customers(filters=filters)

    return customers


@router.get(
    "/count",
    response_model=dict,
    summary="Count customers",
    description="Get total count of customers matching filters"
)
async def count_customers(
    status_filter: str = Query(None, alias="status"),
    customer_type: str = Query(None),
    source: str = Query(None),
    assigned_to: int = Query(None),
    search: str = Query(None),
    tags: str = Query(None),
    needs_followup: bool = Query(None),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Get count of customers matching filters (for pagination).
    """
    service = CustomerService(db)

    filters = CustomerFilters(
        status=status_filter,
        customer_type=customer_type,
        source=source,
        assigned_to=assigned_to,
        search=search,
        tags=tags,
        needs_followup=needs_followup
    )

    total = service.count_customers(filters=filters)

    return {"total": total}


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Get customer details",
    description="Get full customer details by ID"
)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Get customer by ID with full details.

    Returns complete customer information including:
    - Basic info (name, email decrypted), phone decrypted)
    - CRM data (status, type, source, etc.)
    - Financial metrics (LTV, total spent, etc.)
    - Engagement data (last contact, follow-up dates)
    """
    service = CustomerService(db)

    customer = service.get_customer(customer_id)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} not found"
        )

    return customer


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Update customer",
    description="Update customer details (partial update supported)"
)
async def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Update customer.

    Supports partial updates - only provide fields you want to change.
    """
    service = CustomerService(db)

    customer = service.update_customer(customer_id, data)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} not found"
        )

    return customer


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete customer",
    description="Soft delete a customer (GDPR compliant)"
)
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Soft delete a customer.

    The customer will be marked as deleted but data remains in database
    for audit purposes. Related notes and interactions are preserved.
    """
    service = CustomerService(db)

    success = service.delete_customer(customer_id, deleted_by=current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} not found"
        )



@router.post(
    "/{customer_id}/restore",
    response_model=CustomerResponse,
    summary="Restore deleted customer",
    description="Restore a soft-deleted customer"
)
async def restore_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Restore a soft-deleted customer.
    """
    service = CustomerService(db)

    customer = service.restore_customer(customer_id)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deleted customer {customer_id} not found"
        )

    return customer


# ============================================================================
# CUSTOMER NOTES ENDPOINTS
# ============================================================================

@router.post(
    "/{customer_id}/notes",
    response_model=CustomerNoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add note to customer",
    description="Add an internal note to a customer"
)
async def add_customer_note(
    customer_id: int,
    data: CustomerNoteCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Add a note to customer.

    Notes are internal annotations visible only to admin users.
    """
    service = CustomerService(db)

    note = service.add_note(
        customer_id=customer_id,
        data=data,
        created_by=current_user.id
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} not found"
        )

    return note


@router.get(
    "/{customer_id}/notes",
    response_model=list[CustomerNoteResponse],
    summary="Get customer notes",
    description="Get all notes for a customer"
)
async def get_customer_notes(
    customer_id: int,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Get all notes for a customer, ordered by creation date (newest first).
    """
    service = CustomerService(db)

    notes = service.get_customer_notes(customer_id, limit=limit)

    return notes


@router.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete customer note",
    description="Delete a customer note"
)
async def delete_customer_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Delete a customer note.
    """
    service = CustomerService(db)

    success = service.delete_note(note_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note {note_id} not found"
        )



# ============================================================================
# CUSTOMER INTERACTIONS ENDPOINTS
# ============================================================================

@router.post(
    "/{customer_id}/interactions",
    response_model=CustomerInteractionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log customer interaction",
    description="Log an interaction with a customer (call, email, meeting, etc.)"
)
async def log_customer_interaction(
    customer_id: int,
    data: CustomerInteractionCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Log an interaction with customer.

    Interaction types: email, call, meeting, demo, support, follow_up, etc.

    Updates customer's last_contact_date if interaction is completed.
    """
    service = CustomerService(db)

    interaction = service.log_interaction(
        customer_id=customer_id,
        data=data,
        created_by=current_user.id
    )

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} not found"
        )

    return interaction


@router.get(
    "/{customer_id}/interactions",
    response_model=list[CustomerInteractionResponse],
    summary="Get customer interactions",
    description="Get interaction history for a customer"
)
async def get_customer_interactions(
    customer_id: int,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Get all interactions for a customer, ordered by creation date (newest first).

    Provides a complete timeline of customer engagement.
    """
    service = CustomerService(db)

    interactions = service.get_customer_interactions(customer_id, limit=limit)

    return interactions


@router.delete(
    "/interactions/{interaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete customer interaction",
    description="Delete a customer interaction record"
)
async def delete_customer_interaction(
    interaction_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Delete a customer interaction.
    """
    service = CustomerService(db)

    success = service.delete_interaction(interaction_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interaction {interaction_id} not found"
        )



# ============================================================================
# ANALYTICS & STATS ENDPOINTS
# ============================================================================

@router.get(
    "/stats/overview",
    response_model=CustomerStats,
    summary="Get customer statistics",
    description="Get aggregated customer statistics for dashboard"
)
async def get_customer_stats(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Get customer statistics:
    - Total customers
    - Breakdown by status, type, source
    - Total and average LTV
    - Top 5 customers by LTV
    """
    service = CustomerService(db)

    stats = service.get_customer_stats()

    return stats


@router.get(
    "/followup/needed",
    response_model=list[CustomerListItem],
    summary="Get customers needing follow-up",
    description="Get customers with follow-up date today or earlier"
)
async def get_customers_needing_followup(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Get customers that need follow-up.

    Returns customers where next_followup_date <= today.
    """
    service = CustomerService(db)

    customers = service.get_customers_needing_followup()

    return customers


@router.get(
    "/inactive",
    response_model=list[CustomerListItem],
    summary="Get inactive customers",
    description="Get customers not contacted in X days"
)
async def get_inactive_customers(
    days: int = Query(90, ge=1, le=365, description="Days threshold for inactive"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Get customers who haven't been contacted in X days.

    Useful for re-engagement campaigns.
    """
    service = CustomerService(db)

    customers = service.get_inactive_customers(days_threshold=days)

    return customers


# ============================================================================
# BULK OPERATIONS ENDPOINTS
# ============================================================================

@router.post(
    "/bulk/update-status",
    response_model=dict,
    summary="Bulk update customer status",
    description="Update status for multiple customers at once"
)
async def bulk_update_status(
    data: CustomerBulkUpdateStatus,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Bulk update status for multiple customers.

    Example: Move multiple leads to prospect status.
    """
    service = CustomerService(db)

    count = service.bulk_update_status(
        customer_ids=data.customer_ids,
        new_status=data.new_status
    )

    return {"updated": count}


@router.post(
    "/bulk/assign",
    response_model=dict,
    summary="Bulk assign customers",
    description="Assign multiple customers to an admin user"
)
async def bulk_assign_customers(
    customer_ids: list[int],
    assigned_to: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Bulk assign customers to an admin user.
    """
    service = CustomerService(db)

    count = service.bulk_assign(
        customer_ids=customer_ids,
        assigned_to=assigned_to
    )

    return {"assigned": count}




# ============================================================================
# FASE 1: LEAD MANAGEMENT ENDPOINTS
# ============================================================================

@router.post(
    "/bulk-create-from-leads",
    response_model=BulkCreateFromLeadsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk create customers from lead finder",
    description="Convert selected leads from AI lead finder to customers with duplicate checking"
)
async def bulk_create_customers_from_leads(
    data: BulkCreateFromLeadsRequest,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Bulk create customers from lead finder results.

    FASE 1 Implementation:
    - Converts selected leads to customers
    - Status: LEAD
    - Source: ADVERTISING (from lead finder campaign)
    - Checks for duplicates by email
    - Skips duplicates and reports them
    - Creates CustomerInteraction for each lead (initial contact)

    Returns counts of created vs skipped.
    """
    from app.core.security import encrypt_pii

    service = CustomerService(db)
    created_ids = []
    skipped_emails = []

    for lead in data.leads:
        try:
            # Check if customer already exists (by email)
            encrypted_email = encrypt_pii(lead.email)
            existing = db.query(Customer).filter(
                Customer._email == encrypted_email
            ).first()

            if existing:
                skipped_emails.append(lead.email)
                continue

            # Create CustomerCreate schema from LeadItem
            customer_data = CustomerCreate(
                name=lead.company,
                email=lead.email,
                phone=lead.phone if lead.phone else None,
                company_name=lead.company,
                company_website=lead.website if lead.website else None,
                address_line1=lead.address,
                city=lead.location,
                country="IT",
                status="lead",
                customer_type="business",
                source="advertising",
                tags=f"{lead.industry},{lead.need}",
                notes=f"Lead from AI finder - Score: {lead.score}% - Need: {lead.need_reason}",
                marketing_consent=False
            )

            # Create customer
            customer = service.create_customer(
                data=customer_data,
                created_by=current_user.id
            )
            created_ids.append(customer.id)

            # Log initial interaction
            interaction_data = CustomerInteractionCreate(
                interaction_type="lead_found",
                subject=f"Lead trovato - {lead.industry}",
                description=f"Lead score: {lead.score}%\nNeed: {lead.need}\nReason: {lead.need_reason}\nLocation: {lead.location}",
                outcome="positive",
                next_action=f"Contattare per {lead.need}"
            )

            service.log_interaction(
                customer_id=customer.id,
                data=interaction_data,
                created_by=current_user.id
            )

        except ValueError:
            skipped_emails.append(lead.email)
            continue

    message = f"Created {len(created_ids)} customers"
    if len(skipped_emails) > 0:
        message += f", skipped {len(skipped_emails)} duplicates"

    return BulkCreateFromLeadsResponse(
        created_count=len(created_ids),
        skipped_count=len(skipped_emails),
        created_ids=created_ids,
        skipped_emails=skipped_emails,
        message=message
    )


# ============================================================================
# DEDUPLICATION & MERGE ENDPOINTS
# ============================================================================

@router.get(
    "/duplicates/find",
    response_model=list[dict],
    summary="Find potential duplicate customers",
    description="Find customers that might be duplicates"
)
async def find_potential_duplicates(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Find potential duplicate customers based on similar names/emails.

    Returns pairs of customers that might be the same entity.
    """
    service = CustomerService(db)

    duplicates = service.find_potential_duplicates(limit=limit)

    # Format response
    result = []
    for customer1, customer2 in duplicates:
        result.append({
            "customer1_id": customer1.id,
            "customer1_name": customer1.name,
            "customer2_id": customer2.id,
            "customer2_name": customer2.name
        })

    return result


@router.post(
    "/merge",
    response_model=CustomerResponse,
    summary="Merge customers",
    description="Merge duplicate customers into one primary customer"
)
async def merge_customers(
    data: CustomerMergeRequest,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Merge multiple duplicate customers into a primary customer.

    This will:
    - Move all notes, interactions, bookings, quotes to primary customer
    - Aggregate financial metrics
    - Soft delete the merged customers

    **Warning**: This operation cannot be easily reversed.
    """
    service = CustomerService(db)

    customer = service.merge_customers(
        primary_customer_id=data.primary_customer_id,
        customer_ids_to_merge=data.customer_ids_to_merge,
        merged_by=current_user.id
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Primary customer {data.primary_customer_id} not found"
        )

    return customer
