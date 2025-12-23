"""
🎬 VEO Video Router

API completa per generazione video con VEO 3.1.

Endpoints:
- POST /generate - Genera video (sincrono o asincrono)
- GET /jobs - Lista job
- GET /jobs/{job_id} - Status job specifico
- POST /generate-marketing - Genera video marketing con template
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.veo_video_service import (
    veo_service,
    VideoGenerationRequest,
    VideoGenerationResult,
    VideoJob,
    VideoJobStatus,
    VideoAspectRatio,
    VideoResolution,
    generate_marketing_video,
)

router = APIRouter(prefix="/video", tags=["veo-video"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class GenerateVideoRequest(BaseModel):
    """Request per generazione video."""
    prompt: str = Field(..., min_length=10, max_length=2000)
    aspect_ratio: VideoAspectRatio = VideoAspectRatio.LANDSCAPE
    duration_seconds: int = Field(default=8, ge=5, le=8)
    resolution: VideoResolution = VideoResolution.HD
    negative_prompt: Optional[str] = None
    image_url: Optional[str] = None  # Per image-to-video
    wait_for_completion: bool = True  # Se false, ritorna subito job_id


class MarketingVideoRequest(BaseModel):
    """Request per video marketing."""
    topic: str = Field(..., min_length=5, max_length=500)
    style: str = Field(default="professional", max_length=100)
    duration: int = Field(default=8, ge=5, le=8)
    aspect: str = Field(default="16:9", pattern="^(16:9|9:16|1:1)$")


class VeoStatusResponse(BaseModel):
    """Status del servizio VEO."""
    configured: bool
    api_key_set: bool
    active_jobs: int
    completed_jobs: int


class JobListResponse(BaseModel):
    """Lista job."""
    count: int
    jobs: list[VideoJob]


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/status", response_model=VeoStatusResponse)
async def get_veo_status():
    """
    Verifica lo status del servizio VEO.
    """
    jobs = veo_service.list_jobs(limit=100)
    active = len([j for j in jobs if j.status in [VideoJobStatus.PENDING, VideoJobStatus.PROCESSING, VideoJobStatus.DOWNLOADING]])
    completed = len([j for j in jobs if j.status == VideoJobStatus.COMPLETED])

    return VeoStatusResponse(
        configured=veo_service.is_configured,
        api_key_set=bool(veo_service.api_key),
        active_jobs=active,
        completed_jobs=completed
    )


@router.post("/generate", response_model=VideoGenerationResult)
async def generate_video(request: GenerateVideoRequest):
    """
    Genera un video con VEO 3.1.

    Se wait_for_completion=true (default), la richiesta blocca
    fino al completamento del video (può richiedere 1-5 minuti).

    Se wait_for_completion=false, ritorna subito con job_id
    per polling successivo.
    """
    if not veo_service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="VEO non configurato. Imposta GOOGLE_API_KEY."
        )

    gen_request = VideoGenerationRequest(
        prompt=request.prompt,
        aspect_ratio=request.aspect_ratio,
        duration_seconds=request.duration_seconds,
        resolution=request.resolution,
        negative_prompt=request.negative_prompt,
        image_input_url=request.image_url
    )

    if request.wait_for_completion:
        # Sincrono - attende completamento
        return await veo_service.generate_video(gen_request, wait_for_completion=True)
    else:
        # Asincrono - ritorna subito
        job_id = await veo_service.generate_video_async(gen_request)
        job = veo_service.get_job(job_id)
        return VideoGenerationResult(success=True, job=job)


@router.post("/generate-async")
async def generate_video_async(
    request: GenerateVideoRequest,
    background_tasks: BackgroundTasks
):
    """
    Avvia generazione video in background.

    Ritorna immediatamente con job_id per polling.
    """
    if not veo_service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="VEO non configurato. Imposta GOOGLE_API_KEY."
        )

    gen_request = VideoGenerationRequest(
        prompt=request.prompt,
        aspect_ratio=request.aspect_ratio,
        duration_seconds=request.duration_seconds,
        resolution=request.resolution,
        negative_prompt=request.negative_prompt,
        image_input_url=request.image_url
    )

    job_id = await veo_service.generate_video_async(gen_request)
    job = veo_service.get_job(job_id)

    return {
        "success": True,
        "job_id": job_id,
        "status": job.status.value if job else "unknown",
        "message": "Video generation started. Poll /jobs/{job_id} for status."
    }


@router.post("/generate-marketing", response_model=VideoGenerationResult)
async def generate_marketing_video_endpoint(request: MarketingVideoRequest):
    """
    Genera video ottimizzato per marketing.

    Costruisce automaticamente prompt professionali.
    """
    if not veo_service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="VEO non configurato. Imposta GOOGLE_API_KEY."
        )

    return await generate_marketing_video(
        topic=request.topic,
        style=request.style,
        duration=request.duration,
        aspect=request.aspect
    )


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    limit: int = Query(20, ge=1, le=100),
    status: Optional[VideoJobStatus] = None
):
    """
    Lista job di generazione video.
    """
    jobs = veo_service.list_jobs(limit=limit)

    if status:
        jobs = [j for j in jobs if j.status == status]

    return JobListResponse(count=len(jobs), jobs=jobs)


@router.get("/jobs/{job_id}", response_model=VideoJob)
async def get_job(job_id: str):
    """
    Ottiene status di un job specifico.
    """
    job = veo_service.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} non trovato"
        )

    return job


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Elimina un job (e opzionalmente il file video).
    """
    job = veo_service.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} non trovato"
        )

    # Remove job from memory
    if job_id in veo_service._jobs:
        del veo_service._jobs[job_id]

    # Optionally delete file
    if job.video_path:
        try:
            import os
            if os.path.exists(job.video_path):
                os.remove(job.video_path)
        except Exception:
            pass

    return {"success": True, "message": f"Job {job_id} eliminato"}


@router.post("/cleanup")
async def cleanup_old_jobs(max_age_hours: int = Query(24, ge=1, le=168)):
    """
    Pulisce job più vecchi di N ore.
    """
    before_count = len(veo_service._jobs)
    veo_service.cleanup_old_jobs(max_age_hours)
    after_count = len(veo_service._jobs)

    return {
        "success": True,
        "jobs_before": before_count,
        "jobs_after": after_count,
        "jobs_removed": before_count - after_count
    }


# =============================================================================
# TEMPLATES
# =============================================================================

@router.get("/templates")
async def get_video_templates():
    """
    Ottiene template predefiniti per video marketing.
    """
    return {
        "templates": [
            {
                "id": "product_showcase",
                "name": "Product Showcase",
                "description": "Video per presentare un prodotto",
                "prompt_template": "Professional product showcase video featuring {product}. Cinematic angles, clean background, elegant lighting. Focus on product details and quality.",
                "suggested_duration": 8,
                "suggested_aspect": "16:9"
            },
            {
                "id": "social_story",
                "name": "Social Story",
                "description": "Video verticale per Instagram/TikTok Stories",
                "prompt_template": "Vertical video for social media story about {topic}. Eye-catching, trendy, fast-paced. Modern visuals with smooth transitions.",
                "suggested_duration": 8,
                "suggested_aspect": "9:16"
            },
            {
                "id": "brand_intro",
                "name": "Brand Introduction",
                "description": "Video introduttivo del brand",
                "prompt_template": "Elegant brand introduction video for {brand}. Professional, trustworthy, premium feel. Corporate colors, clean typography, inspiring visuals.",
                "suggested_duration": 8,
                "suggested_aspect": "16:9"
            },
            {
                "id": "testimonial_bg",
                "name": "Testimonial Background",
                "description": "Background video per testimonials",
                "prompt_template": "Abstract background video with soft bokeh lights and gentle movement. Colors: {colors}. Calming, professional, suitable for overlay text.",
                "suggested_duration": 8,
                "suggested_aspect": "16:9"
            },
            {
                "id": "event_promo",
                "name": "Event Promo",
                "description": "Promozione evento",
                "prompt_template": "Dynamic event promotional video for {event}. Exciting, energetic, builds anticipation. Quick cuts, bold typography, countdown feel.",
                "suggested_duration": 8,
                "suggested_aspect": "16:9"
            }
        ]
    }


@router.post("/templates/{template_id}/generate")
async def generate_from_template(
    template_id: str,
    variables: dict[str, str]
):
    """
    Genera video da un template.

    Esempio:
    POST /templates/product_showcase/generate
    {
        "product": "luxury watch"
    }
    """
    templates = (await get_video_templates())["templates"]
    template = next((t for t in templates if t["id"] == template_id), None)

    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Template {template_id} non trovato"
        )

    # Fill in template
    prompt = template["prompt_template"]
    for key, value in variables.items():
        prompt = prompt.replace(f"{{{key}}}", value)

    # Check if all placeholders are filled
    if "{" in prompt:
        missing = [s.split("}")[0] for s in prompt.split("{")[1:]]
        raise HTTPException(
            status_code=400,
            detail=f"Variabili mancanti: {missing}"
        )

    aspect = template["suggested_aspect"]

    return await generate_marketing_video(
        topic=prompt,
        style="professional",
        duration=template["suggested_duration"],
        aspect=aspect
    )
