from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, Enum
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class SourceType(str, enum.Enum):
    """Tipi di fonte per i bandi"""
    COMUNE_SALERNO = "comune_salerno"
    REGIONE_CAMPANIA = "regione_campania"
    CSV_SALERNO = "csv_salerno"
    FONDAZIONE_COMUNITA = "fondazione_comunita"
    ALTRO = "altro"


class ScheduleFrequency(str, enum.Enum):
    """Frequenza di scheduling"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class BandoConfig(Base):
    """Configurazione per il sistema di monitoraggio bandi"""
    __tablename__ = "bando_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    
    # Configurazione email
    email_enabled = Column(Boolean, default=True)
    email_smtp_server = Column(String(100), default="smtp.gmail.com")
    email_smtp_port = Column(Integer, default=587)
    email_username = Column(String(200), nullable=True)
    email_password = Column(String(200), nullable=True)  # Criptata in produzione
    email_recipient = Column(String(200), nullable=True)
    
    # Configurazione Telegram
    telegram_enabled = Column(Boolean, default=False)
    telegram_bot_token = Column(String(200), nullable=True)
    telegram_chat_id = Column(String(50), nullable=True)
    
    # Keywords per il matching (JSON array)
    keywords = Column(JSON, nullable=False)
    
    # Configurazioni scraping
    scraping_delay = Column(Integer, default=2)  # secondi tra richieste
    max_retries = Column(Integer, default=3)
    timeout = Column(Integer, default=10)
    
    # Scheduling
    is_active = Column(Boolean, default=True)
    schedule_enabled = Column(Boolean, default=True)
    schedule_interval_hours = Column(Integer, default=24)
    last_run = Column(DateTime(timezone=True), nullable=True)
    next_run = Column(DateTime(timezone=True), nullable=True)
    
    # Filtri
    min_deadline_days = Column(Integer, default=30)  # Minimo giorni di preavviso
    fonte_enabled = Column(JSON, nullable=False)  # Quali fonti abilitare
    
    # Metadati
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, nullable=True)  # FK to admin user
    
    def __repr__(self):
        return f"<BandoConfig(id={self.id}, name='{self.name}', active={self.is_active})>"


class BandoLog(Base):
    """Log delle esecuzioni del monitoraggio"""
    __tablename__ = "bando_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, nullable=False)  # FK to BandoConfig
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Risultati
    bandi_found = Column(Integer, default=0)
    bandi_new = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    
    # Status
    status = Column(String(20), default="running")  # running, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Dettagli delle fonti
    sources_processed = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<BandoLog(id={self.id}, config_id={self.config_id}, status='{self.status}')>"
