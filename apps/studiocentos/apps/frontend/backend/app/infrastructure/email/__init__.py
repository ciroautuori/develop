"""
Email Infrastructure Module
IMAP reading + SMTP sending
"""

from .imap_service import IMAPEmailService, get_imap_service, EmailMessage, EmailFolder, EmailAttachment

__all__ = [
    "IMAPEmailService",
    "get_imap_service",
    "EmailMessage",
    "EmailFolder",
    "EmailAttachment",
]
