"""
ToolAI Pydantic Schemas

Request/Response models for ToolAI API.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from .models import ToolAIPostStatus


# =============================================================================
# AI Tool Schemas
# =============================================================================

class AIToolBase(BaseModel):
    """Base schema for AI Tool."""
    name: str = Field(..., description="Tool/Model name")
    source: Optional[str] = Field(None, description="Source: huggingface, github, arxiv")
    source_url: Optional[str] = Field(None, description="URL to source")
    description_it: str = Field(..., description="Description in Italian")
    description_en: Optional[str] = Field(None, description="Description in English")
    description_es: Optional[str] = Field(None, description="Description in Spanish")
    relevance_it: Optional[str] = Field(None, description="Why relevant (IT)")
    relevance_en: Optional[str] = Field(None, description="Why relevant (EN)")
    relevance_es: Optional[str] = Field(None, description="Why relevant (ES)")
    category: Optional[str] = Field(None, description="Category: llm, image, audio, code")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags")
    stars: Optional[int] = Field(None, description="GitHub stars")
    downloads: Optional[int] = Field(None, description="Downloads count")
    trending_score: Optional[int] = Field(None, description="Trending score")
    display_order: int = Field(default=0, description="Order in post")


class AIToolCreate(AIToolBase):
    """Schema for creating an AI Tool."""
    pass


class AIToolResponse(AIToolBase):
    """Schema for AI Tool response."""
    id: int
    post_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# ToolAI Post Schemas
# =============================================================================

class ToolAIPostBase(BaseModel):
    """Base schema for ToolAI Post."""
    post_date: datetime = Field(..., description="Post date (one per day)")
    title_it: str = Field(..., description="SEO title in Italian")
    title_en: Optional[str] = Field(None, description="SEO title in English")
    title_es: Optional[str] = Field(None, description="SEO title in Spanish")
    summary_it: str = Field(..., description="Summary in Italian")
    summary_en: Optional[str] = Field(None, description="Summary in English")
    summary_es: Optional[str] = Field(None, description="Summary in Spanish")
    content_it: str = Field(..., description="Full content in Italian")
    content_en: Optional[str] = Field(None, description="Full content in English")
    content_es: Optional[str] = Field(None, description="Full content in Spanish")
    insights_it: Optional[str] = Field(None, description="Practical insights (IT)")
    insights_en: Optional[str] = Field(None, description="Practical insights (EN)")
    insights_es: Optional[str] = Field(None, description="Practical insights (ES)")
    takeaway_it: Optional[str] = Field(None, description="Takeaway (IT)")
    takeaway_en: Optional[str] = Field(None, description="Takeaway (EN)")
    takeaway_es: Optional[str] = Field(None, description="Takeaway (ES)")
    meta_description: Optional[str] = Field(None, max_length=160, description="Meta description")
    meta_keywords: Optional[List[str]] = Field(default_factory=list, description="SEO keywords")
    slug: Optional[str] = Field(None, description="URL slug")
    image_url: Optional[str] = Field(None, description="Featured image URL")


class ToolAIPostCreate(ToolAIPostBase):
    """Schema for creating a ToolAI Post."""
    status: str = Field(default="draft")
    tools: List[AIToolCreate] = Field(default_factory=list, description="AI tools in post")


class ToolAIPostUpdate(BaseModel):
    """Schema for updating a ToolAI Post."""
    title_it: Optional[str] = None
    title_en: Optional[str] = None
    title_es: Optional[str] = None
    summary_it: Optional[str] = None
    summary_en: Optional[str] = None
    summary_es: Optional[str] = None
    content_it: Optional[str] = None
    content_en: Optional[str] = None
    content_es: Optional[str] = None
    insights_it: Optional[str] = None
    insights_en: Optional[str] = None
    insights_es: Optional[str] = None
    takeaway_it: Optional[str] = None
    takeaway_en: Optional[str] = None
    takeaway_es: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[List[str]] = None
    slug: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[str] = None


class ToolAIPostResponse(ToolAIPostBase):
    """Schema for ToolAI Post response."""
    id: int
    status: str
    ai_generated: bool
    ai_model: Optional[str]
    generation_time: Optional[int]
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    tools: List[AIToolResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ToolAIPostListResponse(BaseModel):
    """Schema for paginated list of ToolAI Posts."""
    total: int
    page: int
    per_page: int
    posts: List[ToolAIPostResponse]


# =============================================================================
# Generation Schemas
# =============================================================================

class GeneratePostRequest(BaseModel):
    """Request to generate a new ToolAI post."""
    target_date: Optional[datetime] = Field(None, description="Date for post (default: today)")
    num_tools: int = Field(default=3, ge=1, le=10, description="Number of tools to discover")
    categories: List[str] = Field(
        default_factory=lambda: ["llm", "image", "code", "audio"],
        description="Categories to search"
    )
    auto_publish: bool = Field(default=False, description="Publish immediately after generation")
    translate: bool = Field(default=True, description="Generate EN/ES translations")
    generate_image: bool = Field(default=True, description="Generate featured image")


class GeneratePostResponse(BaseModel):
    """Response from post generation."""
    success: bool
    post_id: Optional[int]
    post: Optional[ToolAIPostResponse]
    tools_discovered: int
    generation_time_seconds: float
    ai_model: str
    message: str


class DiscoverToolsRequest(BaseModel):
    """Request to discover AI tools."""
    num_tools: int = Field(default=5, ge=1, le=20)
    categories: List[str] = Field(default_factory=lambda: ["llm", "image", "code"])
    sources: List[str] = Field(default_factory=lambda: ["huggingface", "github"])
    min_trending_score: int = Field(default=0)


class DiscoverToolsResponse(BaseModel):
    """Response from tool discovery."""
    tools: List[AIToolResponse]
    sources_searched: List[str]
    search_time_seconds: float


# =============================================================================
# Stats Schema
# =============================================================================

class RecentPostInfo(BaseModel):
    """Info for recent post in stats."""
    id: int
    date: str
    title: str
    status: str


class ToolAIStats(BaseModel):
    """ToolAI statistics response."""
    total_posts: int
    published_posts: int
    draft_posts: int
    total_tools_discovered: int
    recent_posts: List[RecentPostInfo] = Field(default_factory=list)
