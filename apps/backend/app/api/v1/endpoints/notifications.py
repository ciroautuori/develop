"""
Endpoint API per sistema notifiche e alert
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.database.database import get_db
from app.services.email_notifications import email_notification_service
from app.services.alert_system import alert_system
from app.crud.aps_user import aps_user_crud
from app.crud.bando import bando_crud

router = APIRouter()


# ========== SCHEMAS ==========

class NotificationPreferences(BaseModel):
    """Preferenze notifiche utente"""
    email_enabled: bool = True
    new_bandi_alerts: bool = True
    deadline_reminders: bool = True
    weekly_newsletter: bool = True
    ai_recommendations: bool = True
    emergency_alerts: bool = True


class TestEmailRequest(BaseModel):
    """Richiesta test email"""
    to_email: EmailStr
    email_type: str = "test"  # test, new_bandi, deadline, newsletter


class BulkNotificationRequest(BaseModel):
    """Richiesta notifica bulk"""
    notification_type: str  # new_bandi, deadline, newsletter
    target_users: Optional[List[int]] = None  # Se None, invia a tutti
    test_mode: bool = False


class NotificationStats(BaseModel):
    """Statistiche notifiche"""
    total_users: int
    active_users: int
    emails_sent_today: int
    emails_sent_week: int
    newsletter_subscribers: int
    alert_subscribers: int


# ========== ENDPOINTS ==========

@router.get("/preferences/{user_id}", response_model=NotificationPreferences)
async def get_notification_preferences(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    🔔 Ottieni preferenze notifiche utente
    """
    user = await aps_user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    preferences = user.notification_preferences or {}
    return NotificationPreferences(**preferences)


@router.put("/preferences/{user_id}", response_model=NotificationPreferences)
async def update_notification_preferences(
    user_id: int,
    preferences: NotificationPreferences,
    db: AsyncSession = Depends(get_db)
):
    """
    ⚙️ Aggiorna preferenze notifiche utente
    """
    user = await aps_user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    # Aggiorna preferenze
    update_data = {"notification_preferences": preferences.dict()}
    await aps_user_crud.update(db, db_obj=user, obj_in=update_data)
    
    return preferences


@router.post("/test-email")
async def send_test_email(
    request: TestEmailRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    📧 Invia email di test per verificare configurazione
    """
    async def send_test():
        try:
            if request.email_type == "test":
                await email_notification_service.send_email(
                    to_email=request.to_email,
                    subject="🧪 Test Email - ISS Platform",
                    html_content="""
                    <h2>🧪 Email di Test ISS</h2>
                    <p>Questa è una email di test dal sistema ISS.</p>
                    <p>Se ricevi questa email, la configurazione funziona correttamente! ✅</p>
                    <p><strong>ISS - Innovazione Sociale Salernitana</strong></p>
                    """
                )
            elif request.email_type == "new_bandi":
                # Test con bandi fittizi
                bandi, _ = await bando_crud.get_bandi(db, limit=2)
                if bandi:
                    fake_user = type('User', (), {
                        'organization_name': 'Organizzazione Test',
                        'contact_email': request.to_email
                    })()
                    await email_notification_service.send_new_bandi_alert(fake_user, bandi)
            elif request.email_type == "newsletter":
                fake_user = type('User', (), {
                    'organization_name': 'Organizzazione Test',
                    'contact_email': request.to_email
                })()
                fake_stats = {
                    'nuovi_bandi': 5,
                    'totali_attivi': 23,
                    'importo_totale': '2,500,000',
                    'raccomandazioni_ai': 3,
                    'bandi_raccomandati': [],
                    'scadenze_imminenti': []
                }
                await email_notification_service.send_weekly_newsletter(fake_user, fake_stats)
                
        except Exception as e:
            print(f"Errore invio test email: {e}")
    
    background_tasks.add_task(send_test)
    return {"message": f"Test email {request.email_type} inviata a {request.to_email}"}


@router.post("/send-bulk")
async def send_bulk_notification(
    request: BulkNotificationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    📨 Invia notifiche bulk agli utenti
    """
    if request.test_mode:
        return {"message": "Modalità test - nessuna email inviata"}
    
    async def send_bulk():
        try:
            if request.notification_type == "new_bandi":
                results = await alert_system.check_new_bandi_alerts(db)
            elif request.notification_type == "deadline":
                results = await alert_system.check_deadline_reminders(db)
            elif request.notification_type == "newsletter":
                results = await alert_system.send_weekly_newsletters(db)
            else:
                results = {"error": "Tipo notifica non supportato"}
            
            print(f"Bulk notification results: {results}")
        except Exception as e:
            print(f"Errore bulk notification: {e}")
    
    background_tasks.add_task(send_bulk)
    return {"message": f"Notifica bulk '{request.notification_type}' avviata in background"}


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(db: AsyncSession = Depends(get_db)):
    """
    📊 Statistiche sistema notifiche
    """
    try:
        # Conta utenti
        all_users, total_users = await aps_user_crud.search_users(db, skip=0, limit=10000)
        active_users, _ = await aps_user_crud.search_users(db, skip=0, limit=10000, is_active=True)
        
        # Conta sottoscrittori newsletter e alert
        newsletter_subscribers = 0
        alert_subscribers = 0
        
        for user in active_users:
            preferences = user.notification_preferences or {}
            if preferences.get('weekly_newsletter', True):
                newsletter_subscribers += 1
            if preferences.get('new_bandi_alerts', True):
                alert_subscribers += 1
        
        return NotificationStats(
            total_users=total_users,
            active_users=len(active_users),
            emails_sent_today=0,  # TODO: Implementare tracking
            emails_sent_week=0,   # TODO: Implementare tracking
            newsletter_subscribers=newsletter_subscribers,
            alert_subscribers=alert_subscribers
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore calcolo statistiche: {e}")


@router.post("/trigger-alerts")
async def trigger_manual_alerts(
    background_tasks: BackgroundTasks,
    alert_type: str = "all",  # all, new_bandi, deadlines, newsletter
    db: AsyncSession = Depends(get_db)
):
    """
    ⚡ Trigger manuale per alert (solo admin)
    """
    async def run_alerts():
        try:
            results = {}
            
            if alert_type in ["all", "new_bandi"]:
                results["new_bandi"] = await alert_system.check_new_bandi_alerts(db)
            
            if alert_type in ["all", "deadlines"]:
                results["deadlines"] = await alert_system.check_deadline_reminders(db)
            
            if alert_type in ["all", "newsletter"]:
                results["newsletter"] = await alert_system.send_weekly_newsletters(db)
            
            print(f"Manual alerts triggered: {results}")
            
        except Exception as e:
            print(f"Errore trigger alerts: {e}")
    
    background_tasks.add_task(run_alerts)
    return {"message": f"Alert manuali '{alert_type}' avviati in background"}


@router.get("/preview/{user_id}")
async def preview_user_notifications(
    user_id: int,
    notification_type: str = "newsletter",  # newsletter, new_bandi, deadline
    db: AsyncSession = Depends(get_db)
):
    """
    👁️ Anteprima notifiche per un utente specifico
    """
    user = await aps_user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    if notification_type == "newsletter":
        # Preview newsletter
        stats = await alert_system._calculate_weekly_stats(db)
        user_stats = await alert_system._personalize_stats_for_user(db, user, stats)
        
        return {
            "user": {
                "organization_name": user.organization_name,
                "email": user.contact_email
            },
            "preview_data": user_stats,
            "notification_type": "newsletter"
        }
    
    elif notification_type == "new_bandi":
        # Preview nuovi bandi
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        bandi, _ = await bando_crud.get_bandi(db, limit=10)
        new_bandi = [b for b in bandi if b.data_trovato >= cutoff_time]
        
        relevant_bandi = await alert_system._find_relevant_bandi_for_user(db, user, new_bandi)
        
        return {
            "user": {
                "organization_name": user.organization_name,
                "email": user.contact_email
            },
            "preview_data": {
                "new_bandi_count": len(new_bandi),
                "relevant_bandi": [{"title": b.title, "ente": b.ente} for b in relevant_bandi]
            },
            "notification_type": "new_bandi"
        }
    
    else:
        return {"error": "Tipo notifica non supportato per preview"}
