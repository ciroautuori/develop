from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.partner import Partner, PartnerStato
from app.schemas.partner import PartnerCreate, PartnerUpdate
import uuid

async def get_partners(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = False
) -> List[Partner]:
    query = select(Partner).where(Partner.archiviato == False)
    if active_only:
        query = query.where(Partner.stato == PartnerStato.ATTIVA)
    query = query.offset(skip).limit(limit).order_by(Partner.nome_organizzazione.asc())
    result = await db.execute(query)
    return result.scalars().all()

async def get_partner_by_id(db: AsyncSession, partner_id: int) -> Optional[Partner]:
    query = select(Partner).where(Partner.id == partner_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_partner_by_slug(db: AsyncSession, slug: str) -> Optional[Partner]:
    query = select(Partner).where(Partner.slug == slug)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_partner(db: AsyncSession, partner_in: PartnerCreate, user_id: Optional[int] = None) -> Partner:
    obj_data = partner_in.model_dump()
    # Generate a unique code if not provided
    if not obj_data.get("codice_partner"):
        obj_data["codice_partner"] = f"ISS-PTR-{uuid.uuid4().hex[:8].upper()}"
    
    # Generate slug if not provided
    if not obj_data.get("slug"):
        obj_data["slug"] = obj_data["nome_organizzazione"].lower().replace(" ", "-")
        
    db_obj = Partner(**obj_data, creato_da_user_id=user_id)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_partner(
    db: AsyncSession, 
    partner_id: int, 
    partner_in: PartnerUpdate
) -> Optional[Partner]:
    db_obj = await get_partner_by_id(db, partner_id)
    if not db_obj:
        return None
    
    update_data = partner_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_partner(db: AsyncSession, partner_id: int) -> bool:
    db_obj = await get_partner_by_id(db, partner_id)
    if not db_obj:
        return False
    
    # Soft delete
    db_obj.archiviato = True
    await db.commit()
    return True

async def get_stats(db: AsyncSession):
    total = await db.execute(select(func.count(Partner.id)).where(Partner.archiviato == False))
    active = await db.execute(select(func.count(Partner.id)).where(Partner.stato == PartnerStato.ATTIVA, Partner.archiviato == False))
    
    return {
        "total": total.scalar() or 0,
        "active": active.scalar() or 0
    }
