"""
iModels Domain - AI Model Management System
Gestione centralizzata modelli AI: GPT-4, Claude, Llama, Custom
"""

from .models import AIModel, ModelProvider, ModelCapability
from .schemas import (
    AIModelCreate,
    AIModelUpdate,
    AIModelResponse,
    ModelExecutionRequest,
    ModelExecutionResponse
)
from .service import AIModelService
from .router import router

__all__ = [
    # Models
    'AIModel',
    'ModelProvider',
    'ModelCapability',
    # Schemas
    'AIModelCreate',
    'AIModelUpdate',
    'AIModelResponse',
    'ModelExecutionRequest',
    'ModelExecutionResponse',
    # Service
    'AIModelService',
    # Router
    'router',
]
