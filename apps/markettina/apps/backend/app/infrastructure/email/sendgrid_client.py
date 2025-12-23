"""
SendGrid Email API Client - Production-ready email marketing integration.

Features:
- Transactional email sending
- Template-based emails
- Contact and list management
- Marketing campaigns (Single Sends)
- Email statistics and analytics
- Bounce and spam management
- Sender verification

API Reference: https://docs.sendgrid.com/api-reference
API Version: v3
"""

import logging
from datetime import datetime
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class SendGridClient:
    """
    SendGrid API v3 client.

    Features:
    - Mail Send API
    - Contacts API
    - Marketing Campaigns
    - Stats API

    Rate Limits:
    - Sending: Based on plan (100 emails/day free tier)
    - API: 600 requests per minute

    Usage:
        client = SendGridClient()
        await client.send_email(
            to_email="user@example.com",
            subject="Hello",
            content="World",
        )
    """

    BASE_URL = "https://api.sendgrid.com/v3"

    def __init__(
        self,
        api_key: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
    ):
        self._api_key = api_key or getattr(settings, "SENDGRID_API_KEY", "")
        self._from_email = from_email or getattr(settings, "SENDGRID_FROM_EMAIL", settings.EMAILS_FROM_EMAIL)
        self._from_name = from_name or getattr(settings, "SENDGRID_FROM_NAME", settings.EMAILS_FROM_NAME)
        self._client: httpx.AsyncClient | None = None

    def is_configured(self) -> bool:
        """Check if client is properly configured."""
        return bool(self._api_key and self._from_email)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=30.0,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
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
    ) -> dict[str, Any] | list[Any]:
        """Make API request."""
        if not self._api_key:
            raise ValueError("SendGrid API key not configured")

        client = await self._get_client()

        response = await client.request(
            method,
            endpoint,
            json=json,
            params=params,
        )

        if response.status_code >= 400:
            logger.error(f"SendGrid API error: {response.status_code} - {response.text}")
            raise ValueError(f"SendGrid error: {response.status_code}")

        if response.content:
            return response.json()
        return {}

    # =========================================================================
    # MAIL SEND
    # =========================================================================

    async def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
        reply_to: str | None = None,
        attachments: list[dict[str, Any]] | None = None,
        categories: list[str] | None = None,
        custom_args: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Send a single email.

        Args:
            to_email: Recipient email
            subject: Email subject
            content: Plain text content
            html_content: HTML content (optional)
            from_email: Sender email (default from config)
            from_name: Sender name
            reply_to: Reply-to address
            attachments: File attachments
            categories: Email categories for tracking
            custom_args: Custom tracking arguments

        Returns:
            Send result
        """
        message: dict[str, Any] = {
            "personalizations": [
                {"to": [{"email": to_email}]}
            ],
            "from": {
                "email": from_email or self._from_email,
                "name": from_name or self._from_name,
            },
            "subject": subject,
            "content": [
                {"type": "text/plain", "value": content}
            ],
        }

        if html_content:
            message["content"].append({"type": "text/html", "value": html_content})

        if reply_to:
            message["reply_to"] = {"email": reply_to}

        if attachments:
            message["attachments"] = attachments

        if categories:
            message["categories"] = categories

        if custom_args:
            message["custom_args"] = custom_args

        await self._request("POST", "/mail/send", json=message)

        return {"success": True, "to": to_email}

    async def send_template_email(
        self,
        to_email: str,
        template_id: str,
        dynamic_data: dict[str, Any],
        from_email: str | None = None,
        from_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Send email using a dynamic template.

        Args:
            to_email: Recipient email
            template_id: SendGrid template ID
            dynamic_data: Template variables
            from_email: Sender email
            from_name: Sender name

        Returns:
            Send result
        """
        message = {
            "personalizations": [
                {
                    "to": [{"email": to_email}],
                    "dynamic_template_data": dynamic_data,
                }
            ],
            "from": {
                "email": from_email or self._from_email,
                "name": from_name or self._from_name,
            },
            "template_id": template_id,
        }

        await self._request("POST", "/mail/send", json=message)

        return {"success": True, "to": to_email, "template_id": template_id}

    async def send_bulk_email(
        self,
        recipients: list[dict[str, Any]],
        subject: str,
        html_content: str,
        text_content: str,
    ) -> dict[str, Any]:
        """
        Send bulk personalized emails.

        Args:
            recipients: List of {"email": str, "data": dict} for personalization
            subject: Email subject (can include {{variables}})
            html_content: HTML content (can include {{variables}})
            text_content: Plain text content

        Returns:
            Bulk send result
        """
        personalizations = [
            {
                "to": [{"email": r["email"]}],
                "dynamic_template_data": r.get("data", {}),
            }
            for r in recipients
        ]

        message = {
            "personalizations": personalizations,
            "from": {
                "email": self._from_email,
                "name": self._from_name,
            },
            "subject": subject,
            "content": [
                {"type": "text/plain", "value": text_content},
                {"type": "text/html", "value": html_content},
            ],
        }

        await self._request("POST", "/mail/send", json=message)

        return {"success": True, "recipients": len(recipients)}

    # =========================================================================
    # CONTACTS
    # =========================================================================

    async def add_contact(
        self,
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
        list_ids: list[str] | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Add or update a contact.

        Args:
            email: Contact email
            first_name: First name
            last_name: Last name
            list_ids: Lists to add contact to
            custom_fields: Custom field values

        Returns:
            Job ID for async processing
        """
        contact: dict[str, Any] = {"email": email}

        if first_name:
            contact["first_name"] = first_name
        if last_name:
            contact["last_name"] = last_name
        if custom_fields:
            contact["custom_fields"] = custom_fields

        payload: dict[str, Any] = {"contacts": [contact]}

        if list_ids:
            payload["list_ids"] = list_ids

        response = await self._request("PUT", "/marketing/contacts", json=payload)

        return {"job_id": response.get("job_id")}

    async def search_contacts(
        self,
        query: str,
    ) -> list[dict[str, Any]]:
        """
        Search contacts with SGQL query.

        Args:
            query: SGQL query string

        Returns:
            List of matching contacts
        """
        response = await self._request(
            "POST",
            "/marketing/contacts/search",
            json={"query": query},
        )

        return response.get("result", [])

    async def get_contact(self, email: str) -> dict[str, Any] | None:
        """
        Get contact by email.

        Args:
            email: Contact email

        Returns:
            Contact data or None
        """
        contacts = await self.search_contacts(f"email = '{email}'")
        return contacts[0] if contacts else None

    async def delete_contacts(self, emails: list[str]) -> dict[str, Any]:
        """
        Delete contacts by email.

        Args:
            emails: List of emails to delete

        Returns:
            Job ID
        """
        # First, get contact IDs
        query = " OR ".join([f"email = '{e}'" for e in emails])
        contacts = await self.search_contacts(query)

        if not contacts:
            return {"deleted": 0}

        ids = [c["id"] for c in contacts]

        response = await self._request(
            "DELETE",
            "/marketing/contacts",
            params={"ids": ",".join(ids)},
        )

        return {"job_id": response.get("job_id"), "deleted": len(ids)}

    # =========================================================================
    # LISTS
    # =========================================================================

    async def get_lists(self) -> list[dict[str, Any]]:
        """
        Get all contact lists.

        Returns:
            List of contact lists
        """
        response = await self._request("GET", "/marketing/lists")
        return response.get("result", [])

    async def create_list(self, name: str) -> dict[str, Any]:
        """
        Create a contact list.

        Args:
            name: List name

        Returns:
            Created list data
        """
        response = await self._request(
            "POST",
            "/marketing/lists",
            json={"name": name},
        )
        return response

    async def add_contacts_to_list(
        self,
        list_id: str,
        emails: list[str],
    ) -> dict[str, Any]:
        """
        Add contacts to a list.

        Args:
            list_id: List ID
            emails: Contact emails to add

        Returns:
            Job ID
        """
        contacts = [{"email": e} for e in emails]

        response = await self._request(
            "PUT",
            "/marketing/contacts",
            json={
                "list_ids": [list_id],
                "contacts": contacts,
            },
        )

        return {"job_id": response.get("job_id")}

    # =========================================================================
    # STATISTICS
    # =========================================================================

    async def get_global_stats(
        self,
        start_date: str,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get global email statistics.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD), defaults to today

        Returns:
            Daily statistics
        """
        params: dict[str, Any] = {"start_date": start_date}
        if end_date:
            params["end_date"] = end_date

        response = await self._request("GET", "/stats", params=params)
        return response if isinstance(response, list) else []

    async def get_category_stats(
        self,
        categories: list[str],
        start_date: str,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get statistics by category.

        Args:
            categories: Category names
            start_date: Start date
            end_date: End date

        Returns:
            Category statistics
        """
        params: dict[str, Any] = {
            "start_date": start_date,
            "categories": ",".join(categories),
        }
        if end_date:
            params["end_date"] = end_date

        response = await self._request("GET", "/categories/stats", params=params)
        return response if isinstance(response, list) else []

    async def get_bounce_stats(
        self,
        start_date: str,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """
        Get bounce statistics.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Bounce breakdown
        """
        stats = await self.get_global_stats(start_date, end_date)

        total_bounces = 0
        soft_bounces = 0
        hard_bounces = 0

        for day in stats:
            for stat in day.get("stats", []):
                metrics = stat.get("metrics", {})
                total_bounces += metrics.get("bounces", 0)
                # Note: SendGrid doesn't separate soft/hard in basic stats

        return {
            "total": total_bounces,
            "soft": soft_bounces,
            "hard": hard_bounces,
        }

    async def get_spam_report_stats(
        self,
        start_date: str,
        end_date: str | None = None,
    ) -> int:
        """
        Get spam report count.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Total spam reports
        """
        stats = await self.get_global_stats(start_date, end_date)

        total_spam = 0
        for day in stats:
            for stat in day.get("stats", []):
                metrics = stat.get("metrics", {})
                total_spam += metrics.get("spam_reports", 0)

        return total_spam

    # =========================================================================
    # SUPPRESSIONS
    # =========================================================================

    async def get_bounces(
        self,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get bounced emails.

        Args:
            start_time: Unix timestamp start
            end_time: Unix timestamp end

        Returns:
            List of bounced emails
        """
        params = {}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time

        response = await self._request("GET", "/suppression/bounces", params=params)
        return response if isinstance(response, list) else []

    async def get_spam_reports(self) -> list[dict[str, Any]]:
        """
        Get spam reports.

        Returns:
            List of spam reports
        """
        response = await self._request("GET", "/suppression/spam_reports")
        return response if isinstance(response, list) else []

    async def get_unsubscribes(self) -> list[dict[str, Any]]:
        """
        Get unsubscribed emails.

        Returns:
            List of unsubscribes
        """
        response = await self._request("GET", "/suppression/unsubscribes")
        return response if isinstance(response, list) else []

    # =========================================================================
    # SENDER VERIFICATION
    # =========================================================================

    async def get_verified_senders(self) -> list[dict[str, Any]]:
        """
        Get verified sender identities.

        Returns:
            List of verified senders
        """
        response = await self._request("GET", "/verified_senders")
        return response.get("results", [])

    async def verify_sender(
        self,
        nickname: str,
        from_email: str,
        from_name: str,
        reply_to: str | None = None,
    ) -> dict[str, Any]:
        """
        Create sender verification request.

        Args:
            nickname: Sender nickname
            from_email: Sender email
            from_name: Sender name
            reply_to: Reply-to email

        Returns:
            Verification status
        """
        payload = {
            "nickname": nickname,
            "from_email": from_email,
            "from_name": from_name,
            "reply_to": reply_to or from_email,
        }

        response = await self._request("POST", "/verified_senders", json=payload)
        return response
