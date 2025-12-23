"""
MARKETTINA v2.0 - Media Upload Router
Handles file uploads for social media, content, etc.
"""
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.core.api.dependencies.auth_deps import get_current_admin_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["Media Upload"])

# Allowed file types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


class UploadResponse(BaseModel):
    """Upload response model"""
    success: bool
    url: str
    filename: str
    content_type: str
    size: int


@router.post("/image", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    folder: str = "general",
    current_user = Depends(get_current_admin_user)
):
    """
    Upload an image file.

    Supported formats: JPEG, PNG, GIF, WebP
    Max size: 50MB
    """
    # Validate content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )

    # Read file content
    content = await file.read()

    # Validate size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Generate unique filename
    ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    unique_filename = f"{uuid.uuid4().hex}{ext}"

    # Create upload directory
    upload_dir = Path("/app/uploads") / folder
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = upload_dir / unique_filename
    with open(file_path, "wb") as f:
        f.write(content)

    # Generate URL
    url = f"/uploads/{folder}/{unique_filename}"

    logger.info(f"Image uploaded: {url} by user {current_user.id}")

    return UploadResponse(
        success=True,
        url=url,
        filename=unique_filename,
        content_type=file.content_type,
        size=len(content)
    )


@router.post("/video", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    folder: str = "videos",
    current_user = Depends(get_current_admin_user)
):
    """
    Upload a video file.

    Supported formats: MP4, WebM, QuickTime
    Max size: 50MB
    """
    # Validate content type
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_VIDEO_TYPES)}"
        )

    # Read file content
    content = await file.read()

    # Validate size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Generate unique filename
    ext = Path(file.filename).suffix.lower() if file.filename else ".mp4"
    unique_filename = f"{uuid.uuid4().hex}{ext}"

    # Create upload directory
    upload_dir = Path("/app/uploads") / folder
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = upload_dir / unique_filename
    with open(file_path, "wb") as f:
        f.write(content)

    # Generate URL
    url = f"/uploads/{folder}/{unique_filename}"

    logger.info(f"Video uploaded: {url} by user {current_user.id}")

    return UploadResponse(
        success=True,
        url=url,
        filename=unique_filename,
        content_type=file.content_type,
        size=len(content)
    )
