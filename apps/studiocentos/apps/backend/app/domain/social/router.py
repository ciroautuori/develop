"""
Social Publisher Router - API per pubblicazione multi-piattaforma.

Endpoints:
- GET /social/platforms - Lista piattaforme configurate
- POST /social/publish - Pubblica su piattaforme selezionate
- POST /social/publish/story - Pubblica story
- GET /social/status - Stato connessioni
- POST /social/upload-media - Upload file media per social
- POST /social/schedule - Programma post per pubblicazione futura
"""

import os
import uuid
import aiofiles
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.api.dependencies.database import get_db
from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.domain.auth.admin_models import AdminUser
from app.domain.marketing.models import ScheduledPost, PostStatus, PostType
from .publisher_service import SocialPublisherService, PublishResult

import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/social", tags=["Social Publishing"])


# ============================================================================
# SCHEMAS
# ============================================================================

class PublishRequest(BaseModel):
    """Request per pubblicazione."""
    content: str = Field(..., min_length=1, max_length=5000)
    platforms: list[str] = Field(..., min_length=1)
    media_url: Optional[str] = None
    media_type: str = Field(default="image", pattern="^(image|video)$")
    hashtags: list[str] = []


class StoryPublishRequest(BaseModel):
    """Request per pubblicazione story."""
    media_url: str = Field(...)
    platforms: list[str] = Field(default=["instagram"])


class SchedulePostRequest(BaseModel):
    """Request per programmare un post."""
    content: str = Field(..., min_length=1, max_length=5000)
    platforms: list[str] = Field(..., min_length=1)
    scheduled_time: datetime = Field(..., description="Data/ora pubblicazione programmata (ISO 8601)")
    media_url: Optional[str] = None
    media_type: str = Field(default="image", pattern="^(image|video|text)$")
    hashtags: list[str] = []
    title: Optional[str] = None


class SchedulePostResponse(BaseModel):
    """Response programmazione post."""
    success: bool
    post_id: int
    scheduled_at: datetime
    platforms: list[str]
    message: str


class MediaUploadResponse(BaseModel):
    """Response upload media."""
    success: bool
    url: str
    filename: str
    content_type: str
    size: int


class PublishResponse(BaseModel):
    """Response pubblicazione."""
    success: bool
    results: list[dict]
    published_count: int
    failed_count: int


class PlatformStatus(BaseModel):
    """Stato piattaforma."""
    configured: bool
    page_id: Optional[str] = None
    account_id: Optional[str] = None


class PlatformsStatusResponse(BaseModel):
    """Response stato piattaforme."""
    facebook: PlatformStatus
    instagram: PlatformStatus
    linkedin: PlatformStatus
    twitter: PlatformStatus
    configured_platforms: list[str]


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/platforms")
async def get_configured_platforms(
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Ottieni lista piattaforme social configurate.

    Ritorna solo le piattaforme con credenziali valide.
    """
    service = SocialPublisherService()
    platforms = service.get_configured_platforms()

    return {
        "platforms": platforms,
        "count": len(platforms)
    }


@router.get("/status", response_model=PlatformsStatusResponse)
async def get_platforms_status(
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Ottieni stato dettagliato di tutte le piattaforme.

    Mostra quali sono configurate e i relativi account ID.
    """
    service = SocialPublisherService()
    status = await service.get_platform_status()

    configured = service.get_configured_platforms()

    return PlatformsStatusResponse(
        facebook=PlatformStatus(**status["facebook"]),
        instagram=PlatformStatus(**status["instagram"]),
        linkedin=PlatformStatus(**status["linkedin"]),
        twitter=PlatformStatus(**status["twitter"]),
        configured_platforms=configured
    )


@router.post("/publish", response_model=PublishResponse)
async def publish_content(
    request: PublishRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Pubblica contenuto su piattaforme selezionate.

    Supporta:
    - Post testuali (tutte le piattaforme)
    - Post con immagine (tutte tranne LinkedIn per ora)
    - Post con video (Facebook, Instagram)

    Gli hashtag vengono aggiunti automaticamente al contenuto.
    """
    # Add hashtags to content
    content = request.content
    if request.hashtags:
        hashtag_text = " ".join([f"#{tag}" for tag in request.hashtags])
        content = f"{content}\n\n{hashtag_text}"

    service = SocialPublisherService()

    try:
        results = await service.publish(
            content=content,
            platforms=request.platforms,
            media_url=request.media_url,
            media_type=request.media_type
        )

        # Convert to dict for response
        results_dict = [r.dict() for r in results]

        published = sum(1 for r in results if r.success)
        failed = len(results) - published

        # Log results
        logger.info(
            "social_publish_completed",
            user_id=admin.id,
            platforms=request.platforms,
            published=published,
            failed=failed
        )

        # Save to database (scheduled_posts table)
        if published > 0:
            await _save_publish_record(db, request, results)

        return PublishResponse(
            success=published > 0,
            results=results_dict,
            published_count=published,
            failed_count=failed
        )

    except Exception as e:
        logger.exception("social_publish_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore pubblicazione: {str(e)}"
        )
    finally:
        await service.close()


@router.post("/publish/story", response_model=PublishResponse)
async def publish_story(
    request: StoryPublishRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Pubblica story su Instagram e/o Facebook.

    Le stories richiedono un'immagine o video.
    Durata: 24 ore.
    """
    service = SocialPublisherService()

    try:
        results = await service.publish_story(
            media_url=request.media_url,
            platforms=request.platforms
        )

        results_dict = [r.dict() for r in results]
        published = sum(1 for r in results if r.success)

        return PublishResponse(
            success=published > 0,
            results=results_dict,
            published_count=published,
            failed_count=len(results) - published
        )

    except Exception as e:
        logger.exception("story_publish_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore pubblicazione story: {str(e)}"
        )
    finally:
        await service.close()


@router.post("/test-connection/{platform}")
async def test_platform_connection(
    platform: str,
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Testa la connessione ad una piattaforma specifica.

    Verifica che le credenziali siano valide.
    """
    service = SocialPublisherService()

    platform = platform.lower()

    try:
        if platform == "facebook":
            if not service.meta.is_configured:
                return {"success": False, "error": "Facebook non configurato"}

            # Test by getting page info
            client = await service.meta.get_client()
            response = await client.get(
                f"{service.meta.BASE_URL}/{service.meta.page_id}",
                params={"access_token": service.meta.access_token, "fields": "name,id"}
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "platform": "facebook",
                    "page_name": data.get("name"),
                    "page_id": data.get("id")
                }
            else:
                return {"success": False, "error": response.text}

        elif platform == "instagram":
            if not service.meta.instagram_id:
                return {"success": False, "error": "Instagram non configurato"}

            client = await service.meta.get_client()
            response = await client.get(
                f"{service.meta.BASE_URL}/{service.meta.instagram_id}",
                params={
                    "access_token": service.meta.access_token,
                    "fields": "username,name,profile_picture_url"
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "platform": "instagram",
                    "username": data.get("username"),
                    "name": data.get("name")
                }
            else:
                return {"success": False, "error": response.text}

        elif platform == "linkedin":
            if not service.linkedin.is_configured:
                return {"success": False, "error": "LinkedIn non configurato"}

            client = await service.linkedin.get_client()
            response = await client.get(f"{service.linkedin.BASE_URL}/me")

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "platform": "linkedin",
                    "profile_id": data.get("id")
                }
            else:
                return {"success": False, "error": response.text}

        else:
            return {"success": False, "error": f"Piattaforma {platform} non supportata"}

    except Exception as e:
        return {"success": False, "error": str(e)}

    finally:
        await service.close()


# ============================================================================
# MEDIA UPLOAD ENDPOINT
# ============================================================================

# Upload configuration
SOCIAL_UPLOAD_DIR = Path("/app/uploads/social")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB for videos


@router.post("/upload-media", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Upload media file per social post.

    Supporta:
    - Immagini: JPEG, PNG, WebP, GIF
    - Video: MP4, MOV, WebM

    Limite: 50MB

    Returns URL pubblico per utilizzo in post.
    """
    # Ensure upload directory exists
    SOCIAL_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Validate content type
    content_type = file.content_type or ""
    if content_type not in ALLOWED_IMAGE_TYPES and content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo file non supportato: {content_type}. Usa JPEG, PNG, WebP, GIF, MP4, MOV o WebM."
        )

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Validate file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File troppo grande: {file_size / 1024 / 1024:.1f}MB. Limite: 50MB."
        )

    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    original_ext = Path(file.filename or "file").suffix.lower()

    # Normalize extension
    ext_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "video/mp4": ".mp4",
        "video/quicktime": ".mov",
        "video/webm": ".webm",
    }
    ext = ext_map.get(content_type, original_ext)

    filename = f"{timestamp}_{unique_id}{ext}"
    file_path = SOCIAL_UPLOAD_DIR / filename

    try:
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)

        # Generate public URL (served by nginx)
        public_url = f"/uploads/social/{filename}"

        logger.info(
            "social_media_uploaded",
            user_id=admin.id,
            filename=filename,
            content_type=content_type,
            size=file_size
        )

        return MediaUploadResponse(
            success=True,
            url=public_url,
            filename=filename,
            content_type=content_type,
            size=file_size
        )

    except Exception as e:
        # Cleanup on error
        if file_path.exists():
            file_path.unlink(missing_ok=True)

        logger.exception("social_media_upload_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore upload: {str(e)}"
        )


# ============================================================================
# SCHEDULE POST ENDPOINT
# ============================================================================

@router.post("/schedule", response_model=SchedulePostResponse)
async def schedule_post(
    request: SchedulePostRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Programma un post per pubblicazione futura.

    Il post verrà salvato nel database e pubblicato automaticamente
    all'orario programmato dallo scheduler.

    Args:
        content: Contenuto del post
        platforms: Lista piattaforme (facebook, instagram, linkedin, twitter)
        scheduled_time: Data/ora pubblicazione (ISO 8601)
        media_url: URL media opzionale
        media_type: Tipo media (image, video, text)
        hashtags: Lista hashtag opzionale
        title: Titolo interno opzionale

    Returns:
        Post ID e conferma programmazione
    """
    # Validate scheduled time is in the future
    now = datetime.utcnow()
    if request.scheduled_time.replace(tzinfo=None) <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La data di pubblicazione deve essere nel futuro"
        )

    # Validate platforms
    valid_platforms = {"facebook", "instagram", "linkedin", "twitter"}
    invalid_platforms = set(p.lower() for p in request.platforms) - valid_platforms
    if invalid_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Piattaforme non valide: {', '.join(invalid_platforms)}"
        )

    # Determine media type enum
    media_type_map = {
        "text": PostType.TEXT,
        "image": PostType.IMAGE,
        "video": PostType.VIDEO,
    }
    post_media_type = media_type_map.get(request.media_type, PostType.TEXT)

    # Prepare content with hashtags
    content = request.content
    if request.hashtags:
        hashtag_text = " ".join([f"#{tag.lstrip('#')}" for tag in request.hashtags])
        content = f"{content}\n\n{hashtag_text}"

    try:
        # Create scheduled post
        scheduled_post = ScheduledPost(
            content=content,
            title=request.title,
            hashtags=request.hashtags or [],
            mentions=[],
            media_urls=[request.media_url] if request.media_url else [],
            media_type=post_media_type,
            platforms=[p.lower() for p in request.platforms],
            scheduled_at=request.scheduled_time,
            status=PostStatus.SCHEDULED,
            platform_results={},
            ai_generated=False,
            created_by=admin.id,
            metrics={}
        )

        db.add(scheduled_post)
        db.commit()
        db.refresh(scheduled_post)

        logger.info(
            "social_post_scheduled",
            user_id=admin.id,
            post_id=scheduled_post.id,
            platforms=request.platforms,
            scheduled_at=request.scheduled_time.isoformat()
        )

        return SchedulePostResponse(
            success=True,
            post_id=scheduled_post.id,
            scheduled_at=scheduled_post.scheduled_at,
            platforms=scheduled_post.platforms,
            message=f"Post programmato per {scheduled_post.scheduled_at.strftime('%d/%m/%Y %H:%M')}"
        )

    except Exception as e:
        db.rollback()
        logger.exception("social_schedule_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore programmazione post: {str(e)}"
        )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _save_publish_record(db: Session, request: PublishRequest, results: list[PublishResult]):
    """Salva record pubblicazione nel database."""
    from sqlalchemy import text
    import json
    from datetime import datetime

    # Find successful platforms
    successful_platforms = [r.platform for r in results if r.success]
    platform_results = {r.platform: {"post_id": r.post_id, "post_url": r.post_url} for r in results}

    if not successful_platforms:
        return

    try:
        insert_query = text("""
            INSERT INTO scheduled_posts (
                content, platforms, media_urls, media_type,
                status, scheduled_at, published_at,
                platform_results, ai_generated,
                created_at, updated_at
            ) VALUES (
                :content, :platforms, :media_urls, :media_type,
                'published', NOW(), NOW(),
                :platform_results, false,
                NOW(), NOW()
            )
        """)

        db.execute(insert_query, {
            "content": request.content,
            "platforms": json.dumps(successful_platforms),
            "media_urls": json.dumps([request.media_url] if request.media_url else []),
            "media_type": request.media_type,
            "platform_results": json.dumps(platform_results)
        })
        db.commit()

    except Exception as e:
        logger.error("save_publish_record_error", error=str(e))
        # Non-blocking - pubblicazione già avvenuta


# ============================================================================
# IMAGE RESIZE ENDPOINT
# ============================================================================

class ImageResizeRequest(BaseModel):
    """Request per resize immagine."""
    image_url: str = Field(..., description="URL immagine sorgente")
    platform: str = Field(..., description="Piattaforma target (facebook, instagram, etc.)")
    quality: int = Field(default=90, ge=1, le=100, description="Qualità output 1-100")


class ImageResizeResponse(BaseModel):
    """Response resize immagine."""
    success: bool
    platform: str
    width: int
    height: int
    size_bytes: int
    message: str


@router.post("/image/resize", response_model=ImageResizeResponse)
async def resize_image_for_platform(
    request: ImageResizeRequest,
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Ridimensiona immagine per piattaforma social specifica.

    Piattaforme supportate:
    - facebook: 1200x630
    - instagram: 1080x1080
    - instagram_portrait: 1080x1350
    - instagram_story: 1080x1920
    - linkedin: 1200x627
    - twitter: 1600x900
    - tiktok: 1080x1920
    - pinterest: 1000x1500
    """
    from app.infrastructure.media import image_resize_service, SOCIAL_SIZES

    if request.platform not in SOCIAL_SIZES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Piattaforma non supportata. Usa: {list(SOCIAL_SIZES.keys())}"
        )

    try:
        resized_bytes = await image_resize_service.resize_from_url(
            image_url=request.image_url,
            platform=request.platform,
            quality=request.quality
        )

        width, height = SOCIAL_SIZES[request.platform]

        # Storage: Save to S3/CloudStorage and return public URL
        # Current: Returns resize info only (client handles storage)

        return ImageResizeResponse(
            success=True,
            platform=request.platform,
            width=width,
            height=height,
            size_bytes=len(resized_bytes),
            message=f"Immagine ridimensionata per {request.platform}: {width}x{height}"
        )

    except Exception as e:
        logger.exception("image_resize_endpoint_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore resize: {str(e)}"
        )


@router.get("/image/sizes")
async def get_image_sizes():
    """
    Ottieni dimensioni ottimali per tutte le piattaforme social.
    """
    from app.infrastructure.media import SOCIAL_SIZES

    return {
        "platforms": {
            platform: {"width": w, "height": h, "aspect_ratio": f"{w}:{h}"}
            for platform, (w, h) in SOCIAL_SIZES.items()
        }
    }


# ============================================================================
# TOKEN MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/token/status")
async def get_token_status(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    🔑 Verifica lo stato dei token Meta (Facebook/Instagram).

    Controlla:
    - Validità del token
    - Data di scadenza
    - Necessità di refresh
    """
    from .token_refresh_service import meta_token_service

    try:
        status = await meta_token_service.get_token_status()
        return status
    finally:
        await meta_token_service.close()


@router.get("/token/refresh-instructions")
async def get_token_refresh_instructions(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    📋 Ottieni istruzioni per rinnovare i token Meta.

    Guida passo-passo per:
    - Generare nuovo token
    - Convertire in long-lived
    - Aggiornare configurazione
    """
    from .token_refresh_service import meta_token_service

    return {
        "instructions": meta_token_service.get_refresh_instructions(),
        "links": {
            "graph_api_explorer": "https://developers.facebook.com/tools/explorer/",
            "app_dashboard": f"https://developers.facebook.com/apps/{meta_token_service.app_id or ''}/",
            "token_debugger": "https://developers.facebook.com/tools/debug/accesstoken/"
        }
    }


@router.post("/token/convert-to-long-lived")
async def convert_token_to_long_lived(
    short_lived_token: str,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    🔄 Converti un token short-lived in long-lived (60 giorni).

    Args:
        short_lived_token: Token da Graph API Explorer (1 ora)

    Returns:
        Long-lived token (60 giorni)
    """
    from .token_refresh_service import meta_token_service

    try:
        result = await meta_token_service.convert_to_long_lived(short_lived_token)

        if result:
            return {
                "success": True,
                "access_token": result.access_token,
                "expires_in": result.expires_in,
                "expires_at": result.expires_at.isoformat() if result.expires_at else None,
                "message": "Token convertito! Aggiorna META_ACCESS_TOKEN in .env.production"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conversione fallita. Verifica che il token sia valido."
            )
    finally:
        await meta_token_service.close()
