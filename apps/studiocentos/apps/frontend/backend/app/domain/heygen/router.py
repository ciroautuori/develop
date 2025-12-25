"""
HeyGen API Integration Router
AI Avatar Video Generation for Marketing Hub

API Reference: https://docs.heygen.com/reference
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import httpx
import os
import json
import structlog
from app.core.api.dependencies.auth_deps import get_current_admin_user

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/admin/heygen", tags=["HeyGen Integration"])

# HeyGen API Configuration
HEYGEN_API_URL = "https://api.heygen.com"
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY", "")


def get_heygen_headers():
    """Get headers for HeyGen API requests."""
    if not HEYGEN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="HeyGen API key not configured. Please add HEYGEN_API_KEY to environment variables."
        )
    return {
        "X-Api-Key": HEYGEN_API_KEY,
        "Content-Type": "application/json"
    }


# ============ REQUEST/RESPONSE MODELS ============

class VideoGenerateRequest(BaseModel):
    title: str = Field(..., description="Video title")
    script: str = Field(..., max_length=5000, description="Script text (max 5000 chars)")
    avatar_id: str = Field(..., description="Selected avatar ID")
    voice_id: str = Field(..., description="Selected voice ID")
    platform: str = Field(default="instagram_story", description="Target platform")
    background_type: str = Field(default="color", description="Background type: color, image, gradient")
    background_value: str = Field(default="#0a0a0a", description="Background value (hex color or URL)")
    voice_speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Voice speed 0.5-2.0")
    voice_pitch: int = Field(default=0, ge=-50, le=50, description="Voice pitch -50 to 50")
    avatar_style: str = Field(default="normal", description="Avatar style: normal, circle, closeUp")


class ScriptGenerateRequest(BaseModel):
    topic: str = Field(..., description="Script topic")
    tone: str = Field(default="professional", description="Tone: professional, casual, enthusiastic, educational")
    duration: str = Field(default="short", description="Duration: short, medium, long")
    language: str = Field(default="it", description="Language code")


# Platform dimensions mapping
PLATFORM_DIMENSIONS = {
    "instagram_story": {"width": 1080, "height": 1920},
    "tiktok": {"width": 1080, "height": 1920},
    "youtube_shorts": {"width": 1080, "height": 1920},
    "facebook_story": {"width": 1080, "height": 1920},
    "linkedin": {"width": 1920, "height": 1080},
}


# ============ AVATAR ENDPOINTS ============

@router.get("/avatars")
async def list_avatars(current_user = Depends(get_current_admin_user)):
    """
    Get list of available HeyGen avatars.
    Includes public, private, and instant avatars.
    """
    try:
        headers = get_heygen_headers()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEYGEN_API_URL}/v2/avatars",
                headers=headers
            )

            if response.status_code != 200:
                logger.error("heygen_list_avatars_failed", status=response.status_code, body=response.text)
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"HeyGen API error: {response.text}"
                )

            data = response.json()
            avatars = []

            # Process avatar groups
            if "data" in data and "avatars" in data["data"]:
                for avatar in data["data"]["avatars"]:
                    avatars.append({
                        "avatar_id": avatar.get("avatar_id"),
                        "avatar_name": avatar.get("avatar_name", "Unknown"),
                        "gender": avatar.get("gender", "other"),
                        "preview_image_url": avatar.get("preview_image_url", ""),
                        "preview_video_url": avatar.get("preview_video_url", ""),
                        "type": avatar.get("type", "public"),
                    })

            logger.info("heygen_avatars_loaded", count=len(avatars))
            return {"avatars": avatars}

    except httpx.HTTPError as e:
        logger.error("heygen_http_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")


# ============ VOICE ENDPOINTS ============

@router.get("/voices")
async def list_voices(
    language: Optional[str] = None,
    current_user = Depends(get_current_admin_user)
):
    """
    Get list of available HeyGen voices.
    Optionally filter by language.
    """
    try:
        headers = get_heygen_headers()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEYGEN_API_URL}/v2/voices",
                headers=headers
            )

            if response.status_code != 200:
                logger.error("heygen_list_voices_failed", status=response.status_code)
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"HeyGen API error: {response.text}"
                )

            data = response.json()
            voices = []

            if "data" in data and "voices" in data["data"]:
                for voice in data["data"]["voices"]:
                    # Filter by language if specified
                    if language and voice.get("language", "").lower() != language.lower():
                        # Check if language is in the name or supported languages
                        voice_lang = voice.get("language", "").lower()
                        if language.lower() not in voice_lang:
                            continue

                    voices.append({
                        "voice_id": voice.get("voice_id"),
                        "name": voice.get("name", "Unknown"),
                        "language": voice.get("language", "en"),
                        "gender": voice.get("gender", "neutral"),
                        "preview_audio": voice.get("preview_audio", ""),
                        "support_pause": voice.get("support_pause", False),
                        "emotion_support": voice.get("emotion_support", False),
                    })

            logger.info("heygen_voices_loaded", count=len(voices), language=language)
            return {"voices": voices}

    except httpx.HTTPError as e:
        logger.error("heygen_http_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")


# ============ VIDEO GENERATION ENDPOINTS ============

@router.post("/video/generate")
async def generate_video(
    request: VideoGenerateRequest,
    current_user = Depends(get_current_admin_user)
):
    """
    Generate an avatar video using HeyGen API.
    Returns video_id for status polling.
    """
    try:
        headers = get_heygen_headers()

        # Get platform dimensions
        dimensions = PLATFORM_DIMENSIONS.get(request.platform, PLATFORM_DIMENSIONS["instagram_story"])

        # Build HeyGen API request
        heygen_request = {
            "title": request.title,
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": request.avatar_id,
                        "avatar_style": request.avatar_style,
                    },
                    "voice": {
                        "type": "text",
                        "input_text": request.script,
                        "voice_id": request.voice_id,
                        "speed": request.voice_speed,
                        "pitch": request.voice_pitch,
                    },
                    "background": {
                        "type": request.background_type,
                        "value": request.background_value,
                    }
                }
            ],
            "dimension": dimensions,
        }

        logger.info("heygen_generate_video",
                   title=request.title,
                   platform=request.platform,
                   avatar=request.avatar_id)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{HEYGEN_API_URL}/v2/video/generate",
                headers=headers,
                json=heygen_request
            )

            if response.status_code != 200:
                logger.error("heygen_generate_failed",
                           status=response.status_code,
                           body=response.text)
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"HeyGen API error: {response.text}"
                )

            data = response.json()
            video_id = data.get("data", {}).get("video_id")

            if not video_id:
                raise HTTPException(
                    status_code=500,
                    detail="No video_id in HeyGen response"
                )

            logger.info("heygen_video_created", video_id=video_id)
            return {
                "error": None,
                "data": {
                    "video_id": video_id
                }
            }

    except httpx.HTTPError as e:
        logger.error("heygen_http_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")


@router.get("/video/{video_id}/status")
async def get_video_status(
    video_id: str,
    current_user = Depends(get_current_admin_user)
):
    """
    Check video generation status.
    Returns status, video_url when completed.
    """
    try:
        headers = get_heygen_headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEYGEN_API_URL}/v1/video_status.get",
                headers=headers,
                params={"video_id": video_id}
            )

            if response.status_code != 200:
                logger.error("heygen_status_failed",
                           video_id=video_id,
                           status=response.status_code)
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"HeyGen API error: {response.text}"
                )

            data = response.json()
            status_data = data.get("data", {})

            return {
                "error": None,
                "data": {
                    "video_id": video_id,
                    "status": status_data.get("status", "pending"),
                    "video_url": status_data.get("video_url"),
                    "thumbnail_url": status_data.get("thumbnail_url"),
                    "duration": status_data.get("duration"),
                    "gif_url": status_data.get("gif_url"),
                    "created_at": status_data.get("created_at"),
                    "error": status_data.get("error"),
                }
            }

    except httpx.HTTPError as e:
        logger.error("heygen_http_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")


@router.get("/videos")
async def list_videos(current_user = Depends(get_current_admin_user)):
    """
    Get list of generated videos.
    """
    try:
        headers = get_heygen_headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEYGEN_API_URL}/v1/video.list",
                headers=headers
            )

            if response.status_code != 200:
                logger.error("heygen_list_videos_failed", status=response.status_code)
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"HeyGen API error: {response.text}"
                )

            data = response.json()
            return {"videos": data.get("data", {}).get("videos", [])}

    except httpx.HTTPError as e:
        logger.error("heygen_http_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")


@router.delete("/video/{video_id}")
async def delete_video(
    video_id: str,
    current_user = Depends(get_current_admin_user)
):
    """
    Delete a generated video.
    """
    try:
        headers = get_heygen_headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"{HEYGEN_API_URL}/v1/video.delete",
                headers=headers,
                params={"video_id": video_id}
            )

            if response.status_code != 200:
                logger.error("heygen_delete_failed",
                           video_id=video_id,
                           status=response.status_code)
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"HeyGen API error: {response.text}"
                )

            logger.info("heygen_video_deleted", video_id=video_id)
            return {"message": "Video deleted successfully"}

    except httpx.HTTPError as e:
        logger.error("heygen_http_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")


# ============ QUOTA ENDPOINT ============

@router.get("/quota")
async def get_quota(current_user = Depends(get_current_admin_user)):
    """
    Get remaining API quota.
    """
    try:
        headers = get_heygen_headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEYGEN_API_URL}/v2/user/remaining_quota",
                headers=headers
            )

            if response.status_code != 200:
                logger.error("heygen_quota_failed", status=response.status_code)
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"HeyGen API error: {response.text}"
                )

            data = response.json()
            return {
                "error": None,
                "data": data.get("data", {
                    "remaining_quota": 0,
                    "used_quota": 0
                })
            }

    except httpx.HTTPError as e:
        logger.error("heygen_http_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")


# ============ SCRIPT GENERATION ============

@router.post("/script/generate")
async def generate_script(
    request: ScriptGenerateRequest,
    current_user = Depends(get_current_admin_user)
):
    """
    Generate a video script using AI.
    Uses our existing AI infrastructure.
    """
    from app.domain.marketing.content_generator import content_generator

    # Duration to character count mapping
    duration_chars = {
        "short": 200,   # ~15-30 seconds
        "medium": 400,  # ~30-60 seconds
        "long": 800,    # ~1-2 minutes
    }

    max_chars = duration_chars.get(request.duration, 200)

    prompt = f"""Genera uno script per un video social in {request.language}.

Argomento: {request.topic}
Tono: {request.tone}
Lunghezza massima: {max_chars} caratteri (circa {request.duration})

Requisiti:
- Parla in prima persona
- Inizia con un hook accattivante
- Mantieni il linguaggio naturale e colloquiale
- Adatto per essere pronunciato da un avatar AI
- NO emoji nel testo (saranno aggiunte graficamente)
- Concludi con una call-to-action

Genera SOLO lo script, senza introduzioni o spiegazioni."""

    try:
        script = await content_generator.generate_content(
            content_type="script",
            topic=request.topic,
            custom_prompt=prompt,
            max_length=max_chars
        )

        logger.info("script_generated", topic=request.topic, length=len(script))
        return {"script": script}

    except Exception as e:
        logger.error("script_generation_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Script generation failed: {str(e)}"
        )
