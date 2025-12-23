from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from app.api.deps import get_current_admin
from app.crud import project
from app.database.database import get_db
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.models.admin import AdminUser

router = APIRouter()


@router.get("/", response_model=List[ProjectRead])
@cache(expire=600)
async def get_projects(
    skip: int = 0,
    limit: int = 12,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all active projects (public endpoint)."""
    projects = await project.get_projects(db, skip=skip, limit=limit)
    return projects


@router.get("/{slug}", response_model=ProjectRead)
@cache(expire=300)
async def get_project_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve a project by slug (public endpoint)."""
    db_project = await project.get_project_by_slug(db, slug=slug)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return db_project


@router.post("/", response_model=ProjectRead)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Create a new project (protected endpoint)."""
    return await project.create_project(db, project=project_data)


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Update a project (protected endpoint)."""
    db_project = await project.update_project(db, project_id=project_id, project_update=project_data)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return db_project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Delete a project (protected endpoint)."""
    success = await project.delete_project(db, project_id=project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return {"message": "Project deleted successfully"}
