"""
Image Generation Provider Helpers
Modular provider implementations for generate_image endpoint.
"""

import base64
import hashlib
import logging
import os
import time
import urllib.parse
from pathlib import Path

import aiohttp

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS - BRAND DNA SYSTEM
# =============================================================================

# Default Brand Context (used when no custom Brand DNA is provided)
DEFAULT_BRAND_CONTEXT = {
    "company_name": "MARKETTINA",
    "tagline": "Digital Innovation for Italian Business",
    "industry": "Digital Marketing & Software Development",
    "primary_color": "#D4AF37",      # Gold luxury
    "secondary_color": "#0A0A0A",    # Deep black
    "accent_color": "#FAFAFA",       # Pure white
    "style": "Modern, Professional, Tech-Forward, Italian Excellence, Premium Luxury",
    "avoid_colors": ["blue", "navy", "cyan"],  # Brand-specific restrictions
    "visual_elements": ["gold highlights", "dark elegant backgrounds", "premium feel", "clean lines"],
}

# Style Modifiers with expanded options
STYLE_MODIFIERS = {
    "professional": {
        "prompt": "professional corporate photography, high quality, 8k resolution, clean studio lighting, sharp focus, premium luxury aesthetic, sophisticated",
        "mood": "trustworthy, authoritative, competent",
    },
    "creative": {
        "prompt": "artistic composition, creative digital art, imaginative visual storytelling, dynamic composition, tech-inspired futurism",
        "mood": "innovative, inspiring, bold",
    },
    "minimalist": {
        "prompt": "minimalist design, clean lines, simple composition, flat design, elegant negative space, sophisticated simplicity",
        "mood": "clean, focused, modern",
    },
    "modern": {
        "prompt": "modern aesthetic, sleek design, contemporary style, cutting-edge visual, forward-thinking",
        "mood": "trendy, fresh, progressive",
    },
    "inspirational": {
        "prompt": "aspirational imagery, uplifting atmosphere, success visualization, motivating visual elements, dreamy quality",
        "mood": "empowering, optimistic, visionary",
    },
    "educational": {
        "prompt": "infographic style, clear hierarchy, knowledge visualization, instructional design, information architecture",
        "mood": "helpful, informative, clear",
    },
    "premium": {
        "prompt": "luxury brand photography, high-end aesthetic, exclusive feel, magazine quality, editorial style, sophisticated lighting",
        "mood": "exclusive, luxurious, prestigious",
    },
    "tech": {
        "prompt": "futuristic technology visualization, digital innovation, AI and data patterns, circuit aesthetics, neon accents on dark",
        "mood": "cutting-edge, innovative, advanced",
    },
    "friendly": {
        "prompt": "warm and approachable, inviting atmosphere, human connection, authentic moments, relatable scenes",
        "mood": "welcoming, accessible, personable",
    },
    "urgent": {
        "prompt": "bold and impactful, attention-grabbing design, dynamic energy, action-oriented composition, high contrast",
        "mood": "exciting, time-sensitive, compelling",
    },
}

# Platform-specific aspect ratios and dimensions
ASPECT_DIMENSIONS = {
    "1:1": (1024, 1024),      # Instagram post, Facebook, Threads
    "4:5": (1024, 1280),      # Instagram portrait (optimal)
    "9:16": (576, 1024),      # Stories, Reels, TikTok
    "16:9": (1024, 576),      # YouTube, Twitter, LinkedIn
    "1.91:1": (1024, 536),    # Facebook link preview, LinkedIn
    "2:3": (682, 1024),       # Pinterest
    "4:3": (1024, 768),       # Google Business
    "3:4": (768, 1024),       # Alternative portrait
    "21:9": (1024, 439),      # Ultrawide banner
}

# Platform to optimal aspect ratio mapping
PLATFORM_ASPECT_RATIOS = {
    "instagram": "1:1",
    "instagram_story": "9:16",
    "instagram_reel": "9:16",
    "instagram_carousel": "4:5",
    "facebook": "1.91:1",
    "facebook_story": "9:16",
    "linkedin": "1.91:1",
    "twitter": "16:9",
    "tiktok": "9:16",
    "youtube": "16:9",
    "youtube_short": "9:16",
    "threads": "1:1",
    "pinterest": "2:3",
    "google_business": "4:3",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_aspect_ratio_for_platform(platform: str) -> str:
    """Get optimal aspect ratio for a platform."""
    return PLATFORM_ASPECT_RATIOS.get(platform, "1:1")


def build_enhanced_prompt(
    prompt: str,
    style: str = "professional",
    brand_dna: dict | None = None,
    platform: str = "default",
    template_type: str | None = None
) -> str:
    """
    Build enhanced prompt with brand context, style modifiers, and platform optimization.

    Args:
        prompt: User's base prompt
        style: Visual style (professional, creative, minimalist, etc.)
        brand_dna: Custom brand DNA with colors, style, etc.
        platform: Target platform for optimization
        template_type: Post template type (lancio, tip, case-study, etc.)

    Returns:
        Enhanced prompt optimized for high-quality generation
    """
    # Merge brand DNA with defaults
    brand = {**DEFAULT_BRAND_CONTEXT, **(brand_dna or {})}

    # Get style modifier
    style_config = STYLE_MODIFIERS.get(style, STYLE_MODIFIERS["professional"])
    style_prompt = style_config["prompt"] if isinstance(style_config, dict) else style_config
    style_mood = style_config.get("mood", "professional") if isinstance(style_config, dict) else "professional"

    # Build color instructions
    color_instructions = f"""
Color Palette (USE THESE COLORS):
- Primary: {brand.get('primary_color', '#D4AF37')} (for key elements, highlights, CTAs)
- Secondary: {brand.get('secondary_color', '#0A0A0A')} (for backgrounds, depth)
- Accent: {brand.get('accent_color', '#FAFAFA')} (for contrast, text areas)
AVOID these colors: {', '.join(brand.get('avoid_colors', ['blue', 'navy']))}
"""

    # Template-specific enhancements
    template_enhancements = {
        "lancio": "product launch visualization, spotlight effect, unveiling moment, excitement, new and fresh feeling",
        "tip": "educational infographic style, lightbulb concept, clear and helpful, knowledge sharing",
        "case-study": "success visualization, growth charts, achievement symbols, trust-building, data-driven",
        "promo": "promotional sale design, urgency elements, attention-grabbing, valuable offer feeling",
        "educational": "informative design, clear hierarchy, knowledge visualization, structured learning",
        "behind-scenes": "authentic workspace, real moments, team culture, candid but curated",
        "engagement": "interactive design, poll/vote visual, community feeling, fun and inclusive",
        "announcement": "news bulletin style, important update, professional announcement, credible",
        "testimonial": "quote design, trust symbols, customer success, authentic review style",
        "comparison": "split screen comparison, before/after, clear contrast, decision-making visual",
    }

    template_addition = template_enhancements.get(template_type, "") if template_type else ""

    # Platform-specific notes
    platform_notes = {
        "instagram": "Instagram-optimized: vibrant but refined, scroll-stopping, feed-worthy",
        "linkedin": "LinkedIn-optimized: professional, corporate-friendly, business-appropriate",
        "facebook": "Facebook-optimized: shareable, engaging, community-friendly",
        "twitter": "Twitter-optimized: bold, impactful, works at small size too",
        "tiktok": "TikTok-optimized: trendy, youthful energy, vertical-first thinking",
        "youtube": "YouTube-optimized: thumbnail-worthy, high contrast, click-worthy",
        "pinterest": "Pinterest-optimized: aspirational, save-worthy, text-on-image friendly",
    }

    platform_note = platform_notes.get(platform.split("_")[0], "")

    # Build final enhanced prompt
    enhanced = f"""
Create a premium marketing visual for {brand.get('company_name', 'MARKETTINA')}.

SUBJECT: {prompt}

BRAND IDENTITY:
- Company: {brand.get('company_name', 'MARKETTINA')}
- Industry: {brand.get('industry', 'Digital Marketing & Tech')}
- Style: {brand.get('style', 'Modern, Professional, Premium')}

{color_instructions}

VISUAL STYLE:
{style_prompt}
Mood: {style_mood}
{template_addition}

{platform_note}

TECHNICAL REQUIREMENTS:
- Ultra-high resolution, 8K quality, sharp details
- Professional lighting, subtle gradients
- Clean composition with clear focal point
- No text, logos, or watermarks in the image
- No generic stock photo aesthetics
- Avoid: cluttered designs, low contrast, cliché imagery, deformed elements

FINAL OUTPUT:
A scroll-stopping, memorable, share-worthy image that:
1. Represents "{prompt}" visually
2. Uses the brand color palette
3. Feels {style_mood}
4. Is perfect for professional marketing use
""".strip()

    return enhanced


async def save_generated_image(
    image_bytes: bytes,
    provider: str,
    model: str,
    prompt: str,
    enhanced_prompt: str,
    start_time: float,
    aspect_ratio: str,
    style: str,
    apply_branding: bool = True,
    platform: str = "default"
) -> dict:
    """Save image and return response data."""
    # Apply branding if enabled
    if apply_branding:
        try:
            from app.domain.marketing.image_branding import image_branding
            image_bytes = image_branding.apply_branding(
                image_bytes,
                platform=platform,
                footer_text="MARKETTINA"
            )
            logger.info("branding_applied", platform=platform, provider=provider)
        except Exception as e:
            logger.warning("branding_failed", error=str(e))

    # Save image
    save_dir = Path("/app/media/generated")
    save_dir.mkdir(parents=True, exist_ok=True)

    hash_id = hashlib.md5(prompt.encode()).hexdigest()[:8]
    filename = f"{provider}_{int(time.time())}_{hash_id}.png"
    file_path = save_dir / filename

    with open(file_path, "wb") as f:
        f.write(image_bytes)

    base_url = os.getenv("BASE_URL", "https://markettina.it")

    return {
        "image_url": f"{base_url}/ai/media/generated/{filename}",
        "prompt_used": enhanced_prompt,
        "generation_time": time.time() - start_time,
        "metadata": {
            "provider": provider,
            "model": model,
            "cost": "FREE",
            "branded": apply_branding,
            "aspect_ratio": aspect_ratio,
            "style": style
        }
    }


# =============================================================================
# PROVIDER: IMAGEN 4 ULTRA (Google - Best Quality)
# =============================================================================

async def try_imagen4_ultra(
    google_key: str,
    enhanced_prompt: str,
    aspect_ratio: str
) -> bytes | None:
    """Try Google Imagen 4 Ultra for image generation."""
    try:
        logger.info("provider_imagen4ultra_trying")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-ultra-generate-001:predict?key={google_key}"

        aspect_map = {"1:1": "1:1", "16:9": "16:9", "9:16": "9:16", "4:3": "4:3", "3:4": "3:4"}

        payload = {
            "instances": [{"prompt": enhanced_prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": aspect_map.get(aspect_ratio, "1:1"),
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
                        logger.info("provider_imagen4ultra_success", size_kb=len(image_bytes)//1024)
                        return image_bytes
                else:
                    error_text = await response.text()
                    logger.warning("provider_imagen4ultra_failed", status=response.status, error=error_text[:150])
    except Exception as e:
        logger.warning("provider_imagen4ultra_error", error=str(e))

    return None


# =============================================================================
# PROVIDER: POLLINATIONS (Free, Unlimited)
# =============================================================================

async def try_pollinations(
    prompt: str,
    aspect_ratio: str
) -> bytes | None:
    """Try Pollinations.ai for free unlimited image generation."""
    try:
        width, height = ASPECT_DIMENSIONS.get(aspect_ratio, (1024, 1024))

        # Create SHORT prompt for Pollinations (URL length limit!)
        short_prompt = f"{prompt}, professional marketing, gold and black colors, dark elegant theme, premium luxury, high quality, 8k"
        if len(short_prompt) > 300:
            short_prompt = short_prompt[:297] + "..."

        encoded_prompt = urllib.parse.quote(short_prompt)

        pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={int(time.time())}&nologo=true&model=flux"

        logger.info("provider_pollinations_trying", prompt_length=len(short_prompt))

        async with aiohttp.ClientSession() as session:
            async with session.get(pollinations_url, timeout=aiohttp.ClientTimeout(total=90)) as response:
                if response.status == 200:
                    content_type = response.headers.get("Content-Type", "")
                    if "image" in content_type:
                        image_bytes = await response.read()
                        logger.info("provider_pollinations_success", size=len(image_bytes))
                        return image_bytes
                    logger.warning("pollinations_not_image", content_type=content_type)
                else:
                    logger.warning("pollinations_error", status=response.status)
    except Exception as e:
        logger.warning("pollinations_error", error=str(e))

    return None


# =============================================================================
# PROVIDER: HUGGINGFACE FLUX (Via Router)
# =============================================================================

async def try_huggingface_flux(
    hf_token: str,
    enhanced_prompt: str,
    aspect_ratio: str
) -> bytes | None:
    """Try HuggingFace FLUX via router for image generation."""
    try:
        url = "https://router.huggingface.co/novita-ai/flux/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }

        height = 1024 if aspect_ratio == "1:1" else (576 if aspect_ratio == "16:9" else 1024)

        payload = {
            "prompt": enhanced_prompt,
            "model": "flux/dev",
            "width": 1024,
            "height": height,
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
                            logger.info("provider_hf_flux_success", size=len(image_bytes))
                            return image_bytes
                else:
                    error_text = await response.text()
                    logger.warning("hf_flux_error", status=response.status, error=error_text[:150])
    except Exception as e:
        logger.warning("hf_flux_error", error=str(e))

    return None


# =============================================================================
# PROVIDER: NANO BANANA PRO (Gemini 3 Pro Image Preview)
# IL PIÙ POTENTE - Usato come default per tutto il marketing!
# =============================================================================

async def try_nano_banana_pro(
    google_key: str,
    enhanced_prompt: str,
    aspect_ratio: str = "1:1",
    image_size: str = "2048",
    use_grounding: bool = False,
    use_thinking: bool = True
) -> bytes | None:
    """
    Try Nano Banana Pro (Gemini 3 Pro Image Preview) for premium image generation.

    🚀 NANO BANANA PRO = GEMINI 3 PRO IMAGE PREVIEW
    Usa la stessa GOOGLE_API_KEY - già configurata!

    CARATTERISTICHE PREMIUM:
    - 4K resolution (fino a 4096px)
    - Fino a 14 reference images per style consistency
    - Google Search grounding per eventi attuali
    - THINKING PROCESS per prompt complessi
    - Character consistency tra immagini multiple
    - Qualità superiore e aderenza al prompt

    IDEALE PER:
    - Post Instagram/Facebook (3 al giorno)
    - Stories (qualche al giorno)
    - Contenuti marketing di alta qualità

    Model: gemini-3-pro-image-preview
    """
    try:
        logger.info(
            "provider_nano_banana_pro_trying",
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            use_thinking=use_thinking
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key={google_key}"

        # Configure image generation - MASSIMA QUALITÀ
        image_config = {
            "aspectRatio": aspect_ratio,
            "imageSize": image_size  # Default: 2048px per alta qualità
        }

        # Build payload with Gemini 3 Pro Image format
        generation_config = {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": image_config
        }

        # Abilita THINKING PROCESS per prompt complessi (migliora qualità)
        if use_thinking:
            generation_config["thinkingConfig"] = {
                "thinkingBudget": 1024  # Token per il processo di "pensiero"
            }

        payload = {
            "contents": [{
                "parts": [{
                    "text": f"""Create a stunning, high-quality professional marketing image.

REQUIREMENTS:
{enhanced_prompt}

QUALITY STANDARDS:
- Ultra high resolution, sharp details
- Professional lighting and composition
- Rich, vibrant colors
- Clean, polished aesthetic
- Suitable for social media marketing"""
                }]
            }],
            "generationConfig": generation_config
        }

        # Add Google Search grounding for current events/trends
        if use_grounding:
            payload["tools"] = [{"googleSearch": {}}]

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=180)  # Longer for higher quality
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for part in parts:
                            if "inlineData" in part:
                                image_bytes = base64.b64decode(part["inlineData"]["data"])
                                logger.info(
                                    "provider_nano_banana_pro_success",
                                    size_kb=len(image_bytes)//1024,
                                    aspect_ratio=aspect_ratio
                                )
                                return image_bytes
                else:
                    error_text = await response.text()
                    logger.warning(
                        "provider_nano_banana_pro_failed",
                        status=response.status,
                        error=error_text[:200]
                    )
    except Exception as e:
        logger.warning("provider_nano_banana_pro_error", error=str(e))

    return None


# =============================================================================
# PROVIDER: NANO BANANA (Gemini 2.5 Flash Image - Fast)
# =============================================================================

async def try_nano_banana(
    google_key: str,
    enhanced_prompt: str,
    aspect_ratio: str = "1:1"
) -> bytes | None:
    """
    Try Nano Banana (Gemini 2.5 Flash Image) for fast image generation.

    Nano Banana IS Gemini 2.5 Flash Image!
    Uses the same GOOGLE_API_KEY, no separate subscription needed.

    Features:
    - Fast generation (Flash model)
    - Good quality for quick iterations
    - Cost-effective for high volume

    Model: gemini-2.5-flash-image
    """
    try:
        logger.info("provider_nano_banana_trying", aspect_ratio=aspect_ratio)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={google_key}"

        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Generate an image: {enhanced_prompt}"
                }]
            }],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {
                    "aspectRatio": aspect_ratio
                }
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for part in parts:
                            if "inlineData" in part:
                                image_bytes = base64.b64decode(part["inlineData"]["data"])
                                logger.info(
                                    "provider_nano_banana_success",
                                    size_kb=len(image_bytes)//1024
                                )
                                return image_bytes
                else:
                    error_text = await response.text()
                    logger.warning(
                        "provider_nano_banana_failed",
                        status=response.status,
                        error=error_text[:150]
                    )
    except Exception as e:
        logger.warning("provider_nano_banana_error", error=str(e))

    return None


# =============================================================================
# PROVIDER: GOOGLE VEO 3.1 (AI Video Generation)
# =============================================================================

async def try_veo_video_generation(
    google_key: str,
    prompt: str,
    aspect_ratio: str = "16:9",
    duration_seconds: int = 8,
    resolution: str = "720p",
    image_input: bytes | None = None,
    negative_prompt: str | None = None
) -> dict | None:
    """
    Generate video using Google VEO 3.1 via Gemini API.

    VEO 3.1 Features:
    - 8-second 720p or 1080p videos
    - Native audio generation
    - Image-to-video support
    - Video extension up to 148 seconds
    - Reference images for style consistency

    Returns dict with operation_name for polling, or video_url if ready.
    """
    try:
        # VEO is accessed via Gemini API's generate_videos endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-generate-preview:generateVideos"

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": google_key
        }

        config = {
            "aspectRatio": aspect_ratio,
            "resolution": resolution,
            "durationSeconds": str(duration_seconds),
            "numberOfVideos": 1
        }

        if negative_prompt:
            config["negativePrompt"] = negative_prompt

        payload = {
            "prompt": prompt,
            "config": config
        }

        # Add image input for image-to-video
        if image_input:
            image_b64 = base64.b64encode(image_input).decode()
            payload["image"] = {
                "bytesBase64Encoded": image_b64
            }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)  # Initial request is quick
            ) as response:
                if response.status == 200:
                    data = await response.json()

                    # VEO returns a long-running operation
                    operation_name = data.get("name")
                    if operation_name:
                        logger.info("veo_operation_started", operation=operation_name)
                        return {
                            "status": "pending",
                            "operation_name": operation_name,
                            "message": "Video generation started. Poll for completion."
                        }
                else:
                    error_text = await response.text()
                    logger.warning("veo_error", status=response.status, error=error_text[:200])

    except Exception as e:
        logger.warning("veo_error", error=str(e))

    return None


async def poll_veo_operation(
    google_key: str,
    operation_name: str,
    max_polls: int = 36,  # 6 minutes max (36 * 10 seconds)
    poll_interval: int = 10
) -> dict | None:
    """
    Poll VEO operation until video is ready.

    Returns dict with video_url or None if failed/timeout.
    """
    import asyncio

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/{operation_name}"
        headers = {
            "x-goog-api-key": google_key
        }

        for attempt in range(max_polls):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()

                        if data.get("done"):
                            # Operation completed
                            result = data.get("response", {})
                            generated_videos = result.get("generatedVideos", [])

                            if generated_videos:
                                video_info = generated_videos[0]
                                video_file = video_info.get("video", {})

                                return {
                                    "status": "completed",
                                    "video_uri": video_file.get("uri"),
                                    "video_name": video_file.get("name"),
                                    "mime_type": video_file.get("mimeType", "video/mp4")
                                }
                            else:
                                logger.warning("veo_no_videos", data=data)
                                return None
                        else:
                            # Still processing
                            logger.info("veo_polling", attempt=attempt + 1, max=max_polls)
                            await asyncio.sleep(poll_interval)
                    else:
                        error_text = await response.text()
                        logger.warning("veo_poll_error", status=response.status, error=error_text[:150])
                        return None

        logger.warning("veo_timeout", operation=operation_name)
        return None

    except Exception as e:
        logger.warning("veo_poll_error", error=str(e))
        return None


async def download_veo_video(
    google_key: str,
    video_name: str
) -> bytes | None:
    """Download generated video from VEO."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/{video_name}:download"
        headers = {
            "x-goog-api-key": google_key
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    video_bytes = await response.read()
                    logger.info("veo_download_success", size=len(video_bytes))
                    return video_bytes
                else:
                    error_text = await response.text()
                    logger.warning("veo_download_error", status=response.status, error=error_text[:150])

    except Exception as e:
        logger.warning("veo_download_error", error=str(e))

    return None


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

async def generate_image_with_providers(
    prompt: str,
    style: str = "professional",
    aspect_ratio: str = "1:1",
    platform: str = "default",
    apply_branding: bool = True,
    provider: str = "auto",
    brand_dna: dict | None = None,
    template_type: str | None = None
) -> tuple[bytes | None, str, str]:
    """
    Orchestrate image generation across providers with Brand DNA support.

    Args:
        prompt: User's image prompt
        style: Visual style (professional, creative, minimalist, etc.)
        aspect_ratio: Target aspect ratio
        platform: Target social platform
        apply_branding: Whether to apply brand overlay
        provider: Provider preference (auto, premium, free, google, nanobanana, etc.)
        brand_dna: Custom brand DNA dict with colors, company info, etc.
        template_type: Post template type for visual optimization

    Returns:
        (image_bytes, provider_name, model_name) or (None, "", "") if all fail.
    """
    # Auto-detect aspect ratio from platform if not specified
    if aspect_ratio == "auto" or (aspect_ratio == "1:1" and platform != "default"):
        aspect_ratio = get_aspect_ratio_for_platform(platform)

    # Build enhanced prompt with Brand DNA
    enhanced_prompt = build_enhanced_prompt(
        prompt=prompt,
        style=style,
        brand_dna=brand_dna,
        platform=platform,
        template_type=template_type
    )

    logger.info(
        "image_generation_start",
        style=style,
        platform=platform,
        aspect_ratio=aspect_ratio,
        has_brand_dna=bool(brand_dna),
        template_type=template_type
    )

    # Detect available API keys
    # NANO BANANA PRO = Gemini 3 Pro Image Preview (IL PIÙ POTENTE!)
    # Usa la stessa GOOGLE_API_KEY - già configurata!
    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")
    hf_token = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")

    has_google = bool(google_key)
    has_hf = bool(hf_token)
    force_free = provider == "free"

    # =========================================================================
    # PRIORITÀ ASSOLUTA: GEMINI 3 PRO IMAGE (NANO BANANA PRO)
    # Per 3 foto + stories al giorno, usiamo SEMPRE il più potente!
    # =========================================================================

    # TIER 0: Nano Banana Pro (Gemini 3 Pro Image) - DEFAULT PER TUTTO
    # 4K, 14 reference images, thinking process, character consistency
    if has_google and not force_free:
        logger.info("using_nano_banana_pro", reason="best_quality_for_marketing")
        image_bytes = await try_nano_banana_pro(
            google_key,
            enhanced_prompt,
            aspect_ratio,
            image_size="2048"  # Alta qualità per marketing
        )
        if image_bytes:
            return image_bytes, "nano-banana-pro", "gemini-3-pro-image-preview"

    # FALLBACK 1: Imagen 4 Ultra (se Gemini 3 non disponibile)
    if has_google and not force_free:
        image_bytes = await try_imagen4_ultra(google_key, enhanced_prompt, aspect_ratio)
        if image_bytes:
            return image_bytes, "imagen4-ultra", "imagen-4.0-ultra-generate-001"

    # FALLBACK 2: Nano Banana (Gemini 2.5 Flash - veloce ma meno potente)
    if has_google and not force_free:
        image_bytes = await try_nano_banana(google_key, enhanced_prompt, aspect_ratio)
        if image_bytes:
            return image_bytes, "nano-banana", "gemini-2.5-flash-image"

    # FALLBACK 3: HuggingFace FLUX
    if has_hf and provider in ["auto", "huggingface"]:
        image_bytes = await try_huggingface_flux(hf_token, enhanced_prompt, aspect_ratio)
        if image_bytes:
            return image_bytes, "flux", "flux-dev"

    # FALLBACK 4: Pollinations (Free - ultima risorsa)
    if provider in ["auto", "free", "pollinations"] or not has_google:
        image_bytes = await try_pollinations(prompt, aspect_ratio)
        if image_bytes:
            return image_bytes, "pollinations", "flux"

    return None, "", ""


# =============================================================================
# VIDEO GENERATION ORCHESTRATOR (VEO)
# =============================================================================

async def generate_video_with_veo(
    prompt: str,
    style: str = "professional",
    aspect_ratio: str = "16:9",
    duration_seconds: int = 8,
    resolution: str = "720p",
    platform: str = "default",
    brand_dna: dict | None = None,
    image_input: bytes | None = None,
    negative_prompt: str | None = None,
    wait_for_completion: bool = True
) -> dict | None:
    """
    Generate video using Google VEO 3.1.

    Args:
        prompt: Video description/prompt
        style: Visual style
        aspect_ratio: "16:9" or "9:16"
        duration_seconds: 4, 6, or 8 seconds
        resolution: "720p" or "1080p"
        platform: Target platform for optimization
        brand_dna: Brand context for prompt enhancement
        image_input: Optional starting frame image
        negative_prompt: What to avoid in video
        wait_for_completion: If True, polls until video ready

    Returns:
        Dict with video info or None if failed
    """
    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")

    if not google_key:
        logger.warning("veo_no_api_key")
        return None

    # Build enhanced prompt for video
    enhanced_prompt = build_enhanced_prompt(
        prompt=prompt,
        style=style,
        brand_dna=brand_dna,
        platform=platform
    )

    # Adjust aspect ratio for video platforms
    video_aspect_map = {
        "tiktok": "9:16",
        "youtube_short": "9:16",
        "instagram_reel": "9:16",
        "instagram_story": "9:16",
        "youtube": "16:9",
        "facebook": "16:9",
        "linkedin": "16:9",
    }

    if platform in video_aspect_map:
        aspect_ratio = video_aspect_map[platform]

    # Start video generation
    result = await try_veo_video_generation(
        google_key=google_key,
        prompt=enhanced_prompt,
        aspect_ratio=aspect_ratio,
        duration_seconds=duration_seconds,
        resolution=resolution,
        image_input=image_input,
        negative_prompt=negative_prompt
    )

    if not result:
        return None

    if not wait_for_completion:
        return result

    # Poll for completion
    operation_name = result.get("operation_name")
    if operation_name:
        completion = await poll_veo_operation(google_key, operation_name)

        if completion and completion.get("status") == "completed":
            # Download the video
            video_name = completion.get("video_name")
            if video_name:
                video_bytes = await download_veo_video(google_key, video_name)
                if video_bytes:
                    # Save video
                    save_dir = Path("/app/media/generated/videos")
                    save_dir.mkdir(parents=True, exist_ok=True)

                    filename = f"veo_{int(time.time())}_{hashlib.md5(prompt.encode()).hexdigest()[:8]}.mp4"
                    file_path = save_dir / filename

                    with open(file_path, "wb") as f:
                        f.write(video_bytes)

                    return {
                        "status": "completed",
                        "video_url": f"/media/generated/videos/{filename}",
                        "video_path": str(file_path),
                        "provider": "veo-3.1",
                        "duration": duration_seconds,
                        "resolution": resolution,
                        "aspect_ratio": aspect_ratio
                    }

        return completion

    return result
