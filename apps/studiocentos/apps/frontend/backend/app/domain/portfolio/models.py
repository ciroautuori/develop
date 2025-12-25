"""
Portfolio Domain Models - Prodotti e Servizi StudiocentOS.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import String, Text, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.session import Base


class ProjectStatus(str, Enum):
    """Status del progetto."""
    ACTIVE = "active"
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    ARCHIVED = "archived"


class ServiceCategory(str, Enum):
    """Categorie servizi."""
    FRAMEWORK = "framework"
    AI_TOOLS = "ai_tools"
    COMPONENTS = "components"
    CUSTOM_DEV = "custom_dev"
    MOBILE = "mobile"
    AI_INTEGRATION = "ai_integration"


class Project(Base):
    """
    Prodotti realizzati - Portfolio StudiocentOS.

    Rappresenta i progetti completati da mostrare nel portfolio.
    Supporta traduzioni multilingua (it, en, es) tramite campi JSON.
    """
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Info base (default italiano)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)

    # Traduzioni multilingua - JSON con chiavi "en", "es"
    # Formato: {"en": {"title": "...", "description": "..."}, "es": {...}}
    translations: Mapped[dict] = mapped_column(JSON, default=dict)

    # URLs e links
    live_url: Mapped[Optional[str]] = mapped_column(String(500))
    github_url: Mapped[Optional[str]] = mapped_column(String(500))
    demo_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Tech stack
    technologies: Mapped[List[str]] = mapped_column(JSON, default=list)

    # Metriche
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    # Esempio: {"files": 850, "domains": 11, "time_to_market": "45gg"}

    # Status e visibilità
    status: Mapped[str] = mapped_column(
        String(50),
        default=ProjectStatus.ACTIVE.value
    )
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    order: Mapped[int] = mapped_column(Integer, default=0)

    # Media
    cover_image: Mapped[Optional[str]] = mapped_column(String(500))  # Main project image
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))
    images: Mapped[List[str]] = mapped_column(JSON, default=list)

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

    # Relationships - RIMOSSO PER EVITARE ERRORI CIRCOLARI
    # expenses = relationship("CompanyExpense", back_populates="project", lazy="dynamic")

    # Testimonials relationship (Phase 2: requires ProjectTestimonial model)
    # testimonials: Mapped[List["ProjectTestimonial"]] = relationship(
    #     "ProjectTestimonial",
    #     back_populates="project",
    #     cascade="all, delete-orphan"
    # )


class Service(Base):
    """
    Servizi offerti - StudiocentOS Services.

    Rappresenta i servizi e prodotti che offriamo.
    Supporta traduzioni multilingua (it, en, es) tramite campi JSON.
    """
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Info base (default italiano)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(50), nullable=False)  # emoji o icon name

    # Traduzioni multilingua - JSON con chiavi "en", "es"
    # Formato: {"en": {"title": "...", "description": "...", "features": [...], "cta_text": "..."}, "es": {...}}
    translations: Mapped[dict] = mapped_column(JSON, default=dict)

    # Thumbnail image
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Categoria
    category: Mapped[str] = mapped_column(
        String(50),
        default=ServiceCategory.CUSTOM_DEV.value
    )

    # Features e benefits
    features: Mapped[List[str]] = mapped_column(JSON, default=list)
    benefits: Mapped[List[str]] = mapped_column(JSON, default=list)

    # Pricing info (opzionale, non mostrato pubblicamente)
    value_indicator: Mapped[Optional[str]] = mapped_column(String(100))
    # Esempio: "€100K valore codice", "-90% dev time"

    # CTA
    cta_text: Mapped[str] = mapped_column(String(100), default="Scopri di più →")
    cta_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Visibilità e ordine
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    order: Mapped[int] = mapped_column(Integer, default=0)

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


class ProjectTestimonial(Base):
    """
    Testimonial per progetti.
    """
    __tablename__ = "project_testimonials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE")
    )

    # Info testimonial
    author_name: Mapped[str] = mapped_column(String(200), nullable=False)
    author_role: Mapped[str] = mapped_column(String(200), nullable=False)
    author_company: Mapped[Optional[str]] = mapped_column(String(200))
    author_avatar: Mapped[Optional[str]] = mapped_column(String(500))

    # Contenuto
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, default=5)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships (Phase 2: Enable with Project.testimonials)
    # project: Mapped["Project"] = relationship(
    #     "Project",
    #     back_populates="testimonials"
    # )


class ContactRequest(Base):
    """
    Richieste di contatto dal sito.
    """
    __tablename__ = "contact_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Info contatto
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    company: Mapped[Optional[str]] = mapped_column(String(200))
    phone: Mapped[Optional[str]] = mapped_column(String(50))

    # Messaggio
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Tipo richiesta
    request_type: Mapped[str] = mapped_column(
        String(50),
        default="general"
    )  # general, quote, support, partnership

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        default="new"
    )  # new, read, replied, closed

    # Metadata
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    referrer: Mapped[Optional[str]] = mapped_column(String(500))

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    replied_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
