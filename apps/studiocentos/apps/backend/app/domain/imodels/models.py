"""
iModels Database Models
Definisce i modelli SQLAlchemy per la gestione AI models
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.infrastructure.database import Base
import enum


class ModelProvider(str, enum.Enum):
    """Provider di modelli AI supportati."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    META = "meta"
    GOOGLE = "google"
    MISTRAL = "mistral"
    CUSTOM = "custom"


class ModelCapability(str, enum.Enum):
    """Capabilities dei modelli AI."""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    CHAT = "chat"
    EMBEDDINGS = "embeddings"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ANALYSIS = "image_analysis"
    FUNCTION_CALLING = "function_calling"
    RAG = "rag"
    AGENTS = "agents"


class AIModel(Base):
    """
    Modello AI - Gestione centralizzata modelli.
    
    Supporta GPT-4, Claude, Llama, Gemini, Mistral e custom models.
    """
    __tablename__ = "ai_models"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Model info
    name = Column(String(200), nullable=False, unique=True, index=True)
    slug = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    
    # Provider
    provider = Column(SQLEnum(ModelProvider), nullable=False)
    model_id = Column(String(200), nullable=False)  # es: "gpt-4-turbo", "claude-3-opus"
    
    # Capabilities
    capabilities = Column(JSON, nullable=False, default=list)  # List[ModelCapability]
    
    # Configuration
    config = Column(JSON, nullable=False, default=dict)  # API keys, endpoints, parameters
    default_params = Column(JSON, nullable=False, default=dict)  # temperature, max_tokens, etc
    
    # Limits
    context_window = Column(Integer, nullable=False)  # Max context tokens
    max_output_tokens = Column(Integer, nullable=False)  # Max output tokens
    rpm_limit = Column(Integer, nullable=True)  # Requests per minute
    tpm_limit = Column(Integer, nullable=True)  # Tokens per minute
    
    # Pricing (per 1M tokens)
    input_price = Column(Integer, nullable=True)  # cents per 1M input tokens
    output_price = Column(Integer, nullable=True)  # cents per 1M output tokens
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    is_featured = Column(Boolean, nullable=False, default=False)
    
    # Metadata
    tags = Column(JSON, nullable=False, default=list)  # ["fast", "cheap", "powerful"]
    use_cases = Column(JSON, nullable=False, default=list)  # ["chat", "code", "analysis"]
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<AIModel {self.name} ({self.provider})>"
