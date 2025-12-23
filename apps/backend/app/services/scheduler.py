"""
Servizio di scheduling per il monitoraggio automatico dei bandi
Utilizza APScheduler per gestire i job programmati
"""

import logging
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import async_session_maker
from app.crud.bando_config import bando_config_crud
from app.services.bando_monitor import bando_monitor_service
from app.services.alert_system import alert_system
from app.core.config import settings

logger = logging.getLogger(__name__)


class BandoSchedulerService:
    """Servizio per la programmazione automatica del monitoraggio bandi"""

    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.is_running = False

    async def start(self):
        """Avvia lo scheduler"""
        if self.is_running:
            logger.warning("Scheduler già in esecuzione")
            return

        try:
            self.scheduler = AsyncIOScheduler()

            # Job principale per controllare le configurazioni da eseguire
            self.scheduler.add_job(
                func=self._check_and_run_configs,
                trigger=IntervalTrigger(minutes=5),  # Controlla ogni 5 minuti
                id='bandi_monitor_check',
                name='Controllo configurazioni bandi',
                replace_existing=True,
                max_instances=1
            )

            # 🤖 Job AI Bandi Agent - Ricerca automatica ogni 24 ore
            self.scheduler.add_job(
                func=self._run_ai_bandi_search,
                trigger=CronTrigger(hour=6, minute=0),  # Ogni giorno alle 06:00
                id='ai_bandi_search_daily',
                name='AI Bandi Agent - Ricerca giornaliera',
                replace_existing=True,
                max_instances=1
            )

            # 🏛️ Job ricerca comuni - Due volte al giorno
            self.scheduler.add_job(
                func=self._run_ai_bandi_search,
                trigger=CronTrigger(hour=18, minute=0),  # Anche alle 18:00
                id='ai_bandi_search_evening',
                name='AI Bandi Agent - Ricerca serale',
                replace_existing=True,
                max_instances=1
            )

            # Job di pulizia giornaliera (alle 02:00)
            self.scheduler.add_job(
                func=self._daily_cleanup,
                trigger=CronTrigger(hour=2, minute=0),
                id='bandi_cleanup',
                name='Pulizia automatica bandi vecchi',
                replace_existing=True,
                max_instances=1
            )

            # Job per alert nuovi bandi (ogni ora)
            self.scheduler.add_job(
                func=self._check_new_bandi_alerts,
                trigger=IntervalTrigger(hours=1),
                id='new_bandi_alerts',
                name='Alert nuovi bandi agli utenti',
                replace_existing=True,
                max_instances=1
            )

            # Job per reminder scadenze (ogni 6 ore)
            self.scheduler.add_job(
                func=self._check_deadline_reminders,
                trigger=IntervalTrigger(hours=6),
                id='deadline_reminders',
                name='Reminder scadenze bandi',
                replace_existing=True,
                max_instances=1
            )

            # Job per newsletter settimanale (lunedì alle 09:00)
            self.scheduler.add_job(
                func=self._send_weekly_newsletters,
                trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),
                id='weekly_newsletters',
                name='Newsletter settimanali',
                replace_existing=True,
                max_instances=1
            )

            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduler bandi avviato con successo")

        except Exception as e:
            logger.error(f"Errore avvio scheduler: {e}")
            raise

    async def stop(self):
        """Ferma lo scheduler"""
        if not self.is_running or not self.scheduler:
            return

        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Scheduler bandi fermato")
        except Exception as e:
            logger.error(f"Errore stop scheduler: {e}")

    async def _check_and_run_configs(self):
        """Controlla le configurazioni da eseguire"""

        async with async_session_maker() as db:
            try:
                # Ottieni configurazioni da eseguire
                configs_to_run = await bando_config_crud.get_configs_to_run(db)

                if not configs_to_run:
                    return

                logger.info(f"Trovate {len(configs_to_run)} configurazioni da eseguire")

                # Esegui ogni configurazione
                for config in configs_to_run:
                    try:
                        await self._run_single_config(config, db)
                    except Exception as e:
                        logger.error(f"Errore esecuzione config {config.id}: {e}")

                        # Crea log di errore
                        await bando_config_crud.create_log(db, {
                            'config_id': config.id,
                            'status': 'failed',
                            'error_message': str(e),
                            'completed_at': datetime.now()
                        })

            except Exception as e:
                logger.error(f"Errore controllo configurazioni: {e}")

    async def _run_single_config(self, config, db: AsyncSession):
        """Esegue il monitoraggio per una singola configurazione"""

        logger.info(f"Esecuzione monitoraggio per config: {config.name} (ID: {config.id})")

        # Crea log di inizio
        log_data = {
            'config_id': config.id,
            'status': 'running'
        }
        log_entry = await bando_config_crud.create_log(db, log_data)

        try:
            # Esegui monitoraggio
            async with bando_monitor_service as monitor:
                result = await monitor.run_monitoring(db, config)

            # Aggiorna log con risultati
            await bando_config_crud.create_log(db, {
                'config_id': config.id,
                'bandi_found': result.get('bandi_found', 0),
                'bandi_new': result.get('bandi_new', 0),
                'errors_count': result.get('errors_count', 0),
                'status': result.get('status', 'completed'),
                'error_message': result.get('error_message'),
                'sources_processed': result.get('sources_processed'),
                'completed_at': datetime.now()
            })

            logger.info(
                f"Monitoraggio completato per {config.name}: "
                f"{result.get('bandi_new', 0)} nuovi bandi trovati"
            )

        except Exception as e:
            logger.error(f"Errore monitoraggio config {config.id}: {e}")

            # Aggiorna log con errore
            await bando_config_crud.create_log(db, {
                'config_id': config.id,
                'status': 'failed',
                'error_message': str(e),
                'completed_at': datetime.now()
            })

            raise

    async def _daily_cleanup(self):
        """Pulizia automatica giornaliera"""

        async with async_session_maker() as db:
            try:
                logger.info("Avvio pulizia automatica giornaliera")

                # Importa qui per evitare circular imports
                from app.crud.bando import bando_crud

                # Archivia bandi vecchi di 1 anno
                archived_count = await bando_crud.cleanup_old_bandi(db, days_old=365)

                logger.info(f"Pulizia completata: {archived_count} bandi archiviati")

            except Exception as e:
                logger.error(f"Errore pulizia automatica: {e}")

    def add_custom_job(
        self,
        func,
        trigger,
        job_id: str,
        name: str = None,
        **kwargs
    ):
        """Aggiungi un job personalizzato"""
        if not self.scheduler:
            raise RuntimeError("Scheduler non avviato")

        return self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            name=name or job_id,
            replace_existing=True,
            max_instances=1,
            **kwargs
        )

    def remove_job(self, job_id: str):
        """Rimuovi un job"""
        if not self.scheduler:
            return

        try:
            self.scheduler.remove_job(job_id)
        except Exception as e:
            logger.warning(f"Errore rimozione job {job_id}: {e}")

    def get_jobs(self):
        """Ottieni lista job attivi"""
        if not self.scheduler:
            return []

        return self.scheduler.get_jobs()

    def get_job_status(self, job_id: str):
        """Stato di un job specifico"""
        if not self.scheduler:
            return None

        return self.scheduler.get_job(job_id)

    # ========== NOTIFICATION JOBS ==========

    async def _check_new_bandi_alerts(self):
        """Job per controllare nuovi bandi e inviare alert"""
        async with async_session_maker() as db:
            try:
                logger.info("📧 Esecuzione job alert nuovi bandi")
                results = await alert_system.check_new_bandi_alerts(db)
                logger.info(f"📧 Alert nuovi bandi completato: {results}")
            except Exception as e:
                logger.error(f"❌ Errore job alert nuovi bandi: {e}")

    async def _check_deadline_reminders(self):
        """Job per controllare scadenze e inviare reminder"""
        async with async_session_maker() as db:
            try:
                logger.info("⏰ Esecuzione job reminder scadenze")
                results = await alert_system.check_deadline_reminders(db)
                logger.info(f"⏰ Reminder scadenze completato: {results}")
            except Exception as e:
                logger.error(f"❌ Errore job reminder scadenze: {e}")

    async def _send_weekly_newsletters(self):
        """Job per inviare newsletter settimanali"""
        async with async_session_maker() as db:
            try:
                logger.info("📊 Esecuzione job newsletter settimanali")
                results = await alert_system.send_weekly_newsletters(db)
                logger.info(f"📊 Newsletter settimanali completate: {results}")
            except Exception as e:
                logger.error(f"❌ Errore job newsletter settimanali: {e}")

    async def _run_ai_bandi_search(self):
        """🤖 Job per ricerca AI automatica dei bandi"""
        async with async_session_maker() as db:
            try:
                logger.info("🤖 Avvio AI Bandi Agent - Ricerca automatica schedulata")
                from app.services.ai_bandi_agent import ai_bandi_agent

                async with ai_bandi_agent as agent:
                    results = await agent.run_full_search(db)

                logger.info(f"🤖 AI Bandi Agent completato: {results.get('bandi_saved', 0)} nuovi bandi salvati")
            except Exception as e:
                logger.error(f"❌ Errore AI Bandi Agent: {e}")


# Istanza singleton del servizio scheduler
scheduler_service = BandoSchedulerService()


# Context manager per gestione automatica dello scheduler
@asynccontextmanager
async def scheduler_lifespan():
    """Context manager per gestire il ciclo di vita dello scheduler"""
    try:
        await scheduler_service.start()
        yield scheduler_service
    finally:
        await scheduler_service.stop()
