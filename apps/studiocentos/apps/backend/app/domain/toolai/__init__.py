"""
ToolAI Domain - Daily AI Tools Discovery & Content Generation

This module provides:
- Daily AI tools/models discovery via semantic search
- Automated content generation with multi-language support
- SEO optimization for AI news
- Integration with existing AI pipelines
"""

from .models import ToolAIPost, AITool, ToolAIPostStatus
from .schemas import (
    ToolAIPostCreate,
    ToolAIPostUpdate,
    ToolAIPostResponse,
    ToolAIPostListResponse,
    AIToolResponse,
    GeneratePostRequest,
    GeneratePostResponse,
)
from .routers import router as toolai_router

__all__ = [
    "ToolAIPost",
    "AITool",
    "ToolAIPostStatus",
    "ToolAIPostCreate",
    "ToolAIPostUpdate",
    "ToolAIPostResponse",
    "ToolAIPostListResponse",
    "AIToolResponse",
    "GeneratePostRequest",
    "GeneratePostResponse",
    "toolai_router",
]
