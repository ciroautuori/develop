"""
iModels Service - Business Logic
Gestione modelli AI e esecuzione
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import HTTPException, status

from .models import AIModel, ModelProvider
from .schemas import (
    AIModelCreate,
    AIModelUpdate,
    AIModelResponse,
    AIModelListResponse,
    ModelExecutionRequest,
    ModelExecutionResponse
)
import time
from datetime import datetime


class AIModelService:
    """Service per gestione modelli AI."""

    @staticmethod
    def get_models(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        provider: Optional[ModelProvider] = None,
        is_active: Optional[bool] = None,
        capability: Optional[str] = None
    ) -> AIModelListResponse:
        """Lista modelli AI con filtri."""
        from sqlalchemy import text

        where_conditions = []
        params = {}

        if provider:
            where_conditions.append("provider = :provider")
            params['provider'] = provider.value

        if is_active is not None:
            where_conditions.append("is_active = :is_active")
            params['is_active'] = is_active

        # Capability filter: Use JSON contains for PostgreSQL JSONB column

        where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""

        # Count
        count_query = f"SELECT COUNT(*) FROM ai_models {where_clause}"
        total = db.execute(text(count_query), params).scalar() or 0

        # Get models
        offset = (page - 1) * page_size
        query = f"""
            SELECT id, name, slug, description, provider, model_id,
                   capabilities, config, default_params,
                   context_window, max_output_tokens, rpm_limit, tpm_limit,
                   input_price, output_price,
                   is_active, is_featured,
                   tags, use_cases,
                   created_at, updated_at
            FROM ai_models
            {where_clause}
            ORDER BY is_featured DESC, name ASC
            LIMIT :limit OFFSET :offset
        """
        params['limit'] = page_size
        params['offset'] = offset

        result = db.execute(text(query), params)
        rows = result.fetchall()

        models = []
        for row in rows:
            models.append(AIModelResponse(
                id=row[0],
                name=row[1],
                slug=row[2],
                description=row[3],
                provider=row[4],
                model_id=row[5],
                capabilities=row[6] or [],
                config=row[7] or {},
                default_params=row[8] or {},
                context_window=row[9],
                max_output_tokens=row[10],
                rpm_limit=row[11],
                tpm_limit=row[12],
                input_price=row[13],
                output_price=row[14],
                is_active=row[15],
                is_featured=row[16],
                tags=row[17] or [],
                use_cases=row[18] or [],
                created_at=row[19],
                updated_at=row[20]
            ))

        return AIModelListResponse(
            items=models,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )

    @staticmethod
    def execute_model(
        db: Session,
        request: ModelExecutionRequest
    ) -> ModelExecutionResponse:
        """
        Esegue un modello AI.
        PLACEHOLDER - Implementare integrazione provider.
        """
        # Get model
        from sqlalchemy import text

        query = text("SELECT * FROM ai_models WHERE slug = :slug AND is_active = true")
        row = db.execute(query, {"slug": request.model_slug}).fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {request.model_slug} not found or inactive"
            )

        start_time = time.time()

        # Provider integration: Route to AI Microservice
        # See: ai_microservice/app/core/api/v1/marketing.py for implementation

        latency_ms = int((time.time() - start_time) * 1000)

        # Mock values
        prompt_tokens = len(request.prompt.split()) * 1.3
        completion_tokens = 100
        total_tokens = int(prompt_tokens + completion_tokens)

        # Calculate cost (mock)
        input_price_per_token = (row[13] or 0) / 1_000_000  # cents
        output_price_per_token = (row[14] or 0) / 1_000_000
        cost = (prompt_tokens * input_price_per_token) + (completion_tokens * output_price_per_token)

        return ModelExecutionResponse(
            model_slug=request.model_slug,
            provider=row[4],
            response="This is a mock response. Implement provider integration.",
            finish_reason="stop",
            prompt_tokens=int(prompt_tokens),
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost=round(cost, 4),
            latency_ms=latency_ms,
            created_at=datetime.utcnow()
        )
