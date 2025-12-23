from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.volunteer import VolunteerApplication
from app.schemas.volunteer import VolunteerApplicationCreate


async def get_volunteer_applications(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[VolunteerApplication]:
    query = select(VolunteerApplication).offset(skip).limit(limit).order_by(VolunteerApplication.submitted_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def get_volunteer_application_by_id(db: AsyncSession, application_id: int) -> Optional[VolunteerApplication]:
    query = select(VolunteerApplication).where(VolunteerApplication.id == application_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_volunteer_application(db: AsyncSession, application: VolunteerApplicationCreate) -> VolunteerApplication:
    db_application = VolunteerApplication(**application.model_dump())
    db.add(db_application)
    await db.commit()
    await db.refresh(db_application)
    return db_application
