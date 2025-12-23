"""
Script per recuperare BANDI REALI dai siti istituzionali
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.database.database import get_db, engine, Base
from app.models.bando_config import BandoConfig
from app.services.bando_monitor import BandoMonitorService

async def create_tables():
    """Crea tutte le tabelle"""
    from app.models.bando import Bando, BandoSource, BandoStatus
    from app.models.bando_config import BandoConfig, BandoLog
    from app.models.user import User
    from app.models.admin import AdminUser

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tabelle create!")

async def create_default_config(db):
    """Crea configurazione di default"""
    from sqlalchemy import select

    # Verifica se esiste già
    result = await db.execute(select(BandoConfig))
    existing = result.scalar_one_or_none()

    if existing:
        print(f"📋 Config esistente: {existing.name}")
        return existing

    # Crea nuova config
    config = BandoConfig(
        name="ISS Default Config",
        email_enabled=False,  # Disabilitato per ora
        telegram_enabled=False,
        keywords=[
            "digitale", "innovazione", "giovani", "inclusione",
            "formazione", "cultura", "sociale", "aps",
            "terzo settore", "volontariato", "disabilità",
            "ambiente", "sostenibilità", "educazione",
            "imprese", "start-up", "mezzogiorno", "pnrr"
        ],
        scraping_delay=3,
        max_retries=3,
        timeout=30,
        is_active=True,
        schedule_enabled=False,
        schedule_interval_hours=24,
        min_deadline_days=7,  # Accetta anche bandi in scadenza tra 7 giorni
        fonte_enabled={
            "comune_salerno": True,
            "regione_campania": True,
            "csv_salerno": True,
            "invitalia": True,
            "ministero_lavoro": True,
            "fondazione_con_il_sud": True,
            "pnrr_italia_domani": True
        }
    )

    db.add(config)
    await db.commit()
    await db.refresh(config)

    print(f"✅ Config creata: {config.name}")
    return config

async def fetch_real_bandi():
    """Recupera bandi REALI dai siti"""

    print("🚀 INIZIO RECUPERO BANDI REALI\n")

    # Crea tabelle
    await create_tables()

    db = None
    try:
        async for session in get_db():
            db = session
            break
        # Crea o recupera config
        config = await create_default_config(db)

        print(f"\n🔍 Keywords attive: {', '.join(config.keywords[:5])}...\n")

        # Usa il servizio di monitoraggio REALE
        async with BandoMonitorService() as monitor:
            print("📡 Avvio scraping REALE dai siti istituzionali...\n")

            result = await monitor.run_monitoring(db, config)

            print("\n" + "="*60)
            print("📊 RISULTATI SCRAPING")
            print("="*60)
            print(f"✅ Status: {result['status']}")
            print(f"📋 Bandi trovati: {result['bandi_found']}")
            print(f"🆕 Bandi nuovi: {result['bandi_new']}")
            print(f"❌ Errori: {result['errors_count']}")

            if result.get('sources_processed'):
                print("\n📂 FONTI PROCESSATE:")
                for source, info in result['sources_processed'].items():
                    status_emoji = "✅" if info.get('status') == 'success' else "❌"
                    print(f"  {status_emoji} {source}: {info.get('found', 0)} bandi trovati")
                    if 'error' in info:
                        print(f"     ⚠️  Errore: {info['error']}")

            print("="*60)

        # Verifica finale
        from sqlalchemy import select, func
        from app.models.bando import Bando, BandoStatus

        total_result = await db.execute(select(func.count(Bando.id)))
        total = total_result.scalar()

        attivi_result = await db.execute(
            select(func.count(Bando.id)).where(Bando.status == BandoStatus.ATTIVO)
        )
        attivi = attivi_result.scalar()

        print(f"\n📊 DATABASE FINALE:")
        print(f"   Totale bandi: {total}")
        print(f"   Bandi attivi: {attivi}")

        if total > 0:
            print("\n✅ DATABASE POPOLATO CON SUCCESSO!")
        else:
            print("\n⚠️  Nessun bando trovato. Possibili cause:")
            print("   - Siti non raggiungibili")
            print("   - Struttura HTML dei siti cambiata")
            print("   - Nessun bando corrisponde alle keywords")
    finally:
        if db:
            await db.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  RECUPERO BANDI REALI - ISS Platform")
    print("="*60 + "\n")

    asyncio.run(fetch_real_bandi())
