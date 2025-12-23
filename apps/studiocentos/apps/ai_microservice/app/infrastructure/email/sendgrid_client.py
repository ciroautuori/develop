"""
SendGrid Email API Client.

Production-ready client for SendGrid v3 API with:
- Transactional emails
- Marketing campaigns
- Contact management
- Template support
- Analytics/stats

API Reference: https://docs.sendgrid.com/api-reference
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class SendGridError(Exception):
    """SendGrid API error."""

    def __init__(self, message: str, status_code: Optional[int] = None, errors: Optional[List[Dict]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.errors = errors or []


class SendGridClient:
    """
    SendGrid Email API Client.

    Provides:
    - Send transactional emails
    - Create and send marketing campaigns
    - Manage contacts and lists
    - Use dynamic templates
    - Track email analytics

    Example:
        >>> client = SendGridClient(api_key=os.getenv("SENDGRID_API_KEY"))
        >>> await client.send_email(
        ...     to="customer@example.com",
        ...     subject="Welcome!",
        ...     html_content="<h1>Welcome to our service</h1>",
        ... )
    """

    API_BASE = "https://api.sendgrid.com/v3"

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ):
        """
        Initialize SendGrid client.

        Args:
            api_key: SendGrid API key
            from_email: Default sender email
            from_name: Default sender name
        """
        self.api_key = api_key or os.getenv("SENDGRID_API_KEY", "")
        self.from_email = from_email or os.getenv("SENDGRID_FROM_EMAIL", "noreply@studiocentos.it")
        self.from_name = from_name or os.getenv("SENDGRID_FROM_NAME", "StudioCentos")

        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
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
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make API request."""
        url = f"{self.API_BASE}{endpoint}"

        response = await self.client.request(method, url, **kwargs)

        if response.status_code >= 400:
            errors = []
            try:
                error_data = response.json()
                errors = error_data.get("errors", [])
            except Exception:
                pass

            raise SendGridError(
                f"SendGrid API error: {response.status_code}",
                status_code=response.status_code,
                errors=errors,
            )

        if response.status_code == 204 or not response.content:
            return {}

        return response.json()

    # =========================================================================
    # TRANSACTIONAL EMAIL
    # =========================================================================

    async def send_email(
        self,
        to: str | List[str],
        subject: str,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, str]]] = None,
        categories: Optional[List[str]] = None,
        custom_args: Optional[Dict[str, str]] = None,
        send_at: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Send a transactional email.

        Args:
            to: Recipient email(s)
            subject: Email subject
            html_content: HTML body
            text_content: Plain text body
            from_email: Sender email (overrides default)
            from_name: Sender name (overrides default)
            reply_to: Reply-to email
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of attachments [{"content": base64, "filename": "file.pdf", "type": "application/pdf"}]
            categories: Email categories for tracking
            custom_args: Custom tracking args
            send_at: Unix timestamp for scheduled send

        Returns:
            Message ID and status
        """
        # Build recipients
        recipients = [to] if isinstance(to, str) else to

        personalizations: List[Dict[str, Any]] = [{
            "to": [{"email": email} for email in recipients],
        }]

        if cc:
            personalizations[0]["cc"] = [{"email": email} for email in cc]
        if bcc:
            personalizations[0]["bcc"] = [{"email": email} for email in bcc]
        if custom_args:
            personalizations[0]["custom_args"] = custom_args
        if send_at:
            personalizations[0]["send_at"] = send_at

        # Build message
        payload: Dict[str, Any] = {
            "personalizations": personalizations,
            "from": {
                "email": from_email or self.from_email,
                "name": from_name or self.from_name,
            },
            "subject": subject,
        }

        # Content
        content = []
        if text_content:
            content.append({"type": "text/plain", "value": text_content})
        if html_content:
            content.append({"type": "text/html", "value": html_content})

        if not content:
            raise SendGridError("Either html_content or text_content required")

        payload["content"] = content

        # Optional fields
        if reply_to:
            payload["reply_to"] = {"email": reply_to}
        if attachments:
            payload["attachments"] = attachments
        if categories:
            payload["categories"] = categories

        result = await self._request("POST", "/mail/send", json=payload)

        logger.info(f"✅ Email sent to {len(recipients)} recipient(s)")

        return {"status": "sent", "recipients": len(recipients)}

    async def send_template_email(
        self,
        to: str | List[str],
        template_id: str,
        dynamic_data: Optional[Dict[str, Any]] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        categories: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send email using a dynamic template.

        Args:
            to: Recipient email(s)
            template_id: SendGrid template ID
            dynamic_data: Template variables
            from_email: Sender email
            from_name: Sender name
            categories: Categories for tracking

        Returns:
            Message ID and status
        """
        recipients = [to] if isinstance(to, str) else to

        personalizations: List[Dict[str, Any]] = [{
            "to": [{"email": email} for email in recipients],
        }]

        if dynamic_data:
            personalizations[0]["dynamic_template_data"] = dynamic_data

        payload = {
            "personalizations": personalizations,
            "from": {
                "email": from_email or self.from_email,
                "name": from_name or self.from_name,
            },
            "template_id": template_id,
        }

        if categories:
            payload["categories"] = categories

        result = await self._request("POST", "/mail/send", json=payload)

        logger.info(f"✅ Template email sent to {len(recipients)} recipient(s)")

        return {"status": "sent", "template_id": template_id, "recipients": len(recipients)}

    # =========================================================================
    # CONTACTS & LISTS
    # =========================================================================

    async def add_contact(
        self,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        custom_fields: Optional[Dict[str, str]] = None,
        list_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Add or update a contact.

        Args:
            email: Contact email
            first_name: First name
            last_name: Last name
            custom_fields: Custom field values
            list_ids: Lists to add contact to

        Returns:
            Job ID for import
        """
        contact: Dict[str, Any] = {"email": email}

        if first_name:
            contact["first_name"] = first_name
        if last_name:
            contact["last_name"] = last_name
        if custom_fields:
            contact["custom_fields"] = custom_fields

        payload: Dict[str, Any] = {"contacts": [contact]}

        if list_ids:
            payload["list_ids"] = list_ids

        result = await self._request("PUT", "/marketing/contacts", json=payload)

        logger.info(f"✅ Contact added/updated: {email}")

        return result

    async def add_contacts_bulk(
        self,
        contacts: List[Dict[str, Any]],
        list_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Bulk add or update contacts.

        Args:
            contacts: List of contact dicts with email, first_name, etc.
            list_ids: Lists to add contacts to

        Returns:
            Job ID for import
        """
        payload: Dict[str, Any] = {"contacts": contacts}

        if list_ids:
            payload["list_ids"] = list_ids

        result = await self._request("PUT", "/marketing/contacts", json=payload)

        logger.info(f"✅ Bulk contacts added: {len(contacts)}")

        return result

    async def get_contact(self, email: str) -> Optional[Dict[str, Any]]:
        """Get contact by email."""
        try:
            result = await self._request(
                "POST",
                "/marketing/contacts/search",
                json={"query": f"email LIKE '{email}'"},
            )

            contacts = result.get("result", [])
            return contacts[0] if contacts else None

        except SendGridError as e:
            if e.status_code == 404:
                return None
            raise

    async def delete_contact(self, email: str) -> bool:
        """Delete contact by email."""
        contact = await self.get_contact(email)

        if not contact:
            return False

        contact_id = contact.get("id")

        await self._request(
            "DELETE",
            "/marketing/contacts",
            params={"ids": contact_id},
        )

        logger.info(f"✅ Contact deleted: {email}")

        return True

    async def get_lists(self) -> List[Dict[str, Any]]:
        """Get all contact lists."""
        result = await self._request("GET", "/marketing/lists")
        return result.get("result", [])

    async def create_list(
        self,
        name: str,
    ) -> Dict[str, Any]:
        """Create a contact list."""
        result = await self._request(
            "POST",
            "/marketing/lists",
            json={"name": name},
        )

        logger.info(f"✅ List created: {name}")

        return result

    async def add_contacts_to_list(
        self,
        list_id: str,
        contact_ids: List[str],
    ) -> Dict[str, Any]:
        """Add contacts to a list."""
        result = await self._request(
            "POST",
            f"/marketing/lists/{list_id}/contacts",
            json={"contact_ids": contact_ids},
        )

        logger.info(f"✅ Added {len(contact_ids)} contacts to list {list_id}")

        return result

    # =========================================================================
    # MARKETING CAMPAIGNS
    # =========================================================================

    async def create_single_send(
        self,
        name: str,
        subject: str,
        html_content: str,
        sender_id: int,
        list_ids: List[str],
        categories: Optional[List[str]] = None,
        send_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Create a marketing single send (campaign).

        Args:
            name: Campaign name
            subject: Email subject
            html_content: HTML content
            sender_id: Verified sender ID
            list_ids: Target list IDs
            categories: Categories for tracking
            send_at: Scheduled send time

        Returns:
            Single send details
        """
        payload: Dict[str, Any] = {
            "name": name,
            "send_to": {"list_ids": list_ids},
            "email_config": {
                "subject": subject,
                "html_content": html_content,
                "sender_id": sender_id,
            },
        }

        if categories:
            payload["email_config"]["categories"] = categories

        if send_at:
            payload["send_at"] = send_at.isoformat()

        result = await self._request(
            "POST",
            "/marketing/singlesends",
            json=payload,
        )

        logger.info(f"✅ Single send created: {name}")

        return result

    async def schedule_single_send(
        self,
        single_send_id: str,
        send_at: datetime,
    ) -> Dict[str, Any]:
        """Schedule a single send for delivery."""
        result = await self._request(
            "PUT",
            f"/marketing/singlesends/{single_send_id}/schedule",
            json={"send_at": send_at.isoformat()},
        )

        logger.info(f"✅ Single send scheduled: {single_send_id}")

        return result

    async def send_single_send_now(
        self,
        single_send_id: str,
    ) -> Dict[str, Any]:
        """Send a single send immediately."""
        result = await self._request(
            "PUT",
            f"/marketing/singlesends/{single_send_id}/schedule",
            json={"send_at": "now"},
        )

        logger.info(f"✅ Single send sent now: {single_send_id}")

        return result

    # =========================================================================
    # TEMPLATES
    # =========================================================================

    async def get_templates(
        self,
        generations: str = "dynamic",
    ) -> List[Dict[str, Any]]:
        """Get all templates."""
        result = await self._request(
            "GET",
            "/templates",
            params={"generations": generations, "page_size": 100},
        )
        return result.get("result", [])

    async def create_template(
        self,
        name: str,
        generation: str = "dynamic",
    ) -> Dict[str, Any]:
        """Create a new template."""
        result = await self._request(
            "POST",
            "/templates",
            json={"name": name, "generation": generation},
        )

        logger.info(f"✅ Template created: {name}")

        return result

    async def create_template_version(
        self,
        template_id: str,
        name: str,
        subject: str,
        html_content: str,
        active: int = 1,
    ) -> Dict[str, Any]:
        """Create a template version."""
        result = await self._request(
            "POST",
            f"/templates/{template_id}/versions",
            json={
                "name": name,
                "subject": subject,
                "html_content": html_content,
                "active": active,
            },
        )

        logger.info(f"✅ Template version created: {name}")

        return result

    # =========================================================================
    # ANALYTICS
    # =========================================================================

    async def get_stats(
        self,
        start_date: str,
        end_date: Optional[str] = None,
        aggregated_by: str = "day",
    ) -> List[Dict[str, Any]]:
        """
        Get email statistics.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            aggregated_by: day, week, or month

        Returns:
            List of stats by date
        """
        params: Dict[str, Any] = {
            "start_date": start_date,
            "aggregated_by": aggregated_by,
        }

        if end_date:
            params["end_date"] = end_date

        result = await self._request("GET", "/stats", params=params)

        return result

    async def get_category_stats(
        self,
        categories: List[str],
        start_date: str,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get stats by category."""
        params: Dict[str, Any] = {
            "categories": ",".join(categories),
            "start_date": start_date,
        }

        if end_date:
            params["end_date"] = end_date

        result = await self._request("GET", "/categories/stats", params=params)

        return result

    async def get_campaign_stats(
        self,
        single_send_id: str,
    ) -> Dict[str, Any]:
        """Get stats for a specific single send campaign."""
        result = await self._request(
            "GET",
            f"/marketing/stats/singlesends/{single_send_id}",
        )

        return result

    # =========================================================================
    # SUPPRESSIONS
    # =========================================================================

    async def add_to_unsubscribe_group(
        self,
        group_id: int,
        emails: List[str],
    ) -> Dict[str, Any]:
        """Add emails to an unsubscribe group."""
        result = await self._request(
            "POST",
            f"/asm/groups/{group_id}/suppressions",
            json={"recipient_emails": emails},
        )

        logger.info(f"✅ Added {len(emails)} emails to unsubscribe group {group_id}")

        return result

    async def add_to_global_unsubscribe(
        self,
        emails: List[str],
    ) -> Dict[str, Any]:
        """Add emails to global unsubscribe list."""
        result = await self._request(
            "POST",
            "/asm/suppressions/global",
            json={"recipient_emails": emails},
        )

        logger.info(f"✅ Added {len(emails)} emails to global unsubscribe")

        return result

    async def check_suppression(
        self,
        email: str,
    ) -> Dict[str, Any]:
        """Check if email is suppressed."""
        result = await self._request(
            "GET",
            f"/suppression/unsubscribes/{email}",
        )

        return result

    # =========================================================================
    # SENDERS
    # =========================================================================

    async def get_senders(self) -> List[Dict[str, Any]]:
        """Get all verified senders."""
        result = await self._request("GET", "/marketing/senders")
        return result.get("results", [])

    async def create_sender(
        self,
        nickname: str,
        from_email: str,
        from_name: str,
        reply_to: str,
        address: str,
        city: str,
        country: str,
    ) -> Dict[str, Any]:
        """Create a sender identity."""
        result = await self._request(
            "POST",
            "/marketing/senders",
            json={
                "nickname": nickname,
                "from": {"email": from_email, "name": from_name},
                "reply_to": {"email": reply_to},
                "address": address,
                "city": city,
                "country": country,
            },
        )

        logger.info(f"✅ Sender created: {nickname}")

        return result

    # =========================================================================
    # ADDITIONAL METHODS FOR EMAIL MARKETING AGENT
    # =========================================================================

    async def get_contacts(
        self,
        page_size: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Get all contacts."""
        try:
            result = await self._request(
                "POST",
                "/marketing/contacts/search",
                json={"query": ""},
            )
            return result.get("result", [])
        except SendGridError as e:
            if e.status_code == 404:
                return []
            raise

    async def search_contacts(
        self,
        email: str,
    ) -> List[Dict[str, Any]]:
        """Search contacts by email."""
        try:
            result = await self._request(
                "POST",
                "/marketing/contacts/search",
                json={"query": f"email LIKE '%{email}%'"},
            )
            return result.get("result", [])
        except SendGridError:
            return []

    async def get_contact_activity(
        self,
        email: str,
    ) -> List[Dict[str, Any]]:
        """Get email activity for a contact."""
        try:
            # Get email activity using v3 API
            result = await self._request(
                "GET",
                "/messages",
                params={"query": f"to_email=\"{email}\"", "limit": 100},
            )
            return result.get("messages", [])
        except SendGridError:
            return []

    async def get_global_stats(
        self,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """Get global email statistics for recent days."""
        from datetime import datetime, timedelta

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        try:
            result = await self._request(
                "GET",
                "/stats",
                params={
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                },
            )

            # Flatten stats from daily format
            stats = []
            for day_stat in result:
                for metric in day_stat.get("stats", []):
                    stats.append(metric.get("metrics", {}))

            return stats
        except SendGridError:
            return []

    async def get_suppressions(
        self,
    ) -> List[Dict[str, Any]]:
        """Get all suppressions (bounces, spam reports, unsubscribes)."""
        suppressions = []

        try:
            # Get bounces
            bounces = await self._request("GET", "/suppression/bounces")
            suppressions.extend([{"type": "bounce", **b} for b in bounces])
        except SendGridError:
            pass

        try:
            # Get spam reports
            spam = await self._request("GET", "/suppression/spam_reports")
            suppressions.extend([{"type": "spam_report", **s} for s in spam])
        except SendGridError:
            pass

        try:
            # Get global unsubscribes
            unsubs = await self._request("GET", "/suppression/unsubscribes")
            suppressions.extend([{"type": "unsubscribe", **u} for u in unsubs])
        except SendGridError:
            pass

        return suppressions
