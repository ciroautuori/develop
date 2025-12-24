from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.crud import partner as partner_crud
from app.database.database import get_db
from app.schemas.partner import PartnerCreate, PartnerResponse, PartnerUpdate, PartnerListResponse
from app.models.admin import AdminUser

router = APIRouter()

@router.get("/", response_model=PartnerListResponse)
async def get_partners(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Recupera la lista dei partner ISS."""
    partners = await partner_crud.get_partners(db, skip=skip, limit=limit, active_only=active_only)
    # Note: we need total for the response, let's get it from stats or a quick query
    stats = await partner_crud.get_stats(db)
    return {
        "partners": partners,
        "total": stats["total"],
        "skip": skip,
        "limit": limit
    }

@router.post("/", response_model=PartnerResponse, status_code=status.HTTP_201_CREATED)
async def create_partner(
    partner_in: PartnerCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Crea un nuovo partner (Admin solo)."""
    return await partner_crud.create_partner(db, partner_in=partner_in, user_id=current_admin.id)

@router.get("/{partner_id}", response_model=PartnerResponse)
async def get_partner(
    partner_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Recupera i dettagli di un partner specifico per ID."""
    partner = await partner_crud.get_partner_by_id(db, partner_id=partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner non trovato")
    return partner

@router.get("/slug/{slug}", response_model=PartnerResponse)
async def get_partner_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Recupera i dettagli di un partner tramite slug."""
    partner = await partner_crud.get_partner_by_slug(db, slug=slug)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner non trovato")
    return partner

@router.put("/{partner_id}", response_model=PartnerResponse)
async def update_partner(
    partner_id: int,
    partner_in: PartnerUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Aggiorna i dati di un partner (Admin solo)."""
    partner = await partner_crud.update_partner(db, partner_id=partner_id, partner_in=partner_in)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner non trovato")
    return partner

@router.delete("/{partner_id}")
async def delete_partner(
    partner_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Archivia un partner (Admin solo)."""
    success = await partner_crud.delete_partner(db, partner_id=partner_id)
    if not success:
        raise HTTPException(status_code=404, detail="Partner non trovato")
    return {"message": "Partner archiviato con successo"}
