"""
iModels Pydantic Schemas
Request/Response schemas per gestione modelli AI
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import ModelProvider, ModelCapability


# ============================================================================
# AI MODEL SCHEMAS
# ============================================================================

class AIModelBase(BaseModel):
    """Schema base per AI Model."""
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    
    provider: ModelProvider
    model_id: str = Field(..., min_length=1, max_length=200)
    
    capabilities: List[ModelCapability] = Field(default_factory=list)
    
    config: Dict[str, Any] = Field(default_factory=dict)
    default_params: Dict[str, Any] = Field(default_factory=dict)
    
    context_window: int = Field(..., ge=1000)
    max_output_tokens: int = Field(..., ge=100)
    rpm_limit: Optional[int] = Field(None, ge=1)
    tpm_limit: Optional[int] = Field(None, ge=1000)
    
    input_price: Optional[int] = Field(None, ge=0)
    output_price: Optional[int] = Field(None, ge=0)
    
    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False)
    
    tags: List[str] = Field(default_factory=list)
    use_cases: List[str] = Field(default_factory=list)


class AIModelCreate(AIModelBase):
    """Schema per creazione AI Model."""
    pass


class AIModelUpdate(BaseModel):
    """Schema per aggiornamento AI Model."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    
    provider: Optional[ModelProvider] = None
    model_id: Optional[str] = Field(None, min_length=1, max_length=200)
    
    capabilities: Optional[List[ModelCapability]] = None
    
    config: Optional[Dict[str, Any]] = None
    default_params: Optional[Dict[str, Any]] = None
    
    context_window: Optional[int] = Field(None, ge=1000)
    max_output_tokens: Optional[int] = Field(None, ge=100)
    rpm_limit: Optional[int] = Field(None, ge=1)
    tpm_limit: Optional[int] = Field(None, ge=1000)
    
    input_price: Optional[int] = Field(None, ge=0)
    output_price: Optional[int] = Field(None, ge=0)
    
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    
    tags: Optional[List[str]] = None
    use_cases: Optional[List[str]] = None


class AIModelResponse(AIModelBase):
    """Schema response AI Model."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# MODEL EXECUTION SCHEMAS
# ============================================================================

class ModelExecutionRequest(BaseModel):
    """Request per esecuzione modello AI."""
    model_slug: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1)
    
    # Optional parameters (override model defaults)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    
    # Context
    system_message: Optional[str] = None
    chat_history: Optional[List[Dict[str, str]]] = None
    
    # RAG
    use_rag: bool = Field(default=False)
    rag_context: Optional[List[str]] = None
    
    # Metadata
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class ModelExecutionResponse(BaseModel):
    """Response esecuzione modello AI."""
    model_slug: str
    provider: ModelProvider
    
    # Output
    response: str
    finish_reason: str  # "stop", "length", "content_filter"
    
    # Usage
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
    # Cost (cents)
    cost: float
    
    # Metadata
    latency_ms: int
    created_at: datetime


# ============================================================================
# LIST SCHEMAS
# ============================================================================

class AIModelListResponse(BaseModel):
    """Response lista modelli."""
    items: List[AIModelResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
