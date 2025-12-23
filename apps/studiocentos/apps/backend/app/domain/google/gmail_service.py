"""
Gmail API Service
Send booking confirmations, reminders, and automated emails
"""
import logging
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.domain.auth.oauth_tokens import OAuthTokenService, OAuthProvider

logger = logging.getLogger(__name__)

# Gmail API Base URL
GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1"


class GmailService:
    """Service for Gmail API - Send automated emails."""

    def __init__(self, access_token: str):
        """
        Initialize Gmail service.

        Args:
            access_token: Valid Google OAuth access token with gmail.send scope
        """
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    @classmethod
    def from_admin_token(cls, db: Session, admin_id: int) -> Optional["GmailService"]:
        """Create service instance from admin's stored OAuth token."""
        token = OAuthTokenService.get_valid_token(db, admin_id, OAuthProvider.GOOGLE)
        if not token:
            logger.warning(f"No valid Google OAuth token for admin {admin_id}")
            return None
        return cls(access_token=token)

    def _create_message(
        self,
        to: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        from_name: str = "StudioCentOS",
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> str:
        """Create a base64 encoded email message."""
        message = MIMEMultipart("alternative")
        message["To"] = to
        message["Subject"] = subject

        if from_name:
            message["From"] = f"{from_name} <noreply@studiocentos.it>"

        if reply_to:
            message["Reply-To"] = reply_to

        if cc:
            message["Cc"] = ", ".join(cc)

        if bcc:
            message["Bcc"] = ", ".join(bcc)

        # Plain text version
        if body_text:
            part1 = MIMEText(body_text, "plain", "utf-8")
            message.attach(part1)

        # HTML version
        part2 = MIMEText(body_html, "html", "utf-8")
        message.attach(part2)

        # Encode to base64
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        return raw

    async def send_email(
        self,
        to: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send an email via Gmail API.

        Args:
            to: Recipient email
            subject: Email subject
            body_html: HTML body
            body_text: Plain text body (optional)
            reply_to: Reply-to address
            cc: CC recipients

        Returns:
            Sent message data or None if failed
        """
        raw = self._create_message(
            to=to,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            reply_to=reply_to,
            cc=cc
        )

        url = f"{GMAIL_API_BASE}/users/me/messages/send"
        body = {"raw": raw}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=body,
                    timeout=30.0
                )

                if response.status_code not in [200, 201]:
                    logger.error(f"Gmail API error: {response.status_code} - {response.text}")
                    return None

                data = response.json()
                logger.info(f"Email sent successfully: {data.get('id')}")
                return data

        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            return None


# =============================================================================
# Email Templates
# =============================================================================

def get_booking_confirmation_html(
    client_name: str,
    booking_title: str,
    booking_date: datetime,
    duration_minutes: int,
    meet_link: Optional[str] = None,
    calendar_link: Optional[str] = None
) -> str:
    """Generate HTML for booking confirmation email."""

    date_str = booking_date.strftime("%A %d %B %Y")
    time_str = booking_date.strftime("%H:%M")

    meet_section = ""
    if meet_link:
        meet_section = f"""
        <tr>
            <td style="padding: 20px; background: #e8f5e9; border-radius: 8px; text-align: center;">
                <p style="margin: 0 0 10px; font-size: 14px; color: #2e7d32;">
                    🎥 <strong>Link Videocall Google Meet</strong>
                </p>
                <a href="{meet_link}" style="display: inline-block; padding: 12px 24px; background: #1a73e8; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    Unisciti alla chiamata
                </a>
                <p style="margin: 10px 0 0; font-size: 12px; color: #666;">
                    {meet_link}
                </p>
            </td>
        </tr>
        """

    calendar_section = ""
    if calendar_link:
        calendar_section = f"""
        <p style="text-align: center; margin-top: 20px;">
            <a href="{calendar_link}" style="color: #1a73e8; text-decoration: none;">
                📅 Aggiungi al calendario
            </a>
        </p>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background: white;">
            <!-- Header -->
            <tr>
                <td style="padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); text-align: center;">
                    <h1 style="margin: 0; color: white; font-size: 28px;">StudioCentOS</h1>
                    <p style="margin: 10px 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">
                        Conferma Prenotazione
                    </p>
                </td>
            </tr>

            <!-- Content -->
            <tr>
                <td style="padding: 30px;">
                    <h2 style="margin: 0 0 20px; color: #333; font-size: 22px;">
                        Ciao {client_name}! 👋
                    </h2>

                    <p style="margin: 0 0 20px; color: #555; line-height: 1.6;">
                        La tua prenotazione è stata confermata! Ecco i dettagli:
                    </p>

                    <!-- Booking Details -->
                    <table width="100%" style="background: #f8f9fa; border-radius: 8px; margin-bottom: 20px;">
                        <tr>
                            <td style="padding: 20px;">
                                <p style="margin: 0 0 10px;">
                                    <strong style="color: #333;">📌 Appuntamento:</strong><br>
                                    <span style="color: #555;">{booking_title}</span>
                                </p>
                                <p style="margin: 0 0 10px;">
                                    <strong style="color: #333;">📅 Data:</strong><br>
                                    <span style="color: #555;">{date_str}</span>
                                </p>
                                <p style="margin: 0 0 10px;">
                                    <strong style="color: #333;">⏰ Orario:</strong><br>
                                    <span style="color: #555;">{time_str} ({duration_minutes} minuti)</span>
                                </p>
                            </td>
                        </tr>
                    </table>

                    <!-- Meet Link -->
                    {meet_section}

                    {calendar_section}
                </td>
            </tr>

            <!-- Footer -->
            <tr>
                <td style="padding: 20px 30px; background: #f8f9fa; text-align: center; border-top: 1px solid #eee;">
                    <p style="margin: 0 0 10px; color: #666; font-size: 14px;">
                        Hai domande? Rispondi a questa email o contattaci.
                    </p>
                    <p style="margin: 0; color: #999; font-size: 12px;">
                        © 2024 StudioCentOS - Milano, Italia
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def get_booking_reminder_html(
    client_name: str,
    booking_title: str,
    booking_date: datetime,
    meet_link: Optional[str] = None,
    hours_before: int = 24
) -> str:
    """Generate HTML for booking reminder email."""

    date_str = booking_date.strftime("%A %d %B %Y")
    time_str = booking_date.strftime("%H:%M")

    meet_button = ""
    if meet_link:
        meet_button = f"""
        <p style="text-align: center; margin-top: 20px;">
            <a href="{meet_link}" style="display: inline-block; padding: 14px 28px; background: #1a73e8; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">
                🎥 Unisciti alla chiamata
            </a>
        </p>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background: white;">
            <tr>
                <td style="padding: 30px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); text-align: center;">
                    <h1 style="margin: 0; color: white; font-size: 28px;">⏰ Promemoria</h1>
                </td>
            </tr>

            <tr>
                <td style="padding: 30px;">
                    <h2 style="margin: 0 0 20px; color: #333;">
                        Ciao {client_name}!
                    </h2>

                    <p style="color: #555; line-height: 1.6;">
                        Ti ricordiamo che il tuo appuntamento è tra <strong>{hours_before} ore</strong>!
                    </p>

                    <table width="100%" style="background: #fff3cd; border-radius: 8px; margin: 20px 0;">
                        <tr>
                            <td style="padding: 20px;">
                                <p style="margin: 0;">
                                    <strong>📌 {booking_title}</strong><br>
                                    📅 {date_str} alle {time_str}
                                </p>
                            </td>
                        </tr>
                    </table>

                    {meet_button}

                    <p style="color: #666; font-size: 14px; margin-top: 20px;">
                        Se non puoi partecipare, contattaci per riprogrammare.
                    </p>
                </td>
            </tr>

            <tr>
                <td style="padding: 20px 30px; background: #f8f9fa; text-align: center;">
                    <p style="margin: 0; color: #999; font-size: 12px;">
                        © 2024 StudioCentOS - Milano, Italia
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def get_quote_email_html(
    client_name: str,
    project_title: str,
    total_amount: float,
    valid_until: datetime,
    quote_link: str
) -> str:
    """Generate HTML for quote/preventivo email."""

    valid_str = valid_until.strftime("%d/%m/%Y")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background: white;">
            <tr>
                <td style="padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); text-align: center;">
                    <h1 style="margin: 0; color: white; font-size: 28px;">StudioCentOS</h1>
                    <p style="margin: 10px 0 0; color: rgba(255,255,255,0.9);">
                        📄 Il tuo preventivo è pronto!
                    </p>
                </td>
            </tr>

            <tr>
                <td style="padding: 30px;">
                    <h2 style="margin: 0 0 20px; color: #333;">
                        Ciao {client_name}!
                    </h2>

                    <p style="color: #555; line-height: 1.6;">
                        Grazie per averci contattato! Abbiamo preparato il preventivo per il progetto <strong>{project_title}</strong>.
                    </p>

                    <table width="100%" style="background: #e8f5e9; border-radius: 8px; margin: 20px 0;">
                        <tr>
                            <td style="padding: 20px; text-align: center;">
                                <p style="margin: 0 0 5px; color: #2e7d32; font-size: 14px;">
                                    Investimento totale
                                </p>
                                <p style="margin: 0; color: #1b5e20; font-size: 32px; font-weight: bold;">
                                    €{total_amount:,.2f}
                                </p>
                                <p style="margin: 10px 0 0; color: #666; font-size: 12px;">
                                    Validità: fino al {valid_str}
                                </p>
                            </td>
                        </tr>
                    </table>

                    <p style="text-align: center;">
                        <a href="{quote_link}" style="display: inline-block; padding: 14px 28px; background: #667eea; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            📥 Scarica il Preventivo PDF
                        </a>
                    </p>

                    <p style="color: #666; font-size: 14px; margin-top: 20px; text-align: center;">
                        Hai domande? Prenota una call con noi per discuterne!
                    </p>
                </td>
            </tr>

            <tr>
                <td style="padding: 20px 30px; background: #f8f9fa; text-align: center;">
                    <p style="margin: 0; color: #999; font-size: 12px;">
                        © 2024 StudioCentOS - Milano, Italia
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


# =============================================================================
# Booking Email Functions
# =============================================================================

async def send_booking_confirmation(
    db: Session,
    admin_id: int,
    client_email: str,
    client_name: str,
    booking_title: str,
    booking_date: datetime,
    duration_minutes: int,
    meet_link: Optional[str] = None,
    calendar_link: Optional[str] = None
) -> bool:
    """Send booking confirmation email."""
    service = GmailService.from_admin_token(db, admin_id)
    if not service:
        logger.error("Could not create Gmail service")
        return False

    html = get_booking_confirmation_html(
        client_name=client_name,
        booking_title=booking_title,
        booking_date=booking_date,
        duration_minutes=duration_minutes,
        meet_link=meet_link,
        calendar_link=calendar_link
    )

    result = await service.send_email(
        to=client_email,
        subject=f"✅ Prenotazione confermata: {booking_title}",
        body_html=html,
        reply_to="info@studiocentos.it"
    )

    return result is not None


async def send_booking_reminder(
    db: Session,
    admin_id: int,
    client_email: str,
    client_name: str,
    booking_title: str,
    booking_date: datetime,
    meet_link: Optional[str] = None,
    hours_before: int = 24
) -> bool:
    """Send booking reminder email."""
    service = GmailService.from_admin_token(db, admin_id)
    if not service:
        return False

    html = get_booking_reminder_html(
        client_name=client_name,
        booking_title=booking_title,
        booking_date=booking_date,
        meet_link=meet_link,
        hours_before=hours_before
    )

    result = await service.send_email(
        to=client_email,
        subject=f"⏰ Promemoria: {booking_title} tra {hours_before}h",
        body_html=html,
        reply_to="info@studiocentos.it"
    )

    return result is not None


async def send_quote_email(
    db: Session,
    admin_id: int,
    client_email: str,
    client_name: str,
    project_title: str,
    total_amount: float,
    valid_until: datetime,
    quote_pdf_link: str
) -> bool:
    """Send quote/preventivo email with PDF link."""
    service = GmailService.from_admin_token(db, admin_id)
    if not service:
        return False

    html = get_quote_email_html(
        client_name=client_name,
        project_title=project_title,
        total_amount=total_amount,
        valid_until=valid_until,
        quote_link=quote_pdf_link
    )

    result = await service.send_email(
        to=client_email,
        subject=f"📄 Preventivo StudioCentOS: {project_title}",
        body_html=html,
        reply_to="info@studiocentos.it"
    )

    return result is not None
