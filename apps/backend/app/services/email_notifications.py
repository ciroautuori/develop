"""
Servizio di notifiche email per bandi e alerts ISS
Sistema completo di email automation per APS/ODV
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import asyncio
from jinja2 import Template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.bando import Bando
from app.models.aps_user import APSUser, BandoWatchlist
from app.crud.aps_user import aps_user_crud
from app.crud.bando import bando_crud

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Servizio completo per notifiche email agli utenti APS"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'MAIL_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'MAIL_PORT', 587)
        self.smtp_username = getattr(settings, 'MAIL_USERNAME', '')
        self.smtp_password = getattr(settings, 'MAIL_PASSWORD', '')
        self.from_email = getattr(settings, 'MAIL_FROM', 'noreply@innovazionesocialesalernitana.it')
        self.enabled = bool(self.smtp_username and self.smtp_password)
        
        if not self.enabled:
            logger.warning("📧 Email service not configured - notifications disabled")
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Invia email utilizzando SMTP"""
        if not self.enabled:
            logger.info(f"📧 Email service disabled - would send to {to_email}: {subject}")
            return False
        
        try:
            # Crea messaggio
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = to_email
            
            # Aggiungi contenuto
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)
            
            part2 = MIMEText(html_content, "html")
            message.attach(part2)
            
            # Invia email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, to_email, message.as_string())
            
            logger.info(f"✅ Email inviata con successo a {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore invio email a {to_email}: {e}")
            return False
    
    async def send_new_bandi_alert(self, user: APSUser, bandi: List[Bando]) -> bool:
        """Invia alert per nuovi bandi compatibili con il profilo utente"""
        if not bandi:
            return False
        
        subject = f"🎯 {len(bandi)} nuovi bandi per {user.organization_name}"
        
        # Template HTML
        html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .header { background: #1e40af; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .bando { border: 1px solid #e5e7eb; margin: 15px 0; padding: 15px; border-radius: 8px; }
                .bando-title { color: #1e40af; font-weight: bold; margin-bottom: 8px; }
                .bando-info { color: #6b7280; font-size: 14px; margin: 5px 0; }
                .cta-button { background: #1e40af; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0; }
                .footer { background: #f9fafb; padding: 15px; text-align: center; color: #6b7280; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏛️ ISS - Innovazione Sociale Salernitana</h1>
                <h2>Nuovi Bandi per {{ organization_name }}</h2>
            </div>
            
            <div class="content">
                <p>Ciao <strong>{{ organization_name }}</strong>,</p>
                <p>Abbiamo trovato <strong>{{ bandi_count }} nuovi bandi</strong> che potrebbero interessarti:</p>
                
                {% for bando in bandi %}
                <div class="bando">
                    <div class="bando-title">{{ bando.title }}</div>
                    <div class="bando-info">🏛️ <strong>Ente:</strong> {{ bando.ente }}</div>
                    {% if bando.importo %}
                    <div class="bando-info">💰 <strong>Importo:</strong> {{ bando.importo }}</div>
                    {% endif %}
                    {% if bando.scadenza %}
                    <div class="bando-info">📅 <strong>Scadenza:</strong> {{ bando.scadenza.strftime('%d/%m/%Y') }}</div>
                    {% endif %}
                    {% if bando.descrizione %}
                    <div class="bando-info">📝 {{ bando.descrizione[:200] }}{% if bando.descrizione|length > 200 %}...{% endif %}</div>
                    {% endif %}
                </div>
                {% endfor %}
                
                <a href="https://innovazionesocialesalernitana.it/bandi" class="cta-button">
                    🔍 Visualizza Tutti i Bandi
                </a>
                
                <p>Il nostro sistema AI ha selezionato questi bandi basandosi sul tuo profilo organizzativo. 
                   Accedi alla piattaforma per vedere le raccomandazioni personalizzate!</p>
            </div>
            
            <div class="footer">
                <p>Questa email è stata inviata automaticamente dal sistema ISS</p>
                <p>ISS - Innovazione Sociale Salernitana | Primo Hub Bandi AI-Powered d'Italia</p>
                <p><a href="https://innovazionesocialesalernitana.it">innovazionesocialesalernitana.it</a></p>
            </div>
        </body>
        </html>
        """)
        
        html_content = html_template.render(
            organization_name=user.organization_name,
            bandi_count=len(bandi),
            bandi=bandi
        )
        
        return await self.send_email(user.contact_email, subject, html_content)
    
    async def send_deadline_reminder(self, user: APSUser, bando: Bando, days_left: int) -> bool:
        """Invia reminder per scadenza bando imminente"""
        if days_left <= 0:
            return False
        
        urgency = "🚨 URGENTE" if days_left <= 3 else "⚠️ IMPORTANTE" if days_left <= 7 else "📅 REMINDER"
        subject = f"{urgency}: {bando.title} scade in {days_left} giorni"
        
        html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .header { background: {% if days_left <= 3 %}#dc2626{% elif days_left <= 7 %}#ea580c{% else %}#1e40af{% endif %}; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .deadline-box { background: {% if days_left <= 3 %}#fee2e2{% elif days_left <= 7 %}#fed7aa{% else %}#dbeafe{% endif %}; border: 2px solid {% if days_left <= 3 %}#dc2626{% elif days_left <= 7 %}#ea580c{% else %}#1e40af{% endif %}; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }
                .days-left { font-size: 2em; font-weight: bold; color: {% if days_left <= 3 %}#dc2626{% elif days_left <= 7 %}#ea580c{% else %}#1e40af{% endif %}; }
                .bando-details { background: #f9fafb; padding: 15px; border-radius: 8px; margin: 15px 0; }
                .cta-button { background: {% if days_left <= 3 %}#dc2626{% elif days_left <= 7 %}#ea580c{% else %}#1e40af{% endif %}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0; }
                .footer { background: #f9fafb; padding: 15px; text-align: center; color: #6b7280; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⏰ Scadenza Bando Imminente</h1>
                <h2>{{ organization_name }}</h2>
            </div>
            
            <div class="content">
                <div class="deadline-box">
                    <div class="days-left">{{ days_left }}</div>
                    <div>giorni rimasti per candidarti</div>
                </div>
                
                <div class="bando-details">
                    <h3>{{ bando.title }}</h3>
                    <p><strong>🏛️ Ente:</strong> {{ bando.ente }}</p>
                    {% if bando.importo %}
                    <p><strong>💰 Importo:</strong> {{ bando.importo }}</p>
                    {% endif %}
                    <p><strong>📅 Scadenza:</strong> {{ bando.scadenza.strftime('%d/%m/%Y alle %H:%M') if bando.scadenza else 'Da definire' }}</p>
                    {% if bando.descrizione %}
                    <p><strong>📝 Descrizione:</strong> {{ bando.descrizione[:300] }}{% if bando.descrizione|length > 300 %}...{% endif %}</p>
                    {% endif %}
                </div>
                
                <a href="{{ bando.link }}" class="cta-button">
                    🔗 Vai al Bando Originale
                </a>
                
                <p>{% if days_left <= 3 %}
                    <strong>⚠️ ATTENZIONE:</strong> Restano solo {{ days_left }} giorni! Non perdere questa opportunità.
                {% elif days_left <= 7 %}
                    <strong>📋 PROMEMORIA:</strong> Il tempo stringe, organizza la documentazione necessaria.
                {% else %}
                    <strong>📅 PIANIFICA:</strong> Hai ancora {{ days_left }} giorni per preparare la candidatura.
                {% endif %}</p>
                
                <p>Questo bando è nella tua watchlist perché compatibile con il profilo di <strong>{{ organization_name }}</strong>.</p>
            </div>
            
            <div class="footer">
                <p>Reminder automatico dal sistema ISS</p>
                <p>ISS - Innovazione Sociale Salernitana</p>
            </div>
        </body>
        </html>
        """)
        
        html_content = html_template.render(
            organization_name=user.organization_name,
            days_left=days_left,
            bando=bando
        )
        
        return await self.send_email(user.contact_email, subject, html_content)
    
    async def send_weekly_newsletter(self, user: APSUser, stats: Dict[str, Any]) -> bool:
        """Invia newsletter settimanale con statistiche e nuovi bandi"""
        subject = f"📊 Newsletter ISS: {stats.get('nuovi_bandi', 0)} nuovi bandi questa settimana"
        
        html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .header { background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 30px; text-align: center; }
                .content { padding: 20px; }
                .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
                .stat-card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; text-align: center; }
                .stat-value { font-size: 2em; font-weight: bold; color: #1e40af; }
                .stat-label { color: #64748b; font-size: 14px; }
                .section { margin: 30px 0; }
                .bando-list { background: #f9fafb; padding: 15px; border-radius: 8px; }
                .cta-button { background: #1e40af; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0; }
                .footer { background: #1f2937; color: white; padding: 20px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 ISS Weekly Newsletter</h1>
                <p>La tua dose settimanale di opportunità per {{ organization_name }}</p>
            </div>
            
            <div class="content">
                <div class="section">
                    <h2>📈 Statistiche della Settimana</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value">{{ stats.nuovi_bandi }}</div>
                            <div class="stat-label">Nuovi Bandi</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{{ stats.totali_attivi }}</div>
                            <div class="stat-label">Bandi Attivi</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">€{{ stats.importo_totale | default('N/A') }}</div>
                            <div class="stat-label">Importo Disponibile</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{{ stats.raccomandazioni_ai | default(0) }}</div>
                            <div class="stat-label">Raccomandazioni AI</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🎯 I Tuoi Bandi Raccomandati</h2>
                    {% if stats.bandi_raccomandati %}
                    <div class="bando-list">
                        {% for bando in stats.bandi_raccomandati %}
                        <div style="margin: 10px 0; padding: 10px; border-left: 4px solid #1e40af;">
                            <strong>{{ bando.title }}</strong><br>
                            <small>{{ bando.ente }} • {{ bando.importo if bando.importo else 'Importo non specificato' }}</small>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <p>🤖 Il nostro AI sta analizzando i nuovi bandi per generare raccomandazioni personalizzate.</p>
                    {% endif %}
                </div>
                
                <div class="section">
                    <h2>📅 Scadenze Imminenti</h2>
                    {% if stats.scadenze_imminenti %}
                    <div class="bando-list">
                        {% for scadenza in stats.scadenze_imminenti %}
                        <div style="margin: 10px 0; padding: 10px; border-left: 4px solid #dc2626;">
                            <strong>{{ scadenza.bando.title }}</strong><br>
                            <small>⏰ {{ scadenza.days_left }} giorni rimasti</small>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <p>✅ Nessuna scadenza imminente nella tua watchlist.</p>
                    {% endif %}
                </div>
                
                <div class="section">
                    <h2>💡 Suggerimento della Settimana</h2>
                    <div style="background: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 8px;">
                        <p><strong>🚀 Ottimizza il tuo profilo:</strong> Aggiungi più parole chiave specifiche al tuo profilo per ricevere raccomandazioni AI più precise!</p>
                    </div>
                </div>
                
                <a href="https://innovazionesocialesalernitana.it/dashboard" class="cta-button">
                    🏠 Vai alla Dashboard
                </a>
            </div>
            
            <div class="footer">
                <h3>🏛️ ISS - Innovazione Sociale Salernitana</h3>
                <p>Il primo Hub Bandi AI-powered per il terzo settore</p>
                <p><a href="https://innovazionesocialesalernitana.it" style="color: #60a5fa;">innovazionesocialesalernitana.it</a></p>
                <p style="font-size: 12px; margin-top: 10px;">
                    Per disattivare queste email, <a href="#" style="color: #60a5fa;">clicca qui</a>
                </p>
            </div>
        </body>
        </html>
        """)
        
        html_content = html_template.render(
            organization_name=user.organization_name,
            stats=stats
        )
        
        return await self.send_email(user.contact_email, subject, html_content)
    
    async def send_bulk_notifications(self, db: AsyncSession, notification_type: str, **kwargs) -> Dict[str, int]:
        """Invia notifiche bulk a tutti gli utenti attivi"""
        results = {"sent": 0, "failed": 0, "skipped": 0}
        
        # Recupera tutti gli utenti attivi
        users, _ = await aps_user_crud.search_users(db, skip=0, limit=1000, is_active=True)
        
        for user in users:
            try:
                # Controlla preferenze notifiche
                preferences = user.notification_preferences or {}
                if not preferences.get('email_enabled', True):
                    results["skipped"] += 1
                    continue
                
                success = False
                if notification_type == "new_bandi" and "bandi" in kwargs:
                    success = await self.send_new_bandi_alert(user, kwargs["bandi"])
                elif notification_type == "deadline" and "bando" in kwargs and "days_left" in kwargs:
                    success = await self.send_deadline_reminder(user, kwargs["bando"], kwargs["days_left"])
                elif notification_type == "newsletter" and "stats" in kwargs:
                    success = await self.send_weekly_newsletter(user, kwargs["stats"])
                
                if success:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
                    
                # Pausa tra invii per evitare spam
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Errore invio notifica a {user.contact_email}: {e}")
                results["failed"] += 1
        
        logger.info(f"📧 Bulk notification '{notification_type}': {results}")
        return results


# Singleton service instance
email_notification_service = EmailNotificationService()
