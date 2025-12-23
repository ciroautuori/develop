"""
Customer dependencies for FastAPI dependency injection.
"""

from typing import Optional
from fastapi import Query
from app.domain.customers.schemas import CustomerFilters


def get_customer_filters(
    status: Optional[str] = Query(None, description="Filter by status"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    location: Optional[str] = Query(None, description="Filter by location"),
    company_size: Optional[str] = Query(None, description="Filter by company size"),
    search: Optional[str] = Query(None, description="Search in name, email, company"),
) -> CustomerFilters:
    """
    Extract customer filters from query parameters.

    Args:
        status: Customer status filter
        industry: Industry filter
        location: Location filter
        company_size: Company size filter
        search: Free text search

    Returns:
        CustomerFilters object with applied filters
    """
    return CustomerFilters(
        status=status,
        industry=industry,
        location=location,
        company_size=company_size,
        search=search,
    )
