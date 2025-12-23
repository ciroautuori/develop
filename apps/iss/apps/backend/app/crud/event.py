from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate


async def get_events(db: AsyncSession, skip: int = 0, limit: int = 100, future_only: bool = True) -> List[Event]:
    query = select(Event).where(Event.is_active == True)
    if future_only:
        query = query.where(Event.event_date >= datetime.now())
    query = query.offset(skip).limit(limit).order_by(Event.event_date.asc())
    result = await db.execute(query)
    return result.scalars().all()


async def get_event_by_slug(db: AsyncSession, slug: str) -> Optional[Event]:
    query = select(Event).where(Event.slug == slug, Event.is_active == True)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_event_by_id(db: AsyncSession, event_id: int) -> Optional[Event]:
    query = select(Event).where(Event.id == event_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_event(db: AsyncSession, event: EventCreate) -> Event:
    db_event = Event(**event.model_dump())
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event


async def update_event(db: AsyncSession, event_id: int, event_update: EventUpdate) -> Optional[Event]:
    db_event = await get_event_by_id(db, event_id)
    if not db_event:
        return None
    
    update_data = event_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_event, field, value)
    
    await db.commit()
    await db.refresh(db_event)
    return db_event


async def delete_event(db: AsyncSession, event_id: int) -> bool:
    db_event = await get_event_by_id(db, event_id)
    if not db_event:
        return False
    
    await db.delete(db_event)
    await db.commit()
    return True
