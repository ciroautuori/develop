"""
ToolAI Database Models

Stores daily AI tools/models posts with multi-language support.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    JSON, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base


class ToolAIPostStatus(str, Enum):
    """Status of a ToolAI post."""
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"


class ToolAIPost(Base):
    """
    Daily AI Tools/Models Discovery Post.

    Each post contains:
    - SEO-optimized title and summary
    - 3+ AI tools/models discovered
    - Practical insights
    - Multi-language support (IT, EN, ES)
    """
    __tablename__ = "toolai_posts"

    id = Column(Integer, primary_key=True, index=True)

    # Post date (one per day)
    post_date = Column(DateTime, nullable=False, unique=True, index=True)

    # Status (using String for PostgreSQL compatibility)
    status = Column(String(20), default="draft", nullable=False)

    # SEO-friendly title (multi-language)
    title_it = Column(String(255), nullable=False)
    title_en = Column(String(255), nullable=True)
    title_es = Column(String(255), nullable=True)

    # Summary of the day's AI news (multi-language)
    summary_it = Column(Text, nullable=False)
    summary_en = Column(Text, nullable=True)
    summary_es = Column(Text, nullable=True)

    # Full content (multi-language)
    content_it = Column(Text, nullable=False)
    content_en = Column(Text, nullable=True)
    content_es = Column(Text, nullable=True)

    # Practical insights section (multi-language)
    insights_it = Column(Text, nullable=True)
    insights_en = Column(Text, nullable=True)
    insights_es = Column(Text, nullable=True)

    # Conclusion/Takeaway (multi-language)
    takeaway_it = Column(Text, nullable=True)
    takeaway_en = Column(Text, nullable=True)
    takeaway_es = Column(Text, nullable=True)

    # SEO metadata
    meta_description = Column(String(160), nullable=True)
    meta_keywords = Column(JSON, default=list)  # List of keywords
    slug = Column(String(255), nullable=True, unique=True, index=True)

    # Featured image
    image_url = Column(String(512), nullable=True)

    # AI generation metadata
    ai_generated = Column(Boolean, default=True)
    ai_model = Column(String(100), nullable=True)
    generation_time = Column(Integer, nullable=True)  # Seconds

    # Publishing
    published_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tools = relationship("AITool", back_populates="post", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_toolai_posts_status_date', 'status', 'post_date'),
    )


class AITool(Base):
    """
    Individual AI Tool/Model discovered.

    Each tool includes:
    - Name and description
    - Source (HuggingFace, GitHub, etc.)
    - Category and tags
    - Relevance explanation
    """
    __tablename__ = "toolai_tools"

    id = Column(Integer, primary_key=True, index=True)

    # Parent post
    post_id = Column(Integer, ForeignKey("toolai_posts.id", ondelete="CASCADE"), nullable=False)

    # Tool info
    name = Column(String(255), nullable=False)
    source = Column(String(100), nullable=True)  # huggingface, github, arxiv, etc.
    source_url = Column(String(512), nullable=True)

    # Description (multi-language)
    description_it = Column(Text, nullable=False)
    description_en = Column(Text, nullable=True)
    description_es = Column(Text, nullable=True)

    # Why it's relevant (multi-language)
    relevance_it = Column(Text, nullable=True)
    relevance_en = Column(Text, nullable=True)
    relevance_es = Column(Text, nullable=True)

    # Category and tags
    category = Column(String(100), nullable=True)  # llm, image, audio, code, etc.
    tags = Column(JSON, default=list)

    # Metrics (if available)
    stars = Column(Integer, nullable=True)
    downloads = Column(Integer, nullable=True)
    trending_score = Column(Integer, nullable=True)

    # Order in the post
    display_order = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    post = relationship("ToolAIPost", back_populates="tools")

    # Indexes
    __table_args__ = (
        Index('ix_toolai_tools_category', 'category'),
        Index('ix_toolai_tools_post_order', 'post_id', 'display_order'),
    )
