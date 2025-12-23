from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


async def get_projects(db: AsyncSession, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Project]:
    query = select(Project)
    if active_only:
        query = query.where(Project.is_active == True)
    query = query.offset(skip).limit(limit).order_by(Project.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def get_project_by_slug(db: AsyncSession, slug: str) -> Optional[Project]:
    query = select(Project).where(Project.slug == slug, Project.is_active == True)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_project_by_id(db: AsyncSession, project_id: int) -> Optional[Project]:
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_project(db: AsyncSession, project: ProjectCreate) -> Project:
    db_project = Project(**project.model_dump())
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project


async def update_project(db: AsyncSession, project_id: int, project_update: ProjectUpdate) -> Optional[Project]:
    db_project = await get_project_by_id(db, project_id)
    if not db_project:
        return None
    
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    await db.commit()
    await db.refresh(db_project)
    return db_project


async def delete_project(db: AsyncSession, project_id: int) -> bool:
    db_project = await get_project_by_id(db, project_id)
    if not db_project:
        return False
    
    await db.delete(db_project)
    await db.commit()
    return True
