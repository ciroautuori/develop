"""
Lead Enrichment Router - API per arricchimento e ricerca lead.

Endpoints:
- POST /leads/search/places - Cerca aziende su Google Places
- POST /leads/{id}/enrich - Arricchisci singolo lead
- POST /leads/bulk-enrich - Arricchisci multipli lead
- GET /leads/{id}/score - Calcola score lead
"""


import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.core.api.dependencies.database import get_db
from app.domain.auth.admin_models import AdminUser

from .lead_enrichment_service import LeadEnrichmentService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/leads", tags=["Lead Enrichment"])


# ============================================================================
# SCHEMAS
# ============================================================================

class PlacesSearchRequest(BaseModel):
    """Request per ricerca Google Places."""
    query: str = Field(..., min_length=2, description="Nome azienda o tipo business")
    location: str | None = Field(None, description="Città/regione (es. 'Salerno, Italia')")
    radius_km: int = Field(50, ge=5, le=200, description="Raggio ricerca in km")
    industry: str | None = Field(None, description="Settore per filtraggio")


class PlaceResult(BaseModel):
    """Risultato singola azienda."""
    place_id: str
    name: str
    address: str
    phone: str | None
    website: str | None
    rating: float | None
    reviews_count: int
    status: str
    types: list[str]
    primary_type: str | None
    maps_url: str
    source: str


class PlacesSearchResponse(BaseModel):
    """Response ricerca Places."""
    results: list[PlaceResult]
    total: int
    query: str
    location: str | None


class EnrichmentResult(BaseModel):
    """Risultato arricchimento lead."""
    lead_id: int
    enriched_data: dict
    enrichment_sources: dict
    enriched_at: str


class BulkEnrichRequest(BaseModel):
    """Request arricchimento bulk."""
    lead_ids: list[int] = Field(..., min_length=1, max_length=100)


class BulkEnrichResponse(BaseModel):
    """Response arricchimento bulk."""
    total: int
    enriched: int
    failed: int
    results: dict


class LeadScoreResponse(BaseModel):
    """Response score lead."""
    lead_id: int
    score: int
    grade: str
    breakdown: dict
    recommendation: str
    calculated_at: str


class SavePlaceAsLeadRequest(BaseModel):
    """Request per salvare un place come lead."""
    place_id: str
    name: str
    address: str
    phone: str | None = None
    website: str | None = None
    rating: float | None = None
    reviews_count: int = 0
    industry: str | None = None
    notes: str | None = None
    tags: list[str] = []


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/search/places", response_model=PlacesSearchResponse)
async def search_google_places(
    request: PlacesSearchRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Cerca aziende su Google Places API.

    Permette di trovare potenziali lead cercando per:
    - Nome azienda
    - Tipo di business (es. "ristorante", "avvocato")
    - Località

    Ritorna info complete: nome, indirizzo, telefono, website, rating.
    """
    service = LeadEnrichmentService(db)

    try:
        results = await service.search_google_places(
            query=request.query,
            location=request.location,
            radius_km=request.radius_km
        )

        # Filter by industry if provided
        if request.industry:
            industry_lower = request.industry.lower()
            results = [
                r for r in results
                if industry_lower in r.get("primary_type", "").lower()
                or any(industry_lower in t.lower() for t in r.get("types", []))
            ]

        return PlacesSearchResponse(
            results=[PlaceResult(**r) for r in results],
            total=len(results),
            query=request.query,
            location=request.location
        )

    except Exception as e:
        logger.error("places_search_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore ricerca: {e!s}"
        )
    finally:
        await service.close()


@router.post("/{lead_id}/enrich", response_model=EnrichmentResult)
async def enrich_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Arricchisci un lead con dati esterni.

    Fonti:
    - Google Places (telefono, indirizzo, rating)
    - Clearbit Logo (logo aziendale)
    - Hunter.io (email discovery, se configurato)
    - AI Scoring (valutazione lead)

    Aggiorna automaticamente il lead nel database.
    """
    service = LeadEnrichmentService(db)

    try:
        result = await service.enrich_lead(lead_id)
        return EnrichmentResult(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error("enrich_lead_error", lead_id=lead_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore arricchimento: {e!s}"
        )
    finally:
        await service.close()


@router.post("/bulk-enrich", response_model=BulkEnrichResponse)
async def bulk_enrich_leads(
    request: BulkEnrichRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Arricchisci multipli lead in parallelo.

    Max 100 lead per richiesta.
    Esegue fino a 5 arricchimenti in parallelo.
    """
    service = LeadEnrichmentService(db)

    try:
        result = await service.bulk_enrich_leads(request.lead_ids)
        return BulkEnrichResponse(**result)

    except Exception as e:
        logger.error("bulk_enrich_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore bulk enrichment: {e!s}"
        )
    finally:
        await service.close()


@router.get("/{lead_id}/score", response_model=LeadScoreResponse)
async def get_lead_score(
    lead_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Calcola e ritorna lo score di un lead.

    Score 0-100 basato su:
    - Completezza dati (25%)
    - Presenza online (20%)
    - Reputazione (15%)
    - Settore target (20%)
    - Località (20%)

    Gradi: A (80+), B (60-79), C (40-59), D (<40)
    """
    from sqlalchemy import text

    # Get lead data
    query = text("""
        SELECT id, company_name, contact_name, email, phone, website,
               city, region, address, industry, score, custom_fields
        FROM leads WHERE id = :lead_id
    """)
    row = db.execute(query, {"lead_id": lead_id}).fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead {lead_id} non trovato"
        )

    lead_data = {
        "id": row[0],
        "company_name": row[1],
        "contact_name": row[2],
        "email": row[3],
        "phone": row[4],
        "website": row[5],
        "city": row[6],
        "region": row[7],
        "address": row[8],
        "industry": row[9]
    }

    # Check for cached enrichment data
    custom_fields = row[11] or {}
    if isinstance(custom_fields, str):
        import json
        custom_fields = json.loads(custom_fields)

    if "google_places" in custom_fields:
        places_data = custom_fields["google_places"]
        lead_data["rating"] = places_data.get("rating")
        lead_data["reviews_count"] = places_data.get("reviews_count")
        lead_data["types"] = places_data.get("types", [])

    service = LeadEnrichmentService(db)

    try:
        score_result = await service.calculate_lead_score(lead_data)

        return LeadScoreResponse(
            lead_id=lead_id,
            score=score_result["score"],
            grade=score_result["grade"],
            breakdown=score_result["breakdown"],
            recommendation=score_result["recommendation"],
            calculated_at=score_result["calculated_at"]
        )

    finally:
        await service.close()


@router.post("/save-from-place")
async def save_place_as_lead(
    request: SavePlaceAsLeadRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Salva un risultato Google Places come nuovo lead nel CRM.

    Estrae automaticamente città/regione dall'indirizzo.
    Calcola score iniziale.
    """
    import json

    from sqlalchemy import text

    # Parse address for city/region
    address_parts = request.address.split(",") if request.address else []
    city = ""
    region = ""

    if len(address_parts) >= 2:
        # Typical format: "Via XXX, 84100 Salerno SA, Italia"
        for part in address_parts:
            part = part.strip()
            # Check for Italian cities
            if any(c in part.lower() for c in ["salerno", "napoli", "roma", "milano"]):
                city = part.split()[-2] if len(part.split()) > 1 else part
            if "italia" in part.lower():
                continue
            # Check for CAP + city pattern
            if any(char.isdigit() for char in part):
                parts = part.split()
                if len(parts) >= 2:
                    city = parts[-2] if len(parts) > 2 else parts[-1]

    # Check for existing lead by name
    check_query = text("""
        SELECT id FROM leads
        WHERE company_name ILIKE :name
        LIMIT 1
    """)
    existing = db.execute(check_query, {"name": f"%{request.name}%"}).fetchone()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lead con nome simile già esistente (ID: {existing[0]})"
        )

    # Insert new lead
    insert_query = text("""
        INSERT INTO leads (
            company_name, email, phone, website,
            city, region, address,
            source, status,
            industry, notes, tags, custom_fields, score,
            created_at, updated_at
        ) VALUES (
            :company_name, :email, :phone, :website,
            :city, :region, :address,
            'GOOGLE_MAPS', 'NEW',
            :industry, :notes, :tags, :custom_fields, 0,
            NOW(), NOW()
        ) RETURNING id
    """)

    custom_fields = {
        "place_id": request.place_id,
        "rating": request.rating,
        "reviews_count": request.reviews_count,
        "source_search": "google_places",
        "imported_at": None  # Will be set below
    }

    from datetime import datetime
    custom_fields["imported_at"] = datetime.utcnow().isoformat()

    result = db.execute(insert_query, {
        "company_name": request.name,
        "email": None,  # Will be enriched later
        "phone": request.phone,
        "website": request.website,
        "city": city or None,
        "region": region or "Campania",  # Default
        "address": request.address,
        "industry": request.industry,
        "notes": request.notes,
        "tags": json.dumps(request.tags),
        "custom_fields": json.dumps(custom_fields)
    })

    lead_id = result.scalar()
    db.commit()

    logger.info("lead_saved_from_place", lead_id=lead_id, place_id=request.place_id)

    return {
        "success": True,
        "lead_id": lead_id,
        "message": f"Lead '{request.name}' salvato con successo"
    }


@router.get("/enrichment/stats")
async def get_enrichment_stats(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Statistiche arricchimento lead.

    Mostra:
    - Lead totali
    - Lead arricchiti
    - Distribuzione score
    - Lead per fonte
    """
    from sqlalchemy import text

    stats_query = text("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN score > 0 THEN 1 END) as enriched,
            COUNT(CASE WHEN score >= 80 THEN 1 END) as grade_a,
            COUNT(CASE WHEN score >= 60 AND score < 80 THEN 1 END) as grade_b,
            COUNT(CASE WHEN score >= 40 AND score < 60 THEN 1 END) as grade_c,
            COUNT(CASE WHEN score < 40 AND score > 0 THEN 1 END) as grade_d,
            COUNT(CASE WHEN source = 'GOOGLE_MAPS' THEN 1 END) as from_places,
            COUNT(CASE WHEN source = 'MANUAL' THEN 1 END) as from_manual,
            COUNT(CASE WHEN source = 'WEBSITE' THEN 1 END) as from_website,
            AVG(score) FILTER (WHERE score > 0) as avg_score
        FROM leads
    """)

    row = db.execute(stats_query).fetchone()

    return {
        "total_leads": row[0] or 0,
        "enriched_leads": row[1] or 0,
        "enrichment_rate": round((row[1] or 0) / max(row[0] or 1, 1) * 100, 1),
        "score_distribution": {
            "A": row[2] or 0,
            "B": row[3] or 0,
            "C": row[4] or 0,
            "D": row[5] or 0
        },
        "sources": {
            "google_maps": row[6] or 0,
            "manual": row[7] or 0,
            "website": row[8] or 0
        },
        "average_score": round(row[9] or 0, 1)
    }


@router.get("/stats")
async def get_lead_conversion_stats(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Statistiche complete conversione lead.

    Per il Marketing Hub Pro:
    - Lead trovati totali
    - Salvati nel CRM
    - Convertiti in clienti
    - Rifiutati
    - Rate conversione
    - Breakdown per settore e città
    """
    from sqlalchemy import text

    # Get leads stats
    leads_query = text("""
        SELECT
            COUNT(*) as total_found,
            COUNT(CASE WHEN status = 'CONTACTED' THEN 1 END) as contacted,
            COUNT(CASE WHEN status = 'QUALIFIED' THEN 1 END) as qualified,
            COUNT(CASE WHEN status = 'PROPOSAL_SENT' THEN 1 END) as proposal_sent,
            COUNT(CASE WHEN status = 'WON' THEN 1 END) as won,
            COUNT(CASE WHEN status = 'LOST' THEN 1 END) as lost,
            COUNT(CASE WHEN status = 'NEW' THEN 1 END) as pending
        FROM leads
    """)

    leads_row = db.execute(leads_query).fetchone()

    # Get customers from advertising source (lead finder)
    customers_query = text("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN status = 'active' THEN 1 END) as active,
            COUNT(CASE WHEN status = 'lead' THEN 1 END) as leads,
            COUNT(CASE WHEN status = 'churned' THEN 1 END) as churned
        FROM customers
        WHERE source = 'advertising'
    """)

    cust_row = db.execute(customers_query).fetchone()

    # Get by industry
    industry_query = text("""
        SELECT
            industry,
            COUNT(*) as total,
            COUNT(CASE WHEN status = 'WON' THEN 1 END) as converted,
            COUNT(CASE WHEN status = 'LOST' THEN 1 END) as rejected
        FROM leads
        WHERE industry IS NOT NULL
        GROUP BY industry
        ORDER BY total DESC
        LIMIT 10
    """)

    industry_rows = db.execute(industry_query).fetchall()

    # Get by city
    city_query = text("""
        SELECT
            city,
            COUNT(*) as total,
            COUNT(CASE WHEN status = 'WON' THEN 1 END) as converted
        FROM leads
        WHERE city IS NOT NULL
        GROUP BY city
        ORDER BY total DESC
        LIMIT 10
    """)

    city_rows = db.execute(city_query).fetchall()

    # Recent leads
    recent_query = text("""
        SELECT id, company_name, status, created_at
        FROM leads
        ORDER BY created_at DESC
        LIMIT 5
    """)

    recent_rows = db.execute(recent_query).fetchall()

    total_found = leads_row[0] or 0
    converted = leads_row[4] or 0
    saved_to_crm = cust_row[0] or 0

    return {
        "total_found": total_found,
        "saved_to_crm": saved_to_crm,
        "email_campaigns_sent": db.execute(text("SELECT count(*) FROM email_campaigns WHERE status = 'SENT'")).scalar() or 0,
        "converted_to_customer": converted,
        "rejected": leads_row[5] or 0,
        "pending": leads_row[6] or 0,
        "conversion_rate": round((converted / max(total_found, 1)) * 100, 1),
        "by_industry": {
            row[0]: {"total": row[1], "converted": row[2], "rejected": row[3]}
            for row in industry_rows
        },
        "by_city": {
            row[0]: {"total": row[1], "converted": row[2]}
            for row in city_rows
        },
        "recent_leads": [
            {
                "id": row[0],
                "company": row[1],
                "status": row[2],
                "created_at": row[3].isoformat() if row[3] else None
            }
            for row in recent_rows
        ]
    }
