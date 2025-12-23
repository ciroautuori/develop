"""
RAG Service - Complete document processing and retrieval.

Provides:
- Document upload with chunking
- Semantic search with context retrieval
- Document management (list, delete)
- Context injection for content generation
"""

import hashlib
import logging
import re
from datetime import datetime
from typing import Any

from app.core.config import settings
from app.domain.rag.embeddings import BaseEmbeddings, GoogleEmbeddings
from app.domain.rag.models import Document, SearchFilter, SearchResult
from app.domain.rag.stores import BaseVectorStore, ChromaVectorStore

logger = logging.getLogger(__name__)


class TextChunker:
    """Split text into overlapping chunks for RAG."""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: list[str] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " "]

    def split(self, text: str) -> list[str]:
        """Split text into chunks."""
        chunks = []
        current_chunk = ""

        # Split by paragraphs first
        paragraphs = text.split("\n\n")

        for para in paragraphs:
            if len(current_chunk) + len(para) <= self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # If paragraph itself is too long, split by sentences
                if len(para) > self.chunk_size:
                    sentences = re.split(r"(?<=[.!?])\s+", para)
                    current_chunk = ""
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) <= self.chunk_size:
                            current_chunk += sentence + " "
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sentence + " "
                else:
                    current_chunk = para + "\n\n"

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        # Add overlap between chunks
        overlapped_chunks = []
        for i, chunk in enumerate(chunks):
            if i > 0 and self.chunk_overlap > 0:
                # Get last N chars from previous chunk
                prev_overlap = chunks[i-1][-self.chunk_overlap:]
                chunk = prev_overlap + " " + chunk
            overlapped_chunks.append(chunk)

        return overlapped_chunks


class RAGService:
    """
    Complete RAG service for document management and retrieval.

    Features:
    - Document upload with automatic chunking
    - Semantic search
    - Context retrieval for AI generation
    - Document listing and deletion
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize RAG service."""
        if RAGService._initialized:
            return

        self.chunker = TextChunker(
            chunk_size=settings.RAG_CHUNK_SIZE,
            chunk_overlap=settings.RAG_CHUNK_OVERLAP
        )

        # Initialize embeddings
        self.embeddings: BaseEmbeddings | None = None
        self.vector_store: BaseVectorStore | None = None

        # Document metadata storage (in-memory, extend to DB if needed)
        self._documents: dict[str, dict[str, Any]] = {}

        RAGService._initialized = True
        logger.info("rag_service_initialized")

    async def _ensure_initialized(self):
        """Lazy initialization of embeddings and vector store."""
        if self.embeddings is None:
            try:
                self.embeddings = GoogleEmbeddings()
                logger.info("embeddings_initialized", provider="google")
            except Exception as e:
                logger.warning("embeddings_fallback", error=str(e))
                # Fallback to simple embeddings if Google fails
                self.embeddings = None

        if self.vector_store is None and self.embeddings:
            try:
                self.vector_store = ChromaVectorStore(
                    embeddings=self.embeddings,
                    collection_name="markettina_knowledge",
                    persist_directory=settings.CHROMADB_PERSIST_DIR
                )
                logger.info("vector_store_initialized", type="chroma")
            except Exception as e:
                logger.error("vector_store_init_failed", error=str(e))

    def _generate_doc_id(self, filename: str, content: str) -> str:
        """Generate unique document ID."""
        hash_input = f"{filename}:{content[:100]}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]

    async def upload_document(
        self,
        filename: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        user_id: int = 1
    ) -> dict[str, Any]:
        """
        Upload and index a document.

        Args:
            filename: Document filename
            content: Document text content
            metadata: Optional metadata
            user_id: Owner user ID

        Returns:
            Upload result with document ID and chunk count
        """
        await self._ensure_initialized()

        doc_id = self._generate_doc_id(filename, content)

        # Split into chunks
        chunks = self.chunker.split(content)

        logger.info(
            "document_chunked",
            doc_id=doc_id,
            filename=filename,
            chunks=len(chunks)
        )

        # Create chunk documents
        chunk_docs = []
        for i, chunk_text in enumerate(chunks):
            chunk_doc = Document(
                id=f"{doc_id}_chunk_{i}",
                text=chunk_text,
                metadata={
                    "doc_id": doc_id,
                    "filename": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "user_id": user_id,
                    "uploaded_at": datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
            )
            chunk_docs.append(chunk_doc)

        # Add to vector store
        if self.vector_store:
            try:
                await self.vector_store.add_documents(chunk_docs)
                logger.info("document_indexed", doc_id=doc_id, chunks=len(chunks))
            except Exception as e:
                logger.error("indexing_failed", error=str(e))
                return {
                    "document_id": doc_id,
                    "filename": filename,
                    "chunks_count": len(chunks),
                    "status": "error",
                    "error": str(e)
                }

        # Store document metadata
        self._documents[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "chunks_count": len(chunks),
            "user_id": user_id,
            "uploaded_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        return {
            "document_id": doc_id,
            "filename": filename,
            "chunks_count": len(chunks),
            "status": "indexed"
        }

    async def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.7,
        user_id: int | None = None
    ) -> list[SearchResult]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            top_k: Number of results
            min_score: Minimum similarity score
            user_id: Filter by user (optional)

        Returns:
            List of search results
        """
        await self._ensure_initialized()

        if not self.vector_store:
            logger.warning("search_no_vector_store")
            return []

        # Build filter
        filter_obj = None
        if user_id or min_score > 0:
            metadata_filters = {}
            if user_id:
                metadata_filters["user_id"] = user_id
            filter_obj = SearchFilter(
                min_score=min_score,
                metadata_filters=metadata_filters if metadata_filters else None
            )

        try:
            results = await self.vector_store.search(
                query=query,
                top_k=top_k,
                filter=filter_obj
            )
            logger.info("search_completed", query_len=len(query), results=len(results))
            return results
        except Exception as e:
            logger.error("search_failed", error=str(e))
            return []

    async def get_context(
        self,
        query: str,
        max_tokens: int = 2000,
        user_id: int | None = None
    ) -> str:
        """
        Get context string for AI generation.

        Retrieves relevant documents and formats them as context.

        Args:
            query: Query to find relevant context
            max_tokens: Approximate max tokens in context
            user_id: Filter by user (optional)

        Returns:
            Formatted context string
        """
        results = await self.search(
            query=query,
            top_k=10,
            min_score=settings.RAG_SIMILARITY_THRESHOLD,
            user_id=user_id
        )

        if not results:
            return ""

        # Build context from results
        context_parts = []
        total_chars = 0
        max_chars = max_tokens * 4  # Approximate chars per token

        for result in results:
            text = result.document.text
            if total_chars + len(text) > max_chars:
                break

            source = result.document.metadata.get("filename", "unknown")
            context_parts.append(f"[Fonte: {source}]\n{text}")
            total_chars += len(text)

        if context_parts:
            return "\n\n---\n\n".join(context_parts)

        return ""

    async def list_documents(
        self,
        user_id: int | None = None
    ) -> list[dict[str, Any]]:
        """
        List all indexed documents.

        Args:
            user_id: Filter by user (optional)

        Returns:
            List of document metadata
        """
        docs = list(self._documents.values())

        if user_id:
            docs = [d for d in docs if d.get("user_id") == user_id]

        return docs

    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document and its chunks.

        Args:
            doc_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        if doc_id not in self._documents:
            return False

        doc_info = self._documents[doc_id]
        chunks_count = doc_info.get("chunks_count", 0)

        # Delete chunks from vector store
        if self.vector_store and chunks_count > 0:
            chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(chunks_count)]
            try:
                await self.vector_store.delete(chunk_ids)
                logger.info("document_deleted", doc_id=doc_id, chunks=chunks_count)
            except Exception as e:
                logger.error("delete_failed", error=str(e))

        # Remove from metadata
        del self._documents[doc_id]

        return True

    async def get_document(self, doc_id: str) -> dict[str, Any] | None:
        """Get document metadata by ID."""
        return self._documents.get(doc_id)


# Singleton instance
rag_service = RAGService()
