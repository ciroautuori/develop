"""
Schemas Pydantic per il modello Corso
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class CorsoCategoria(str, Enum):
    DIGITALE_BASE = "digitale_base"
    WEB_DEVELOPMENT = "web_development"
    DATA_SCIENCE = "data_science"
    CYBERSECURITY = "cybersecurity"
    DIGITAL_MARKETING = "digital_marketing"
    DESIGN_GRAFICO = "design_grafico"
    IMPRENDITORIALITA = "imprenditorialita"


class CorsoLivello(str, Enum):
    PRINCIPIANTE = "principiante"
    INTERMEDIO = "intermedio"
    AVANZATO = "avanzato"


class CorsoStato(str, Enum):
    BOZZA = "bozza"
    PUBBLICATO = "pubblicato"
    IN_CORSO = "in_corso"
    COMPLETATO = "completato"
    ANNULLATO = "annullato"


class CorsoBase(BaseModel):
    titolo: str = Field(..., min_length=1, max_length=200)
    descrizione_breve: Optional[str] = Field(None, max_length=500)
    descrizione: Optional[str] = None
    categoria: CorsoCategoria
    livello: CorsoLivello
    durata_ore: Optional[int] = Field(None, ge=1)
    prezzo: Optional[float] = Field(None, ge=0)
    gratuito: bool = True
    data_inizio: datetime
    data_fine: Optional[datetime] = None
    posti_totali: int = Field(..., ge=1)
    docente: Optional[str] = Field(None, max_length=200)
    modalita_online: bool = False
    luogo: Optional[str] = Field(None, max_length=200)
    indirizzo: Optional[str] = Field(None, max_length=300)
    citta: str = Field(..., max_length=100)
    immagine_copertina: Optional[str] = None
    certificato_rilasciato: bool = True
    prerequisiti: Optional[str] = None
    obiettivi_apprendimento: Optional[str] = None
    materiali_inclusi: Optional[str] = None


class CorsoCreate(CorsoBase):
    """Schema per la creazione di un corso"""
    pass


class CorsoUpdate(BaseModel):
    """Schema per l'aggiornamento di un corso"""
    titolo: Optional[str] = Field(None, min_length=1, max_length=200)
    descrizione_breve: Optional[str] = Field(None, max_length=500)
    descrizione: Optional[str] = None
    categoria: Optional[CorsoCategoria] = None
    livello: Optional[CorsoLivello] = None
    durata_ore: Optional[int] = Field(None, ge=1)
    prezzo: Optional[float] = Field(None, ge=0)
    gratuito: Optional[bool] = None
    data_inizio: Optional[datetime] = None
    data_fine: Optional[datetime] = None
    posti_totali: Optional[int] = Field(None, ge=1)
    docente: Optional[str] = Field(None, max_length=200)
    modalita_online: Optional[bool] = None
    luogo: Optional[str] = Field(None, max_length=200)
    indirizzo: Optional[str] = Field(None, max_length=300)
    citta: Optional[str] = Field(None, max_length=100)
    immagine_copertina: Optional[str] = None
    certificato_rilasciato: Optional[bool] = None
    prerequisiti: Optional[str] = None
    obiettivi_apprendimento: Optional[str] = None
    materiali_inclusi: Optional[str] = None
    stato: Optional[CorsoStato] = None
    pubblicato: Optional[bool] = None


class CorsoResponse(CorsoBase):
    """Schema per la risposta di un corso"""
    id: int
    slug: str
    stato: CorsoStato
    pubblicato: bool
    posti_disponibili: int
    numero_iscritti: int
    rating_medio: Optional[float] = None
    numero_recensioni: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    creato_da_user_id: Optional[int] = None

    class Config:
        from_attributes = True


class CorsoListResponse(BaseModel):
    """Schema per la lista paginata di corsi"""
    corsi: List[CorsoResponse]
    total: int
    skip: int
    limit: int


class CorsoStatsResponse(BaseModel):
    """Schema per le statistiche di un corso"""
    corso_id: int
    numero_iscritti: int
    numero_completati: int
    tasso_completamento: float
    rating_medio: Optional[float] = None
    numero_recensioni: int
    ore_erogate: Optional[int] = None
    certificati_rilasciati: int


# ================================
# 📝 SCHEMI ISCRIZIONI
# ================================

class CorsoIscrizioneBase(BaseModel):
    """Schema base per iscrizione corso"""
    note: Optional[str] = None


class CorsoIscrizioneCreate(CorsoIscrizioneBase):
    """Schema per creare una nuova iscrizione"""
    pass


class CorsoIscrizioneResponse(CorsoIscrizioneBase):
    """Schema per la risposta di un'iscrizione"""
    id: int
    corso_id: int
    user_id: int
    data_iscrizione: datetime
    stato: str
    completato: bool = False
    voto_finale: Optional[int] = None
    data_completamento: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ================================
# 📚 SCHEMI LEZIONI
# ================================

class CorsoLezioneBase(BaseModel):
    """Schema base per lezione corso"""
    titolo: str
    descrizione: Optional[str] = None
    contenuto: Optional[str] = None
    ordine: int = 1
    durata_minuti: Optional[int] = None


class CorsoLezioneCreate(CorsoLezioneBase):
    """Schema per creare una nuova lezione"""
    pass


class CorsoLezioneResponse(CorsoLezioneBase):
    """Schema per la risposta di una lezione"""
    id: int
    corso_id: int
    slug: str
    pubblicata: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ================================
# 🌟 SCHEMI RECENSIONI
# ================================

class CorsoRecensioneBase(BaseModel):
    """Schema base per recensione corso"""
    voto: int = Field(..., ge=1, le=5)
    commento: Optional[str] = None


class CorsoRecensioneCreate(CorsoRecensioneBase):
    """Schema per creare una nuova recensione"""
    pass


class CorsoRecensioneResponse(CorsoRecensioneBase):
    """Schema per la risposta di una recensione"""
    id: int
    corso_id: int
    user_id: int
    data_recensione: datetime
    
    class Config:
        from_attributes = True
