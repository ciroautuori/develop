"""
Google Docs + Drive Service
Generate PDF quotes from templates, store documents
"""
import json
import logging
from datetime import datetime
from typing import Any, Optional

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.auth.oauth_tokens import OAuthProvider, OAuthTokenService

logger = logging.getLogger(__name__)

# Google APIs Base URLs
DOCS_API_BASE = "https://docs.googleapis.com/v1"
DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"


class GoogleDocsService:
    """Service for Google Docs + Drive API - Generate quotes/invoices."""

    def __init__(self, access_token: str):
        """
        Initialize Docs/Drive service.

        Args:
            access_token: Valid Google OAuth access token with drive scope
        """
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    @classmethod
    def from_admin_token(cls, db: Session, admin_id: int) -> Optional["GoogleDocsService"]:
        """Create service instance from admin's stored OAuth token."""
        token = OAuthTokenService.get_valid_token(db, admin_id, OAuthProvider.GOOGLE)
        if not token:
            logger.warning(f"No valid Google OAuth token for admin {admin_id}")
            return None
        return cls(access_token=token)

    async def copy_template(
        self,
        template_id: str,
        new_name: str,
        folder_id: str | None = None
    ) -> str | None:
        """
        Copy a Google Docs template to create a new document.

        Args:
            template_id: ID of the template document
            new_name: Name for the new document
            folder_id: Optional folder to place the copy in

        Returns:
            New document ID or None if failed
        """
        url = f"{DRIVE_API_BASE}/files/{template_id}/copy"
        body = {"name": new_name}

        if folder_id:
            body["parents"] = [folder_id]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=body,
                    timeout=30.0
                )

                if response.status_code not in [200, 201]:
                    logger.error(f"Drive copy error: {response.status_code} - {response.text}")
                    return None

                data = response.json()
                return data.get("id")

        except Exception as e:
            logger.error(f"Error copying template: {e}", exc_info=True)
            return None

    async def replace_placeholders(
        self,
        document_id: str,
        replacements: dict[str, str]
    ) -> bool:
        """
        Replace placeholders in a document.

        Args:
            document_id: Document ID
            replacements: Dict of placeholder -> value (e.g., {"{{CLIENT_NAME}}": "Mario Rossi"})

        Returns:
            True if successful
        """
        requests = []
        for placeholder, value in replacements.items():
            requests.append({
                "replaceAllText": {
                    "containsText": {
                        "text": placeholder,
                        "matchCase": True
                    },
                    "replaceText": value
                }
            })

        url = f"{DOCS_API_BASE}/documents/{document_id}:batchUpdate"
        body = {"requests": requests}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=body,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Docs update error: {response.status_code} - {response.text}")
                    return False

                return True

        except Exception as e:
            logger.error(f"Error replacing placeholders: {e}", exc_info=True)
            return False

    async def export_as_pdf(self, document_id: str) -> bytes | None:
        """
        Export a Google Doc as PDF.

        Args:
            document_id: Document ID

        Returns:
            PDF bytes or None if failed
        """
        url = f"{DRIVE_API_BASE}/files/{document_id}/export"
        params = {"mimeType": "application/pdf"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params=params,
                    timeout=60.0
                )

                if response.status_code != 200:
                    logger.error(f"Export error: {response.status_code}")
                    return None

                return response.content

        except Exception as e:
            logger.error(f"Error exporting PDF: {e}", exc_info=True)
            return None

    async def upload_file(
        self,
        content: bytes,
        filename: str,
        mime_type: str,
        folder_id: str | None = None
    ) -> str | None:
        """
        Upload a file to Google Drive.

        Args:
            content: File content
            filename: File name
            mime_type: MIME type
            folder_id: Optional folder ID

        Returns:
            File ID or None if failed
        """
        # Metadata request
        metadata = {"name": filename}
        if folder_id:
            metadata["parents"] = [folder_id]

        # Multipart upload
        url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"


        boundary = "markettina_boundary"

        body = (
            f"--{boundary}\r\n"
            f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
            f"{json.dumps(metadata)}\r\n"
            f"--{boundary}\r\n"
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode() + content + f"\r\n--{boundary}--".encode()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": f"multipart/related; boundary={boundary}"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    content=body,
                    timeout=60.0
                )

                if response.status_code not in [200, 201]:
                    logger.error(f"Upload error: {response.status_code} - {response.text}")
                    return None

                data = response.json()
                return data.get("id")

        except Exception as e:
            logger.error(f"Error uploading file: {e}", exc_info=True)
            return None

    async def get_file_link(
        self,
        file_id: str,
        share_publicly: bool = True
    ) -> str | None:
        """
        Get a shareable link for a file.

        Args:
            file_id: File ID
            share_publicly: Whether to make the file public

        Returns:
            Shareable link or None
        """
        if share_publicly:
            # Create public permission
            url = f"{DRIVE_API_BASE}/files/{file_id}/permissions"
            body = {
                "type": "anyone",
                "role": "reader"
            }

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        headers=self.headers,
                        json=body,
                        timeout=30.0
                    )

                    if response.status_code not in [200, 201]:
                        logger.warning(f"Could not share file: {response.text}")

            except Exception as e:
                logger.warning(f"Error sharing file: {e}")

        # Get web view link
        url = f"{DRIVE_API_BASE}/files/{file_id}"
        params = {"fields": "webViewLink,webContentLink"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code != 200:
                    return None

                data = response.json()
                return data.get("webViewLink") or data.get("webContentLink")

        except Exception as e:
            logger.error(f"Error getting file link: {e}", exc_info=True)
            return None

    async def create_folder(
        self,
        name: str,
        parent_id: str | None = None
    ) -> str | None:
        """Create a folder in Google Drive."""
        url = f"{DRIVE_API_BASE}/files"
        body = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder"
        }

        if parent_id:
            body["parents"] = [parent_id]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=body,
                    timeout=30.0
                )

                if response.status_code not in [200, 201]:
                    logger.error(f"Folder create error: {response.status_code}")
                    return None

                return response.json().get("id")

        except Exception as e:
            logger.error(f"Error creating folder: {e}", exc_info=True)
            return None

    async def list_files(
        self,
        folder_id: str | None = None,
        mime_type: str | None = None,
        max_results: int = 50
    ) -> list[dict[str, Any]]:
        """List files in Drive."""
        url = f"{DRIVE_API_BASE}/files"

        query_parts = ["trashed = false"]
        if folder_id:
            query_parts.append(f"'{folder_id}' in parents")
        if mime_type:
            query_parts.append(f"mimeType = '{mime_type}'")

        params = {
            "q": " and ".join(query_parts),
            "pageSize": max_results,
            "fields": "files(id, name, mimeType, createdTime, webViewLink)"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code != 200:
                    return []

                data = response.json()
                return data.get("files", [])

        except Exception as e:
            logger.error(f"Error listing files: {e}", exc_info=True)
            return []


# =============================================================================
# Quote Generation Functions
# =============================================================================

async def generate_quote_pdf(
    db: Session,
    admin_id: int,
    template_id: str,
    quote_data: dict[str, Any],
    output_folder_id: str | None = None
) -> dict[str, str] | None:
    """
    Generate a quote PDF from a Google Docs template.

    Args:
        db: Database session
        admin_id: Admin user ID
        template_id: Google Docs template ID
        quote_data: Quote information including:
            - quote_number: str
            - client_name: str
            - client_email: str
            - client_company: str
            - client_address: str
            - project_title: str
            - project_description: str
            - items: List of {description, quantity, unit_price, total}
            - subtotal: float
            - vat_rate: float
            - vat_amount: float
            - total: float
            - valid_until: date
            - notes: str
        output_folder_id: Optional folder to store the PDF

    Returns:
        Dict with pdf_id, pdf_link, doc_id, doc_link
    """
    service = GoogleDocsService.from_admin_token(db, admin_id)
    if not service:
        logger.error("Could not create Docs service")
        return None

    # 1. Copy template
    quote_number = quote_data.get("quote_number", f"Q-{datetime.now().strftime('%Y%m%d%H%M')}")
    new_doc_name = f"Preventivo_{quote_number}_{quote_data.get('client_name', 'Cliente')}"

    doc_id = await service.copy_template(template_id, new_doc_name, output_folder_id)
    if not doc_id:
        logger.error("Failed to copy template")
        return None

    # 2. Build replacements
    today = datetime.now()
    valid_until = quote_data.get("valid_until", today + timedelta(days=30))
    if isinstance(valid_until, str):
        valid_until = datetime.fromisoformat(valid_until)

    # Build items table
    items = quote_data.get("items", [])
    items_text = ""
    for i, item in enumerate(items, 1):
        items_text += f"{i}. {item.get('description', '')}\n"
        items_text += f"   Quantità: {item.get('quantity', 1)} | "
        items_text += f"Prezzo: €{item.get('unit_price', 0):,.2f} | "
        items_text += f"Totale: €{item.get('total', 0):,.2f}\n\n"

    replacements = {
        "{{QUOTE_NUMBER}}": quote_number,
        "{{DATE}}": today.strftime("%d/%m/%Y"),
        "{{VALID_UNTIL}}": valid_until.strftime("%d/%m/%Y") if hasattr(valid_until, "strftime") else str(valid_until),
        "{{CLIENT_NAME}}": quote_data.get("client_name", ""),
        "{{CLIENT_EMAIL}}": quote_data.get("client_email", ""),
        "{{CLIENT_COMPANY}}": quote_data.get("client_company", ""),
        "{{CLIENT_ADDRESS}}": quote_data.get("client_address", ""),
        "{{PROJECT_TITLE}}": quote_data.get("project_title", ""),
        "{{PROJECT_DESCRIPTION}}": quote_data.get("project_description", ""),
        "{{ITEMS}}": items_text,
        "{{SUBTOTAL}}": f"€{quote_data.get('subtotal', 0):,.2f}",
        "{{VAT_RATE}}": f"{quote_data.get('vat_rate', 22)}%",
        "{{VAT_AMOUNT}}": f"€{quote_data.get('vat_amount', 0):,.2f}",
        "{{TOTAL}}": f"€{quote_data.get('total', 0):,.2f}",
        "{{NOTES}}": quote_data.get("notes", ""),
        "{{COMPANY_NAME}}": "MARKETTINA",
        "{{COMPANY_ADDRESS}}": "Milano, Italia",
        "{{COMPANY_EMAIL}}": "info@markettina.it",
        "{{COMPANY_VAT}}": "IT12345678901",
    }

    # 3. Replace placeholders
    success = await service.replace_placeholders(doc_id, replacements)
    if not success:
        logger.warning("Some placeholder replacements may have failed")

    # 4. Export as PDF
    pdf_content = await service.export_as_pdf(doc_id)
    if not pdf_content:
        logger.error("Failed to export PDF")
        return {
            "doc_id": doc_id,
            "doc_link": await service.get_file_link(doc_id)
        }

    # 5. Upload PDF
    pdf_filename = f"{new_doc_name}.pdf"
    pdf_id = await service.upload_file(
        content=pdf_content,
        filename=pdf_filename,
        mime_type="application/pdf",
        folder_id=output_folder_id
    )

    # 6. Get links
    doc_link = await service.get_file_link(doc_id)
    pdf_link = await service.get_file_link(pdf_id) if pdf_id else None

    logger.info(f"Generated quote: {quote_number} - PDF: {pdf_id}")

    return {
        "doc_id": doc_id,
        "doc_link": doc_link,
        "pdf_id": pdf_id,
        "pdf_link": pdf_link,
        "quote_number": quote_number
    }


# =============================================================================
# Template Management
# =============================================================================

# Default quote template (create this in your Google Drive)
DEFAULT_QUOTE_TEMPLATE_ID = settings.GOOGLE_QUOTE_TEMPLATE_ID if hasattr(settings, "GOOGLE_QUOTE_TEMPLATE_ID") else None


async def get_or_create_quotes_folder(
    db: Session,
    admin_id: int
) -> str | None:
    """Get or create a folder for storing quotes."""
    service = GoogleDocsService.from_admin_token(db, admin_id)
    if not service:
        return None

    # Check if folder exists
    files = await service.list_files(
        mime_type="application/vnd.google-apps.folder"
    )

    for file in files:
        if file.get("name") == "MARKETTINA_Preventivi":
            return file.get("id")

    # Create folder
    folder_id = await service.create_folder("MARKETTINA_Preventivi")
    return folder_id


from datetime import timedelta
