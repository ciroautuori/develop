"""
Vector Store Implementations - Pinecone, Chroma, FAISS.

Unified interface for multiple vector database backends.
"""

import json
import os
from abc import ABC, abstractmethod

from app.domain.rag.embeddings import BaseEmbeddings
from app.domain.rag.models import (
    Document,
    SearchFilter,
    SearchResult,
)


class BaseVectorStore(ABC):
    """
    Abstract base class for vector stores.
    
    Subclasses must implement:
        - add_documents: Add documents to the store
        - search: Search for similar documents
        - delete: Delete documents by ID
        - clear: Clear all documents
    """

    def __init__(self, embeddings: BaseEmbeddings):
        """
        Initialize vector store.
        
        Args:
            embeddings: Embeddings provider
        """
        self.embeddings = embeddings

    @abstractmethod
    async def add_documents(self, documents: list[Document]) -> None:
        """Add documents to vector store."""

    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: SearchFilter | None = None,
    ) -> list[SearchResult]:
        """Search for similar documents."""

    @abstractmethod
    async def delete(self, doc_ids: list[str]) -> None:
        """Delete documents by ID."""

    @abstractmethod
    async def clear(self) -> None:
        """Clear all documents."""


class PineconeVectorStore(BaseVectorStore):
    """
    Pinecone vector database integration.
    
    Environment Variables:
        PINECONE_API_KEY: Pinecone API key
        PINECONE_ENVIRONMENT: Pinecone environment
        PINECONE_INDEX_NAME: Index name
    
    Example:
        >>> from app.domain.rag import PineconeVectorStore, OpenAIEmbeddings
        >>> embeddings = OpenAIEmbeddings()
        >>> store = PineconeVectorStore(embeddings=embeddings)
        >>> await store.add_documents([doc1, doc2])
    """

    def __init__(
        self,
        embeddings: BaseEmbeddings,
        index_name: str | None = None,
        api_key: str | None = None,
        environment: str | None = None,
    ):
        """
        Initialize Pinecone vector store.
        
        Args:
            embeddings: Embeddings provider
            index_name: Pinecone index name
            api_key: Pinecone API key
            environment: Pinecone environment
        """
        super().__init__(embeddings)

        try:
            import pinecone
        except ImportError:
            raise ImportError(
                "pinecone-client required. Install with: pip install pinecone-client"
            )

        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME")
        if not self.index_name:
            raise ValueError("Pinecone index name required")

        api_key = api_key or os.getenv("PINECONE_API_KEY")
        environment = environment or os.getenv("PINECONE_ENVIRONMENT")

        # Initialize Pinecone
        pinecone.init(api_key=api_key, environment=environment)
        self.index = pinecone.Index(self.index_name)

    async def add_documents(self, documents: list[Document]) -> None:
        """
        Add documents to Pinecone index.
        
        Args:
            documents: Documents to add
        """
        # Generate embeddings for documents without them
        texts = [doc.text for doc in documents if doc.embedding is None]
        if texts:
            embeddings = await self.embeddings.embed_batch(texts)
            embed_idx = 0
            for doc in documents:
                if doc.embedding is None:
                    doc.embedding = embeddings[embed_idx]
                    embed_idx += 1

        # Prepare vectors for Pinecone
        vectors = [
            (
                doc.id,
                doc.embedding,
                {
                    "text": doc.text,
                    "metadata": json.dumps(doc.metadata),
                    "created_at": doc.created_at.isoformat(),
                },
            )
            for doc in documents
        ]

        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]
            self.index.upsert(vectors=batch)

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: SearchFilter | None = None,
    ) -> list[SearchResult]:
        """
        Search Pinecone index for similar documents.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filter: Optional search filter
            
        Returns:
            List of search results
        """
        # Generate query embedding
        query_embedding = await self.embeddings.embed_text(query)

        # Build Pinecone filter
        pinecone_filter = None
        if filter and filter.metadata_filters:
            pinecone_filter = {
                f"metadata.{k}": v for k, v in filter.metadata_filters.items()
            }

        # Search
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=pinecone_filter,
        )

        # Parse results
        search_results = []
        for rank, match in enumerate(results.matches, start=1):
            metadata = json.loads(match.metadata.get("metadata", "{}"))
            doc = Document(
                id=match.id,
                text=match.metadata["text"],
                metadata=metadata,
            )
            search_results.append(
                SearchResult(document=doc, score=match.score, rank=rank)
            )

        # Apply min_score filter
        if filter and filter.min_score > 0:
            search_results = [
                r for r in search_results if r.score >= filter.min_score
            ]

        return search_results

    async def delete(self, doc_ids: list[str]) -> None:
        """
        Delete documents from Pinecone index.
        
        Args:
            doc_ids: Document IDs to delete
        """
        self.index.delete(ids=doc_ids)

    async def clear(self) -> None:
        """Clear all vectors from Pinecone index."""
        self.index.delete(delete_all=True)


class ChromaVectorStore(BaseVectorStore):
    """
    Chroma vector database integration (local or remote).
    
    Example:
        >>> store = ChromaVectorStore(
        ...     embeddings=embeddings,
        ...     collection_name="datapizza_docs"
        ... )
    """

    def __init__(
        self,
        embeddings: BaseEmbeddings,
        collection_name: str = "datapizza_ai",
        persist_directory: str | None = None,
    ):
        """
        Initialize Chroma vector store.
        
        Args:
            embeddings: Embeddings provider
            collection_name: Chroma collection name
            persist_directory: Local persistence directory (if None, in-memory)
        """
        super().__init__(embeddings)

        try:
            import chromadb
        except ImportError:
            raise ImportError(
                "chromadb required. Install with: pip install chromadb"
            )

        # Initialize Chroma client
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client()

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    async def add_documents(self, documents: list[Document]) -> None:
        """Add documents to Chroma collection."""
        # Generate embeddings
        texts = [doc.text for doc in documents if doc.embedding is None]
        if texts:
            embeddings = await self.embeddings.embed_batch(texts)
            embed_idx = 0
            for doc in documents:
                if doc.embedding is None:
                    doc.embedding = embeddings[embed_idx]
                    embed_idx += 1

        # Add to Chroma
        self.collection.add(
            ids=[doc.id for doc in documents],
            embeddings=[doc.embedding for doc in documents],
            documents=[doc.text for doc in documents],
            metadatas=[doc.metadata for doc in documents],
        )

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: SearchFilter | None = None,
    ) -> list[SearchResult]:
        """Search Chroma collection."""
        # Generate query embedding
        query_embedding = await self.embeddings.embed_text(query)

        # Build where filter
        where = filter.metadata_filters if filter else None

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
        )

        # Parse results
        search_results = []
        for rank, (doc_id, text, metadata, distance) in enumerate(
            zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ),
            start=1,
        ):
            # Convert distance to similarity score (0-1)
            score = 1.0 / (1.0 + distance)

            doc = Document(id=doc_id, text=text, metadata=metadata)
            search_results.append(
                SearchResult(document=doc, score=score, rank=rank)
            )

        # Apply min_score filter
        if filter and filter.min_score > 0:
            search_results = [
                r for r in search_results if r.score >= filter.min_score
            ]

        return search_results

    async def delete(self, doc_ids: list[str]) -> None:
        """Delete documents from Chroma collection."""
        self.collection.delete(ids=doc_ids)

    async def clear(self) -> None:
        """Clear Chroma collection."""
        self.client.delete_collection(name=self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name
        )


class FAISSVectorStore(BaseVectorStore):
    """
    FAISS local vector database (Facebook AI Similarity Search).
    
    Best for: Local development, small to medium datasets
    
    Example:
        >>> store = FAISSVectorStore(embeddings=embeddings)
    """

    def __init__(self, embeddings: BaseEmbeddings):
        """
        Initialize FAISS vector store.
        
        Args:
            embeddings: Embeddings provider
        """
        super().__init__(embeddings)

        try:
            import faiss
            import numpy as np
        except ImportError:
            raise ImportError(
                "faiss-cpu required. Install with: pip install faiss-cpu"
            )

        self.faiss = faiss
        self.np = np

        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(embeddings.dimension)  # Inner product
        self.documents: dict[str, Document] = {}

    async def add_documents(self, documents: list[Document]) -> None:
        """Add documents to FAISS index."""
        # Generate embeddings
        texts = [doc.text for doc in documents if doc.embedding is None]
        if texts:
            embeddings = await self.embeddings.embed_batch(texts)
            embed_idx = 0
            for doc in documents:
                if doc.embedding is None:
                    doc.embedding = embeddings[embed_idx]
                    embed_idx += 1

        # Add to FAISS
        vectors = self.np.array([doc.embedding for doc in documents]).astype(
            "float32"
        )
        self.index.add(vectors)

        # Store documents
        for doc in documents:
            self.documents[doc.id] = doc

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: SearchFilter | None = None,
    ) -> list[SearchResult]:
        """Search FAISS index."""
        # Generate query embedding
        query_embedding = await self.embeddings.embed_text(query)
        query_vector = self.np.array([query_embedding]).astype("float32")

        # Search
        scores, indices = self.index.search(query_vector, top_k)

        # Parse results
        search_results = []
        for rank, (idx, score) in enumerate(
            zip(indices[0], scores[0]), start=1
        ):
            if idx == -1:  # No more results
                break

            # Find document by index
            doc = list(self.documents.values())[idx]

            # Apply metadata filters
            if filter and filter.metadata_filters:
                match = all(
                    doc.metadata.get(k) == v
                    for k, v in filter.metadata_filters.items()
                )
                if not match:
                    continue

            search_results.append(
                SearchResult(document=doc, score=float(score), rank=rank)
            )

        # Apply min_score filter
        if filter and filter.min_score > 0:
            search_results = [
                r for r in search_results if r.score >= filter.min_score
            ]

        return search_results

    async def delete(self, doc_ids: list[str]) -> None:
        """Delete documents (requires rebuilding index)."""
        for doc_id in doc_ids:
            if doc_id in self.documents:
                del self.documents[doc_id]

        # Rebuild index
        await self._rebuild_index()

    async def clear(self) -> None:
        """Clear FAISS index."""
        self.index.reset()
        self.documents.clear()

    async def _rebuild_index(self) -> None:
        """Rebuild FAISS index from stored documents."""
        self.index.reset()
        if self.documents:
            vectors = self.np.array(
                [doc.embedding for doc in self.documents.values()]
            ).astype("float32")
            self.index.add(vectors)


# ============================================================================
# FACTORY
# ============================================================================


def get_vector_store(
    store_type: str,
    embeddings: BaseEmbeddings,
    **kwargs,
) -> BaseVectorStore:
    """
    Factory function to get vector store instance.
    
    Args:
        store_type: Vector store type ('pinecone', 'chroma', 'faiss')
        embeddings: Embeddings provider
        **kwargs: Additional store-specific arguments
        
    Returns:
        Vector store instance
        
    Example:
        >>> embeddings = OpenAIEmbeddings()
        >>> store = get_vector_store("chroma", embeddings=embeddings)
    """
    stores = {
        "pinecone": PineconeVectorStore,
        "chroma": ChromaVectorStore,
        "faiss": FAISSVectorStore,
    }

    if store_type not in stores:
        raise ValueError(
            f"Unknown store type: {store_type}. Choose from: {list(stores.keys())}"
        )

    return stores[store_type](embeddings=embeddings, **kwargs)
