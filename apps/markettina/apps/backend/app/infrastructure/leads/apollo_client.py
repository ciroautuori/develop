"""
Apollo.io API Client - Production-ready B2B lead intelligence integration.

Features:
- People search and enrichment
- Company search and intelligence
- Email verification
- Contact data enrichment
- Saved searches and lists
- Credits management

API Reference: https://apolloio.github.io/apollo-api-docs/
"""

import logging
from datetime import datetime
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class ApolloClient:
    """
    Apollo.io API client for B2B lead intelligence.

    Features:
    - People search with filters
    - Company enrichment
    - Email finding and verification
    - Contact data enrichment

    Rate Limits:
    - Varies by plan
    - Standard: 300 requests per minute

    Usage:
        client = ApolloClient()
        leads = await client.search_people(
            titles=["CEO", "CTO"],
            industries=["Software"],
        )
    """

    BASE_URL = "https://api.apollo.io/v1"

    def __init__(
        self,
        api_key: str | None = None,
    ):
        self._api_key = api_key or getattr(settings, "APOLLO_API_KEY", "")
        self._client: httpx.AsyncClient | None = None

    def is_configured(self) -> bool:
        """Check if client is properly configured."""
        return bool(self._api_key)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=30.0,
                headers={
                    "Content-Type": "application/json",
                    "Cache-Control": "no-cache",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        json: dict | None = None,
        params: dict | None = None,
    ) -> dict[str, Any]:
        """Make authenticated API request."""
        if not self._api_key:
            raise ValueError("Apollo API key not configured")

        client = await self._get_client()

        # Add API key to request body
        if json is None:
            json = {}
        json["api_key"] = self._api_key

        response = await client.request(
            method,
            endpoint,
            json=json,
            params=params,
        )

        if response.status_code >= 400:
            logger.error(f"Apollo API error: {response.status_code} - {response.text}")
            raise ValueError(f"Apollo error: {response.status_code}")

        return response.json() if response.content else {}

    # =========================================================================
    # PEOPLE SEARCH
    # =========================================================================

    async def search_people(
        self,
        titles: list[str] | None = None,
        seniorities: list[str] | None = None,
        industries: list[str] | None = None,
        company_sizes: list[str] | None = None,
        locations: list[str] | None = None,
        keywords: list[str] | None = None,
        company_domains: list[str] | None = None,
        page: int = 1,
        per_page: int = 25,
    ) -> dict[str, Any]:
        """
        Search for people/contacts.

        Args:
            titles: Job titles to filter (e.g., ["CEO", "CTO", "VP Marketing"])
            seniorities: Seniority levels (e.g., ["c_suite", "vp", "director"])
            industries: Industry filters
            company_sizes: Company size ranges (e.g., ["1-10", "11-50", "51-200"])
            locations: Location filters
            keywords: Keyword search
            company_domains: Specific company domains
            page: Page number
            per_page: Results per page (max 100)

        Returns:
            Search results with people data
        """
        payload: dict[str, Any] = {
            "page": page,
            "per_page": min(per_page, 100),
        }

        if titles:
            payload["person_titles"] = titles

        if seniorities:
            payload["person_seniorities"] = seniorities

        if industries:
            payload["organization_industry_tag_ids"] = industries

        if company_sizes:
            payload["organization_num_employees_ranges"] = company_sizes

        if locations:
            payload["person_locations"] = locations

        if keywords:
            payload["q_keywords"] = " ".join(keywords)

        if company_domains:
            payload["organization_domains"] = company_domains

        response = await self._request("POST", "/mixed_people/search", json=payload)

        people = response.get("people", [])
        pagination = response.get("pagination", {})

        return {
            "people": [self._format_person(p) for p in people],
            "total": pagination.get("total_entries", 0),
            "page": pagination.get("page", page),
            "per_page": pagination.get("per_page", per_page),
            "total_pages": pagination.get("total_pages", 1),
        }

    def _format_person(self, person: dict[str, Any]) -> dict[str, Any]:
        """Format person data to standard structure."""
        org = person.get("organization", {}) or {}

        return {
            "id": person.get("id", ""),
            "first_name": person.get("first_name", ""),
            "last_name": person.get("last_name", ""),
            "name": person.get("name", ""),
            "title": person.get("title", ""),
            "seniority": person.get("seniority", ""),
            "email": person.get("email"),
            "email_status": person.get("email_status", ""),
            "linkedin_url": person.get("linkedin_url", ""),
            "phone": person.get("phone_numbers", [{}])[0].get("sanitized_number") if person.get("phone_numbers") else None,
            "city": person.get("city", ""),
            "state": person.get("state", ""),
            "country": person.get("country", ""),
            "company": {
                "id": org.get("id", ""),
                "name": org.get("name", ""),
                "domain": org.get("primary_domain", ""),
                "industry": org.get("industry", ""),
                "employees": org.get("estimated_num_employees"),
                "linkedin_url": org.get("linkedin_url", ""),
                "website": org.get("website_url", ""),
            },
        }

    async def get_person(self, person_id: str) -> dict[str, Any]:
        """
        Get person by ID.

        Args:
            person_id: Apollo person ID

        Returns:
            Person details
        """
        response = await self._request("GET", f"/people/{person_id}", json={})
        person = response.get("person", {})
        return self._format_person(person)

    async def enrich_person(
        self,
        email: str | None = None,
        linkedin_url: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        domain: str | None = None,
    ) -> dict[str, Any]:
        """
        Enrich person data.

        Args:
            email: Person's email
            linkedin_url: LinkedIn profile URL
            first_name: First name
            last_name: Last name
            domain: Company domain

        Returns:
            Enriched person data
        """
        payload: dict[str, Any] = {}

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

        response = await self._request("POST", "/people/match", json=payload)
        person = response.get("person", {})

        if person:
            return self._format_person(person)

        return {}

    # =========================================================================
    # COMPANY SEARCH
    # =========================================================================

    async def search_companies(
        self,
        keywords: list[str] | None = None,
        industries: list[str] | None = None,
        company_sizes: list[str] | None = None,
        locations: list[str] | None = None,
        domains: list[str] | None = None,
        page: int = 1,
        per_page: int = 25,
    ) -> dict[str, Any]:
        """
        Search for companies.

        Args:
            keywords: Keyword search
            industries: Industry filters
            company_sizes: Company size ranges
            locations: Location filters
            domains: Specific domains
            page: Page number
            per_page: Results per page

        Returns:
            Search results with company data
        """
        payload: dict[str, Any] = {
            "page": page,
            "per_page": min(per_page, 100),
        }

        if keywords:
            payload["q_organization_keyword_tags"] = keywords

        if industries:
            payload["organization_industry_tag_ids"] = industries

        if company_sizes:
            payload["organization_num_employees_ranges"] = company_sizes

        if locations:
            payload["organization_locations"] = locations

        if domains:
            payload["organization_domains"] = domains

        response = await self._request("POST", "/mixed_companies/search", json=payload)

        organizations = response.get("organizations", [])
        pagination = response.get("pagination", {})

        return {
            "companies": [self._format_company(c) for c in organizations],
            "total": pagination.get("total_entries", 0),
            "page": pagination.get("page", page),
            "per_page": pagination.get("per_page", per_page),
        }

    def _format_company(self, company: dict[str, Any]) -> dict[str, Any]:
        """Format company data to standard structure."""
        return {
            "id": company.get("id", ""),
            "name": company.get("name", ""),
            "domain": company.get("primary_domain", ""),
            "website": company.get("website_url", ""),
            "industry": company.get("industry", ""),
            "sub_industry": company.get("subindustry", ""),
            "employees": company.get("estimated_num_employees"),
            "revenue": company.get("annual_revenue"),
            "founded_year": company.get("founded_year"),
            "linkedin_url": company.get("linkedin_url", ""),
            "twitter_url": company.get("twitter_url", ""),
            "facebook_url": company.get("facebook_url", ""),
            "phone": company.get("phone", ""),
            "address": {
                "street": company.get("street_address", ""),
                "city": company.get("city", ""),
                "state": company.get("state", ""),
                "country": company.get("country", ""),
                "postal_code": company.get("postal_code", ""),
            },
            "technologies": company.get("technologies", []),
            "keywords": company.get("keywords", []),
            "description": company.get("short_description", ""),
        }

    async def enrich_company(
        self,
        domain: str,
    ) -> dict[str, Any]:
        """
        Enrich company data by domain.

        Args:
            domain: Company domain

        Returns:
            Enriched company data
        """
        response = await self._request(
            "POST",
            "/organizations/enrich",
            json={"domain": domain},
        )

        organization = response.get("organization", {})

        if organization:
            return self._format_company(organization)

        return {}

    # =========================================================================
    # EMAIL OPERATIONS
    # =========================================================================

    async def find_email(
        self,
        first_name: str,
        last_name: str,
        domain: str,
    ) -> dict[str, Any]:
        """
        Find person's email by name and company domain.

        Args:
            first_name: First name
            last_name: Last name
            domain: Company domain

        Returns:
            Email data with confidence
        """
        response = await self._request(
            "POST",
            "/people/match",
            json={
                "first_name": first_name,
                "last_name": last_name,
                "domain": domain,
                "reveal_personal_emails": False,
            },
        )

        person = response.get("person", {})

        return {
            "email": person.get("email"),
            "email_status": person.get("email_status", ""),
            "confidence": "high" if person.get("email_status") == "verified" else "medium",
            "person_id": person.get("id"),
        }

    async def verify_email(self, email: str) -> dict[str, Any]:
        """
        Verify an email address.

        Args:
            email: Email to verify

        Returns:
            Verification result
        """
        # Apollo doesn't have a direct verify endpoint
        # Use person match to check email status
        response = await self._request(
            "POST",
            "/people/match",
            json={"email": email},
        )

        person = response.get("person", {})
        email_status = person.get("email_status", "unknown")

        return {
            "email": email,
            "status": email_status,
            "is_valid": email_status in ["verified", "likely valid"],
            "is_catch_all": email_status == "catch-all",
            "is_invalid": email_status == "invalid",
        }

    # =========================================================================
    # LISTS AND SEQUENCES
    # =========================================================================

    async def get_lists(self) -> list[dict[str, Any]]:
        """
        Get saved contact lists.

        Returns:
            List of contact lists
        """
        response = await self._request("GET", "/labels", json={})

        labels = response.get("labels", [])

        return [
            {
                "id": label.get("id", ""),
                "name": label.get("name", ""),
                "cached_count": label.get("cached_count", 0),
                "created_at": label.get("created_at"),
            }
            for label in labels
        ]

    async def add_to_list(
        self,
        list_id: str,
        contact_ids: list[str],
    ) -> dict[str, Any]:
        """
        Add contacts to a list.

        Args:
            list_id: List ID
            contact_ids: Contact IDs to add

        Returns:
            Operation result
        """
        response = await self._request(
            "POST",
            f"/labels/{list_id}/add_contact_ids",
            json={"contact_ids": contact_ids},
        )

        return {"success": True, "added": len(contact_ids)}

    # =========================================================================
    # ACCOUNT INFO
    # =========================================================================

    async def get_credits_info(self) -> dict[str, Any]:
        """
        Get account credits information.

        Returns:
            Credits balance and usage
        """
        response = await self._request("GET", "/auth/health", json={})

        return {
            "credits_remaining": response.get("credits", {}).get("remaining", 0),
            "credits_used": response.get("credits", {}).get("used", 0),
            "credits_limit": response.get("credits", {}).get("limit", 0),
            "plan": response.get("plan_name", ""),
        }

    async def health_check(self) -> dict[str, Any]:
        """
        Check API health and authentication.

        Returns:
            Health status
        """
        try:
            response = await self._request("GET", "/auth/health", json={})
            return {
                "status": "healthy",
                "is_authenticated": response.get("is_logged_in", False),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
