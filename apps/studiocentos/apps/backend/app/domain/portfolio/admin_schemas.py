"""
Portfolio Admin Schemas - CRUD operations
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# PROJECT SCHEMAS
# ============================================================================

class ProjectCreateRequest(BaseModel):
    """Schema per creazione progetto."""
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    year: int = Field(..., ge=2000, le=2100)
    category: str = Field(..., min_length=1, max_length=100)
    
    live_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    demo_url: Optional[str] = Field(None, max_length=500)
    
    technologies: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    
    status: str = Field(default="active")
    is_featured: bool = Field(default=False)
    is_public: bool = Field(default=True)
    order: int = Field(default=0)
    
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    images: List[str] = Field(default_factory=list)
    
    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug deve contenere solo lettere, numeri, - e _')
        return v.lower()


class ProjectUpdateRequest(BaseModel):
    """Schema per aggiornamento progetto."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    year: Optional[int] = Field(None, ge=2000, le=2100)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    
    live_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    demo_url: Optional[str] = Field(None, max_length=500)
    
    technologies: Optional[List[str]] = None
    metrics: Optional[Dict[str, Any]] = None
    
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    is_public: Optional[bool] = None
    order: Optional[int] = None
    
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    images: Optional[List[str]] = None


class ProjectResponse(BaseModel):
    """Schema response progetto."""
    id: int
    title: str
    slug: str
    description: str
    year: int
    category: str
    
    live_url: Optional[str]
    github_url: Optional[str]
    demo_url: Optional[str]
    
    technologies: List[str]
    metrics: Dict[str, Any]
    
    status: str
    is_featured: bool
    is_public: bool
    order: int
    
    thumbnail_url: Optional[str]
    images: List[str]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema lista progetti con paginazione."""
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# SERVICE SCHEMAS
# ============================================================================

class ServiceCreateRequest(BaseModel):
    """Schema per creazione servizio."""
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    icon: str = Field(..., min_length=1, max_length=50)
    
    category: str = Field(default="custom_dev")
    
    features: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    
    value_indicator: Optional[str] = Field(None, max_length=100)
    cta_text: str = Field(default="Scopri di più →", max_length=100)
    cta_url: Optional[str] = Field(None, max_length=500)
    
    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False)
    order: int = Field(default=0)
    
    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug deve contenere solo lettere, numeri, - e _')
        return v.lower()


class ServiceUpdateRequest(BaseModel):
    """Schema per aggiornamento servizio."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    icon: Optional[str] = Field(None, min_length=1, max_length=50)
    
    category: Optional[str] = None
    
    features: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    
    value_indicator: Optional[str] = Field(None, max_length=100)
    cta_text: Optional[str] = Field(None, max_length=100)
    cta_url: Optional[str] = Field(None, max_length=500)
    
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    order: Optional[int] = None


class ServiceResponse(BaseModel):
    """Schema response servizio."""
    id: int
    title: str
    slug: str
    description: str
    icon: str
    
    category: str
    
    features: List[str]
    benefits: List[str]
    
    value_indicator: Optional[str]
    cta_text: str
    cta_url: Optional[str]
    
    is_active: bool
    is_featured: bool
    order: int
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ServiceListResponse(BaseModel):
    """Schema lista servizi con paginazione."""
    items: List[ServiceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# BULK OPERATIONS
# ============================================================================

class BulkOrderUpdate(BaseModel):
    """Schema per aggiornamento ordine multiplo."""
    items: List[Dict[str, int]] = Field(..., description="Lista {id: order}")


class BulkDeleteRequest(BaseModel):
    """Schema per eliminazione multipla."""
    ids: List[int] = Field(..., min_length=1)


class BulkToggleRequest(BaseModel):
    """Schema per toggle multiplo (featured, public, active)."""
    ids: List[int] = Field(..., min_length=1)
    field: str = Field(..., description="Campo da toggleare")
    value: bool = Field(..., description="Nuovo valore")
