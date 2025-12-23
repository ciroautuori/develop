"""
Brand DNA Router - API Endpoints
Persistenza e gestione identità brand per AI agents.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.core.api.dependencies.database import get_db
from app.domain.auth.admin_models import AdminUser

from .models import BrandSettings
from .schemas import BrandSettingsCreate, BrandSettingsResponse, BrandSettingsUpdate

router = APIRouter(tags=["brand-dna"])


# ============================================================================
# BRAND DNA ENDPOINTS
# ============================================================================

@router.get("/brand-dna", response_model=Optional[BrandSettingsResponse])
def get_brand_dna(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Ottieni Brand DNA per l'admin corrente.
    Restituisce null se non ancora configurato.
    """
    brand = db.query(BrandSettings).filter(
        BrandSettings.admin_id == admin.id
    ).first()

    return brand


@router.post("/brand-dna", response_model=BrandSettingsResponse)
def create_or_update_brand_dna(
    data: BrandSettingsCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Crea o aggiorna Brand DNA.
    Upsert: se esiste aggiorna, altrimenti crea.
    """
    # Check if already exists
    existing = db.query(BrandSettings).filter(
        BrandSettings.admin_id == admin.id
    ).first()

    if existing:
        # Update existing
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing
    # Create new
    brand = BrandSettings(
        admin_id=admin.id,
        **data.model_dump()
    )
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


@router.patch("/brand-dna", response_model=BrandSettingsResponse)
def patch_brand_dna(
    data: BrandSettingsUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Aggiornamento parziale Brand DNA.
    Solo i campi forniti vengono aggiornati.
    """
    brand = db.query(BrandSettings).filter(
        BrandSettings.admin_id == admin.id
    ).first()

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand DNA non trovato. Usa POST per creare."
        )

    # Update only provided fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(brand, field, value)

    db.commit()
    db.refresh(brand)
    return brand


@router.delete("/brand-dna", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand_dna(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Elimina Brand DNA.
    """
    brand = db.query(BrandSettings).filter(
        BrandSettings.admin_id == admin.id
    ).first()

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand DNA non trovato."
        )

    db.delete(brand)
    db.commit()


@router.get("/brand-dna/ai-context")
def get_brand_dna_for_ai(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Restituisce Brand DNA formattato per contesto AI.
    Ottimizzato per essere passato agli agenti AI come system prompt.
    """
    brand = db.query(BrandSettings).filter(
        BrandSettings.admin_id == admin.id
    ).first()

    if not brand:
        return {
            "context": None,
            "message": "Brand DNA non configurato. Vai su Settings per configurarlo."
        }

    # Format for AI context
    ai_context = f"""
## BRAND IDENTITY: {brand.company_name or 'Non specificato'}

### Tagline
{brand.tagline or 'Non definito'}

### Descrizione
{brand.description or 'Non definita'}

### Tone of Voice
{brand.tone_of_voice.value.upper()}

### Target Audience
{brand.target_audience or 'Non definito'}

### Unique Value Proposition
{brand.unique_value_proposition or 'Non definita'}

### Keywords Principali
{', '.join(brand.keywords) if brand.keywords else 'Nessuna'}

### Valori Aziendali
{', '.join(brand.values) if brand.values else 'Nessuno'}

### Content Pillars
{', '.join(brand.content_pillars) if brand.content_pillars else 'Nessuno'}

### Hashtag Preferiti
{', '.join(brand.preferred_hashtags) if brand.preferred_hashtags else 'Nessuno'}

### Parole da EVITARE
{', '.join(brand.forbidden_words) if brand.forbidden_words else 'Nessuna restrizione'}

### AI Persona
{brand.ai_persona or 'Usa un tono professionale e competente.'}
"""

    return {
        "context": ai_context.strip(),
        "brand_name": brand.company_name,
        "tone": brand.tone_of_voice.value,
        "colors": {
            "primary": brand.primary_color,
            "secondary": brand.secondary_color,
            "accent": brand.accent_color
        }
    }
