"""
VEO Video Router - API endpoints per generazione video AI.

Endpoints:
- GET  /status                  - Stato servizio
- POST /generate                - Genera video da prompt
- POST /generate/from-image     - Genera video da immagine
- POST /generate/marketing      - Genera video marketing ottimizzato
- GET  /progress/{request_id}   - Progresso generazione
- GET  /result/{request_id}     - Risultato completo
- GET  /gallery                 - Gallery video generati
- GET  /pending                 - Job in corso
- GET  /templates               - Template prompt disponibili
- GET  /templates/{content_type} - Template specifico
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.api.dependencies.permissions import require_admin
from app.domain.auth.models import User
from app.services.veo_video_service import (
    get_veo_video_service,
    VeoVideoService,
    VeoAPIError,
    VideoRequest,
    VideoResult,
    VideoAspectRatio,
    VideoStyle,
    VideoStatus,
    ContentType,
    GenerationProgress,
    VideoGalleryItem,
    PromptTemplate,
    ServiceStatus
)

router = APIRouter(prefix="/ai/veo", tags=["VEO Video Generation"])


# =============================================================================
# DEPENDENCIES
# =============================================================================


def get_service() -> VeoVideoService:
    """Dependency per VEO service."""
    return get_veo_video_service()


# =============================================================================
# REQUEST MODELS
# =============================================================================


class GenerateVideoRequest(BaseModel):
    """Request per generazione video."""
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Descrizione dettagliata del video"
    )
    aspect_ratio: VideoAspectRatio = Field(
        default=VideoAspectRatio.LANDSCAPE_16_9,
        description="Aspect ratio: 16:9, 9:16, o 1:1"
    )
    style: VideoStyle = Field(
        default=VideoStyle.REALISTIC,
        description="Stile video: realistic, cinematic, animated, etc."
    )
    duration_seconds: int = Field(
        default=4,
        ge=4,
        le=8,
        description="Durata video (4-8 secondi)"
    )
    seed: Optional[int] = Field(
        None,
        description="Seed per riproducibilità"
    )
    negative_prompt: Optional[str] = Field(
        None,
        max_length=500,
        description="Elementi da evitare nel video"
    )
    content_type: Optional[ContentType] = Field(
        None,
        description="Tipo contenuto marketing"
    )
    brand_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Nome brand per ottimizzazione"
    )
    target_platform: Optional[str] = Field(
        None,
        description="Piattaforma target: instagram, tiktok, youtube, linkedin"
    )


class ImageToVideoRequest(BaseModel):
    """Request per video da immagine."""
    image_url: str = Field(..., description="URL immagine sorgente")
    motion_prompt: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Descrizione del movimento desiderato"
    )
    aspect_ratio: VideoAspectRatio = Field(default=VideoAspectRatio.LANDSCAPE_16_9)
    duration_seconds: int = Field(default=4, ge=4, le=8)
    style: VideoStyle = Field(default=VideoStyle.REALISTIC)


class MarketingVideoRequest(BaseModel):
    """Request per video marketing."""
    content_type: ContentType = Field(
        ...,
        description="Tipo contenuto: product_showcase, brand_story, social_reel, etc."
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Descrizione specifica del contenuto"
    )
    brand_name: Optional[str] = Field(None, max_length=100)
    product: Optional[str] = Field(None, max_length=100)
    target_platform: Optional[str] = Field(None)


class GalleryResponse(BaseModel):
    """Response gallery video."""
    videos: List[VideoGalleryItem]
    total: int
    limit: int
    offset: int


# =============================================================================
# STATUS ENDPOINT
# =============================================================================


@router.get("/status", response_model=ServiceStatus)
async def get_veo_status(
    current_user: User = Depends(require_admin),
    service: VeoVideoService = Depends(get_service)
):
    """
    Stato servizio VEO.

    Verifica disponibilità modello e quota rimanente.
    """
    return await service.get_status()


# =============================================================================
# GENERATION ENDPOINTS
# =============================================================================


@router.post("/generate", response_model=VideoResult)
async def generate_video(
    request: GenerateVideoRequest,
    current_user: User = Depends(require_admin),
    service: VeoVideoService = Depends(get_service)
):
    """
    Genera video da prompt testuale.

    Ritorna immediatamente con request_id per tracking progresso.
    La generazione avviene in background (tipicamente 30-60 secondi).

    **Esempio prompt:**
    - "A coffee cup on a wooden table, steam rising slowly, morning light"
    - "Modern city skyline at sunset, timelapse, cinematic quality"
    - "Product rotating on white background, studio lighting, 4K"
    """
    if not service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VEO non configurato. Configurare GOOGLE_CLOUD_PROJECT e GOOGLE_API_KEY."
        )

    video_request = VideoRequest(
        prompt=request.prompt,
        aspect_ratio=request.aspect_ratio,
        style=request.style,
        duration_seconds=request.duration_seconds,
        seed=request.seed,
        negative_prompt=request.negative_prompt,
        content_type=request.content_type,
        brand_name=request.brand_name,
        target_platform=request.target_platform
    )

    result = await service.generate_video(video_request)

    if result.status == VideoStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error
        )

    return result


@router.post("/generate/from-image", response_model=VideoResult)
async def generate_video_from_image(
    request: ImageToVideoRequest,
    current_user: User = Depends(require_admin),
    service: VeoVideoService = Depends(get_service)
):
    """
    Genera video animando un'immagine (image-to-video).

    L'immagine viene scaricata, analizzata e animata secondo il motion_prompt.

    **Esempio motion_prompt:**
    - "Camera slowly zooms in while leaves sway gently"
    - "The person smiles and turns their head"
    - "Parallax effect, subtle depth motion"
    """
    if not service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VEO non configurato"
        )

    video_request = VideoRequest(
        prompt=request.motion_prompt,
        aspect_ratio=request.aspect_ratio,
        style=request.style,
        duration_seconds=request.duration_seconds
    )

    result = await service.generate_video_from_image(
        image_url=request.image_url,
        motion_prompt=request.motion_prompt,
        request=video_request
    )

    if result.status == VideoStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error
        )

    return result


@router.post("/generate/marketing", response_model=VideoResult)
async def generate_marketing_video(
    request: MarketingVideoRequest,
    current_user: User = Depends(require_admin),
    service: VeoVideoService = Depends(get_service)
):
    """
    Genera video ottimizzato per marketing.

    Usa template e best practices per il tipo di contenuto specificato.

    **Tipi contenuto supportati:**
    - `product_showcase`: Video prodotto professionale
    - `brand_story`: Video storytelling emozionale
    - `social_reel`: Reel per social media
    - `testimonial`: Background per testimonial
    - `tutorial`: Video tutorial/how-to
    - `promo`: Video promozionale
    """
    if not service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VEO non configurato"
        )

    result = await service.generate_marketing_video(
        content_type=request.content_type,
        description=request.description,
        brand_name=request.brand_name,
        product=request.product,
        target_platform=request.target_platform
    )

    if result.status == VideoStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error
        )

    return result


# =============================================================================
# TRACKING ENDPOINTS
# =============================================================================


@router.get("/progress/{request_id}", response_model=GenerationProgress)
async def get_generation_progress(
    request_id: str,
    current_user: User = Depends(require_admin),
    service: VeoVideoService = Depends(get_service)
):
    """
    Ottiene progresso generazione video.

    Poll questo endpoint ogni 2-5 secondi durante la generazione.
    """
    try:
        return await service.get_progress(request_id)
    except VeoAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/result/{request_id}", response_model=VideoResult)
async def get_generation_result(
    request_id: str,
    current_user: User = Depends(require_admin),
    service: VeoVideoService = Depends(get_service)
):
    """
    Ottiene risultato completo generazione.

    Include video_url e thumbnail_url quando completato.
    """
    try:
        return await service.get_result(request_id)
    except VeoAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# =============================================================================
# GALLERY ENDPOINTS
# =============================================================================


@router.get("/gallery", response_model=GalleryResponse)
async def get_video_gallery(
    limit: int = Query(20, ge=1, le=100, description="Numero massimo risultati"),
    offset: int = Query(0, ge=0, description="Offset paginazione"),
    content_type: Optional[ContentType] = Query(None, description="Filtra per tipo contenuto"),
    current_user: User = Depends(require_admin),
    service: VeoVideoService = Depends(get_service)
):
    """
    Gallery video generati.

    Restituisce gli ultimi video completati con paginazione.
    """
    videos = await service.get_gallery(
        limit=limit,
        offset=offset,
        content_type=content_type
    )

    return GalleryResponse(
        videos=videos,
        total=len(service._gallery),  # Total in gallery
        limit=limit,
        offset=offset
    )


@router.get("/pending", response_model=List[VideoResult])
async def get_pending_jobs(
    current_user: User = Depends(require_admin),
    service: VeoVideoService = Depends(get_service)
):
    """
    Job in corso o in coda.

    Restituisce tutte le generazioni non ancora completate.
    """
    return await service.get_pending_jobs()


# =============================================================================
# TEMPLATE ENDPOINTS
# =============================================================================


@router.get("/templates", response_model=List[PromptTemplate])
async def get_prompt_templates(
    current_user: User = Depends(require_admin),
    service: VeoVideoService = Depends(get_service)
):
    """
    Lista template prompt disponibili.

    Ogni template è ottimizzato per un tipo di contenuto marketing.
    """
    return list(service.PROMPT_TEMPLATES.values())


@router.get("/templates/{content_type}", response_model=PromptTemplate)
async def get_prompt_template(
    content_type: ContentType,
    current_user: User = Depends(require_admin),
    service: VeoVideoService = Depends(get_service)
):
    """
    Template prompt specifico per tipo contenuto.

    Include:
    - Base prompt da personalizzare
    - Stili suggeriti
    - Aspect ratio consigliato
    - Durata raccomandata
    """
    template = service.get_prompt_template(content_type)
    return template


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================


@router.get("/styles")
async def get_available_styles(
    current_user: User = Depends(require_admin)
):
    """
    Lista stili video disponibili con descrizione.
    """
    return {
        "styles": [
            {
                "id": VideoStyle.REALISTIC.value,
                "name": "Realistico",
                "description": "Video fotorealistici, alta qualità, illuminazione naturale"
            },
            {
                "id": VideoStyle.CINEMATIC.value,
                "name": "Cinematico",
                "description": "Qualità cinematografica, color grading drammatico, film grain"
            },
            {
                "id": VideoStyle.ANIMATED.value,
                "name": "Animato",
                "description": "Stile animazione, colori vibranti, movimento fluido"
            },
            {
                "id": VideoStyle.DOCUMENTARY.value,
                "name": "Documentario",
                "description": "Stile documentario, autentico, footage naturale"
            },
            {
                "id": VideoStyle.COMMERCIAL.value,
                "name": "Commerciale",
                "description": "Video commerciale professionale, pulito, advertising quality"
            },
            {
                "id": VideoStyle.ARTISTIC.value,
                "name": "Artistico",
                "description": "Stile artistico creativo, visivamente unico, estetico"
            }
        ]
    }


@router.get("/aspect-ratios")
async def get_aspect_ratios(
    current_user: User = Depends(require_admin)
):
    """
    Aspect ratio supportati con use case.
    """
    return {
        "aspect_ratios": [
            {
                "id": VideoAspectRatio.LANDSCAPE_16_9.value,
                "name": "Landscape 16:9",
                "resolution": "1280x720",
                "use_cases": ["YouTube", "Website", "Presentations", "TV"]
            },
            {
                "id": VideoAspectRatio.PORTRAIT_9_16.value,
                "name": "Portrait 9:16",
                "resolution": "720x1280",
                "use_cases": ["Instagram Reels", "TikTok", "YouTube Shorts", "Stories"]
            },
            {
                "id": VideoAspectRatio.SQUARE_1_1.value,
                "name": "Square 1:1",
                "resolution": "1080x1080",
                "use_cases": ["Instagram Feed", "LinkedIn", "Facebook"]
            }
        ]
    }


@router.get("/content-types")
async def get_content_types(
    current_user: User = Depends(require_admin)
):
    """
    Tipi contenuto marketing supportati.
    """
    return {
        "content_types": [
            {
                "id": ContentType.PRODUCT_SHOWCASE.value,
                "name": "Product Showcase",
                "description": "Video prodotto professionale con rotazione e studio lighting"
            },
            {
                "id": ContentType.BRAND_STORY.value,
                "name": "Brand Story",
                "description": "Video storytelling emozionale per raccontare il brand"
            },
            {
                "id": ContentType.SOCIAL_REEL.value,
                "name": "Social Reel",
                "description": "Reel dinamici e accattivanti per social media"
            },
            {
                "id": ContentType.TESTIMONIAL.value,
                "name": "Testimonial",
                "description": "Background professionale per video testimonial"
            },
            {
                "id": ContentType.TUTORIAL.value,
                "name": "Tutorial",
                "description": "Video how-to e tutorial educativi"
            },
            {
                "id": ContentType.PROMO.value,
                "name": "Promo",
                "description": "Video promozionali ad alto impatto"
            }
        ]
    }
