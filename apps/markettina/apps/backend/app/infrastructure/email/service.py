"""
Email Service - Send emails using SMTP or email service provider.
Supports async sending and queue.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


class EmailConfig:
    """Email configuration from environment."""
    SMTP_HOST: str = "smtp.gmail.com"  # or your SMTP server
    SMTP_PORT: int = 587
    SMTP_USER: str = ""  # Set from env
    SMTP_PASSWORD: str = ""  # Set from env
    FROM_EMAIL: str = "noreply@markettina.it"
    FROM_NAME: str = "MARKETTINA"


class EmailService:
    """
    Email sending service.
    
    Supports:
    - HTML emails
    - Multiple recipients
    - Attachments
    - Template rendering
    """

    def __init__(self, config: EmailConfig = None):
        self.config = config or EmailConfig()

    def send_email(
        self,
        to: list[str],
        subject: str,
        html_content: str,
        text_content: str | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
    ) -> bool:
        """
        Send email.
        
        Args:
            to: List of recipient emails
            subject: Email subject
            html_content: HTML body
            text_content: Plain text fallback (optional)
            cc: CC recipients
            bcc: BCC recipients
            
        Returns:
            True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{self.config.FROM_NAME} <{self.config.FROM_EMAIL}>"
            msg["To"] = ", ".join(to)
            msg["Subject"] = subject

            if cc:
                msg["Cc"] = ", ".join(cc)

            # Add text part (fallback)
            if text_content:
                part1 = MIMEText(text_content, "plain", "utf-8")
                msg.attach(part1)

            # Add HTML part
            part2 = MIMEText(html_content, "html", "utf-8")
            msg.attach(part2)

            # All recipients
            all_recipients = to + (cc or []) + (bcc or [])

            # Send email
            with smtplib.SMTP(self.config.SMTP_HOST, self.config.SMTP_PORT) as server:
                server.starttls()

                if self.config.SMTP_USER and self.config.SMTP_PASSWORD:
                    server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)

                server.sendmail(
                    self.config.FROM_EMAIL,
                    all_recipients,
                    msg.as_string()
                )

            logger.info(f"Email sent successfully to {', '.join(to)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    async def send_email_async(
        self,
        to: list[str],
        subject: str,
        html_content: str,
        text_content: str | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
    ) -> bool:
        """
        Send email asynchronously.
        
        Uses asyncio to not block the main thread.
        """
        import asyncio
        return await asyncio.to_thread(
            self.send_email,
            to,
            subject,
            html_content,
            text_content,
            cc,
            bcc
        )


# Singleton instance
email_service = EmailService()


# Helper functions using templates

async def send_welcome_email(to_email: str, name: str):
    """Send welcome email."""
    from .templates import welcome_email

    html = welcome_email(name)
    return await email_service.send_email_async(
        to=[to_email],
        subject="Benvenuto in MARKETTINA!",
        html_content=html
    )


async def send_booking_confirmation(
    to_email: str,
    name: str,
    service_type: str,
    preferred_date: str,
    budget_range: str,
    booking_id: int
):
    """Send booking confirmation email."""
    from .templates import booking_confirmation_email

    html = booking_confirmation_email(
        name, service_type, preferred_date, budget_range, booking_id
    )
    return await email_service.send_email_async(
        to=[to_email],
        subject=f"Prenotazione #{booking_id} Confermata",
        html_content=html
    )


async def send_contact_confirmation(to_email: str, name: str, subject: str):
    """Send contact form confirmation."""
    from .templates import contact_confirmation_email

    html = contact_confirmation_email(name, subject)
    return await email_service.send_email_async(
        to=[to_email],
        subject="Messaggio Ricevuto - MARKETTINA",
        html_content=html
    )


async def send_password_reset(to_email: str, name: str, reset_token: str):
    """Send password reset email."""
    from .templates import password_reset_email

    html = password_reset_email(
        name,
        reset_token,
        "https://markettina.it/admin/reset-password"
    )
    return await email_service.send_email_async(
        to=[to_email],
        subject="Reset Password - MARKETTINA",
        html_content=html
    )
