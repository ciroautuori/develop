"""
🎬 VEO Video Service - Complete Video Generation

Servizio completo per generazione video con Google VEO 3.1:
- Generazione asincrona
- Polling automatico
- Download e storage
- Tracking jobs
- Retry con fallback

VEO 3.1 Features:
- Video fino a 8 secondi (estendibili a 148s)
- Risoluzioni 720p e 1080p
- Audio nativo generato
- Image-to-video
- Reference images per consistenza stile
"""

import asyncio
import base64
import os
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import aiohttp
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


# =============================================================================
# MODELS
# =============================================================================

class VideoJobStatus(str, Enum):
    """Stato del job di generazione video."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DOWNLOADING = "downloading"


class VideoAspectRatio(str, Enum):
    """Aspect ratio supportati."""
    LANDSCAPE = "16:9"
    PORTRAIT = "9:16"
    SQUARE = "1:1"


class VideoResolution(str, Enum):
    """Risoluzioni supportate."""
    HD = "720p"
    FULL_HD = "1080p"


class VideoGenerationRequest(BaseModel):
    """Request per generazione video."""
    prompt: str
    aspect_ratio: VideoAspectRatio = VideoAspectRatio.LANDSCAPE
    duration_seconds: int = Field(default=8, ge=5, le=8)
    resolution: VideoResolution = VideoResolution.HD
    negative_prompt: Optional[str] = None
    image_input_url: Optional[str] = None  # Per image-to-video
    reference_image_url: Optional[str] = None  # Per style consistency


class VideoJob(BaseModel):
    """Job di generazione video."""
    job_id: str
    status: VideoJobStatus
    prompt: str
    operation_name: Optional[str] = None
    video_url: Optional[str] = None
    video_path: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_seconds: int = 8
    aspect_ratio: str = "16:9"
    resolution: str = "720p"
    file_size_bytes: Optional[int] = None


class VideoGenerationResult(BaseModel):
    """Risultato finale generazione."""
    success: bool
    job: VideoJob
    download_url: Optional[str] = None


# =============================================================================
# VEO VIDEO SERVICE
# =============================================================================

class VeoVideoService:
    """
    Servizio completo per VEO video generation.

    Features:
    - Job tracking con storage in-memory
    - Polling asincrono
    - Download automatico
    - Retry logic
    """

    VEO_GENERATE_URL = "https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-generate-preview:generateVideos"
    VEO_POLL_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self._jobs: dict[str, VideoJob] = {}
        self._upload_dir = Path(os.getenv("UPLOAD_DIR", "/app/uploads/videos"))

    @property
    def is_configured(self) -> bool:
        """Verifica se VEO è configurato."""
        return bool(self.api_key)

    # =========================================================================
    # JOB MANAGEMENT
    # =========================================================================

    def get_job(self, job_id: str) -> Optional[VideoJob]:
        """Ottiene un job per ID."""
        return self._jobs.get(job_id)

    def list_jobs(self, limit: int = 20) -> list[VideoJob]:
        """Lista ultimi job."""
        jobs = list(self._jobs.values())
        jobs.sort(key=lambda x: x.created_at, reverse=True)
        return jobs[:limit]

    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Pulisce job vecchi."""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        to_delete = [
            job_id for job_id, job in self._jobs.items()
            if job.created_at < cutoff
        ]
        for job_id in to_delete:
            del self._jobs[job_id]

        logger.info("veo_jobs_cleaned", count=len(to_delete))

    # =========================================================================
    # VIDEO GENERATION
    # =========================================================================

    async def generate_video(
        self,
        request: VideoGenerationRequest,
        wait_for_completion: bool = True
    ) -> VideoGenerationResult:
        """
        Genera un video con VEO 3.1.

        Se wait_for_completion=True, fa polling fino al completamento.
        Altrimenti ritorna subito con job in pending.
        """
        if not self.is_configured:
            job = VideoJob(
                job_id=str(uuid.uuid4()),
                status=VideoJobStatus.FAILED,
                prompt=request.prompt,
                error="VEO non configurato. Imposta GOOGLE_API_KEY."
            )
            return VideoGenerationResult(success=False, job=job)

        # Create job
        job = VideoJob(
            job_id=str(uuid.uuid4()),
            status=VideoJobStatus.PENDING,
            prompt=request.prompt,
            duration_seconds=request.duration_seconds,
            aspect_ratio=request.aspect_ratio.value,
            resolution=request.resolution.value
        )
        self._jobs[job.job_id] = job

        logger.info("veo_job_created", job_id=job.job_id, prompt=request.prompt[:50])

        try:
            # Prepare image input if provided
            image_data = None
            if request.image_input_url:
                image_data = await self._download_image(request.image_input_url)

            # Start generation
            result = await self._start_generation(
                prompt=request.prompt,
                aspect_ratio=request.aspect_ratio.value,
                duration_seconds=request.duration_seconds,
                resolution=request.resolution.value,
                negative_prompt=request.negative_prompt,
                image_input=image_data
            )

            if not result:
                job.status = VideoJobStatus.FAILED
                job.error = "Failed to start video generation"
                return VideoGenerationResult(success=False, job=job)

            job.operation_name = result.get("operation_name")
            job.status = VideoJobStatus.PROCESSING

            if not wait_for_completion:
                return VideoGenerationResult(success=True, job=job)

            # Poll for completion
            poll_result = await self._poll_until_complete(job)

            if not poll_result:
                job.status = VideoJobStatus.FAILED
                job.error = "Video generation timed out or failed"
                return VideoGenerationResult(success=False, job=job)

            # Download video
            job.status = VideoJobStatus.DOWNLOADING
            download_result = await self._download_and_save_video(job, poll_result)

            if download_result:
                job.status = VideoJobStatus.COMPLETED
                job.completed_at = datetime.utcnow()
                job.video_url = download_result["url"]
                job.video_path = download_result["path"]
                job.file_size_bytes = download_result.get("size")

                logger.info(
                    "veo_video_completed",
                    job_id=job.job_id,
                    size=job.file_size_bytes
                )

                return VideoGenerationResult(
                    success=True,
                    job=job,
                    download_url=job.video_url
                )
            else:
                job.status = VideoJobStatus.FAILED
                job.error = "Failed to download video"
                return VideoGenerationResult(success=False, job=job)

        except Exception as e:
            job.status = VideoJobStatus.FAILED
            job.error = str(e)
            logger.error("veo_generation_error", error=str(e), job_id=job.job_id)
            return VideoGenerationResult(success=False, job=job)

    async def _start_generation(
        self,
        prompt: str,
        aspect_ratio: str,
        duration_seconds: int,
        resolution: str,
        negative_prompt: Optional[str] = None,
        image_input: Optional[bytes] = None
    ) -> Optional[dict]:
        """Avvia generazione video."""
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
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

        # Add image for image-to-video
        if image_input:
            image_b64 = base64.b64encode(image_input).decode()
            payload["image"] = {
                "bytesBase64Encoded": image_b64
            }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.VEO_GENERATE_URL,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    operation_name = data.get("name")
                    if operation_name:
                        return {"operation_name": operation_name}
                else:
                    error_text = await response.text()
                    logger.warning("veo_start_error", status=response.status, error=error_text[:200])

        return None

    async def _poll_until_complete(
        self,
        job: VideoJob,
        max_polls: int = 72,  # 12 minutes (72 * 10s)
        poll_interval: int = 10
    ) -> Optional[dict]:
        """Polling fino al completamento."""
        if not job.operation_name:
            return None

        url = f"{self.VEO_POLL_BASE_URL}/{job.operation_name}"
        headers = {"x-goog-api-key": self.api_key}

        for attempt in range(max_polls):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()

                        if data.get("done"):
                            result = data.get("response", {})
                            generated_videos = result.get("generatedVideos", [])

                            if generated_videos:
                                video_info = generated_videos[0]
                                video_file = video_info.get("video", {})

                                return {
                                    "video_uri": video_file.get("uri"),
                                    "video_name": video_file.get("name"),
                                    "mime_type": video_file.get("mimeType", "video/mp4")
                                }

                        # Still processing
                        logger.debug(
                            "veo_polling",
                            job_id=job.job_id,
                            attempt=attempt + 1,
                            max=max_polls
                        )
                        await asyncio.sleep(poll_interval)
                    else:
                        error_text = await response.text()
                        logger.warning("veo_poll_error", status=response.status, error=error_text[:150])
                        return None

        logger.warning("veo_poll_timeout", job_id=job.job_id)
        return None

    async def _download_and_save_video(
        self,
        job: VideoJob,
        poll_result: dict
    ) -> Optional[dict]:
        """Scarica e salva il video."""
        video_uri = poll_result.get("video_uri")
        if not video_uri:
            return None

        # Ensure upload directory exists
        self._upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        filename = f"veo_{job.job_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp4"
        filepath = self._upload_dir / filename

        # Download video - VEO returns a GCS URI that needs authentication
        # For GCS URIs, we need to use the File API
        try:
            if video_uri.startswith("gs://"):
                # Use Google's File API to get the video
                download_url = await self._get_download_url(poll_result.get("video_name"))
                if download_url:
                    video_uri = download_url

            async with aiohttp.ClientSession() as session:
                # Add auth header for Google APIs
                headers = {"x-goog-api-key": self.api_key} if "googleapis.com" in str(video_uri) else {}

                async with session.get(video_uri, headers=headers) as response:
                    if response.status == 200:
                        content = await response.read()

                        # Save file
                        with open(filepath, "wb") as f:
                            f.write(content)

                        # Generate public URL
                        base_url = os.getenv("BASE_URL", "https://markettina.it")
                        public_url = f"{base_url}/uploads/videos/{filename}"

                        return {
                            "path": str(filepath),
                            "url": public_url,
                            "size": len(content)
                        }
                    else:
                        logger.warning("veo_download_error", status=response.status)
        except Exception as e:
            logger.error("veo_download_error", error=str(e))

        return None

    async def _get_download_url(self, file_name: str) -> Optional[str]:
        """Get download URL for Google File API resource."""
        if not file_name:
            return None

        # The video_name is in format "files/xxxxx"
        # We can get it via the files API
        url = f"https://generativelanguage.googleapis.com/v1beta/{file_name}"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={"x-goog-api-key": self.api_key}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("uri")

        return None

    async def _download_image(self, url: str) -> Optional[bytes]:
        """Scarica immagine da URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
        except Exception as e:
            logger.warning("veo_image_download_error", error=str(e))
        return None

    # =========================================================================
    # ASYNC JOB PROCESSING (Background)
    # =========================================================================

    async def generate_video_async(
        self,
        request: VideoGenerationRequest
    ) -> str:
        """
        Avvia generazione in background e ritorna job_id.

        Utile per UI che non vogliono bloccare.
        """
        result = await self.generate_video(request, wait_for_completion=False)

        # Start background polling
        asyncio.create_task(self._background_poll_and_download(result.job))

        return result.job.job_id

    async def _background_poll_and_download(self, job: VideoJob):
        """Background task per polling e download."""
        try:
            poll_result = await self._poll_until_complete(job)

            if poll_result:
                job.status = VideoJobStatus.DOWNLOADING
                download_result = await self._download_and_save_video(job, poll_result)

                if download_result:
                    job.status = VideoJobStatus.COMPLETED
                    job.completed_at = datetime.utcnow()
                    job.video_url = download_result["url"]
                    job.video_path = download_result["path"]
                    job.file_size_bytes = download_result.get("size")

                    logger.info("veo_background_completed", job_id=job.job_id)
                else:
                    job.status = VideoJobStatus.FAILED
                    job.error = "Download failed"
            else:
                job.status = VideoJobStatus.FAILED
                job.error = "Generation timed out"

        except Exception as e:
            job.status = VideoJobStatus.FAILED
            job.error = str(e)
            logger.error("veo_background_error", error=str(e))


# =============================================================================
# SINGLETON
# =============================================================================

veo_service = VeoVideoService()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def generate_marketing_video(
    topic: str,
    style: str = "professional",
    duration: int = 8,
    aspect: str = "16:9"
) -> VideoGenerationResult:
    """
    Helper per generazione video marketing.

    Costruisce prompt ottimizzato per contenuti marketing.
    """
    prompt = f"""Create a {duration}-second professional marketing video.

Topic: {topic}
Style: {style}, modern, engaging
Visual quality: Cinematic, high production value
Camera: Smooth movements, professional framing
Lighting: Professional, well-lit
Colors: Vibrant but professional

The video should be suitable for social media marketing and grab attention immediately."""

    request = VideoGenerationRequest(
        prompt=prompt,
        aspect_ratio=VideoAspectRatio.PORTRAIT if aspect == "9:16" else VideoAspectRatio.LANDSCAPE,
        duration_seconds=duration
    )

    return await veo_service.generate_video(request)
