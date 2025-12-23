"""
Modelli per utenti APS e organizzazioni del terzo settore
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime
import enum
from typing import List, Optional

from app.database.database import Base


class OrganizationType(str, enum.Enum):
    """Tipi di organizzazione del terzo settore"""
    APS = "aps"  # Associazione di Promozione Sociale
    ODV = "odv"  # Organizzazione di Volontariato
    COOPERATIVA = "cooperativa"  # Cooperativa Sociale
    FONDAZIONE = "fondazione"  # Fondazione
    ONG = "ong"  # Organizzazione Non Governativa
    IMPRESA_SOCIALE = "impresa_sociale"  # Impresa Sociale
    ALTRO = "altro"


class APSUser(Base):
    """Utente registrato - Organizzazione del terzo settore"""
    __tablename__ = "aps_users"

    id = Column(Integer, primary_key=True, index=True)
    
    # Dati organizzazione
    organization_name = Column(String(200), nullable=False, index=True)
    organization_type = Column(SQLEnum(OrganizationType), nullable=False, default=OrganizationType.APS)
    fiscal_code = Column(String(16), unique=True, nullable=False, index=True)
    vat_number = Column(String(11), nullable=True)  # P.IVA se presente
    
    # Contatti
    contact_email = Column(String(255), unique=True, nullable=False, index=True)
    contact_phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Indirizzo
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    province = Column(String(2), nullable=True)  # Sigla provincia
    postal_code = Column(String(5), nullable=True)
    region = Column(String(50), nullable=True, default="Campania")
    
    # Profilo organizzazione
    description = Column(Text, nullable=True)
    sectors = Column(JSON, nullable=True)  # Lista settori di interesse
    target_groups = Column(JSON, nullable=True)  # Gruppi target
    keywords = Column(JSON, nullable=True)  # Keywords interesse
    
    # Budget e capacità
    annual_budget_range = Column(String(50), nullable=True)  # "0-10k", "10k-50k", etc.
    team_size = Column(Integer, nullable=True)
    volunteer_count = Column(Integer, nullable=True)
    
    # Preferenze ricerca
    max_budget_interest = Column(Float, nullable=True)  # Importo massimo bandi interesse
    geographical_scope = Column(String(100), nullable=True, default="Campania")  # Ambito geografico
    notification_preferences = Column(JSON, nullable=True)  # Preferenze notifiche
    
    # Sistema
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Email verificata
    last_login = Column(DateTime, nullable=True)
    
    # Relazioni
    applications = relationship("BandoApplication", back_populates="aps_user")
    watchlists = relationship("BandoWatchlist", back_populates="aps_user")
    ai_recommendations = relationship("AIRecommendation", back_populates="aps_user")


class BandoApplication(Base):
    """Candidatura a un bando"""
    __tablename__ = "bando_applications"

    id = Column(Integer, primary_key=True, index=True)
    
    # Riferimenti
    aps_user_id = Column(Integer, ForeignKey("aps_users.id"), nullable=False)
    bando_id = Column(Integer, ForeignKey("bandi.id"), nullable=False)
    
    # Stato candidatura
    status = Column(String(50), nullable=False, default="submitted")  # submitted, in_review, approved, rejected
    application_date = Column(DateTime, default=datetime.utcnow)
    last_update = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Dettagli candidatura
    project_title = Column(String(200), nullable=True)
    project_description = Column(Text, nullable=True)
    requested_amount = Column(Float, nullable=True)
    documents_submitted = Column(JSON, nullable=True)  # Lista documenti
    
    # Note e feedback
    internal_notes = Column(Text, nullable=True)
    feedback_received = Column(Text, nullable=True)
    success_probability = Column(Float, nullable=True)  # Score AI 0-1
    
    # Relazioni
    aps_user = relationship("APSUser", back_populates="applications")
    bando = relationship("Bando", back_populates="applications")


class BandoWatchlist(Base):
    """Lista bandi seguiti da un'organizzazione"""
    __tablename__ = "bando_watchlists"

    id = Column(Integer, primary_key=True, index=True)
    
    # Riferimenti
    aps_user_id = Column(Integer, ForeignKey("aps_users.id"), nullable=False)
    bando_id = Column(Integer, ForeignKey("bandi.id"), nullable=False)
    
    # Tracking
    added_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    priority = Column(String(20), nullable=False, default="medium")  # high, medium, low
    
    # AI insights
    match_score = Column(Float, nullable=True)  # Score AI compatibilità
    ai_insights = Column(JSON, nullable=True)  # Insights AI
    
    # Relazioni
    aps_user = relationship("APSUser", back_populates="watchlists")
    bando = relationship("Bando", back_populates="watchlists")


class AIRecommendation(Base):
    """Raccomandazioni AI personalizzate per organizzazioni"""
    __tablename__ = "ai_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Riferimenti
    aps_user_id = Column(Integer, ForeignKey("aps_users.id"), nullable=False)
    bando_id = Column(Integer, ForeignKey("bandi.id"), nullable=False)
    
    # Raccomandazione AI
    recommendation_score = Column(Float, nullable=False)  # Score 0-1
    reasoning = Column(Text, nullable=True)  # Spiegazione AI
    match_factors = Column(JSON, nullable=True)  # Fattori di match
    
    # Stato
    created_at = Column(DateTime, default=datetime.utcnow)
    viewed = Column(Boolean, default=False)
    dismissed = Column(Boolean, default=False)
    applied = Column(Boolean, default=False)
    
    # Feedback loop
    user_feedback = Column(String(20), nullable=True)  # positive, negative, neutral
    feedback_reason = Column(Text, nullable=True)
    
    # Relazioni
    aps_user = relationship("APSUser", back_populates="ai_recommendations")
    bando = relationship("Bando", back_populates="ai_recommendations")


# Aggiungo le relazioni inverse ai modelli esistenti
# Queste vanno aggiunte al modello Bando esistente:
"""
# Da aggiungere a app/models/bando.py:
applications = relationship("BandoApplication", back_populates="bando")
watchlists = relationship("BandoWatchlist", back_populates="bando") 
ai_recommendations = relationship("AIRecommendation", back_populates="bando")
"""
