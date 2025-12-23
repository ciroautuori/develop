"""Knowledge base integration for agent systems.

Provides integration with vector stores and knowledge bases
for retrieval-augmented generation (RAG) patterns.
"""

from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class Document(BaseModel):
    """Represents a document in the knowledge base.
    
    Attributes:
        id: Unique document identifier
        content: Document content
        metadata: Document metadata (source, author, date, etc.)
        embedding: Optional pre-computed embedding vector
    """
    
    id: str = Field(default_factory=lambda: uuid4().hex)
    content: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    
    def __hash__(self) -> int:
        """Make document hashable by ID."""
        return hash(self.id)


class SearchResult(BaseModel):
    """Result from knowledge base search.
    
    Attributes:
        document: Retrieved document
        score: Relevance score (0.0 to 1.0)
        rank: Result rank (1-indexed)
    """
    
    document: Document
    score: float = Field(ge=0.0, le=1.0)
    rank: int = Field(ge=1)


class KnowledgeBase:
    """Interface for knowledge base operations.
    
    Provides unified interface for different knowledge base backends
    (vector stores, search engines, databases).
    """
    
    def __init__(
        self,
        name: str = "default",
        max_results: int = 10
    ) -> None:
        """Initialize knowledge base.
        
        Args:
            name: Knowledge base name
            max_results: Default maximum search results
        """
        self.name = name
        self.max_results = max_results
        self._documents: Dict[str, Document] = {}
        self._index: Dict[str, List[str]] = {}  # Simple keyword index
    
    def add_document(self, document: Document) -> None:
        """Add document to knowledge base.
        
        Args:
            document: Document to add
        """
        self._documents[document.id] = document
        
        # Build simple keyword index
        words = document.content.lower().split()
        for word in set(words):
            if word not in self._index:
                self._index[word] = []
            if document.id not in self._index[word]:
                self._index[word].append(document.id)
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add multiple documents to knowledge base.
        
        Args:
            documents: List of documents to add
        """
        for doc in documents:
            self.add_document(doc)
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search knowledge base.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of search results ranked by relevance
        """
        k = top_k or self.max_results
        
        # Simple keyword-based search
        query_words = set(query.lower().split())
        
        # Find matching documents
        doc_scores: Dict[str, int] = {}
        for word in query_words:
            if word in self._index:
                for doc_id in self._index[word]:
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1
        
        # Apply filters if specified
        if filters:
            filtered_scores = {}
            for doc_id, score in doc_scores.items():
                doc = self._documents[doc_id]
                if all(
                    doc.metadata.get(k) == v
                    for k, v in filters.items()
                ):
                    filtered_scores[doc_id] = score
            doc_scores = filtered_scores
        
        # Sort by score and limit results
        sorted_docs = sorted(
            doc_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:k]
        
        # Create search results
        results = []
        for rank, (doc_id, score) in enumerate(sorted_docs, start=1):
            # Normalize score to 0-1
            max_score = max(doc_scores.values()) if doc_scores else 1
            normalized_score = score / max_score
            
            results.append(SearchResult(
                document=self._documents[doc_id],
                score=normalized_score,
                rank=rank
            ))
        
        return results
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get document by ID.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Document or None if not found
        """
        return self._documents.get(doc_id)
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document from knowledge base.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            True if deleted, False if not found
        """
        if doc_id in self._documents:
            # Remove from documents
            doc = self._documents.pop(doc_id)
            
            # Remove from index
            words = doc.content.lower().split()
            for word in set(words):
                if word in self._index and doc_id in self._index[word]:
                    self._index[word].remove(doc_id)
                    if not self._index[word]:
                        del self._index[word]
            
            return True
        return False
    
    def clear(self) -> None:
        """Clear all documents from knowledge base."""
        self._documents.clear()
        self._index.clear()
    
    @property
    def document_count(self) -> int:
        """Get total document count."""
        return len(self._documents)


class VectorStore(KnowledgeBase):
    """Vector-based knowledge base with semantic search.
    
    Extends KnowledgeBase with vector similarity search capabilities.
    Note: This is a simple implementation. For production, use
    dedicated vector stores like Pinecone, Weaviate, ChromaDB.
    """
    
    def __init__(
        self,
        name: str = "default",
        max_results: int = 10,
        embedding_dim: int = 768
    ) -> None:
        """Initialize vector store.
        
        Args:
            name: Vector store name
            max_results: Default maximum search results
            embedding_dim: Embedding vector dimension
        """
        super().__init__(name, max_results)
        self.embedding_dim = embedding_dim
    
    def semantic_search(
        self,
        query_embedding: List[float],
        top_k: Optional[int] = None,
        threshold: float = 0.7
    ) -> List[SearchResult]:
        """Search using semantic similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            threshold: Minimum similarity threshold (0.0 to 1.0)
            
        Returns:
            List of semantically similar documents
        """
        k = top_k or self.max_results
        
        # Calculate cosine similarity for documents with embeddings
        similarities: List[tuple[str, float]] = []
        
        for doc_id, doc in self._documents.items():
            if doc.embedding is None:
                continue
            
            # Cosine similarity
            similarity = self._cosine_similarity(
                query_embedding,
                doc.embedding
            )
            
            if similarity >= threshold:
                similarities.append((doc_id, similarity))
        
        # Sort by similarity and limit
        similarities.sort(key=lambda x: x[1], reverse=True)
        similarities = similarities[:k]
        
        # Create search results
        results = []
        for rank, (doc_id, score) in enumerate(similarities, start=1):
            results.append(SearchResult(
                document=self._documents[doc_id],
                score=score,
                rank=rank
            ))
        
        return results
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity (0.0 to 1.0)
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")
        
        # Dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Magnitudes
        mag1 = sum(a * a for a in vec1) ** 0.5
        mag2 = sum(b * b for b in vec2) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
