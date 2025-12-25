"""
Courses Domain Models - Corso Tool AI StudiocentOS.
Dynamic courses management with multilingual support.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import String, Text, Integer, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.session import Base


class CourseStatus(str, Enum):
    """Status del corso."""
    ACTIVE = "active"
    DRAFT = "draft"
    ARCHIVED = "archived"


class CourseDifficulty(str, Enum):
    """Livello difficoltà corso."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Course(Base):
    """
    Corsi - Corso Tool AI StudiocentOS.

    Rappresenta i moduli del Corso Tool AI da mostrare nel portfolio.
    Supporta traduzioni multilingua (it, en, es) tramite campi JSON.
    """
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Info base (default italiano)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(50), nullable=False)  # emoji o icon name
    module_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-7 ordering

    # Traduzioni multilingua - JSON con chiavi "en", "es"
    # Formato: {"en": {"title": "...", "description": "..."}, "es": {...}}
    translations: Mapped[dict] = mapped_column(JSON, default=dict)

    # Links
    purchase_url: Mapped[str] = mapped_column(String(500), nullable=False)  # Gumroad/Stripe
    preview_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Metadata corso
    duration_hours: Mapped[Optional[int]] = mapped_column(Integer)
    difficulty: Mapped[str] = mapped_column(
        String(50),
        default=CourseDifficulty.BEGINNER.value
    )
    topics: Mapped[List[str]] = mapped_column(JSON, default=list)
    # Esempio: ["AI Tools", "Prompt Engineering", "Automazione"]

    # Pricing (opzionale, mostrato pubblicamente)
    price: Mapped[Optional[str]] = mapped_column(String(50))  # "€49", "Gratuito"
    
    # Status e visibilità
    status: Mapped[str] = mapped_column(
        String(50),
        default=CourseStatus.ACTIVE.value
    )
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_new: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    order: Mapped[int] = mapped_column(Integer, default=0)

    # Media
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))
    cover_image: Mapped[Optional[str]] = mapped_column(String(500))

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
