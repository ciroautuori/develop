"""
EmailService - Servizio Email Avanzato ISS
Gestione completa invio email, template, newsletter e notifiche
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from pathlib import Path
import jinja2
import asyncio
from datetime import datetime, timedelta
import logging

from app.core.config import settings
from app.models.user import User
from app.models.newspost import NewsNewsletter
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class EmailService:
    """Servizio completo per gestione email ISS"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAILS_FROM_EMAIL
        self.from_name = settings.EMAILS_FROM_NAME
        
        # Setup template engine
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Invia email singola
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Aggiungi contenuto testuale
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Aggiungi contenuto HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Aggiungi allegati
            if attachments:
                for file_path in attachments:
                    self._add_attachment(msg, file_path)
            
            # Lista destinatari
            recipients = [to]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            # Invia email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, recipients, msg.as_string())
            
            logger.info(f"Email inviata con successo a {to}")
            return True
            
        except Exception as e:
            logger.error(f"Errore invio email a {to}: {str(e)}")
            return False
    
    def send_template_email(
        self,
        to: str,
        template_name: str,
        context: Dict[str, Any],
        subject: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Invia email usando template Jinja2
        """
        try:
            # Carica template HTML
            html_template = self.jinja_env.get_template(f"{template_name}.html")
            html_content = html_template.render(**context)
            
            # Carica template testo (opzionale)
            text_content = None
            try:
                text_template = self.jinja_env.get_template(f"{template_name}.txt")
                text_content = text_template.render(**context)
            except jinja2.TemplateNotFound:
                pass
            
            # Subject dal template o parametro
            if not subject:
                try:
                    subject_template = self.jinja_env.get_template(f"{template_name}_subject.txt")
                    subject = subject_template.render(**context).strip()
                except jinja2.TemplateNotFound:
                    subject = f"Notifica da {self.from_name}"
            
            return self.send_email(
                to=to,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                attachments=attachments
            )
            
        except Exception as e:
            logger.error(f"Errore invio template email {template_name} a {to}: {str(e)}")
            return False
    
    def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        batch_size: int = 50,
        delay_seconds: int = 1
    ) -> Dict[str, int]:
        """
        Invia email in massa con batching
        """
        results = {"success": 0, "failed": 0}
        
        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]
            
            for email in batch:
                if self.send_email(email, subject, html_content, text_content):
                    results["success"] += 1
                else:
                    results["failed"] += 1
            
            # Pausa tra batch per evitare rate limiting
            if i + batch_size < len(recipients):
                asyncio.sleep(delay_seconds)
        
        logger.info(f"Bulk email completato: {results['success']} successi, {results['failed']} fallimenti")
        return results
    
    def send_newsletter(
        self,
        newsletter_id: int,
        db: Session,
        test_mode: bool = False,
        test_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invia newsletter programmata
        """
        try:
            # Recupera newsletter
            newsletter = db.query(NewsNewsletter).filter(
                NewsNewsletter.id == newsletter_id
            ).first()
            
            if not newsletter:
                raise ValueError(f"Newsletter {newsletter_id} non trovata")
            
            # In modalità test, invia solo all'email di test
            if test_mode and test_email:
                recipients = [test_email]
            else:
                # Recupera tutti gli utenti iscritti alla newsletter
                recipients = db.query(User.email).filter(
                    User.newsletter_abilitata == True,
                    User.is_active == True
                ).all()
                recipients = [r[0] for r in recipients]
            
            # Invia newsletter
            results = self.send_bulk_email(
                recipients=recipients,
                subject=newsletter.titolo,
                html_content=newsletter.template_html,
                text_content=newsletter.template_text
            )
            
            # Aggiorna statistiche newsletter
            if not test_mode:
                newsletter.data_invio_effettiva = datetime.now()
                newsletter.destinatari_totali = len(recipients)
                newsletter.invii_riusciti = results["success"]
                newsletter.invii_falliti = results["failed"]
                newsletter.stato = "inviata" if results["failed"] == 0 else "parzialmente_fallita"
                db.commit()
            
            return {
                "newsletter_id": newsletter_id,
                "test_mode": test_mode,
                "destinatari": len(recipients),
                "successi": results["success"],
                "fallimenti": results["failed"]
            }
            
        except Exception as e:
            logger.error(f"Errore invio newsletter {newsletter_id}: {str(e)}")
            if not test_mode:
                newsletter.stato = "fallita"
                db.commit()
            raise
    
    def send_welcome_email(self, user: User) -> bool:
        """
        Email di benvenuto per nuovi utenti
        """
        context = {
            "user_name": user.nome,
            "user_email": user.email,
            "login_url": f"{settings.FRONTEND_URL}/auth/login",
            "dashboard_url": f"{settings.FRONTEND_URL}/dashboard",
            "support_email": settings.EMAILS_FROM_EMAIL
        }
        
        return self.send_template_email(
            to=user.email,
            template_name="welcome",
            context=context,
            subject=f"Benvenuto in {settings.PROJECT_NAME}!"
        )
    
    def send_password_reset_email(self, user: User, reset_token: str) -> bool:
        """
        Email per reset password
        """
        reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}"
        
        context = {
            "user_name": user.nome,
            "reset_url": reset_url,
            "expiry_hours": 24,
            "support_email": settings.EMAILS_FROM_EMAIL
        }
        
        return self.send_template_email(
            to=user.email,
            template_name="password_reset",
            context=context,
            subject="Reset della password"
        )
    
    def send_email_verification(self, user: User, verification_token: str) -> bool:
        """
        Email per verifica indirizzo email
        """
        verification_url = f"{settings.FRONTEND_URL}/auth/verify-email?token={verification_token}"
        
        context = {
            "user_name": user.nome,
            "verification_url": verification_url,
            "support_email": settings.EMAILS_FROM_EMAIL
        }
        
        return self.send_template_email(
            to=user.email,
            template_name="email_verification",
            context=context,
            subject="Verifica il tuo indirizzo email"
        )
    
    def send_course_enrollment_confirmation(self, user: User, course_title: str, course_date: datetime) -> bool:
        """
        Conferma iscrizione corso
        """
        context = {
            "user_name": user.nome,
            "course_title": course_title,
            "course_date": course_date.strftime("%d/%m/%Y alle %H:%M"),
            "dashboard_url": f"{settings.FRONTEND_URL}/dashboard/corsi"
        }
        
        return self.send_template_email(
            to=user.email,
            template_name="course_enrollment",
            context=context,
            subject=f"Iscrizione confermata: {course_title}"
        )
    
    def send_event_reminder(self, user: User, event_title: str, event_date: datetime, hours_before: int = 24) -> bool:
        """
        Promemoria evento
        """
        context = {
            "user_name": user.nome,
            "event_title": event_title,
            "event_date": event_date.strftime("%d/%m/%Y alle %H:%M"),
            "hours_before": hours_before,
            "dashboard_url": f"{settings.FRONTEND_URL}/dashboard/eventi"
        }
        
        return self.send_template_email(
            to=user.email,
            template_name="event_reminder",
            context=context,
            subject=f"Promemoria: {event_title}"
        )
    
    def send_volunteer_application_notification(
        self, 
        manager_email: str, 
        manager_name: str,
        applicant_name: str,
        opportunity_title: str,
        application_url: str
    ) -> bool:
        """
        Notifica nuova candidatura volontariato
        """
        context = {
            "manager_name": manager_name,
            "applicant_name": applicant_name,
            "opportunity_title": opportunity_title,
            "application_url": application_url,
            "dashboard_url": f"{settings.FRONTEND_URL}/dashboard/volontariato"
        }
        
        return self.send_template_email(
            to=manager_email,
            template_name="volunteer_application",
            context=context,
            subject=f"Nuova candidatura: {opportunity_title}"
        )
    
    def send_project_update_notification(
        self,
        team_emails: List[str],
        project_name: str,
        update_title: str,
        update_content: str,
        project_url: str
    ) -> Dict[str, int]:
        """
        Notifica aggiornamento progetto al team
        """
        context = {
            "project_name": project_name,
            "update_title": update_title,
            "update_content": update_content,
            "project_url": project_url
        }
        
        # Genera HTML per ogni email
        html_template = self.jinja_env.get_template("project_update.html")
        html_content = html_template.render(**context)
        
        return self.send_bulk_email(
            recipients=team_emails,
            subject=f"Aggiornamento progetto: {project_name}",
            html_content=html_content
        )
    
    def send_testimonial_request(
        self,
        user_email: str,
        user_name: str,
        context_type: str,
        context_name: str,
        response_token: str
    ) -> bool:
        """
        Richiesta testimonial
        """
        response_url = f"{settings.FRONTEND_URL}/testimonials/create?token={response_token}"
        
        context = {
            "user_name": user_name,
            "context_type": context_type,
            "context_name": context_name,
            "response_url": response_url,
            "support_email": settings.EMAILS_FROM_EMAIL
        }
        
        return self.send_template_email(
            to=user_email,
            template_name="testimonial_request",
            context=context,
            subject=f"Condividi la tua esperienza con {context_name}"
        )
    
    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """
        Aggiunge allegato all'email
        """
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            
            filename = Path(file_path).name
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            msg.attach(part)
            
        except Exception as e:
            logger.error(f"Errore aggiunta allegato {file_path}: {str(e)}")
    
    def create_email_template(
        self,
        template_name: str,
        html_content: str,
        text_content: Optional[str] = None,
        subject_template: Optional[str] = None
    ) -> bool:
        """
        Crea nuovo template email
        """
        try:
            template_dir = Path(__file__).parent.parent / "templates" / "email"
            template_dir.mkdir(parents=True, exist_ok=True)
            
            # Salva template HTML
            html_file = template_dir / f"{template_name}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Salva template testo se fornito
            if text_content:
                text_file = template_dir / f"{template_name}.txt"
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(text_content)
            
            # Salva template subject se fornito
            if subject_template:
                subject_file = template_dir / f"{template_name}_subject.txt"
                with open(subject_file, 'w', encoding='utf-8') as f:
                    f.write(subject_template)
            
            logger.info(f"Template email {template_name} creato con successo")
            return True
            
        except Exception as e:
            logger.error(f"Errore creazione template {template_name}: {str(e)}")
            return False
    
    def get_email_stats(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """
        Statistiche invio email degli ultimi giorni
        """
        try:
            # In un'implementazione reale, queste statistiche verrebbero da una tabella di log
            # Per ora restituiamo dati di esempio
            
            return {
                "period_days": days,
                "total_sent": 1250,
                "total_delivered": 1180,
                "total_bounced": 45,
                "total_opened": 890,
                "total_clicked": 340,
                "delivery_rate": 94.4,
                "open_rate": 75.4,
                "click_rate": 38.2,
                "bounce_rate": 3.6,
                "top_templates": [
                    {"name": "welcome", "sent": 320, "open_rate": 82.1},
                    {"name": "course_enrollment", "sent": 280, "open_rate": 78.5},
                    {"name": "event_reminder", "sent": 190, "open_rate": 71.2}
                ]
            }
            
        except Exception as e:
            logger.error(f"Errore recupero statistiche email: {str(e)}")
            return {}


# Istanza globale del servizio
email_service = EmailService()
