"""
Schemas Pydantic per il modello Progetto
"""

from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class ProgettoStato(str, Enum):
    PIANIFICATO = "pianificato"
    IN_CORSO = "in_corso"
    COMPLETATO = "completato"
    SOSPESO = "sospeso"
    ANNULLATO = "annullato"


class ProgettoCategoria(str, Enum):
    DIGITALE = "digitale"
    SOCIALE = "sociale"
    EDUCATIVO = "educativo"
    AMBIENTALE = "ambientale"
    CULTURALE = "culturale"
    SANITARIO = "sanitario"
    RICERCA = "ricerca"


class ProgettoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    descrizione_breve: Optional[str] = Field(None, max_length=500)
    descrizione: Optional[str] = None
    categoria: ProgettoCategoria
    obiettivi: Optional[str] = None
    budget_totale: Optional[float] = Field(None, ge=0)
    budget_utilizzato: Optional[float] = Field(None, ge=0)
    data_inizio: date
    data_fine_prevista: Optional[date] = None
    data_fine_effettiva: Optional[date] = None
    responsabile_progetto: Optional[str] = Field(None, max_length=200)
    partner_coinvolti: Optional[str] = None
    beneficiari_target: Optional[str] = None
    impatto_sociale: Optional[str] = None
    immagine_copertina: Optional[str] = None
    sito_web: Optional[str] = None
    repository_codice: Optional[str] = None


class ProgettoCreate(ProgettoBase):
    """Schema per la creazione di un progetto"""
    pass


class ProgettoUpdate(BaseModel):
    """Schema per l'aggiornamento di un progetto"""
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descrizione_breve: Optional[str] = Field(None, max_length=500)
    descrizione: Optional[str] = None
    categoria: Optional[ProgettoCategoria] = None
    obiettivi: Optional[str] = None
    budget_totale: Optional[float] = Field(None, ge=0)
    budget_utilizzato: Optional[float] = Field(None, ge=0)
    data_inizio: Optional[date] = None
    data_fine_prevista: Optional[date] = None
    data_fine_effettiva: Optional[date] = None
    responsabile_progetto: Optional[str] = Field(None, max_length=200)
    partner_coinvolti: Optional[str] = None
    beneficiari_target: Optional[str] = None
    impatto_sociale: Optional[str] = None
    immagine_copertina: Optional[str] = None
    sito_web: Optional[str] = None
    repository_codice: Optional[str] = None
    stato: Optional[ProgettoStato] = None
    pubblicato: Optional[bool] = None


class ProgettoResponse(ProgettoBase):
    """Schema per la risposta di un progetto"""
    id: int
    slug: str
    stato: ProgettoStato
    pubblicato: bool
    percentuale_completamento: Optional[float] = None
    numero_team_members: int = 0
    numero_aggiornamenti: int = 0
    in_evidenza: bool = False
    archiviato: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    creato_da_user_id: Optional[int] = None

    class Config:
        from_attributes = True


class ProgettoListResponse(BaseModel):
    """Schema per la lista paginata di progetti"""
    progetti: List[ProgettoResponse]
    total: int
    skip: int
    limit: int


# Team Member Schemas
class ProgettoTeamMemberCreate(BaseModel):
    """Schema per la creazione di un membro del team"""
    user_id: int
    ruolo: str = Field(..., max_length=100)
    descrizione_ruolo: Optional[str] = None


class ProgettoTeamMemberResponse(BaseModel):
    """Schema per la risposta di un membro del team"""
    id: int
    user_id: int
    ruolo: str
    descrizione_ruolo: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Aggiornamento Schemas
class ProgettoAggiornamentoCreate(BaseModel):
    """Schema per la creazione di un aggiornamento progetto"""
    titolo: str = Field(..., max_length=200)
    contenuto: str
    tipo: Optional[str] = Field(None, max_length=50)


class ProgettoAggiornamentoResponse(BaseModel):
    """Schema per la risposta di un aggiornamento"""
    id: int
    titolo: str
    contenuto: str
    tipo: Optional[str] = None
    created_at: datetime
    creato_da_user_id: Optional[int] = None

    class Config:
        from_attributes = True


# Documento Schemas
class ProgettoDocumentoCreate(BaseModel):
    """Schema per la creazione di un documento"""
    nome: str = Field(..., max_length=200)
    descrizione: Optional[str] = None
    file_path: str
    tipo_file: Optional[str] = Field(None, max_length=50)


class ProgettoDocumentoResponse(BaseModel):
    """Schema per la risposta di un documento"""
    id: int
    nome: str
    descrizione: Optional[str] = None
    file_path: str
    tipo_file: Optional[str] = None
    dimensione_file: Optional[int] = None
    created_at: datetime
    caricato_da_user_id: Optional[int] = None

    class Config:
        from_attributes = True


# Stats Schemas
class ProgettoStatsResponse(BaseModel):
    """Schema per le statistiche dei progetti"""
    totale_progetti: int
    progetti_attivi: int
    progetti_completati: int
    budget_totale: float
    budget_utilizzato: float


# Search Filters
class ProgettoSearchFilters(BaseModel):
    """Schema per i filtri di ricerca"""
    categoria: Optional[str] = None
    stato: Optional[str] = None
    search: Optional[str] = None
    data_inizio_da: Optional[date] = None
    data_inizio_a: Optional[date] = None
