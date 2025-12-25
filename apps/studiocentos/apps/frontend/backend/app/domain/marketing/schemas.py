"""
Marketing Pydantic Schemas
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from .models import LeadSource, LeadStatus, PostStatus, PostType, SocialPlatform, ToneOfVoice


# ============================================================================
# BRAND SETTINGS (DNA) SCHEMAS
# ============================================================================

class BrandSettingsCreate(BaseModel):
    """Schema per creazione/aggiornamento Brand DNA."""
    # Logo & Visual
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None

    # Colors
    primary_color: str = Field(default="#D4AF37", pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary_color: str = Field(default="#0A0A0A", pattern=r"^#[0-9A-Fa-f]{6}$")
    accent_color: Optional[str] = Field(default="#FAFAFA", pattern=r"^#[0-9A-Fa-f]{6}$")

    # Company Info
    company_name: Optional[str] = Field(None, max_length=255)
    tagline: Optional[str] = None
    description: Optional[str] = None

    # Voice & Tone
    tone_of_voice: ToneOfVoice = Field(default=ToneOfVoice.PROFESSIONAL)

    # Target & Positioning
    target_audience: Optional[str] = None
    unique_value_proposition: Optional[str] = None

    # Structured Data
    keywords: List[str] = Field(default_factory=list)
    values: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)
    content_pillars: List[str] = Field(default_factory=list)

    # Social
    social_handles: Dict[str, str] = Field(default_factory=dict)

    # AI Configuration
    ai_persona: Optional[str] = None
    forbidden_words: List[str] = Field(default_factory=list)
    preferred_hashtags: List[str] = Field(default_factory=list)


class BrandSettingsUpdate(BaseModel):
    """Schema per aggiornamento parziale Brand DNA."""
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None

    primary_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    accent_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")

    company_name: Optional[str] = Field(None, max_length=255)
    tagline: Optional[str] = None
    description: Optional[str] = None

    tone_of_voice: Optional[ToneOfVoice] = None

    target_audience: Optional[str] = None
    unique_value_proposition: Optional[str] = None

    keywords: Optional[List[str]] = None
    values: Optional[List[str]] = None
    competitors: Optional[List[str]] = None
    content_pillars: Optional[List[str]] = None

    social_handles: Optional[Dict[str, str]] = None

    ai_persona: Optional[str] = None
    forbidden_words: Optional[List[str]] = None
    preferred_hashtags: Optional[List[str]] = None


class BrandSettingsResponse(BaseModel):
    """Schema response Brand DNA."""
    id: int
    admin_id: int

    logo_url: Optional[str]
    favicon_url: Optional[str]

    primary_color: str
    secondary_color: str
    accent_color: Optional[str]

    company_name: Optional[str]
    tagline: Optional[str]
    description: Optional[str]

    tone_of_voice: ToneOfVoice

    target_audience: Optional[str]
    unique_value_proposition: Optional[str]

    keywords: List[str]
    values: List[str]
    competitors: List[str]
    content_pillars: List[str]

    social_handles: Dict[str, str]

    ai_persona: Optional[str]
    forbidden_words: List[str]
    preferred_hashtags: List[str]

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
    contact_name: Optional[str] = Field(None, max_length=200)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=500)

    city: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=500)

    source: LeadSource
    status: LeadStatus = Field(default=LeadStatus.NEW)

    industry: Optional[str] = Field(None, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)

    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

    score: int = Field(default=0, ge=0, le=100)


class LeadUpdate(BaseModel):
    """Schema per aggiornamento lead."""
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    contact_name: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=500)

    city: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=500)

    source: Optional[LeadSource] = None
    status: Optional[LeadStatus] = None

    industry: Optional[str] = Field(None, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)

    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None

    score: Optional[int] = Field(None, ge=0, le=100)


class LeadResponse(BaseModel):
    """Schema response lead."""
    id: int
    company_name: str
    contact_name: Optional[str]
    email: str
    phone: Optional[str]
    website: Optional[str]

    city: Optional[str]
    region: Optional[str]
    address: Optional[str]

    source: LeadSource
    status: LeadStatus

    industry: Optional[str]
    company_size: Optional[str]

    notes: Optional[str]
    tags: List[str]
    custom_fields: Dict[str, Any]

    score: int

    last_contact_date: Optional[datetime]
    next_followup_date: Optional[datetime]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """Response lista leads."""
    items: List[LeadResponse]
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

    target_region: Optional[str] = Field(None, max_length=100)
    target_industry: Optional[str] = Field(None, max_length=100)
    target_tags: List[str] = Field(default_factory=list)

    scheduled_date: Optional[datetime] = None

    ai_generated: bool = Field(default=False)
    ai_model: Optional[str] = Field(None, max_length=100)


class EmailCampaignResponse(BaseModel):
    """Schema response campagna."""
    id: int
    name: str
    subject: str

    html_content: str
    text_content: str

    target_region: Optional[str]
    target_industry: Optional[str]
    target_tags: List[str]

    scheduled_date: Optional[datetime]
    sent_date: Optional[datetime]

    is_active: bool
    is_sent: bool

    total_sent: int
    total_opened: int
    total_clicked: int
    total_replied: int

    ai_generated: bool
    ai_model: Optional[str]

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
    company_name: Optional[str] = None
    contact_name: Optional[str] = None


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
    title: Optional[str] = Field(None, max_length=500, description="Titolo interno")
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)

    media_urls: List[str] = Field(default_factory=list)
    media_type: PostType = Field(default=PostType.TEXT)

    platforms: List[str] = Field(..., min_length=1, description="Piattaforme target")

    scheduled_at: datetime = Field(..., description="Data/ora pubblicazione")

    ai_generated: bool = Field(default=False)
    ai_prompt: Optional[str] = None
    ai_model: Optional[str] = None

    campaign_id: Optional[int] = None


class ScheduledPostUpdate(BaseModel):
    """Schema per aggiornamento post programmato."""
    content: Optional[str] = Field(None, min_length=1)
    title: Optional[str] = Field(None, max_length=500)
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None

    media_urls: Optional[List[str]] = None
    media_type: Optional[PostType] = None

    platforms: Optional[List[str]] = None

    scheduled_at: Optional[datetime] = None
    status: Optional[PostStatus] = None


class ScheduledPostResponse(BaseModel):
    """Schema response post programmato."""
    id: int
    content: str
    title: Optional[str]
    hashtags: List[str]
    mentions: List[str]

    media_urls: List[str]
    media_type: PostType

    platforms: List[str]

    scheduled_at: datetime
    published_at: Optional[datetime]

    status: PostStatus

    platform_results: Dict[str, Any]
    error_message: Optional[str]
    retry_count: int

    ai_generated: bool
    ai_prompt: Optional[str]
    ai_model: Optional[str]

    campaign_id: Optional[int]
    created_by: Optional[int]

    metrics: Dict[str, Any]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduledPostListResponse(BaseModel):
    """Response lista post programmati."""
    items: List[ScheduledPostResponse]
    total: int
    page: int
    page_size: int


class CalendarViewResponse(BaseModel):
    """Response per vista calendario."""
    posts: List[ScheduledPostResponse]
    start_date: datetime
    end_date: datetime
    total_scheduled: int
    total_published: int
    total_failed: int
    platforms_stats: Dict[str, int]


# ============================================================================
# EDITORIAL CALENDAR SCHEMAS
# ============================================================================

class EditorialCalendarCreate(BaseModel):
    """Schema per creazione calendario editoriale."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

    start_date: datetime
    end_date: datetime

    default_platforms: List[str] = Field(default_factory=list)
    posting_frequency: Optional[str] = Field(None, description="daily, 3x_week, weekly")
    optimal_times: List[str] = Field(default_factory=list, description="['09:00', '12:00', '18:00']")


class EditorialCalendarResponse(BaseModel):
    """Schema response calendario editoriale."""
    id: int
    name: str
    description: Optional[str]

    start_date: datetime
    end_date: datetime

    default_platforms: List[str]
    posting_frequency: Optional[str]
    optimal_times: List[str]

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
    posts: List[ScheduledPostCreate]


class BulkScheduleResponse(BaseModel):
    """Response scheduling bulk."""
    created: int
    failed: int
    errors: List[str]


class PublishNowRequest(BaseModel):
    """Request per pubblicazione immediata."""
    post_id: int


class AIGeneratePostsRequest(BaseModel):
    """Request per generazione AI di post."""
    topic: str = Field(..., description="Argomento principale")
    platforms: List[str] = Field(..., description="Piattaforme target")
    count: int = Field(default=7, ge=1, le=30, description="Numero di post da generare")
    tone: str = Field(default="professional", description="Tono: professional, friendly, casual")
    include_hashtags: bool = Field(default=True)
    schedule_start: datetime = Field(..., description="Data inizio scheduling")
    frequency: str = Field(default="daily", description="daily, 3x_week, weekly")
