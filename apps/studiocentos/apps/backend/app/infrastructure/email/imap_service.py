"""
IMAP Email Reader Service - Register.it Webmail Integration
Legge email dalla casella info@studiocentos.it via IMAP SSL
"""

import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import os
import re

logger = logging.getLogger(__name__)


@dataclass
class EmailAttachment:
    """Attachment data."""
    filename: str
    content_type: str
    size: int


@dataclass
class EmailMessage:
    """Parsed email message."""
    id: str
    subject: str
    from_email: str
    from_name: Optional[str]
    to_email: str
    date: datetime
    body_text: Optional[str]
    body_html: Optional[str]
    is_read: bool
    is_starred: bool
    attachments: List[EmailAttachment] = field(default_factory=list)
    folder: str = "INBOX"


@dataclass
class EmailFolder:
    """Email folder info."""
    name: str
    display_name: str
    total: int
    unread: int


class IMAPEmailService:
    """
    IMAP Email Service for Register.it Webmail.
    Supports reading, searching, and managing emails.
    """

    def __init__(
        self,
        host: str = None,
        port: int = 993,
        username: str = None,
        password: str = None,
        use_ssl: bool = True
    ):
        self.host = host or os.getenv("IMAP_HOST", "imaps.register.it")
        self.port = port or int(os.getenv("IMAP_PORT", "993"))
        self.username = username or os.getenv("IMAP_USERNAME", "")
        self.password = password or os.getenv("IMAP_PASSWORD", "")
        self.use_ssl = use_ssl
        self._connection: Optional[imaplib.IMAP4_SSL] = None

    def _connect(self) -> imaplib.IMAP4_SSL:
        """Establish IMAP connection."""
        if self._connection:
            try:
                self._connection.noop()
                return self._connection
            except:
                self._connection = None

        try:
            if self.use_ssl:
                self._connection = imaplib.IMAP4_SSL(self.host, self.port)
            else:
                self._connection = imaplib.IMAP4(self.host, self.port)

            self._connection.login(self.username, self.password)
            logger.info(f"IMAP connected to {self.host} as {self.username}")
            return self._connection
        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")
            raise ConnectionError(f"Failed to connect to IMAP server: {e}")

    def _disconnect(self):
        """Close IMAP connection."""
        if self._connection:
            try:
                self._connection.logout()
            except:
                pass
            self._connection = None

    def _decode_header_value(self, value: str) -> str:
        """Decode email header value."""
        if not value:
            return ""

        decoded_parts = []
        for part, encoding in decode_header(value):
            if isinstance(part, bytes):
                try:
                    decoded_parts.append(part.decode(encoding or 'utf-8', errors='replace'))
                except:
                    decoded_parts.append(part.decode('utf-8', errors='replace'))
            else:
                decoded_parts.append(part)

        return ' '.join(decoded_parts)

    def _parse_email_address(self, addr: str) -> tuple[str, str]:
        """Parse email address into (name, email)."""
        if not addr:
            return ("", "")

        # Pattern: "Name" <email@domain.com> or just email@domain.com
        match = re.match(r'^"?([^"<]*)"?\s*<?([^>]+)>?$', addr.strip())
        if match:
            name = match.group(1).strip().strip('"')
            email_addr = match.group(2).strip()
            return (name, email_addr)

        return ("", addr.strip())

    def _get_email_body(self, msg: email.message.Message) -> tuple[Optional[str], Optional[str]]:
        """Extract text and HTML body from email."""
        text_body = None
        html_body = None

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in content_disposition:
                    continue

                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        decoded = payload.decode(charset, errors='replace')

                        if content_type == "text/plain" and not text_body:
                            text_body = decoded
                        elif content_type == "text/html" and not html_body:
                            html_body = decoded
                except Exception as e:
                    logger.warning(f"Failed to decode email part: {e}")
        else:
            content_type = msg.get_content_type()
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or 'utf-8'
                    decoded = payload.decode(charset, errors='replace')

                    if content_type == "text/plain":
                        text_body = decoded
                    elif content_type == "text/html":
                        html_body = decoded
            except Exception as e:
                logger.warning(f"Failed to decode email body: {e}")

        return text_body, html_body

    def _get_attachments(self, msg: email.message.Message) -> List[EmailAttachment]:
        """Extract attachment info from email."""
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        filename = self._decode_header_value(filename)
                        content_type = part.get_content_type()
                        payload = part.get_payload(decode=True)
                        size = len(payload) if payload else 0

                        attachments.append(EmailAttachment(
                            filename=filename,
                            content_type=content_type,
                            size=size
                        ))

        return attachments

    def _parse_message(self, msg_id: str, msg_data: bytes, folder: str = "INBOX") -> EmailMessage:
        """Parse raw email data into EmailMessage."""
        msg = email.message_from_bytes(msg_data)

        # Parse headers
        subject = self._decode_header_value(msg.get("Subject", "(Nessun oggetto)"))
        from_header = self._decode_header_value(msg.get("From", ""))
        to_header = self._decode_header_value(msg.get("To", ""))

        from_name, from_email = self._parse_email_address(from_header)
        _, to_email = self._parse_email_address(to_header)

        # Parse date
        date_str = msg.get("Date", "")
        try:
            date = parsedate_to_datetime(date_str)
        except:
            date = datetime.now()

        # Get body
        text_body, html_body = self._get_email_body(msg)

        # Get attachments
        attachments = self._get_attachments(msg)

        return EmailMessage(
            id=msg_id,
            subject=subject,
            from_email=from_email,
            from_name=from_name if from_name else None,
            to_email=to_email,
            date=date,
            body_text=text_body,
            body_html=html_body,
            is_read=True,  # Will be updated based on flags
            is_starred=False,
            attachments=attachments,
            folder=folder
        )

    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================

    async def get_folders(self) -> List[EmailFolder]:
        """Get list of email folders."""
        def _get_folders():
            conn = self._connect()
            folders = []

            status, folder_list = conn.list()
            if status != "OK":
                return folders

            for folder_data in folder_list:
                if folder_data:
                    # Parse folder name
                    match = re.search(r'"([^"]+)"$|(\S+)$', folder_data.decode())
                    if match:
                        folder_name = match.group(1) or match.group(2)

                        # Get folder stats
                        try:
                            conn.select(folder_name, readonly=True)
                            status, messages = conn.search(None, "ALL")
                            total = len(messages[0].split()) if status == "OK" and messages[0] else 0

                            status, unseen = conn.search(None, "UNSEEN")
                            unread = len(unseen[0].split()) if status == "OK" and unseen[0] else 0

                            # Display name mapping
                            display_names = {
                                "INBOX": "Posta in arrivo",
                                "Sent": "Inviati",
                                "Drafts": "Bozze",
                                "Trash": "Cestino",
                                "Spam": "Spam",
                                "Junk": "Spam",
                            }

                            folders.append(EmailFolder(
                                name=folder_name,
                                display_name=display_names.get(folder_name, folder_name),
                                total=total,
                                unread=unread
                            ))
                        except Exception as e:
                            logger.warning(f"Failed to get stats for folder {folder_name}: {e}")

            return folders

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_folders)

    async def get_emails(
        self,
        folder: str = "INBOX",
        limit: int = 50,
        offset: int = 0,
        search_query: Optional[str] = None,
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """
        Get emails from folder.

        Args:
            folder: Folder name (INBOX, Sent, etc.)
            limit: Max emails to return
            offset: Offset for pagination
            search_query: Optional search query
            unread_only: Only return unread emails

        Returns:
            Dict with emails list and pagination info
        """
        def _get_emails():
            conn = self._connect()

            # Select folder
            status, _ = conn.select(folder, readonly=True)
            if status != "OK":
                raise ValueError(f"Failed to select folder: {folder}")

            # Build search criteria
            criteria = []
            if unread_only:
                criteria.append("UNSEEN")
            if search_query:
                # Search in subject and from
                criteria.append(f'OR SUBJECT "{search_query}" FROM "{search_query}"')

            if not criteria:
                criteria = ["ALL"]

            # Search
            status, messages = conn.search(None, *criteria)
            if status != "OK":
                return {"emails": [], "total": 0, "unread": 0}

            msg_ids = messages[0].split() if messages[0] else []
            total = len(msg_ids)

            # Reverse for newest first
            msg_ids = list(reversed(msg_ids))

            # Apply pagination
            paginated_ids = msg_ids[offset:offset + limit]

            emails = []
            for msg_id in paginated_ids:
                try:
                    # Fetch email
                    status, msg_data = conn.fetch(msg_id, "(RFC822 FLAGS)")
                    if status != "OK":
                        continue

                    # Parse flags
                    flags_match = re.search(rb'FLAGS \(([^)]*)\)', msg_data[0][0])
                    flags = flags_match.group(1).decode() if flags_match else ""
                    is_read = "\\Seen" in flags
                    is_starred = "\\Flagged" in flags

                    # Parse message
                    raw_email = msg_data[0][1]
                    email_msg = self._parse_message(msg_id.decode(), raw_email, folder)
                    email_msg.is_read = is_read
                    email_msg.is_starred = is_starred

                    emails.append(email_msg)
                except Exception as e:
                    logger.warning(f"Failed to parse email {msg_id}: {e}")

            # Get unread count
            status, unseen = conn.search(None, "UNSEEN")
            unread = len(unseen[0].split()) if status == "OK" and unseen[0] else 0

            return {
                "emails": emails,
                "total": total,
                "unread": unread,
                "limit": limit,
                "offset": offset
            }

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_emails)

    async def get_email(self, msg_id: str, folder: str = "INBOX") -> Optional[EmailMessage]:
        """Get single email by ID."""
        def _get_email():
            conn = self._connect()

            status, _ = conn.select(folder, readonly=True)
            if status != "OK":
                return None

            status, msg_data = conn.fetch(msg_id.encode(), "(RFC822 FLAGS)")
            if status != "OK":
                return None

            # Parse flags
            flags_match = re.search(rb'FLAGS \(([^)]*)\)', msg_data[0][0])
            flags = flags_match.group(1).decode() if flags_match else ""
            is_read = "\\Seen" in flags
            is_starred = "\\Flagged" in flags

            raw_email = msg_data[0][1]
            email_msg = self._parse_message(msg_id, raw_email, folder)
            email_msg.is_read = is_read
            email_msg.is_starred = is_starred

            return email_msg

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_email)

    async def mark_as_read(self, msg_id: str, folder: str = "INBOX") -> bool:
        """Mark email as read."""
        def _mark_read():
            conn = self._connect()
            conn.select(folder)
            status, _ = conn.store(msg_id.encode(), "+FLAGS", "\\Seen")
            return status == "OK"

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _mark_read)

    async def mark_as_unread(self, msg_id: str, folder: str = "INBOX") -> bool:
        """Mark email as unread."""
        def _mark_unread():
            conn = self._connect()
            conn.select(folder)
            status, _ = conn.store(msg_id.encode(), "-FLAGS", "\\Seen")
            return status == "OK"

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _mark_unread)

    async def toggle_star(self, msg_id: str, starred: bool, folder: str = "INBOX") -> bool:
        """Toggle star/flag on email."""
        def _toggle_star():
            conn = self._connect()
            conn.select(folder)
            flag_op = "+FLAGS" if starred else "-FLAGS"
            status, _ = conn.store(msg_id.encode(), flag_op, "\\Flagged")
            return status == "OK"

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _toggle_star)

    async def delete_email(self, msg_id: str, folder: str = "INBOX") -> bool:
        """Move email to trash."""
        def _delete():
            conn = self._connect()
            conn.select(folder)
            # Mark as deleted
            status, _ = conn.store(msg_id.encode(), "+FLAGS", "\\Deleted")
            if status == "OK":
                conn.expunge()
                return True
            return False

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _delete)

    async def move_email(self, msg_id: str, from_folder: str, to_folder: str) -> bool:
        """Move email to another folder."""
        def _move():
            conn = self._connect()
            conn.select(from_folder)

            # Copy to destination
            status, _ = conn.copy(msg_id.encode(), to_folder)
            if status != "OK":
                return False

            # Delete from source
            conn.store(msg_id.encode(), "+FLAGS", "\\Deleted")
            conn.expunge()
            return True

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _move)

    async def test_connection(self) -> Dict[str, Any]:
        """Test IMAP connection."""
        def _test():
            try:
                conn = self._connect()
                status, _ = conn.select("INBOX", readonly=True)

                if status == "OK":
                    status, messages = conn.search(None, "ALL")
                    total = len(messages[0].split()) if messages[0] else 0

                    status, unseen = conn.search(None, "UNSEEN")
                    unread = len(unseen[0].split()) if unseen[0] else 0

                    return {
                        "connected": True,
                        "server": self.host,
                        "username": self.username,
                        "inbox_total": total,
                        "inbox_unread": unread
                    }

                return {"connected": False, "error": "Failed to select INBOX"}
            except Exception as e:
                return {"connected": False, "error": str(e)}

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _test)


# Singleton instance (will be configured at runtime)
imap_service: Optional[IMAPEmailService] = None


def get_imap_service() -> IMAPEmailService:
    """Get or create IMAP service instance."""
    global imap_service
    if imap_service is None:
        imap_service = IMAPEmailService()
    return imap_service
