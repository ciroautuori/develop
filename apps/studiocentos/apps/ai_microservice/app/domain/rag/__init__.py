"""
Vector Store Integration for Semantic Search and Embeddings.

This module provides a unified interface for vector databases with support
for multiple backends (Pinecone, Chroma, FAISS) and embedding generation.

Components:
    - embeddings: Text embedding generation with multiple providers
    - stores: Vector database implementations (Pinecone, Chroma, FAISS)
    - search: Semantic search with filters and ranking

Features:
    - Provider abstraction (easy to switch backends)
    - Batch processing for efficiency
    - Metadata filtering
    - Hybrid search (vector + keyword)
    - Automatic embedding caching

Example:
    >>> from app.domain.rag import get_vector_store, OpenAIEmbeddings
    >>> 
    >>> # Initialize
    >>> embeddings = OpenAIEmbeddings()
    >>> store = get_vector_store("pinecone", embeddings=embeddings)
    >>> 
    >>> # Add documents
    >>> await store.add_documents([
    ...     {"id": "1", "text": "AI agents...", "metadata": {"type": "doc"}},
    ... ])
    >>> 
    >>> # Search
    >>> results = await store.search("artificial intelligence", top_k=5)
"""

from app.domain.rag.embeddings import (
    BaseEmbeddings,
    OpenAIEmbeddings,
    AnthropicEmbeddings,
    HuggingFaceEmbeddings,
)
from app.domain.rag.stores import (
    BaseVectorStore,
    PineconeVectorStore,
    ChromaVectorStore,
    FAISSVectorStore,
    get_vector_store,
)
from app.domain.rag.models import (
    Document,
    SearchResult,
    SearchFilter,
)

__all__ = [
    # Embeddings
    "BaseEmbeddings",
    "OpenAIEmbeddings",
    "AnthropicEmbeddings",
    "HuggingFaceEmbeddings",
    # Vector Stores
    "BaseVectorStore",
    "PineconeVectorStore",
    "ChromaVectorStore",
    "FAISSVectorStore",
    "get_vector_store",
    # Models
    "Document",
    "SearchResult",
    "SearchFilter",
]
