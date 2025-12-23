"""
Schemas Pydantic per il modello Evento
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class EventoCategoria(str, Enum):
    WORKSHOP = "workshop"
    HACKATHON = "hackathon"
    CONFERENZA = "conferenza"
    WEBINAR = "webinar"
    NETWORKING = "networking"
    FORMAZIONE = "formazione"
    PRESENTAZIONE = "presentazione"


class EventoStato(str, Enum):
    BOZZA = "bozza"
    PUBBLICATO = "pubblicato"
    IN_CORSO = "in_corso"
    COMPLETATO = "completato"
    ANNULLATO = "annullato"


class EventoBase(BaseModel):
    titolo: str = Field(..., min_length=1, max_length=200)
    descrizione_breve: Optional[str] = Field(None, max_length=500)
    descrizione: Optional[str] = None
    categoria: EventoCategoria
    data_inizio: datetime
    data_fine: Optional[datetime] = None
    posti_disponibili: Optional[int] = Field(None, ge=1)
    prezzo: Optional[float] = Field(None, ge=0)
    gratuito: bool = True
    relatore: Optional[str] = Field(None, max_length=200)
    modalita_online: bool = False
    luogo: Optional[str] = Field(None, max_length=200)
    indirizzo: Optional[str] = Field(None, max_length=300)
    citta: str = Field(..., max_length=100)
    immagine_copertina: Optional[str] = None
    link_streaming: Optional[str] = None
    materiali_evento: Optional[str] = None


class EventoCreate(EventoBase):
    """Schema per la creazione di un evento"""
    pass


class EventoUpdate(BaseModel):
    """Schema per l'aggiornamento di un evento"""
    titolo: Optional[str] = Field(None, min_length=1, max_length=200)
    descrizione_breve: Optional[str] = Field(None, max_length=500)
    descrizione: Optional[str] = None
    categoria: Optional[EventoCategoria] = None
    data_inizio: Optional[datetime] = None
    data_fine: Optional[datetime] = None
    posti_disponibili: Optional[int] = Field(None, ge=1)
    prezzo: Optional[float] = Field(None, ge=0)
    gratuito: Optional[bool] = None
    relatore: Optional[str] = Field(None, max_length=200)
    modalita_online: Optional[bool] = None
    luogo: Optional[str] = Field(None, max_length=200)
    indirizzo: Optional[str] = Field(None, max_length=300)
    citta: Optional[str] = Field(None, max_length=100)
    immagine_copertina: Optional[str] = None
    link_streaming: Optional[str] = None
    materiali_evento: Optional[str] = None
    stato: Optional[EventoStato] = None
    pubblicato: Optional[bool] = None


class EventoResponse(EventoBase):
    """Schema per la risposta di un evento"""
    id: int
    slug: str
    stato: EventoStato
    pubblicato: bool
    numero_partecipanti: int
    in_evidenza: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    creato_da_user_id: Optional[int] = None

    class Config:
        from_attributes = True


class EventoListResponse(BaseModel):
    """Schema per la lista paginata di eventi"""
    eventi: List[EventoResponse]
    total: int
    skip: int
    limit: int


# ================================
# 📝 SCHEMI ISCRIZIONI EVENTI
# ================================

class EventoIscrizioneBase(BaseModel):
    """Schema base per iscrizione evento"""
    note: Optional[str] = None


class EventoIscrizioneCreate(EventoIscrizioneBase):
    """Schema per creare una nuova iscrizione evento"""
    pass


class EventoIscrizioneResponse(EventoIscrizioneBase):
    """Schema per la risposta di un'iscrizione evento"""
    id: int
    evento_id: int
    user_id: int
    data_iscrizione: datetime
    stato: str
    presente: bool = False
    data_checkin: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ================================
# 📊 SCHEMI STATISTICHE EVENTI
# ================================

class EventoStatsResponse(BaseModel):
    """Schema per le statistiche di un evento"""
    evento_id: int
    numero_iscritti: int
    numero_presenti: int
    tasso_partecipazione: float
    rating_medio: Optional[float] = None
    numero_recensioni: int


# ================================
# 📅 SCHEMI CALENDARIO EVENTI
# ================================

class EventoCalendarResponse(BaseModel):
    """Schema per evento nel calendario"""
    id: int
    titolo: str
    data_inizio: datetime
    data_fine: Optional[datetime] = None
    categoria: EventoCategoria
    colore: str = "#e74c3c"
    
    class Config:
        from_attributes = True


# ================================
# ✅ SCHEMI CHECK-IN EVENTI
# ================================

class EventoCheckInResponse(BaseModel):
    """Schema per la risposta di check-in evento"""
    id: int
    evento_id: int
    user_id: int
    data_checkin: datetime
    presente: bool = True
    note: Optional[str] = None
    
    class Config:
        from_attributes = True


# ================================
# 🌟 SCHEMI RECENSIONI EVENTI
# ================================

class EventoRecensioneBase(BaseModel):
    """Schema base per recensione evento"""
    voto: int = Field(..., ge=1, le=5)
    commento: Optional[str] = None


class EventoRecensioneCreate(EventoRecensioneBase):
    """Schema per creare una nuova recensione evento"""
    pass


class EventoRecensioneResponse(EventoRecensioneBase):
    """Schema per la risposta di una recensione evento"""
    id: int
    evento_id: int
    user_id: int
    data_recensione: datetime
    
    class Config:
        from_attributes = True
