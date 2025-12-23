"""
Email Marketing Infrastructure.

Production-ready clients for email marketing:
- SendGrid Email API
- AWS SES (future)
- Mailchimp (future)
"""

from .sendgrid_client import SendGridClient, SendGridError

__all__ = [
    "SendGridClient",
    "SendGridError",
]
