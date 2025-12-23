"""
Finance Notifications Service - Sistema notifiche finanziarie MARKETTINA
Gestisce alert automatici, email notifications, push notifications
"""

import logging
import smtplib
from datetime import date, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from .models import CompanyExpense, FinanceAlert, MonthlyBudget, ROITracking
from .schemas import AlertResponse

logger = logging.getLogger(__name__)


class FinanceNotificationsService:
    """Service per gestione notifiche finanziarie"""

    # ========================================================================
    # ALERT CREATION & MANAGEMENT
    # ========================================================================

    @staticmethod
    def create_expense_due_alert(db: Session, expense: CompanyExpense) -> FinanceAlert | None:
        """Crea alert per spesa in scadenza"""

        days_until_due = (expense.due_date - date.today()).days

        # Solo per spese pending
        if expense.status != "pending":
            return None

        # Verifica se alert già esiste
        existing = db.query(FinanceAlert).filter(
            and_(
                FinanceAlert.expense_id == expense.id,
                FinanceAlert.alert_type == "expense_due",
                FinanceAlert.status == "active"
            )
        ).first()

        if existing:
            return existing

        # Determina severità
        if days_until_due < 0:
            severity = "critical"
            title = f"⚠️ SPESA SCADUTA: {expense.title}"
            message = f"La spesa '{expense.title}' di €{expense.amount} è scaduta da {abs(days_until_due)} giorni!"
        elif days_until_due <= 1:
            severity = "high"
            title = f"🔥 SCADENZA IMMINENTE: {expense.title}"
            message = f"La spesa '{expense.title}' di €{expense.amount} scade {'oggi' if days_until_due == 0 else 'domani'}!"
        elif days_until_due <= 7:
            severity = "medium"
            title = f"⏰ Scadenza tra {days_until_due} giorni: {expense.title}"
            message = f"La spesa '{expense.title}' di €{expense.amount} scade il {expense.due_date.strftime('%d/%m/%Y')}"
        else:
            return None  # Non creare alert per scadenze troppo lontane

        alert = FinanceAlert(
            alert_type="expense_due",
            expense_id=expense.id,
            title=title,
            message=message,
            severity=severity,
            trigger_date=datetime.utcnow(),
            due_date=datetime.combine(expense.due_date, datetime.min.time())
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        return alert

    @staticmethod
    def create_budget_exceeded_alert(db: Session, budget: MonthlyBudget) -> FinanceAlert | None:
        """Crea alert per budget superato"""

        if budget.actual_amount <= budget.planned_amount:
            return None

        # Verifica se alert già esiste
        existing = db.query(FinanceAlert).filter(
            and_(
                FinanceAlert.budget_id == budget.id,
                FinanceAlert.alert_type == "budget_exceeded",
                FinanceAlert.status == "active"
            )
        ).first()

        if existing:
            return existing

        variance_pct = ((budget.actual_amount / budget.planned_amount - 1) * 100)

        # Determina severità
        if variance_pct > 50:
            severity = "critical"
        elif variance_pct > 25:
            severity = "high"
        elif variance_pct > 10:
            severity = "medium"
        else:
            severity = "low"

        alert = FinanceAlert(
            alert_type="budget_exceeded",
            budget_id=budget.id,
            title=f"📊 Budget Superato: {budget.category}",
            message=f"Budget {budget.category} {budget.month}/{budget.year} superato del {variance_pct:.1f}% (€{budget.actual_amount - budget.planned_amount:,.2f})",
            severity=severity,
            trigger_date=datetime.utcnow()
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        return alert

    @staticmethod
    def create_roi_milestone_alert(db: Session, roi: ROITracking) -> FinanceAlert | None:
        """Crea alert per milestone ROI raggiunto"""

        if roi.status != "active" or roi.actual_return <= 0:
            return None

        roi_percentage = roi.roi_calculated

        # Milestone predefiniti
        milestones = [10, 25, 50, 100, 200, 500]  # % ROI

        for milestone in milestones:
            if roi_percentage >= milestone:
                # Verifica se alert per questo milestone già esiste
                existing = db.query(FinanceAlert).filter(
                    and_(
                        FinanceAlert.roi_id == roi.id,
                        FinanceAlert.alert_type == "roi_milestone",
                        FinanceAlert.message.contains(f"{milestone}%"),
                        FinanceAlert.status == "active"
                    )
                ).first()

                if not existing:
                    alert = FinanceAlert(
                        alert_type="roi_milestone",
                        roi_id=roi.id,
                        title=f"🎯 ROI Milestone: {roi.investment_name}",
                        message=f"Investimento '{roi.investment_name}' ha raggiunto {roi_percentage:.1f}% ROI (milestone {milestone}%)",
                        severity="medium",
                        trigger_date=datetime.utcnow()
                    )

                    db.add(alert)
                    db.commit()
                    db.refresh(alert)

                    return alert

        return None

    @staticmethod
    def create_cashflow_warning_alert(db: Session, projected_negative_days: int) -> FinanceAlert | None:
        """Crea alert per cashflow negativo previsto"""

        if projected_negative_days <= 0:
            return None

        # Verifica se alert cashflow già esiste per questo periodo
        existing = db.query(FinanceAlert).filter(
            and_(
                FinanceAlert.alert_type == "cashflow_warning",
                FinanceAlert.status == "active",
                FinanceAlert.trigger_date >= datetime.utcnow() - timedelta(days=7)
            )
        ).first()

        if existing:
            return existing

        severity = "critical" if projected_negative_days <= 30 else "high"

        alert = FinanceAlert(
            alert_type="cashflow_warning",
            title="💸 Alert Cashflow",
            message=f"Cashflow negativo previsto tra {projected_negative_days} giorni. Verificare liquidità aziendale.",
            severity=severity,
            trigger_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=projected_negative_days)
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        return alert

    # ========================================================================
    # ALERT MANAGEMENT
    # ========================================================================

    @staticmethod
    def get_active_alerts(
        db: Session,
        severity: str | None = None,
        alert_type: str | None = None,
        limit: int = 50
    ) -> list[AlertResponse]:
        """Ottieni alert attivi"""

        query = db.query(FinanceAlert).filter(
            FinanceAlert.status == "active"
        )

        if severity:
            query = query.filter(FinanceAlert.severity == severity)

        if alert_type:
            query = query.filter(FinanceAlert.alert_type == alert_type)

        alerts = query.order_by(
            desc(FinanceAlert.severity),
            desc(FinanceAlert.trigger_date)
        ).limit(limit).all()

        return [AlertResponse.model_validate(alert) for alert in alerts]

    @staticmethod
    def dismiss_alert(db: Session, alert_id: int, resolved_by: int) -> bool:
        """Dismissi alert"""

        alert = db.query(FinanceAlert).filter(FinanceAlert.id == alert_id).first()

        if not alert:
            return False

        alert.status = "dismissed"
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = resolved_by

        db.commit()
        return True

    @staticmethod
    def snooze_alert(db: Session, alert_id: int, hours: int) -> bool:
        """Posticipa alert per X ore"""

        alert = db.query(FinanceAlert).filter(FinanceAlert.id == alert_id).first()

        if not alert:
            return False

        alert.status = "snoozed"
        alert.snoozed_until = datetime.utcnow() + timedelta(hours=hours)
        alert.snooze_count = (alert.snooze_count or 0) + 1

        db.commit()
        return True

    @staticmethod
    def resolve_alert(db: Session, alert_id: int, resolved_by: int, notes: str = None) -> bool:
        """Risolvi alert"""

        alert = db.query(FinanceAlert).filter(FinanceAlert.id == alert_id).first()

        if not alert:
            return False

        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = resolved_by
        alert.resolution_notes = notes

        db.commit()
        return True

    # ========================================================================
    # AUTOMATIC ALERT GENERATION
    # ========================================================================

    @staticmethod
    async def run_daily_alert_check(db: Session):
        """Job giornaliero per controllo e creazione alert"""

        logger.info("🔔 Starting daily alert check...")

        alerts_created = 0

        # 1. Controllo spese in scadenza
        upcoming_expenses = db.query(CompanyExpense).filter(
            and_(
                CompanyExpense.status == "pending",
                CompanyExpense.due_date >= date.today(),
                CompanyExpense.due_date <= date.today() + timedelta(days=30)
            )
        ).all()

        for expense in upcoming_expenses:
            alert = FinanceNotificationsService.create_expense_due_alert(db, expense)
            if alert:
                alerts_created += 1

        # 2. Controllo spese scadute
        overdue_expenses = db.query(CompanyExpense).filter(
            and_(
                CompanyExpense.status == "pending",
                CompanyExpense.due_date < date.today()
            )
        ).all()

        for expense in overdue_expenses:
            alert = FinanceNotificationsService.create_expense_due_alert(db, expense)
            if alert:
                alerts_created += 1

        # 3. Controllo budget superati
        current_month = date.today().month
        current_year = date.today().year

        budgets = db.query(MonthlyBudget).filter(
            and_(
                MonthlyBudget.year == current_year,
                MonthlyBudget.month == current_month
            )
        ).all()

        for budget in budgets:
            # Aggiorna actual_amount
            FinanceNotificationsService._update_budget_actual(db, budget)

            alert = FinanceNotificationsService.create_budget_exceeded_alert(db, budget)
            if alert:
                alerts_created += 1

        # 4. Controllo ROI milestones
        active_rois = db.query(ROITracking).filter(
            ROITracking.status == "active"
        ).all()

        for roi in active_rois:
            alert = FinanceNotificationsService.create_roi_milestone_alert(db, roi)
            if alert:
                alerts_created += 1

        # 5. Riattiva alert snoozed scaduti
        snoozed_alerts = db.query(FinanceAlert).filter(
            and_(
                FinanceAlert.status == "snoozed",
                FinanceAlert.snoozed_until <= datetime.utcnow()
            )
        ).all()

        for alert in snoozed_alerts:
            alert.status = "active"
            alert.snoozed_until = None

        db.commit()

        logger.info(f"✅ Daily alert check completed. Created {alerts_created} new alerts, reactivated {len(snoozed_alerts)} snoozed alerts")

        return {
            "alerts_created": alerts_created,
            "alerts_reactivated": len(snoozed_alerts),
            "timestamp": datetime.utcnow().isoformat()
        }

    # ========================================================================
    # EMAIL NOTIFICATIONS
    # ========================================================================

    @staticmethod
    async def send_alert_email(
        db: Session,
        alert: FinanceAlert,
        recipient_email: str,
        smtp_config: dict[str, Any]
    ):
        """Invia email per alert"""

        try:
            # Crea messaggio email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[MARKETTINA Finance] {alert.title}"
            msg["From"] = smtp_config["from_email"]
            msg["To"] = recipient_email

            # Email body HTML
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">MARKETTINA Finance Alert</h1>
                  </div>
                  
                  <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; border: 1px solid #dee2e6;">
                    <div style="background: {'#dc3545' if alert.severity == 'critical' else '#fd7e14' if alert.severity == 'high' else '#ffc107' if alert.severity == 'medium' else '#28a745'}; color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                      <strong>Priorità: {alert.severity.upper()}</strong>
                    </div>
                    
                    <h2 style="color: #495057; margin-top: 0;">{alert.title}</h2>
                    <p style="font-size: 16px; margin-bottom: 20px;">{alert.message}</p>
                    
                    <div style="background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff;">
                      <p><strong>Data trigger:</strong> {alert.trigger_date.strftime('%d/%m/%Y %H:%M')}</p>
                      {f'<p><strong>Scadenza:</strong> {alert.due_date.strftime("%d/%m/%Y %H:%M")}</p>' if alert.due_date else ''}
                      <p><strong>Tipo alert:</strong> {alert.alert_type.replace('_', ' ').title()}</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                      <a href="https://markettina.it/admin/finance" 
                         style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Visualizza Dashboard Finance
                      </a>
                    </div>
                  </div>
                  
                  <div style="text-align: center; margin-top: 20px; color: #6c757d; font-size: 14px;">
                    <p>Questo è un messaggio automatico del sistema MARKETTINA Finance</p>
                    <p>Per domande contatta: <a href="mailto:ciro@markettina.it">ciro@markettina.it</a></p>
                  </div>
                </div>
              </body>
            </html>
            """

            msg.attach(MIMEText(html_body, "html"))

            # Invia email
            with smtplib.SMTP(smtp_config["smtp_server"], smtp_config["smtp_port"]) as server:
                server.starttls()
                server.login(smtp_config["username"], smtp_config["password"])
                server.send_message(msg)

            # Aggiorna alert
            alert.email_sent = True
            alert.email_sent_at = datetime.utcnow()
            db.commit()

            logger.info(f"📧 Email sent for alert {alert.id} to {recipient_email}")

        except Exception as e:
            logger.error(f"❌ Failed to send email for alert {alert.id}: {e!s}")
            raise

    @staticmethod
    async def send_daily_finance_summary(
        db: Session,
        recipient_email: str,
        smtp_config: dict[str, Any]
    ):
        """Invia riepilogo giornaliero via email"""

        try:
            today = date.today()

            # Statistiche giornaliere
            active_alerts = db.query(FinanceAlert).filter(
                FinanceAlert.status == "active"
            ).count()

            overdue_expenses = db.query(CompanyExpense).filter(
                and_(
                    CompanyExpense.status == "pending",
                    CompanyExpense.due_date < today
                )
            ).count()

            due_today = db.query(CompanyExpense).filter(
                and_(
                    CompanyExpense.status == "pending",
                    CompanyExpense.due_date == today
                )
            ).all()

            due_this_week = db.query(CompanyExpense).filter(
                and_(
                    CompanyExpense.status == "pending",
                    CompanyExpense.due_date >= today,
                    CompanyExpense.due_date <= today + timedelta(days=7)
                )
            ).count()

            # Crea email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[MARKETTINA] Riepilogo Finance - {today.strftime('%d/%m/%Y')}"
            msg["From"] = smtp_config["from_email"]
            msg["To"] = recipient_email

            # Email body
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <h1 style="color: #2c3e50; text-align: center;">Riepilogo Finance Giornaliero</h1>
                  <p style="text-align: center; color: #7f8c8d; font-size: 18px;">{today.strftime('%d %B %Y')}</p>
                  
                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 30px 0;">
                    <div style="background: #e74c3c; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                      <h3 style="margin: 0; font-size: 32px;">{active_alerts}</h3>
                      <p style="margin: 5px 0 0 0;">Alert Attivi</p>
                    </div>
                    
                    <div style="background: #f39c12; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                      <h3 style="margin: 0; font-size: 32px;">{overdue_expenses}</h3>
                      <p style="margin: 5px 0 0 0;">Spese Scadute</p>
                    </div>
                    
                    <div style="background: #e67e22; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                      <h3 style="margin: 0; font-size: 32px;">{len(due_today)}</h3>
                      <p style="margin: 5px 0 0 0;">Scadenze Oggi</p>
                    </div>
                    
                    <div style="background: #3498db; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                      <h3 style="margin: 0; font-size: 32px;">{due_this_week}</h3>
                      <p style="margin: 5px 0 0 0;">Scadenze 7gg</p>
                    </div>
                  </div>
                  
                  {f'''
                  <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 10px; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #856404; margin-top: 0;">⚠️ Scadenze di Oggi:</h3>
                    <ul style="color: #856404;">
                      {"".join([f"<li><strong>{exp.title}</strong> - €{exp.amount:,.2f} ({exp.supplier_name or 'N/A'})</li>" for exp in due_today])}
                    </ul>
                  </div>
                  ''' if due_today else ''}
                  
                  <div style="text-align: center; margin-top: 40px;">
                    <a href="https://markettina.it/admin/finance" 
                       style="background: #2c3e50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: bold; font-size: 16px;">
                      🔗 Vai al Dashboard Finance
                    </a>
                  </div>
                  
                  <div style="text-align: center; margin-top: 30px; color: #95a5a6; font-size: 14px;">
                    <p>Riepilogo automatico MARKETTINA Finance System</p>
                  </div>
                </div>
              </body>
            </html>
            """

            msg.attach(MIMEText(html_body, "html"))

            # Invia email
            with smtplib.SMTP(smtp_config["smtp_server"], smtp_config["smtp_port"]) as server:
                server.starttls()
                server.login(smtp_config["username"], smtp_config["password"])
                server.send_message(msg)

            logger.info(f"📧 Daily finance summary sent to {recipient_email}")

            return {
                "sent": True,
                "recipient": recipient_email,
                "stats": {
                    "active_alerts": active_alerts,
                    "overdue_expenses": overdue_expenses,
                    "due_today": len(due_today),
                    "due_this_week": due_this_week
                }
            }

        except Exception as e:
            logger.error(f"❌ Failed to send daily summary: {e!s}")
            raise

    # ========================================================================
    # PUSH NOTIFICATIONS
    # ========================================================================

    @staticmethod
    async def send_push_notification(
        alert: FinanceAlert,
        user_tokens: list[str],
        fcm_server_key: str
    ):
        """Invia push notification"""

        try:
            import requests

            # FCM endpoint
            fcm_url = "https://fcm.googleapis.com/fcm/send"

            headers = {
                "Authorization": f"key={fcm_server_key}",
                "Content-Type": "application/json"
            }

            # Determina icona e colore per tipo alert
            icon_map = {
                "expense_due": "💰",
                "budget_exceeded": "📊",
                "roi_milestone": "🎯",
                "cashflow_warning": "💸"
            }

            color_map = {
                "critical": "#dc3545",
                "high": "#fd7e14",
                "medium": "#ffc107",
                "low": "#28a745"
            }

            # Payload notifica
            notification_data = {
                "registration_ids": user_tokens,
                "notification": {
                    "title": f"{icon_map.get(alert.alert_type, '🔔')} {alert.title}",
                    "body": alert.message[:100] + ("..." if len(alert.message) > 100 else ""),
                    "icon": "/icons/finance-icon-192x192.png",
                    "badge": "/icons/finance-badge.png",
                    "color": color_map.get(alert.severity, "#007bff"),
                    "click_action": "https://markettina.it/admin/finance"
                },
                "data": {
                    "alert_id": str(alert.id),
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "timestamp": alert.trigger_date.isoformat(),
                    "action_url": "/admin/finance"
                }
            }

            # Invia richiesta FCM
            response = requests.post(fcm_url, json=notification_data, headers=headers)
            response.raise_for_status()

            result = response.json()

            if result.get("success", 0) > 0:
                # Aggiorna alert
                # Nota: db session dovrebbe essere passata come parametro

                logger.info(f"📱 Push notification sent for alert {alert.id} to {len(user_tokens)} devices")

                return {
                    "sent": True,
                    "success_count": result.get("success", 0),
                    "failure_count": result.get("failure", 0),
                    "results": result.get("results", [])
                }
            logger.warning(f"⚠️ Push notification failed for alert {alert.id}")
            return {"sent": False, "error": "No successful deliveries"}

        except Exception as e:
            logger.error(f"❌ Failed to send push notification for alert {alert.id}: {e!s}")
            raise

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    @staticmethod
    def _update_budget_actual(db: Session, budget: MonthlyBudget):
        """Aggiorna actual_amount del budget"""

        start_date = date(budget.year, budget.month, 1)
        if budget.month == 12:
            end_date = date(budget.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(budget.year, budget.month + 1, 1) - timedelta(days=1)

        from sqlalchemy import func
        actual_amount = db.query(func.sum(CompanyExpense.amount)).filter(
            and_(
                CompanyExpense.category == budget.category,
                CompanyExpense.due_date >= start_date,
                CompanyExpense.due_date <= end_date,
                CompanyExpense.status.in_(["paid", "pending"])
            )
        ).scalar() or 0

        budget.actual_amount = actual_amount
        budget.variance_amount = actual_amount - budget.planned_amount

        if budget.planned_amount > 0:
            budget.variance_percentage = (
                (actual_amount / budget.planned_amount - 1) * 100
            )

        db.commit()

    @staticmethod
    def get_notification_preferences(user_id: int) -> dict[str, Any]:
        """Ottieni preferenze notifiche utente"""

        # Placeholder - implementare con tabella user_notification_preferences
        return {
            "email_enabled": True,
            "push_enabled": True,
            "sms_enabled": False,
            "email_frequency": "immediate",  # immediate, daily, weekly
            "alert_types": ["expense_due", "budget_exceeded", "roi_milestone"],
            "severity_threshold": "medium"  # low, medium, high, critical
        }
