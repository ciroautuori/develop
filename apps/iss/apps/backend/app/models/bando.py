from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database.database import Base


class BandoStatus(enum.Enum):
    """Stati possibili di un bando"""
    ATTIVO = "attivo"
    SCADUTO = "scaduto"
    ARCHIVIATO = "archiviato"


class BandoSource(enum.Enum):
    """Fonti dei bandi"""
    COMUNE_SALERNO = "comune_salerno"
    REGIONE_CAMPANIA = "regione_campania"
    CSV_SALERNO = "csv_salerno"
    FONDAZIONE_COMUNITA = "fondazione_comunita"
    INVITALIA = "invitalia"
    MINISTERO_LAVORO = "ministero_lavoro"
    PNRR_ITALIA_DOMANI = "pnrr_italia_domani"
    AGENZIA_COESIONE = "agenzia_coesione"
    TERZO_SETTORE = "terzo_settore"
    ALTRO = "altro"


class Bando(Base):
    """Modello per i bandi trovati dal sistema di monitoraggio"""
    __tablename__ = "bandi"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    ente = Column(String(200), nullable=False)
    scadenza = Column(DateTime, nullable=True)
    scadenza_raw = Column(String(100), nullable=True)  # Testo originale della scadenza
    link = Column(Text, nullable=False)
    descrizione = Column(Text, nullable=True)
    fonte = Column(Enum(BandoSource, values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    status = Column(Enum(BandoStatus, values_callable=lambda x: [e.value for e in x]), default=BandoStatus.ATTIVO, nullable=False, index=True)

    # Metadati per il monitoraggio
    hash_identifier = Column(String(32), unique=True, nullable=False, index=True)  # MD5 hash per deduplicazione
    data_trovato = Column(DateTime(timezone=True), server_default=func.now())
    data_aggiornamento = Column(DateTime(timezone=True), onupdate=func.now())

    # Flags di processo
    notificato_email = Column(Boolean, default=False)
    notificato_telegram = Column(Boolean, default=False)
    keyword_match = Column(Text, nullable=True)  # Parole chiave che hanno matchato

    # Dati aggiuntivi strutturati
    importo = Column(String(100), nullable=True)
    categoria = Column(String(100), nullable=True)

    # AI Analysis Persistence
    ai_score = Column(Integer, nullable=True, index=True)
    ai_reasoning = Column(Text, nullable=True)
    deep_analysis = Column(JSON, nullable=True) # Strategic report from Agent Analyst

    # Relazioni con sistema utenti
    applications = relationship("BandoApplication", back_populates="bando")
    watchlists = relationship("BandoWatchlist", back_populates="bando")
    ai_recommendations = relationship("AIRecommendation", back_populates="bando")

    def __repr__(self):
        return f"<Bando(id={self.id}, title='{self.title}', ente='{self.ente}', fonte='{self.fonte}')>"
