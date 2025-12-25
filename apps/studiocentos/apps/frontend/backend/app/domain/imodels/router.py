"""
iModels Router - API Endpoints
Gestione modelli AI + Execution
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.api.dependencies.database import get_db
from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.domain.auth.admin_models import AdminUser

from .schemas import (
    AIModelCreate,
    AIModelUpdate,
    AIModelResponse,
    AIModelListResponse,
    ModelExecutionRequest,
    ModelExecutionResponse
)
from .service import AIModelService
from .models import ModelProvider

router = APIRouter(prefix="/api/v1/imodels", tags=["imodels"])


# ============================================================================
# ADMIN ENDPOINTS (Protected)
# ============================================================================

@router.post("/models", response_model=AIModelResponse)
def create_model(
    data: AIModelCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Crea nuovo modello AI (Admin only)."""
    return AIModelService.create_model(db=db, data=data)


@router.get("/models", response_model=AIModelListResponse)
def list_models(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    provider: Optional[ModelProvider] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Lista modelli AI disponibili."""
    return AIModelService.get_models(
        db=db,
        page=page,
        page_size=page_size,
        provider=provider,
        is_active=is_active
    )


@router.get("/models/{model_id}", response_model=AIModelResponse)
def get_model(
    model_id: int,
    db: Session = Depends(get_db)
):
    """Ottieni dettagli modello."""
    return AIModelService.get_model(db=db, model_id=model_id)


# ============================================================================
# EXECUTION ENDPOINTS (Public con auth)
# ============================================================================

@router.post("/execute", response_model=ModelExecutionResponse)
def execute_model(
    request: ModelExecutionRequest,
    db: Session = Depends(get_db)
):
    """
    Esegue un modello AI.

    Supporta:
    - GROQ (llama-3.3-70b-versatile)
    - OpenRouter (:free models)
    - Google Gemini (gemini-2.0-flash-exp)
    - HuggingFace (DeepSeek-V3)
    """
    return AIModelService.execute_model(db=db, request=request)
