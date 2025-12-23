#!/usr/bin/env python3
"""
Script di setup per il sistema di monitoraggio bandi ISS
- Esegue le migrazioni del database
- Crea la configurazione di default
- Verifica le dipendenze
"""

import asyncio
import sys
import os
from pathlib import Path

# Aggiungi il path della app
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import async_session_maker
from app.crud.bando_config import bando_config_crud
from app.schemas.bando_config import BandoConfigCreate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_database_connection():
    """Verifica connessione database"""
    try:
        async with async_session_maker() as db:
            await db.execute("SELECT 1")
        logger.info("✅ Connessione database OK")
        return True
    except Exception as e:
        logger.error(f"❌ Errore connessione database: {e}")
        return False


async def create_default_bando_config():
    """Crea configurazione di default per il monitoraggio"""
    try:
        async with async_session_maker() as db:
            # Verifica se esiste già una configurazione di default
            existing = await bando_config_crud.get_config_by_name(db, "ISS Default")
            
            if existing:
                logger.info("⚠️  Configurazione 'ISS Default' già esistente")
                return existing
            
            # Crea configurazione di default
            default_config = BandoConfigCreate(
                name="ISS Default",
                email_enabled=True,
                email_smtp_server="smtp.gmail.com",
                email_smtp_port=587,
                email_username="",  # Da configurare
                email_recipient="",  # Da configurare
                telegram_enabled=False,
                keywords=[
                    "alfabetizzazione digitale",
                    "inclusione digitale", 
                    "competenze digitali",
                    "anziani",
                    "digitalizzazione",
                    "innovazione sociale",
                    "terzo settore",
                    "associazioni",
                    "volontariato",
                    "coesione sociale",
                    "comunità",
                    "formazione digitale",
                    "divario digitale",
                    "cittadinanza digitale",
                    "promozione sociale",
                    "educazione digitale",
                    "smart city",
                    "welfare",
                    "inclusione sociale"
                ],
                scraping_delay=2,
                max_retries=3,
                timeout=10,
                schedule_enabled=True,
                schedule_interval_hours=24,
                min_deadline_days=30,
                fonte_enabled={
                    "comune_salerno": True,
                    "regione_campania": True,
                    "csv_salerno": True,
                    "fondazione_comunita": True
                }
            )
            
            config = await bando_config_crud.create_config(
                db, config=default_config, created_by=1
            )
            
            logger.info(f"✅ Configurazione di default creata (ID: {config.id})")
            return config
            
    except Exception as e:
        logger.error(f"❌ Errore creazione configurazione di default: {e}")
        return None


async def run_setup():
    """Esegue il setup completo del sistema"""
    
    logger.info("🚀 Avvio setup sistema monitoraggio bandi ISS")
    
    # 1. Verifica connessione database
    if not await check_database_connection():
        logger.error("❌ Setup fallito: problema connessione database")
        return False
    
    # 2. Crea configurazione di default
    config = await create_default_bando_config()
    if not config:
        logger.error("❌ Setup fallito: problema creazione configurazione")
        return False
    
    # 3. Verifica dipendenze importanti
    try:
        import beautifulsoup4
        import apscheduler
        import httpx
        logger.info("✅ Dipendenze Python verificate")
    except ImportError as e:
        logger.error(f"❌ Dipendenza mancante: {e}")
        logger.info("💡 Esegui: pip install -r requirements.txt")
        return False
    
    logger.info("🎉 Setup completato con successo!")
    
    # Mostra informazioni di configurazione
    logger.info("\n" + "="*50)
    logger.info("📋 CONFIGURAZIONE SISTEMA BANDI")
    logger.info("="*50)
    logger.info(f"ID Configurazione: {config.id}")
    logger.info(f"Nome: {config.name}")
    logger.info(f"Parole chiave: {len(config.keywords)} configurate")
    logger.info(f"Intervallo controllo: {config.schedule_interval_hours} ore")
    logger.info(f"Fonti abilitate: {len([k for k, v in config.fonte_enabled.items() if v])}")
    logger.info("\n⚠️  CONFIGURAZIONE RICHIESTA:")
    logger.info("1. Imposta email_username e email_recipient nella configurazione")
    logger.info("2. Configura password applicazione Gmail")
    logger.info("3. [Opzionale] Configura bot Telegram")
    logger.info("\n🔧 Gestisci configurazioni tramite:")
    logger.info("   GET /api/v1/admin/bandi-config/")
    logger.info("   PUT /api/v1/admin/bandi-config/{id}")
    logger.info("="*50)
    
    return True


def print_migration_info():
    """Mostra informazioni sulle migrazioni"""
    logger.info("\n" + "="*50)
    logger.info("🗄️  MIGRAZIONI DATABASE")
    logger.info("="*50)
    logger.info("Per applicare le migrazioni del sistema bandi:")
    logger.info("   cd /home/ciroautuori/Scrivania/iss/backend")
    logger.info("   alembic upgrade head")
    logger.info("\nLa migrazione '003' aggiunge:")
    logger.info("   - Tabella 'bandi' per i bandi trovati")
    logger.info("   - Tabella 'bando_configs' per le configurazioni")
    logger.info("   - Tabella 'bando_logs' per i log di esecuzione")
    logger.info("="*50)


if __name__ == "__main__":
    print_migration_info()
    
    print(f"\n🔄 Vuoi procedere con il setup? (y/N): ", end="")
    response = input().lower().strip()
    
    if response in ['y', 'yes', 's', 'si']:
        success = asyncio.run(run_setup())
        sys.exit(0 if success else 1)
    else:
        logger.info("Setup annullato dall'utente")
        sys.exit(0)
