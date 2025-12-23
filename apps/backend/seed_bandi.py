"""
Script per popolare il database con bandi di esempio
"""
import asyncio
from datetime import datetime, timedelta
from app.database.database import Base, engine, SessionLocal
from app.models.bando import Bando, BandoSource, BandoStatus
from app.models.bando_config import BandoConfig
import hashlib

async def create_tables():
    """Crea tutte le tabelle"""
    from app.models import *  # Import all models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tabelle create!")

def generate_hash(title: str, ente: str, link: str) -> str:
    """Genera hash univoco"""
    content = f"{title}_{ente}_{link}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()

async def seed_bandi():
    """Popola con bandi di esempio"""
    
    # Crea tabelle prima
    await create_tables()
    
    async with SessionLocal() as db:
        # Bandi di esempio
        bandi_esempio = [
            {
                "title": "Bando Cultura Digitale 2025 - Sostegno alla digitalizzazione delle APS",
                "ente": "Comune di Salerno",
                "scadenza": datetime.now() + timedelta(days=45),
                "scadenza_raw": (datetime.now() + timedelta(days=45)).strftime("%d/%m/%Y"),
                "link": "https://www.comune.salerno.it/bandi/cultura-digitale-2025",
                "descrizione": "Bando per sostenere progetti di digitalizzazione e innovazione tecnologica nelle associazioni di promozione sociale. Finanziamento fino a €50.000.",
                "fonte": BandoSource.COMUNE_SALERNO,
                "status": BandoStatus.ATTIVO,
                "categoria": "digitale",
                "importo": "€50.000",
                "keyword_match": "digitale, innovazione, aps"
            },
            {
                "title": "Finanziamenti per Progetti di Inclusione Sociale Giovanile",
                "ente": "Regione Campania",
                "scadenza": datetime.now() + timedelta(days=60),
                "scadenza_raw": (datetime.now() + timedelta(days=60)).strftime("%d/%m/%Y"),
                "link": "https://www.regione.campania.it/bandi/inclusione-giovani",
                "descrizione": "Sostegno a progetti di inclusione sociale rivolti a giovani NEET. Contributi da €30.000 a €100.000.",
                "fonte": BandoSource.REGIONE_CAMPANIA,
                "status": BandoStatus.ATTIVO,
                "categoria": "sociale",
                "importo": "€30.000 - €100.000",
                "keyword_match": "giovani, inclusione, sociale"
            },
            {
                "title": "Bando Formazione Digitale per il Terzo Settore",
                "ente": "CSV Salerno",
                "scadenza": datetime.now() + timedelta(days=30),
                "scadenza_raw": (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y"),
                "link": "https://www.csvsalerno.it/bandi/formazione-digitale",
                "descrizione": "Percorsi formativi gratuiti su competenze digitali per volontari e operatori del terzo settore.",
                "fonte": BandoSource.CSV_SALERNO,
                "status": BandoStatus.ATTIVO,
                "categoria": "formazione",
                "importo": "Gratuito",
                "keyword_match": "formazione, digitale, terzo settore"
            },
            {
                "title": "Avviso Pubblico Cultura e Ambiente 2025",
                "ente": "Comune di Salerno",
                "scadenza": datetime.now() + timedelta(days=90),
                "scadenza_raw": (datetime.now() + timedelta(days=90)).strftime("%d/%m/%Y"),
                "link": "https://www.comune.salerno.it/bandi/cultura-ambiente",
                "descrizione": "Sostegno a progetti culturali con focus su sostenibilità ambientale e valorizzazione del territorio.",
                "fonte": BandoSource.COMUNE_SALERNO,
                "status": BandoStatus.ATTIVO,
                "categoria": "cultura",
                "importo": "€75.000",
                "keyword_match": "cultura, ambiente, sostenibilità"
            },
            {
                "title": "Bando Sport e Inclusione - Attività Sportive per Disabili",
                "ente": "Regione Campania",
                "scadenza": datetime.now() + timedelta(days=75),
                "scadenza_raw": (datetime.now() + timedelta(days=75)).strftime("%d/%m/%Y"),
                "link": "https://www.regione.campania.it/bandi/sport-inclusione",
                "descrizione": "Finanziamenti per associazioni che promuovono attività sportive inclusive per persone con disabilità.",
                "fonte": BandoSource.REGIONE_CAMPANIA,
                "status": BandoStatus.ATTIVO,
                "categoria": "sport",
                "importo": "€40.000",
                "keyword_match": "sport, inclusione, disabilità"
            },
            {
                "title": "Bando Scaduto - Progetto Educazione 2024",
                "ente": "Comune di Salerno",
                "scadenza": datetime.now() - timedelta(days=10),
                "scadenza_raw": (datetime.now() - timedelta(days=10)).strftime("%d/%m/%Y"),
                "link": "https://www.comune.salerno.it/bandi/educazione-2024",
                "descrizione": "Bando chiuso per progetti educativi rivolti alle scuole.",
                "fonte": BandoSource.COMUNE_SALERNO,
                "status": BandoStatus.SCADUTO,
                "categoria": "educazione",
                "importo": "€25.000",
                "keyword_match": "educazione, scuole"
            }
        ]
        
        # Inserisci i bandi
        count = 0
        for bando_data in bandi_esempio:
            # Genera hash
            hash_id = generate_hash(
                bando_data["title"],
                bando_data["ente"],
                bando_data["link"]
            )
            
            # Crea oggetto Bando
            bando = Bando(
                **bando_data,
                hash_identifier=hash_id
            )
            
            db.add(bando)
            count += 1
        
        # Crea configurazione di esempio
        config = BandoConfig(
            name="Config Default ISS",
            email_enabled=True,
            email_smtp_server="smtp.gmail.com",
            email_smtp_port=587,
            telegram_enabled=False,
            keywords=["digitale", "innovazione", "giovani", "inclusione", "formazione", "cultura", "aps", "terzo settore"],
            scraping_delay=2,
            max_retries=3,
            timeout=10,
            is_active=True,
            schedule_enabled=True,
            schedule_interval_hours=24,
            min_deadline_days=30,
            fonte_enabled={
                "comune_salerno": True,
                "regione_campania": True,
                "csv_salerno": True
            }
        )
        
        db.add(config)
        
        await db.commit()
        
        print(f"✅ Inseriti {count} bandi di esempio!")
        print("✅ Creata 1 configurazione di monitoraggio!")
        
        # Verifica
        from sqlalchemy import select, func
        from app.models.bando import Bando
        
        result = await db.execute(select(func.count(Bando.id)))
        total = result.scalar()
        print(f"📊 Totale bandi nel database: {total}")

if __name__ == "__main__":
    asyncio.run(seed_bandi())
