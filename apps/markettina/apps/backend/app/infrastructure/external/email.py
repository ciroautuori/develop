import logging
import os
import smtplib
from datetime import UTC
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

class EmailService:
    """Service per invio email."""

    @staticmethod
    def get_smtp_config():
        """Ottiene configurazione SMTP da environment variables."""
        return {
            "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("SMTP_USERNAME", ""),
            "password": os.getenv("SMTP_PASSWORD", ""),
            "from_email": os.getenv("SMTP_FROM_EMAIL", "noreply@portfolio-saas.com"),
            "from_name": os.getenv("SMTP_FROM_NAME", "Portfolio SaaS"),
            "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
        }

    @staticmethod
    def send_email(
        to_email: str, subject: str, html_content: str, text_content: str | None = None
    ) -> bool:
        """Invia email generica.

        Args:
            to_email: Destinatario
            subject: Oggetto
            html_content: Contenuto HTML
            text_content: Contenuto testo (optional)

        Returns:
            True se successo
        """
        config = EmailService.get_smtp_config()

        if not config["username"] or not config["password"]:
            logger.warning(f"SMTP not configured. Would send email to {to_email}: {subject}")
            return False

        try:
            # Crea messaggio
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{config['from_name']} <{config['from_email']}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            # Aggiungi contenuto
            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            # Invia email
            with smtplib.SMTP(config["host"], config["port"]) as server:
                if config["use_tls"]:
                    server.starttls()
                server.login(config["username"], config["password"])
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e!s}")
            return False

    @staticmethod
    def send_tester_invitation(email: str, temp_password: str) -> bool:
        """Invia email invito tester con password temporanea.

        Args:
            email: Email destinatario
            temp_password: Password temporanea generata

        Returns:
            True se successo
        """
        from app.core.config import settings

        frontend_url = settings.FRONTEND_URL

        subject = "🚀 Invito Tester - Portfolio SaaS Platform"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .credentials {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #667eea; }}
                .warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Benvenuto nel Team Tester!</h1>
                    <p>Sei stato invitato a testare Portfolio SaaS Platform</p>
                </div>

                <div class="content">
                    <h2>Ciao Tester! 👋</h2>

                    <p>Sei stato selezionato per testare la nostra piattaforma con accesso completo alle funzionalità PRO.</p>

                    <div class="credentials">
                        <h3>🔐 Le tue credenziali temporanee:</h3>
                        <p><strong>Email:</strong> <code>{email}</code></p>
                        <p><strong>Password temporanea:</strong> <code>{temp_password}</code></p>
                    </div>

                    <div class="warning">
                        <strong>⚠️ Importante:</strong> Al primo accesso dovrai cambiare la password temporanea con una personale.
                    </div>

                    <h3>📋 Prossimi passi:</h3>
                    <ol>
                        <li>Clicca sul pulsante qui sotto per accedere</li>
                        <li>Effettua il login con le credenziali fornite</li>
                        <li>Verrai reindirizzato per impostare una nuova password</li>
                        <li>Inizia a testare tutte le funzionalità PRO!</li>
                    </ol>

                    <div style="text-align: center;">
                        <a href="{frontend_url}/login" class="button">Accedi alla Piattaforma</a>
                    </div>

                    <h3>✨ Cosa puoi fare come Tester:</h3>
                    <ul>
                        <li>✅ Creare fino a 5 portfolio</li>
                        <li>✅ Generare CV in formato PDF</li>
                        <li>✅ Accedere a tutte le funzionalità PRO</li>
                        <li>✅ Testare l'intero workflow della piattaforma</li>
                    </ul>

                    <p><strong>Nota:</strong> Questo invito scade tra 7 giorni. Se hai bisogno di un nuovo invito, contatta l'amministratore.</p>
                </div>

                <div class="footer">
                    <p>Portfolio SaaS Platform © 2025</p>
                    <p>Questa è un'email automatica, non rispondere a questo messaggio.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Benvenuto nel Team Tester!

        Sei stato invitato a testare Portfolio SaaS Platform.

        Le tue credenziali temporanee:
        Email: {email}
        Password temporanea: {temp_password}

        IMPORTANTE: Al primo accesso dovrai cambiare la password.

        Accedi qui: {frontend_url}/login

        Cosa puoi fare come Tester:
        - Creare fino a 5 portfolio
        - Generare CV in formato PDF
        - Accedere a tutte le funzionalità PRO
        - Testare l'intero workflow

        Questo invito scade tra 7 giorni.

        Portfolio SaaS Platform © 2025
        """

        return EmailService.send_email(
            to_email=email, subject=subject, html_content=html_content, text_content=text_content
        )

    @staticmethod
    def send_password_changed_confirmation(email: str) -> bool:
        """Invia conferma cambio password.

        Args:
            email: Email destinatario

        Returns:
            True se successo
        """
        subject = "✅ Password modificata con successo"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #28a745; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .success {{ background: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Password Modificata</h1>
                </div>

                <div class="content">
                    <div class="success">
                        <strong>La tua password è stata modificata con successo!</strong>
                    </div>

                    <p>Ciao {email},</p>

                    <p>Confermiamo che la password del tuo account tester è stata modificata con successo.</p>

                    <p>Ora puoi accedere alla piattaforma con la tua nuova password e iniziare a testare tutte le funzionalità.</p>

                    <p>Buon testing! 🚀</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(to_email=email, subject=subject, html_content=html_content)

    @staticmethod
    def send_api_key_rotation_notification(
        email: str, key_name: str, new_key_prefix: str, rotation_reason: str = "scheduled"
    ) -> bool:
        """Invia notifica di rotazione API key.

        Args:
            email: Email destinatario
            key_name: Nome della API key ruotata
            new_key_prefix: Prefisso della nuova key
            rotation_reason: Motivo rotazione (scheduled, manual, security)

        Returns:
            True se successo
        """
        from app.core.config import settings

        frontend_url = settings.FRONTEND_URL

        reason_text = {
            "scheduled": "rotazione automatica programmata",
            "manual": "richiesta manuale",
            "security": "misura di sicurezza precauzionale"
        }.get(rotation_reason, "rotazione programmata")

        subject = f"🔐 API Key Rotated: {key_name}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .info {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #667eea; }}
                .warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 API Key Rotated</h1>
                    <p>La tua API key è stata ruotata con successo</p>
                </div>

                <div class="content">
                    <h2>Ciao! 👋</h2>

                    <p>Ti informiamo che l'API key <strong>{key_name}</strong> è stata ruotata per motivi di {reason_text}.</p>

                    <div class="info">
                        <h3>📋 Dettagli:</h3>
                        <p><strong>Key Name:</strong> <code>{key_name}</code></p>
                        <p><strong>New Key Prefix:</strong> <code>{new_key_prefix}...</code></p>
                        <p><strong>Rotation Reason:</strong> {reason_text}</p>
                        <p><strong>Rotation Time:</strong> {EmailService._get_current_time()}</p>
                    </div>

                    <div class="warning">
                        <strong>⚠️ Azione Richiesta:</strong>
                        <ul>
                            <li>La vecchia API key continuerà a funzionare per 7 giorni (grace period)</li>
                            <li>Aggiorna le tue applicazioni con la nuova key entro questo periodo</li>
                            <li>Dopo il grace period, la vecchia key sarà disattivata automaticamente</li>
                        </ul>
                    </div>

                    <h3>📋 Prossimi passi:</h3>
                    <ol>
                        <li>Accedi al dashboard per recuperare la nuova API key completa</li>
                        <li>Aggiorna le configurazioni delle tue applicazioni</li>
                        <li>Testa che tutto funzioni correttamente</li>
                        <li>Opzionale: Puoi revocare manualmente la vecchia key dopo l'aggiornamento</li>
                    </ol>

                    <div style="text-align: center;">
                        <a href="{frontend_url}/dashboard/api-keys" class="button">Gestisci API Keys</a>
                    </div>

                    <p><strong>Sicurezza:</strong> Se non hai richiesto questa rotazione, contatta immediatamente il supporto.</p>
                </div>

                <div class="footer">
                    <p>CV-Lab Platform © 2025</p>
                    <p>Questa è un'email automatica, non rispondere a questo messaggio.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        API Key Rotated: {key_name}

        La tua API key è stata ruotata per motivi di {reason_text}.

        Dettagli:
        - Key Name: {key_name}
        - New Key Prefix: {new_key_prefix}...
        - Rotation Time: {EmailService._get_current_time()}

        AZIONE RICHIESTA:
        - La vecchia key funzionerà per altri 7 giorni
        - Aggiorna le tue applicazioni con la nuova key
        - Dopo il grace period, la vecchia key sarà disattivata

        Prossimi passi:
        1. Accedi al dashboard per recuperare la nuova key completa
        2. Aggiorna le configurazioni delle tue applicazioni
        3. Testa che tutto funzioni correttamente

        Dashboard: {frontend_url}/dashboard/api-keys

        Se non hai richiesto questa rotazione, contatta il supporto.

        CV-Lab Platform © 2025
        """

        return EmailService.send_email(
            to_email=email, subject=subject, html_content=html_content, text_content=text_content
        )

    @staticmethod
    def _get_current_time() -> str:
        """Get current time formatted for emails."""
        from datetime import datetime
        return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
