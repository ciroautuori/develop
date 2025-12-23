"""
Endpoint API per sistema utenti APS
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from app.database.database import get_db
from app.crud.aps_user import aps_user_crud, bando_application_crud, bando_watchlist_crud
from app.schemas.aps_user import (
    APSUserCreate, APSUserRead, APSUserUpdate, APSUserPublic, APSUserSearch, APSUserSearchResponse,
    BandoApplicationCreate, BandoApplicationRead, BandoApplicationUpdate,
    BandoWatchlistCreate, BandoWatchlistRead, BandoWatchlistUpdate,
    AIRecommendationRead, AIRecommendationUpdate, UserDashboard,
    OrganizationTypeEnum
)
from app.models.aps_user import OrganizationType

router = APIRouter()


# ========== USER REGISTRATION & MANAGEMENT ==========

@router.post("/register", response_model=APSUserRead, status_code=status.HTTP_201_CREATED)
async def register_aps_user(
    user_data: APSUserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    🆕 Registrazione nuova organizzazione APS/ODV
    
    Registra una nuova organizzazione del terzo settore nella piattaforma ISS.
    Ogni organizzazione può poi accedere a bandi personalizzati e AI.
    """
    # Controlla se email già esistente
    existing_user = await aps_user_crud.get_by_email(db, user_data.contact_email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email già registrata"
        )
    
    # Controlla se codice fiscale già esistente
    existing_fiscal = await aps_user_crud.get_by_fiscal_code(db, user_data.fiscal_code)
    if existing_fiscal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Codice fiscale già registrato"
        )
    
    # Crea utente
    try:
        user = await aps_user_crud.create_aps_user(db, user_data.dict())
        
        # TODO: Invia email di benvenuto
        # TODO: Genera prime raccomandazioni AI
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore registrazione: {str(e)}"
        )


@router.get("/search", response_model=APSUserSearchResponse)
@cache(expire=300)  # Cache 5 minuti
async def search_aps_users(
    search: Optional[str] = Query(None, description="Cerca per nome organizzazione, email o città"),
    organization_type: Optional[OrganizationTypeEnum] = Query(None, description="Filtra per tipo organizzazione"),
    region: Optional[str] = Query(None, description="Filtra per regione"),
    sectors: Optional[str] = Query(None, description="Settori comma-separated"),
    is_active: Optional[bool] = Query(None, description="Solo utenti attivi"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """
    🔍 Ricerca organizzazioni APS registrate
    
    Permette di cercare e filtrare le organizzazioni registrate nella piattaforma.
    Utile per networking e collaborazioni.
    """
    # Parse sectors
    sectors_list = None
    if sectors:
        sectors_list = [s.strip() for s in sectors.split(",") if s.strip()]
    
    # Converti enum
    org_type = None
    if organization_type:
        org_type = OrganizationType(organization_type.value)
    
    users, total = await aps_user_crud.search_users(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        organization_type=org_type,
        region=region,
        sectors=sectors_list,
        is_active=is_active
    )
    
    return APSUserSearchResponse(
        items=[APSUserPublic.from_orm(user) for user in users],
        total=total,
        skip=skip,
        limit=limit,
        has_more=total > skip + len(users)
    )


@router.get("/{user_id}", response_model=APSUserRead)
async def get_aps_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    👤 Dettagli organizzazione APS
    """
    user = await aps_user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizzazione non trovata"
        )
    return user


@router.put("/{user_id}", response_model=APSUserRead)
async def update_aps_user(
    user_id: int,
    user_update: APSUserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    ✏️ Aggiorna profilo organizzazione
    """
    user = await aps_user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizzazione non trovata"
        )
    
    update_data = user_update.dict(exclude_unset=True)
    user = await aps_user_crud.update(db, db_obj=user, obj_in=update_data)
    return user


# ========== DASHBOARD ==========

@router.get("/{user_id}/dashboard", response_model=UserDashboard)
async def get_user_dashboard(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    📊 Dashboard completa organizzazione
    
    Dashboard personalizzata con:
    - Statistiche candidature
    - Bandi in watchlist
    - Raccomandazioni AI
    - Scadenze imminenti
    """
    dashboard_data = await aps_user_crud.get_user_dashboard_data(db, user_id)
    
    if not dashboard_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizzazione non trovata"
        )
    
    return UserDashboard(
        user=APSUserRead.from_orm(dashboard_data['user']),
        stats={
            'total_applications': dashboard_data['applications_stats']['total'],
            'successful_applications': dashboard_data['applications_stats']['approved'],
            'pending_applications': dashboard_data['applications_stats']['submitted'] + dashboard_data['applications_stats']['in_review'],
            'success_rate': dashboard_data['applications_stats']['success_rate'],
            'active_watchlist_count': dashboard_data['active_watchlist_count'],
            'unviewed_recommendations_count': dashboard_data['unviewed_recommendations_count'],
            'upcoming_deadlines_count': len(dashboard_data['upcoming_deadlines'])
        },
        recent_applications=[BandoApplicationRead.from_orm(app) for app in dashboard_data['recent_applications']],
        top_recommendations=[AIRecommendationRead.from_orm(rec) for rec in dashboard_data['top_recommendations']],
        upcoming_deadlines=dashboard_data['upcoming_deadlines']
    )


# ========== APPLICATIONS MANAGEMENT ==========

@router.post("/{user_id}/applications", response_model=BandoApplicationRead, status_code=status.HTTP_201_CREATED)
async def create_application(
    user_id: int,
    application_data: BandoApplicationCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    📝 Candidatura a un bando
    
    Registra una nuova candidatura dell'organizzazione a un bando specifico.
    """
    # Verifica utente esista
    user = await aps_user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Organizzazione non trovata")
    
    # Verifica bando esista (importiamo al bisogno)
    from app.crud.bando import bando_crud
    bando = await bando_crud.get(db, id=application_data.bando_id)
    if not bando:
        raise HTTPException(status_code=404, detail="Bando non trovato")
    
    try:
        application = await bando_application_crud.create_application(
            db=db,
            user_id=user_id,
            bando_id=application_data.bando_id,
            application_data=application_data.dict(exclude={'bando_id'})
        )
        
        # Background task: calcola probabilità successo con AI
        # background_tasks.add_task(calculate_success_probability, application.id)
        
        return application
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/applications", response_model=List[BandoApplicationRead])
async def get_user_applications(
    user_id: int,
    status_filter: Optional[str] = Query(None, description="Filtra per stato: submitted, in_review, approved, rejected"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """
    📋 Lista candidature organizzazione
    """
    user = await aps_user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Organizzazione non trovata")
    
    applications = await bando_application_crud.get_user_applications(
        db=db,
        user_id=user_id,
        status=status_filter,
        skip=skip,
        limit=limit
    )
    
    return [BandoApplicationRead.from_orm(app) for app in applications]


@router.put("/applications/{application_id}", response_model=BandoApplicationRead)
async def update_application(
    application_id: int,
    application_update: BandoApplicationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    ✏️ Aggiorna candidatura
    """
    application = await bando_application_crud.get(db, id=application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Candidatura non trovata")
    
    update_data = application_update.dict(exclude_unset=True)
    application = await bando_application_crud.update(db, db_obj=application, obj_in=update_data)
    return application


# ========== WATCHLIST MANAGEMENT ==========

@router.post("/{user_id}/watchlist", response_model=BandoWatchlistRead, status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    user_id: int,
    watchlist_data: BandoWatchlistCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    ⭐ Aggiungi bando alla watchlist
    
    Aggiunge un bando alla lista di quelli seguiti dall'organizzazione.
    """
    user = await aps_user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Organizzazione non trovata")
    
    try:
        watchlist_item = await bando_watchlist_crud.add_to_watchlist(
            db=db,
            user_id=user_id,
            bando_id=watchlist_data.bando_id,
            priority=watchlist_data.priority,
            notes=watchlist_data.notes
        )
        return watchlist_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}/watchlist", response_model=List[BandoWatchlistRead])
async def get_user_watchlist(
    user_id: int,
    active_only: bool = Query(True, description="Solo bandi ancora attivi"),
    db: AsyncSession = Depends(get_db)
):
    """
    📌 Lista bandi in watchlist
    """
    user = await aps_user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Organizzazione non trovata")
    
    watchlist = await bando_watchlist_crud.get_user_watchlist(
        db=db,
        user_id=user_id,
        active_only=active_only
    )
    
    return [BandoWatchlistRead.from_orm(item) for item in watchlist]


@router.delete("/{user_id}/watchlist/{bando_id}")
async def remove_from_watchlist(
    user_id: int,
    bando_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    🗑️ Rimuovi bando dalla watchlist
    """
    user = await aps_user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Organizzazione non trovata")
    
    removed = await bando_watchlist_crud.remove_from_watchlist(db, user_id, bando_id)
    
    if not removed:
        raise HTTPException(status_code=404, detail="Bando non trovato in watchlist")
    
    return {"message": "Bando rimosso dalla watchlist"}


# ========== AI RECOMMENDATIONS ==========

@router.get("/{user_id}/recommendations", response_model=List[AIRecommendationRead])
async def get_ai_recommendations(
    user_id: int,
    unviewed_only: bool = Query(False, description="Solo raccomandazioni non viste"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    🤖 Raccomandazioni AI personalizzate
    
    Lista delle raccomandazioni AI basate sul profilo dell'organizzazione.
    """
    user = await aps_user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Organizzazione non trovata")
    
    # TODO: Implementare query per raccomandazioni
    # Per ora placeholder
    return []


@router.post("/{user_id}/generate-recommendations")
async def generate_ai_recommendations(
    user_id: int,
    background_tasks: BackgroundTasks,
    force_refresh: bool = Query(False, description="Forza rigenerazione"),
    db: AsyncSession = Depends(get_db)
):
    """
    ⚡ Genera nuove raccomandazioni AI
    
    Rigenera le raccomandazioni AI per l'organizzazione basandosi sul profilo aggiornato.
    """
    user = await aps_user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Organizzazione non trovata")
    
    # Background task per generazione AI
    async def generate_recommendations_task():
        try:
            # TODO: Implementare logica AI per raccomandazioni
            # Usare semantic_search_service per match profilo → bandi
            pass
        except Exception as e:
            print(f"Errore generazione raccomandazioni: {e}")
    
    background_tasks.add_task(generate_recommendations_task)
    
    return {"message": "Generazione raccomandazioni AI avviata in background"}
