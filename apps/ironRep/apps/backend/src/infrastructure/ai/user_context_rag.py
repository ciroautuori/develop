"""
User Context RAG Service

Stores and retrieves user-specific context (pain, goals, equipment, history)
in ChromaDB for personalized agent responses.

Uses HuggingFace embeddings (all-MiniLM-L6-v2) - same as RAGService for consistency.
"""
from typing import Dict, Any, List, Optional, Literal
from langchain_core.tools import BaseTool
from datetime import datetime
import os

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from src.infrastructure.ai.google_embeddings import CustomGoogleEmbeddingFunction

from src.infrastructure.config.settings import settings
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


ContextCategory = Literal["pain", "goal", "equipment", "history", "preference", "medical"]


class UserContextRAG:
    """
    RAG service for storing and retrieving user-specific context.

    Separate from knowledge base RAG - this stores dynamic user data
    that agents use for personalization.

    Uses Google Generative AI embeddings for consistency with main RAG.
    """

    COLLECTION_NAME = "user_context_v2"

    def __init__(self):
        """Initialize user context RAG service with Google embeddings."""
        # Use Custom Google Generative AI Embeddings to avoid ChromaDB serialization issues
        logger.info("Using Custom Google Generative AI Embeddings")
        self.embedding_fn = CustomGoogleEmbeddingFunction(
            api_key=settings.google_api_key
        )

        # Initialize ChromaDB
        chroma_host = os.getenv("CHROMA_HOST", "localhost")
        chroma_port = int(os.getenv("CHROMA_PORT", "8000"))

        try:
            self.client = chromadb.HttpClient(
                host=chroma_host,
                port=chroma_port,
                settings=Settings(anonymized_telemetry=False)
            )

            # Get or create user_context collection WITHOUT embedding function
            self.collection = self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                embedding_function=None,
                metadata={"description": "User-specific context for personalization"}
            )
            logger.info(f"UserContextRAG initialized with collection: {self.COLLECTION_NAME}")

        except Exception as e:
            logger.error(f"ChromaDB connection failed: {e}")
            self.client = None
            self.collection = None

    def store_context(
        self,
        user_id: str,
        text: str,
        category: ContextCategory,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store user context in vector database.

        Args:
            user_id: User identifier
            text: Context text to embed and store
            category: Category of context (pain, goal, equipment, history)
            metadata: Additional metadata

        Returns:
            Document ID
        """
        if not self.collection:
            logger.warning("ChromaDB not available, skipping context storage")
            return ""

        # Generate embedding using ChromaDB's default embedding function
        embeddings = self.embedding_fn([text])
        embedding = embeddings[0] if embeddings else None
        if embedding is None:
            logger.error("Failed to generate embedding")
            return ""

        # Create document ID
        doc_id = f"{user_id}_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Prepare metadata
        doc_metadata = {
            "user_id": str(user_id),  # Ensure user_id is string
            "category": str(category),
            "timestamp": datetime.now().isoformat(),
            "text_preview": str(text[:200]) if len(text) > 200 else str(text)
        }
        if metadata:
            # Sanitize metadata: ChromaDB only accepts str, int, float, bool, or None
            for key, value in metadata.items():
                # Convert keys to string just in case
                safe_key = str(key)

                if isinstance(value, (str, int, float, bool)):
                    doc_metadata[safe_key] = value
                elif value is None:
                    doc_metadata[safe_key] = ""
                elif isinstance(value, (list, dict)):
                    # Convert complex types to string representation
                    import json
                    try:
                        doc_metadata[safe_key] = json.dumps(value)
                    except:
                        doc_metadata[safe_key] = str(value)
                else:
                    doc_metadata[safe_key] = str(value)

        # Store in ChromaDB
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[doc_metadata]
        )

        logger.debug(f"Stored context [{category}] for user {user_id}: {text[:50]}...")
        return doc_id

    def retrieve_context(
        self,
        user_id: str,
        query: str,
        categories: Optional[List[ContextCategory]] = None,
        k: int = 5
    ) -> List[Dict]:
        """
        Retrieve relevant context for a user.

        Args:
            user_id: User identifier
            query: Search query
            categories: Filter by categories (optional)
            k: Number of results

        Returns:
            List of relevant context chunks with scores
        """
        if not self.collection:
            return []

        # Build filter - ChromaDB requires $and for multiple conditions
        if categories:
            where_filter = {
                "$and": [
                    {"user_id": user_id},
                    {"category": {"$in": categories}}
                ]
            }
        else:
            where_filter = {"user_id": user_id}

        # Generate query embedding using ChromaDB's default embedding function
        query_embeddings = self.embedding_fn([query])
        query_embedding = query_embeddings[0] if query_embeddings else None
        if query_embedding is None:
            logger.error("Failed to generate query embedding")
            return []

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        # Format results
        context_chunks = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                context_chunks.append({
                    "content": doc,
                    "category": results["metadatas"][0][i].get("category", "unknown"),
                    "timestamp": results["metadatas"][0][i].get("timestamp"),
                    "relevance_score": 1 - results["distances"][0][i] if results["distances"] else 0
                })

        return context_chunks

    def get_user_profile_context(self, user_id: str) -> str:
        """
        Get formatted context string for LLM prompts.

        Args:
            user_id: User identifier

        Returns:
            Formatted context string
        """
        if not self.collection:
            return ""

        # Get all categories
        categories: List[ContextCategory] = ["pain", "goal", "equipment", "history", "medical"]

        context_parts = []

        for category in categories:
            cat_embedding = self.embedding_fn([category])[0]
            results = self.collection.query(
                query_embeddings=[cat_embedding],
                n_results=3,
                where={"$and": [{"user_id": user_id}, {"category": category}]},
                include=["documents", "metadatas"]
            )

            if results and results["documents"] and results["documents"][0]:
                context_parts.append(f"\n=== {category.upper()} ===")
                for doc in results["documents"][0]:
                    context_parts.append(f"- {doc}")

        if not context_parts:
            return ""

        return "\n".join(context_parts)

    def delete_user_context(self, user_id: str, category: Optional[ContextCategory] = None) -> int:
        """
        Delete user context.

        Args:
            user_id: User identifier
            category: Optional category filter

        Returns:
            Number of deleted documents
        """
        if not self.collection:
            return 0

        # Build filter - ChromaDB requires $and for multiple conditions
        if category:
            where_filter = {
                "$and": [
                    {"user_id": user_id},
                    {"category": category}
                ]
            }
        else:
            where_filter = {"user_id": user_id}

        # Get matching IDs
        results = self.collection.get(
            where=where_filter,
            include=["metadatas"]
        )

        if results and results["ids"]:
            self.collection.delete(ids=results["ids"])
            return len(results["ids"])

        return 0

    def store_wizard_answer(
        self,
        user_id: str,
        question: str,
        answer: str,
        category: ContextCategory
    ) -> str:
        """
        Store a wizard interview answer.

        Args:
            user_id: User identifier
            question: The question asked
            answer: User's answer
            category: Category of the answer

        Returns:
            Document ID
        """
        # Format as Q&A for better retrieval
        text = f"Domanda: {question}\nRisposta: {answer}"

        return self.store_context(
            user_id=user_id,
            text=text,
            category=category,
            metadata={
                "source": "wizard_interview",
                "question": question
            }
        )

    def get_context_summary(self, user_id: str) -> Dict:
        """
        Get summary of stored context for a user.

        Args:
            user_id: User identifier

        Returns:
            Summary dict with counts per category
        """
        if not self.collection:
            return {"total": 0, "categories": {}}

        summary = {"total": 0, "categories": {}}

        for category in ["pain", "goal", "equipment", "history", "medical", "preference"]:
            results = self.collection.get(
                where={"$and": [{"user_id": user_id}, {"category": category}]},
                include=["metadatas"]
            )
            count = len(results["ids"]) if results and results["ids"] else 0
            summary["categories"][category] = count
            summary["total"] += count

        return summary


# Singleton instance
_user_context_rag = None


def get_user_context_rag() -> UserContextRAG:
    """Get or create UserContextRAG singleton."""
    global _user_context_rag
    if _user_context_rag is None:
        _user_context_rag = UserContextRAG()
    return _user_context_rag
