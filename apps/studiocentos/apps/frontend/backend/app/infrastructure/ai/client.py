"""
AI Microservice Client - Centralized HTTP client for AI service calls.

Single source of truth for all backend → AI microservice communication.
Provides consistent error handling, retries, and fallback behavior.
"""

import os
import logging
from typing import Any, Optional
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass
class AIClientConfig:
    """Configuration for AI client."""
    base_url: str = ""
    api_key: str = ""
    timeout: float = 60.0
    max_retries: int = 2

    def __post_init__(self):
        self.base_url = self.base_url or os.getenv("AI_SERVICE_URL", "http://ai_microservice:8001")
        self.api_key = self.api_key or os.getenv("AI_SERVICE_API_KEY", "")


class AIServiceError(Exception):
    """Exception raised when AI service call fails."""
    def __init__(self, message: str, status_code: int = 500, fallback_used: bool = False):
        self.message = message
        self.status_code = status_code
        self.fallback_used = fallback_used
        super().__init__(self.message)


class AIClient:
    """
    Centralized client for AI Microservice communication.

    Usage:
        client = AIClient()
        response = await client.generate_content(topic="...", tone="...")
        response = await client.chat(message="...")
        response = await client.generate_image(prompt="...")
    """

    def __init__(self, config: Optional[AIClientConfig] = None):
        self.config = config or AIClientConfig()
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def headers(self) -> dict:
        """Build request headers."""
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                headers=self.headers
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[dict] = None,
        timeout: Optional[float] = None
    ) -> dict:
        """
        Make HTTP request to AI service with retry logic.

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint path
            json: Request body
            timeout: Optional timeout override

        Returns:
            Response data as dict

        Raises:
            AIServiceError: If request fails after retries
        """
        client = await self._get_client()
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = await client.get(endpoint, timeout=timeout)
                else:
                    response = await client.post(endpoint, json=json, timeout=timeout)

                if response.status_code == 200:
                    return response.json()

                logger.warning(
                    f"AI service returned {response.status_code} on attempt {attempt + 1}: {response.text[:200]}"
                )
                last_error = AIServiceError(
                    f"AI service error: {response.status_code}",
                    status_code=response.status_code
                )

            except httpx.TimeoutException:
                logger.warning(f"AI service timeout on attempt {attempt + 1}")
                last_error = AIServiceError("AI service timeout", status_code=504)

            except httpx.ConnectError:
                logger.warning(f"AI service connection error on attempt {attempt + 1}")
                last_error = AIServiceError("AI service unavailable", status_code=503)

            except Exception as e:
                logger.error(f"AI service error on attempt {attempt + 1}: {e}")
                last_error = AIServiceError(str(e), status_code=500)

        raise last_error or AIServiceError("Unknown error")

    # =========================================================================
    # MARKETING ENDPOINTS
    # =========================================================================

    async def generate_content(
        self,
        topic: str,
        content_type: str = "social",
        tone: str = "professional",
        platform: str = "instagram",
        brand_context: Optional[str] = None
    ) -> dict:
        """
        Generate marketing content via AI (basic endpoint).

        Args:
            topic: Content topic or prompt
            content_type: Type (social, blog, ad, video)
            tone: Tone of voice
            platform: Target platform
            brand_context: Brand context for personalization

        Returns:
            Dict with content, metadata, provider
        """
        return await self._request(
            "POST",
            "/api/v1/marketing/content/generate",
            json={
                "type": content_type,
                "topic": topic,
                "tone": tone,
                "platform": platform,
                "brand_context": brand_context
            }
        )

    async def generate_content_pro(
        self,
        topic: str,
        post_type: str = "educational",
        platform: str = "instagram",
        sector: str = "tech",
        additional_context: Optional[str] = None,
        language: str = "it",
        generate_image_prompt: bool = True,
        brand_context: Optional[str] = None
    ) -> dict:
        """
        Generate PROFESSIONAL marketing content via AI with full Brand DNA integration.

        Uses POST_TYPE_PROMPTS and PLATFORM_FORMAT_RULES for platform-specific,
        structured content generation (HOOK → BODY → CTA → HASHTAG format).

        Args:
            topic: Content topic or prompt
            post_type: Type of post (lancio_prodotto, tip_giorno, caso_successo,
                       trend_settore, offerta_speciale, ai_business, educational,
                       testimonial, engagement)
            platform: Target platform (linkedin, instagram, facebook, twitter, tiktok)
            sector: Business sector (ristorazione, hospitality, legal, medical,
                    retail, manufacturing, tech, consulting)
            additional_context: Extra context for content generation
            language: Output language (it, en)
            generate_image_prompt: Whether to generate matching image prompt
            brand_context: Brand DNA context for personalization

        Returns:
            Dict with content, image_prompt, hashtags, cta_options, metadata, provider
        """
        return await self._request(
            "POST",
            "/api/v1/marketing/content/generate-pro",
            json={
                "topic": topic,
                "post_type": post_type,
                "platform": platform,
                "sector": sector,
                "additional_context": additional_context,
                "language": language,
                "generate_image_prompt": generate_image_prompt,
                "brand_context": brand_context
            }
        )

    async def generate_content_format(
        self,
        topic: str,
        content_format: str = "post",
        platform: str = "instagram",
        slides_count: int = 5,
        duration_seconds: int = 15,
        video_style: str = "dinamico",
        music_mood: str = "energetico",
        brand_context: Optional[str] = None
    ) -> dict:
        """
        Generate FORMAT-SPECIFIC content (Story, Carousel, Reel, Video).

        Power endpoint with MASTER prompts for structured slide-by-slide generation.

        Args:
            topic: Content topic or prompt
            content_format: Format type (post, story, carousel, reel, video)
            platform: Target platform
            slides_count: Number of slides for carousel/story
            duration_seconds: Duration for video/reel
            video_style: Style for video (dinamico, cinematografico, tutorial, etc.)
            music_mood: Music mood for video
            brand_context: Brand DNA context

        Returns:
            Dict with content, slides[], scenes[], cover_prompt, thumbnail_prompt, etc.
        """
        return await self._request(
            "POST",
            "/api/v1/marketing/content/generate-format",
            json={
                "topic": topic,
                "content_format": content_format,
                "platform": platform,
                "slides_count": slides_count,
                "duration_seconds": duration_seconds,
                "video_style": video_style,
                "music_mood": music_mood,
                "brand_context": brand_context
            },
            timeout=120.0  # Longer timeout for complex generation
        )

    def _map_to_aspect_ratio(self, width: int, height: int) -> str:
        """Map width/height to standard aspect ratio string."""
        ratio = width / height
        if abs(ratio - 1.0) < 0.1:
            return "1:1"
        elif abs(ratio - 16/9) < 0.1:
            return "16:9"
        elif abs(ratio - 9/16) < 0.1:
            return "9:16"
        elif abs(ratio - 4/3) < 0.1:
            return "4:3"
        elif abs(ratio - 3/4) < 0.1:
            return "3:4"
        elif abs(ratio - 4/5) < 0.1:
            return "4:5"
        else:
            return "1:1"  # Default

    async def generate_image(
        self,
        prompt: str,
        style: str = "professional",
        width: int = 1024,
        height: int = 1024,
        platform: str = "linkedin",
        apply_branding: bool = True,
        branding_position: str = "top_center",
        logo_url: Optional[str] = None,
        brand_name: Optional[str] = None,
        post_type: Optional[str] = None,
        sector: Optional[str] = None
    ) -> dict:
        """
        Generate AI image with full Brand DNA integration.

        Args:
            prompt: Image generation prompt
            style: Visual style
            width: Image width
            height: Image height
            platform: Target platform
            apply_branding: Whether to apply brand overlay
            branding_position: Position of branding
            logo_url: Custom logo URL (Brand DNA)
            brand_name: Brand name for footer
            post_type: Post type for style matching (lancio_prodotto, tip_giorno, etc.)
            sector: Business sector for context (tech, ristorazione, etc.)

        Returns:
            Dict with image_url, prompt_used, metadata
        """
        # Map width/height to aspect_ratio for AI Microservice
        aspect_ratio = self._map_to_aspect_ratio(width, height)

        return await self._request(
            "POST",
            "/api/v1/marketing/image/generate",
            json={
                "prompt": prompt,
                "style": style,
                "aspect_ratio": aspect_ratio,
                "platform": platform,
                "apply_branding": apply_branding,
                "logo_url": logo_url,
                "brand_name": brand_name or "StudioCentOS",
                "post_type": post_type or "",
                "sector": sector or "tech"
            },
            timeout=120.0  # Image generation takes longer
        )

    # =========================================================================
    # SUPPORT ENDPOINTS
    # =========================================================================

    async def chat(
        self,
        message: str,
        context: Optional[str] = None,
        provider: str = "groq"
    ) -> dict:
        """
        Chat with AI assistant.

        Args:
            message: User message
            context: Conversation context
            provider: LLM provider

        Returns:
            Dict with response, confidence, provider, sentiment
        """
        return await self._request(
            "POST",
            "/api/v1/support/chat",
            json={
                "message": message,
                "context": context,
                "provider": provider
            },
            timeout=30.0
        )

    # =========================================================================
    # TOOLAI ENDPOINTS
    # =========================================================================

    async def discover_tools(
        self,
        category: Optional[str] = None,
        limit: int = 10
    ) -> dict:
        """
        Discover AI tools.

        Args:
            category: Tool category filter
            limit: Max results

        Returns:
            Dict with tools list
        """
        return await self._request(
            "POST",
            "/api/v1/toolai/discover",
            json={
                "category": category,
                "limit": limit
            }
        )

    # =========================================================================
    # RAG ENDPOINTS
    # =========================================================================

    async def rag_list_documents(self, user_id: Optional[int] = None) -> list:
        """List all indexed documents."""
        params = {}
        if user_id:
            params["user_id"] = user_id

        client = await self._get_client()
        response = await client.get("/api/v1/rag/documents", params=params)

        if response.status_code == 200:
            return response.json()
        raise AIServiceError(f"Failed to list documents: {response.text}", status_code=response.status_code)

    async def rag_upload_document(
        self,
        file_content: bytes,
        filename: str,
        category: str,
        tags: str,
        user_id: int
    ) -> dict:
        """Upload document to RAG."""
        client = await self._get_client()

        files = {"file": (filename, file_content)}
        data = {
            "category": category,
            "tags": tags,
            "user_id": str(user_id)
        }

        # Note: httpx handles multipart/form-data automatically when 'files' is passed
        # We need to avoid setting Content-Type: application/json in this case
        # So we use a request-specific client or override headers?
        # _get_client sets headers with JSON content type.
        # We should create a temporary client or strip the header for this request.

        # Better: Use a separate request method or override headers in _request if possible.
        # But _request is for JSON.
        # Let's allow overriding headers in _get_client or make a raw request here.

        # Using headers=None to override default headers won't work if they are set on client init.
        # We'll make a new request with custom headers.

        headers = self.headers.copy()
        if "Content-Type" in headers:
            del headers["Content-Type"]  # Let httpx set boundary

        response = await client.post(
            "/api/v1/rag/documents/upload",
            files=files,
            data=data,
            headers=headers # Override client headers for this request
        )

        if response.status_code == 200:
            return response.json()
        raise AIServiceError(f"Failed to upload document: {response.text}", status_code=response.status_code)

    async def rag_delete_document(self, doc_id: str) -> dict:
        """Delete document."""
        return await self._request("DELETE", f"/api/v1/rag/documents/{doc_id}")

    async def rag_search(
        self,
        query: str,
        k: int = 5,
        threshold: float = 0.5,
        user_id: Optional[int] = None
    ) -> dict:
        """Search documents."""
        return await self._request(
            "POST",
            "/api/v1/rag/search",
            json={
                "query": query,
                "k": k,
                "threshold": threshold,
                "user_id": user_id
            }
        )

    async def rag_query(
        self,
        query: str,
        collection: str = "default",
        top_k: int = 5
    ) -> dict:
        """
        Query RAG system.

        Args:
            query: Search query
            collection: Vector collection name
            top_k: Number of results

        Returns:
            Dict with results, sources
        """
        return await self._request(
            "POST",
            "/api/v1/rag/query",
            json={
                "query": query,
                "collection": collection,
                "top_k": top_k
            }
        )

    # =========================================================================
    # HEALTH CHECK
    # =========================================================================

    async def health_check(self) -> dict:
        """
        Check AI service health.

        Returns:
            Dict with status, version, providers
        """
        try:
            return await self._request("GET", "/health", timeout=5.0)
        except AIServiceError:
            return {
                "status": "unavailable",
                "fallback": "enabled"
            }


# Singleton instance
ai_client = AIClient()


async def get_ai_client() -> AIClient:
    """Dependency injection for AI client."""
    return ai_client
