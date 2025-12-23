"""
ToolAI API Endpoints

Endpoints for AI tool discovery and content generation.
Called by the backend service to generate daily ToolAI posts.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.core.security import verify_api_key
from app.core.logging import get_logger
from app.domain.toolai.discovery_agent import ToolDiscoveryAgent, DiscoveredTool
from app.domain.toolai.content_agent import ToolContentAgent, GeneratedContent

logger = get_logger(__name__)
router = APIRouter(dependencies=[Depends(verify_api_key)])


# =============================================================================
# Request/Response Models
# =============================================================================

class DiscoverRequest(BaseModel):
    """Request to discover AI tools."""
    num_tools: int = Field(default=5, ge=1, le=20)
    categories: List[str] = Field(
        default=["llm", "image", "audio", "code"],
        description="Categories: llm, image, audio, video, code, multimodal"
    )
    sources: List[str] = Field(
        default=["huggingface", "github"],
        description="Sources: huggingface, github"
    )


class DiscoverResponse(BaseModel):
    """Response from tool discovery."""
    tools: List[dict]
    num_discovered: int
    sources_searched: List[str]


class GenerateContentRequest(BaseModel):
    """Request to generate post content."""
    tools: List[dict]
    target_date: str = Field(..., description="ISO format date")
    translate: bool = Field(default=True, description="Generate EN/ES translations")


class GenerateContentResponse(BaseModel):
    """Response from content generation."""
    title_it: str
    title_en: Optional[str] = None
    title_es: Optional[str] = None
    summary_it: str
    summary_en: Optional[str] = None
    summary_es: Optional[str] = None
    content_it: str
    content_en: Optional[str] = None
    content_es: Optional[str] = None
    insights_it: Optional[str] = None
    insights_en: Optional[str] = None
    insights_es: Optional[str] = None
    takeaway_it: Optional[str] = None
    takeaway_en: Optional[str] = None
    takeaway_es: Optional[str] = None
    meta_description: str
    meta_keywords: List[str]
    ai_model: str


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/discover", response_model=DiscoverResponse)
async def discover_tools(request: DiscoverRequest):
    """
    🔍 Discover trending AI tools.

    Searches HuggingFace and GitHub for the latest AI tools/models.
    Returns tools with Italian descriptions and relevance scores.
    """
    logger.info(
        "toolai_discover_request",
        num_tools=request.num_tools,
        categories=request.categories,
        sources=request.sources
    )

    agent = ToolDiscoveryAgent()

    try:
        tools = await agent.discover_tools(
            num_tools=request.num_tools,
            categories=request.categories,
            sources=request.sources,
        )

        # Convert to dict for response
        tools_data = [t.model_dump() for t in tools]

        logger.info("toolai_discover_success", num_tools=len(tools_data))

        return DiscoverResponse(
            tools=tools_data,
            num_discovered=len(tools_data),
            sources_searched=request.sources
        )

    except Exception as e:
        logger.error("toolai_discover_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-content", response_model=GenerateContentResponse)
async def generate_content(request: GenerateContentRequest):
    """
    ✍️ Generate SEO-optimized content for a ToolAI post.

    Takes discovered tools and generates:
    - Italian title, summary, and content
    - Optional English and Spanish translations
    - SEO metadata (description, keywords)
    """
    logger.info(
        "toolai_content_request",
        num_tools=len(request.tools),
        target_date=request.target_date,
        translate=request.translate
    )

    agent = ToolContentAgent()

    try:
        # Convert dict tools back to DiscoveredTool objects
        tools = [DiscoveredTool(**t) for t in request.tools]

        # Parse target date
        target_date = datetime.fromisoformat(request.target_date.replace("Z", "+00:00"))

        # Generate content
        content = await agent.generate_content(
            tools=tools,
            target_date=target_date,
            translate=request.translate,
        )

        logger.info("toolai_content_success", ai_model=content.ai_model)

        return GenerateContentResponse(
            title_it=content.title_it,
            title_en=content.title_en,
            title_es=content.title_es,
            summary_it=content.summary_it,
            summary_en=content.summary_en,
            summary_es=content.summary_es,
            content_it=content.content_it,
            content_en=content.content_en,
            content_es=content.content_es,
            insights_it=content.insights_it,
            insights_en=content.insights_en,
            insights_es=content.insights_es,
            takeaway_it=content.takeaway_it,
            takeaway_en=content.takeaway_en,
            takeaway_es=content.takeaway_es,
            meta_description=content.meta_description,
            meta_keywords=content.meta_keywords,
            ai_model=content.ai_model,
        )

    except Exception as e:
        logger.error("toolai_content_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check for ToolAI service."""
    return {"status": "healthy", "service": "toolai"}
