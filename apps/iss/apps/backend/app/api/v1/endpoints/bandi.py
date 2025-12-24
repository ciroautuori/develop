from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from app.api.deps import get_current_admin
from app.crud.bando import bando_crud
from app.database.database import get_db
from app.schemas.bando import (
    BandoCreate, BandoRead, BandoUpdate, BandoList, BandoSearch, BandoStats,
    BandoStatusEnum, BandoSourceEnum
)
from app.models.admin import AdminUser
from app.services.bando_monitor import bando_monitor_service

router = APIRouter()


@router.get("/", response_model=BandoList)
@cache(expire=300)
async def get_bandi(
    # Paginazione - supporta sia skip/limit che page/per_page
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    page: Optional[int] = Query(None, ge=1),
    per_page: Optional[int] = Query(None, ge=1, le=100),

    # Ricerca e filtri
    search: Optional[str] = Query(None, description="Termine di ricerca"),
    query: Optional[str] = Query(None, description="Termine di ricerca (alias)"),
    fonte: Optional[str] = Query(None, description="Filtra per fonte"),
    categoria: Optional[str] = Query(None, description="Filtra per categoria"),
    status: Optional[str] = Query(None, description="Filtra per status"),

    # Filtri importo
    importo_min: Optional[float] = Query(None, ge=0),
    importo_max: Optional[float] = Query(None, ge=0),

    # Filtri data
    data_scadenza_da: Optional[str] = Query(None),
    data_scadenza_a: Optional[str] = Query(None),

    # Ordinamento
    sort_by: Optional[str] = Query("relevance", description="Campo di ordinamento"),
    sort_order: Optional[str] = Query("desc", description="Direzione ordinamento"),

    db: AsyncSession = Depends(get_db)
):
    """Recupera lista bandi con filtri e paginazione (endpoint pubblico)."""

    # Gestione paginazione - supporta sia page/per_page che skip/limit
    if page is not None and per_page is not None:
        skip = (page - 1) * per_page
        limit = per_page

    # Gestione termine di ricerca - usa search o query
    search_term = search or query

    # Ignora filtri con valore "all"
    fonte_filter = fonte if fonte and fonte != "all" else None
    categoria_filter = categoria if categoria and categoria != "all" else None
    status_filter = status if status and status != "all" else None

    search_params = BandoSearch(
        query=search_term,
        fonte=fonte_filter,
        status=status_filter,
        categoria=categoria_filter,
        importo_min=importo_min,
        importo_max=importo_max,
        data_scadenza_da=data_scadenza_da,
        data_scadenza_a=data_scadenza_a,
        sort_by=sort_by,
        sort_order=sort_order
    ) if any([search_term, fonte_filter, categoria_filter, status_filter,
              importo_min, importo_max, data_scadenza_da, data_scadenza_a]) else None

    bandi, total = await bando_crud.get_bandi(
        db, skip=skip, limit=limit, search=search_params
    )

    pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1

    return BandoList(
        items=bandi,
        total=total,
        page=current_page,
        size=limit,
        pages=pages
    )


@router.get("/stats", response_model=BandoStats)
@cache(expire=600)
async def get_bandi_stats(db: AsyncSession = Depends(get_db)):
    """Statistiche sui bandi (endpoint pubblico)."""
    stats = await bando_crud.get_stats(db)
    return BandoStats(**stats)


@router.get("/recent", response_model=List[BandoRead])
@cache(expire=180)
async def get_recent_bandi(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Recupera i bandi più recenti (endpoint pubblico)."""
    return await bando_crud.get_recent_bandi(db, limit=limit)


@router.get("/best-matches")
async def get_best_matches(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
    # Autenticazione admin opzionale per demo, ma consigliata
):
    """
    🧠 Analizza i bandi attivi e trova i 'Perfect Match' per ISS.
    Usa il profilo associazione predefinito (Mission, Target, Progetti).
    """
    from app.services.match_service import match_service
    
    matches = await match_service.get_perfect_matches(db, limit=limit)
    return matches


@router.get("/{bando_id}", response_model=BandoRead)
async def get_bando(
    bando_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Recupera un bando specifico per ID (endpoint pubblico)."""
    bando = await bando_crud.get_bando(db, bando_id=bando_id)
    if not bando:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bando non trovato"
        )
    return bando


# --- ADMIN ENDPOINTS ---

@router.post("/", response_model=BandoRead)
async def create_bando(
    bando_data: BandoCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Crea un nuovo bando manualmente (endpoint admin)."""
    return await bando_crud.create_bando(db, bando=bando_data)


@router.put("/{bando_id}", response_model=BandoRead)
async def update_bando(
    bando_id: int,
    bando_data: BandoUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Aggiorna un bando (endpoint admin)."""
    bando = await bando_crud.update_bando(db, bando_id=bando_id, bando_update=bando_data)
    if not bando:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bando non trovato"
        )
    return bando


@router.delete("/{bando_id}")
async def delete_bando(
    bando_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Elimina un bando (endpoint admin)."""
    success = await bando_crud.delete_bando(db, bando_id=bando_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bando non trovato"
        )
    return {"message": "Bando eliminato con successo"}


@router.post("/{bando_id}/notify")
async def mark_bando_notified(
    bando_id: int,
    email: bool = Query(False),
    telegram: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Marca un bando come notificato (endpoint admin)."""
    bando = await bando_crud.mark_as_notified(
        db, bando_id=bando_id, email=email, telegram=telegram
    )
    if not bando:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bando non trovato"
        )
    return {"message": "Bando marcato come notificato", "bando": bando}


@router.post("/cleanup")
async def cleanup_old_bandi(
    days_old: int = Query(365, ge=30, le=2000),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Pulisce/archivia i bandi vecchi (endpoint admin)."""
    count = await bando_crud.cleanup_old_bandi(db, days_old=days_old)
    return {"message": f"Archiviati {count} bandi", "archived_count": count}


@router.post("/trigger-monitoring")
async def trigger_monitoring(
    background_tasks: BackgroundTasks,
    config_id: Optional[int] = Query(None, description="ID configurazione specifica"),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Trigger manuale del monitoraggio bandi (endpoint admin)."""

    # Questo sarà implementato quando avremo il sistema di configurazione
    # Per ora ritorna un placeholder
    background_tasks.add_task(_run_monitoring_task, db, config_id)

    return {
        "message": "Monitoraggio avviato in background",
        "config_id": config_id,
        "status": "scheduled"
    }


@router.post("/ai-search")
async def ai_search_bandi(
    background_tasks: BackgroundTasks,
    keywords: Optional[List[str]] = Query(None, description="Keywords specifiche"),
    db: AsyncSession = Depends(get_db)
):
    """
    🤖 Avvia ricerca AI automatica di bandi per APS Campania.
    Usa Google Gemini e Groq per trovare opportunità di finanziamento.
    Endpoint pubblico per demo.
    """
    from app.services.ai_bandi_agent import ai_bandi_agent

    # Avvia ricerca in background
    background_tasks.add_task(_run_ai_search, keywords)

    return {
        "message": "🤖 Ricerca AI avviata in background",
        "keywords": keywords or ai_bandi_agent.keywords_aps[:5],
        "status": "scheduled",
        "info": "I risultati saranno visibili nella lista bandi tra qualche minuto"
    }


    async with ai_bandi_agent as agent:
        results = await agent.run_full_search(db, keywords)

    return results






async def _run_ai_search(keywords: Optional[List[str]] = None):
    """Task in background per ricerca AI"""
    from app.services.ai_bandi_agent import ai_bandi_agent
    from app.database.database import async_session_maker

    try:
        async with async_session_maker() as db:
            async with ai_bandi_agent as agent:
                results = await agent.run_full_search(db, keywords)
                return results
    except Exception as e:
        import logging
        logging.error(f"Errore AI search background: {e}")


async def _run_monitoring_task(db: AsyncSession, config_id: Optional[int] = None):
    """Task in background per eseguire il monitoraggio"""
    try:
        # Placeholder per il task di monitoraggio
        # Sarà implementato quando avremo la gestione configurazioni
        pass
    except Exception as e:
        # Log dell'errore
        pass


# --- BANDO SAVE/UNSAVE ENDPOINTS (MVP) ---

@router.post("/{bando_id}/save")
async def save_bando(
    bando_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Salva un bando nei preferiti dell'utente.
    MVP: Restituisce successo, il salvataggio effettivo è gestito lato frontend.
    In produzione: richiede autenticazione e salva in DB.
    """
    bando = await bando_crud.get_bando(db, bando_id=bando_id)
    if not bando:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bando non trovato"
        )
    return {"success": True, "message": "Bando salvato", "bando_id": bando_id}


@router.delete("/{bando_id}/save")
async def unsave_bando(
    bando_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Rimuove un bando dai preferiti dell'utente.
    MVP: Restituisce successo, la rimozione effettiva è gestita lato frontend.
    In produzione: richiede autenticazione e rimuove da DB.
    """
    return {"success": True, "message": "Bando rimosso dai salvati", "bando_id": bando_id}
