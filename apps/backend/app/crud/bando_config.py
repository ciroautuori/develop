from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from datetime import datetime, timedelta

from app.models.bando_config import BandoConfig, BandoLog
from app.models.bando import Bando, BandoStatus
from app.schemas.bando_config import BandoConfigCreate, BandoConfigUpdate


class BandoConfigCRUD:
    
    async def create_config(
        self, 
        db: AsyncSession, 
        config: BandoConfigCreate, 
        created_by: int
    ) -> BandoConfig:
        """Crea una nuova configurazione"""
        
        # Calcola next_run se scheduling è abilitato
        next_run = None
        if config.schedule_enabled:
            next_run = datetime.now() + timedelta(hours=config.schedule_interval_hours)
        
        db_config = BandoConfig(
            **config.model_dump(exclude={'email_password', 'telegram_bot_token'}),
            created_by=created_by,
            next_run=next_run
        )
        
        # Gestione sicura delle password (in produzione andrebbero crittografate)
        if config.email_password:
            db_config.email_password = config.email_password  # TODO: Encrypt
        if config.telegram_bot_token:
            db_config.telegram_bot_token = config.telegram_bot_token  # TODO: Encrypt
        
        db.add(db_config)
        await db.commit()
        await db.refresh(db_config)
        return db_config
    
    async def get_config(self, db: AsyncSession, config_id: int) -> Optional[BandoConfig]:
        """Recupera una configurazione per ID"""
        result = await db.execute(select(BandoConfig).where(BandoConfig.id == config_id))
        return result.scalar_one_or_none()
    
    async def get_config_by_name(self, db: AsyncSession, name: str) -> Optional[BandoConfig]:
        """Recupera una configurazione per nome"""
        result = await db.execute(select(BandoConfig).where(BandoConfig.name == name))
        return result.scalar_one_or_none()
    
    async def get_configs(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 20,
        active_only: bool = False
    ) -> List[BandoConfig]:
        """Recupera lista configurazioni"""
        
        query = select(BandoConfig)
        
        if active_only:
            query = query.where(BandoConfig.is_active == True)
        
        query = query.order_by(desc(BandoConfig.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def update_config(
        self, 
        db: AsyncSession, 
        config_id: int, 
        config_update: BandoConfigUpdate
    ) -> Optional[BandoConfig]:
        """Aggiorna una configurazione"""
        
        db_config = await self.get_config(db, config_id)
        if not db_config:
            return None
        
        update_data = config_update.model_dump(exclude_unset=True)
        
        # Aggiorna next_run se cambia l'intervallo
        if 'schedule_interval_hours' in update_data:
            if db_config.schedule_enabled:
                db_config.next_run = datetime.now() + timedelta(hours=update_data['schedule_interval_hours'])
        
        # Gestione sicura password
        if 'email_password' in update_data:
            db_config.email_password = update_data.pop('email_password')  # TODO: Encrypt
        if 'telegram_bot_token' in update_data:
            db_config.telegram_bot_token = update_data.pop('telegram_bot_token')  # TODO: Encrypt
        
        for field, value in update_data.items():
            setattr(db_config, field, value)
        
        await db.commit()
        await db.refresh(db_config)
        return db_config
    
    async def delete_config(self, db: AsyncSession, config_id: int) -> bool:
        """Elimina una configurazione"""
        db_config = await self.get_config(db, config_id)
        if not db_config:
            return False
        
        await db.delete(db_config)
        await db.commit()
        return True
    
    async def activate_config(self, db: AsyncSession, config_id: int) -> Optional[BandoConfig]:
        """Attiva una configurazione"""
        db_config = await self.get_config(db, config_id)
        if not db_config:
            return None
        
        db_config.is_active = True
        if db_config.schedule_enabled and not db_config.next_run:
            db_config.next_run = datetime.now() + timedelta(hours=db_config.schedule_interval_hours)
        
        await db.commit()
        await db.refresh(db_config)
        return db_config
    
    async def deactivate_config(self, db: AsyncSession, config_id: int) -> Optional[BandoConfig]:
        """Disattiva una configurazione"""
        db_config = await self.get_config(db, config_id)
        if not db_config:
            return None
        
        db_config.is_active = False
        await db.commit()
        await db.refresh(db_config)
        return db_config
    
    async def get_configs_to_run(self, db: AsyncSession) -> List[BandoConfig]:
        """Recupera configurazioni da eseguire (per scheduler)"""
        now = datetime.now()
        
        query = select(BandoConfig).where(
            and_(
                BandoConfig.is_active == True,
                BandoConfig.schedule_enabled == True,
                BandoConfig.next_run <= now
            )
        )
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    # --- LOG OPERATIONS ---
    
    async def create_log(self, db: AsyncSession, log_data: Dict[str, Any]) -> BandoLog:
        """Crea un nuovo log di esecuzione"""
        db_log = BandoLog(**log_data)
        db.add(db_log)
        await db.commit()
        await db.refresh(db_log)
        return db_log
    
    async def get_config_logs(
        self, 
        db: AsyncSession, 
        config_id: int, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[BandoLog]:
        """Recupera i log per una configurazione"""
        
        query = (
            select(BandoLog)
            .where(BandoLog.config_id == config_id)
            .order_by(desc(BandoLog.started_at))
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_latest_log(self, db: AsyncSession, config_id: int) -> Optional[BandoLog]:
        """Recupera l'ultimo log per una configurazione"""
        
        query = (
            select(BandoLog)
            .where(BandoLog.config_id == config_id)
            .order_by(desc(BandoLog.started_at))
            .limit(1)
        )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    # --- STATUS E STATISTICHE ---
    
    async def get_monitor_status(self, db: AsyncSession) -> Dict[str, Any]:
        """Recupera lo status generale del sistema di monitoraggio"""
        
        # Configurazioni attive
        active_configs_query = select(func.count(BandoConfig.id)).where(BandoConfig.is_active == True)
        active_result = await db.execute(active_configs_query)
        active_configs = active_result.scalar()
        
        # Ultima esecuzione riuscita
        last_success_query = (
            select(BandoLog.completed_at)
            .where(BandoLog.status == "completed")
            .order_by(desc(BandoLog.completed_at))
            .limit(1)
        )
        success_result = await db.execute(last_success_query)
        last_successful_run = success_result.scalar_one_or_none()
        
        # Totale bandi trovati
        total_bandi_query = select(func.count(Bando.id))
        total_result = await db.execute(total_bandi_query)
        total_bandi_found = total_result.scalar()
        
        # Errori nelle ultime 24 ore
        yesterday = datetime.now() - timedelta(hours=24)
        errors_query = (
            select(func.count(BandoLog.id))
            .where(and_(
                BandoLog.status == "failed",
                BandoLog.started_at >= yesterday
            ))
        )
        errors_result = await db.execute(errors_query)
        errors_last_24h = errors_result.scalar()
        
        # Prossime esecuzioni programmate
        next_runs_query = (
            select(BandoConfig.name, BandoConfig.next_run)
            .where(and_(
                BandoConfig.is_active == True,
                BandoConfig.schedule_enabled == True,
                BandoConfig.next_run.isnot(None)
            ))
            .order_by(BandoConfig.next_run)
            .limit(5)
        )
        
        next_runs_result = await db.execute(next_runs_query)
        next_scheduled_runs = [
            {"config_name": name, "next_run": next_run}
            for name, next_run in next_runs_result.fetchall()
        ]
        
        # Verifica se ci sono processi in esecuzione
        running_query = select(func.count(BandoLog.id)).where(BandoLog.status == "running")
        running_result = await db.execute(running_query)
        is_running = running_result.scalar() > 0
        
        return {
            "is_running": is_running,
            "active_configs": active_configs,
            "last_successful_run": last_successful_run,
            "total_bandi_found": total_bandi_found,
            "errors_last_24h": errors_last_24h,
            "next_scheduled_runs": next_scheduled_runs
        }


# Istanza singleton
bando_config_crud = BandoConfigCRUD()
