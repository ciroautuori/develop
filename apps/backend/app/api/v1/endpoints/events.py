from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from app.api.deps import get_current_admin
from app.crud import event
from app.database.database import get_db
from app.schemas.event import EventCreate, EventRead, EventUpdate
from app.models.admin import AdminUser

router = APIRouter()


@router.get("/", response_model=List[EventRead])
@cache(expire=600)
async def get_events(
    skip: int = 0,
    limit: int = 12,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all future events (public endpoint)."""
    events = await event.get_events(db, skip=skip, limit=limit)
    return events


@router.get("/{slug}", response_model=EventRead)
@cache(expire=300)
async def get_event_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve an event by slug (public endpoint)."""
    db_event = await event.get_event_by_slug(db, slug=slug)
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return db_event


@router.post("/", response_model=EventRead)
async def create_event(
    event_data: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Create a new event (protected endpoint)."""
    return await event.create_event(db, event=event_data)


@router.put("/{event_id}", response_model=EventRead)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Update an event (protected endpoint)."""
    db_event = await event.update_event(db, event_id=event_id, event_update=event_data)
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return db_event


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Delete an event (protected endpoint)."""
    success = await event.delete_event(db, event_id=event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return {"message": "Event deleted successfully"}
