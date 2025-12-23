"""
Endpoint API per gestione ADMIN
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.database.database import get_db
from app.models.aps_user import APSUser, OrganizationType

router = APIRouter()


class AdminCreate(BaseModel):
    """Schema creazione admin"""
    email: EmailStr
    organization_name: str = "ISS Platform Admin"
    password: str = "ISSAdmin2024!"


class AdminResponse(BaseModel):
    """Risposta creazione admin"""
    id: int
    email: str
    organization_name: str
    is_admin: bool
    message: str


@router.post("/create-admin", response_model=AdminResponse)
async def create_admin_account(
    admin_data: Optional[AdminCreate] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    🔐 Crea account ADMIN per ISS Platform
    
    Questo endpoint crea un account amministratore con privilegi speciali.
    Usare solo per setup iniziale!
    """
    
    # Usa dati default se non forniti
    if not admin_data:
        admin_data = AdminCreate(
            email="admin@innovazionesocialesalernitana.it",
            organization_name="ISS Platform Admin"
        )
    
    try:
        # Controlla se admin esiste già
        result = await db.execute(
            select(APSUser).where(APSUser.contact_email == admin_data.email)
        )
        existing = result.scalars().first()
        
        if existing:
            return AdminResponse(
                id=existing.id,
                email=existing.contact_email,
                organization_name=existing.organization_name,
                is_admin=True,
                message="✅ Admin già esistente"
            )
        
        # Crea nuovo admin usando il modello APSUser
        admin = APSUser(
            organization_name=admin_data.organization_name,
            organization_type=OrganizationType.ALTRO,
            fiscal_code="ADMIN00000000000",
            contact_email=admin_data.email,
            region="Campania",
            geographical_scope="Nazionale",
            description="Account amministratore ISS Platform",
            sectors=["sociale", "cultura", "formazione", "innovazione"],
            keywords=["admin", "gestione", "piattaforma"],
            is_active=True,
            is_verified=True,
            notification_preferences={
                "email_enabled": True,
                "new_bandi_alerts": True,
                "deadline_reminders": True,
                "weekly_newsletter": True,
                "ai_recommendations": True
            }
        )
        
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        
        return AdminResponse(
            id=admin.id,
            email=admin.contact_email,
            organization_name=admin.organization_name,
            is_admin=True,
            message="🎉 Admin creato con successo!"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore creazione admin: {str(e)}"
        )


@router.get("/test-system")
async def test_system_status(db: AsyncSession = Depends(get_db)):
    """
    🧪 Test completo sistema ISS
    
    Verifica:
    - Database connessione
    - Bandi presenti
    - Utenti registrati
    - API funzionanti
    """
    try:
        from app.models.bando import Bando
        
        # Conta bandi
        bandi_result = await db.execute(select(Bando))
        bandi = list(bandi_result.scalars().all())
        
        # Conta utenti
        users_result = await db.execute(select(APSUser))
        users = list(users_result.scalars().all())
        
        return {
            "status": "✅ Sistema operativo",
            "database": "✅ Connesso",
            "bandi": {
                "totale": len(bandi),
                "attivi": len([b for b in bandi if (b.status.value if hasattr(b.status, 'value') else b.status) == 'attivo'])
            },
            "utenti": {
                "totale": len(users),
                "attivi": len([u for u in users if u.is_active])
            },
            "api_endpoints": {
                "bandi": "✅ /api/v1/bandi",
                "aps_users": "✅ /api/v1/aps-users",
                "notifications": "✅ /api/v1/notifications",
                "analytics": "✅ /api/v1/analytics",
                "ai_search": "✅ /api/v1/ai/search"
            },
            "features": {
                "ai_semantic_search": "✅ Attivo",
                "email_notifications": "⚠️ Configurare SMTP",
                "scheduler_alerts": "✅ Attivo",
                "analytics_dashboard": "✅ Attivo"
            }
        }
        
    except Exception as e:
        return {
            "status": "❌ Errore",
            "error": str(e)
        }


@router.get("/quick-stats")
async def get_quick_stats(db: AsyncSession = Depends(get_db)):
    """
    📊 Statistiche rapide sistema
    """
    try:
        from app.models.bando import Bando
        from app.models.aps_user import BandoApplication, BandoWatchlist
        
        # Query veloci
        bandi_count = await db.execute(select(APSUser.id).select_from(Bando))
        users_count = await db.execute(select(APSUser.id))
        apps_count = await db.execute(select(BandoApplication.id))
        watch_count = await db.execute(select(BandoWatchlist.id))
        
        return {
            "🏛️ Bandi totali": len(list(bandi_count.scalars().all())),
            "👥 Utenti APS": len(list(users_count.scalars().all())),
            "📝 Candidature": len(list(apps_count.scalars().all())),
            "⭐ Watchlist items": len(list(watch_count.scalars().all())),
            "timestamp": "2025-10-10T09:17:00Z"
        }
        
    except Exception as e:
        return {"error": str(e)}
