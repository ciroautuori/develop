"""
Upload Router - API endpoints per upload immagini.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.domain.auth.admin_models import AdminUser
from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.infrastructure.database.session import get_db
from .upload_service import ImageUploadService
from .models import Project


router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/project-image")
async def upload_project_image(
    file: UploadFile = File(...),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Upload immagine progetto.

    Returns URLs per immagine e thumbnail.
    """
    result = await ImageUploadService.upload_project_image(file)
    return {
        "success": True,
        "data": result
    }


@router.post("/project/{project_id}/cover")
async def set_project_cover(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Upload e imposta cover image per progetto.
    """
    # Get project
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    # Upload image
    result = await ImageUploadService.upload_project_image(file)

    # Update project
    project.cover_image = result["image_url"]
    project.thumbnail_url = result["thumbnail_url"]
    db.commit()

    return {
        "success": True,
        "data": {
            "project_id": project_id,
            **result
        }
    }


@router.delete("/project/{project_id}/cover")
def delete_project_cover(
    project_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Rimuovi cover image da progetto.
    """
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    # Delete file if exists
    if project.cover_image:
        try:
            filename = project.cover_image.split("/")[-1]
            ImageUploadService.delete_image(filename)
        except Exception:
            pass  # File already deleted or missing

    # Clear DB fields
    project.cover_image = None
    project.thumbnail_url = None
    db.commit()

    return {
        "success": True,
        "message": "Cover image removed"
    }
