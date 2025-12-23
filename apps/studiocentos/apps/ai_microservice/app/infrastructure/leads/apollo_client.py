"""
Apollo.io API Client.

Production-ready client for Apollo.io with:
- People search and enrichment
- Company search and enrichment
- Lead lists management
- Email finding

API Reference: https://apolloio.github.io/apollo-api-docs/
"""

import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class ApolloError(Exception):
    """Apollo.io API error."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class ApolloClient:
    """
    Apollo.io API Client.

    Provides:
    - People search by criteria
    - Company search and enrichment
    - Contact enrichment
    - Email finding
    - Lead list management

    Example:
        >>> client = ApolloClient(api_key=os.getenv("APOLLO_API_KEY"))
        >>> leads = await client.search_people(
        ...     titles=["CEO", "Founder"],
        ...     industries=["technology"],
        ...     location="Italy",
        ...     per_page=25,
        ... )
    """

    API_BASE = "https://api.apollo.io/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
    ):
        """
        Initialize Apollo client.

        Args:
            api_key: Apollo.io API key
        """
        self.api_key = api_key or os.getenv("APOLLO_API_KEY", "")

        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get HTTP client."""
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "Content-Type": "application/json",
                    "Cache-Control": "no-cache",
                },
            )
        return self._client

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make API request with API key injection."""
        url = f"{self.API_BASE}{endpoint}"

        # Inject API key into request body for POST
        if method.upper() == "POST":
            json_data = kwargs.get("json", {})
            json_data["api_key"] = self.api_key
            kwargs["json"] = json_data
        else:
            # For GET requests, add to params
            params = kwargs.get("params", {})
            params["api_key"] = self.api_key
            kwargs["params"] = params

        response = await self.client.request(method, url, **kwargs)

        if response.status_code >= 400:
            raise ApolloError(
                f"Apollo API error: {response.text}",
                status_code=response.status_code,
            )

        return response.json() if response.content else {}

    # =========================================================================
    # PEOPLE SEARCH
    # =========================================================================

    async def search_people(
        self,
        titles: Optional[List[str]] = None,
        industries: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None,
        company_size: Optional[List[str]] = None,
        revenue_range: Optional[Dict[str, int]] = None,
        per_page: int = 25,
        page: int = 1,
        include_emails: bool = True,
    ) -> Dict[str, Any]:
        """
        Search for people/contacts.

        Args:
            titles: Job titles to search for (e.g., ["CEO", "CTO", "Founder"])
            industries: Industry categories
            keywords: Keywords in bio/company
            location: Location string (e.g., "Italy", "Milan, Italy")
            company_size: Company size ranges (e.g., ["1,10", "11,50"])
            revenue_range: Revenue range {"min": 1000000, "max": 10000000}
            per_page: Results per page (max 100)
            page: Page number
            include_emails: Whether to include email data

        Returns:
            People results with contact info
        """
        payload: Dict[str, Any] = {
            "page": page,
            "per_page": min(per_page, 100),
        }

        if titles:
            payload["person_titles"] = titles

        if industries:
            payload["organization_industry_tag_ids"] = industries

        if keywords:
            payload["q_keywords"] = " ".join(keywords)

        if location:
            payload["person_locations"] = [location]

        if company_size:
            payload["organization_num_employees_ranges"] = company_size

        if revenue_range:
            if "min" in revenue_range:
                payload["organization_estimated_annual_revenue_min"] = revenue_range["min"]
            if "max" in revenue_range:
                payload["organization_estimated_annual_revenue_max"] = revenue_range["max"]

        result = await self._request("POST", "/mixed_people/search", json=payload)

        people = result.get("people", [])
        pagination = result.get("pagination", {})

        logger.info(f"✅ Found {len(people)} people (page {page})")

        # Clean and structure results
        leads = []
        for person in people:
            lead = {
                "id": person.get("id"),
                "first_name": person.get("first_name"),
                "last_name": person.get("last_name"),
                "name": person.get("name"),
                "title": person.get("title"),
                "headline": person.get("headline"),
                "email": person.get("email"),
                "email_status": person.get("email_status"),
                "phone": person.get("sanitized_phone"),
                "linkedin_url": person.get("linkedin_url"),
                "twitter_url": person.get("twitter_url"),
                "city": person.get("city"),
                "state": person.get("state"),
                "country": person.get("country"),
                "organization": {
                    "id": person.get("organization_id"),
                    "name": person.get("organization", {}).get("name"),
                    "website": person.get("organization", {}).get("website_url"),
                    "industry": person.get("organization", {}).get("industry"),
                    "employees": person.get("organization", {}).get("estimated_num_employees"),
                    "revenue": person.get("organization", {}).get("estimated_annual_revenue"),
                },
            }
            leads.append(lead)

        return {
            "leads": leads,
            "total": pagination.get("total_entries", 0),
            "page": pagination.get("page", page),
            "per_page": pagination.get("per_page", per_page),
            "total_pages": pagination.get("total_pages", 1),
        }

    async def enrich_person(
        self,
        email: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Enrich a person with additional data.

        Provide at least one of: email, linkedin_url, or name+domain.

        Args:
            email: Person's email
            linkedin_url: LinkedIn profile URL
            first_name: First name
            last_name: Last name
            domain: Company domain

        Returns:
            Enriched person data or None
        """
        payload: Dict[str, Any] = {}

        if email:
            payload["email"] = email
        if linkedin_url:
            payload["linkedin_url"] = linkedin_url
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name
        if domain:
            payload["domain"] = domain

        if not payload:
            raise ApolloError("At least one identifier required")

        result = await self._request("POST", "/people/match", json=payload)

        person = result.get("person")

        if person:
            logger.info(f"✅ Enriched person: {person.get('name')}")
            return {
                "id": person.get("id"),
                "first_name": person.get("first_name"),
                "last_name": person.get("last_name"),
                "name": person.get("name"),
                "title": person.get("title"),
                "headline": person.get("headline"),
                "email": person.get("email"),
                "email_status": person.get("email_status"),
                "phone": person.get("sanitized_phone"),
                "linkedin_url": person.get("linkedin_url"),
                "twitter_url": person.get("twitter_url"),
                "city": person.get("city"),
                "state": person.get("state"),
                "country": person.get("country"),
                "seniority": person.get("seniority"),
                "departments": person.get("departments"),
                "employment_history": person.get("employment_history", []),
                "organization": {
                    "name": person.get("organization", {}).get("name"),
                    "website": person.get("organization", {}).get("website_url"),
                    "industry": person.get("organization", {}).get("industry"),
                    "linkedin": person.get("organization", {}).get("linkedin_url"),
                    "employees": person.get("organization", {}).get("estimated_num_employees"),
                },
            }

        return None

    # =========================================================================
    # COMPANY SEARCH
    # =========================================================================

    async def search_organizations(
        self,
        industries: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None,
        company_size: Optional[List[str]] = None,
        revenue_range: Optional[Dict[str, int]] = None,
        per_page: int = 25,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        Search for organizations/companies.

        Args:
            industries: Industry categories
            keywords: Keywords in company info
            location: Location string
            company_size: Size ranges (e.g., ["1,10", "51,200"])
            revenue_range: Revenue range {"min": X, "max": Y}
            per_page: Results per page
            page: Page number

        Returns:
            Organization results
        """
        payload: Dict[str, Any] = {
            "page": page,
            "per_page": min(per_page, 100),
        }

        if industries:
            payload["organization_industry_tag_ids"] = industries

        if keywords:
            payload["q_organization_keyword_tags"] = keywords

        if location:
            payload["organization_locations"] = [location]

        if company_size:
            payload["organization_num_employees_ranges"] = company_size

        if revenue_range:
            if "min" in revenue_range:
                payload["organization_estimated_annual_revenue_min"] = revenue_range["min"]
            if "max" in revenue_range:
                payload["organization_estimated_annual_revenue_max"] = revenue_range["max"]

        result = await self._request("POST", "/mixed_companies/search", json=payload)

        organizations = result.get("organizations", [])
        pagination = result.get("pagination", {})

        logger.info(f"✅ Found {len(organizations)} organizations (page {page})")

        companies = []
        for org in organizations:
            companies.append({
                "id": org.get("id"),
                "name": org.get("name"),
                "website": org.get("website_url"),
                "blog_url": org.get("blog_url"),
                "linkedin_url": org.get("linkedin_url"),
                "twitter_url": org.get("twitter_url"),
                "facebook_url": org.get("facebook_url"),
                "phone": org.get("primary_phone", {}).get("number"),
                "industry": org.get("industry"),
                "keywords": org.get("keywords", []),
                "estimated_employees": org.get("estimated_num_employees"),
                "estimated_revenue": org.get("estimated_annual_revenue"),
                "city": org.get("city"),
                "state": org.get("state"),
                "country": org.get("country"),
                "founded_year": org.get("founded_year"),
                "technologies": org.get("technologies", []),
            })

        return {
            "companies": companies,
            "total": pagination.get("total_entries", 0),
            "page": pagination.get("page", page),
            "per_page": pagination.get("per_page", per_page),
            "total_pages": pagination.get("total_pages", 1),
        }

    async def enrich_organization(
        self,
        domain: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Enrich an organization with additional data.

        Args:
            domain: Company domain (preferred)
            name: Company name

        Returns:
            Enriched organization data or None
        """
        payload: Dict[str, Any] = {}

        if domain:
            payload["domain"] = domain
        if name:
            payload["name"] = name

        if not payload:
            raise ApolloError("Domain or name required")

        result = await self._request("POST", "/organizations/enrich", json=payload)

        org = result.get("organization")

        if org:
            logger.info(f"✅ Enriched organization: {org.get('name')}")
            return {
                "id": org.get("id"),
                "name": org.get("name"),
                "website": org.get("website_url"),
                "blog_url": org.get("blog_url"),
                "linkedin_url": org.get("linkedin_url"),
                "twitter_url": org.get("twitter_url"),
                "facebook_url": org.get("facebook_url"),
                "phone": org.get("phone"),
                "industry": org.get("industry"),
                "sub_industry": org.get("subindustry"),
                "keywords": org.get("keywords", []),
                "estimated_employees": org.get("estimated_num_employees"),
                "estimated_revenue": org.get("estimated_annual_revenue"),
                "headquarters": {
                    "city": org.get("city"),
                    "state": org.get("state"),
                    "country": org.get("country"),
                    "street": org.get("street_address"),
                    "postal_code": org.get("postal_code"),
                },
                "founded_year": org.get("founded_year"),
                "technologies": org.get("technologies", []),
                "short_description": org.get("short_description"),
                "annual_revenue_printed": org.get("annual_revenue_printed"),
                "total_funding_printed": org.get("total_funding_printed"),
            }

        return None

    # =========================================================================
    # EMAIL FINDING
    # =========================================================================

    async def find_email(
        self,
        first_name: str,
        last_name: str,
        domain: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Find a person's email by name and company domain.

        Args:
            first_name: First name
            last_name: Last name
            domain: Company domain

        Returns:
            Email data or None
        """
        result = await self._request(
            "POST",
            "/people/match",
            json={
                "first_name": first_name,
                "last_name": last_name,
                "domain": domain,
                "reveal_personal_emails": False,
            },
        )

        person = result.get("person")

        if person and person.get("email"):
            logger.info(f"✅ Found email for {first_name} {last_name}")
            return {
                "email": person.get("email"),
                "email_status": person.get("email_status"),
                "confidence": "high" if person.get("email_status") == "verified" else "medium",
                "person_id": person.get("id"),
            }

        return None

    async def bulk_find_emails(
        self,
        contacts: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """
        Bulk find emails for multiple contacts.

        Args:
            contacts: List of dicts with first_name, last_name, domain

        Returns:
            List of results with emails
        """
        results = []

        for contact in contacts:
            try:
                email_data = await self.find_email(
                    first_name=contact.get("first_name", ""),
                    last_name=contact.get("last_name", ""),
                    domain=contact.get("domain", ""),
                )

                results.append({
                    "input": contact,
                    "found": bool(email_data),
                    "email": email_data.get("email") if email_data else None,
                    "status": email_data.get("email_status") if email_data else None,
                })

            except ApolloError as e:
                results.append({
                    "input": contact,
                    "found": False,
                    "error": str(e),
                })

        logger.info(f"✅ Bulk email find: {sum(1 for r in results if r['found'])}/{len(contacts)} found")

        return results

    # =========================================================================
    # LISTS MANAGEMENT
    # =========================================================================

    async def get_saved_lists(self) -> List[Dict[str, Any]]:
        """Get all saved lists."""
        result = await self._request("GET", "/labels")

        lists = result.get("labels", [])

        return [
            {
                "id": lst.get("id"),
                "name": lst.get("name"),
                "cached_count": lst.get("cached_count", 0),
                "created_at": lst.get("created_at"),
            }
            for lst in lists
        ]

    async def create_list(
        self,
        name: str,
    ) -> Dict[str, Any]:
        """Create a new saved list."""
        result = await self._request(
            "POST",
            "/labels",
            json={"name": name},
        )

        label = result.get("label", {})

        logger.info(f"✅ List created: {name}")

        return {
            "id": label.get("id"),
            "name": label.get("name"),
        }

    async def add_to_list(
        self,
        list_id: str,
        contact_ids: List[str],
    ) -> Dict[str, Any]:
        """Add contacts to a saved list."""
        result = await self._request(
            "POST",
            "/labels/add_contact_ids",
            json={
                "label_id": list_id,
                "contact_ids": contact_ids,
            },
        )

        logger.info(f"✅ Added {len(contact_ids)} contacts to list")

        return {"success": True, "added": len(contact_ids)}

    # =========================================================================
    # ACCOUNT INFO
    # =========================================================================

    async def get_account_info(self) -> Dict[str, Any]:
        """Get current account information and credits."""
        result = await self._request("GET", "/auth/health")

        return {
            "is_logged_in": result.get("is_logged_in"),
            "email_credits_used": result.get("num_email_credits_used"),
            "email_credits_total": result.get("num_email_credits_total"),
            "export_credits_used": result.get("num_export_credits_used"),
            "export_credits_total": result.get("num_export_credits_total"),
        }
