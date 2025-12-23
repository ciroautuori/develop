"""
A/B Testing API Router.

Endpoints per gestione test A/B marketing.
"""

import uuid

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.domain.marketing.ab_testing import (
    ABTest,
    TestStatus,
    TestType,
    Variant,
    ab_testing_service,
    create_cta_test,
    create_email_subject_test,
)

router = APIRouter(prefix="/ab-tests", tags=["A/B Testing"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class VariantCreate(BaseModel):
    name: str
    content: str
    traffic_percent: float = 50.0


class TestCreate(BaseModel):
    name: str
    description: str = ""
    test_type: TestType
    variants: list[VariantCreate]
    goal: str = "conversions"
    min_sample_size: int = 100
    confidence_level: float = 95.0
    auto_select_winner: bool = True


class QuickEmailTest(BaseModel):
    name: str
    subjects: list[str] = Field(..., min_items=2, max_items=5)


class QuickCTATest(BaseModel):
    name: str
    cta_texts: list[str] = Field(..., min_items=2, max_items=5)


class TrackEvent(BaseModel):
    variant_id: str
    event_type: str  # click, conversion, revenue
    value: float = 1.0


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/")
async def list_tests(status: str | None = None):
    """Lista tutti i test A/B."""
    status_enum = TestStatus(status) if status else None
    tests = ab_testing_service.list_tests(status_enum)
    return [ab_testing_service.get_test_summary(t.id) for t in tests]


@router.post("/")
async def create_test(data: TestCreate):
    """Crea nuovo test A/B."""
    # Validate traffic
    total = sum(v.traffic_percent for v in data.variants)
    if abs(total - 100.0) > 0.1:
        raise HTTPException(status_code=400, detail=f"Traffic must sum to 100%, got {total}")

    variants = [
        Variant(
            id=f"var_{uuid.uuid4().hex[:8]}",
            name=v.name,
            content=v.content,
            traffic_percent=v.traffic_percent
        )
        for v in data.variants
    ]

    test = ABTest(
        id=f"test_{uuid.uuid4().hex[:12]}",
        name=data.name,
        description=data.description,
        test_type=data.test_type,
        variants=variants,
        goal=data.goal,
        min_sample_size=data.min_sample_size,
        confidence_level=data.confidence_level,
        auto_select_winner=data.auto_select_winner
    )

    created = ab_testing_service.create_test(test)
    return ab_testing_service.get_test_summary(created.id)


@router.post("/quick/email-subject")
async def create_quick_email_test(data: QuickEmailTest):
    """Crea rapidamente test A/B per oggetto email."""
    test = create_email_subject_test(data.name, data.subjects)
    created = ab_testing_service.create_test(test)
    return ab_testing_service.get_test_summary(created.id)


@router.post("/quick/cta")
async def create_quick_cta_test(data: QuickCTATest):
    """Crea rapidamente test A/B per CTA button."""
    test = create_cta_test(data.name, data.cta_texts)
    created = ab_testing_service.create_test(test)
    return ab_testing_service.get_test_summary(created.id)


@router.get("/{test_id}")
async def get_test(test_id: str):
    """Ottieni dettagli test."""
    test = ab_testing_service.get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return ab_testing_service.get_test_summary(test_id)


@router.delete("/{test_id}")
async def delete_test(test_id: str):
    """Elimina test."""
    if not ab_testing_service.delete_test(test_id):
        raise HTTPException(status_code=404, detail="Test not found")
    return {"status": "deleted", "id": test_id}


@router.post("/{test_id}/start")
async def start_test(test_id: str):
    """Avvia test."""
    if not ab_testing_service.start_test(test_id):
        raise HTTPException(status_code=400, detail="Cannot start test")
    return {"status": "running", "id": test_id}


@router.post("/{test_id}/pause")
async def pause_test(test_id: str):
    """Pausa test."""
    if not ab_testing_service.pause_test(test_id):
        raise HTTPException(status_code=400, detail="Cannot pause test")
    return {"status": "paused", "id": test_id}


@router.post("/{test_id}/stop")
async def stop_test(test_id: str):
    """Termina test e calcola vincitore."""
    if not ab_testing_service.stop_test(test_id):
        raise HTTPException(status_code=400, detail="Cannot stop test")
    return ab_testing_service.get_test_summary(test_id)


@router.get("/{test_id}/variant")
async def get_variant(test_id: str, user_id: str = Query(...)):
    """Ottieni variante per utente (per mostrare contenuto test)."""
    variant = ab_testing_service.get_variant_for_user(test_id, user_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Test not active or not found")
    return {
        "variant_id": variant.id,
        "variant_name": variant.name,
        "content": variant.content
    }


@router.post("/{test_id}/track")
async def track_event(test_id: str, data: TrackEvent):
    """Traccia evento per variante."""
    ab_testing_service.track_event(test_id, data.variant_id, data.event_type, data.value)
    return {"status": "tracked"}


@router.get("/{test_id}/results")
async def get_results(test_id: str):
    """Ottieni risultati analisi test."""
    result = ab_testing_service.analyze_test(test_id)
    return {
        "test_id": result.test_id,
        "winner": result.winner.model_dump() if result.winner else None,
        "confidence": result.confidence,
        "statistical_significance": result.statistical_significance,
        "lift_percent": result.lift_percent,
        "p_value": result.p_value,
        "sample_size_reached": result.sample_size_reached,
        "recommendation": result.recommendation
    }


# ============================================================================
# TEST TYPES INFO
# ============================================================================

@router.get("/meta/types")
async def get_test_types():
    """Lista tipi di test disponibili."""
    return [
        {"value": "email_subject", "label": "📧 Oggetto Email"},
        {"value": "email_content", "label": "📝 Contenuto Email"},
        {"value": "landing_page", "label": "🖥️ Landing Page"},
        {"value": "cta_button", "label": "🔘 CTA Button"},
        {"value": "social_post", "label": "📱 Post Social"},
        {"value": "ad_copy", "label": "📢 Testo Ads"},
    ]


@router.get("/meta/goals")
async def get_goals():
    """Lista goal disponibili."""
    return [
        {"value": "conversions", "label": "Conversioni"},
        {"value": "clicks", "label": "Click"},
        {"value": "revenue", "label": "Revenue"},
    ]
