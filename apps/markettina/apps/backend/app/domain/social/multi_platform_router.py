"""
Multi-Platform Social Media Post Creation Endpoint.

New workflow:
1. Create content
2. Select platforms
3. Generate platform-specific images
4. Publish/schedule
"""
from datetime import datetime

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.domain.social.publisher_service import SocialPublisherService

router = APIRouter(prefix="/social", tags=["Multi-Platform Social"])


# ============================================================================
# SCHEMAS
# ============================================================================

class PlatformImageConfig(BaseModel):
    """Configuration for a single platform's image."""
    platform: str = Field(..., description="facebook, instagram, instagram_story")
    prompt: str = Field(..., description="Image-specific prompt")
    aspect_ratio: str = Field(default="auto", description="Override aspect ratio")


class MultiPlatformPostRequest(BaseModel):
    """Request to create multi-platform social media post."""
    # Content
    content: str = Field(..., description="Post text/caption")
    cta: str | None = Field(None, description="Call to action")
    hashtags: list[str] = Field(default_factory=list, description="Hashtags without #")

    # Platforms & Images
    platforms: list[str] = Field(..., description="Platforms: facebook, instagram, instagram_story")
    base_image_prompt: str = Field(..., description="Base prompt for all images")
    platform_prompts: dict[str, str] | None = Field(None, description="Platform-specific prompts")

    # Publishing
    publish_immediately: bool = Field(default=False, description="Publish now or save as draft")
    schedule_time: datetime | None = Field(None, description="Schedule for future")

    # AI Options
    image_style: str = Field(default="professional", description="Image style")
    image_provider: str = Field(default="auto", description="AI provider")


class PlatformResult(BaseModel):
    """Result for single platform."""
    platform: str
    success: bool
    post_id: str | None = None
    post_url: str | None = None
    image_url: str | None = None
    error: str | None = None


class MultiPlatformPostResponse(BaseModel):
    """Response from multi-platform post creation."""
    job_id: str
    status: str  # "published", "scheduled", "draft", "partial"
    platforms: list[PlatformResult]
    total_platforms: int
    successful: int
    failed: int
    images_generated: int
    total_time: float


# ============================================================================
# ENDPOINT
# ============================================================================

@router.post("/create-multi-platform-post", response_model=MultiPlatformPostResponse)
async def create_multi_platform_post(
    request: MultiPlatformPostRequest,
    # user: User = Depends(get_current_user)  # Add auth when ready
):
    """
    🚀 Create and publish social media post across multiple platforms!

    Workflow:
    1. Generates platform-optimized images (batch)
    2. Publishes to selected platforms
    3. Returns results for each platform

    Supports:
    - Immediate publishing
    - Scheduled posts
    - Draft mode (images only, no publish)
    """
    import time
    import uuid

    start_time = time.time()
    job_id = str(uuid.uuid4())[:8]

    # Build full content with CTA and hashtags
    full_content = request.content
    if request.cta:
        full_content += f"\n\n{request.cta}"
    if request.hashtags:
        hashtags_str = " ".join([f"#{tag}" for tag in request.hashtags])
        full_content += f"\n\n{hashtags_str}"

    # Step 1: Generate images for each platform
    platform_images = {}
    images_generated = 0

    try:
        # Build batch image request
        batch_images = []
        for platform in request.platforms:
            # Get platform-specific prompt or use base
            platform_prompt = request.platform_prompts.get(platform) if request.platform_prompts else None
            full_prompt = f"{request.base_image_prompt} {platform_prompt}".strip() if platform_prompt else request.base_image_prompt

            batch_images.append({
                "prompt": full_prompt,
                "platform": platform,
                "tag": platform
            })

        # Call AI microservice batch endpoint
        async with httpx.AsyncClient(timeout=180.0) as client:
            ai_response = await client.post(
                f"{settings.AI_SERVICE_URL}/api/v1/marketing/image/batch-generate",
                json={
                    "base_prompt": "",  # Already included in full_prompt
                    "style": request.image_style,
                    "provider": request.image_provider,
                    "images": batch_images
                },
                headers={"Authorization": f"Bearer {settings.AI_SERVICE_API_KEY}"}
            )

        if ai_response.status_code == 200:
            batch_result = ai_response.json()
            for result in batch_result["results"]:
                if result["success"]:
                    platform_images[result["platform"]] = result["image_url"]
                    images_generated += 1
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Image generation failed: {ai_response.text[:200]}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation error: {e!s}"
        )

    # Step 2: Publish to platforms (if not draft mode)
    platform_results = []

    if request.publish_immediately and not request.schedule_time:
        # Publish now
        publisher = SocialPublisherService()

        for platform in request.platforms:
            try:
                image_url = platform_images.get(platform)

                if not image_url:
                    platform_results.append(PlatformResult(
                        platform=platform,
                        success=False,
                        error="Image generation failed"
                    ))
                    continue

                # Publish based on platform
                if platform == "facebook":
                    result = await publisher.meta.publish_to_facebook(
                        message=full_content,
                        media_url=image_url
                    )
                elif platform == "instagram":
                    result = await publisher.meta.publish_to_instagram(
                        caption=full_content,
                        image_url=image_url
                    )
                elif platform == "instagram_story":
                    result = await publisher.meta.publish_story(
                        platform="instagram",
                        media_url=image_url
                    )
                else:
                    result = None

                if result and result.success:
                    platform_results.append(PlatformResult(
                        platform=platform,
                        success=True,
                        post_id=result.post_id,
                        post_url=result.post_url,
                        image_url=image_url
                    ))
                else:
                    platform_results.append(PlatformResult(
                        platform=platform,
                        success=False,
                        image_url=image_url,
                        error=result.error if result else "Unknown error"
                    ))

            except Exception as e:
                platform_results.append(PlatformResult(
                    platform=platform,
                    success=False,
                    image_url=platform_images.get(platform),
                    error=str(e)
                ))

    else:
        # Draft mode or scheduled - just return images
        for platform in request.platforms:
            platform_results.append(PlatformResult(
                platform=platform,
                success=True,
                image_url=platform_images.get(platform),
                post_id=None,
                post_url=None
            ))

    # Calculate stats
    successful = sum(1 for r in platform_results if r.success)
    failed = len(platform_results) - successful
    total_time = time.time() - start_time

    # Determine status
    if request.schedule_time:
        status_str = "scheduled"
    elif not request.publish_immediately:
        status_str = "draft"
    elif successful == len(platform_results):
        status_str = "published"
    elif successful > 0:
        status_str = "partial"
    else:
        status_str = "failed"

    return MultiPlatformPostResponse(
        job_id=job_id,
        status=status_str,
        platforms=platform_results,
        total_platforms=len(platform_results),
        successful=successful,
        failed=failed,
        images_generated=images_generated,
        total_time=total_time
    )
