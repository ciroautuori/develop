"""
Schemas Pydantic per il modello Volontariato
"""

from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class TipoImpegno(str, Enum):
    CONTINUATIVO = "continuativo"
    PROGETTO = "progetto"
    EVENTO = "evento"
    EMERGENZA = "emergenza"


class ModalitaVolontariato(str, Enum):
    PRESENZA = "presenza"
    REMOTO = "remoto"
    IBRIDO = "ibrido"


class StatoOpportunita(str, Enum):
    BOZZA = "bozza"
    PUBBLICATA = "pubblicata"
    SOSPESA = "sospesa"
    CHIUSA = "chiusa"


class OpportunitaVolontariatoBase(BaseModel):
    titolo: str = Field(..., min_length=1, max_length=200)
    descrizione_breve: Optional[str] = Field(None, max_length=500)
    descrizione: Optional[str] = None
    tipo_impegno: TipoImpegno
    modalita: ModalitaVolontariato
    ore_settimanali: Optional[int] = Field(None, ge=1, le=40)
    durata_mesi: Optional[int] = Field(None, ge=1)
    data_inizio: Optional[date] = None
    data_fine: Optional[date] = None
    luogo: Optional[str] = Field(None, max_length=200)
    citta: str = Field(..., max_length=100)
    skills_richieste: Optional[str] = None
    requisiti: Optional[str] = None
    benefici: Optional[str] = None
    contatto_referente: Optional[str] = Field(None, max_length=200)
    email_contatto: Optional[str] = Field(None, max_length=200)
    telefono_contatto: Optional[str] = Field(None, max_length=20)


class OpportunitaVolontariatoCreate(OpportunitaVolontariatoBase):
    """Schema per la creazione di un'opportunità di volontariato"""
    pass


class OpportunitaVolontariatoUpdate(BaseModel):
    """Schema per l'aggiornamento di un'opportunità di volontariato"""
    titolo: Optional[str] = Field(None, min_length=1, max_length=200)
    descrizione_breve: Optional[str] = Field(None, max_length=500)
    descrizione: Optional[str] = None
    tipo_impegno: Optional[TipoImpegno] = None
    modalita: Optional[ModalitaVolontariato] = None
    ore_settimanali: Optional[int] = Field(None, ge=1, le=40)
    durata_mesi: Optional[int] = Field(None, ge=1)
    data_inizio: Optional[date] = None
    data_fine: Optional[date] = None
    luogo: Optional[str] = Field(None, max_length=200)
    citta: Optional[str] = Field(None, max_length=100)
    skills_richieste: Optional[str] = None
    requisiti: Optional[str] = None
    benefici: Optional[str] = None
    contatto_referente: Optional[str] = Field(None, max_length=200)
    email_contatto: Optional[str] = Field(None, max_length=200)
    telefono_contatto: Optional[str] = Field(None, max_length=20)
    stato: Optional[StatoOpportunita] = None
    candidature_aperte: Optional[bool] = None


class OpportunitaVolontariatoResponse(OpportunitaVolontariatoBase):
    """Schema per la risposta di un'opportunità di volontariato"""
    id: int
    slug: str
    stato: StatoOpportunita
    candidature_aperte: bool = True
    numero_candidature: int = 0
    numero_volontari_attivi: int = 0
    in_evidenza: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    creato_da_user_id: Optional[int] = None

    class Config:
        from_attributes = True


class OpportunitaVolontariatoListResponse(BaseModel):
    """Schema per la lista paginata di opportunità di volontariato"""
    opportunita: List[OpportunitaVolontariatoResponse]
    total: int
    skip: int
    limit: int


# Candidatura Schemas
class StatoCandidatura(str, Enum):
    INVIATA = "inviata"
    IN_VALUTAZIONE = "in_valutazione"
    ACCETTATA = "accettata"
    RIFIUTATA = "rifiutata"
    RITIRATA = "ritirata"


class VolontariatoCandidaturaCreate(BaseModel):
    """Schema per la creazione di una candidatura"""
    opportunita_id: int
    motivazione: str
    disponibilita: Optional[str] = None
    esperienza_precedente: Optional[str] = None


class VolontariatoCandidaturaUpdate(BaseModel):
    """Schema per l'aggiornamento di una candidatura"""
    motivazione: Optional[str] = None
    disponibilita: Optional[str] = None
    esperienza_precedente: Optional[str] = None
    stato: Optional[StatoCandidatura] = None
    note_valutazione: Optional[str] = None


class VolontariatoCandidaturaResponse(BaseModel):
    """Schema per la risposta di una candidatura"""
    id: int
    opportunita_id: int
    user_id: int
    motivazione: str
    disponibilita: Optional[str] = None
    esperienza_precedente: Optional[str] = None
    stato: StatoCandidatura
    note_valutazione: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VolontariatoCandidaturaListResponse(BaseModel):
    """Schema per la lista paginata di candidature"""
    candidature: List[VolontariatoCandidaturaResponse]
    total: int
    skip: int
    limit: int


# Attività Schemas
class VolontariatoAttivitaCreate(BaseModel):
    """Schema per la creazione di un'attività di volontariato"""
    opportunita_id: int
    user_id: int
    data_attivita: date
    ore_svolte: float = Field(..., ge=0.5, le=24)
    descrizione: str
    note: Optional[str] = None


class VolontariatoAttivitaResponse(BaseModel):
    """Schema per la risposta di un'attività"""
    id: int
    opportunita_id: int
    user_id: int
    data_attivita: date
    ore_svolte: float
    descrizione: str
    note: Optional[str] = None
    validata: bool = False
    validata_da_user_id: Optional[int] = None
    data_validazione: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Certificato Schemas
class VolontariatoCertificatoResponse(BaseModel):
    """Schema per la risposta di un certificato"""
    id: int
    user_id: int
    opportunita_id: int
    numero_certificato: str
    data_emissione: date
    ore_totali: float
    descrizione_attivita: str
    file_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Skill Schemas
class VolontariatoSkillCreate(BaseModel):
    """Schema per la creazione di una skill"""
    nome: str = Field(..., max_length=100)
    descrizione: Optional[str] = None
    categoria: Optional[str] = Field(None, max_length=50)


class VolontariatoSkillResponse(BaseModel):
    """Schema per la risposta di una skill"""
    id: int
    nome: str
    descrizione: Optional[str] = None
    categoria: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Stats Schemas
class VolontariatoStatsResponse(BaseModel):
    """Schema per le statistiche del volontariato"""
    totale_opportunita: int
    opportunita_attive: int
    totale_candidature: int
    totale_volontari_attivi: int
    ore_totali_volontariato: float
    certificati_emessi: int


# Match Schemas
class VolontariatoMatchResponse(BaseModel):
    """Schema per il matching opportunità-volontario"""
    opportunita_id: int
    match_score: float = Field(..., ge=0, le=100)
    motivi_match: List[str]
    skills_corrispondenti: List[str]
