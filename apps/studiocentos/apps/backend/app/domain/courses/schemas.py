"""
Courses Domain Schemas - Pydantic models for API.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CourseBase(BaseModel):
    """Base schema per Course."""
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: str
    icon: str = Field(..., max_length=50)
    module_number: int = Field(..., ge=1)
    purchase_url: str = Field(..., max_length=500)
    preview_url: Optional[str] = None
    duration_hours: Optional[int] = None
    difficulty: str = "beginner"
    topics: List[str] = []
    price: Optional[str] = None
    thumbnail_url: Optional[str] = None
    cover_image: Optional[str] = None


class CourseCreate(CourseBase):
    """Schema per creazione corso."""
    translations: Dict[str, Any] = {}
    status: str = "active"
    is_featured: bool = False
    is_new: bool = False
    is_public: bool = True
    order: int = 0


class CourseUpdate(BaseModel):
    """Schema per aggiornamento corso (tutti i campi opzionali)."""
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    module_number: Optional[int] = None
    purchase_url: Optional[str] = None
    preview_url: Optional[str] = None
    duration_hours: Optional[int] = None
    difficulty: Optional[str] = None
    topics: Optional[List[str]] = None
    price: Optional[str] = None
    translations: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    is_new: Optional[bool] = None
    is_public: Optional[bool] = None
    order: Optional[int] = None
    thumbnail_url: Optional[str] = None
    cover_image: Optional[str] = None


class CourseResponse(CourseBase):
    """Schema per risposta corso."""
    id: int
    translations: Dict[str, Any] = {}
    status: str
    is_featured: bool
    is_new: bool
    is_public: bool
    order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CourseLocalizedResponse(BaseModel):
    """Schema per risposta corso localizzata (public API)."""
    id: int
    title: str
    slug: str
    description: str
    icon: str
    module_number: int
    purchase_url: str
    preview_url: Optional[str] = None
    duration_hours: Optional[int] = None
    difficulty: str
    topics: List[str] = []
    price: Optional[str] = None
    is_featured: bool
    is_new: bool
    thumbnail_url: Optional[str] = None
    cover_image: Optional[str] = None


class CourseListResponse(BaseModel):
    """Schema per lista corsi paginata."""
    items: List[CourseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
