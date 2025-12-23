from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.crud import volunteer
from app.database.database import get_db
from app.schemas.volunteer import VolunteerApplicationCreate, VolunteerApplicationRead
from app.models.admin import AdminUser

router = APIRouter()


@router.post("/", response_model=VolunteerApplicationRead)
async def submit_volunteer_application(
    application_data: VolunteerApplicationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Submit a new volunteer application (public endpoint)."""
    return await volunteer.create_volunteer_application(db, application=application_data)


@router.get("/", response_model=List[VolunteerApplicationRead])
async def get_volunteer_applications(
    skip: int = 0,
    limit: int = 12,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Retrieve all volunteer applications (protected endpoint)."""
    applications = await volunteer.get_volunteer_applications(db, skip=skip, limit=limit)
    return applications


@router.get("/{application_id}", response_model=VolunteerApplicationRead)
async def get_volunteer_application(
    application_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Retrieve a volunteer application by ID (protected endpoint)."""
    application = await volunteer.get_volunteer_application_by_id(db, application_id=application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer application not found"
        )
    return application
