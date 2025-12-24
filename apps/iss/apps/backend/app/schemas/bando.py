from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List
from enum import Enum


class BandoStatusEnum(str, Enum):
    ATTIVO = "attivo"
    SCADUTO = "scaduto"
    ARCHIVIATO = "archiviato"


class BandoSourceEnum(str, Enum):
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


class BandoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    ente: str = Field(..., min_length=1, max_length=200)
    scadenza_raw: Optional[str] = Field(None, max_length=100)
    link: str = Field(..., min_length=1)
    descrizione: Optional[str] = None
    fonte: BandoSourceEnum
    importo: Optional[str] = Field(None, max_length=100)
    categoria: Optional[str] = Field(None, max_length=100)


class BandoCreate(BandoBase):
    """Schema per la creazione di un nuovo bando"""
    keyword_match: Optional[str] = None
    ai_score: Optional[int] = None
    ai_reasoning: Optional[str] = None


class BandoUpdate(BaseModel):
    """Schema per l'aggiornamento di un bando"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    ente: Optional[str] = Field(None, min_length=1, max_length=200)
    scadenza_raw: Optional[str] = Field(None, max_length=100)
    link: Optional[str] = Field(None, min_length=1)
    descrizione: Optional[str] = None
    status: Optional[BandoStatusEnum] = None
    importo: Optional[str] = Field(None, max_length=100)
    categoria: Optional[str] = Field(None, max_length=100)
    notificato_email: Optional[bool] = None
    notificato_telegram: Optional[bool] = None
    ai_score: Optional[int] = None
    ai_reasoning: Optional[str] = None


class BandoRead(BandoBase):
    """Schema per la lettura di un bando"""
    id: int
    status: BandoStatusEnum
    hash_identifier: str
    scadenza: Optional[datetime] = None
    data_trovato: datetime
    data_aggiornamento: Optional[datetime] = None
    notificato_email: bool
    notificato_telegram: bool
    keyword_match: Optional[str] = None
    ai_score: Optional[int] = None
    ai_reasoning: Optional[str] = None

    class Config:
        from_attributes = True


class BandoList(BaseModel):
    """Schema per la lista paginata di bandi"""
    items: List[BandoRead]
    total: int
    page: int
    size: int
    pages: int


class BandoSearch(BaseModel):
    """Schema per la ricerca bandi"""
    query: Optional[str] = None
    fonte: Optional[str] = None  # Cambiato da enum a string per flessibilità
    categoria: Optional[str] = None
    status: Optional[str] = None  # Cambiato da enum a string per flessibilità
    importo_min: Optional[float] = None
    importo_max: Optional[float] = None
    data_scadenza_da: Optional[str] = None
    data_scadenza_a: Optional[str] = None
    sort_by: Optional[str] = "relevance"
    sort_order: Optional[str] = "desc"
    keyword: Optional[str] = None
    # Campi legacy per compatibilità
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class TrendMensile(BaseModel):
    """Trend mensile per statistiche"""
    mese: str
    count: int
    importo: float


class BandoStats(BaseModel):
    """Statistiche sui bandi"""
    totali: int
    attivi: int
    scaduti: int
    in_scadenza: int
    importo_totale: float
    importo_medio: float
    nuovi_settimana: int
    fonti: dict[str, int]
    categorie: dict[str, int]
    trend_mensile: List[TrendMensile]

    # Campi legacy per compatibilità
    total_bandi: Optional[int] = None
    bandi_attivi: Optional[int] = None
    bandi_scaduti: Optional[int] = None
    bandi_per_fonte: Optional[dict] = None
    ultimi_trovati: Optional[int] = None
    media_giornaliera: Optional[float] = None
