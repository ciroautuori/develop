"""
Portfolio Domain Schemas - Pydantic models.
Supporta traduzioni multilingua (it, en, es).
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr

from .models import ProjectStatus, ServiceCategory


# ============================================================================
# TRANSLATION SCHEMAS
# ============================================================================

class TranslationContent(BaseModel):
    """Schema per contenuti tradotti."""
    title: Optional[str] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    cta_text: Optional[str] = None


class Translations(BaseModel):
    """Schema per tutte le traduzioni."""
    en: Optional[TranslationContent] = None
    es: Optional[TranslationContent] = None


# ============================================================================
# PROJECT SCHEMAS
# ============================================================================

class ProjectBase(BaseModel):
    """Base project schema."""
    title: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)
    description: str
    year: int = Field(..., ge=2020, le=2030)
    category: str = Field(..., max_length=100)
    live_url: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default=ProjectStatus.ACTIVE.value)
    is_featured: bool = False
    is_public: bool = True
    order: int = 0
    thumbnail_url: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    # Traduzioni multilingua
    translations: Dict[str, Any] = Field(default_factory=dict)


class ProjectCreate(ProjectBase):
    """Schema for creating project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating project."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    year: Optional[int] = Field(None, ge=2020, le=2030)
    category: Optional[str] = Field(None, max_length=100)
    live_url: Optional[str] = None
    github_url: Optional[str] = None
    technologies: Optional[List[str]] = None
    metrics: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    is_public: Optional[bool] = None
    order: Optional[int] = None
    translations: Optional[Dict[str, Any]] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectLocalizedResponse(BaseModel):
    """Schema per progetto con contenuto localizzato."""
    id: int
    title: str
    slug: str
    description: str
    year: int
    category: str
    live_url: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    technologies: List[str] = []
    metrics: Dict[str, Any] = {}
    status: str
    is_featured: bool
    is_public: bool
    order: int
    thumbnail_url: Optional[str] = None
    images: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SERVICE SCHEMAS
# ============================================================================

class ServiceBase(BaseModel):
    """Base service schema."""
    title: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)
    description: str
    icon: str = Field(..., max_length=50)
    category: str = Field(default=ServiceCategory.CUSTOM_DEV.value)
    features: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    value_indicator: Optional[str] = Field(None, max_length=100)
    cta_text: str = Field(default="Scopri di più →", max_length=100)
    cta_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_active: bool = True
    is_featured: bool = False
    order: int = 0
    # Traduzioni multilingua
    translations: Dict[str, Any] = Field(default_factory=dict)


class ServiceCreate(ServiceBase):
    """Schema for creating service."""
    pass


class ServiceUpdate(BaseModel):
    """Schema for updating service."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = None
    features: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    value_indicator: Optional[str] = None
    cta_text: Optional[str] = None
    cta_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    order: Optional[int] = None
    translations: Optional[Dict[str, Any]] = None


class ServiceResponse(ServiceBase):
    """Schema for service response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceLocalizedResponse(BaseModel):
    """Schema per servizio con contenuto localizzato."""
    id: int
    title: str
    slug: str
    description: str
    icon: str
    category: str
    features: List[str] = []
    benefits: List[str] = []
    value_indicator: Optional[str] = None
    cta_text: str
    cta_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_active: bool
    is_featured: bool
    order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CONTACT SCHEMAS
# ============================================================================

class ContactRequestCreate(BaseModel):
    """Schema for creating contact request."""
    name: str = Field(..., max_length=200)
    email: EmailStr
    company: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    subject: str = Field(..., max_length=200)
    message: str = Field(..., min_length=10)
    request_type: str = Field(default="general")


class ContactRequestResponse(BaseModel):
    """Schema for contact request response."""
    id: int
    name: str
    email: str
    company: Optional[str]
    subject: str
    message: str
    request_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# PUBLIC PORTFOLIO SCHEMAS
# ============================================================================

class PortfolioPublicResponse(BaseModel):
    """Schema for public portfolio page."""
    projects: List[ProjectResponse]
    services: List[ServiceResponse]
    stats: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True
