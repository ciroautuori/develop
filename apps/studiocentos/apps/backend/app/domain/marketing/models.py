"""
Marketing Database Models
Lead generation + Email campaigns per Salerno/Campania
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base
import enum


class LeadSource(str, enum.Enum):
    """Fonte del lead."""
    WEBSITE = "WEBSITE"
    LINKEDIN = "LINKEDIN"
    GOOGLE_MAPS = "GOOGLE_MAPS"
    EMAIL_CAMPAIGN = "EMAIL_CAMPAIGN"
    REFERRAL = "REFERRAL"
    SALERNO_SEARCH = "SALERNO_SEARCH"
    CAMPANIA_SEARCH = "CAMPANIA_SEARCH"
    MANUAL = "MANUAL"


class LeadStatus(str, enum.Enum):
    """Status del lead."""
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    PROPOSAL_SENT = "PROPOSAL_SENT"
    NEGOTIATION = "NEGOTIATION"
    WON = "WON"
    LOST = "LOST"
    NURTURING = "NURTURING"


class Lead(Base):
    """
    Lead - Potenziale cliente.
    Focus su Salerno e Campania.
    """
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    # Contact info
    company_name = Column(String(200), nullable=False, index=True)
    contact_name = Column(String(200), nullable=True)
    email = Column(String(200), nullable=False, unique=True, index=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(500), nullable=True)

    # Location (focus Salerno/Campania)
    city = Column(String(100), nullable=True, index=True)
    region = Column(String(100), nullable=True, index=True)
    address = Column(String(500), nullable=True)

    # Source & Status
    source = Column(SQLEnum(LeadSource), nullable=False)
    status = Column(SQLEnum(LeadStatus), nullable=False, default=LeadStatus.NEW)

    # Industry & Size
    industry = Column(String(100), nullable=True)  # "software", "ecommerce", "services"
    company_size = Column(String(50), nullable=True)  # "1-10", "11-50", "51-200"

    # Notes & Metadata
    notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=False, default=list)  # ["ai-ready", "web-dev", "urgent"]
    custom_fields = Column(JSON, nullable=False, default=dict)

    # Scoring
    score = Column(Integer, nullable=False, default=0)  # 0-100 lead quality score

    # Communication
    last_contact_date = Column(DateTime(timezone=True), nullable=True)
    next_followup_date = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Lead {self.company_name} - {self.city}>"


class EmailCampaign(Base):
    """
    Email Campaign - Campagna email marketing.
    """
    __tablename__ = "email_campaigns"

    id = Column(Integer, primary_key=True, index=True)

    # Campaign info
    name = Column(String(200), nullable=False)
    subject = Column(String(500), nullable=False)

    # Content
    html_content = Column(Text, nullable=False)
    text_content = Column(Text, nullable=False)

    # Targeting
    target_region = Column(String(100), nullable=True)  # "Salerno", "Campania"
    target_industry = Column(String(100), nullable=True)
    target_tags = Column(JSON, nullable=False, default=list)

    # Schedule
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    sent_date = Column(DateTime(timezone=True), nullable=True)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    is_sent = Column(Boolean, nullable=False, default=False)

    # Stats
    total_sent = Column(Integer, nullable=False, default=0)
    total_opened = Column(Integer, nullable=False, default=0)
    total_clicked = Column(Integer, nullable=False, default=0)
    total_replied = Column(Integer, nullable=False, default=0)

    # AI Generated
    ai_generated = Column(Boolean, nullable=False, default=False)
    ai_model = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<EmailCampaign {self.name}>"


class SocialPlatform(str, enum.Enum):
    """Piattaforme social supportate."""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    THREADS = "threads"
    TIKTOK = "tiktok"


class PostStatus(str, enum.Enum):
    """Status del post programmato."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PostType(str, enum.Enum):
    """Tipo di contenuto."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"


class ScheduledPost(Base):
    """
    Post programmato per calendario editoriale.
    Supporta multi-piattaforma e scheduling automatico.
    """
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True, index=True)

    # Content
    content = Column(Text, nullable=False)
    title = Column(String(500), nullable=True)  # Titolo interno per organizzazione
    hashtags = Column(JSON, nullable=False, default=list)  # ["#marketing", "#ai"]
    mentions = Column(JSON, nullable=False, default=list)  # ["@studiocentos"]

    # Media
    media_urls = Column(JSON, nullable=False, default=list)  # URLs delle immagini/video
    media_type = Column(String, nullable=False, default="text")

    # Targeting
    platforms = Column(JSON, nullable=False, default=list)  # ["facebook", "instagram"]

    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Status
    status = Column(String, nullable=False, default="draft", index=True)

    # Results per platform (dopo pubblicazione)
    platform_results = Column(JSON, nullable=False, default=dict)
    # Esempio: {"facebook": {"post_id": "123", "status": "published"}, "instagram": {"post_id": "456", "error": "..."}}

    # Error tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)

    # AI Generation metadata
    ai_generated = Column(Boolean, nullable=False, default=False)
    ai_prompt = Column(Text, nullable=True)
    ai_model = Column(String(100), nullable=True)

    # Campaign linking (optional)
    campaign_id = Column(Integer, ForeignKey("email_campaigns.id"), nullable=True)
    campaign = relationship("EmailCampaign", backref="scheduled_posts")

    # User tracking
    created_by = Column(Integer, nullable=True)  # User ID

    # Engagement metrics (updated after publish)
    metrics = Column(JSON, nullable=False, default=dict)
    # Esempio: {"likes": 10, "comments": 5, "shares": 2, "impressions": 1000}

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<ScheduledPost {self.id} - {self.status.value} @ {self.scheduled_at}>"


class EditorialCalendar(Base):
    """
    Calendario editoriale - Piano mensile/settimanale.
    Organizza i post per periodo.
    """
    __tablename__ = "editorial_calendars"

    id = Column(Integer, primary_key=True, index=True)

    # Calendar info
    name = Column(String(200), nullable=False)  # "Novembre 2025", "Week 48"
    description = Column(Text, nullable=True)

    # Period
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)

    # Settings
    default_platforms = Column(JSON, nullable=False, default=list)
    posting_frequency = Column(String(50), nullable=True)  # "daily", "3x_week", "weekly"
    optimal_times = Column(JSON, nullable=False, default=list)  # ["09:00", "12:00", "18:00"]

    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    # Stats
    total_posts_planned = Column(Integer, nullable=False, default=0)
    total_posts_published = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<EditorialCalendar {self.name}>"


class ToneOfVoice(str, enum.Enum):
    """Tone of voice per brand."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ENTHUSIASTIC = "enthusiastic"
    FORMAL = "formal"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"


class BrandSettings(Base):
    """
    Brand DNA Settings - Configurazione identità brand.
    Persistenza dati brand per utilizzo negli agenti AI.
    """
    __tablename__ = "brand_settings"

    id = Column(Integer, primary_key=True, index=True)

    # Owner - relazione con AdminUser
    admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False, unique=True, index=True)

    # Logo & Visual Identity
    logo_url = Column(Text, nullable=True)
    favicon_url = Column(Text, nullable=True)

    # Brand Colors
    primary_color = Column(String(7), nullable=False, default="#D4AF37")  # GOLD
    secondary_color = Column(String(7), nullable=False, default="#0A0A0A")  # BLACK
    accent_color = Column(String(7), nullable=True, default="#FAFAFA")  # WHITE

    # Company Info
    company_name = Column(String(255), nullable=True)
    tagline = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    # Voice & Tone
    tone_of_voice = Column(SQLEnum(ToneOfVoice), nullable=False, default=ToneOfVoice.PROFESSIONAL)

    # Target & Positioning
    target_audience = Column(Text, nullable=True)
    unique_value_proposition = Column(Text, nullable=True)

    # Structured Data (JSONB)
    keywords = Column(JSON, nullable=False, default=list)  # ["AI", "automazione", "marketing"]
    values = Column(JSON, nullable=False, default=list)  # ["innovazione", "affidabilità"]
    competitors = Column(JSON, nullable=False, default=list)  # ["competitor1", "competitor2"]
    content_pillars = Column(JSON, nullable=False, default=list)  # ["tech", "business", "lifestyle"]

    # Social Presence
    social_handles = Column(JSON, nullable=False, default=dict)  # {"instagram": "@brand", "linkedin": "..."}

    # AI Configuration
    ai_persona = Column(Text, nullable=True)  # Descrizione personalità AI
    forbidden_words = Column(JSON, nullable=False, default=list)  # Parole da evitare
    preferred_hashtags = Column(JSON, nullable=False, default=list)  # Hashtag preferiti

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<BrandSettings {self.company_name} - Admin {self.admin_id}>"
