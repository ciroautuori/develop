from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List, Dict


class BandoConfigBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    
    # Email configuration
    email_enabled: bool = True
    email_smtp_server: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_username: Optional[EmailStr] = None
    email_recipient: Optional[EmailStr] = None
    
    # Telegram configuration
    telegram_enabled: bool = False
    telegram_chat_id: Optional[str] = None
    
    # Keywords
    keywords: List[str] = Field(..., min_items=1)
    
    # Scraping settings
    scraping_delay: int = Field(2, ge=1, le=10)
    max_retries: int = Field(3, ge=1, le=5)
    timeout: int = Field(10, ge=5, le=30)
    
    # Scheduling
    schedule_enabled: bool = True
    schedule_interval_hours: int = Field(24, ge=1, le=168)  # Max 1 week
    
    # Filters
    min_deadline_days: int = Field(30, ge=0, le=365)
    fonte_enabled: Dict[str, bool] = Field(default_factory=lambda: {
        "comune_salerno": True,
        "regione_campania": True,
        "csv_salerno": True,
        "fondazione_comunita": True
    })


class BandoConfigCreate(BandoConfigBase):
    """Schema per la creazione di una configurazione"""
    email_password: Optional[str] = None  # Handled securely
    telegram_bot_token: Optional[str] = None  # Handled securely


class BandoConfigUpdate(BaseModel):
    """Schema per l'aggiornamento di una configurazione"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    
    # Email
    email_enabled: Optional[bool] = None
    email_smtp_server: Optional[str] = None
    email_smtp_port: Optional[int] = Field(None, ge=1, le=65535)
    email_username: Optional[EmailStr] = None
    email_password: Optional[str] = None
    email_recipient: Optional[EmailStr] = None
    
    # Telegram
    telegram_enabled: Optional[bool] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Keywords
    keywords: Optional[List[str]] = Field(None, min_items=1)
    
    # Scraping
    scraping_delay: Optional[int] = Field(None, ge=1, le=10)
    max_retries: Optional[int] = Field(None, ge=1, le=5)
    timeout: Optional[int] = Field(None, ge=5, le=30)
    
    # Scheduling
    is_active: Optional[bool] = None
    schedule_enabled: Optional[bool] = None
    schedule_interval_hours: Optional[int] = Field(None, ge=1, le=168)
    
    # Filters
    min_deadline_days: Optional[int] = Field(None, ge=0, le=365)
    fonte_enabled: Optional[Dict[str, bool]] = None


class BandoConfigRead(BandoConfigBase):
    """Schema per la lettura di una configurazione"""
    id: int
    is_active: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    
    # Security: exclude sensitive fields in read
    email_password: Optional[str] = Field(None, exclude=True)
    telegram_bot_token: Optional[str] = Field(None, exclude=True)

    class Config:
        from_attributes = True


class BandoLogBase(BaseModel):
    config_id: int
    bandi_found: int = 0
    bandi_new: int = 0
    errors_count: int = 0
    status: str = "running"
    error_message: Optional[str] = None


class BandoLogCreate(BandoLogBase):
    sources_processed: Optional[Dict[str, dict]] = None


class BandoLogRead(BandoLogBase):
    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    sources_processed: Optional[Dict[str, dict]] = None

    class Config:
        from_attributes = True


class BandoMonitorStatus(BaseModel):
    """Status del sistema di monitoraggio"""
    is_running: bool
    active_configs: int
    last_successful_run: Optional[datetime]
    total_bandi_found: int
    errors_last_24h: int
    next_scheduled_runs: List[Dict[str, datetime]]
