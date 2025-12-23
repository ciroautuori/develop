"""
Image Generation Agent - AI-Powered Image Creation.

This agent specializes in generating high-quality images for marketing content
using multiple AI providers (Google Gemini, Hugging Face, OpenAI).

Features:
    - Multi-provider support with fallback
    - Intelligent caching
    - Prompt enhancement
    - Cost tracking and optimization
    - Rate limiting

Tools:
    1. generate_image() - Generate image from prompt
    2. clear_cache() - Clear image cache
    3. get_statistics() - Get usage stats

Example:
    >>> agent = ImageGenerationAgent(config=config)
    >>> result = await agent.generate_image(
    ...     prompt="Modern office workspace",
    ...     style="professional",
    ...     width=1024,
    ...     height=1024
    ... )
"""

import logging
import asyncio
import hashlib
import json
import time
import aiohttp
import os
import base64
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
from enum import Enum

from pydantic import BaseModel, Field
from openai import AsyncOpenAI

from app.infrastructure.agents.base_agent import BaseAgent, AgentConfig, AgentCapability
from app.infrastructure.agents.task import Task, TaskOutput
from app.domain.marketing.image_branding import ImageBranding

logger = logging.getLogger(__name__)


# ============================================================================
# BRAND DNA - IMAGE GENERATION STYLE GUIDE
# ============================================================================

BRAND_DNA_IMAGE = {
    "identity": {
        "name": "StudioCentOS",
        "tagline": "Tecnologia enterprise per la tua PMI",
    },
    "colors": {
        "primary": "#D4AF37",      # Oro - Eccellenza
        "secondary": "#0A0A0A",    # Nero - Professionalità
        "accent": "#FAFAFA",       # Bianco - Pulizia
        "gradients": {
            "premium": "linear-gradient(135deg, #D4AF37 0%, #0A0A0A 100%)",
            "gold": "linear-gradient(135deg, #D4AF37 0%, #B8960C 100%)",
        },
    },
    "visual_style": {
        "primary": "professional, clean, modern, minimal, premium",
        "secondary": "warm, approachable, Italian",
        "avoid": "cold, corporate, generic stock, cluttered",
    },
    "image_characteristics": {
        "lighting": "Natural, soft shadows, warm tones",
        "composition": "Clean, balanced, focus on subject",
        "mood": "Confident, innovative, approachable",
        "quality": "High resolution, sharp, professional grade",
    },
}

# ============================================================================
# PLATFORM ASPECT RATIOS - Auto-detect correct dimensions per platform
# ============================================================================

PLATFORM_ASPECT_RATIOS = {
    # Instagram
    "instagram_post": {"width": 1080, "height": 1080, "ratio": "1:1"},
    "instagram_portrait": {"width": 1080, "height": 1350, "ratio": "4:5"},
    "instagram_story": {"width": 1080, "height": 1920, "ratio": "9:16"},
    "instagram_reel": {"width": 1080, "height": 1920, "ratio": "9:16"},
    "instagram_carousel": {"width": 1080, "height": 1350, "ratio": "4:5"},
    # LinkedIn
    "linkedin_post": {"width": 1200, "height": 627, "ratio": "1.91:1"},
    "linkedin_square": {"width": 1200, "height": 1200, "ratio": "1:1"},
    "linkedin_article": {"width": 1200, "height": 644, "ratio": "1.91:1"},
    # Facebook
    "facebook_post": {"width": 1200, "height": 630, "ratio": "1.91:1"},
    "facebook_story": {"width": 1080, "height": 1920, "ratio": "9:16"},
    "facebook_cover": {"width": 820, "height": 312, "ratio": "2.63:1"},
    # Twitter/X
    "twitter_post": {"width": 1600, "height": 900, "ratio": "16:9"},
    "twitter_square": {"width": 1080, "height": 1080, "ratio": "1:1"},
    # TikTok
    "tiktok_video": {"width": 1080, "height": 1920, "ratio": "9:16"},
    # YouTube
    "youtube_thumbnail": {"width": 1280, "height": 720, "ratio": "16:9"},
    "youtube_shorts": {"width": 1080, "height": 1920, "ratio": "9:16"},
    "youtube_banner": {"width": 2560, "height": 1440, "ratio": "16:9"},
    # Pinterest
    "pinterest_pin": {"width": 1000, "height": 1500, "ratio": "2:3"},
    "pinterest_square": {"width": 1000, "height": 1000, "ratio": "1:1"},
    # Threads
    "threads_post": {"width": 1080, "height": 1080, "ratio": "1:1"},
    # Default
    "default": {"width": 1080, "height": 1080, "ratio": "1:1"},
}


def get_platform_dimensions(platform: str, content_type: str = "post") -> dict:
    """Get recommended dimensions for a platform and content type."""
    key = f"{platform.lower()}_{content_type}"
    return PLATFORM_ASPECT_RATIOS.get(key, PLATFORM_ASPECT_RATIOS["default"])


# Style presets for image generation
IMAGE_STYLE_PRESETS = {
    "professional": {
        "description": "Fotografia professionale, corporate moderno",
        "lighting": "Luce naturale, soft shadows",
        "composition": "Pulita, simmetrica, spazio negativo",
        "mood": "Affidabile, competente, premium",
        "prompt_suffix": "professional corporate photography, high quality, 8k, clean lighting, modern office aesthetic, premium feel",
    },
    "creative": {
        "description": "Digitale, artistico, dinamico",
        "lighting": "Drammatico, colori vibranti",
        "composition": "Asimmetrica, movimento, energia",
        "mood": "Innovativo, energico, moderno",
        "prompt_suffix": "artistic, vibrant colors, creative composition, digital art, dynamic, energetic",
    },
    "minimal": {
        "description": "Minimalista, essenziale, tipografico",
        "lighting": "Flat, uniforme",
        "composition": "Tanto spazio bianco, focus singolo",
        "mood": "Elegante, sofisticato, chiaro",
        "prompt_suffix": "minimalist design, clean lines, simple, flat design, white space, elegant, modern minimal",
    },
    "elegant": {
        "description": "Lussuoso, premium, raffinato",
        "lighting": "Golden hour, warm tones",
        "composition": "Simmetrica, classica",
        "mood": "Prestigioso, esclusivo, di qualità",
        "prompt_suffix": "luxurious, premium quality, refined, golden accents, sophisticated, elegant design",
    },
    "tech": {
        "description": "Tecnologico, futuristico, digitale",
        "lighting": "Neon accents, dark mode",
        "composition": "Geometrica, linee pulite",
        "mood": "Innovativo, all'avanguardia, smart",
        "prompt_suffix": "futuristic technology, digital, neon accents, dark background, geometric, clean lines, modern tech",
    },
    # === NEW STYLE PRESETS ===
    "neon_glow": {
        "description": "Neon accents su sfondo scuro, cyberpunk vibes",
        "lighting": "Neon edge lighting, ambiente buio",
        "composition": "Alto contrasto, soggetto centrale",
        "mood": "Moderno, edgy, tech-forward",
        "prompt_suffix": "neon glow effect, dark background, cyberpunk aesthetic, vibrant edge lighting, 8k, electric atmosphere",
    },
    "sunset_warm": {
        "description": "Golden hour warmth, bellezza naturale",
        "lighting": "Golden hour, luce solare calda",
        "composition": "Naturale, organica, invitante",
        "mood": "Caldo, accogliente, ottimistico",
        "prompt_suffix": "golden hour lighting, warm sunset tones, natural beauty, cozy atmosphere, soft shadows",
    },
    "gradient_abstract": {
        "description": "Sfondi gradient astratti, moderni",
        "lighting": "Gradienti smooth, no ombre dure",
        "composition": "Minimalista, astratto, pulito",
        "mood": "Moderno, pulito, sofisticato",
        "prompt_suffix": "smooth gradient background, abstract shapes, minimal design, modern aesthetic, soft colors transition",
    },
    "glassmorphism": {
        "description": "Elementi UI in vetro smerigliato, premium",
        "lighting": "Soft backlight, translucent",
        "composition": "Layered, profondità, trasparenza",
        "mood": "Premium, moderno, innovativo",
        "prompt_suffix": "glassmorphism design, frosted glass effect, translucent layers, modern UI, soft blur, premium feel",
    },
    "dark_luxury": {
        "description": "Nero profondo con accenti oro, ultra premium",
        "lighting": "Drammatico, low key, gold highlights",
        "composition": "Elegante, minimale, premium",
        "mood": "Lussuoso, esclusivo, premium",
        "prompt_suffix": "dark luxury aesthetic, gold accents on deep black, premium feel, elegant, cinematic lighting, 8k",
    },
    # === STYLE PRESETS 2.0 ===
    "cyberpunk": {
        "description": "Città futuristica, pioggia, luci neon blu/viola",
        "lighting": "Volumetric neon, night, reflections",
        "composition": "Densa, verticale, futuristica",
        "mood": "High tech, low life, cinematic",
        "prompt_suffix": "cyberpunk city style, neon lights, rain reflections, futuristic, cinematic, high detail, blue and purple palette",
    },
    "editorial": {
        "description": "Stile rivista di moda, pulito, fashion",
        "lighting": "Studio lighting, softbox",
        "composition": "Portrait, fashion magazine layout",
        "mood": "Trendy, sofisticato, high-end",
        "prompt_suffix": "editorial fashion photography, vogue style, high fashion, studio lighting, clean background, sharp focus",
    },
    "flat_vector": {
        "description": "Illustrazione vettoriale piatta, colori solidi",
        "lighting": "No shadows, flat colors",
        "composition": "Geometrica, semplice, iconica",
        "mood": "Playful, moderno, chiaro",
        "prompt_suffix": "flat vector illustration, clean lines, solid colors, minimal, corporate art style, behance, dribbble",
    },
    "3d_render": {
        "description": "Rendering 3D stile Blender/Pixar, cute",
        "lighting": "Global illumination, soft shadows",
        "composition": "Centrale, isometrica o prospettica",
        "mood": "Friendly, moderno, plasticoso",
        "prompt_suffix": "3d render, blender style, clay render, soft lighting, cute, isometric, high quality 3d",
    },
    "vintage_film": {
        "description": "Fotografia analogica, grana, nostalgic",
        "lighting": "Natural, film grain, warm leakage",
        "composition": "Candid, imperfetta, reale",
        "mood": "Nostalgico, autentico, retro",
        "prompt_suffix": "vintage film photography, kodak portra 400, film grain, analog look, nostalgic, warm tones, authentic",
    },
}

# Content type presets
IMAGE_CONTENT_PRESETS = {
    "social_post": {
        "format_hint": "Quadrato o verticale",
        "focus": "Un soggetto principale chiaro",
        "text_space": "Spazio per overlay di testo se necessario",
        "branding": "Logo o colori brand visibili ma non invasivi",
    },
    "story": {
        "format_hint": "Verticale 9:16",
        "focus": "Centro del frame (safe zone)",
        "text_space": "Spazio per testo e sticker in alto e in basso",
        "branding": "Dinamica, accattivante, scroll-stopping",
    },
    "thumbnail": {
        "format_hint": "16:9",
        "focus": "Alto contrasto, colori vivaci",
        "text_space": "Grande, leggibile anche piccolo",
        "branding": "Impatto immediato",
    },
    "cover": {
        "format_hint": "Panoramico",
        "focus": "Logo e colori prominenti",
        "text_space": "Messaggio chiaro",
        "branding": "Safe zones per diversi device",
    },
    "product": {
        "format_hint": "Quadrato o verticale",
        "focus": "Prodotto al centro, sfondo pulito",
        "text_space": "Professionale, ombre soft",
        "branding": "Qualità premium visibile",
    },
}

# Sector-specific modifiers
SECTOR_IMAGE_MODIFIERS = {
    "ristorazione": "ambiente caldo, cibo appetitoso, atmosfera accogliente, dettagli gastronomici, Italian restaurant",
    "hospitality": "lusso, comfort, accoglienza, dettagli hotel, esperienza ospite premium",
    "legal": "professionale, serio, affidabile, ufficio elegante, documenti, legal office",
    "medical": "pulito, sterile, tecnologia medica, fiducia, cura, healthcare professional",
    "retail": "prodotti in vetrina, shopping experience, packaging, cliente soddisfatto, retail store",
    "manufacturing": "industria, macchinari, produzione, qualità, precisione, made in italy, factory",
    "tech": "schermi, codice, server, innovazione, digitale, futuristico, technology workspace",
    "consulting": "meeting, strategia, grafici, professionisti, business discussion, corporate meeting",
}


def get_brand_image_prompt(
    base_prompt: str,
    style: str = "professional",
    content_type: str = "social_post",
    sector: str = None
) -> str:
    """
    Generate enhanced prompt with Brand DNA style guide.

    Args:
        base_prompt: The user's base image description
        style: One of the style presets
        content_type: Type of content being created
        sector: Optional sector for industry-specific styling

    Returns:
        Enhanced prompt with brand guidelines
    """
    style_preset = IMAGE_STYLE_PRESETS.get(style, IMAGE_STYLE_PRESETS["professional"])
    content_preset = IMAGE_CONTENT_PRESETS.get(content_type, IMAGE_CONTENT_PRESETS["social_post"])

    enhanced_prompt = f"""
{base_prompt}

BRAND STUDIOCENTOS STYLE:
- Colori: Oro {BRAND_DNA_IMAGE["colors"]["primary"]}, Nero {BRAND_DNA_IMAGE["colors"]["secondary"]}
- Stile: {BRAND_DNA_IMAGE["visual_style"]["primary"]}
- Evitare: {BRAND_DNA_IMAGE["visual_style"]["avoid"]}

STILE IMMAGINE: {style_preset["description"]}
- Lighting: {style_preset["lighting"]}
- Composizione: {style_preset["composition"]}
- Mood: {style_preset["mood"]}

FORMATO: {content_preset["format_hint"]}
- Focus: {content_preset["focus"]}

{style_preset["prompt_suffix"]}
"""

    # Add sector modifier if specified
    if sector and sector in SECTOR_IMAGE_MODIFIERS:
        enhanced_prompt += f"\n\nSETTORE: {SECTOR_IMAGE_MODIFIERS[sector]}"

    return enhanced_prompt.strip()


# ============================================================================
# ENUMS & MODELS
# ============================================================================

class ImageProvider(str, Enum):
    """Supported image generation providers."""
    GOOGLE_PRO = "google_pro"    # PAID/QUOTA - Gemini 3.0 Pro Image (Nano Banana Pro)
    GOOGLE = "google"            # FREE - Gemini 2.5 Flash Image
    HUGGINGFACE = "huggingface"  # FREE - Stable Diffusion
    OPENAI = "openai"            # PAID - DALL-E 3


class ImageGenerationConfig(BaseModel):
    """Configuration for image generation task."""
    prompt: str = Field(..., description="Image description")
    style: str = Field(default="professional", description="Visual style: professional, creative, minimal, elegant, tech")
    content_type: str = Field(default="social_post", description="Content type: social_post, story, thumbnail, cover, product")
    sector: Optional[str] = Field(default=None, description="Sector: ristorazione, hospitality, legal, medical, retail, manufacturing, tech, consulting")
    width: int = Field(default=1024, description="Image width")
    height: int = Field(default=1024, description="Image height")
    quality: str = Field("standard", description="Image quality (standard/hd)")
    apply_branding: bool = Field(False, description="Whether to apply branding overlay")
    overlay_position: Optional[str] = Field(None, description="Position for text overlay (top, bottom, left, right, center)")

class ImageResult(BaseModel):
    """Result from image generation."""
    image_url: str
    image_id: str
    prompt_used: str
    generation_time: float
    metadata: Dict[str, Any]


# ============================================================================
# UTILITIES
# ============================================================================

class RateLimiter:
    """Token bucket rate limiter for API calls."""

    def __init__(self, requests_per_minute: int = 50):
        self.requests_per_minute = requests_per_minute
        self.tokens = requests_per_minute
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(
                self.requests_per_minute,
                self.tokens + (elapsed * self.requests_per_minute / 60)
            )
            self.last_update = now
            if self.tokens < 1:
                wait_time = (1 - self.tokens) * 60 / self.requests_per_minute
                await asyncio.sleep(wait_time)
                self.tokens = 1
            self.tokens -= 1


class ImageCache:
    """File-based cache for generated images."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = cache_dir / "cache_index.json"
        self.index = {}
        self._load_index()

    def _load_index(self):
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    self.index = json.load(f)
            except json.JSONDecodeError:
                self.index = {}

    def _save_index(self):
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")

    def get_cache_key(self, prompt: str, style: str, size: str) -> str:
        key_data = f"{prompt}:{style}:{size}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        return self.index.get(cache_key)

    def set(self, cache_key: str, result: Dict[str, Any]):
        self.index[cache_key] = result
        self._save_index()


# ============================================================================
# IMAGE GENERATION AGENT
# ============================================================================

class ImageGenerationAgent(BaseAgent):
    """
    Image Generation Agent using multi-provider strategy.
    """

    def __init__(self, config: AgentConfig):
        super().__init__(config)

        # API Keys
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.hf_key = os.getenv('HUGGINGFACE_API_KEY') or os.getenv('HUGGINGFACE_TOKEN')
        self.google_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')

        self.openai_client = AsyncOpenAI(api_key=self.openai_key) if self.openai_key else None

        # Priority: Google Pro (Nano Banana) -> Google Flash -> HF -> OpenAI
        self.providers = [
            ImageProvider.GOOGLE_PRO,
            ImageProvider.GOOGLE,
            ImageProvider.HUGGINGFACE,
            ImageProvider.OPENAI
        ]

        # Infrastructure
        self.cache_dir = Path("media/cache/images")
        self.cache = ImageCache(self.cache_dir)
        self.rate_limiter = RateLimiter(requests_per_minute=50)

        # Metrics
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'errors': 0,
            'by_provider': {p.value: 0 for p in ImageProvider}
        }

        # Branding
        self.branding = ImageBranding()

    async def on_start(self) -> None:
        """Initialize agent resources."""
        await super().on_start()
        logger.info(f"ImageAgent started. Providers: {[p.value for p in self.providers]}")

    def get_capabilities(self) -> List[AgentCapability]:
        """Get agent capabilities."""
        return [
            AgentCapability(
                name="generate_image",
                description="Generate AI image from prompt",
                input_schema={"prompt": "str", "style": "str", "width": "int", "height": "int", "apply_branding": "bool"},
                output_schema={"image_url": "str", "metadata": "dict"}
            ),
            AgentCapability(
                name="get_statistics",
                description="Get usage statistics",
                input_schema={},
                output_schema={"stats": "dict"}
            )
        ]

    async def execute(self, task: Task) -> TaskOutput:
        """Execute task."""
        action = task.input.data.get("action", "generate")

        try:
            if action == "generate":
                config = ImageGenerationConfig(**task.input.data)
                result = await self.generate_image(config)
                return TaskOutput(
                    result=result.model_dump(),
                    metadata={"provider": result.metadata.get("provider")}
                )
            elif action == "stats":
                return TaskOutput(result=self.stats)
            else:
                raise ValueError(f"Unknown action: {action}")

        except Exception as e:
            return TaskOutput(
                result={"error": str(e)},
                metadata={"status": "failed"}
            )

    async def generate_image(self, config: ImageGenerationConfig) -> ImageResult:
        """Generate image with caching and provider fallback."""
        self.stats['total_requests'] += 1

        # Check cache
        size = f"{config.width}x{config.height}"
        cache_key = self.cache.get_cache_key(config.prompt, config.style, size)
        cached = self.cache.get(cache_key)

        if cached:
            self.stats['cache_hits'] += 1
            return ImageResult(**cached)

        await self.rate_limiter.acquire()

        last_error = None
        for provider in self.providers:
            try:
                logger.info(f"Generating image with {provider.value}...")

                if provider == ImageProvider.GOOGLE_PRO:
                    result = await self._generate_google_pro(config)
                elif provider == ImageProvider.GOOGLE:
                    result = await self._generate_google(config)
                elif provider == ImageProvider.HUGGINGFACE:
                    result = await self._generate_huggingface(config)
                elif provider == ImageProvider.OPENAI:
                    result = await self._generate_openai(config)
                else:
                    continue

                # Success
                self.stats['by_provider'][provider.value] += 1
                self.cache.set(cache_key, result.model_dump())
                return result

            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider.value} failed: {e}")
                continue

        self.stats['errors'] += 1
        raise Exception(f"All providers failed. Last error: {last_error}")

    # ... PROVIDER IMPLEMENTATIONS ...

    async def _generate_google_pro(self, config: ImageGenerationConfig) -> ImageResult:
        """Generate with NanoBanana Pro (nano-banana-pro-preview) - Most Powerful."""
        if not self.google_key:
            raise ValueError("GOOGLE_API_KEY not configured")

        start_time = time.time()
        enhanced_prompt = self._enhance_prompt(
            config.prompt,
            config.style,
            config.content_type,
            config.sector,
            config.overlay_position
        )

        # NanoBanana Pro - The most powerful image generation model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/nano-banana-pro-preview:generateContent?key={self.google_key}"

        payload = {
            "contents": [{"parts": [{"text": f"Generate a high-quality image: {enhanced_prompt}"}]}],
            "generationConfig": {
                "temperature": 1.0,
                "topP": 0.95,
                "topK": 40,
                "candidateCount": 1
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"Google Pro API error: {response.status} - {text}")

                data = await response.json()
                image_data = self._extract_google_image(data)

                if config.apply_branding:
                    image_data = self.branding.apply_branding(image_data)

                filename = self._save_image(image_data, "gemini_pro", config.prompt)

                return ImageResult(
                    image_url=self._get_image_url(filename),
                    image_id=filename.split('.')[0],
                    prompt_used=enhanced_prompt,
                    generation_time=time.time() - start_time,
                    metadata={"provider": "nanobanana_pro", "model": "nano-banana-pro-preview", "cost": "HIGH_QUALITY"}
                )

    async def _generate_google(self, config: ImageGenerationConfig) -> ImageResult:
        """Generate with Google Gemini 2.5."""
        if not self.google_key:
            raise ValueError("GOOGLE_API_KEY not configured")

        start_time = time.time()
        enhanced_prompt = self._enhance_prompt(
            config.prompt,
            config.style,
            config.content_type,
            config.sector,
            config.overlay_position
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={self.google_key}"

        payload = {
            "contents": [{"parts": [{"text": f"Generate an image: {enhanced_prompt}"}]}],
            "generationConfig": {"temperature": 1.0, "topP": 0.95, "topK": 40}
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"Google API error: {response.status} - {text}")

                data = await response.json()
                image_data = self._extract_google_image(data)

                if config.apply_branding:
                    image_data = self.branding.apply_branding(image_data)

                filename = self._save_image(image_data, "gemini", config.prompt)

                return ImageResult(
                    image_url=self._get_image_url(filename),
                    image_id=filename.split('.')[0],
                    prompt_used=enhanced_prompt,
                    generation_time=time.time() - start_time,
                    metadata={"provider": "google", "model": "gemini-2.5-flash-image", "cost": "FREE"}
                )

    async def _generate_huggingface(self, config: ImageGenerationConfig) -> ImageResult:
        """Generate with Hugging Face."""
        if not self.hf_key:
            raise ValueError("HUGGINGFACE_API_KEY not configured")

        start_time = time.time()
        enhanced_prompt = self._enhance_prompt(
            config.prompt,
            config.style,
            config.content_type,
            config.sector
        )

        url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {"Authorization": f"Bearer {self.hf_key}"}
        payload = {"inputs": enhanced_prompt}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"HF API error: {response.status}")

                image_data = await response.read()

                if config.apply_branding:
                    image_data = self.branding.apply_branding(image_data)

                filename = self._save_image(image_data, "hf", config.prompt)

                return ImageResult(
                    image_url=self._get_image_url(filename),
                    image_id=filename.split('.')[0],
                    prompt_used=enhanced_prompt,
                    generation_time=time.time() - start_time,
                    metadata={"provider": "huggingface", "model": "sdxl", "cost": "FREE"}
                )

    async def _generate_openai(self, config: ImageGenerationConfig) -> ImageResult:
        """Generate with OpenAI."""
        if not self.openai_client:
            raise ValueError("OPENAI_API_KEY not configured")

        start_time = time.time()
        enhanced_prompt = self._enhance_prompt(
            config.prompt,
            config.style,
            config.content_type,
            config.sector
        )

        response = await self.openai_client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        # If branding requested, download and process
        if config.apply_branding:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(response.data[0].url) as resp:
                        if resp.status == 200:
                            image_data = await resp.read()
                            image_data = self.branding.apply_branding(image_data)
                            filename = self._save_image(image_data, "dalle", config.prompt)

                            return ImageResult(
                                image_url=self._get_image_url(filename),
                                image_id=filename.split('.')[0],
                                prompt_used=response.data[0].revised_prompt or enhanced_prompt,
                                generation_time=time.time() - start_time,
                                metadata={"provider": "openai", "model": "dall-e-3", "cost": 0.04, "branded": True}
                            )
            except Exception as e:
                logger.warning(f"Failed to brand OpenAI image: {e}")
                # Fallback to original URL
                pass

        return ImageResult(
            image_url=response.data[0].url,
            image_id=f"dalle_{int(time.time())}",
            prompt_used=response.data[0].revised_prompt or enhanced_prompt,
            generation_time=time.time() - start_time,
            metadata={"provider": "openai", "model": "dall-e-3", "cost": 0.04}
        )

    async def generate_ab_variants(self, config: ImageGenerationConfig) -> List[ImageResult]:
        """
        Generate A/B test variants for a single prompt.
        Creates 3 variants with slight stylistic differences to test engagement.
        """
        variants = []
        base_prompt = config.prompt
        
        # Define variant strategies
        strategies = [
            {"suffix": "close up shot, detailed texture, focused", "style_mod": "macro"},
            {"suffix": "wide angle, environmental context, cinematic lighting", "style_mod": "cinematic"},
            {"suffix": "high contrast, dramatic shadows, bold", "style_mod": "dramatic"}
        ]
        
        tasks = []
        for i, strategy in enumerate(strategies):
            # Create modified config for this variant
            variant_config = config.model_copy()
            variant_config.prompt = f"{base_prompt}, {strategy['suffix']}"
            
            # Use gather for parallel generation if supported (Google/OpenAI handle concurrency limits)
            # For robustness, we'll run sequential in this step or gather if we trust rate limits
            tasks.append(self.generate_image(variant_config))
            
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for res in results:
            if isinstance(res, ImageResult):
                valid_results.append(res)
            else:
                logger.warning(f"Variant generation failed: {res}")
                
        return valid_results

    async def generate_batch(
        self, 
        configs: List[ImageGenerationConfig], 
        consistency_seed: int = None
    ) -> List[ImageResult]:
        """
        Generate multiple images in parallel.
        output order matches input configs order.
        """
        tasks = []
        for config in configs:
            # Inject seed into metadata or config if model supports it
            # For NanoBanana Pro (Gemini), we rely on prompt consistency mostly
            tasks.append(self.generate_image(config))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_results = []
        for i, res in enumerate(results):
            if isinstance(res, ImageResult):
                final_results.append(res)
            else:
                logger.error(f"Batch generation failed for item {i}: {res}")
                final_results.append(None) # Keep index alignment
                
        return final_results

    def _extract_google_image(self, data: Dict) -> bytes:
        """Extract base64 image from Google response."""
        try:
            candidates = data.get("candidates", [])
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                if "inlineData" in part:
                    return base64.b64decode(part["inlineData"]["data"])
            raise Exception("No image found in response")
        except Exception as e:
            raise Exception(f"Failed to parse Google response: {e}")

    def _save_image(self, data: bytes, prefix: str, prompt: str) -> str:
        """Save image data to disk and return filename."""
        # Note: In production, this should upload to S3/GCS
        # For now, we assume a shared volume or local serving

        # Ensure directory exists
        save_dir = Path("media/generated")
        save_dir.mkdir(parents=True, exist_ok=True)

        hash_id = hashlib.md5(prompt.encode()).hexdigest()[:8]
        filename = f"{prefix}_{int(time.time())}_{hash_id}.png"
        file_path = save_dir / filename

        with open(file_path, 'wb') as f:
            f.write(data)

        return filename

    def _get_image_url(self, filename: str) -> str:
        """Get full URL for saved image."""
        base_url = os.getenv('BASE_URL', 'http://localhost:8002')
        return f"{base_url}/media/generated/{filename}"

    def _enhance_prompt(
        self,
        prompt: str,
        style: str,
        content_type: str = "social_post",
        sector: str = None,
        overlay_position: str = None
    ) -> str:
        """
        Enhance prompt with Brand DNA style guidelines and text overlay support.

        Args:
            prompt: Base image description
            style: Style preset (professional, creative, minimal, elegant, tech)
            content_type: Type of content (social_post, story, thumbnail, cover, product)
            sector: Optional sector for industry-specific styling
            overlay_position: Optional position for text overlay negative space
            
        Returns:
            Enhanced prompt with StudioCentOS brand guidelines
        """
        # Append instruction for text overlay if requested
        overlay_instruction = ""
        if overlay_position:
            overlay_instruction = self._get_overlay_instruction(overlay_position)
            if overlay_instruction:
                prompt = f"{prompt}. {overlay_instruction}"

        # Use Brand DNA enhanced prompt generator
        return get_brand_image_prompt(
            base_prompt=prompt,
            style=style,
            content_type=content_type,
            sector=sector
        )

    def _get_overlay_instruction(self, position: str) -> str:
        """Get prompt instruction for negative space/padding."""
        instructions = {
            "top": "Leave the top 30% of the image empty/solid color for text overlay. Composition focused on bottom.",
            "bottom": "Leave the bottom 30% of the image empty/solid color for text overlay. Composition focused on top.",
            "left": "Leave the left third of the image empty for text. Composition weighted to the right.",
            "right": "Leave the right third of the image empty for text. Composition weighted to the left.",
            "center": "Leave the center empty for text context. Frame the subject around the edges.",
            "none": ""
        }
        return instructions.get(position.lower(), "")

    async def generate_ab_variants(
        self, config: ImageGenerationConfig, num_variants: int = 3
    ) -> List[ImageResult]:
        """
        Generate multiple image variants for A/B testing.
        
        Creates variations using different style presets to allow
        testing which visual style performs better.
        
        Args:
            config: Base image configuration
            num_variants: Number of variants to generate (default 3)
        
        Returns:
            List of ImageResult objects with variant metadata
        """
        variants = []
        style_variants = ["professional", "elegant", "dark_luxury", "tech", "minimal"]
        
        for i, style in enumerate(style_variants[:num_variants]):
            try:
                # Create new config with variant style
                variant_config = ImageGenerationConfig(
                    prompt=config.prompt,
                    style=style,
                    content_type=config.content_type,
                    sector=config.sector,
                    width=config.width,
                    height=config.height,
                    quality=config.quality,
                    apply_branding=config.apply_branding,
                )
                
                result = await self.generate_image(variant_config)
                result.metadata["variant_number"] = i + 1
                result.metadata["style_variant"] = style
                result.metadata["is_ab_variant"] = True
                variants.append(result)
                
                logger.info(f"Generated A/B variant {i+1}/{num_variants}: style={style}")
                
            except Exception as e:
                logger.warning(f"Failed to generate variant {i+1} ({style}): {e}")
                continue
        
        return variants

    async def generate_for_platform(
        self, prompt: str, platform: str, content_type: str = "post", **kwargs
    ) -> ImageResult:
        """
        Generate image with auto-detected dimensions for a specific platform.
        
        Args:
            prompt: Image description
            platform: Target platform (instagram, linkedin, facebook, etc.)
            content_type: Type of content (post, story, reel, thumbnail, etc.)
            **kwargs: Additional config options (style, sector, apply_branding, etc.)
        
        Returns:
            ImageResult with correct platform dimensions
        """
        # Get platform-specific dimensions
        dimensions = get_platform_dimensions(platform, content_type)
        
        config = ImageGenerationConfig(
            prompt=prompt,
            width=dimensions["width"],
            height=dimensions["height"],
            style=kwargs.get("style", "professional"),
            content_type=content_type,
            sector=kwargs.get("sector"),
            apply_branding=kwargs.get("apply_branding", True),
        )
        
        result = await self.generate_image(config)
        result.metadata["platform"] = platform
        result.metadata["content_type"] = content_type
        result.metadata["dimensions"] = dimensions
        
        return result

