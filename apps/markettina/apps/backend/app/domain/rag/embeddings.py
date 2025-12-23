"""
Embedding Generation with Multiple Providers.

Supports OpenAI, Anthropic, and HuggingFace embedding models.
"""

import os
import time
from abc import ABC, abstractmethod

import httpx

from app.domain.rag.models import EmbeddingStats


class BaseEmbeddings(ABC):
    """
    Abstract base class for embedding generation.

    Subclasses must implement:
        - embed_text: Generate embedding for single text
        - embed_batch: Generate embeddings for multiple texts (optional, has default)
    """

    def __init__(self, model: str, dimension: int):
        """
        Initialize embeddings provider.

        Args:
            model: Model identifier
            dimension: Embedding dimension
        """
        self.model = model
        self.dimension = dimension
        self.stats = EmbeddingStats()

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text

        Returns:
            Embedding vector (list of floats)
        """

    async def embed_batch(
        self, texts: list[str], batch_size: int = 100
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of input texts
            batch_size: Batch size for processing

        Returns:
            List of embedding vectors
        """
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_embeddings = await self._process_batch(batch)
            embeddings.extend(batch_embeddings)
        return embeddings

    async def _process_batch(self, texts: list[str]) -> list[list[float]]:
        """Process a single batch of texts."""
        start_time = time.time()
        embeddings = []

        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)

        # Update stats
        elapsed = time.time() - start_time
        self.stats.total_time += elapsed
        self.stats.documents_processed += len(texts)
        self.stats.avg_time_per_doc = (
            self.stats.total_time / self.stats.documents_processed
            if self.stats.documents_processed > 0
            else 0.0
        )

        return embeddings


class OpenAIEmbeddings(BaseEmbeddings):
    """
    OpenAI embedding generation using text-embedding-3-small or ada-002.

    Environment Variables:
        OPENAI_API_KEY: OpenAI API key

    Example:
        >>> embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        >>> vector = await embeddings.embed_text("Hello world")
    """

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
    ):
        """
        Initialize OpenAI embeddings.

        Args:
            model: OpenAI embedding model name
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
            base_url: OpenAI API base URL
        """
        # Model dimensions
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }

        super().__init__(model=model, dimension=dimensions.get(model, 1536))

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key parameter."
            )

        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def embed_text(self, text: str) -> list[float]:
        """
        Generate OpenAI embedding for text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        response = await self.client.post(
            f"{self.base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={"input": text, "model": self.model},
        )
        response.raise_for_status()

        data = response.json()
        embedding = data["data"][0]["embedding"]

        # Update token stats
        self.stats.total_tokens += data.get("usage", {}).get("total_tokens", 0)

        return embedding

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class AnthropicEmbeddings(BaseEmbeddings):
    """
    Anthropic Claude embedding generation (using Voyage AI).

    Note: Anthropic uses Voyage AI for embeddings.

    Environment Variables:
        ANTHROPIC_API_KEY: Anthropic API key
    """

    def __init__(
        self,
        model: str = "voyage-2",
        api_key: str | None = None,
    ):
        """
        Initialize Anthropic/Voyage embeddings.

        Args:
            model: Voyage model name
            api_key: API key
        """
        dimensions = {
            "voyage-2": 1024,
            "voyage-large-2": 1536,
        }

        super().__init__(model=model, dimension=dimensions.get(model, 1024))

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY env var."
            )

        self.client = httpx.AsyncClient(timeout=30.0)

    async def embed_text(self, text: str) -> list[float]:
        """
        Generate Voyage embedding for text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        response = await self.client.post(
            "https://api.voyageai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={"input": text, "model": self.model},
        )
        response.raise_for_status()

        data = response.json()
        return data["data"][0]["embedding"]

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class GoogleEmbeddings(BaseEmbeddings):
    """
    Google Generative AI embedding generation.

    Uses Gemini embedding models for text embeddings.

    Environment Variables:
        GOOGLE_API_KEY or GEMINI_API_KEY: Google API key

    Example:
        >>> embeddings = GoogleEmbeddings()
        >>> vector = await embeddings.embed_text("Hello world")
    """

    def __init__(
        self,
        model: str = "text-embedding-004",
        api_key: str | None = None,
    ):
        """
        Initialize Google embeddings.

        Args:
            model: Google embedding model name
            api_key: Google API key (if None, reads from env)
        """
        dimensions = {
            "text-embedding-004": 768,
            "embedding-001": 768,
        }

        super().__init__(model=model, dimension=dimensions.get(model, 768))

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google API key required. Set GOOGLE_API_KEY or GEMINI_API_KEY env var."
            )

        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def embed_text(self, text: str) -> list[float]:
        """
        Generate Google embedding for text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        response = await self.client.post(
            f"{self.base_url}/models/{self.model}:embedContent",
            params={"key": self.api_key},
            headers={"Content-Type": "application/json"},
            json={
                "model": f"models/{self.model}",
                "content": {"parts": [{"text": text}]}
            },
        )
        response.raise_for_status()

        data = response.json()
        embedding = data.get("embedding", {}).get("values", [])

        return embedding

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class HuggingFaceEmbeddings(BaseEmbeddings):
    """
    HuggingFace local embedding generation using sentence-transformers.

    Requires: sentence-transformers package

    Example:
        >>> embeddings = HuggingFaceEmbeddings()
        >>> vector = await embeddings.embed_text("Hello world")
    """

    def __init__(
        self,
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu",
    ):
        """
        Initialize HuggingFace embeddings.

        Args:
            model: HuggingFace model identifier
            device: Device to run on ('cpu', 'cuda', 'mps')
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers required for HuggingFaceEmbeddings. "
                "Install with: pip install sentence-transformers"
            )

        # Load model
        self.encoder = SentenceTransformer(model, device=device)
        dimension = self.encoder.get_sentence_embedding_dimension()

        super().__init__(model=model, dimension=dimension)

    async def embed_text(self, text: str) -> list[float]:
        """
        Generate HuggingFace embedding for text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        # sentence-transformers is sync, wrap in async
        import asyncio

        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None, self.encoder.encode, text
        )

        return embedding.tolist()
