"""
Vector Store Data Models.

Pydantic models for documents, search results, and filters.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    Document for vector storage.
    
    Attributes:
        id: Unique document identifier
        text: Document text content
        embedding: Optional pre-computed embedding vector
        metadata: Additional document metadata
        created_at: Document creation timestamp
    """

    id: str = Field(..., description="Unique document identifier")
    text: str = Field(..., description="Document text content")
    embedding: list[float] | None = Field(
        default=None, description="Pre-computed embedding vector"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Document metadata"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_123",
                "text": "AI agents are autonomous software entities...",
                "metadata": {
                    "type": "documentation",
                    "category": "ai",
                    "author": "DataPizza",
                },
            }
        }


class SearchFilter(BaseModel):
    """
    Search filter for metadata filtering.
    
    Attributes:
        metadata_filters: Key-value filters for metadata
        min_score: Minimum similarity score threshold (0-1)
        max_results: Maximum number of results to return
    """

    metadata_filters: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata filters (exact match)",
    )
    min_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score",
    )
    max_results: int = Field(
        default=10, gt=0, le=100, description="Maximum results"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "metadata_filters": {"type": "documentation", "category": "ai"},
                "min_score": 0.7,
                "max_results": 5,
            }
        }


class SearchResult(BaseModel):
    """
    Search result with similarity score.
    
    Attributes:
        document: Matched document
        score: Similarity score (0-1, higher is better)
        rank: Result rank (1-based)
    """

    document: Document = Field(..., description="Matched document")
    score: float = Field(
        ..., ge=0.0, le=1.0, description="Similarity score (0-1)"
    )
    rank: int = Field(..., gt=0, description="Result rank (1-based)")

    class Config:
        json_schema_extra = {
            "example": {
                "document": {
                    "id": "doc_123",
                    "text": "AI agents...",
                    "metadata": {"type": "documentation"},
                },
                "score": 0.92,
                "rank": 1,
            }
        }


class EmbeddingStats(BaseModel):
    """
    Embedding generation statistics.
    
    Attributes:
        total_tokens: Total tokens processed
        total_time: Total processing time in seconds
        avg_time_per_doc: Average time per document
        documents_processed: Number of documents processed
    """

    total_tokens: int = Field(default=0, description="Total tokens processed")
    total_time: float = Field(default=0.0, description="Total time (seconds)")
    avg_time_per_doc: float = Field(
        default=0.0, description="Average time per document"
    )
    documents_processed: int = Field(
        default=0, description="Documents processed"
    )
