from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base
import enum


class UserRole(str, enum.Enum):
    """Ruoli utente per il sistema ISS"""
    ADMIN = "admin"  # Super admin ISS
    MODERATOR = "moderator"  # Staff ISS
    APS_RESPONSABILE = "aps_responsabile"  # Responsabile APS
    APS_OPERATORE = "aps_operatore"  # Operatore APS
    CITTADINO = "cittadino"  # Cittadino normale
    VOLONTARIO = "volontario"  # Volontario attivo


class UserStatus(str, enum.Enum):
    """Status account utente"""
    ACTIVE = "active"  # Account attivo
    PENDING = "pending"  # In attesa di verifica email
    SUSPENDED = "suspended"  # Account sospeso
    DELETED = "deleted"  # Account eliminato (soft delete)


class AccessibilityNeeds(str, enum.Enum):
    """Esigenze di accessibilità utente"""
    NONE = "none"  # Nessuna esigenza particolare
    SCREEN_READER = "screen_reader"  # Screen reader
    HIGH_CONTRAST = "high_contrast"  # Alto contrasto
    LARGE_TEXT = "large_text"  # Testo ingrandito
    KEYBOARD_ONLY = "keyboard_only"  # Solo tastiera
    MOTOR_IMPAIRMENT = "motor_impairment"  # Disabilità motorie
    HEARING_IMPAIRMENT = "hearing_impairment"  # Disabilità uditive
    COGNITIVE_SUPPORT = "cognitive_support"  # Supporto cognitivo
    MULTIPLE = "multiple"  # Esigenze multiple


class User(Base):
    """Modello User completo per piattaforma ISS"""
    __tablename__ = "users"

    # Identificatori primari
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=True, index=True)
    
    # Autenticazione
    hashed_password = Column(String(255), nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(100), nullable=True)
    password_reset_token = Column(String(100), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Profilo personale
    nome = Column(String(100), nullable=False)
    cognome = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    data_nascita = Column(DateTime(timezone=True), nullable=True)
    codice_fiscale = Column(String(16), nullable=True, unique=True)
    
    # Ruoli e permessi
    role = Column(Enum(UserRole), default=UserRole.CITTADINO, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)
    
    # Informazioni APS (se applicabile)
    aps_nome_organizzazione = Column(String(200), nullable=True)
    aps_partita_iva = Column(String(11), nullable=True)
    aps_codice_fiscale_org = Column(String(16), nullable=True)
    aps_indirizzo = Column(Text, nullable=True)
    aps_citta = Column(String(100), nullable=True)
    aps_cap = Column(String(5), nullable=True)
    aps_provincia = Column(String(2), nullable=True)
    aps_settore_attivita = Column(String(200), nullable=True)
    aps_website = Column(String(255), nullable=True)
    aps_descrizione = Column(Text, nullable=True)
    
    # Accessibilità e preferenze
    accessibility_needs = Column(Enum(AccessibilityNeeds), default=AccessibilityNeeds.NONE)
    preferred_language = Column(String(5), default="it", nullable=False)
    timezone = Column(String(50), default="Europe/Rome", nullable=False)
    
    # Notifiche e privacy
    email_notifications = Column(Boolean, default=True, nullable=False)
    sms_notifications = Column(Boolean, default=False, nullable=False)
    newsletter_subscription = Column(Boolean, default=True, nullable=False)
    privacy_policy_accepted = Column(Boolean, default=False, nullable=False)
    privacy_policy_accepted_at = Column(DateTime(timezone=True), nullable=True)
    marketing_consent = Column(Boolean, default=False, nullable=False)
    
    # Timestamp e audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    
    # Bio e social
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    twitter_url = Column(String(255), nullable=True)
    facebook_url = Column(String(255), nullable=True)
    
    # Gamification e engagement
    points = Column(Integer, default=0, nullable=False)
    badges = Column(Text, nullable=True)  # JSON array di badge guadagnati
    level = Column(Integer, default=1, nullable=False)
    
    # Relationships
    # Note: Defined with strings to avoid circular imports
    # corsi_creati = relationship("Corso", foreign_keys="Corso.creato_da_user_id", back_populates="creato_da")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}', status='{self.status}')>"
    
    @property
    def full_name(self) -> str:
        """Nome completo dell'utente"""
        return f"{self.nome} {self.cognome}"
    
    @property
    def is_aps(self) -> bool:
        """Verifica se l'utente appartiene a un'APS"""
        return self.role in [UserRole.APS_RESPONSABILE, UserRole.APS_OPERATORE]
    
    @property
    def is_staff(self) -> bool:
        """Verifica se l'utente è staff ISS"""
        return self.role in [UserRole.ADMIN, UserRole.MODERATOR]
    
    @property
    def can_manage_bandi(self) -> bool:
        """Verifica se può gestire configurazioni bandi"""
        return self.role in [UserRole.ADMIN, UserRole.MODERATOR]
    
    @property
    def needs_accessibility_support(self) -> bool:
        """Verifica se ha esigenze di accessibilità"""
        return self.accessibility_needs != AccessibilityNeeds.NONE


class UserSession(Base):
    """Sessioni utente per tracking sicurezza"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    user_agent = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationship
    user = relationship("User", backref="sessions")


class UserPreferences(Base):
    """Preferenze utente avanzate"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Preferenze UI
    theme = Column(String(20), default="light", nullable=False)  # light, dark, auto
    font_size = Column(String(10), default="medium", nullable=False)  # small, medium, large, xl
    reduced_motion = Column(Boolean, default=False, nullable=False)
    high_contrast = Column(Boolean, default=False, nullable=False)
    
    # Preferenze bandi
    preferred_bandi_sources = Column(Text, nullable=True)  # JSON array
    preferred_categories = Column(Text, nullable=True)  # JSON array
    min_importo_interesse = Column(Integer, nullable=True)
    max_importo_interesse = Column(Integer, nullable=True)
    
    # Preferenze notifiche
    notify_new_bandi = Column(Boolean, default=True, nullable=False)
    notify_bandi_expiring = Column(Boolean, default=True, nullable=False)
    notify_corsi_available = Column(Boolean, default=True, nullable=False)
    notify_eventi_upcoming = Column(Boolean, default=True, nullable=False)
    
    # Alert personalizzati
    custom_keywords = Column(Text, nullable=True)  # JSON array di parole chiave
    alert_frequency = Column(String(20), default="daily", nullable=False)  # instant, daily, weekly
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship
    user = relationship("User", backref="preferences", uselist=False)
