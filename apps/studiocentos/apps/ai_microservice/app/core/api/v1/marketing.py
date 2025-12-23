"""Marketing Agents API Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum
import httpx
import os
from app.core.security import verify_api_key
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)
router = APIRouter(dependencies=[Depends(verify_api_key)])

class ContentRequest(BaseModel):
    type: str = Field(..., description="blog, social, ad, video")
    topic: str
    tone: str = "professional"
    platform: Optional[str] = None
    brand_context: Optional[str] = None

class ContentResponse(BaseModel):
    content: str
    metadata: dict
    provider: str = "huggingface"

# LEGACY CODE REMOVED - Using ContentCreatorAgent instead
# generate_with_ai() removed to eliminate duplication

@router.post("/content/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest):
    """
    Standard Content Generation (Refactored to use ContentCreatorAgent)
    """
    try:
        logger.info("generate_content_agent", type=request.type, topic=request.topic[:50])

        # Import imports locally
        from app.domain.marketing.content_creator import (
            ContentCreatorAgent, AgentConfig, BlogPostConfig,
            SocialPostConfig, SocialPlatform, ContentTone, ContentType
        )

        # Initialize Agent
        agent = ContentCreatorAgent(
            config=AgentConfig(
                id="marketing_agent_standard",
                agent_type="marketing_content_creator",
                name="StudioCentOS Standard Creator",
                model="llama-3.3-70b-versatile",
                temperature=0.7
            )
        )
        await agent.on_start()

        content = ""
        metadata = {}

        if request.type == "blog":
            config = BlogPostConfig(
                topic=request.topic,
                tone=ContentTone.PROFESSIONAL, # Map from request.tone string if needed
                keywords=[],
                brand_context=request.brand_context
            )
            result = await agent.generate_blog_post(config)
            content = result.content
            metadata = result.metadata

        elif request.type == "social":
            # Map platform from request or default
            platform = SocialPlatform.LINKEDIN # Default safe
            if request.platform:
                try:
                    platform = SocialPlatform(request.platform.lower())
                except ValueError:
                    pass

            config = SocialPostConfig(
                platform=platform,
                message=request.topic,
                tone=ContentTone.PROFESSIONAL,
                brand_context=request.brand_context,
                post_type="educational" # Default
            )
            result = await agent.generate_social_post(config)
            content = result.content
            metadata = result.metadata

        else:
            # Fallback direct generation via internal helper or just error
            # Let's map ad/video too if possible, or just use social as generic
            config = SocialPostConfig(
                platform=SocialPlatform.LINKEDIN,
                message=f"[{request.type.upper()}] {request.topic}",
                tone=ContentTone.PROFESSIONAL,
                brand_context=request.brand_context
            )
            result = await agent.generate_social_post(config)
            content = result.content
            metadata = result.metadata

        return ContentResponse(
            content=content,
            metadata=metadata,
            provider="groq-llama-3.3"
        )

    except Exception as e:
        logger.error("generate_content_error", error=str(e), exc_info=True)
        # Fallback to simple message to avoid crash
        return ContentResponse(
            content=f"Errore nella generazione: {str(e)}. Riprova.",
            metadata={"status": "error"},
            provider="system"
        )

@router.get("/")
async def marketing_root():
    return {
        "service": "marketing",
        "status": "available",
        "agents": 5,
        "provider": "huggingface",
        "features": ["blog", "social", "ad", "video", "leads", "generate-pro"]
    }


# ============================================================================
# PROFESSIONAL CONTENT GENERATION - FULL BRAND DNA INTEGRATION
# ============================================================================

from app.domain.marketing.content_creator import (
    BRAND_DNA,
    POST_TYPE_PROMPTS,
    PLATFORM_FORMAT_RULES,
    get_brand_dna_prompt,
)

class ProContentRequest(BaseModel):
    """Request for professional content generation with full Brand DNA."""
    post_type: str = Field(
        default="educational",
        description="Post type: lancio_prodotto, tip_giorno, caso_successo, trend_settore, offerta_speciale, ai_business, educational, testimonial, engagement"
    )
    platform: str = Field(
        default="instagram",
        description="Platform: instagram, linkedin, facebook, twitter, tiktok, threads"
    )
    topic: str = Field(..., description="Main topic/subject of the post")
    sector: str = Field(
        default="tech",
        description="Industry sector: ristorazione, hospitality, legal, medical, retail, manufacturing, tech, consulting"
    )
    additional_context: Optional[str] = Field(
        default=None,
        description="Additional context, product details, or specific requirements"
    )
    language: str = Field(default="it", description="Language: it, en")
    generate_image_prompt: bool = Field(
        default=True,
        description="Also generate a matching image prompt"
    )
    brand_context: Optional[str] = Field(
        default=None,
        description="Brand context from frontend for personalization"
    )

class ProContentResponse(BaseModel):
    """Response with professional generated content."""
    content: str
    image_prompt: Optional[str] = None
    hashtags: List[str]
    cta_options: List[str]
    metadata: dict
    provider: str = "groq"

# Image style mapping per post type
IMAGE_STYLE_BY_POST_TYPE = {
    "lancio_prodotto": {
        "style": "creative",
        "mood": "exciting, innovative, new",
        "composition": "product focus, dynamic angles, bold colors",
        "elements": "product showcase, launch graphics, celebration",
    },
    "tip_giorno": {
        "style": "minimal",
        "mood": "helpful, clear, educational",
        "composition": "clean layout, numbered steps, visual guide",
        "elements": "lightbulb icons, checklist visual, how-to graphic",
    },
    "caso_successo": {
        "style": "professional",
        "mood": "success, achievement, trust",
        "composition": "before/after, metrics graphics, testimonial",
        "elements": "graphs, charts, success icons, trophy",
    },
    "trend_settore": {
        "style": "tech",
        "mood": "forward-thinking, analytical, informative",
        "composition": "data visualization, trend lines, futuristic",
        "elements": "charts, arrows, trend indicators",
    },
    "offerta_speciale": {
        "style": "creative",
        "mood": "urgent, valuable, exclusive",
        "composition": "bold text emphasis, discount graphics, countdown",
        "elements": "sale badge, percentage, timer, special offer tag",
    },
    "ai_business": {
        "style": "tech",
        "mood": "innovative, futuristic, accessible",
        "composition": "AI visualization, neural networks, automation",
        "elements": "robot, brain, circuits, automation icons",
    },
    "educational": {
        "style": "minimal",
        "mood": "informative, structured, clear",
        "composition": "step-by-step, numbered list, infographic",
        "elements": "books, graduation cap, lightbulb, process flow",
    },
    "testimonial": {
        "style": "elegant",
        "mood": "trustworthy, authentic, professional",
        "composition": "quote marks, person silhouette, stars",
        "elements": "5-star rating, quote bubble, satisfied customer",
    },
    "engagement": {
        "style": "creative",
        "mood": "fun, interactive, conversational",
        "composition": "question mark, poll visual, conversation",
        "elements": "speech bubbles, emoji, hands up, community",
    },
}

# Sector-specific modifiers for images
SECTOR_IMAGE_CONTEXT = {
    "ristorazione": "Italian restaurant ambiance, food photography, warm lighting, appetizing dishes, chef, kitchen",
    "hospitality": "luxury hotel lobby, concierge, travel, elegant rooms, hospitality service",
    "legal": "law office, legal documents, professional setting, scales of justice, formal attire",
    "medical": "healthcare, clean medical environment, doctor, patient care, medical technology",
    "retail": "store display, shopping experience, product showcase, retail environment, customer",
    "manufacturing": "industrial setting, production line, quality control, made in Italy, factory floor",
    "tech": "modern office, computer screens, technology workspace, coding, innovation lab",
    "consulting": "business meeting, strategy session, boardroom, professional discussion, charts",
}

@router.post("/content/generate-pro", response_model=ProContentResponse)
async def generate_content_pro(request: ProContentRequest):
    """
    PROFESSIONAL Content Generation with ContentCreatorAgent (Llama-3.3-70B)
    """
    try:
        logger.info("generate_content_pro_agent",
                    post_type=request.post_type,
                    platform=request.platform,
                    sector=request.sector,
                    topic=request.topic[:50] if request.topic else "")

        # 1. Initialize Agent (Lazy or Global)
        # In a real scenario, this should be dependency injected or global singleton
        # For now, we instantiate here to ensure fresh config matching request

        # Prepare Brand Context for Agent
        agent_brand_context = request.brand_context
        if request.sector:
            agent_brand_context = f"{agent_brand_context or ''}\nSETTORE TARGET: {request.sector}"

        if request.additional_context:
            agent_brand_context = f"{agent_brand_context or ''}\nCONTESTO EXTRA: {request.additional_context}"

        # Import locally to avoid circular deps if any, though top level is fine
        from app.domain.marketing.content_creator import (
            ContentCreatorAgent, AgentConfig, SocialPostConfig,
            SocialPlatform, ContentTone
        )

        # Create Agent Instance
        agent = ContentCreatorAgent(
            config=AgentConfig(
                id="marketing_agent_pro",
                agent_type="marketing_content_creator",
                name="StudioCentOS Pro Creator",
                model="llama-3.3-70b-versatile", # POWERHOUSE MODEL
                temperature=0.7
            )
        )
        await agent.on_start() # Load resources

        # 2. Generate TEXT using Agent
        social_config = SocialPostConfig(
            platform=request.platform,
            message=request.topic,
            post_type=request.post_type,
            tone="professional",
            brand_context=agent_brand_context,
            include_hashtags=True, # Agent generates them in text
            include_emojis=True
        )

        # Execute Agent Logic
        result = await agent.generate_social_post(social_config)
        content = result.content

        # 3. Generate IMAGE PROMPT (Using existing Premium Logic)
        image_prompt = None
        if request.generate_image_prompt:
            image_style = IMAGE_STYLE_BY_POST_TYPE.get(
                request.post_type,
                IMAGE_STYLE_BY_POST_TYPE["educational"]
            )
            sector_context = SECTOR_IMAGE_CONTEXT.get(
                request.sector,
                SECTOR_IMAGE_CONTEXT["tech"]
            )

            # PREMIUM PROMPT CONSTRUCTION (Preserved from previous fix)
            image_prompt = f"""
Create a PREMIUM marketing image for StudioCentOS - Italian tech excellence.

SUBJECT: {request.topic}

VISUAL STYLE: {image_style["style"]}
MOOD: {image_style["mood"]} - Modern, high-end, prestigious
COMPOSITION: {image_style["composition"]} - Clean focal point, professional layout

KEY ELEMENTS: {image_style["elements"]}

SECTOR CONTEXT: {sector_context}

🎨 BRAND COLORS (MANDATORY):
- Primary accent: GOLD METALLIC (#D4AF37) - luxurious gold highlights
- Background: Either pure BLACK (#0A0A0A) or clean WHITE (#FAFAFA)
- Accent gradients: Dark gold to light gold
- NO BLUE, NO GENERIC COLORS - exclusively gold/black/white palette

✨ PREMIUM REQUIREMENTS:
- Ultra high quality, 8K resolution, professional photography style
- Modern glassmorphism or gradient effects where appropriate
- Clean, minimalist composition with strong visual hierarchy
- Italian excellence and innovation feel
- Subtle StudioCentOS branding: small gold "S" logo in corner (10% opacity)
- NO text overlays, NO watermarks, NO stock photo feel
- Format: {request.platform} optimized dimensions
- Premium tech aesthetic: sleek, polished, sophisticated
""".strip()

        # 4. Helpers (Hashtags & CTAs)
        # Extract hashtags from content (Agent adds them at the end usually)
        import re
        generated_hashtags = re.findall(r"#\w+", content)
        # Fallback if no hashtags found
        if not generated_hashtags:
            base_hashtags = list(BRAND_DNA["hashtags"]["brand"])
            generated_hashtags = base_hashtags[:5]

        # CTA Options (Static fallback for UI buttons)
        cta_options_map = {
            "lancio_prodotto": ["Prenota una demo gratuita →", "Scopri tutte le funzionalità →", "Contattaci ora"],
            "tip_giorno": ["Salva questo post 📌", "Condividi il tip", "Seguici per altri consigli"],
            "educational": ["Salva per dopo 📌", "Condividi con colleghi", "Approfondisci sul sito"],
            "offerta_speciale": ["Blocca l'offerta", "Acquista ora", "Richiedi info"],
        }
        cta_options = cta_options_map.get(request.post_type, cta_options_map["educational"])

        return ProContentResponse(
            content=content,
            image_prompt=image_prompt,
            hashtags=generated_hashtags,
            cta_options=cta_options,
            metadata={
                "post_type": request.post_type,
                "platform": request.platform,
                "sector": request.sector,
                "agent": "ContentCreatorAgent",
                "model": "llama-3.3-70b"
            },
            provider="groq"
        )

    except Exception as e:
        logger.error("generate_content_pro_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 🚀 POWER CONTENT FORMAT GENERATION - Story/Carousel/Reel MASTER ENGINE
# ============================================================================

class ContentFormatType(str, Enum):
    """Content format types for different content structures."""
    POST = "post"           # Standard social post
    STORY = "story"         # Multi-slide ephemeral content (IG/FB Stories)
    CAROUSEL = "carousel"   # Swipeable multi-slide educational content
    REEL = "reel"           # Short-form video (15-90 sec)
    VIDEO = "video"         # Long-form video script

from enum import Enum

class SlideContent(BaseModel):
    """Individual slide/scene content."""
    slide_num: int
    slide_type: str  # hook, content, recap, cta
    title: str = ""
    content: str
    bullets: List[str] = []
    visual_prompt: Optional[str] = None  # AI image prompt for this slide
    text_overlay: Optional[str] = None
    duration_seconds: Optional[int] = None  # For video/story
    stickers: List[str] = []  # Suggested stickers
    music_mood: Optional[str] = None
    transition: Optional[str] = None

class FormatContentRequest(BaseModel):
    """
    🚀 POWER Request for format-specific content generation.

    Supports: post, story, carousel, reel, video
    Full Brand DNA integration + Platform optimization
    """
    content_format: str = Field(
        default="post",
        description="Content format: post, story, carousel, reel, video"
    )
    post_type: str = Field(
        default="educational",
        description="Post type template: lancio_prodotto, tip_giorno, caso_successo, trend_settore, offerta_speciale, ai_business, educational, testimonial, engagement"
    )
    platform: str = Field(
        default="instagram",
        description="Target platform: instagram, linkedin, facebook, twitter, tiktok, youtube"
    )
    topic: str = Field(..., description="Main topic/subject")
    sector: str = Field(
        default="tech",
        description="Industry sector for context"
    )
    # Format-specific options
    num_slides: int = Field(
        default=7, ge=3, le=10,
        description="Number of slides for story/carousel (3-10)"
    )
    duration_seconds: int = Field(
        default=30, ge=15, le=600,
        description="Duration for reel/video in seconds"
    )
    video_style: str = Field(
        default="educational",
        description="Video style: educational, promotional, entertaining, tutorial, testimonial"
    )
    music_mood: str = Field(
        default="upbeat",
        description="Music mood: upbeat, chill, dramatic, trending, corporate"
    )
    # Generation options
    generate_image_prompts: bool = Field(
        default=True,
        description="Generate AI image prompts for each slide"
    )
    include_stickers: bool = Field(
        default=True,
        description="Include sticker suggestions for stories"
    )
    include_music: bool = Field(
        default=True,
        description="Include music suggestions"
    )
    # Context
    additional_context: Optional[str] = None
    brand_context: Optional[str] = None
    language: str = Field(default="it")

class FormatContentResponse(BaseModel):
    """
    🚀 POWER Response with structured format-specific content.

    Contains slides/scenes with individual image prompts and metadata.
    """
    content_format: str
    main_content: str  # Combined content for quick copy
    caption: str  # Platform caption/description
    slides: List[SlideContent] = []  # Individual slides for carousel/story
    scenes: List[SlideContent] = []  # Video scenes for reel/video
    # Aggregated elements
    hashtags: List[str]
    cta_options: List[str]
    cover_image_prompt: Optional[str] = None  # Cover/thumbnail prompt
    # Metadata
    metadata: Dict
    provider: str = "groq-llama-3.3-70b"


# ============================================================================
# 🎯 MASTER PROMPTS ENGINE - Ultra-Specialized Templates
# ============================================================================

MASTER_STORY_PROMPT = """
🎬 MASTER STORY CREATOR - STUDIOCENTOS AI ENGINE

Sei il MASTER STORY CREATOR di StudioCentOS. Crei Stories che FERMANO lo scroll e generano AZIONI.

{brand_dna}

═══════════════════════════════════════════════════════════════
📱 FORMATO: INSTAGRAM/FACEBOOK STORY - {num_slides} SLIDE
═══════════════════════════════════════════════════════════════

ARGOMENTO: {topic}
TIPO POST: {post_type}
SETTORE: {sector}

{post_type_structure}

═══════════════════════════════════════════════════════════════
🎯 STRUTTURA STORY PERFETTA
═══════════════════════════════════════════════════════════════

SLIDE 1 - HOOK (15 sec):
┌─────────────────────────────────────┐
│ 🔥 PATTERN INTERRUPT                │
│ • Domanda shock o statistica        │
│ • Testo GRANDE e leggibile          │
│ • MAX 10 parole                     │
│ • Emoji accattivante iniziale       │
│ • Sfondo: gradiente oro/nero        │
└─────────────────────────────────────┘

SLIDE 2-{mid_slides} - CONTENUTO:
┌─────────────────────────────────────┐
│ 📝 VALUE DELIVERY                   │
│ • UN singolo concetto per slide     │
│ • Bullet point visivo               │
│ • Progressione numerata (1/X, 2/X)  │
│ • Emoji descrittiva                 │
│ • MAX 20 parole per slide           │
└─────────────────────────────────────┘

SLIDE FINALE - CTA:
┌─────────────────────────────────────┐
│ ✨ CALL TO ACTION                   │
│ • Urgenza + beneficio               │
│ • "Swipe up" / "Link in bio" / "DM" │
│ • Logo StudioCentOS                 │
│ • Emoji azione: 👉 🔗 💬            │
└─────────────────────────────────────┘

═══════════════════════════════════════════════════════════════
📋 OUTPUT RICHIESTO (JSON-like per ogni slide)
═══════════════════════════════════════════════════════════════

Per OGNI slide genera:

---SLIDE [N]---
TIPO: [hook/content/cta]
TESTO_PRINCIPALE: [max 20 parole, diretto]
TESTO_OVERLAY: [testo secondario se serve]
VISUAL_PROMPT: [prompt immagine AI dettagliato per questa slide]
STICKERS: [quiz/poll/countdown/emoji_slider/link/contact]
MUSICA: [mood: upbeat/dramatic/chill]
TRANSIZIONE: [swipe/fade/zoom]
---

GENERA TUTTE LE {num_slides} SLIDE:
"""

MASTER_CAROUSEL_PROMPT = """
🎠 MASTER CAROUSEL CREATOR - STUDIOCENTOS AI ENGINE

Sei il MASTER CAROUSEL CREATOR di StudioCentOS. Crei Carousel EDUCATIVI che vengono SALVATI e CONDIVISI.

{brand_dna}

═══════════════════════════════════════════════════════════════
📚 FORMATO: CAROUSEL EDUCATIVO - {num_slides} SLIDE
═══════════════════════════════════════════════════════════════

ARGOMENTO: {topic}
TIPO POST: {post_type}
SETTORE: {sector}
PIATTAFORMA: {platform}

{post_type_structure}

═══════════════════════════════════════════════════════════════
🎯 STRUTTURA CAROUSEL VIRALE
═══════════════════════════════════════════════════════════════

SLIDE 1 - COVER (FERMA LO SCROLL):
┌─────────────────────────────────────┐
│ 🎯 TITOLO POWER                     │
│ • Pattern: "X Modi per..."          │
│ • Pattern: "La Guida Definitiva a"  │
│ • Pattern: "[Numero] Errori che..."│
│ • Sottotitolo value proposition     │
│ • Sfondo premium nero/oro           │
│ • Logo discreto in corner           │
└─────────────────────────────────────┘

SLIDE 2 - CONTESTO/PROBLEMA:
┌─────────────────────────────────────┐
│ ❓ PERCHÉ QUESTO ARGOMENTO          │
│ • Statistica impattante             │
│ • Problema che il target vive       │
│ • "Ti riconosci?"                   │
│ • Anticipo della soluzione          │
└─────────────────────────────────────┘

SLIDE 3-{content_end} - CONTENUTO CORE:
┌─────────────────────────────────────┐
│ 📖 UN CONCETTO PER SLIDE            │
│ • Titolo numerato (1., 2., 3...)    │
│ • 2-3 bullet points max             │
│ • Esempio pratico o dato            │
│ • Visual coerente con serie         │
└─────────────────────────────────────┘

SLIDE {recap_num} - RECAP:
┌─────────────────────────────────────┐
│ 📋 RIASSUNTO VISIVO                 │
│ • Lista numerata takeaway           │
│ • "Ricorda:"                        │
│ • Checklist visiva                  │
└─────────────────────────────────────┘

SLIDE {num_slides} - CTA:
┌─────────────────────────────────────┐
│ ✨ CALL TO ACTION FINALE            │
│ • "Salva per dopo 📌"               │
│ • "Condividi con chi..."            │
│ • Logo + tagline                    │
│ • Next step chiaro                  │
└─────────────────────────────────────┘

═══════════════════════════════════════════════════════════════
📋 OUTPUT RICHIESTO
═══════════════════════════════════════════════════════════════

Per OGNI slide genera:

---SLIDE [N]---
TIPO: [cover/context/content/recap/cta]
TITOLO: [titolo slide - max 8 parole]
CORPO: [contenuto principale - 2-3 frasi]
BULLETS: [punto 1] | [punto 2] | [punto 3]
VISUAL_PROMPT: [prompt immagine AI dettagliato - stile coerente serie]
DATA_POINT: [statistica o numero se rilevante]
---

GENERA CAPTION POST:
[Caption coinvolgente che accompagna il carousel - max 2000 char]
[Include: hook, value preview, CTA, hashtag]

GENERA TUTTE LE {num_slides} SLIDE:
"""

MASTER_REEL_PROMPT = """
🎬 MASTER REEL CREATOR - STUDIOCENTOS AI ENGINE

Sei il MASTER REEL CREATOR di StudioCentOS. Crei Reel/TikTok che diventano VIRALI.

{brand_dna}

═══════════════════════════════════════════════════════════════
🎥 FORMATO: REEL/TIKTOK - {duration} SECONDI
═══════════════════════════════════════════════════════════════

ARGOMENTO: {topic}
TIPO POST: {post_type}
SETTORE: {sector}
STILE VIDEO: {video_style}
MUSICA MOOD: {music_mood}

{post_type_structure}

═══════════════════════════════════════════════════════════════
🎯 STRUTTURA REEL VIRALE
═══════════════════════════════════════════════════════════════

⏱️ 0-3 SEC - HOOK (FERMA LO SCROLL!):
┌─────────────────────────────────────┐
│ 🔥 PATTERN INTERRUPT                │
│ • Movimento/zoom improvviso         │
│ • Statement controverso/shock       │
│ • "POV:" / "Aspetta..." / "Stop!"   │
│ • Testo GRANDE centro schermo       │
│ • Audio: beat drop o trending sound │
└─────────────────────────────────────┘

⏱️ 3-{hook_end} SEC - PROBLEMA/CURIOSITÀ:
┌─────────────────────────────────────┐
│ 😱 BUILD TENSION                    │
│ • "Ti è mai capitato di..."         │
│ • Situazione riconoscibile          │
│ • Pain point del target             │
│ • Audio: build-up musicale          │
└─────────────────────────────────────┘

⏱️ {hook_end}-{solution_end} SEC - SOLUZIONE:
┌─────────────────────────────────────┐
│ 💡 VALUE BOMB                       │
│ • Tutorial step-by-step             │
│ • Demo pratica                      │
│ • Reveal sorprendente               │
│ • Testo animato per punti chiave    │
│ • Audio: peak energia               │
└─────────────────────────────────────┘

⏱️ {solution_end}-{duration} SEC - CTA + LOOP:
┌─────────────────────────────────────┐
│ ✨ CHIUSURA VIRALE                  │
│ • CTA diretta: "Segui per altri"    │
│ • Collegamento a frame 1 (loop)     │
│ • Logo StudioCentOS                 │
│ • Audio: chiusura clean             │
│ • "Salva per dopo 📌"               │
└─────────────────────────────────────┘

═══════════════════════════════════════════════════════════════
📋 OUTPUT RICHIESTO
═══════════════════════════════════════════════════════════════

Per OGNI scena genera:

---SCENA [TIMESTAMP]---
NOME: [nome scena]
VISUAL: [descrizione ESATTA di cosa si vede - camera, movimenti, elementi]
NARRAZIONE: "[TESTO ESATTO da dire - virgolette obbligatorie]"
TESTO_SCREEN: [testo che appare a schermo - posizione, stile]
AUDIO: [musica, effetti, timing]
TRANSIZIONE: [cut/zoom/swipe/fade + direzione]
THUMBNAIL_WORTHY: [sì/no - questa scena può essere thumbnail?]
---

GENERA CAPTION:
[Caption breve e accattivante - max 150 char per TikTok, 2200 per IG]
[Hashtag trending + brand]

GENERA THUMBNAIL_PROMPT:
[Prompt dettagliato per thumbnail che genera click]

GENERA LO SCRIPT COMPLETO:
"""


# ============================================================================
# 🚀 POWER ENDPOINT - /content/generate-format
# ============================================================================

@router.post("/content/generate-format", response_model=FormatContentResponse)
async def generate_content_format(request: FormatContentRequest):
    """
    🚀 POWER Content Generation with FORMAT DISPATCH

    Generates format-specific content using specialized methods:
    - POST: Standard social post with structure
    - STORY: Multi-slide ephemeral content (5-10 slides)
    - CAROUSEL: Educational swipeable content (7-10 slides)
    - REEL: Video script with scenes and timing
    - VIDEO: Long-form video script

    Returns structured content with slides[], scenes[], and image prompts.
    """
    try:
        logger.info("generate_content_format",
                    format=request.content_format,
                    post_type=request.post_type,
                    platform=request.platform,
                    topic=request.topic[:50])

        # 1. Import Agent components
        from app.domain.marketing.content_creator import (
            ContentCreatorAgent, AgentConfig,
            SocialPostConfig, StoryConfig, CarouselConfig, ReelConfig,
            SocialPlatform, ContentTone,
            get_brand_dna_prompt, POST_TYPE_PROMPTS
        )

        # 2. Prepare contexts
        brand_dna = get_brand_dna_prompt()
        post_type_structure = POST_TYPE_PROMPTS.get(
            request.post_type,
            POST_TYPE_PROMPTS.get("educational", "")
        )

        agent_brand_context = request.brand_context or ""
        if request.sector:
            agent_brand_context += f"\nSETTORE TARGET: {request.sector}"
        if request.additional_context:
            agent_brand_context += f"\nCONTESTO: {request.additional_context}"

        # 3. Create Agent
        agent = ContentCreatorAgent(
            config=AgentConfig(
                id="power_format_agent",
                agent_type="marketing_content_creator",
                name="StudioCentOS POWER Creator",
                model="llama-3.3-70b-versatile",
                temperature=0.75
            )
        )
        await agent.on_start()

        # 4. DISPATCH to correct generation method
        slides = []
        scenes = []
        main_content = ""
        caption = ""
        cover_prompt = None

        content_format = request.content_format.lower()

        if content_format == "story":
            # 📱 STORY GENERATION
            result = await _generate_power_story(
                agent, request, brand_dna, post_type_structure
            )
            slides = result["slides"]
            main_content = result["main_content"]
            caption = result["caption"]
            cover_prompt = result.get("cover_prompt")

        elif content_format == "carousel":
            # 🎠 CAROUSEL GENERATION
            result = await _generate_power_carousel(
                agent, request, brand_dna, post_type_structure
            )
            slides = result["slides"]
            main_content = result["main_content"]
            caption = result["caption"]
            cover_prompt = result.get("cover_prompt")

        elif content_format == "reel":
            # 🎬 REEL GENERATION
            result = await _generate_power_reel(
                agent, request, brand_dna, post_type_structure
            )
            scenes = result["scenes"]
            main_content = result["main_content"]
            caption = result["caption"]
            cover_prompt = result.get("thumbnail_prompt")

        elif content_format == "video":
            # 🎥 VIDEO GENERATION (long-form)
            result = await _generate_power_video(
                agent, request, brand_dna, post_type_structure
            )
            scenes = result["scenes"]
            main_content = result["main_content"]
            caption = result["caption"]
            cover_prompt = result.get("thumbnail_prompt")

        else:
            # 📝 POST GENERATION (default)
            platform_enum = SocialPlatform.INSTAGRAM
            try:
                platform_enum = SocialPlatform(request.platform.lower())
            except ValueError:
                pass

            social_config = SocialPostConfig(
                platform=platform_enum,
                message=request.topic,
                post_type=request.post_type,
                tone=ContentTone.PROFESSIONAL,
                brand_context=agent_brand_context,
                include_hashtags=True,
                include_emojis=True
            )
            result = await agent.generate_social_post(social_config)
            main_content = result.content
            caption = result.content

        # 5. Extract hashtags
        import re
        hashtags = re.findall(r"#\w+", main_content + caption)
        if not hashtags:
            hashtags = list(BRAND_DNA["hashtags"]["brand"])[:5]

        # 6. Generate CTA options
        cta_map = {
            "story": ["Swipe up →", "Link in bio", "Rispondi in DM 💬", "Guarda la prossima storia →"],
            "carousel": ["Salva per dopo 📌", "Condividi con un collega", "Seguici per altri tips", "Commenta il tuo preferito 👇"],
            "reel": ["Segui per altri tips!", "Salva questo reel 📌", "Condividi con chi ne ha bisogno", "Parte 2? Commenta 👇"],
            "video": ["Iscriviti al canale 🔔", "Lascia un like 👍", "Commenta la tua domanda", "Condividi il video"],
            "post": ["Contattaci →", "Scopri di più", "Salva questo post 📌", "Link in bio"],
        }
        cta_options = cta_map.get(content_format, cta_map["post"])

        # 7. Build response
        return FormatContentResponse(
            content_format=content_format,
            main_content=main_content,
            caption=caption,
            slides=slides,
            scenes=scenes,
            hashtags=hashtags[:20],
            cta_options=cta_options,
            cover_image_prompt=cover_prompt,
            metadata={
                "content_format": content_format,
                "post_type": request.post_type,
                "platform": request.platform,
                "sector": request.sector,
                "num_slides": len(slides) if slides else 0,
                "num_scenes": len(scenes) if scenes else 0,
                "duration_seconds": request.duration_seconds if content_format in ["reel", "video"] else None,
                "agent": "ContentCreatorAgent-POWER",
                "model": "llama-3.3-70b"
            },
            provider="groq-llama-3.3-70b"
        )

    except Exception as e:
        logger.error("generate_content_format_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 📱 STORY GENERATION - Power Implementation
# ============================================================================

async def _generate_power_story(
    agent,
    request: FormatContentRequest,
    brand_dna: str,
    post_type_structure: str
) -> Dict:
    """Generate POWER Story content with individual slide prompts."""
    from app.core.llm.groq_client import get_groq_client

    num_slides = request.num_slides
    mid_slides = num_slides - 1

    # Build MASTER prompt
    prompt = MASTER_STORY_PROMPT.format(
        brand_dna=brand_dna,
        num_slides=num_slides,
        mid_slides=mid_slides,
        topic=request.topic,
        post_type=request.post_type,
        sector=request.sector,
        post_type_structure=post_type_structure
    )

    # Generate with GROQ
    client = get_groq_client(model="llama-3.3-70b")
    raw_content = await client.generate(
        prompt=prompt,
        system_prompt=f"""Sei il MASTER STORY CREATOR di StudioCentOS.
Genera Stories VIRALI con struttura perfetta.
Rispondi SEMPRE in italiano.
Segui ESATTAMENTE il formato richiesto.""",
        temperature=0.8,
        max_tokens=3000
    )

    # Parse slides from response
    slides = _parse_story_slides(raw_content, num_slides, request)

    # Generate main content summary
    main_content = _format_story_main_content(slides)

    # Generate caption
    caption_prompt = f"""Genera una CAPTION breve per questa Story su {request.topic}.
Max 150 caratteri. Include emoji e 3 hashtag brand: #StudioCentOS #AIperPMI #DigitalizzazionePMI"""

    caption = await client.generate(
        prompt=caption_prompt,
        temperature=0.7,
        max_tokens=200
    )

    # Cover prompt (slide 1 image)
    cover_prompt = slides[0].visual_prompt if slides else None

    return {
        "slides": slides,
        "main_content": main_content,
        "caption": caption.strip(),
        "cover_prompt": cover_prompt
    }


def _parse_story_slides(raw_content: str, num_slides: int, request: FormatContentRequest) -> List[SlideContent]:
    """Parse story slides from raw LLM output."""
    slides = []

    # Split by slide markers
    sections = raw_content.split("---SLIDE")

    for i, section in enumerate(sections[1:num_slides + 1], 1):
        slide_type = "hook" if i == 1 else ("cta" if i == num_slides else "content")

        slide = SlideContent(
            slide_num=i,
            slide_type=slide_type,
            content="",
            visual_prompt=None,
            stickers=[],
            duration_seconds=15
        )

        lines = section.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("TIPO:"):
                slide.slide_type = line.replace("TIPO:", "").strip().lower()
            elif line.startswith("TESTO_PRINCIPALE:"):
                slide.content = line.replace("TESTO_PRINCIPALE:", "").strip()
            elif line.startswith("TESTO_OVERLAY:"):
                slide.text_overlay = line.replace("TESTO_OVERLAY:", "").strip()
            elif line.startswith("VISUAL_PROMPT:"):
                slide.visual_prompt = line.replace("VISUAL_PROMPT:", "").strip()
            elif line.startswith("STICKERS:"):
                stickers_raw = line.replace("STICKERS:", "").strip()
                slide.stickers = [s.strip() for s in stickers_raw.split("/") if s.strip()]
            elif line.startswith("MUSICA:"):
                slide.music_mood = line.replace("MUSICA:", "").strip()
            elif line.startswith("TRANSIZIONE:"):
                slide.transition = line.replace("TRANSIZIONE:", "").strip()

        # Fallback visual prompt if not generated
        if not slide.visual_prompt:
            slide.visual_prompt = _generate_slide_visual_prompt(
                request.topic, slide_type, i, num_slides, request.sector
            )

        slides.append(slide)

    # Ensure we have the right number of slides
    while len(slides) < num_slides:
        n = len(slides) + 1
        slides.append(SlideContent(
            slide_num=n,
            slide_type="content",
            content=f"Slide {n} - Contenuto",
            visual_prompt=_generate_slide_visual_prompt(
                request.topic, "content", n, num_slides, request.sector
            ),
            duration_seconds=15
        ))

    return slides[:num_slides]


def _generate_slide_visual_prompt(topic: str, slide_type: str, slide_num: int, total: int, sector: str) -> str:
    """Generate fallback visual prompt for a slide."""
    type_prompts = {
        "hook": f"""
Premium Instagram Story slide - HOOK.
Topic: {topic}
Style: Bold, attention-grabbing, pattern interrupt.
Format: Vertical 9:16 (1080x1920).
Colors: Gold #D4AF37 accents, Black #0A0A0A background, White text.
Elements: Large bold text, question mark or exclamation, premium gradient.
Mood: Urgent, curiosity-inducing, scroll-stopping.
Sector context: {sector}.
Quality: Ultra HD, mobile-optimized.
NO: Generic stock, cluttered design, small text.
""",
        "content": f"""
Premium Instagram Story slide - CONTENT {slide_num}/{total}.
Topic: {topic}
Style: Clean, educational, visual guide.
Format: Vertical 9:16 (1080x1920).
Colors: Gold #D4AF37 accents, Black #0A0A0A background, White text.
Elements: Numbered indicator ({slide_num}/{total}), bullet point visual, icon.
Typography: Clear sans-serif, readable on mobile.
Sector context: {sector}.
Quality: Ultra HD, consistent with series.
NO: Cluttered, hard to read, inconsistent style.
""",
        "cta": f"""
Premium Instagram Story slide - CTA FINALE.
Topic: {topic}
Style: Action-oriented, branded, compelling.
Format: Vertical 9:16 (1080x1920).
Colors: Gold #D4AF37 prominent, Black #0A0A0A background.
Elements: StudioCentOS logo, arrow/swipe indicator, contact icon.
Typography: Bold CTA text, clear instruction.
Mood: Urgent but professional, trustworthy.
Sector context: {sector}.
Quality: Ultra HD, brand-aligned.
NO: Weak CTA, missing brand, unclear action.
"""
    }
    return type_prompts.get(slide_type, type_prompts["content"]).strip()


def _format_story_main_content(slides: List[SlideContent]) -> str:
    """Format slides into main content string."""
    content = "📱 INSTAGRAM STORY\n" + "=" * 40 + "\n\n"
    for slide in slides:
        content += f"SLIDE {slide.slide_num} ({slide.slide_type.upper()}):\n"
        content += f"{slide.content}\n"
        if slide.text_overlay:
            content += f"Overlay: {slide.text_overlay}\n"
        content += "\n"
    return content


# ============================================================================
# 🎠 CAROUSEL GENERATION - Power Implementation
# ============================================================================

async def _generate_power_carousel(
    agent,
    request: FormatContentRequest,
    brand_dna: str,
    post_type_structure: str
) -> Dict:
    """Generate POWER Carousel content with individual slide prompts."""
    from app.core.llm.groq_client import get_groq_client

    num_slides = request.num_slides
    content_end = num_slides - 2
    recap_num = num_slides - 1

    # Build MASTER prompt
    prompt = MASTER_CAROUSEL_PROMPT.format(
        brand_dna=brand_dna,
        num_slides=num_slides,
        content_end=content_end,
        recap_num=recap_num,
        topic=request.topic,
        post_type=request.post_type,
        sector=request.sector,
        platform=request.platform,
        post_type_structure=post_type_structure
    )

    # Generate with GROQ
    client = get_groq_client(model="llama-3.3-70b")
    raw_content = await client.generate(
        prompt=prompt,
        system_prompt=f"""Sei il MASTER CAROUSEL CREATOR di StudioCentOS.
Genera Carousel EDUCATIVI virali che vengono salvati e condivisi.
Rispondi SEMPRE in italiano.
Segui ESATTAMENTE il formato richiesto con ---SLIDE [N]---.""",
        temperature=0.75,
        max_tokens=4000
    )

    # Parse slides
    slides = _parse_carousel_slides(raw_content, num_slides, request)

    # Extract caption (look for "GENERA CAPTION" section)
    caption = ""
    if "GENERA CAPTION" in raw_content:
        caption_section = raw_content.split("GENERA CAPTION")[-1]
        # Take first paragraph after marker
        caption_lines = [l for l in caption_section.split("\n") if l.strip() and not l.startswith("---")]
        caption = "\n".join(caption_lines[:10])

    if not caption:
        # Generate caption separately
        caption = await _generate_carousel_caption(client, request, slides)

    # Main content
    main_content = _format_carousel_main_content(slides)

    # Cover prompt
    cover_prompt = slides[0].visual_prompt if slides else None

    return {
        "slides": slides,
        "main_content": main_content,
        "caption": caption.strip(),
        "cover_prompt": cover_prompt
    }


def _parse_carousel_slides(raw_content: str, num_slides: int, request: FormatContentRequest) -> List[SlideContent]:
    """Parse carousel slides from raw LLM output."""
    slides = []

    sections = raw_content.split("---SLIDE")

    for i, section in enumerate(sections[1:num_slides + 1], 1):
        slide_type = _get_carousel_slide_type(i, num_slides)

        slide = SlideContent(
            slide_num=i,
            slide_type=slide_type,
            title="",
            content="",
            bullets=[],
            visual_prompt=None
        )

        lines = section.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("TIPO:"):
                slide.slide_type = line.replace("TIPO:", "").strip().lower()
            elif line.startswith("TITOLO:"):
                slide.title = line.replace("TITOLO:", "").strip()
            elif line.startswith("CORPO:"):
                slide.content = line.replace("CORPO:", "").strip()
            elif line.startswith("BULLETS:"):
                bullets_raw = line.replace("BULLETS:", "").strip()
                slide.bullets = [b.strip() for b in bullets_raw.split("|") if b.strip()]
            elif line.startswith("VISUAL_PROMPT:"):
                slide.visual_prompt = line.replace("VISUAL_PROMPT:", "").strip()
            elif line.startswith("DATA_POINT:"):
                # Store in content if relevant
                data = line.replace("DATA_POINT:", "").strip()
                if data and data.lower() != "n/a":
                    slide.content += f" 📊 {data}"

        # Fallback visual prompt
        if not slide.visual_prompt:
            slide.visual_prompt = _generate_carousel_visual_prompt(
                request.topic, slide_type, slide.title, i, num_slides, request.sector
            )

        slides.append(slide)

    # Ensure correct number of slides
    while len(slides) < num_slides:
        n = len(slides) + 1
        slide_type = _get_carousel_slide_type(n, num_slides)
        slides.append(SlideContent(
            slide_num=n,
            slide_type=slide_type,
            title=f"Slide {n}",
            content="",
            visual_prompt=_generate_carousel_visual_prompt(
                request.topic, slide_type, f"Slide {n}", n, num_slides, request.sector
            )
        ))

    return slides[:num_slides]


def _get_carousel_slide_type(slide_num: int, total: int) -> str:
    """Determine carousel slide type based on position."""
    if slide_num == 1:
        return "cover"
    elif slide_num == 2:
        return "context"
    elif slide_num == total - 1:
        return "recap"
    elif slide_num == total:
        return "cta"
    else:
        return "content"


def _generate_carousel_visual_prompt(topic: str, slide_type: str, title: str, slide_num: int, total: int, sector: str) -> str:
    """Generate visual prompt for carousel slide."""
    base = f"""
Premium Instagram Carousel Slide {slide_num}/{total}.
Topic: {topic}
Title: {title}
Slide type: {slide_type}
Format: Square 1080x1080 or 4:5 (1080x1350).
Colors: Gold #D4AF37 accents, Dark gray/black background, White text.
Style: Premium, professional, consistent series feel.
Typography: Modern sans-serif, bold titles, clean bullets.
Sector: {sector}.
"""

    type_additions = {
        "cover": "Elements: Large title, subtitle, decorative elements. Mood: Scroll-stopping, valuable, must-save.",
        "context": "Elements: Question mark, problem visualization, empathy. Mood: Relatable, 'I feel this'.",
        "content": f"Elements: Number {slide_num-2}, bullet icons, supporting visual. Mood: Educational, clear, actionable.",
        "recap": "Elements: Checklist visual, numbered summary, bookmark icon. Mood: Comprehensive, save-worthy.",
        "cta": "Elements: StudioCentOS logo, arrow/action indicator, contact info. Mood: Trust, next step clear."
    }

    return (base + type_additions.get(slide_type, type_additions["content"])).strip()


async def _generate_carousel_caption(client, request: FormatContentRequest, slides: List[SlideContent]) -> str:
    """Generate carousel caption with AI."""
    slide_titles = [s.title for s in slides if s.title]

    prompt = f"""Genera una CAPTION per questo carousel su {request.topic}.

Slide contenute: {', '.join(slide_titles[:5])}

STRUTTURA CAPTION:
1. HOOK - Prima riga che ferma lo scroll
2. VALORE - Preview di cosa imparerà chi legge
3. CTA - "Scorri per scoprire..." / "Salva per dopo 📌"
4. HASHTAG - Include #StudioCentOS #AIperPMI + 3-5 rilevanti

Max 2000 caratteri. Usa emoji appropriate. Tono professionale ma accessibile."""

    return await client.generate(
        prompt=prompt,
        temperature=0.7,
        max_tokens=500
    )


def _format_carousel_main_content(slides: List[SlideContent]) -> str:
    """Format carousel into main content."""
    content = "🎠 INSTAGRAM CAROUSEL\n" + "=" * 40 + "\n\n"
    for slide in slides:
        content += f"[SLIDE {slide.slide_num}] {slide.slide_type.upper()}\n"
        if slide.title:
            content += f"Titolo: {slide.title}\n"
        if slide.content:
            content += f"Contenuto: {slide.content}\n"
        if slide.bullets:
            content += "Punti:\n" + "\n".join([f"  • {b}" for b in slide.bullets]) + "\n"
        content += "\n"
    return content


# ============================================================================
# 🎬 REEL GENERATION - Power Implementation
# ============================================================================

async def _generate_power_reel(
    agent,
    request: FormatContentRequest,
    brand_dna: str,
    post_type_structure: str
) -> Dict:
    """Generate POWER Reel content with scene breakdown."""
    from app.core.llm.groq_client import get_groq_client

    duration = request.duration_seconds
    hook_end = min(10, int(duration * 0.2))
    solution_end = int(duration * 0.85)

    # Build MASTER prompt
    prompt = MASTER_REEL_PROMPT.format(
        brand_dna=brand_dna,
        duration=duration,
        hook_end=hook_end,
        solution_end=solution_end,
        topic=request.topic,
        post_type=request.post_type,
        sector=request.sector,
        video_style=request.video_style,
        music_mood=request.music_mood,
        post_type_structure=post_type_structure
    )

    # Generate with GROQ
    client = get_groq_client(model="llama-3.3-70b")
    raw_content = await client.generate(
        prompt=prompt,
        system_prompt=f"""Sei il MASTER REEL CREATOR di StudioCentOS.
Genera script video VIRALI con timing preciso.
Rispondi SEMPRE in italiano.
Segui ESATTAMENTE il formato ---SCENA [TIMESTAMP]---.""",
        temperature=0.8,
        max_tokens=3500
    )

    # Parse scenes
    scenes = _parse_reel_scenes(raw_content, duration, request)

    # Extract caption
    caption = ""
    if "GENERA CAPTION" in raw_content:
        caption_section = raw_content.split("GENERA CAPTION")[-1]
        caption_lines = [l for l in caption_section.split("\n") if l.strip() and not l.startswith("---") and "THUMBNAIL" not in l.upper()]
        caption = "\n".join(caption_lines[:5])

    if not caption:
        caption = f"🎬 {request.topic}\n\n#StudioCentOS #AIperPMI #Reel #Tips"

    # Extract thumbnail prompt
    thumbnail_prompt = None
    if "THUMBNAIL_PROMPT" in raw_content:
        thumb_section = raw_content.split("THUMBNAIL_PROMPT")[-1]
        thumb_lines = [l for l in thumb_section.split("\n") if l.strip()]
        thumbnail_prompt = " ".join(thumb_lines[:3])

    if not thumbnail_prompt:
        thumbnail_prompt = _generate_reel_thumbnail_prompt(request.topic, request.sector)

    # Main content
    main_content = _format_reel_main_content(scenes, caption)

    return {
        "scenes": scenes,
        "main_content": main_content,
        "caption": caption.strip(),
        "thumbnail_prompt": thumbnail_prompt.strip()
    }


def _parse_reel_scenes(raw_content: str, duration: int, request: FormatContentRequest) -> List[SlideContent]:
    """Parse reel scenes from raw output."""
    scenes = []

    sections = raw_content.split("---SCENA")

    for section in sections[1:]:
        if "]---" not in section and "---" not in section[:50]:
            continue

        scene = SlideContent(
            slide_num=len(scenes) + 1,
            slide_type="scene",
            content="",
            visual_prompt=None,
            duration_seconds=None
        )

        # Extract timestamp from header
        header_match = section.split("---")[0] if "---" in section else section[:50]
        if "[" in header_match and "]" in header_match:
            scene.text_overlay = header_match.split("[")[-1].split("]")[0]

        lines = section.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("NOME:"):
                scene.title = line.replace("NOME:", "").strip()
            elif line.startswith("VISUAL:"):
                scene.visual_prompt = line.replace("VISUAL:", "").strip()
            elif line.startswith("NARRAZIONE:"):
                narration = line.replace("NARRAZIONE:", "").strip()
                scene.content = narration.strip('"').strip("'")
            elif line.startswith("TESTO_SCREEN:"):
                overlay = line.replace("TESTO_SCREEN:", "").strip()
                if scene.text_overlay:
                    scene.text_overlay += f" | {overlay}"
                else:
                    scene.text_overlay = overlay
            elif line.startswith("AUDIO:"):
                scene.music_mood = line.replace("AUDIO:", "").strip()
            elif line.startswith("TRANSIZIONE:"):
                scene.transition = line.replace("TRANSIZIONE:", "").strip()

        if scene.content or scene.visual_prompt:
            scenes.append(scene)

    # Ensure at least 4 scenes (hook, problem, solution, cta)
    while len(scenes) < 4:
        n = len(scenes) + 1
        scene_type = ["hook", "problem", "solution", "cta"][min(n-1, 3)]
        scenes.append(SlideContent(
            slide_num=n,
            slide_type=scene_type,
            title=scene_type.upper(),
            content=f"[{scene_type.upper()}] Contenuto per {request.topic}",
            visual_prompt=f"Reel scene {n} for {request.topic}, style: {request.video_style}, vertical 9:16"
        ))

    return scenes


def _generate_reel_thumbnail_prompt(topic: str, sector: str) -> str:
    """Generate thumbnail prompt for reel."""
    return f"""
Premium Reel Thumbnail - Click-worthy.
Topic: {topic}
Format: Vertical 9:16 (1080x1920) or Square 1:1 for feed preview.
Style: High contrast, bold, curiosity-inducing.
Colors: Gold #D4AF37 accents, dark background for pop.
Elements: Expressive face/reaction (if applicable), large bold text (max 3 words), arrow/play indicator.
Typography: Ultra-bold, readable at small size.
Mood: "I NEED to watch this", curious, valuable.
Sector: {sector}.
Quality: 4K, crisp, mobile-optimized.
NO: Cluttered, blurry, generic stock, small text.
""".strip()


def _format_reel_main_content(scenes: List[SlideContent], caption: str) -> str:
    """Format reel scenes into main content."""
    content = "🎬 REEL SCRIPT\n" + "=" * 40 + "\n\n"
    for scene in scenes:
        content += f"[SCENA {scene.slide_num}] {scene.title or scene.slide_type.upper()}\n"
        if scene.text_overlay:
            content += f"Timestamp: {scene.text_overlay}\n"
        content += f"Narrazione: \"{scene.content}\"\n"
        if scene.music_mood:
            content += f"Audio: {scene.music_mood}\n"
        content += "\n"
    content += "=" * 40 + f"\nCAPTION:\n{caption}"
    return content


# ============================================================================
# 🎥 VIDEO GENERATION (Long-form) - Power Implementation
# ============================================================================

async def _generate_power_video(
    agent,
    request: FormatContentRequest,
    brand_dna: str,
    post_type_structure: str
) -> Dict:
    """Generate long-form video script."""
    from app.core.llm.groq_client import get_groq_client

    duration = request.duration_seconds
    duration_min = duration // 60

    prompt = f"""
{brand_dna}

TASK: Crea uno SCRIPT VIDEO LUNGO per YouTube/LinkedIn

ARGOMENTO: {request.topic}
DURATA: {duration_min} minuti ({duration} secondi)
SETTORE: {request.sector}
STILE: {request.video_style}

{post_type_structure}

STRUTTURA VIDEO PROFESSIONALE:

⏱️ 0:00-0:30 - COLD OPEN (Teaser):
[Clip più impattante - anticipa il valore]

⏱️ 0:30-1:00 - INTRO:
[Bumper brand + presentazione argomento]

⏱️ 1:00-{int(duration*0.7)//60}:{int(duration*0.7)%60:02d} - CONTENUTO:
[Sezioni numerate con timestamp]

⏱️ {int(duration*0.7)//60}:{int(duration*0.7)%60:02d}-{int(duration*0.9)//60}:{int(duration*0.9)%60:02d} - RECAP:
[Riassunto punti chiave]

⏱️ {int(duration*0.9)//60}:{int(duration*0.9)%60:02d}-{duration//60}:{duration%60:02d} - OUTRO:
[CTA: Subscribe, Like, Commento]

GENERA OUTPUT con formato:

---SCENA [MM:SS-MM:SS]---
NOME: [nome sezione]
VISUAL: [descrizione inquadratura, B-roll, grafiche]
NARRAZIONE: "[testo ESATTO da leggere]"
TESTO_SCREEN: [lower thirds, titoli, bullet animati]
AUDIO: [musica, transizioni]
---

GENERA SCRIPT COMPLETO:
"""

    client = get_groq_client(model="llama-3.3-70b")
    raw_content = await client.generate(
        prompt=prompt,
        system_prompt="Sei un video script writer professionista. Genera script completi con timing preciso.",
        temperature=0.7,
        max_tokens=4000
    )

    # Reuse reel scene parser (similar format)
    scenes = _parse_reel_scenes(raw_content, duration, request)

    # Video description as caption
    caption = f"""🎥 {request.topic}

In questo video scoprirai:
{chr(10).join([f"✅ {s.title or s.content[:50]}" for s in scenes[:5] if s.title or s.content])}

👉 Iscriviti per altri contenuti: @studiocentos

#StudioCentOS #Tutorial #Video #{request.sector.capitalize()}"""

    thumbnail_prompt = f"""
YouTube Thumbnail - High CTR.
Topic: {request.topic}
Format: 16:9 (1920x1080).
Style: Bold, contrasting, click-worthy.
Colors: Gold #D4AF37, dark background, bright accents.
Elements: Face with expression (if applicable), 3 words MAX text, arrows/indicators.
Mood: Curiosity, value, must-click.
Quality: 4K, crisp, YouTube-optimized.
""".strip()

    main_content = _format_reel_main_content(scenes, caption)

    return {
        "scenes": scenes,
        "main_content": main_content,
        "caption": caption,
        "thumbnail_prompt": thumbnail_prompt
    }


# ============================================================================
# LEAD INTELLIGENCE ENDPOINTS
# ============================================================================

from app.domain.marketing.lead_intelligence_agent import (
    lead_intelligence_agent,
    LeadSearchRequest,
    LeadItem
)
from typing import List

# ============================================================================
# IMAGE GENERATION ENDPOINTS - NANO BANANA PRO (Google Gemini)
# ============================================================================

class ImageGenerationRequest(BaseModel):
    """Request for AI image generation."""
    prompt: str = Field(..., description="Image description")
    style: str = Field(default="professional", description="Visual style: professional, creative, minimalist, modern, tech, elegant")
    aspect_ratio: str = Field(default="1:1", description="Aspect ratio: 1:1, 16:9, 9:16, 4:3, 3:4")
    platform: str = Field(default="default", description="Target platform: linkedin, facebook, instagram, twitter, tiktok, default")
    post_type: str = Field(default="", description="Post type for style matching: lancio_prodotto, tip_giorno, caso_successo, trend_settore, offerta_speciale, ai_business, educational, testimonial, engagement")
    sector: str = Field(default="tech", description="Industry sector: ristorazione, hospitality, legal, medical, retail, manufacturing, tech, consulting")
    apply_branding: bool = Field(default=True, description="Apply branding overlay")
    logo_url: Optional[str] = Field(default=None, description="Custom logo URL from Brand DNA settings. If provided, uses this instead of default logo.")
    brand_name: str = Field(default="StudioCentOS", description="Brand name for footer text")
    provider: str = Field(default="auto", description="Provider: auto, google, pro, pollinations, huggingface")
    resolution: str = Field(default="1K", description="Resolution: 1K, 2K, 4K (only for 'pro' provider)")
    use_google_search: bool = Field(default=False, description="Ground with real-time Google Search data (pro only)")
    reference_images: List[str] = Field(default=[], description="URLs to reference images max 14 (pro only)")

class ImageGenerationResponse(BaseModel):
    """Response for generated image."""
    image_url: str
    prompt_used: str
    generation_time: float
    metadata: dict

# Batch Image Generation Models
class BatchImageRequest(BaseModel):
    """Single image request in batch."""
    prompt: str = Field(..., description="Image description")
    aspect_ratio: str = Field(default="1:1", description="Aspect ratio: 1:1, 16:9, 9:16, 4:3")
    platform: str = Field(default="generic", description="Target platform: facebook, instagram, instagram_story, linkedin")
    tag: str = Field(default="", description="Custom tag for this image")

class BatchImageGenerationRequest(BaseModel):
    """Request for generating multiple images in one call."""
    images: List[BatchImageRequest] = Field(..., description="List of images to generate")
    base_prompt: str = Field(default="", description="Base prompt to append to all images")
    style: str = Field(default="professional", description="Visual style for all images")
    provider: str = Field(default="auto", description="Provider: auto, google, pollinations")
    apply_branding: bool = Field(default=True, description="Apply StudioCentOS branding")

class BatchImageResult(BaseModel):
    """Result for single image in batch."""
    image_url: str
    prompt_used: str
    platform: str
    tag: str
    aspect_ratio: str
    generation_time: float
    success: bool
    error: Optional[str] = None

class BatchImageGenerationResponse(BaseModel):
    """Response for batch image generation."""
    results: List[BatchImageResult]
    total_images: int
    successful: int
    failed: int
    total_generation_time: float

@router.post("/image/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    """
    🎨 SMART AI Image Generation - Auto-selects BEST model based on your API keys!

    QUALITY TIERS (auto-detected based on API keys):

    🥇 TIER 1 - PREMIUM (Google Paid/Vertex AI):
       - Imagen 4 Ultra (Best quality, 4K, photorealistic)
       - Gemini 3 Pro Image (Creative, with thinking mode)

    🥈 TIER 2 - PROFESSIONAL (HuggingFace Pro / fal.ai):
       - FLUX.1 Pro (Best open-source, studio quality)
       - FLUX.1 Dev (Great balance speed/quality)

    🥉 TIER 3 - FREE UNLIMITED:
       - Pollinations/FLUX (100% FREE, unlimited, ~15-20 sec)
       - FLUX Schnell (Fast, lower quality)

    Provider parameter:
    - 'auto': Smart selection based on available API keys
    - 'premium': Force Tier 1 (Imagen 4 Ultra)
    - 'pro': Force Tier 2 (FLUX Pro)
    - 'free': Force Tier 3 (Pollinations FREE)
    """
    import aiohttp
    import base64
    import time
    import hashlib
    from pathlib import Path

    logger.info("image_generate", prompt=request.prompt[:50], style=request.style, platform=request.platform, provider=request.provider, resolution=request.resolution)

    start_time = time.time()

    # ========================================================================
    # SMART API KEY DETECTION - Determine available quality tiers
    # ========================================================================
    google_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')
    hf_token = os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HUGGINGFACE_API_KEY')
    fal_key = os.getenv('FAL_KEY') or os.getenv('FAL_API_KEY')

    # Detect available tiers
    has_tier1 = bool(google_key)  # Google = Imagen 4, Gemini Pro Image
    has_tier2 = bool(hf_token) or bool(fal_key)  # HF/fal.ai = FLUX Pro
    has_tier3 = True  # Pollinations is always available (no key needed!)

    # Log available tiers
    logger.info("api_tiers_detected",
                tier1_google=has_tier1,
                tier2_hf_fal=has_tier2,
                tier3_free=has_tier3,
                selected_provider=request.provider)


    # StudioCentos Brand Identity - COLORI REALI (NO BLU!)
    BRAND_CONTEXT = """
    Brand: StudioCentos / NanoBanana
    Industry: Digital Marketing Agency, AI-Powered Business Solutions
    Colors: GOLD (#D4AF37) primary, BLACK (#0A0A0A) background, WHITE (#FAFAFA) text
    Style: Modern, Professional, Tech-Forward, Italian Excellence, Premium Luxury
    NO BLUE colors - only Gold, Black, White!
    """

    # Enhance prompt based on style - BRAND CORRETTO
    # Enhance prompt based on style - BRAND CORRETTO & PREMIUM
    style_modifiers = {
        # Base Styles
        "professional": "professional corporate photography, high quality, 8k resolution, clean studio lighting, sharp focus, gold and black color scheme, premium luxury aesthetic, masterpiece",
        "creative": "artistic, vibrant gold tones, creative composition, digital art, imaginative, golden highlights on dark background, tech-inspired, award winning",
        "minimalist": "minimalist design, clean lines, simple composition, flat design, black background with gold accents, elegant, apple style",
        "modern": "modern aesthetic, sleek design, contemporary style, dark theme with gold highlights, premium feel, futuristic",
        "tech": "futuristic technology, digital elements, neon gold accents, dark mode interface, geometric patterns, circuit board aesthetic, cyber luxury",
        "elegant": "luxurious, refined, sophisticated, golden hour lighting, premium quality, high-end brand aesthetic, vogue style",

        # Frontend Template IDs (Compatibility)
        "professional_marketing": "professional marketing photography, business context, premium quality, 8k, sharp focus, gold accents on black, trustworthy, high-end corporate",
        "educational_post": "clean infographic style, educational context, structured layout, easy to read, professional icons, gold and black theme, modern teaching",
        "product_launch": "dramatic product lighting, hero shot, dynamic composition, excitement, premium product reveal, gold spotlight, cinematic",
        "trend_settore": "futuristic data visualization, upward trending graphics, holographic gold elements, dark background, tech-savvy, analysis",
        "caso_successo": "success metaphor, climbing, peak performance, golden trophy aesthetic, professional achievement, inspiring, cinematic lighting",
        "offerta_speciale": "exclusive offer, premium gift aesthetic, golden ribbon, luxury unboxing, high value, limited edition feel",
        "quote_post": "minimalist background for text, subtle texture, elegant dark theme, golden typography elements, inspirational atmosphere",
        "engagement_post": "interactive, question mark metaphor, community focus, warm lighting, inviting, gold and black conversation bubbles",
    }

    # Normalizza ID stile (gestisce sia underscore che trattini)
    normalized_style = request.style.replace("-", "_")
    modifier = style_modifiers.get(normalized_style, style_modifiers.get("professional_marketing", style_modifiers["professional"]))

    # Get post-type specific style if provided
    post_type_style = ""
    if request.post_type and request.post_type in IMAGE_STYLE_BY_POST_TYPE:
        pt_style = IMAGE_STYLE_BY_POST_TYPE[request.post_type]
        post_type_style = f"""
    Post Type Style: {pt_style["style"]}
    Mood: {pt_style["mood"]}
    Composition: {pt_style["composition"]}
    Key Elements: {pt_style["elements"]}
"""
        # Override style from post_type if not explicitly set
        if request.style == "professional":
            modifier = style_modifiers.get(pt_style["style"], modifier)

    # Get sector-specific context
    sector_context = ""
    if request.sector and request.sector in SECTOR_IMAGE_CONTEXT:
        sector_context = f"""
    Sector Context: {SECTOR_IMAGE_CONTEXT[request.sector]}
"""

    # Build enhanced prompt with brand context + post_type + sector
    enhanced_prompt = f"""
    Create an image for StudioCentos digital marketing agency.
    Content: {request.prompt}
    Style: {modifier}
    Brand colors: GOLD (#D4AF37), BLACK (#0A0A0A), WHITE - NO BLUE!
    Mood: Professional, modern, tech-forward, Italian excellence, luxury premium
{post_type_style}{sector_context}
    Platform: {request.platform} optimized
    DO NOT include any text, logos, or watermarks in the image.
    Focus on visual metaphors for digital transformation, AI, business growth.
    """.strip()

    # Helper function to save and return image
    async def save_image(image_bytes: bytes, provider: str, model: str) -> ImageGenerationResponse:
        # Apply branding if enabled
        if request.apply_branding:
            try:
                from app.domain.marketing.image_branding import image_branding
                image_bytes = image_branding.apply_branding(
                    image_bytes,
                    platform=request.platform,
                    footer_text=request.brand_name,
                    logo_url=request.logo_url,  # Use custom logo from Brand DNA if provided
                )
                logger.info("branding_applied", platform=request.platform, provider=provider, custom_logo=bool(request.logo_url))
            except Exception as e:
                logger.warning("branding_failed", error=str(e))

        # Save image
        save_dir = Path("/app/media/generated")
        save_dir.mkdir(parents=True, exist_ok=True)

        hash_id = hashlib.md5(request.prompt.encode()).hexdigest()[:8]
        filename = f"{provider}_{int(time.time())}_{hash_id}.png"
        file_path = save_dir / filename

        with open(file_path, 'wb') as f:
            f.write(image_bytes)

        base_url = os.getenv('BASE_URL', 'https://studiocentos.it')

        return ImageGenerationResponse(
            image_url=f"{base_url}/ai/media/generated/{filename}",
            prompt_used=enhanced_prompt,
            generation_time=time.time() - start_time,
            metadata={
                "provider": provider,
                "model": model,
                "cost": "FREE",
                "branded": request.apply_branding,
                "aspect_ratio": request.aspect_ratio,
            "style": request.style
            }
        )

    # ========================================================================
    # 🎯 SMART PROVIDER SELECTION LOGIC (December 2025)
    # ========================================================================
    # PRIORITY ORDER - ALWAYS THE BEST AVAILABLE:
    #
    # 🥇 #1: Imagen 4 Ultra (BEST QUALITY - ~50 req/day FREE)
    # 🥈 #2: Gemini 2.5 Flash Image (500 req/day FREE - FAST)
    # 🥉 #3: Pollinations/FLUX (Unlimited FREE - FALLBACK)

    use_google = has_tier1 and request.provider in ["auto", "premium", "google", "pro"]
    force_free = request.provider == "free"

    # ========================================================================
    # 🥇 #1: Imagen 4 Ultra - BEST QUALITY (~50/day FREE then paid)
    # ========================================================================
    if use_google and not force_free:
        try:
            logger.info("provider1_imagen4ultra_trying")

            url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-ultra-generate-001:predict?key={google_key}"

            aspect_map = {
                "1:1": "1:1", "16:9": "16:9", "9:16": "9:16", "4:3": "4:3", "3:4": "3:4"
            }

            payload = {
                "instances": [{"prompt": enhanced_prompt}],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": aspect_map.get(request.aspect_ratio, "1:1"),
                    "personGeneration": "DONT_ALLOW",
                    "safetySetting": "block_low_and_above"
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                    if response.status == 200:
                        data = await response.json()
                        predictions = data.get("predictions", [])
                        if predictions and "bytesBase64Encoded" in predictions[0]:
                            image_bytes = base64.b64decode(predictions[0]["bytesBase64Encoded"])
                            logger.info("provider1_imagen4ultra_success", size_kb=len(image_bytes)//1024)
                            return await save_image(image_bytes, "imagen4-ultra", "imagen-4.0-ultra-generate-001")
                    else:
                        error_text = await response.text()
                        logger.warning("provider1_imagen4ultra_failed", status=response.status, error=error_text[:150])
        except Exception as e:
            logger.warning("provider1_imagen4ultra_error", error=str(e))

    # ========================================================================
    # 🥈 #2: Gemini 2.5 Flash Image (500 RPD FREE - FAST!)
    # ========================================================================
    if use_google and not force_free:
        try:
            logger.info("provider2_gemini25flash_trying")

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={google_key}"

            payload = {
                "contents": [{"parts": [{"text": f"Generate an image: {enhanced_prompt}"}]}],
                "generationConfig": {
                    "responseModalities": ["IMAGE"]
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=aiohttp.ClientTimeout(total=120)) as response:
                    if response.status == 200:
                        data = await response.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            for part in parts:
                                if "inlineData" in part:
                                    image_bytes = base64.b64decode(part["inlineData"]["data"])
                                    logger.info("provider2_gemini25flash_success", size_kb=len(image_bytes)//1024)
                                    return await save_image(image_bytes, "gemini25-flash-image", "gemini-2.5-flash-image")
                    else:
                        error_text = await response.text()
                        logger.warning("provider2_gemini25flash_failed", status=response.status, error=error_text[:150])
        except Exception as e:
            logger.warning("provider2_gemini25flash_error", error=str(e))

    # ========================================================================
    # 🥉 #3: Pollinations.ai (100% FREE, UNLIMITED) - FINAL FALLBACK
    # ========================================================================
    # This ALWAYS works - no API key needed, unlimited usage!
    if request.provider in ["auto", "free", "pollinations"] or not use_google:
        try:
            import urllib.parse

            # Map aspect ratio to dimensions
            dimensions = {
                "1:1": (1024, 1024),
                "16:9": (1024, 576),
                "9:16": (576, 1024),
                "4:3": (1024, 768),
                "3:4": (768, 1024)
            }
            width, height = dimensions.get(request.aspect_ratio, (1024, 1024))

            # Create SHORT prompt for Pollinations (URL length limit!)
            short_prompt = f"{request.prompt}, professional marketing, gold and black colors, dark elegant theme, premium luxury, high quality, 8k"
            if len(short_prompt) > 300:
                short_prompt = short_prompt[:297] + "..."

            encoded_prompt = urllib.parse.quote(short_prompt)

            # Pollinations.ai free API - FLUX model
            pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={int(time.time())}&nologo=true&model=flux"

            logger.info("provider3_pollinations_trying", prompt_length=len(short_prompt))

            async with aiohttp.ClientSession() as session:
                async with session.get(pollinations_url, timeout=aiohttp.ClientTimeout(total=90)) as response:
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '')
                        if 'image' in content_type:
                            image_bytes = await response.read()
                            logger.info("provider3_pollinations_success", size=len(image_bytes))
                            return await save_image(image_bytes, "pollinations", "flux")
                        else:
                            logger.warning("pollinations_not_image", content_type=content_type)
                    else:
                        logger.warning("pollinations_error", status=response.status)

        except Exception as e:
            logger.warning("pollinations_error", error=str(e))


    # ========================================================================
    # PROVIDER 1: Nano Banana PRO (Gemini 3 Pro Image) 🍌⭐ - PROFESSIONAL
    # ========================================================================
    google_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')

    if google_key and request.provider == "pro":
        try:
            logger.info("nano_banana_pro_trying", resolution=request.resolution, google_search=request.use_google_search, ref_images=len(request.reference_images))

            # Gemini 3 Pro Image endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key={google_key}"

            # Map aspect ratio
            aspect_map = {
                "1:1": "1:1",
                "16:9": "16:9",
                "9:16": "9:16",
                "4:3": "4:3",
                "3:4": "3:4",
                "4:5": "4:5",
                "5:4": "5:4",
                "21:9": "21:9"
            }
            aspect = aspect_map.get(request.aspect_ratio, "1:1")

            # Build contents array (text + optional reference images)
            contents_parts = [{"text": enhanced_prompt}]

            # Add reference images if provided (max 14)
            if request.reference_images:
                for img_url in request.reference_images[:14]:
                    try:
                        # Download reference image
                        async with aiohttp.ClientSession() as session:
                            async with session.get(img_url, timeout=aiohttp.ClientTimeout(total=30)) as img_response:
                                if img_response.status == 200:
                                    img_bytes = await img_response.read()
                                    img_b64 = base64.b64encode(img_bytes).decode('utf-8')

                                    # Determine MIME type
                                    content_type = img_response.headers.get('Content-Type', 'image/jpeg')

                                    contents_parts.append({
                                        "inline_data": {
                                            "mime_type": content_type,
                                            "data": img_b64
                                        }
                                    })
                                    logger.info("reference_image_added", url=img_url[:50])
                    except Exception as e:
                        logger.warning("reference_image_failed", url=img_url[:50], error=str(e))

            # Build generation config
            generation_config = {
                "response_modalities": ["IMAGE"],
                "image_config": {
                    "aspect_ratio": aspect,
                    "image_size": request.resolution  # "1K", "2K", or "4K"
                }
            }

            # Add tools if Google Search is enabled
            tools = []
            if request.use_google_search:
                tools.append({"google_search": {}})
                logger.info("google_search_enabled", prompt=enhanced_prompt[:100])

            payload = {
                "contents": [{"parts": contents_parts}],
                "generationConfig": generation_config
            }

            if tools:
                payload["tools"] = tools

            headers = {"Content-Type": "application/json"}

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=180)) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract image from response
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])

                            # Find the final image (skip thought images)
                            for part in reversed(parts):  # Start from last (final image)
                                if "inline_data" in part and not part.get("thought", False):
                                    image_data = part["inline_data"]["data"]
                                    image_bytes = base64.b64decode(image_data)

                                    logger.info("nano_banana_pro_success",
                                              resolution=request.resolution,
                                              size_kb=len(image_bytes) // 1024,
                                              thinking_used=any(p.get("thought") for p in parts))

                                    return await save_image(image_bytes, f"nano-banana-pro-{request.resolution}", "gemini-3-pro-image-preview")

                        logger.warning("nano_banana_pro_no_image", response=str(data)[:200])
                    else:
                        error_text = await response.text()
                        logger.error("nano_banana_pro_error", status=response.status, error=error_text[:300])

        except Exception as e:
            logger.error("nano_banana_pro_exception", error=str(e))

    # ========================================================================
    # PROVIDER 2: Google Imagen 4 Ultra (BEST AVAILABLE!) 🍌⭐
    # ========================================================================

    if google_key and request.provider in ["auto", "google"]:
        # Try Imagen 4 Ultra - Best image generation model (Dec 2025)
        try:
            # Imagen 4 Ultra endpoint - highest quality
            url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-ultra-generate-001:predict?key={google_key}"

            # Map aspect ratio to Imagen format
            aspect_map = {
                "1:1": "1:1",
                "16:9": "16:9",
                "9:16": "9:16",
                "4:3": "4:3",
                "3:4": "3:4"
            }
            imagen_aspect = aspect_map.get(request.aspect_ratio, "1:1")

            payload = {
                "instances": [
                    {"prompt": enhanced_prompt}
                ],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": imagen_aspect,
                    "personGeneration": "DONT_ALLOW",
                    "safetySetting": "BLOCK_MEDIUM_AND_ABOVE"
                }
            }

            logger.info("imagen4_ultra_trying", prompt_length=len(enhanced_prompt))

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                    if response.status == 200:
                        data = await response.json()
                        predictions = data.get("predictions", [])
                        if predictions and "bytesBase64Encoded" in predictions[0]:
                            image_bytes = base64.b64decode(predictions[0]["bytesBase64Encoded"])
                            logger.info("imagen4_ultra_success", size_kb=len(image_bytes)//1024)
                            return await save_image(image_bytes, "imagen4-ultra", "imagen-4.0-ultra-generate-001")
                    else:
                        error_text = await response.text()
                        logger.warning("imagen4_ultra_error", status=response.status, error=error_text[:200])

        except Exception as e:
            logger.warning("imagen4_ultra_error", error=str(e))

        # Fallback: Try Imagen 4 Standard (faster, slightly lower quality)
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={google_key}"

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=90)) as response:
                    if response.status == 200:
                        data = await response.json()
                        predictions = data.get("predictions", [])
                        if predictions and "bytesBase64Encoded" in predictions[0]:
                            image_bytes = base64.b64decode(predictions[0]["bytesBase64Encoded"])
                            logger.info("imagen4_success", size_kb=len(image_bytes)//1024)
                            return await save_image(image_bytes, "imagen4", "imagen-4.0-generate-001")
                    else:
                        error_text = await response.text()
                        logger.warning("imagen4_error", status=response.status, error=error_text[:200])

        except Exception as e:
            logger.warning("imagen4_error", error=str(e))


        # Fallback: Try gemini-2.0-flash-preview-image-generation
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent?key={google_key}"

            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Generate an image: {enhanced_prompt}"
                    }]
                }],
                "generationConfig": {
                    "responseModalities": ["IMAGE", "TEXT"],
                    "temperature": 1.0
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                    if response.status == 200:
                        data = await response.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            for part in parts:
                                if "inlineData" in part:
                                    image_bytes = base64.b64decode(part["inlineData"]["data"])
                                    return await save_image(image_bytes, "gemini", "gemini-2.0-flash-exp-image-generation")
                    else:
                        error_text = await response.text()
                        logger.warning("gemini_image_gen_error", status=response.status, error=error_text[:200])

        except Exception as e:
            logger.warning("gemini_image_gen_error", error=str(e))

    # ========================================================================
    # PROVIDER 2: HuggingFace via Router (FREE)
    # ========================================================================
    hf_token = os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HUGGINGFACE_API_KEY')

    if hf_token and request.provider in ["auto", "huggingface"]:
        # Try HuggingFace Router API for image generation
        # Uses the new router.huggingface.co endpoint
        try:
            # Use novita.ai FLUX model via HuggingFace (fast, free)
            url = "https://router.huggingface.co/novita-ai/flux/v1/images/generations"
            headers = {
                "Authorization": f"Bearer {hf_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "prompt": enhanced_prompt,
                "model": "flux/dev",
                "width": 1024,
                "height": 1024 if request.aspect_ratio == "1:1" else (576 if request.aspect_ratio == "16:9" else 1024),
                "steps": 20,
                "n": 1,
                "response_format": "b64_json"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=180)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "data" in data and len(data["data"]) > 0:
                            image_b64 = data["data"][0].get("b64_json", "")
                            if image_b64:
                                image_bytes = base64.b64decode(image_b64)
                                return await save_image(image_bytes, "flux", "flux-dev")
                    else:
                        error_text = await response.text()
                        logger.warning("flux_error", status=response.status, error=error_text[:150])

        except Exception as e:
            logger.warning("flux_error", error=str(e))

        # Fallback: Try fal.ai FLUX via HuggingFace Router
        try:
            url = "https://router.huggingface.co/fal-ai/fal-ai/flux/dev"
            headers = {
                "Authorization": f"Bearer {hf_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "prompt": enhanced_prompt,
                "image_size": "square_hd" if request.aspect_ratio == "1:1" else "landscape_16_9",
                "num_inference_steps": 28,
                "guidance_scale": 3.5,
                "num_images": 1,
                "enable_safety_checker": True
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=180)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "images" in data and len(data["images"]) > 0:
                            image_url = data["images"][0].get("url", "")
                            if image_url:
                                # Download the image
                                async with session.get(image_url) as img_response:
                                    if img_response.status == 200:
                                        image_bytes = await img_response.read()
                                        return await save_image(image_bytes, "fal", "flux-dev")
                    else:
                        error_text = await response.text()
                        logger.warning("fal_flux_error", status=response.status, error=error_text[:150])

        except Exception as e:
            logger.warning("fal_flux_error", error=str(e))

        # Fallback: Try black-forest-labs FLUX via HuggingFace
        try:
            url = "https://router.huggingface.co/black-forest-labs/flux-schnell"
            headers = {
                "Authorization": f"Bearer {hf_token}",
                "Content-Type": "application/json"
            }
            payload = {"inputs": enhanced_prompt}

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '')
                        if 'image' in content_type:
                            image_bytes = await response.read()
                            return await save_image(image_bytes, "flux", "flux-schnell")
                        else:
                            # Try to parse JSON response with base64 image
                            data = await response.json()
                            if isinstance(data, list) and len(data) > 0:
                                image_bytes = base64.b64decode(data[0])
                                return await save_image(image_bytes, "flux", "flux-schnell")
                    else:
                        error_text = await response.text()
                        logger.warning("flux_schnell_error", status=response.status, error=error_text[:150])

        except Exception as e:
            logger.warning("flux_schnell_error", error=str(e))

    # ========================================================================
    # FALLBACK: Placeholder image
    # ========================================================================
    logger.error("no_image_provider", message="All image providers failed")

    return ImageGenerationResponse(
        image_url="https://placehold.co/1024x1024/1a1a2e/D4AF37?text=Image+Generation+Unavailable",
        prompt_used=enhanced_prompt,
        generation_time=time.time() - start_time,
        metadata={
            "provider": "placeholder",
            "error": "No image provider available - check API keys",
            "tried_providers": ["google", "huggingface"] if hf_token else ["google"]
        }
    )


# ============================================================================
# VIDEO GENERATION ENDPOINTS - VEO 3.1 (Google Gemini) 🎥
# ============================================================================

class VideoGenerationRequest(BaseModel):
    """Request for AI video generation."""
    prompt: str = Field(..., description="Video description")
    duration: int = Field(default=8, ge=1, le=60, description="Duration in seconds (1-60)")
    aspect_ratio: str = Field(default="9:16", description="Aspect ratio: 9:16 (Stories/Reels), 16:9 (YouTube), 1:1 (Square)")
    platform: str = Field(default="instagram", description="Target platform: instagram, tiktok, facebook, youtube")
    style: str = Field(default="professional", description="Visual style")
    input_image: Optional[str] = Field(default=None, description="URL to input image for image-to-video (optional)")
    use_google_search: bool = Field(default=False, description="Ground with real-time data")

class VideoGenerationResponse(BaseModel):
    """Response for generated video."""
    video_url: str
    thumbnail_url: str
    prompt_used: str
    generation_time: float
    metadata: dict


@router.post("/image/batch-generate", response_model=BatchImageGenerationResponse)
async def batch_generate_images(request: BatchImageGenerationRequest):
    """
    🎨 Batch Image Generation - Generate multiple images with different specs!

    Perfect for multi-platform social media posting:
    - Facebook (16:9 landscape)
    - Instagram Feed (1:1 square)
    - Instagram Story (9:16 vertical)

    All images generated concurrently for speed.
    """
    import asyncio
    import time

    start_time = time.time()

    # Platform optimizations
    platform_opts = {
        "facebook": {"aspect_ratio": "16:9", "suffix": "professional, landscape"},
        "instagram": {"aspect_ratio": "1:1", "suffix": "Instagram-optimized, square"},
        "instagram_story": {"aspect_ratio": "9:16", "suffix": "vertical Story, mobile"},
        "generic": {"aspect_ratio": "1:1", "suffix": "versatile social media"}
    }

    async def gen_single(img_req: BatchImageRequest, idx: int):
        try:
            platform = img_req.platform.lower()
            opt = platform_opts.get(platform, platform_opts["generic"])

            full_prompt = f"{request.base_prompt} {img_req.prompt}".strip()
            if request.style:
                full_prompt += f", {request.style} style"
            full_prompt += f", {opt['suffix']}"

            aspect = img_req.aspect_ratio if img_req.aspect_ratio != "1:1" else opt["aspect_ratio"]

            single_req = ImageGenerationRequest(
                prompt=full_prompt,
                style=request.style,
                aspect_ratio=aspect,
                platform=platform,
                apply_branding=request.apply_branding,
                provider=request.provider
            )

            img_start = time.time()
            result = await generate_image(single_req)

            return BatchImageResult(
                image_url=result.image_url,
                prompt_used=result.prompt_used,
                platform=platform,
                tag=img_req.tag or platform,
                aspect_ratio=aspect,
                generation_time=time.time() - img_start,
                success=True
            )
        except Exception as e:
            logger.error("batch_img_error", idx=idx, error=str(e))
            return BatchImageResult(
                image_url="",
                prompt_used=img_req.prompt,
                platform=img_req.platform,
                tag=img_req.tag,
                aspect_ratio=img_req.aspect_ratio,
                generation_time=0,
                success=False,
                error=str(e)
            )

    results = await asyncio.gather(*[gen_single(img, i) for i, img in enumerate(request.images)])

    successful = sum(1 for r in results if r.success)
    total_time = time.time() - start_time

    logger.info("batch_complete", total=len(results), ok=successful, time=total_time)

    return BatchImageGenerationResponse(
        results=results,
        total_images=len(results),
        successful=successful,
        failed=len(results) - successful,
        total_generation_time=total_time
    )


@router.post("/video/generate", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest):
    """
    🎥 Generate AI video using Google Veo 3.1.

    Perfect for:
    - Instagram Reels / Stories (9:16)
    - TikTok videos (9:16)
    - Facebook posts (1:1, 16:9)
    - YouTube Shorts (9:16)
    - LinkedIn videos (16:9, 1:1)

    Features:
    - Text-to-video generation
    - Image-to-video (animate static images)
    - Native audio support
    - High-quality output up to 1080p
    - Google Search grounding for real-time data
    """
    import aiohttp
    import base64
    import time
    import hashlib
    from pathlib import Path

    logger.info("video_generate", prompt=request.prompt[:50], duration=request.duration, platform=request.platform)

    start_time = time.time()

    google_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')

    if not google_key:
        raise HTTPException(status_code=503, detail="GOOGLE_AI_API_KEY not configured - video generation unavailable")

    # StudioCentos Brand Context for videos
    BRAND_VIDEO_CONTEXT = """
    Brand: StudioCentOS Digital Marketing Agency
    Style: Professional, modern, tech-forward, Italian excellence
    Colors: GOLD (#D4AF37), BLACK (#0A0A0A), WHITE (#FAFAFA)
    Mood: Dynamic, energetic, business-focused, premium
    """

    # Platform-specific optimization
    platform_specs = {
        "instagram": {
            "duration_optimal": 15,
            "style_keywords": "trendy, vibrant, mobile-first, vertical format",
            "preferred_ratio": "9:16"
        },
        "tiktok": {
            "duration_optimal": 15,
            "style_keywords": "dynamic, fast-paced, attention-grabbing, viral-worthy",
            "preferred_ratio": "9:16"
        },
        "facebook": {
            "duration_optimal": 30,
            "style_keywords": "engaging, shareable, professional, landscape or square",
            "preferred_ratio": "16:9"
        },
        "youtube": {
            "duration_optimal": 60,
            "style_keywords": "cinematic, high-production, storytelling, landscape",
            "preferred_ratio": "16:9"
        },
        "linkedin": {
            "duration_optimal": 30,
            "style_keywords": "professional, business-focused, informative, square or landscape",
            "preferred_ratio": "1:1"
        }
    }

    platform_config = platform_specs.get(request.platform, platform_specs["instagram"])

    # Enhanced prompt for video
    enhanced_video_prompt = f"""
    Create a professional marketing video for StudioCentOS digital agency.

    Content: {request.prompt}
    Platform: {request.platform.upper()}
    Duration: {request.duration} seconds (optimal: {platform_config['duration_optimal']}s)
    Style: {request.style}, {platform_config['style_keywords']}
    Aspect Ratio: {request.aspect_ratio}

    Visual Guidelines:
    - Brand colors: Gold accents (#D4AF37) on dark backgrounds
    - Modern, clean aesthetic with premium feel
    - Smooth camera movements, professional lighting
    - Dynamic transitions, engaging pacing
    - Clear focus on key message

    Technical:
    - High quality 1080p output
    - Smooth 30fps motion
    - Professional color grading (cinematic look)

    {BRAND_VIDEO_CONTEXT}
    """.strip()


    # HeyGen API Key
    heygen_key = os.getenv('HEYGEN_API_KEY')

    try:
        # ========================================================================
        # 🥇 PROVIDER 1: HeyGen (Avatar video - READY!) 🎬
        # ========================================================================
        # Note: Veo 2 requires Vertex AI Service Account setup (complex)
        # HeyGen is ready to use with current API key (600 credits available)
        if heygen_key:

            try:
                logger.info("heygen_trying", prompt_length=len(request.prompt))

                # HeyGen API v2 - Create video
                url = "https://api.heygen.com/v2/video/generate"

                headers = {
                    "X-Api-Key": heygen_key,
                    "Content-Type": "application/json"
                }

                # Map aspect ratio to HeyGen format
                dimension_map = {
                    "9:16": {"width": 720, "height": 1280},  # Vertical (Stories/Reels)
                    "16:9": {"width": 1920, "height": 1080},  # Landscape (YouTube)
                    "1:1": {"width": 1080, "height": 1080}   # Square
                }
                dimensions = dimension_map.get(request.aspect_ratio, dimension_map["9:16"])

                payload = {
                    "video_inputs": [{
                        "character": {
                            "type": "avatar",
                            "avatar_id": "Anna_public_3_20240108",  # Professional female avatar
                            "avatar_style": "normal"
                        },
                        "voice": {
                            "type": "text",
                            "input_text": request.prompt,
                            "voice_id": "Italian - Female 1"  # Italian voice
                        },
                        "background": {
                            "type": "color",
                            "value": "#0A0A0A"  # StudioCentOS black background
                        }
                    }],
                    "dimension": dimensions,
                    "aspect_ratio": None  # Use dimensions instead
                }

                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=60)) as response:
                        if response.status == 200:
                            data = await response.json()
                            video_id = data.get("data", {}).get("video_id")

                            if video_id:
                                logger.info("heygen_video_created", video_id=video_id)

                                # Poll for completion (HeyGen is async)
                                status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"

                                for _ in range(60):  # Max 5 minutes polling
                                    await asyncio.sleep(5)
                                    async with session.get(status_url, headers=headers) as status_response:
                                        if status_response.status == 200:
                                            status_data = await status_response.json()
                                            status = status_data.get("data", {}).get("status")

                                            if status == "completed":
                                                video_url = status_data.get("data", {}).get("video_url")
                                                thumbnail_url = status_data.get("data", {}).get("thumbnail_url", "")

                                                logger.info("heygen_success", video_url=video_url[:50] if video_url else "")

                                                return VideoGenerationResponse(
                                                    video_url=video_url,
                                                    thumbnail_url=thumbnail_url,
                                                    prompt_used=request.prompt,
                                                    generation_time=time.time() - start_time,
                                                    metadata={
                                                        "provider": "heygen",
                                                        "video_id": video_id,
                                                        "platform": request.platform,
                                                        "aspect_ratio": request.aspect_ratio,
                                                        "cost": "~$0.10/video"
                                                    }
                                                )
                                            elif status == "failed":
                                                error = status_data.get("data", {}).get("error", "Unknown error")
                                                logger.error("heygen_failed", error=error)
                                                break

                                logger.warning("heygen_timeout", video_id=video_id)
                        else:
                            error_text = await response.text()
                            logger.warning("heygen_error", status=response.status, error=error_text[:200])

            except Exception as e:
                logger.warning("heygen_exception", error=str(e))

        # ========================================================================
        # PROVIDER 2: Pollinations (FREE text-to-video fallback) 🆓
        # ========================================================================
        # Pollinations doesn't have native video, but we can create animated GIF/slideshow
        # For real video, we'd need a different provider

        logger.info("video_fallback_pollinations")

        # For now, return an error suggesting HeyGen or placeholder
        base_url = os.getenv('BASE_URL', 'https://studiocentos.it')


        # Build contents
        contents_parts = [{"text": enhanced_video_prompt}]

        # Add input image if provided (image-to-video)
        if request.input_image:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(request.input_image, timeout=aiohttp.ClientTimeout(total=30)) as img_response:
                        if img_response.status == 200:
                            img_bytes = await img_response.read()
                            img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                            content_type = img_response.headers.get('Content-Type', 'image/jpeg')

                            contents_parts.append({
                                "inline_data": {
                                    "mime_type": content_type,
                                    "data": img_b64
                                }
                            })
                            logger.info("input_image_added_for_video", url=request.input_image[:50])
            except Exception as e:
                logger.warning("input_image_failed", error=str(e))

        # Build generation config
        generation_config = {
            "response_modalities": ["VIDEO"],
            "video_config": {
                "duration_seconds": request.duration,
                "aspect_ratio": request.aspect_ratio,
                "resolution": "1080p",
                "fps": 30,
                "include_audio": True  # Veo 3.1 native audio!
            }
        }

        # Add Google Search if enabled
        tools = []
        if request.use_google_search:
            tools.append({"google_search": {}})
            logger.info("google_search_enabled_video")

        payload = {
            "contents": [{"parts": contents_parts}],
            "generationConfig": generation_config
        }

        if tools:
            payload["tools"] = tools

        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            # Video generation can take 60-180 seconds
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=300)) as response:
                if response.status == 200:
                    data = await response.json()

                    # Extract video from response
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])

                        video_data = None
                        thumbnail_data = None

                        for part in parts:
                            if "inline_data" in part:
                                mime_type = part["inline_data"]["mime_type"]

                                if "video" in mime_type:
                                    video_data = part["inline_data"]["data"]
                                elif "image" in mime_type and not thumbnail_data:
                                    thumbnail_data = part["inline_data"]["data"]  # First frame as thumbnail

                        if video_data:
                            # Save video
                            save_dir = Path("/app/media/generated/videos")
                            save_dir.mkdir(parents=True, exist_ok=True)

                            hash_id = hashlib.md5(request.prompt.encode()).hexdigest()[:8]
                            video_filename = f"veo_{int(time.time())}_{hash_id}.mp4"
                            video_path = save_dir / video_filename

                            video_bytes = base64.b64decode(video_data)
                            with open(video_path, 'wb') as f:
                                f.write(video_bytes)

                            # Save thumbnail
                            thumbnail_filename = f"veo_{int(time.time())}_{hash_id}_thumb.jpg"
                            if thumbnail_data:
                                thumb_bytes = base64.b64decode(thumbnail_data)
                            else:
                                # Generate placeholder thumbnail
                                thumb_bytes = b''  # Thumbnail generation requires ffmpeg

                            if thumb_bytes:
                                thumb_path = save_dir / thumbnail_filename
                                with open(thumb_path, 'wb') as f:
                                    f.write(thumb_bytes)

                            base_url = os.getenv('BASE_URL', 'https://studiocentos.it')

                            logger.info("veo_video_success",
                                      duration=request.duration,
                                      size_mb=len(video_bytes) / (1024*1024),
                                      platform=request.platform)

                            return VideoGenerationResponse(
                                video_url=f"{base_url}/ai/media/generated/videos/{video_filename}",
                                thumbnail_url=f"{base_url}/ai/media/generated/videos/{thumbnail_filename}" if thumb_bytes else "",
                                prompt_used=enhanced_video_prompt,
                                generation_time=time.time() - start_time,
                                metadata={
                                    "provider": "veo-3.1",
                                    "duration_seconds": request.duration,
                                    "aspect_ratio": request.aspect_ratio,
                                    "platform": request.platform,
                                    "resolution": "1080p",
                                    "has_audio": True,
                                    "cost": "~$0.10-0.30"  # Estimated
                                }
                            )

                    logger.error("veo_no_video_data", response=str(data)[:200])
                    raise HTTPException(status_code=500, detail="Video generation failed - no video data in response")

                else:
                    error_text = await response.text()
                    logger.error("veo_error", status=response.status, error=error_text[:300])
                    raise HTTPException(status_code=response.status, detail=f"Veo API error: {error_text[:200]}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("veo_exception", error=str(e))
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")


# ============================================================================
# BATCH CONTENT GENERATION FOR SOCIAL MEDIA 🚀
# ============================================================================

class BatchContentRequest(BaseModel):
    """Request for batch social media content generation."""
    topic: str = Field(..., description="Main topic/campaign theme")
    platforms: List[str] = Field(default=["instagram", "facebook", "tiktok", "linkedin"], description="Target platforms")
    post_count: int = Field(default=1, ge=1, le=5, description="Number of posts per platform")
    story_count: int = Field(default=3, ge=0, le=10, description="Number of stories (Instagram/Facebook)")
    video_count: int = Field(default=1, ge=0, le=3, description="Number of videos (Reels/TikTok)")
    style: str = Field(default="professional", description="Visual style")
    use_pro_quality: bool = Field(default=False, description="Use Nano Banana Pro for 4K quality")

class BatchContentItem(BaseModel):
    """Single generated content item."""
    platform: str
    content_type: str  # "post", "story", "video"
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    caption: str
    hashtags: List[str]
    aspect_ratio: str
    metadata: dict

class BatchContentResponse(BaseModel):
    """Response with all generated content."""
    items: List[BatchContentItem]
    generation_time: float
    total_cost_estimate: float
    metadata: dict


@router.post("/content/batch/generate", response_model=BatchContentResponse)
async def batch_generate_social_content(request: BatchContentRequest):
    """
    🚀 BATCH GENERATOR - Generate complete social media campaign.

    Generates for a full day:
    - 1 post per platform (Instagram, Facebook, TikTok, LinkedIn)
    - 3 stories (Instagram/Facebook)
    - 1 video (Reels/TikTok)

    Example: 1 topic → 4 posts + 3 stories + 1 video = 8 assets ready to publish!

    Perfect for:
    - Daily content automation
    - Campaign launches
    - Product promotions
    - Event coverage
    """
    import asyncio
    import time

    logger.info("batch_generate_start",
               topic=request.topic[:50],
               platforms=request.platforms,
               posts=request.post_count,
               stories=request.story_count,
               videos=request.video_count)

    start_time = time.time()
    items = []
    total_cost = 0.0

    # Platform specifications - usa PLATFORM_CONFIGS globale con fallback per campi legacy
    # NOTA: PLATFORM_CONFIGS è definito sotto (linea ~2240), contiene configs complete.
    # Per retrocompatibilità, estraiamo solo i campi necessari qui.
    def get_legacy_config(platform: str) -> dict:
        """Estrae config legacy da PLATFORM_CONFIGS globale."""
        full_config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS.get("instagram", {}))
        return {
            "post_ratio": full_config.get("image_ratio", "1:1"),
            "story_ratio": "9:16",  # Stories sempre 9:16
            "hashtag_count": full_config.get("optimal_hashtags", 10),
            "caption_length": full_config.get("optimal_chars", 150)
        }

    # ========================================================================
    # STEP 1: Generate captions for all posts
    # ========================================================================
    logger.info("batch_step_1", step="Generating captions")

    caption_tasks = []
    for platform in request.platforms:
        config = get_legacy_config(platform)

        for i in range(request.post_count):
            caption_prompt = f"""
Create a {platform} post caption about: {request.topic}

Requirements:
- Platform: {platform.upper()}
- Tone: {request.style}, engaging, professional
- Length: max {config['caption_length']} characters
- Include {config['hashtag_count']} relevant hashtags
- Call-to-action at the end
- Optimized for StudioCentOS digital agency brand

Format:
[Caption text]

Hashtags: [hashtags]
"""
            caption_tasks.append((platform, "post", caption_prompt))

    # Generate story captions
    if request.story_count > 0 and any(p in ["instagram", "facebook"] for p in request.platforms):
        for i in range(request.story_count):
            story_prompt = f"""
Create Instagram/Facebook story text about: {request.topic}

Requirements:
- Very short, punchy text (max 50 chars)
- Story #{i+1} of {request.story_count}
- Engaging, creates curiosity
- Call-to-action (swipe up, DM us, etc)

Format:
[Story text]
"""
            caption_tasks.append(("instagram", "story", story_prompt))

    # Generate video scripts
    if request.video_count > 0:
        for i in range(request.video_count):
            video_prompt = f"""
Create a 15-second video script for Instagram Reel/TikTok about: {request.topic}

Requirements:
- Hook (first 3 seconds)
- Value/Problem-solution (8 seconds)
- CTA (4 seconds)
- Total: 15 seconds
- Engaging, fast-paced
- Include visual directions

Format:
[0-3s] HOOK: [text]
[3-11s] VALUE: [text]
[11-15s] CTA: [text]

Hashtags: [hashtags]
"""
            caption_tasks.append(("instagram", "video", video_prompt))

    # Generate all captions in parallel (fast!)
    caption_results = []
    for platform, content_type, prompt in caption_tasks:
        try:
            content = await generate_with_ai(prompt)
            caption_results.append((platform, content_type, content))
        except Exception as e:
            logger.error("caption_generation_failed", error=str(e))
            caption_results.append((platform, content_type, "Caption generation failed"))

    # ========================================================================
    # STEP 2: Generate images for posts
    # ========================================================================
    logger.info("batch_step_2", step="Generating post images")

    image_tasks = []
    for platform in request.platforms:
        config = get_legacy_config(platform)

        for i in range(request.post_count):
            image_req = ImageGenerationRequest(
                prompt=f"Professional {platform} post image about: {request.topic}. Modern, engaging, premium quality.",
                style=request.style,
                aspect_ratio=config["post_ratio"],
                platform=platform,
                provider="pro" if request.use_pro_quality else "auto",
                resolution="4K" if request.use_pro_quality else "1K"
            )
            image_tasks.append((platform, "post", image_req))

    # Generate images in parallel
    image_results = await asyncio.gather(*[
        generate_image(req) for _, _, req in image_tasks
    ], return_exceptions=True)

    for (platform, content_type, _), result in zip(image_tasks, image_results):
        if isinstance(result, Exception):
            logger.error("image_generation_failed", error=str(result))
            continue

        # Find matching caption
        caption_match = next((c for p, ct, c in caption_results if p == platform and ct == content_type), "")

        # Extract hashtags
        hashtags = []
        if "Hashtags:" in caption_match:
            hashtag_line = caption_match.split("Hashtags:")[-1].strip()
            hashtags = [h.strip() for h in hashtag_line.split("#") if h.strip()][:platform_configs[platform]["hashtag_count"]]

        items.append(BatchContentItem(
            platform=platform,
            content_type="post",
            image_url=result.image_url,
            caption=caption_match.split("Hashtags:")[0].strip() if caption_match else "",
            hashtags=hashtags,
            aspect_ratio=platform_configs[platform]["post_ratio"],
            metadata=result.metadata
        ))

        # Estimate cost
        if request.use_pro_quality:
            total_cost += 0.05  # Pro mode ~$0.05/image
        else:
            total_cost += 0.0  # Standard mode FREE tier

    # ========================================================================
    # STEP 3: Generate stories
    # ========================================================================
    if request.story_count > 0:
        logger.info("batch_step_3", step=f"Generating {request.story_count} stories")

        story_tasks = []
        for i in range(request.story_count):
            story_req = ImageGenerationRequest(
                prompt=f"Instagram story #{i+1} about: {request.topic}. Eye-catching, vertical format, premium.",
                style="creative",
                aspect_ratio="9:16",
                platform="instagram",
                provider="auto"
            )
            story_tasks.append(story_req)

        story_results = await asyncio.gather(*[
            generate_image(req) for req in story_tasks
        ], return_exceptions=True)

        for i, result in enumerate(story_results):
            if isinstance(result, Exception):
                continue

            story_caption = next((c for p, ct, c in caption_results if ct == "story"), "")

            items.append(BatchContentItem(
                platform="instagram",
                content_type="story",
                image_url=result.image_url,
                caption=story_caption,
                hashtags=[],
                aspect_ratio="9:16",
                metadata=result.metadata
            ))

    # ========================================================================
    # STEP 4: Generate videos (if requested)
    # ========================================================================
    if request.video_count > 0:
        logger.info("batch_step_4", step=f"Generating {request.video_count} videos")

        for i in range(request.video_count):
            try:
                video_caption = next((c for p, ct, c in caption_results if ct == "video"), "")

                video_req = VideoGenerationRequest(
                    prompt=f"Instagram Reel / TikTok video about: {request.topic}. {video_caption[:200]}",
                    duration=15,
                    aspect_ratio="9:16",
                    platform="instagram",
                    style=request.style
                )

                video_result = await generate_video(video_req)

                # Extract hashtags from video caption
                hashtags = []
                if "Hashtags:" in video_caption:
                    hashtag_line = video_caption.split("Hashtags:")[-1].strip()
                    hashtags = [h.strip() for h in hashtag_line.split("#") if h.strip()][:5]

                items.append(BatchContentItem(
                    platform="instagram",
                    content_type="video",
                    video_url=video_result.video_url,
                    caption=video_caption.split("Hashtags:")[0].strip(),
                    hashtags=hashtags,
                    aspect_ratio="9:16",
                    metadata=video_result.metadata
                ))

                total_cost += 0.20  # Video ~$0.20 each

            except Exception as e:
                logger.error("video_generation_failed", error=str(e))

    generation_time = time.time() - start_time

    logger.info("batch_generate_complete",
               total_items=len(items),
               generation_time=generation_time,
               cost=total_cost)

    return BatchContentResponse(
        items=items,
        generation_time=generation_time,
        total_cost_estimate=total_cost,
        metadata={
            "topic": request.topic,
            "platforms": request.platforms,
            "quality": "PRO (4K)" if request.use_pro_quality else "STANDARD (1K)",
            "total_posts": request.post_count * len(request.platforms),
            "total_stories": request.story_count,
            "total_videos": request.video_count,
            "total_assets": len(items)
        }
    )


@router.post("/leads/search", response_model=List[LeadItem])
async def search_leads(request: LeadSearchRequest):
    """
    Search for potential leads using ML-powered intelligent matching.

    Uses embeddings + vector similarity to find leads matching successful customer patterns.
    """
    try:
        logger.info("lead_search", industry=request.industry, location=request.location)

        leads = await lead_intelligence_agent.search_leads(
            request=request,
            max_results=5
        )

        return leads

    except Exception as e:
        logger.error("lead_search_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TRANSLATION ENDPOINTS - AI Portfolio Translation
# ============================================================================

class TranslationRequest(BaseModel):
    """Request for AI translation."""
    title: str = Field(..., description="Title to translate")
    description: str = Field(..., description="Description to translate")
    source_language: str = Field(default="it", description="Source language code")
    target_languages: List[str] = Field(default=["en", "es"], description="Target language codes")


class TranslationItem(BaseModel):
    """Single language translation."""
    title: str
    description: str


class TranslationResponse(BaseModel):
    """Response with all translations."""
    translations: Dict[str, TranslationItem]
    source_language: str
    provider: str = "huggingface"


async def translate_with_ai(text: str, source_lang: str, target_lang: str) -> str:
    """Translate text using HuggingFace AI."""
    api_key = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HUGGINGFACE_API_KEY") or settings.huggingface_token_resolved

    if not api_key:
        raise ValueError("HUGGINGFACE_TOKEN not configured")

    api_url = "https://router.huggingface.co/v1/chat/completions"

    language_names = {
        "it": "Italian",
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "pt": "Portuguese"
    }

    src_name = language_names.get(source_lang, source_lang)
    tgt_name = language_names.get(target_lang, target_lang)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": [
            {
                "role": "system",
                "content": f"You are a professional translator. Translate the following text from {src_name} to {tgt_name}. Provide ONLY the translated text, no explanations, no quotes, no additional formatting. Maintain the same tone, style and meaning."
            },
            {"role": "user", "content": text}
        ],
        "max_tokens": 500,
        "temperature": 0.3
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(api_url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

        raise Exception(f"HuggingFace API error: {response.status_code} - {response.text}")


@router.post("/translate/portfolio", response_model=TranslationResponse)
async def translate_portfolio(request: TranslationRequest):
    """
    Translate portfolio content (title + description) to multiple languages using AI.

    Uses Llama 3.2 for high-quality translation maintaining marketing tone.
    """
    try:
        logger.info("translate_portfolio",
                   title_len=len(request.title),
                   description_len=len(request.description),
                   targets=request.target_languages)

        translations = {}

        for target_lang in request.target_languages:
            if target_lang == request.source_language:
                continue

            # Translate title
            translated_title = await translate_with_ai(
                request.title,
                request.source_language,
                target_lang
            )

            # Translate description
            translated_description = await translate_with_ai(
                request.description,
                request.source_language,
                target_lang
            )

            translations[target_lang] = TranslationItem(
                title=translated_title,
                description=translated_description
            )

            logger.info("translation_complete",
                       target=target_lang,
                       title_result=translated_title[:50])

        return TranslationResponse(
            translations=translations,
            source_language=request.source_language,
            provider="huggingface"
        )

    except Exception as e:
        logger.error("translation_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


class BusinessDNARequest(BaseModel):
    company_name: str = Field(..., description="Company name")
    tagline: str = Field(..., description="Company tagline")
    website: str = Field(default="", description="Company website")
    fonts: List[str] = Field(default=["Basecold", "Montserrat"], description="Brand fonts")
    colors: Dict[str, str] = Field(default={"primary": "#D4AF37", "secondary": "#0A0A0A", "accent": "#FAFAFA"}, description="Brand colors")
    brand_attributes: List[str] = Field(default=["Professional", "Modern"], description="Brand characteristics")
    tone_of_voice: List[str] = Field(default=["Confident", "Authentic"], description="Communication style")
    business_overview: str = Field(..., description="Brief business description")


@router.post("/business-dna/generate")
async def generate_business_dna(
    company_name: str = Form(...),
    tagline: str = Form(...),
    business_overview: str = Form(...),
    website: str = Form(default=""),
    fonts: List[str] = Form(default=[]),
    colors: str = Form(default="{}"),
    brand_attributes: List[str] = Form(default=[]),
    tone_of_voice: List[str] = Form(default=[]),
    logo: Optional[UploadFile] = File(default=None)
):
    """
    🎨 Generate BUSINESS DNA PROFILE visual (like example image).

    Creates comprehensive brand identity board with:
    - Logo display with company name (upload custom logo or use default)
    - Color palette swatches
    - Font showcase (Aa samples)
    - Brand attributes tags
    - Tone of voice descriptors
    - Business overview paragraph
    - Professional dark theme with gold accents

    Output: PNG 1920x1080 ready for social media/presentations
    """
    from app.domain.marketing.image_branding import image_branding
    from fastapi.responses import Response
    import json

    logger.info("generate_business_dna", company=company_name)

    try:
        # Parse colors from JSON string
        colors_dict = {"primary": "#D4AF37", "secondary": "#0A0A0A", "accent": "#FAFAFA"}
        if colors and colors != "{}":
            try:
                colors_dict = json.loads(colors)
            except json.JSONDecodeError:
                logger.warning("Failed to parse colors JSON, using defaults")

        # Read logo file if provided
        logo_bytes = None
        if logo:
            logo_bytes = await logo.read()
            logger.info(f"Custom logo uploaded: {logo.filename}, size: {len(logo_bytes)} bytes")

        # Set defaults if empty
        final_fonts = fonts if fonts else ["Basecold", "Montserrat"]
        final_brand_attrs = brand_attributes if brand_attributes else ["Professional", "Modern"]
        final_tov = tone_of_voice if tone_of_voice else ["Confident", "Authentic"]

        image_bytes = image_branding.create_business_dna_profile(
            company_name=company_name,
            tagline=tagline,
            website=website or "",
            fonts=final_fonts,
            colors=colors_dict,
            brand_attributes=final_brand_attrs,
            tone_of_voice=final_tov,
            business_overview=business_overview,
            logo_bytes=logo_bytes
        )

        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={"Content-Disposition": f'inline; filename="business_dna_{company_name.lower().replace(" ", "_")}.png"'}
        )
    except Exception as e:
        logger.error("business_dna_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate Business DNA: {str(e)}")


# =============================================================================
# SOCIAL POST INTELLIGENCE - Multi-Platform Optimizer
# =============================================================================

# Platform-specific configurations
PLATFORM_CONFIGS = {
    "instagram": {
        "max_chars": 2200,
        "optimal_chars": 150,
        "max_hashtags": 30,
        "optimal_hashtags": 11,
        "emoji_density": "high",
        "tone": "casual, visual, inspiring",
        "best_times": ["11:00", "14:00", "19:00", "21:00"],
        "best_days": ["Tuesday", "Wednesday", "Friday"],
        "image_ratio": "1:1",
        "cta_style": "soft",
    },
    "linkedin": {
        "max_chars": 3000,
        "optimal_chars": 1300,
        "max_hashtags": 5,
        "optimal_hashtags": 3,
        "emoji_density": "low",
        "tone": "professional, insightful, data-driven",
        "best_times": ["07:30", "12:00", "17:00"],
        "best_days": ["Tuesday", "Wednesday", "Thursday"],
        "image_ratio": "1.91:1",
        "cta_style": "professional",
    },
    "twitter": {
        "max_chars": 280,
        "optimal_chars": 100,
        "max_hashtags": 3,
        "optimal_hashtags": 2,
        "emoji_density": "medium",
        "tone": "witty, concise, provocative",
        "best_times": ["09:00", "12:00", "17:00"],
        "best_days": ["Wednesday", "Thursday"],
        "image_ratio": "16:9",
        "cta_style": "direct",
    },
    "facebook": {
        "max_chars": 63206,
        "optimal_chars": 80,
        "max_hashtags": 3,
        "optimal_hashtags": 2,
        "emoji_density": "medium",
        "tone": "friendly, conversational, engaging",
        "best_times": ["13:00", "16:00", "21:00"],
        "best_days": ["Thursday", "Friday", "Saturday"],
        "image_ratio": "1.91:1",
        "cta_style": "friendly",
    },
    "tiktok": {
        "max_chars": 2200,
        "optimal_chars": 100,
        "max_hashtags": 5,
        "optimal_hashtags": 4,
        "emoji_density": "very_high",
        "tone": "trendy, fun, authentic, viral",
        "best_times": ["12:00", "15:00", "19:00"],
        "best_days": ["Tuesday", "Thursday", "Friday"],
        "image_ratio": "9:16",
        "cta_style": "loud",
    },
}


class MultiPlatformRequest(BaseModel):
    """Request for multi-platform content generation."""
    idea: str = Field(..., description="The core content idea or message")
    platforms: List[str] = Field(
        default=["instagram", "linkedin", "twitter", "facebook", "tiktok"],
        description="Target platforms"
    )
    brand_context: Optional[str] = Field(None, description="Brand DNA context")
    include_hashtags: bool = Field(default=True)
    include_emojis: bool = Field(default=True)
    generate_image_prompts: bool = Field(default=True)
    language: str = Field(default="it", description="Output language: it, en")


class PlatformContent(BaseModel):
    """Content optimized for a specific platform."""
    platform: str
    content: str
    hashtags: List[str]
    best_post_time: str
    best_day: str
    char_count: int
    optimal_char_count: int
    image_prompt: Optional[str] = None
    image_ratio: str
    engagement_tips: List[str]


class MultiPlatformResponse(BaseModel):
    """Response with content for all platforms."""
    original_idea: str
    generated_at: str
    platform_contents: List[PlatformContent]
    scheduling_suggestion: dict


@router.post("/content/multi-platform", response_model=MultiPlatformResponse)
async def generate_multi_platform_content(request: MultiPlatformRequest):
    """
    🌐 ONE POST → ALL PLATFORMS - Smart Social Content Multiplier

    Takes a single content idea and generates optimized versions for each platform:
    - Instagram: Visual, emoji-rich, 11 hashtags, casual tone
    - LinkedIn: Professional, data-driven, 3 hashtags, long-form
    - Twitter/X: Punchy, max 280 chars, 2 hashtags, provocative
    - Facebook: Friendly, conversational, medium length
    - TikTok: Trendy, viral hooks, heavy emojis

    Includes:
    - Best posting times per platform
    - Image prompts for each
    - Engagement optimization tips
    """
    from datetime import datetime, timedelta
    import json

    logger.info("multi_platform_generate", idea=request.idea[:50], platforms=request.platforms)

    platform_contents = []

    for platform in request.platforms:
        if platform not in PLATFORM_CONFIGS:
            continue

        config = PLATFORM_CONFIGS[platform]

        # Build platform-specific prompt
        emoji_instruction = {
            "very_high": "Usa MOLTE emoji creative in tutto il testo (almeno 5-8)",
            "high": "Usa emoji appropriate e frequenti (4-6)",
            "medium": "Usa qualche emoji appropriata (2-3)",
            "low": "Usa emoji con parsimonia, massimo 1-2 se appropriato",
        }.get(config["emoji_density"], "")

        prompt = f"""Adatta questo contenuto per {platform.upper()}:

IDEA ORIGINALE: {request.idea}

REGOLE {platform.upper()}:
- Lunghezza ottimale: {config['optimal_chars']} caratteri (max {config['max_chars']})
- Tono: {config['tone']}
- {emoji_instruction if request.include_emojis else 'NON usare emoji'}
- {"Genera " + str(config['optimal_hashtags']) + " hashtag rilevanti alla fine" if request.include_hashtags else "NON includere hashtag"}

OUTPUT (JSON valido):
{{
    "content": "Il testo del post ottimizzato",
    "hashtags": ["hashtag1", "hashtag2"],
    "engagement_tips": ["tip1", "tip2"],
    "image_prompt": "Prompt per generare immagine adatta"
}}"""

        try:
            response = await generate_with_ai(prompt, request.brand_context)

            # Parse JSON response
            try:
                # Clean response and parse
                clean_response = response.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]
                if clean_response.startswith("```"):
                    clean_response = clean_response[3:]
                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]

                parsed = json.loads(clean_response)
                content = parsed.get("content", response)
                hashtags = parsed.get("hashtags", [])
                tips = parsed.get("engagement_tips", [])
                image_prompt = parsed.get("image_prompt", "")
            except:
                content = response
                hashtags = []
                tips = []
                image_prompt = f"Professional image for {platform} post about: {request.idea[:50]}"

            platform_contents.append(PlatformContent(
                platform=platform,
                content=content,
                hashtags=hashtags[:config["max_hashtags"]],
                best_post_time=config["best_times"][0],
                best_day=config["best_days"][0],
                char_count=len(content),
                optimal_char_count=config["optimal_chars"],
                image_prompt=image_prompt if request.generate_image_prompts else None,
                image_ratio=config["image_ratio"],
                engagement_tips=tips[:3]
            ))

        except Exception as e:
            logger.error("platform_generation_error", platform=platform, error=str(e))
            continue

    # Generate smart scheduling suggestion
    now = datetime.now()
    scheduling = {
        "suggested_week": {
            platform: {
                "day": PLATFORM_CONFIGS[platform]["best_days"][0],
                "time": PLATFORM_CONFIGS[platform]["best_times"][0],
            }
            for platform in request.platforms if platform in PLATFORM_CONFIGS
        },
        "avoid_times": ["Monday 8-10 AM", "Sunday morning", "Friday after 6 PM"],
        "strategy": "Stagger posts across platforms over 2-3 days for maximum reach"
    }

    return MultiPlatformResponse(
        original_idea=request.idea,
        generated_at=datetime.now().isoformat(),
        platform_contents=platform_contents,
        scheduling_suggestion=scheduling
    )


class PostOptimizerRequest(BaseModel):
    """Request to optimize an existing post."""
    content: str = Field(..., description="Existing post content to optimize")
    target_platform: str = Field(..., description="Target platform")
    optimization_goals: List[str] = Field(
        default=["engagement", "reach", "clicks"],
        description="What to optimize for"
    )
    brand_context: Optional[str] = None


class PostOptimizerResponse(BaseModel):
    """Optimized post with suggestions."""
    original_content: str
    optimized_content: str
    improvements: List[str]
    score_before: int
    score_after: int
    hashtag_suggestions: List[str]
    best_post_time: str
    a_b_variants: List[str]


@router.post("/content/optimize", response_model=PostOptimizerResponse)
async def optimize_post(request: PostOptimizerRequest):
    """
    ⚡ POST OPTIMIZER - Make any post perform better

    Analyzes and improves:
    - Hook strength (first line)
    - Emoji usage
    - Hashtag relevance
    - Call-to-action clarity
    - Platform-specific best practices

    Also generates A/B test variants.
    """
    import json

    logger.info("optimize_post", platform=request.target_platform, content_length=len(request.content))

    config = PLATFORM_CONFIGS.get(request.target_platform, PLATFORM_CONFIGS["instagram"])

    prompt = f"""Analizza e ottimizza questo post per {request.target_platform.upper()}:

POST ORIGINALE:
{request.content}

OBIETTIVI: {', '.join(request.optimization_goals)}

ANALIZZA:
1. Hook (prima riga) - è abbastanza forte?
2. Lunghezza - rispetta i {config['optimal_chars']} caratteri ottimali?
3. Tono - è {config['tone']}?
4. CTA - c'è una call-to-action chiara?
5. Emoji - densità appropriata ({config['emoji_density']})?

OUTPUT (JSON valido):
{{
    "optimized_content": "Versione migliorata del post",
    "improvements": ["miglioramento 1", "miglioramento 2"],
    "score_before": 65,
    "score_after": 85,
    "hashtag_suggestions": ["hashtag1", "hashtag2", "hashtag3"],
    "a_b_variants": ["Variante A alternativa", "Variante B alternativa"]
}}"""

    try:
        response = await generate_with_ai(prompt, request.brand_context)

        # Parse response
        try:
            clean_response = response.strip()
            if "```" in clean_response:
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            parsed = json.loads(clean_response)
        except:
            parsed = {
                "optimized_content": request.content,
                "improvements": ["Unable to parse - see raw output"],
                "score_before": 50,
                "score_after": 50,
                "hashtag_suggestions": [],
                "a_b_variants": []
            }

        return PostOptimizerResponse(
            original_content=request.content,
            optimized_content=parsed.get("optimized_content", request.content),
            improvements=parsed.get("improvements", []),
            score_before=parsed.get("score_before", 50),
            score_after=parsed.get("score_after", 75),
            hashtag_suggestions=parsed.get("hashtag_suggestions", [])[:10],
            best_post_time=config["best_times"][0],
            a_b_variants=parsed.get("a_b_variants", [])[:3]
        )

    except Exception as e:
        logger.error("optimize_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


class ClonePostRequest(BaseModel):
    """Request to generate post variations for A/B testing."""
    original_post: str = Field(..., description="Original post to clone")
    platform: str = Field(default="instagram")
    num_variants: int = Field(default=5, ge=2, le=10)
    variation_type: str = Field(
        default="mixed",
        description="Type: hook, tone, length, emoji, mixed"
    )
    brand_context: Optional[str] = None


class ClonePostResponse(BaseModel):
    """Multiple post variants for A/B testing."""
    original: str
    variants: List[dict]
    recommendation: str


@router.post("/content/clone", response_model=ClonePostResponse)
async def clone_post_for_ab_testing(request: ClonePostRequest):
    """
    🧬 CLONE POST - Generate A/B Test Variants

    Creates multiple variations of a post for testing:
    - Different hooks
    - Alternative CTAs
    - Varying emoji usage
    - Length variations
    - Tone shifts
    """
    import json

    logger.info("clone_post", platform=request.platform, variants=request.num_variants)

    prompt = f"""Crea {request.num_variants} varianti del seguente post per {request.platform.upper()}.
Tipo di variazione: {request.variation_type}

POST ORIGINALE:
{request.original_post}

Per ogni variante, cambia {"l'hook iniziale" if request.variation_type == "hook" else "il tono" if request.variation_type == "tone" else "la lunghezza" if request.variation_type == "length" else "l'uso di emoji" if request.variation_type == "emoji" else "diversi aspetti (hook, tono, emoji)"}.

OUTPUT (JSON valido):
{{
    "variants": [
        {{"content": "Variante 1", "focus": "Cosa è stato cambiato"}},
        {{"content": "Variante 2", "focus": "Cosa è stato cambiato"}}
    ],
    "recommendation": "Quale variante probabilmente performerà meglio e perché"
}}"""

    try:
        response = await generate_with_ai(prompt, request.brand_context)

        try:
            clean_response = response.strip()
            if "```" in clean_response:
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            parsed = json.loads(clean_response)
        except:
            parsed = {
                "variants": [{"content": request.original_post, "focus": "Parsing failed"}],
                "recommendation": "Unable to generate variants"
            }

        return ClonePostResponse(
            original=request.original_post,
            variants=parsed.get("variants", [])[:request.num_variants],
            recommendation=parsed.get("recommendation", "Test all variants to find the best performer")
        )

    except Exception as e:
        logger.error("clone_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


class BestTimeRequest(BaseModel):
    """Request best posting time."""
    platform: str
    timezone: str = Field(default="Europe/Rome")
    industry: str = Field(default="general")


class BestTimeResponse(BaseModel):
    """Best posting times for platform."""
    platform: str
    best_times: List[str]
    best_days: List[str]
    avoid_times: List[str]
    engagement_heatmap: dict


@router.post("/scheduling/best-time", response_model=BestTimeResponse)
async def get_best_posting_time(request: BestTimeRequest):
    """
    ⏰ BEST TIME ANALYZER - When to post for maximum engagement

    Returns optimal posting times based on:
    - Platform best practices
    - Industry patterns
    - Day of week analysis
    """
    logger.info("best_time", platform=request.platform, industry=request.industry)

    config = PLATFORM_CONFIGS.get(request.platform, PLATFORM_CONFIGS["instagram"])

    # Build engagement heatmap
    heatmap = {
        "monday": {"morning": 0.6, "afternoon": 0.7, "evening": 0.5},
        "tuesday": {"morning": 0.8, "afternoon": 0.9, "evening": 0.7},
        "wednesday": {"morning": 0.9, "afternoon": 0.95, "evening": 0.8},
        "thursday": {"morning": 0.85, "afternoon": 0.9, "evening": 0.75},
        "friday": {"morning": 0.7, "afternoon": 0.8, "evening": 0.5},
        "saturday": {"morning": 0.5, "afternoon": 0.6, "evening": 0.7},
        "sunday": {"morning": 0.3, "afternoon": 0.5, "evening": 0.6},
    }

    return BestTimeResponse(
        platform=request.platform,
        best_times=config["best_times"],
        best_days=config["best_days"],
        avoid_times=["Monday 8-10 AM", "Sunday morning", "Friday after 6 PM"],
        engagement_heatmap=heatmap
    )


# ============================================================================
# PHASE 7: CONTENT CALENDAR, STORYBOARD, SCHEDULER TRIGGER
# ============================================================================

from app.domain.marketing.content_creator import (
    CalendarConfig,
    CalendarResult,
    PlannedPost,
    StoryboardConfig,
    StoryboardResult,
    StoryboardFrame,
    ContentCreatorAgent,
    SocialPostConfig,
    SocialPlatform,
    ContentTone,
)

# Initialize ContentCreatorAgent singleton
try:
    content_creator_agent = ContentCreatorAgent()
except Exception as e:
    logger.warning(f"ContentCreatorAgent init failed: {e}")
    content_creator_agent = None


class CalendarRequest(BaseModel):
    """Request for monthly content calendar generation."""
    month: str = Field(..., description="Month name (e.g. January)")
    year: int = Field(..., description="Year (e.g. 2025)")
    industry: str = Field(..., description="Client industry sector")
    goal: str = Field(default="brand_awareness", description="Main marketing goal")
    posts_per_week: int = Field(default=3, description="Frequency")
    brand_context: Optional[str] = None
    target_audience: Optional[str] = None


class StoryboardRequest(BaseModel):
    """Request for video storyboard generation."""
    script: str = Field(..., description="The full video script")
    style: str = Field(default="minimalist_brand", description="Visual style")
    brand_context: Optional[str] = None


class ScheduledPostTriggerRequest(BaseModel):
    """Request to trigger just-in-time content generation for a scheduled post."""
    planned_topic: str = Field(..., description="Topic from the calendar plan")
    planned_angle: str = Field(..., description="Angle/hook from the plan")
    platform: str = Field(default="instagram", description="Target platform")
    format: str = Field(default="static", description="reel, carousel, static")
    sector: str = Field(default="generic", description="Industry sector")
    brand_context: Optional[str] = None
    generate_image: bool = Field(default=True)


class ScheduledPostTriggerResponse(BaseModel):
    """Response with generated content (Just-in-Time)."""
    topic: str
    platform: str
    caption: str
    hashtags: List[str]
    image_url: Optional[str] = None
    engagement_score: Optional[int] = None
    metadata: dict


@router.post("/calendar/generate")
async def generate_content_calendar(request: CalendarRequest):
    """
    📅 CONTENT CALENDAR GENERATOR - Just-in-Time Architecture

    Generates a LIGHTWEIGHT monthly content PLAN (topics/angles only).
    Does NOT generate full captions or images to save API costs.
    Use /post/trigger to generate the actual content when scheduled.
    """
    logger.info("generate_calendar", month=request.month, year=request.year, industry=request.industry)

    if not content_creator_agent:
        raise HTTPException(status_code=503, detail="ContentCreatorAgent not initialized")

    try:
        config = CalendarConfig(
            month=request.month,
            year=request.year,
            industry=request.industry,
            goal=request.goal,
            posts_per_week=request.posts_per_week,
            brand_context=request.brand_context,
            target_audience=request.target_audience
        )

        result = await content_creator_agent.generate_monthly_plan(config)

        return {
            "month": result.month,
            "year": result.year,
            "strategy_summary": result.strategy_summary,
            "plan": [p.model_dump() for p in result.plan],
            "total_posts": len(result.plan)
        }

    except Exception as e:
        logger.error("calendar_generation_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/storyboard/generate")
async def generate_video_storyboard(request: StoryboardRequest):
    """
    🎬 VIDEO STORYBOARD GENERATOR

    Converts a video script into a visual storyboard with:
    - Scene-by-scene breakdown
    - Visual descriptions
    - Camera angles
    - Voiceover text
    - Duration per scene
    """
    logger.info("generate_storyboard", script_length=len(request.script))

    if not content_creator_agent:
        raise HTTPException(status_code=503, detail="ContentCreatorAgent not initialized")

    try:
        config = StoryboardConfig(
            script=request.script,
            style=request.style,
            brand_context=request.brand_context
        )

        result = await content_creator_agent.generate_storyboard(config)

        return {
            "frames": [f.model_dump() for f in result.frames],
            "total_duration": result.total_duration,
            "summary": result.summary,
            "scene_count": len(result.frames)
        }

    except Exception as e:
        logger.error("storyboard_generation_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/post/trigger", response_model=ScheduledPostTriggerResponse)
async def trigger_scheduled_post(request: ScheduledPostTriggerRequest):
    """
    ⏰ JUST-IN-TIME POST GENERATOR - Scheduler Trigger

    Called by the backend scheduler when it's time to publish a planned post.
    Generates the FULL content (caption + image) at the moment of need.

    Benefits:
    - Uses up-to-date AI models
    - Fresh content generation
    - Saves API costs (no pre-generation)
    """
    logger.info("trigger_post",
                topic=request.planned_topic,
                platform=request.platform,
                format=request.format)

    if not content_creator_agent:
        raise HTTPException(status_code=503, detail="ContentCreatorAgent not initialized")

    try:
        # Map string platform to enum
        platform_map = {
            "instagram": SocialPlatform.INSTAGRAM,
            "linkedin": SocialPlatform.LINKEDIN,
            "twitter": SocialPlatform.TWITTER,
            "facebook": SocialPlatform.FACEBOOK,
            "tiktok": SocialPlatform.TIKTOK,
        }
        platform_enum = platform_map.get(request.platform.lower(), SocialPlatform.INSTAGRAM)

        # Build message from topic + angle
        message = f"{request.planned_topic}. Angle: {request.planned_angle}"

        config = SocialPostConfig(
            platform=platform_enum,
            message=message,
            tone=ContentTone.CASUAL,
            include_hashtags=True,
            include_emojis=True,
            post_type="educational",
            brand_context=request.brand_context,
            generate_image=request.generate_image,
            sector=request.sector
        )

        result = await content_creator_agent.generate_social_post(config)

        # Extract hashtags from content
        hashtags = []
        if "#" in result.content:
            parts = result.content.split("#")
            for part in parts[1:]:
                tag = part.split()[0] if part.split() else ""
                if tag:
                    hashtags.append(f"#{tag}")

        return ScheduledPostTriggerResponse(
            topic=request.planned_topic,
            platform=request.platform,
            caption=result.content,
            hashtags=hashtags[:10],
            image_url=result.image_url,
            engagement_score=result.metadata.get("engagement_score", {}).get("score"),
            metadata=result.metadata
        )

    except Exception as e:
        logger.error("post_trigger_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
