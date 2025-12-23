"""
VEO Video Service - Google Veo AI Video Generation.

Servizio completo per generazione video con Google Veo API.
Supporta text-to-video, image-to-video, e video editing.

PREREQUISITI:
- Google Cloud Project con Vertex AI abilitato
- API Key o Service Account per Vertex AI
- Accesso a Veo model (attualmente in preview)

REFERENCE:
- https://cloud.google.com/vertex-ai/docs/generative-ai/video/overview

LIMITI:
- Video duration: 4-8 secondi
- Resolution: 1280x768 o 768x1280
- FPS: 24
- Aspect ratios: 16:9, 9:16
"""

import asyncio
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
import base64
import uuid

import httpx
import structlog
from pydantic import BaseModel, Field

from app.core.config import settings

logger = structlog.get_logger(__name__)


# =============================================================================
# ENUMS
# =============================================================================


class VideoAspectRatio(str, Enum):
    """Aspect ratio video."""
    LANDSCAPE_16_9 = "16:9"
    PORTRAIT_9_16 = "9:16"
    SQUARE_1_1 = "1:1"


class VideoStyle(str, Enum):
    """Stile video."""
    REALISTIC = "realistic"
    CINEMATIC = "cinematic"
    ANIMATED = "animated"
    DOCUMENTARY = "documentary"
    COMMERCIAL = "commercial"
    ARTISTIC = "artistic"


class VideoStatus(str, Enum):
    """Stato generazione video."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ContentType(str, Enum):
    """Tipo contenuto marketing."""
    PRODUCT_SHOWCASE = "product_showcase"
    BRAND_STORY = "brand_story"
    SOCIAL_REEL = "social_reel"
    TESTIMONIAL = "testimonial"
    TUTORIAL = "tutorial"
    PROMO = "promo"


# =============================================================================
# PYDANTIC MODELS
# =============================================================================


class VideoRequest(BaseModel):
    """Request generazione video."""
    prompt: str = Field(..., min_length=10, max_length=1000, description="Descrizione video")
    aspect_ratio: VideoAspectRatio = Field(default=VideoAspectRatio.LANDSCAPE_16_9)
    style: VideoStyle = Field(default=VideoStyle.REALISTIC)
    duration_seconds: int = Field(default=4, ge=4, le=8)
    seed: Optional[int] = Field(None, description="Seed per riproducibilità")
    negative_prompt: Optional[str] = Field(None, max_length=500, description="Cosa evitare")

    # Reference image for image-to-video
    reference_image_url: Optional[str] = Field(None, description="Immagine di riferimento")

    # Marketing context
    content_type: Optional[ContentType] = None
    brand_name: Optional[str] = None
    target_platform: Optional[str] = Field(None, description="instagram, tiktok, youtube, etc.")


class VideoResult(BaseModel):
    """Risultato generazione video."""
    request_id: str
    status: VideoStatus
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    prompt: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GenerationProgress(BaseModel):
    """Progresso generazione."""
    request_id: str
    status: VideoStatus
    progress_percent: int = 0
    estimated_time_remaining: Optional[int] = None  # seconds
    message: str = ""


class VideoGalleryItem(BaseModel):
    """Item nella gallery video."""
    id: str
    prompt: str
    video_url: str
    thumbnail_url: Optional[str] = None
    duration_seconds: int
    aspect_ratio: VideoAspectRatio
    style: VideoStyle
    created_at: datetime
    downloads: int = 0
    views: int = 0


class PromptTemplate(BaseModel):
    """Template prompt per tipo contenuto."""
    content_type: ContentType
    base_prompt: str
    style_suggestions: List[str]
    best_aspect_ratio: VideoAspectRatio
    recommended_duration: int


class ServiceStatus(BaseModel):
    """Stato servizio VEO."""
    available: bool = False
    model_name: str = ""
    region: str = ""
    quota_remaining: Optional[int] = None
    error: Optional[str] = None


# =============================================================================
# VEO VIDEO SERVICE
# =============================================================================


class VeoVideoService:
    """
    Servizio generazione video con Google Veo.

    Features:
    - Text-to-video generation
    - Image-to-video animation
    - Marketing-optimized prompts
    - Progress tracking
    - Video gallery management

    Usage:
        service = VeoVideoService()

        # Genera video da prompt
        result = await service.generate_video(VideoRequest(
            prompt="A coffee cup on a wooden table, steam rising",
            aspect_ratio=VideoAspectRatio.LANDSCAPE_16_9,
            style=VideoStyle.CINEMATIC
        ))

        # Controlla progresso
        progress = await service.get_progress(result.request_id)
    """

    # Vertex AI endpoint per Veo
    VERTEX_AI_BASE = "https://{region}-aiplatform.googleapis.com/v1"
    VEO_MODEL = "veo-001"  # Current Veo model

    # Prompt templates per marketing
    PROMPT_TEMPLATES: Dict[ContentType, PromptTemplate] = {
        ContentType.PRODUCT_SHOWCASE: PromptTemplate(
            content_type=ContentType.PRODUCT_SHOWCASE,
            base_prompt="Professional product showcase video of {product}. Clean white background, elegant rotation, studio lighting, 4K quality, commercial grade.",
            style_suggestions=["cinematic", "realistic", "commercial"],
            best_aspect_ratio=VideoAspectRatio.LANDSCAPE_16_9,
            recommended_duration=6
        ),
        ContentType.BRAND_STORY: PromptTemplate(
            content_type=ContentType.BRAND_STORY,
            base_prompt="Emotional brand story video. {description}. Cinematic color grading, professional videography, inspiring mood.",
            style_suggestions=["cinematic", "documentary"],
            best_aspect_ratio=VideoAspectRatio.LANDSCAPE_16_9,
            recommended_duration=8
        ),
        ContentType.SOCIAL_REEL: PromptTemplate(
            content_type=ContentType.SOCIAL_REEL,
            base_prompt="Trendy social media reel video. {description}. Dynamic movements, vibrant colors, engaging, vertical format.",
            style_suggestions=["animated", "artistic"],
            best_aspect_ratio=VideoAspectRatio.PORTRAIT_9_16,
            recommended_duration=4
        ),
        ContentType.TESTIMONIAL: PromptTemplate(
            content_type=ContentType.TESTIMONIAL,
            base_prompt="Professional testimonial video background. {description}. Soft bokeh, warm lighting, corporate setting.",
            style_suggestions=["realistic", "documentary"],
            best_aspect_ratio=VideoAspectRatio.LANDSCAPE_16_9,
            recommended_duration=6
        ),
        ContentType.TUTORIAL: PromptTemplate(
            content_type=ContentType.TUTORIAL,
            base_prompt="Step-by-step tutorial video. {description}. Clear visuals, educational style, professional demonstration.",
            style_suggestions=["realistic", "documentary"],
            best_aspect_ratio=VideoAspectRatio.LANDSCAPE_16_9,
            recommended_duration=8
        ),
        ContentType.PROMO: PromptTemplate(
            content_type=ContentType.PROMO,
            base_prompt="Eye-catching promotional video. {description}. Bold colors, dynamic transitions, high energy, call to action.",
            style_suggestions=["commercial", "animated", "artistic"],
            best_aspect_ratio=VideoAspectRatio.LANDSCAPE_16_9,
            recommended_duration=6
        )
    }

    def __init__(self):
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.region = settings.GOOGLE_CLOUD_REGION or "us-central1"
        self.api_key = settings.GOOGLE_API_KEY
        self._client: Optional[httpx.AsyncClient] = None
        self._jobs: Dict[str, VideoResult] = {}  # In-memory job tracking
        self._gallery: List[VideoGalleryItem] = []  # In-memory gallery

    @property
    def is_configured(self) -> bool:
        """Verifica se le credenziali sono configurate."""
        return bool(self.project_id and self.api_key)

    @property
    def base_url(self) -> str:
        """URL base Vertex AI."""
        return self.VERTEX_AI_BASE.format(region=self.region)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(120.0),  # Long timeout per video generation
                follow_redirects=True
            )
        return self._client

    async def close(self) -> None:
        """Chiudi HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _get_headers(self) -> Dict[str, str]:
        """Headers per richieste API."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "x-goog-user-project": self.project_id
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Esegue richiesta a Vertex AI API.
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        client = await self._get_client()

        try:
            if method == "GET":
                response = await client.get(url, params=params, headers=headers)
            elif method == "POST":
                response = await client.post(url, json=data, params=params, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            if response.status_code not in [200, 201]:
                error = response.json() if response.content else {}
                error_msg = error.get("error", {}).get("message", response.text)

                logger.error(
                    "veo_api_error",
                    endpoint=endpoint,
                    status=response.status_code,
                    error=error_msg
                )

                raise VeoAPIError(
                    f"Veo API Error [{response.status_code}]: {error_msg}",
                    status_code=response.status_code
                )

            return response.json() if response.content else {}

        except httpx.TimeoutException:
            logger.error("veo_api_timeout", endpoint=endpoint)
            raise VeoAPIError("Veo API timeout")
        except httpx.RequestError as e:
            logger.error("veo_api_request_error", endpoint=endpoint, error=str(e))
            raise VeoAPIError(f"Request error: {str(e)}")

    # =========================================================================
    # VIDEO GENERATION
    # =========================================================================

    async def generate_video(self, request: VideoRequest) -> VideoResult:
        """
        Genera video da prompt testuale.

        Args:
            request: VideoRequest con tutti i parametri

        Returns:
            VideoResult con request_id per tracking
        """
        request_id = str(uuid.uuid4())

        # Enhance prompt con style e marketing context
        enhanced_prompt = self._enhance_prompt(request)

        # Create result placeholder
        result = VideoResult(
            request_id=request_id,
            status=VideoStatus.PENDING,
            prompt=request.prompt,
            metadata={
                "enhanced_prompt": enhanced_prompt,
                "aspect_ratio": request.aspect_ratio.value,
                "style": request.style.value,
                "duration": request.duration_seconds,
                "content_type": request.content_type.value if request.content_type else None
            }
        )

        # Store job
        self._jobs[request_id] = result

        try:
            # Build request payload per Veo API
            payload = self._build_generation_payload(request, enhanced_prompt)

            # Submit to Vertex AI
            endpoint = f"/projects/{self.project_id}/locations/{self.region}/publishers/google/models/{self.VEO_MODEL}:generateVideo"

            response = await self._make_request("POST", endpoint, data=payload)

            # Update status
            result.status = VideoStatus.PROCESSING

            # In produzione, Veo restituisce un operation name per polling
            operation_name = response.get("name")
            if operation_name:
                result.metadata["operation_name"] = operation_name

            logger.info(
                "veo_generation_started",
                request_id=request_id,
                prompt=request.prompt[:50]
            )

            # Start async polling (in produzione, usare task queue)
            asyncio.create_task(self._poll_completion(request_id, operation_name))

            return result

        except VeoAPIError as e:
            result.status = VideoStatus.FAILED
            result.error = str(e)
            return result

    async def generate_video_from_image(
        self,
        image_url: str,
        motion_prompt: str,
        request: Optional[VideoRequest] = None
    ) -> VideoResult:
        """
        Genera video animando un'immagine (image-to-video).

        Args:
            image_url: URL immagine da animare
            motion_prompt: Descrizione del movimento
            request: Parametri aggiuntivi

        Returns:
            VideoResult
        """
        request_id = str(uuid.uuid4())

        if request is None:
            request = VideoRequest(
                prompt=motion_prompt,
                reference_image_url=image_url
            )
        else:
            request.reference_image_url = image_url

        result = VideoResult(
            request_id=request_id,
            status=VideoStatus.PENDING,
            prompt=motion_prompt,
            metadata={
                "type": "image_to_video",
                "source_image": image_url
            }
        )

        self._jobs[request_id] = result

        try:
            # Download and encode image
            client = await self._get_client()
            img_response = await client.get(image_url)

            if img_response.status_code != 200:
                raise VeoAPIError(f"Failed to download image: {img_response.status_code}")

            image_base64 = base64.b64encode(img_response.content).decode()

            # Build image-to-video payload
            payload = {
                "instances": [{
                    "prompt": motion_prompt,
                    "image": {
                        "bytesBase64Encoded": image_base64
                    }
                }],
                "parameters": {
                    "aspectRatio": request.aspect_ratio.value,
                    "durationSeconds": request.duration_seconds,
                    "sampleCount": 1
                }
            }

            if request.seed:
                payload["parameters"]["seed"] = request.seed

            endpoint = f"/projects/{self.project_id}/locations/{self.region}/publishers/google/models/{self.VEO_MODEL}:generateVideo"

            response = await self._make_request("POST", endpoint, data=payload)

            result.status = VideoStatus.PROCESSING

            operation_name = response.get("name")
            if operation_name:
                result.metadata["operation_name"] = operation_name

            logger.info(
                "veo_image_to_video_started",
                request_id=request_id
            )

            asyncio.create_task(self._poll_completion(request_id, operation_name))

            return result

        except VeoAPIError as e:
            result.status = VideoStatus.FAILED
            result.error = str(e)
            return result

    def _build_generation_payload(
        self,
        request: VideoRequest,
        enhanced_prompt: str
    ) -> Dict[str, Any]:
        """
        Costruisce payload per Veo API.
        """
        payload = {
            "instances": [{
                "prompt": enhanced_prompt
            }],
            "parameters": {
                "aspectRatio": request.aspect_ratio.value,
                "durationSeconds": request.duration_seconds,
                "sampleCount": 1  # Numero di varianti
            }
        }

        if request.seed:
            payload["parameters"]["seed"] = request.seed

        if request.negative_prompt:
            payload["instances"][0]["negativePrompt"] = request.negative_prompt

        # Style parameters (modello dipendente)
        style_params = self._get_style_parameters(request.style)
        payload["parameters"].update(style_params)

        return payload

    def _enhance_prompt(self, request: VideoRequest) -> str:
        """
        Arricchisce prompt con context e best practices.
        """
        prompt = request.prompt

        # Add style qualifiers
        style_qualifiers = {
            VideoStyle.REALISTIC: "photorealistic, high quality, natural lighting",
            VideoStyle.CINEMATIC: "cinematic quality, film grain, dramatic lighting, movie-like",
            VideoStyle.ANIMATED: "animation style, vibrant colors, smooth motion",
            VideoStyle.DOCUMENTARY: "documentary style, authentic, natural footage",
            VideoStyle.COMMERCIAL: "professional commercial video, clean, polished, advertising quality",
            VideoStyle.ARTISTIC: "artistic, creative, unique visual style, aesthetic"
        }

        style_suffix = style_qualifiers.get(request.style, "")

        # Add platform-specific optimizations
        platform_hints = {
            "instagram": "optimized for Instagram, engaging, scroll-stopping",
            "tiktok": "TikTok style, trending, dynamic, vertical format",
            "youtube": "YouTube quality, high resolution, professional",
            "linkedin": "professional, corporate-friendly, business appropriate"
        }

        if request.target_platform:
            platform_hint = platform_hints.get(request.target_platform.lower(), "")
            if platform_hint:
                prompt = f"{prompt}. {platform_hint}"

        # Add brand mention if provided
        if request.brand_name:
            prompt = f"{prompt}. Brand: {request.brand_name}"

        # Combine with style
        enhanced = f"{prompt}. {style_suffix}. Smooth motion, high frame rate."

        return enhanced

    def _get_style_parameters(self, style: VideoStyle) -> Dict[str, Any]:
        """
        Restituisce parametri modello per stile.
        """
        # Questi parametri dipendono dalla versione Veo
        style_params = {
            VideoStyle.REALISTIC: {
                "guidanceScale": 7.5,
                "motionBucketId": 127
            },
            VideoStyle.CINEMATIC: {
                "guidanceScale": 8.0,
                "motionBucketId": 180
            },
            VideoStyle.ANIMATED: {
                "guidanceScale": 9.0,
                "motionBucketId": 200
            },
            VideoStyle.DOCUMENTARY: {
                "guidanceScale": 6.0,
                "motionBucketId": 100
            },
            VideoStyle.COMMERCIAL: {
                "guidanceScale": 7.0,
                "motionBucketId": 150
            },
            VideoStyle.ARTISTIC: {
                "guidanceScale": 10.0,
                "motionBucketId": 180
            }
        }

        return style_params.get(style, {})

    async def _poll_completion(
        self,
        request_id: str,
        operation_name: Optional[str]
    ) -> None:
        """
        Polling asincrono per completamento generazione.

        In produzione, usare Pub/Sub o webhook callback.
        """
        if request_id not in self._jobs:
            return

        result = self._jobs[request_id]

        max_polls = 60  # 5 minuti max (5 sec interval)
        poll_interval = 5  # seconds

        for i in range(max_polls):
            await asyncio.sleep(poll_interval)

            try:
                if operation_name:
                    # Check operation status
                    response = await self._make_request(
                        "GET",
                        f"/{operation_name}"
                    )

                    if response.get("done"):
                        # Operation completed
                        if "error" in response:
                            result.status = VideoStatus.FAILED
                            result.error = response["error"].get("message", "Unknown error")
                        else:
                            # Extract video URL from response
                            video_data = response.get("response", {})
                            videos = video_data.get("generatedSamples", [])

                            if videos:
                                video = videos[0]
                                result.video_url = video.get("video", {}).get("uri")
                                result.thumbnail_url = video.get("thumbnail", {}).get("uri")
                                result.duration_seconds = video.get("durationSeconds")
                                result.status = VideoStatus.COMPLETED
                                result.completed_at = datetime.utcnow()

                                # Add to gallery
                                self._add_to_gallery(result)

                                logger.info(
                                    "veo_generation_completed",
                                    request_id=request_id,
                                    video_url=result.video_url
                                )
                            else:
                                result.status = VideoStatus.FAILED
                                result.error = "No video generated"

                        return
                else:
                    # Simulazione per test senza API reale
                    # In produzione rimuovere
                    if i >= 3:  # Simula 15 secondi di elaborazione
                        result.status = VideoStatus.COMPLETED
                        result.video_url = f"https://storage.googleapis.com/veo-output/{request_id}.mp4"
                        result.thumbnail_url = f"https://storage.googleapis.com/veo-output/{request_id}_thumb.jpg"
                        result.duration_seconds = result.metadata.get("duration", 4)
                        result.completed_at = datetime.utcnow()

                        self._add_to_gallery(result)

                        logger.info("veo_generation_simulated_complete", request_id=request_id)
                        return

            except Exception as e:
                logger.warning(
                    "veo_poll_error",
                    request_id=request_id,
                    error=str(e)
                )

        # Timeout
        result.status = VideoStatus.FAILED
        result.error = "Generation timeout"

        logger.error("veo_generation_timeout", request_id=request_id)

    def _add_to_gallery(self, result: VideoResult) -> None:
        """Aggiunge video completato alla gallery."""
        if result.status != VideoStatus.COMPLETED or not result.video_url:
            return

        item = VideoGalleryItem(
            id=result.request_id,
            prompt=result.prompt,
            video_url=result.video_url,
            thumbnail_url=result.thumbnail_url,
            duration_seconds=result.duration_seconds or 4,
            aspect_ratio=VideoAspectRatio(result.metadata.get("aspect_ratio", "16:9")),
            style=VideoStyle(result.metadata.get("style", "realistic")),
            created_at=result.created_at
        )

        self._gallery.insert(0, item)

        # Keep only last 100 items
        if len(self._gallery) > 100:
            self._gallery = self._gallery[:100]

    # =========================================================================
    # STATUS & TRACKING
    # =========================================================================

    async def get_progress(self, request_id: str) -> GenerationProgress:
        """
        Ottiene progresso generazione.

        Args:
            request_id: ID richiesta

        Returns:
            GenerationProgress
        """
        if request_id not in self._jobs:
            raise VeoAPIError(f"Request not found: {request_id}")

        result = self._jobs[request_id]

        # Calculate estimated progress
        if result.status == VideoStatus.PENDING:
            progress = 0
            message = "In coda per elaborazione..."
            eta = 30
        elif result.status == VideoStatus.PROCESSING:
            # Stima basata su tempo trascorso
            elapsed = (datetime.utcnow() - result.created_at).total_seconds()
            estimated_total = 60  # ~60 sec per video
            progress = min(int((elapsed / estimated_total) * 100), 95)
            eta = max(0, int(estimated_total - elapsed))
            message = "Generazione video in corso..."
        elif result.status == VideoStatus.COMPLETED:
            progress = 100
            message = "Video completato!"
            eta = 0
        else:
            progress = 0
            message = result.error or "Generazione fallita"
            eta = None

        return GenerationProgress(
            request_id=request_id,
            status=result.status,
            progress_percent=progress,
            estimated_time_remaining=eta,
            message=message
        )

    async def get_result(self, request_id: str) -> VideoResult:
        """
        Ottiene risultato completo.

        Args:
            request_id: ID richiesta

        Returns:
            VideoResult
        """
        if request_id not in self._jobs:
            raise VeoAPIError(f"Request not found: {request_id}")

        return self._jobs[request_id]

    async def get_status(self) -> ServiceStatus:
        """
        Stato servizio Veo.

        Returns:
            ServiceStatus
        """
        status = ServiceStatus(
            model_name=self.VEO_MODEL,
            region=self.region
        )

        if not self.is_configured:
            status.error = "Google Cloud non configurato"
            return status

        try:
            # Verifica disponibilità modello
            endpoint = f"/projects/{self.project_id}/locations/{self.region}/publishers/google/models/{self.VEO_MODEL}"

            await self._make_request("GET", endpoint)

            status.available = True

            logger.info("veo_service_available")

        except VeoAPIError as e:
            status.error = str(e)
            logger.warning("veo_service_unavailable", error=str(e))

        return status

    # =========================================================================
    # GALLERY & HISTORY
    # =========================================================================

    async def get_gallery(
        self,
        limit: int = 20,
        offset: int = 0,
        content_type: Optional[ContentType] = None
    ) -> List[VideoGalleryItem]:
        """
        Ottiene gallery video generati.

        Args:
            limit: Numero massimo risultati
            offset: Offset per paginazione
            content_type: Filtra per tipo contenuto

        Returns:
            Lista VideoGalleryItem
        """
        gallery = self._gallery

        if content_type:
            gallery = [v for v in gallery if v.metadata.get("content_type") == content_type.value]

        return gallery[offset:offset + limit]

    async def get_pending_jobs(self) -> List[VideoResult]:
        """
        Ottiene job in corso.

        Returns:
            Lista VideoResult con status PENDING o PROCESSING
        """
        return [
            job for job in self._jobs.values()
            if job.status in [VideoStatus.PENDING, VideoStatus.PROCESSING]
        ]

    # =========================================================================
    # MARKETING HELPERS
    # =========================================================================

    def get_prompt_template(self, content_type: ContentType) -> PromptTemplate:
        """
        Ottiene template prompt per tipo contenuto.

        Args:
            content_type: Tipo contenuto marketing

        Returns:
            PromptTemplate
        """
        return self.PROMPT_TEMPLATES.get(content_type, self.PROMPT_TEMPLATES[ContentType.PROMO])

    def build_marketing_prompt(
        self,
        content_type: ContentType,
        description: str,
        brand_name: Optional[str] = None,
        product: Optional[str] = None
    ) -> str:
        """
        Costruisce prompt ottimizzato per marketing.

        Args:
            content_type: Tipo contenuto
            description: Descrizione specifica
            brand_name: Nome brand
            product: Nome prodotto

        Returns:
            Prompt ottimizzato
        """
        template = self.get_prompt_template(content_type)

        prompt = template.base_prompt.format(
            description=description,
            product=product or "product",
            brand=brand_name or "brand"
        )

        return prompt

    async def generate_marketing_video(
        self,
        content_type: ContentType,
        description: str,
        brand_name: Optional[str] = None,
        product: Optional[str] = None,
        target_platform: Optional[str] = None
    ) -> VideoResult:
        """
        Genera video ottimizzato per marketing.

        Usa template e best practices per il tipo di contenuto.

        Args:
            content_type: Tipo contenuto
            description: Descrizione specifica
            brand_name: Nome brand
            product: Nome prodotto
            target_platform: Piattaforma target

        Returns:
            VideoResult
        """
        template = self.get_prompt_template(content_type)

        prompt = self.build_marketing_prompt(
            content_type=content_type,
            description=description,
            brand_name=brand_name,
            product=product
        )

        # Seleziona stile appropriato
        style = VideoStyle(template.style_suggestions[0]) if template.style_suggestions else VideoStyle.REALISTIC

        request = VideoRequest(
            prompt=prompt,
            aspect_ratio=template.best_aspect_ratio,
            style=style,
            duration_seconds=template.recommended_duration,
            content_type=content_type,
            brand_name=brand_name,
            target_platform=target_platform
        )

        return await self.generate_video(request)


# =============================================================================
# EXCEPTIONS
# =============================================================================


class VeoAPIError(Exception):
    """Errore API Veo."""

    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================


_veo_service: Optional[VeoVideoService] = None


def get_veo_video_service() -> VeoVideoService:
    """Get singleton instance of VeoVideoService."""
    global _veo_service
    if _veo_service is None:
        _veo_service = VeoVideoService()
    return _veo_service
