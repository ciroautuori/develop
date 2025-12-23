"""
Customer dependencies for FastAPI dependency injection.
"""


from fastapi import Query

from app.domain.customers.schemas import CustomerFilters


def get_customer_filters(
    status: str | None = Query(None, description="Filter by status"),
    industry: str | None = Query(None, description="Filter by industry"),
    location: str | None = Query(None, description="Filter by location"),
    company_size: str | None = Query(None, description="Filter by company size"),
    search: str | None = Query(None, description="Search in name, email, company"),
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
