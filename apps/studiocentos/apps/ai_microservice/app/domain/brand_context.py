"""
Brand Context Helper - RAG-Powered Brand DNA Injection.

Provides a unified interface for agents to retrieve brand guidelines,
visual styles, and prompt templates from the RAG system.

Usage:
    from app.domain.brand_context import get_brand_context

    # In your agent:
    brand_ctx = await get_brand_context("content_generation")
    prompt = f"{brand_ctx}\\n\\n{your_task_prompt}"
"""

from typing import Optional, Dict, Any
from app.core.logging import get_logger
from app.domain.rag.service import rag_service

logger = get_logger(__name__)


# Default brand context when RAG is not available
DEFAULT_BRAND_CONTEXT = """
[BRAND DNA - StudioCentOS]

IDENTITY:
- Name: StudioCentOS
- Tagline: "Prima Agenzia AI Salerno"
- Location: Salerno, Campania, Italia

VISUAL IDENTITY:
- Primary Color: GOLD #D4AF37 (Luxury, Professionalism)
- Background: #0A0A0A (Deep Black)
- Text: #FAFAFA (White)
- Font: Inter (Sans-Serif, Modern)

TONE OF VOICE:
- Authoritative but Accessible
- Direct & Value-Driven
- Focus on ROI and "Concretezza"
- Empathetic to PMI struggles

FORBIDDEN:
- "Magia" (say "Tecnologia" instead)
- Rainbow/Neon colors
- Spammy emojis (max 1-2)
"""


async def get_brand_context(
    context_type: str = "general",
    max_tokens: int = 1500,
    client_id: Optional[int] = None
) -> str:
    """
    Retrieve brand context from RAG for injection into agent prompts.
    Supports client-specific brand DNA retrieval.

    Args:
        context_type: Type of context needed ("visual", "content", "campaign", "general")
        max_tokens: Maximum context length
        client_id: ID of the client content is being generated for behavior (None = StudioCentOS default)

    Returns:
        Brand context string to prepend to prompts
    """
    try:
        # Build query based on context type
        query_map = {
            "visual": "brand identity color palette gold typography image generation style",
            "content": "brand identity tone voice content generation copywriting",
            "campaign": "campaign kit instagram post carousel reel structure",
            "general": "brand identity guidelines studiocentos",
        }

        query = query_map.get(context_type, query_map["general"])
        
        # If specific client, refine query
        rag_user_id = 1 # Default system user
        if client_id:
             query = f"{query} client_id:{client_id}"
             rag_user_id = client_id

        # Try RAG first
        context = await rag_service.get_context(
            query=query,
            max_tokens=max_tokens,
            user_id=rag_user_id
        )

        if context:
            logger.info(
                "brand_context_retrieved",
                context_type=context_type,
                context_length=len(context)
            )
            return f"[BRAND CONTEXT FROM KNOWLEDGE BASE]\n\n{context}\n\n[END BRAND CONTEXT]"

    except Exception as e:
        logger.warning("brand_context_rag_failed", error=str(e))

    # Fallback to hardcoded defaults
    logger.info("brand_context_using_defaults", context_type=context_type)
    return DEFAULT_BRAND_CONTEXT


async def get_visual_prompt_enhancement(
    base_prompt: str,
    style: str = "professional"
) -> str:
    """
    Enhance an image generation prompt with brand visual guidelines from RAG.

    Args:
        base_prompt: The original image description
        style: Visual style preset

    Returns:
        Enhanced prompt with brand styling
    """
    try:
        # Query RAG for visual guidelines
        context = await rag_service.get_context(
            query=f"image generation {style} visual prompt nano banana veo",
            max_tokens=500
        )

        if context:
            return f"""
{base_prompt}

[APPLY BRAND VISUAL GUIDELINES]
{context}

Style: Cinematic, High Resolution.
Colors: Primary Gold #D4AF37, Background #0A0A0A.
Quality: 8K, Ultra-Detailed.
Negative: No rainbow, no neon pink/green, no cartoon, no blur.
"""

    except Exception as e:
        logger.warning("visual_prompt_enhancement_failed", error=str(e))

    # Fallback
    return f"""
{base_prompt}

Style: Cinematic, Ultra-realistic, 8k resolution.
Lighting: Volumetric Gold lighting, moody deep blacks.
Colors: Dominant #0A0A0A (Black), Accents #D4AF37 (Gold).
Negative: Cartoon, low poly, neon pink/green, cluttered, messy.
"""


async def get_campaign_kit(kit_name: str) -> Optional[str]:
    """
    Retrieve a specific campaign kit by name from RAG.

    Args:
        kit_name: Name of the kit (e.g., "announcement", "case_study")

    Returns:
        Campaign kit content or None if not found
    """
    try:
        results = await rag_service.search(
            query=f"campaign kit {kit_name}",
            top_k=1,
            min_score=0.5
        )

        if results:
            return results[0].document.text

    except Exception as e:
        logger.warning("campaign_kit_retrieval_failed", kit=kit_name, error=str(e))

    return None
