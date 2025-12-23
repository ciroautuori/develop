"""
Marketing Pydantic Schemas
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from .models import LeadSource, LeadStatus, PostStatus, PostType, ToneOfVoice

# ============================================================================
# BRAND SETTINGS (DNA) SCHEMAS
# ============================================================================

class BrandSettingsCreate(BaseModel):
    """Schema per creazione/aggiornamento Brand DNA."""
    # Logo & Visual
    logo_url: str | None = None
    favicon_url: str | None = None

    # Colors
    primary_color: str = Field(default="#D4AF37", pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary_color: str = Field(default="#0A0A0A", pattern=r"^#[0-9A-Fa-f]{6}$")
    accent_color: str | None = Field(default="#FAFAFA", pattern=r"^#[0-9A-Fa-f]{6}$")

    # Company Info
    company_name: str | None = Field(None, max_length=255)
    tagline: str | None = None
    description: str | None = None

    # Voice & Tone
    tone_of_voice: ToneOfVoice = Field(default=ToneOfVoice.PROFESSIONAL)

    # Target & Positioning
    target_audience: str | None = None
    unique_value_proposition: str | None = None

    # Structured Data
    keywords: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)
    competitors: list[str] = Field(default_factory=list)
    content_pillars: list[str] = Field(default_factory=list)

    # Social
    social_handles: dict[str, str] = Field(default_factory=dict)

    # AI Configuration
    ai_persona: str | None = None
    forbidden_words: list[str] = Field(default_factory=list)
    preferred_hashtags: list[str] = Field(default_factory=list)


class BrandSettingsUpdate(BaseModel):
    """Schema per aggiornamento parziale Brand DNA."""
    logo_url: str | None = None
    favicon_url: str | None = None

    primary_color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary_color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    accent_color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")

    company_name: str | None = Field(None, max_length=255)
    tagline: str | None = None
    description: str | None = None

    tone_of_voice: ToneOfVoice | None = None

    target_audience: str | None = None
    unique_value_proposition: str | None = None

    keywords: list[str] | None = None
    values: list[str] | None = None
    competitors: list[str] | None = None
    content_pillars: list[str] | None = None

    social_handles: dict[str, str] | None = None

    ai_persona: str | None = None
    forbidden_words: list[str] | None = None
    preferred_hashtags: list[str] | None = None


class BrandSettingsResponse(BaseModel):
    """Schema response Brand DNA."""
    id: int
    admin_id: int

    logo_url: str | None
    favicon_url: str | None

    primary_color: str
    secondary_color: str
    accent_color: str | None

    company_name: str | None
    tagline: str | None
    description: str | None

    tone_of_voice: ToneOfVoice

    target_audience: str | None
    unique_value_proposition: str | None

    keywords: list[str]
    values: list[str]
    competitors: list[str]
    content_pillars: list[str]

    social_handles: dict[str, str]

    ai_persona: str | None
    forbidden_words: list[str]
    preferred_hashtags: list[str]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# LEAD SCHEMAS
# ============================================================================

class LeadCreate(BaseModel):
    """Schema per creazione lead."""
    company_name: str = Field(..., min_length=1, max_length=200)
    contact_name: str | None = Field(None, max_length=200)
    email: EmailStr
    phone: str | None = Field(None, max_length=50)
    website: str | None = Field(None, max_length=500)

    city: str | None = Field(None, max_length=100)
    region: str | None = Field(None, max_length=100)
    address: str | None = Field(None, max_length=500)

    source: LeadSource
    status: LeadStatus = Field(default=LeadStatus.NEW)

    industry: str | None = Field(None, max_length=100)
    company_size: str | None = Field(None, max_length=50)

    notes: str | None = None
    tags: list[str] = Field(default_factory=list)
    custom_fields: dict[str, Any] = Field(default_factory=dict)

    score: int = Field(default=0, ge=0, le=100)


class LeadUpdate(BaseModel):
    """Schema per aggiornamento lead."""
    company_name: str | None = Field(None, min_length=1, max_length=200)
    contact_name: str | None = Field(None, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    website: str | None = Field(None, max_length=500)

    city: str | None = Field(None, max_length=100)
    region: str | None = Field(None, max_length=100)
    address: str | None = Field(None, max_length=500)

    source: LeadSource | None = None
    status: LeadStatus | None = None

    industry: str | None = Field(None, max_length=100)
    company_size: str | None = Field(None, max_length=50)

    notes: str | None = None
    tags: list[str] | None = None
    custom_fields: dict[str, Any] | None = None

    score: int | None = Field(None, ge=0, le=100)


class LeadResponse(BaseModel):
    """Schema response lead."""
    id: int
    company_name: str
    contact_name: str | None
    email: str
    phone: str | None
    website: str | None

    city: str | None
    region: str | None
    address: str | None

    source: LeadSource
    status: LeadStatus

    industry: str | None
    company_size: str | None

    notes: str | None
    tags: list[str]
    custom_fields: dict[str, Any]

    score: int

    last_contact_date: datetime | None
    next_followup_date: datetime | None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """Response lista leads."""
    items: list[LeadResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# EMAIL CAMPAIGN SCHEMAS
# ============================================================================

class EmailCampaignCreate(BaseModel):
    """Schema per creazione campagna email."""
    name: str = Field(..., min_length=1, max_length=200)
    subject: str = Field(..., min_length=1, max_length=500)

    html_content: str = Field(..., min_length=1)
    text_content: str = Field(..., min_length=1)

    target_region: str | None = Field(None, max_length=100)
    target_industry: str | None = Field(None, max_length=100)
    target_tags: list[str] = Field(default_factory=list)

    scheduled_date: datetime | None = None

    ai_generated: bool = Field(default=False)
    ai_model: str | None = Field(None, max_length=100)


class EmailCampaignResponse(BaseModel):
    """Schema response campagna."""
    id: int
    name: str
    subject: str

    html_content: str
    text_content: str

    target_region: str | None
    target_industry: str | None
    target_tags: list[str]

    scheduled_date: datetime | None
    sent_date: datetime | None

    is_active: bool
    is_sent: bool

    total_sent: int
    total_opened: int
    total_clicked: int
    total_replied: int

    ai_generated: bool
    ai_model: str | None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# AI GENERATION SCHEMAS
# ============================================================================

class GenerateEmailRequest(BaseModel):
    """Request per generare email con AI."""
    campaign_name: str
    target_region: str = Field(..., description="Salerno, Campania, etc")
    target_industry: str = Field(..., description="software, ecommerce, services")
    tone: str = Field(default="professional", description="professional, friendly, casual")
    language: str = Field(default="it", description="it, en")

    # Optional personalization
    company_name: str | None = None
    contact_name: str | None = None


class GenerateEmailResponse(BaseModel):
    """Response email generata."""
    subject: str
    html_content: str
    text_content: str
    ai_model: str


# ============================================================================
# SCHEDULED POST SCHEMAS (Calendario Editoriale)
# ============================================================================

class ScheduledPostCreate(BaseModel):
    """Schema per creazione post programmato."""
    content: str = Field(..., min_length=1, description="Contenuto del post")
    title: str | None = Field(None, max_length=500, description="Titolo interno")
    hashtags: list[str] = Field(default_factory=list)
    mentions: list[str] = Field(default_factory=list)

    media_urls: list[str] = Field(default_factory=list)
    media_type: PostType = Field(default=PostType.TEXT)

    platforms: list[str] = Field(..., min_length=1, description="Piattaforme target")

    scheduled_at: datetime = Field(..., description="Data/ora pubblicazione")

    ai_generated: bool = Field(default=False)
    ai_prompt: str | None = None
    ai_model: str | None = None

    campaign_id: int | None = None


class ScheduledPostUpdate(BaseModel):
    """Schema per aggiornamento post programmato."""
    content: str | None = Field(None, min_length=1)
    title: str | None = Field(None, max_length=500)
    hashtags: list[str] | None = None
    mentions: list[str] | None = None

    media_urls: list[str] | None = None
    media_type: PostType | None = None

    platforms: list[str] | None = None

    scheduled_at: datetime | None = None
    status: PostStatus | None = None


class ScheduledPostResponse(BaseModel):
    """Schema response post programmato."""
    id: int
    content: str
    title: str | None
    hashtags: list[str]
    mentions: list[str]

    media_urls: list[str]
    media_type: PostType

    platforms: list[str]

    scheduled_at: datetime
    published_at: datetime | None

    status: PostStatus

    platform_results: dict[str, Any]
    error_message: str | None
    retry_count: int

    ai_generated: bool
    ai_prompt: str | None
    ai_model: str | None

    campaign_id: int | None
    created_by: int | None

    metrics: dict[str, Any]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduledPostListResponse(BaseModel):
    """Response lista post programmati."""
    items: list[ScheduledPostResponse]
    total: int
    page: int
    page_size: int


class CalendarViewResponse(BaseModel):
    """Response per vista calendario."""
    posts: list[ScheduledPostResponse]
    start_date: datetime
    end_date: datetime
    total_scheduled: int
    total_published: int
    total_failed: int
    platforms_stats: dict[str, int]


# ============================================================================
# EDITORIAL CALENDAR SCHEMAS
# ============================================================================

class EditorialCalendarCreate(BaseModel):
    """Schema per creazione calendario editoriale."""
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None

    start_date: datetime
    end_date: datetime

    default_platforms: list[str] = Field(default_factory=list)
    posting_frequency: str | None = Field(None, description="daily, 3x_week, weekly")
    optimal_times: list[str] = Field(default_factory=list, description="['09:00', '12:00', '18:00']")


class EditorialCalendarResponse(BaseModel):
    """Schema response calendario editoriale."""
    id: int
    name: str
    description: str | None

    start_date: datetime
    end_date: datetime

    default_platforms: list[str]
    posting_frequency: str | None
    optimal_times: list[str]

    is_active: bool
    total_posts_planned: int
    total_posts_published: int

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# BULK OPERATIONS SCHEMAS
# ============================================================================

class BulkScheduleRequest(BaseModel):
    """Request per scheduling bulk di post."""
    posts: list[ScheduledPostCreate]


class BulkScheduleResponse(BaseModel):
    """Response scheduling bulk."""
    created: int
    failed: int
    errors: list[str]


class PublishNowRequest(BaseModel):
    """Request per pubblicazione immediata."""
    post_id: int


class AIGeneratePostsRequest(BaseModel):
    """Request per generazione AI di post."""
    topic: str = Field(..., description="Argomento principale")
    platforms: list[str] = Field(..., description="Piattaforme target")
    count: int = Field(default=7, ge=1, le=30, description="Numero di post da generare")
    tone: str = Field(default="professional", description="Tono: professional, friendly, casual")
    include_hashtags: bool = Field(default=True)
    schedule_start: datetime = Field(..., description="Data inizio scheduling")
    frequency: str = Field(default="daily", description="daily, 3x_week, weekly")
