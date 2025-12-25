from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.sql import func

from app.infrastructure.database.session import Base

if TYPE_CHECKING:
    from app.domain.support.models import SupportTicket
    from app.domain.billing.models import Subscription
    from app.domain.gdpr.models import UserConsent, DataAuditLog, DataExportRequest, DataDeletionRequest

class UserRole(str, Enum):
    """User roles - MUST match PostgreSQL enum exactly (lowercase)"""
    ADMIN = "admin"        # Super admin con accesso completo
    TRIAL = "trial"        # Utenti in periodo di prova 30 giorni (accesso completo)
    USER = "user"          # Ex-trial scaduti senza abbonamento (portfolio privati)
    CUSTOMER = "customer"  # Utenti con abbonamento base attivo
    PRO = "pro"           # Utenti con abbonamento premium attivo
    TESTER = "tester"      # Account test con features PRO e onboarding speciale

class User(Base):
    __tablename__ = "users"

    # Auth fields
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.TRIAL, index=True)  # Index for role-based queries
    is_active = Column(Boolean, default=True, index=True)  # Index for active user queries
    tenant_id = Column(String(255), nullable=True, index=True)
    trial_expires_at = Column(DateTime, nullable=True, index=True)  # Index for trial expiry queries

    # Profile fields (merged from Profile table)
    username = Column(String, unique=True, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=True, index=True)
    full_name = Column(String, nullable=True)
    title = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    avatar = Column(String, nullable=True)
    public_email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    is_public = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    # Auth - lazy loaded to avoid N+1 queries (load explicitly when needed)
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan", lazy="select")
    mfa_secret = relationship("MFASecret", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="select")
    mfa_attempts = relationship("MFAAttempt", back_populates="user", cascade="all, delete-orphan", lazy="select")
    trusted_devices = relationship("TrustedDevice", back_populates="user", cascade="all, delete-orphan", lazy="select")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan", lazy="select")
    oauth_tokens = relationship("OAuthToken", back_populates="user", cascade="all, delete-orphan", lazy="select")

    # Portfolio relationships (Phase 2 - requires Portfolio domain models)
    # experiences = relationship("Experience", back_populates="user", cascade="all, delete-orphan", lazy="select")
    # education = relationship("Education", back_populates="user", cascade="all, delete-orphan", lazy="select")
    # projects = relationship("Project", back_populates="user", cascade="all, delete-orphan", lazy="select")
    # skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan", lazy="select")
    # languages = relationship("PortfolioLanguage", back_populates="user", cascade="all, delete-orphan", lazy="select")
    # portfolio_profile = relationship("PortfolioProfile", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="select")

    # Analytics relationships (Phase 3 - requires Analytics domain models)
    # views = relationship("PortfolioView", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    # downloads = relationship("CVDownload", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    # sessions = relationship("PortfolioSession", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    # contact_submissions = relationship("ContactFormSubmission", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")

    # Support & Billing relationships (Phase 3 - requires Support/Billing domain models)
    # support_tickets = relationship("SupportTicket", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    # subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="joined")  # Joined - used frequently for permissions

    # Usage Tracking relationships (Phase 3 - requires Usage domain models)
    # usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    # ai_usage_counters = relationship("AIUsageCounter", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")

    # GDPR Compliance relationships (Phase 4 - requires GDPR domain models)
    # consents = relationship("UserConsent", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    # audit_logs = relationship("DataAuditLog", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    # data_export_requests = relationship("DataExportRequest", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    # data_deletion_requests = relationship("DataDeletionRequest", foreign_keys="[DataDeletionRequest.user_id]", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def is_admin(self) -> bool:
        """Compatibilità con il sistema esistente."""
        return self.role == UserRole.ADMIN

    @property
    def is_trial(self) -> bool:
        """Verifica se l'utente è in periodo trial attivo."""
        if self.role != UserRole.TRIAL:
            return False
        if not self.trial_expires_at:
            return True  # Trial senza scadenza impostata
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) < self.trial_expires_at

    @property
    def is_trial_expired(self) -> bool:
        """Verifica se il trial è scaduto."""
        if self.role != UserRole.TRIAL:
            return False
        if not self.trial_expires_at:
            return False
        from datetime import datetime
        return datetime.now(timezone.utc) >= self.trial_expires_at

    @property
    def is_customer(self) -> bool:
        """Verifica se l'utente è un customer con abbonamento base."""
        return self.role == UserRole.CUSTOMER

    @property
    def is_pro(self) -> bool:
        """Verifica se l'utente è PRO con abbonamento premium."""
        return self.role == UserRole.PRO

    @property
    def is_tester(self) -> bool:
        """Verifica se l'utente è un tester con subscription PRO."""
        return self.role == UserRole.TESTER

    @property
    def has_premium_access(self) -> bool:
        """Verifica se l'utente ha accesso alle funzionalità premium."""
        return self.role in [UserRole.PRO, UserRole.TESTER] or self.is_trial

    @property
    def can_publish_portfolio(self) -> bool:
        """Verifica se l'utente può pubblicare il portfolio."""
        return self.role in [UserRole.TRIAL, UserRole.CUSTOMER, UserRole.PRO, UserRole.TESTER]

    def expire_trial_to_user(self):
        """Converte un utente TRIAL scaduto in USER."""
        if self.role == UserRole.TRIAL and self.is_trial_expired:
            self.role = UserRole.USER
            return True
        return False

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"
