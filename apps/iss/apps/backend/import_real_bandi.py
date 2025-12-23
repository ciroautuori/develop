"""
Import BANDI REALI verificati manualmente
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from datetime import datetime
from app.database.database import get_db, engine, Base
from app.models.bando import Bando, BandoSource, BandoStatus
import hashlib

async def create_tables():
    """Crea tabelle"""
    from app.models.bando import Bando
    from app.models.bando_config import BandoConfig, BandoLog
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tabelle create!")

def gen_hash(title: str, ente: str, link: str) -> str:
    return hashlib.md5(f"{title}_{ente}_{link}".encode()).hexdigest()

async def import_bandi():
    """Import bandi reali"""
    
    await create_tables()
    
    # BANDI REALI VERIFICATI
    bandi_reali = [
        {
            "title": "Bando 2025 per la valorizzazione dei beni confiscati alle mafie",
            "ente": "Fondazione Con il Sud",
            "scadenza": datetime(2025, 9, 30),
            "scadenza_raw": "30/09/2025",
            "link": "https://granter.it/bandi/bando-2025-per-la-valorizzazione-dei-beni-confiscati-alle-mafie/",
            "descrizione": "Bando per progetti di valorizzazione sociale ed economica di beni confiscati alle mafie nel Sud Italia, con focus su Campania.",
            "fonte": BandoSource.FONDAZIONE_COMUNITA,
            "status": BandoStatus.ATTIVO,
            "categoria": "sociale",
            "importo": "Da definire",
            "keyword_match": "sociale, territorio, campania"
        },
        {
            "title": "Servizi di Consulenza per il Non Profit",
            "ente": "Fondazione Charlemagne",
            "scadenza": None,
            "scadenza_raw": "Sempre attivo",
            "link": "https://granter.it/opportunita/servizi-di-consulenza-per-il-non-profit/",
            "descrizione": "Donazione di servizi di consulenza gratuita per enti del terzo settore in Campania: consulenza legale, fiscale, gestionale e strategica.",
            "fonte": BandoSource.FONDAZIONE_COMUNITA,
            "status": BandoStatus.ATTIVO,
            "categoria": "formazione",
            "importo": "Servizi gratuiti",
            "keyword_match": "terzo settore, formazione, consulenza"
        },
        {
            "title": "Iniziative in cofinanziamento - Fondazione Con il Sud",
            "ente": "Fondazione Con il Sud",
            "scadenza": None,
            "scadenza_raw": "Sempre attivo",
            "link": "https://granter.it/opportunita/iniziative-in-cofinanziamento-fondazione-con-il-sud/",
            "descrizione": "Opportunità di cofinanziamento per progetti in rete nel Mezzogiorno. La Fondazione valuta proposte innovative di partenariato tra enti del terzo settore.",
            "fonte": BandoSource.FONDAZIONE_COMUNITA,
            "status": BandoStatus.ATTIVO,
            "categoria": "sociale",
            "importo": "Variabile",
            "keyword_match": "cofinanziamento, rete, partenariato, sud"
        },
    ]
    
    db = None
    try:
        async for session in get_db():
            db = session
            break
        
        count = 0
        for bando_data in bandi_reali:
            hash_id = gen_hash(
                bando_data["title"],
                bando_data["ente"],
                bando_data["link"]
            )
            
            bando = Bando(
                title=bando_data["title"],
                ente=bando_data["ente"],
                scadenza=bando_data["scadenza"],
                scadenza_raw=bando_data["scadenza_raw"],
                link=bando_data["link"],
                descrizione=bando_data["descrizione"],
                fonte=bando_data["fonte"],
                status=bando_data["status"],
                categoria=bando_data["categoria"],
                importo=bando_data["importo"],
                keyword_match=bando_data["keyword_match"],
                hash_identifier=hash_id
            )
            
            db.add(bando)
            count += 1
        
        await db.commit()
        
        print(f"\n✅ Importati {count} bandi REALI!")
        
        # Verifica
        from sqlalchemy import select, func
        result = await db.execute(select(func.count(Bando.id)))
        total = result.scalar()
        
        print(f"📊 Totale bandi nel database: {total}")
        
        # Mostra bandi
        result = await db.execute(select(Bando).limit(5))
        bandi = result.scalars().all()
        
        print("\n📋 BANDI IMPORTATI:")
        for b in bandi:
            print(f"  • {b.title}")
            print(f"    Ente: {b.ente}")
            print(f"    Scadenza: {b.scadenza_raw}")
            print(f"    Link: {b.link}\n")
        
    finally:
        if db:
            await db.close()

if __name__ == "__main__":
    print("="*60)
    print("  IMPORT BANDI REALI - ISS Platform")
    print("="*60 + "\n")
    asyncio.run(import_bandi())
