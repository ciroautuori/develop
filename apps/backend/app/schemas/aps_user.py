"""
Schemi Pydantic per sistema utenti APS
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.aps_user import OrganizationType


# ========== BASE SCHEMAS ==========

class OrganizationTypeEnum(str, Enum):
    """Enum per tipi organizzazione"""
    APS = "aps"
    ODV = "odv"
    COOPERATIVA = "cooperativa"
    FONDAZIONE = "fondazione"
    ONG = "ong"
    IMPRESA_SOCIALE = "impresa_sociale"
    ALTRO = "altro"


class APSUserBase(BaseModel):
    """Base schema per utente APS"""
    organization_name: str = Field(..., min_length=2, max_length=200)
    organization_type: OrganizationTypeEnum = OrganizationTypeEnum.APS
    fiscal_code: str = Field(..., pattern=r"^[A-Z0-9]{11,16}$")
    vat_number: Optional[str] = Field(None, pattern=r"^[0-9]{11}$")
    
    contact_email: EmailStr
    contact_phone: Optional[str] = Field(None, pattern=r"^[+]?[0-9\s\-()]{8,20}$")
    website: Optional[str] = None
    
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = Field(None, min_length=2, max_length=2)
    postal_code: Optional[str] = Field(None, pattern=r"^[0-9]{5}$")
    region: str = "Campania"
    
    description: Optional[str] = None
    sectors: Optional[List[str]] = []
    target_groups: Optional[List[str]] = []
    keywords: Optional[List[str]] = []
    
    annual_budget_range: Optional[str] = None
    team_size: Optional[int] = Field(None, ge=1, le=1000)
    volunteer_count: Optional[int] = Field(None, ge=0, le=10000)
    
    max_budget_interest: Optional[float] = Field(None, ge=0)
    geographical_scope: str = "Campania"
    notification_preferences: Optional[Dict[str, Any]] = {}


class APSUserCreate(APSUserBase):
    """Schema per creazione utente APS"""
    
    @validator('sectors')
    def validate_sectors(cls, v):
        """Valida settori di interesse"""
        valid_sectors = [
            'sociale', 'cultura', 'ambiente', 'sport', 'formazione',
            'sanitario', 'ricerca', 'innovazione', 'digitale', 'turismo',
            'agricoltura', 'alimentare', 'energia', 'trasporti'
        ]
        if v:
            for sector in v:
                if sector not in valid_sectors:
                    raise ValueError(f'Settore non valido: {sector}')
        return v
    
    @validator('target_groups')
    def validate_target_groups(cls, v):
        """Valida gruppi target"""
        valid_groups = [
            'giovani', 'anziani', 'disabili', 'immigrati', 'donne',
            'minori', 'famiglie', 'comunità', 'studenti', 'lavoratori',
            'emarginati', 'tossicodipendenti', 'detenuti'
        ]
        if v:
            for group in v:
                if group not in valid_groups:
                    raise ValueError(f'Gruppo target non valido: {group}')
        return v


class APSUserUpdate(BaseModel):
    """Schema per aggiornamento utente APS"""
    organization_name: Optional[str] = Field(None, min_length=2, max_length=200)
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    description: Optional[str] = None
    sectors: Optional[List[str]] = None
    target_groups: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    annual_budget_range: Optional[str] = None
    team_size: Optional[int] = None
    volunteer_count: Optional[int] = None
    max_budget_interest: Optional[float] = None
    geographical_scope: Optional[str] = None
    notification_preferences: Optional[Dict[str, Any]] = None


class APSUserRead(APSUserBase):
    """Schema per lettura utente APS"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class APSUserPublic(BaseModel):
    """Schema pubblico utente APS (info minime)"""
    id: int
    organization_name: str
    organization_type: OrganizationTypeEnum
    city: Optional[str] = None
    region: str
    sectors: Optional[List[str]] = []
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


# ========== BANDO APPLICATIONS ==========

class BandoApplicationBase(BaseModel):
    """Base schema candidatura bando"""
    project_title: Optional[str] = None
    project_description: Optional[str] = None
    requested_amount: Optional[float] = Field(None, ge=0)
    documents_submitted: Optional[List[str]] = []
    internal_notes: Optional[str] = None


class BandoApplicationCreate(BandoApplicationBase):
    """Schema creazione candidatura"""
    bando_id: int


class BandoApplicationUpdate(BaseModel):
    """Schema aggiornamento candidatura"""
    status: Optional[str] = None
    project_title: Optional[str] = None
    project_description: Optional[str] = None
    requested_amount: Optional[float] = None
    documents_submitted: Optional[List[str]] = None
    internal_notes: Optional[str] = None
    feedback_received: Optional[str] = None


class BandoApplicationRead(BandoApplicationBase):
    """Schema lettura candidatura"""
    id: int
    aps_user_id: int
    bando_id: int
    status: str
    application_date: datetime
    last_update: datetime
    feedback_received: Optional[str] = None
    success_probability: Optional[float] = None
    
    # Relazioni
    bando: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


# ========== WATCHLIST ==========

class BandoWatchlistBase(BaseModel):
    """Base schema watchlist"""
    notes: Optional[str] = None
    priority: str = Field("medium", pattern="^(high|medium|low)$")


class BandoWatchlistCreate(BandoWatchlistBase):
    """Schema creazione watchlist"""
    bando_id: int


class BandoWatchlistUpdate(BandoWatchlistBase):
    """Schema aggiornamento watchlist"""
    pass


class BandoWatchlistRead(BandoWatchlistBase):
    """Schema lettura watchlist"""
    id: int
    aps_user_id: int
    bando_id: int
    added_date: datetime
    match_score: Optional[float] = None
    ai_insights: Optional[Dict[str, Any]] = None
    
    # Relazioni
    bando: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


# ========== AI RECOMMENDATIONS ==========

class AIRecommendationRead(BaseModel):
    """Schema lettura raccomandazione AI"""
    id: int
    bando_id: int
    recommendation_score: float
    reasoning: Optional[str] = None
    match_factors: Optional[Dict[str, Any]] = None
    created_at: datetime
    viewed: bool
    dismissed: bool
    applied: bool
    user_feedback: Optional[str] = None
    
    # Relazioni
    bando: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class AIRecommendationUpdate(BaseModel):
    """Schema aggiornamento raccomandazione"""  
    viewed: Optional[bool] = None
    dismissed: Optional[bool] = None
    applied: Optional[bool] = None
    user_feedback: Optional[str] = Field(None, pattern="^(positive|negative|neutral)$")
    feedback_reason: Optional[str] = None


# ========== DASHBOARD & STATS ==========

class UserDashboardStats(BaseModel):
    """Statistiche dashboard utente"""
    total_applications: int
    successful_applications: int
    pending_applications: int
    success_rate: float
    active_watchlist_count: int
    unviewed_recommendations_count: int
    upcoming_deadlines_count: int


class UserDashboard(BaseModel):
    """Dashboard completa utente"""
    user: APSUserRead
    stats: UserDashboardStats
    recent_applications: List[BandoApplicationRead]
    top_recommendations: List[AIRecommendationRead]
    upcoming_deadlines: List[Dict[str, Any]]


# ========== SEARCH & FILTERS ==========

class APSUserSearch(BaseModel):
    """Parametri ricerca utenti"""
    search: Optional[str] = None
    organization_type: Optional[OrganizationTypeEnum] = None
    region: Optional[str] = None
    sectors: Optional[List[str]] = None
    is_active: Optional[bool] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=200)


class APSUserSearchResponse(BaseModel):
    """Risposta ricerca utenti"""
    items: List[APSUserPublic]
    total: int
    skip: int
    limit: int
    has_more: bool
