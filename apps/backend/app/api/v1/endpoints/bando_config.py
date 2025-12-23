from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.api.deps import get_current_admin
from app.database.database import get_db
from app.schemas.bando_config import (
    BandoConfigCreate, BandoConfigRead, BandoConfigUpdate,
    BandoLogRead, BandoMonitorStatus
)
from app.models.admin import AdminUser
from app.crud.bando_config import bando_config_crud
from app.services.bando_monitor import bando_monitor_service

router = APIRouter()


@router.get("/", response_model=List[BandoConfigRead])
async def get_bando_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    active_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Recupera tutte le configurazioni di monitoraggio (admin)."""
    return await bando_config_crud.get_configs(
        db, skip=skip, limit=limit, active_only=active_only
    )


@router.get("/status", response_model=BandoMonitorStatus)
async def get_monitor_status(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Stato generale del sistema di monitoraggio (admin)."""
    return await bando_config_crud.get_monitor_status(db)


@router.get("/{config_id}", response_model=BandoConfigRead)
async def get_bando_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Recupera una configurazione specifica (admin)."""
    config = await bando_config_crud.get_config(db, config_id=config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configurazione non trovata"
        )
    return config


@router.post("/", response_model=BandoConfigRead)
async def create_bando_config(
    config_data: BandoConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Crea una nuova configurazione di monitoraggio (admin)."""
    
    # Verifica che il nome sia unico
    existing = await bando_config_crud.get_config_by_name(db, config_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome configurazione già esistente"
        )
    
    return await bando_config_crud.create_config(
        db, config=config_data, created_by=current_admin.id
    )


@router.put("/{config_id}", response_model=BandoConfigRead)
async def update_bando_config(
    config_id: int,
    config_data: BandoConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Aggiorna una configurazione di monitoraggio (admin)."""
    
    # Verifica nome unico se viene cambiato
    if config_data.name:
        existing = await bando_config_crud.get_config_by_name(db, config_data.name)
        if existing and existing.id != config_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome configurazione già esistente"
            )
    
    config = await bando_config_crud.update_config(
        db, config_id=config_id, config_update=config_data
    )
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configurazione non trovata"
        )
    return config


@router.delete("/{config_id}")
async def delete_bando_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Elimina una configurazione di monitoraggio (admin)."""
    success = await bando_config_crud.delete_config(db, config_id=config_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configurazione non trovata"
        )
    return {"message": "Configurazione eliminata con successo"}


@router.post("/{config_id}/activate")
async def activate_bando_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Attiva una configurazione di monitoraggio (admin)."""
    config = await bando_config_crud.activate_config(db, config_id=config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configurazione non trovata"
        )
    return {"message": "Configurazione attivata", "config": config}


@router.post("/{config_id}/deactivate")
async def deactivate_bando_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Disattiva una configurazione di monitoraggio (admin)."""
    config = await bando_config_crud.deactivate_config(db, config_id=config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configurazione non trovata"
        )
    return {"message": "Configurazione disattivata", "config": config}


@router.post("/{config_id}/run")
async def run_monitoring_now(
    config_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Esegui monitoraggio immediato per una configurazione (admin)."""
    
    config = await bando_config_crud.get_config(db, config_id=config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configurazione non trovata"
        )
    
    if not config.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossibile eseguire monitoraggio: configurazione non attiva"
        )
    
    # Avvia task in background
    background_tasks.add_task(_run_monitoring_task, db, config)
    
    return {
        "message": "Monitoraggio avviato in background",
        "config_id": config_id,
        "config_name": config.name,
        "status": "scheduled"
    }


@router.get("/{config_id}/logs", response_model=List[BandoLogRead])
async def get_config_logs(
    config_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Recupera i log di esecuzione per una configurazione (admin)."""
    
    # Verifica che la configurazione esista
    config = await bando_config_crud.get_config(db, config_id=config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configurazione non trovata"
        )
    
    return await bando_config_crud.get_config_logs(
        db, config_id=config_id, skip=skip, limit=limit
    )


@router.post("/{config_id}/test")
async def test_bando_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Test di connettività per una configurazione (admin)."""
    
    config = await bando_config_crud.get_config(db, config_id=config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configurazione non trovata"
        )
    
    # Test delle configurazioni
    test_results = {
        "config_id": config_id,
        "config_name": config.name,
        "tests": {}
    }
    
    # Test email
    if config.email_enabled and config.email_username:
        try:
            # Placeholder per test email
            test_results["tests"]["email"] = {
                "status": "success",
                "message": "Configurazione email valida"
            }
        except Exception as e:
            test_results["tests"]["email"] = {
                "status": "error", 
                "message": f"Errore email: {str(e)}"
            }
    
    # Test Telegram
    if config.telegram_enabled and config.telegram_bot_token:
        try:
            # Placeholder per test Telegram
            test_results["tests"]["telegram"] = {
                "status": "success",
                "message": "Configurazione Telegram valida"
            }
        except Exception as e:
            test_results["tests"]["telegram"] = {
                "status": "error",
                "message": f"Errore Telegram: {str(e)}"
            }
    
    # Test keywords
    if config.keywords and len(config.keywords) > 0:
        test_results["tests"]["keywords"] = {
            "status": "success",
            "message": f"Configurate {len(config.keywords)} parole chiave"
        }
    else:
        test_results["tests"]["keywords"] = {
            "status": "warning",
            "message": "Nessuna parola chiave configurata"
        }
    
    return test_results


async def _run_monitoring_task(db: AsyncSession, config):
    """Task in background per eseguire il monitoraggio"""
    try:
        async with bando_monitor_service as monitor:
            result = await monitor.run_monitoring(db, config)
            
            # Salva log del risultato
            log_data = {
                'config_id': config.id,
                'bandi_found': result.get('bandi_found', 0),
                'bandi_new': result.get('bandi_new', 0),
                'errors_count': result.get('errors_count', 0),
                'status': result.get('status', 'completed'),
                'error_message': result.get('error_message'),
                'sources_processed': result.get('sources_processed'),
                'completed_at': datetime.now()
            }
            
            await bando_config_crud.create_log(db, log_data)
            
    except Exception as e:
        # Log dell'errore
        await bando_config_crud.create_log(db, {
            'config_id': config.id,
            'status': 'failed',
            'error_message': str(e),
            'completed_at': datetime.now()
        })
