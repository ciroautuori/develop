"""
Email Service - Unified email sending with templates
"""

import logging
import os
from typing import Any

import aiohttp
from jinja2 import Template

logger = logging.getLogger(__name__)


class EmailService:
    """Email service using SendGrid or SMTP"""

    def __init__(self):
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@markettina.it")
        self.from_name = os.getenv("FROM_NAME", "markettina")

        # SMTP fallback
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
    ) -> bool:
        """Send email via SendGrid or SMTP"""

        if self.sendgrid_api_key:
            return await self._send_via_sendgrid(
                to_email, subject, html_content, text_content, cc, bcc
            )
        if self.smtp_host:
            return await self._send_via_smtp(
                to_email, subject, html_content, text_content
            )
        logger.debug(f"[DEV MODE] Email to {to_email}: {subject}")
        return True

    async def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None,
        cc: list[str] | None,
        bcc: list[str] | None,
    ) -> bool:
        """Send email via SendGrid API"""

        payload = {
            "personalizations": [{
                "to": [{"email": to_email}],
                "subject": subject,
            }],
            "from": {
                "email": self.from_email,
                "name": self.from_name,
            },
            "content": [
                {"type": "text/html", "value": html_content},
            ],
        }

        if text_content:
            payload["content"].insert(0, {"type": "text/plain", "value": text_content})

        if cc:
            payload["personalizations"][0]["cc"] = [{"email": e} for e in cc]
        if bcc:
            payload["personalizations"][0]["bcc"] = [{"email": e} for e in bcc]

        async with aiohttp.ClientSession() as session, session.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {self.sendgrid_api_key}",
                "Content-Type": "application/json",
            },
            json=payload
        ) as response:
            return response.status == 202

    async def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None,
    ) -> bool:
        """Send email via SMTP"""
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email

        if text_content:
            msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False

    # ========================================================================
    # TEMPLATE METHODS
    # ========================================================================

    async def send_booking_confirmation(
        self,
        to_email: str,
        booking_data: dict[str, Any]
    ) -> bool:
        """Send booking confirmation email"""

        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #4F46E5; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9fafb; }
                .details { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4F46E5; }
                .button { display: inline-block; padding: 12px 24px; background: #4F46E5; color: white; text-decoration: none; border-radius: 6px; margin: 15px 0; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Prenotazione Confermata!</h1>
                </div>
                <div class="content">
                    <p>Ciao <strong>{{ client_name }}</strong>,</p>
                    <p>La tua prenotazione è stata confermata con successo.</p>

                    <div class="details">
                        <h3>📅 Dettagli Appuntamento</h3>
                        <p><strong>Data:</strong> {{ scheduled_date }}</p>
                        <p><strong>Ora:</strong> {{ scheduled_time }}</p>
                        <p><strong>Durata:</strong> {{ duration }} minuti</p>
                        <p><strong>Servizio:</strong> {{ service_type }}</p>
                        {% if meeting_url %}
                        <p><strong>Link Meeting:</strong> <a href="{{ meeting_url }}">{{ meeting_url }}</a></p>
                        {% endif %}
                    </div>

                    <p>Riceverai un promemoria 24 ore prima dell'appuntamento.</p>

                    <p>Se hai bisogno di modificare o cancellare la prenotazione, contattaci a <a href="mailto:info@markettina.it">info@markettina.it</a></p>
                </div>
                <div class="footer">
                    <p>© 2025 markettina - Full Stack Development & AI Solutions</p>
                    <p>Via Example 123, 00100 Roma | <a href="https://markettina.it">markettina.it</a></p>
                </div>
            </div>
        </body>
        </html>
        """)

        html_content = template.render(**booking_data)

        return await self.send_email(
            to_email=to_email,
            subject=f"✅ Prenotazione Confermata - {booking_data.get('scheduled_date')}",
            html_content=html_content
        )

    async def send_booking_reminder(
        self,
        to_email: str,
        booking_data: dict[str, Any]
    ) -> bool:
        """Send booking reminder email (24h before)"""

        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #F59E0B; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9fafb; }
                .details { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #F59E0B; }
                .button { display: inline-block; padding: 12px 24px; background: #F59E0B; color: white; text-decoration: none; border-radius: 6px; margin: 15px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⏰ Promemoria Appuntamento</h1>
                </div>
                <div class="content">
                    <p>Ciao <strong>{{ client_name }}</strong>,</p>
                    <p>Ti ricordiamo che hai un appuntamento domani:</p>

                    <div class="details">
                        <h3>📅 Dettagli</h3>
                        <p><strong>Data:</strong> {{ scheduled_date }}</p>
                        <p><strong>Ora:</strong> {{ scheduled_time }}</p>
                        <p><strong>Durata:</strong> {{ duration }} minuti</p>
                        {% if meeting_url %}
                        <p><a href="{{ meeting_url }}" class="button">🎥 Accedi al Meeting</a></p>
                        {% endif %}
                    </div>

                    <p>Ci vediamo domani!</p>
                </div>
            </div>
        </body>
        </html>
        """)

        html_content = template.render(**booking_data)

        return await self.send_email(
            to_email=to_email,
            subject=f"⏰ Promemoria: Appuntamento domani alle {booking_data.get('scheduled_time')}",
            html_content=html_content
        )

    async def send_contact_confirmation(
        self,
        to_email: str,
        contact_data: dict[str, Any]
    ) -> bool:
        """Send contact form confirmation"""

        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #10B981; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9fafb; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✉️ Messaggio Ricevuto</h1>
                </div>
                <div class="content">
                    <p>Ciao <strong>{{ name }}</strong>,</p>
                    <p>Abbiamo ricevuto il tuo messaggio e ti risponderemo entro 24 ore.</p>
                    <p>Grazie per averci contattato!</p>
                    <p><strong>Il team markettina</strong></p>
                </div>
            </div>
        </body>
        </html>
        """)

        html_content = template.render(**contact_data)

        return await self.send_email(
            to_email=to_email,
            subject="✉️ Messaggio ricevuto - markettina",
            html_content=html_content
        )

    async def send_admin_password_setup(
        self,
        to_email: str,
        setup_token: str
    ) -> bool:
        """Send admin password setup email"""

        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #DC2626; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9fafb; }
                .token { background: #FEF3C7; padding: 15px; margin: 15px 0; border-left: 4px solid #F59E0B; font-family: monospace; font-size: 14px; word-break: break-all; }
                .warning { background: #FEE2E2; padding: 15px; margin: 15px 0; border-left: 4px solid #DC2626; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Setup Password Amministratore</h1>
                </div>
                <div class="content">
                    <p>Benvenuto nel pannello amministrativo di markettina.</p>
                    <p>Per completare il setup del tuo account amministratore, usa il seguente token:</p>

                    <div class="token">
                        <strong>Setup Token:</strong><br>
                        {{ setup_token }}
                    </div>

                    <div class="warning">
                        <strong>⚠️ IMPORTANTE:</strong>
                        <ul>
                            <li>Questo token è valido per 24 ore</li>
                            <li>Usa una password forte (min 12 caratteri, maiuscole, numeri, simboli)</li>
                            <li>Non condividere questo token con nessuno</li>
                            <li>Abilita 2FA dopo il setup per maggiore sicurezza</li>
                        </ul>
                    </div>

                    <p>Accedi al pannello admin: <a href="https://markettina.it/admin/setup">https://markettina.it/admin/setup</a></p>
                </div>
            </div>
        </body>
        </html>
        """)

        html_content = template.render(setup_token=setup_token)

        return await self.send_email(
            to_email=to_email,
            subject="🔐 Setup Password Amministratore - markettina",
            html_content=html_content
        )

    async def send_admin_2fa_enabled(
        self,
        to_email: str,
        backup_codes: list[str]
    ) -> bool:
        """Send 2FA enabled confirmation with backup codes"""

        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #10B981; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9fafb; }
                .codes { background: #FEF3C7; padding: 15px; margin: 15px 0; border-left: 4px solid #F59E0B; }
                .code { font-family: monospace; font-size: 14px; padding: 5px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ 2FA Abilitato</h1>
                </div>
                <div class="content">
                    <p>La verifica a due fattori (2FA) è stata abilitata con successo sul tuo account amministratore.</p>

                    <div class="codes">
                        <strong>🔑 Codici di Backup (conservali in un luogo sicuro):</strong><br><br>
                        {% for code in backup_codes %}
                        <div class="code">{{ code }}</div>
                        {% endfor %}
                    </div>

                    <p><strong>⚠️ IMPORTANTE:</strong> Conserva questi codici in un luogo sicuro. Potrai usarli per accedere se perdi l'accesso all'app authenticator.</p>
                </div>
            </div>
        </body>
        </html>
        """)

        html_content = template.render(backup_codes=backup_codes)

        return await self.send_email(
            to_email=to_email,
            subject="✅ 2FA Abilitato - markettina Admin",
            html_content=html_content
        )

    async def send_admin_login_alert(
        self,
        to_email: str,
        login_data: dict[str, Any]
    ) -> bool:
        """Send admin login alert"""

        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #3B82F6; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9fafb; }
                .details { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #3B82F6; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 Nuovo Accesso Admin</h1>
                </div>
                <div class="content">
                    <p>È stato rilevato un nuovo accesso al pannello amministrativo:</p>

                    <div class="details">
                        <p><strong>Data/Ora:</strong> {{ timestamp }}</p>
                        <p><strong>IP:</strong> {{ ip_address }}</p>
                        <p><strong>User Agent:</strong> {{ user_agent }}</p>
                        <p><strong>Località:</strong> {{ location }}</p>
                    </div>

                    <p>Se non sei stato tu, cambia immediatamente la password e contatta il supporto.</p>
                </div>
            </div>
        </body>
        </html>
        """)

        html_content = template.render(**login_data)

        return await self.send_email(
            to_email=to_email,
            subject="🔔 Nuovo Accesso Admin - markettina",
            html_content=html_content
        )


# Singleton instance
email_service = EmailService()
