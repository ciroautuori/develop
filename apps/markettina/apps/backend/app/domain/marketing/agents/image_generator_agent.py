"""
Image Generation Agent - AI-Powered Image Creation.

This agent specializes in generating high-quality images for marketing content
using multiple AI providers (Google Gemini, Hugging Face, OpenAI).

Features:
    - Multi-provider support with fallback
    - Intelligent caching
    - Prompt enhancement
    - Cost tracking and optimization
    - Rate limiting

Tools:
    1. generate_image() - Generate image from prompt
    2. clear_cache() - Clear image cache
    3. get_statistics() - Get usage stats

Example:
    >>> agent = ImageGenerationAgent(config=config)
    >>> result = await agent.generate_image(
    ...     prompt="Modern office workspace",
    ...     style="professional",
    ...     width=1024,
    ...     height=1024
    ... )
"""

import asyncio
import base64
import hashlib
import json
import logging
import os
import time
from enum import Enum
from pathlib import Path
from typing import Any

import aiohttp
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.domain.marketing.agents.image_branding import ImageBranding
from app.infrastructure.ai.agents.base_agent import AgentCapability, AgentConfig, BaseAgent
from app.infrastructure.ai.agents.task import Task, TaskOutput

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & MODELS
# ============================================================================

class ImageProvider(str, Enum):
    """Supported image generation providers."""
    GOOGLE = "google"            # FREE - Gemini 2.5 Flash Image
    HUGGINGFACE = "huggingface"  # FREE - Stable Diffusion
    OPENAI = "openai"            # PAID - DALL-E 3


class ImageGenerationConfig(BaseModel):
    """Configuration for image generation task."""
    prompt: str = Field(..., description="Image description")
    style: str = Field(default="professional", description="Visual style")
    width: int = Field(default=1024, description="Image width")
    height: int = Field(default=1024, description="Image height")
    quality: str = Field(default="standard", description="Quality setting")
    apply_branding: bool = Field(default=True, description="Apply MARKETTINA branding")


class ImageResult(BaseModel):
    """Result from image generation."""
    image_url: str
    image_id: str
    prompt_used: str
    generation_time: float
    metadata: dict[str, Any]


# ============================================================================
# UTILITIES
# ============================================================================

class RateLimiter:
    """Token bucket rate limiter for API calls."""

    def __init__(self, requests_per_minute: int = 50):
        self.requests_per_minute = requests_per_minute
        self.tokens = requests_per_minute
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(
                self.requests_per_minute,
                self.tokens + (elapsed * self.requests_per_minute / 60)
            )
            self.last_update = now
            if self.tokens < 1:
                wait_time = (1 - self.tokens) * 60 / self.requests_per_minute
                await asyncio.sleep(wait_time)
                self.tokens = 1
            self.tokens -= 1


class ImageCache:
    """File-based cache for generated images."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = cache_dir / "cache_index.json"
        self.index = {}
        self._load_index()

    def _load_index(self):
        if self.index_file.exists():
            try:
                with open(self.index_file) as f:
                    self.index = json.load(f)
            except json.JSONDecodeError:
                self.index = {}

    def _save_index(self):
        try:
            with open(self.index_file, "w") as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")

    def get_cache_key(self, prompt: str, style: str, size: str) -> str:
        key_data = f"{prompt}:{style}:{size}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, cache_key: str) -> dict[str, Any] | None:
        return self.index.get(cache_key)

    def set(self, cache_key: str, result: dict[str, Any]):
        self.index[cache_key] = result
        self._save_index()


# ============================================================================
# IMAGE GENERATION AGENT
# ============================================================================

class ImageGenerationAgent(BaseAgent):
    """
    Image Generation Agent using multi-provider strategy.
    """

    def __init__(self, config: AgentConfig):
        super().__init__(config)

        # API Keys
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.hf_key = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HUGGINGFACE_TOKEN")
        self.google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")

        self.openai_client = AsyncOpenAI(api_key=self.openai_key) if self.openai_key else None

        # Priority: Google (Free) -> HF (Free) -> OpenAI (Paid)
        self.providers = [
            ImageProvider.GOOGLE,
            ImageProvider.HUGGINGFACE,
            ImageProvider.OPENAI
        ]

        # Infrastructure
        self.cache_dir = Path("media/cache/images")
        self.cache = ImageCache(self.cache_dir)
        self.rate_limiter = RateLimiter(requests_per_minute=50)

        # Metrics
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "errors": 0,
            "by_provider": {p.value: 0 for p in ImageProvider}
        }

        # Branding
        self.branding = ImageBranding()

    async def on_start(self) -> None:
        """Initialize agent resources."""
        await super().on_start()
        logger.info(f"ImageAgent started. Providers: {[p.value for p in self.providers]}")

    def get_capabilities(self) -> list[AgentCapability]:
        """Get agent capabilities."""
        return [
            AgentCapability(
                name="generate_image",
                description="Generate AI image from prompt",
                input_schema={"prompt": "str", "style": "str", "width": "int", "height": "int", "apply_branding": "bool"},
                output_schema={"image_url": "str", "metadata": "dict"}
            ),
            AgentCapability(
                name="get_statistics",
                description="Get usage statistics",
                input_schema={},
                output_schema={"stats": "dict"}
            )
        ]

    async def execute(self, task: Task) -> TaskOutput:
        """Execute task."""
        action = task.input.data.get("action", "generate")

        try:
            if action == "generate":
                config = ImageGenerationConfig(**task.input.data)
                result = await self.generate_image(config)
                return TaskOutput(
                    result=result.model_dump(),
                    metadata={"provider": result.metadata.get("provider")}
                )
            if action == "stats":
                return TaskOutput(result=self.stats)
            raise ValueError(f"Unknown action: {action}")

        except Exception as e:
            return TaskOutput(
                result={"error": str(e)},
                metadata={"status": "failed"}
            )

    async def generate_image(self, config: ImageGenerationConfig) -> ImageResult:
        """Generate image with caching and provider fallback."""
        self.stats["total_requests"] += 1

        # Check cache
        size = f"{config.width}x{config.height}"
        cache_key = self.cache.get_cache_key(config.prompt, config.style, size)
        cached = self.cache.get(cache_key)

        if cached:
            self.stats["cache_hits"] += 1
            return ImageResult(**cached)

        await self.rate_limiter.acquire()

        last_error = None
        for provider in self.providers:
            try:
                logger.info(f"Generating image with {provider.value}...")

                if provider == ImageProvider.GOOGLE:
                    result = await self._generate_google(config)
                elif provider == ImageProvider.HUGGINGFACE:
                    result = await self._generate_huggingface(config)
                elif provider == ImageProvider.OPENAI:
                    result = await self._generate_openai(config)
                else:
                    continue

                # Success
                self.stats["by_provider"][provider.value] += 1
                self.cache.set(cache_key, result.model_dump())
                return result

            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider.value} failed: {e}")
                continue

        self.stats["errors"] += 1
        raise Exception(f"All providers failed. Last error: {last_error}")

    # ... PROVIDER IMPLEMENTATIONS ...

    async def _generate_google(self, config: ImageGenerationConfig) -> ImageResult:
        """Generate with Google Gemini 2.5."""
        if not self.google_key:
            raise ValueError("GOOGLE_API_KEY not configured")

        start_time = time.time()
        enhanced_prompt = self._enhance_prompt(config.prompt, config.style)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={self.google_key}"

        payload = {
            "contents": [{"parts": [{"text": f"Generate an image: {enhanced_prompt}"}]}],
            "generationConfig": {"temperature": 1.0, "topP": 0.95, "topK": 40}
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"Google API error: {response.status} - {text}")

                data = await response.json()
                image_data = self._extract_google_image(data)

                if config.apply_branding:
                    image_data = self.branding.apply_branding(image_data)

                filename = self._save_image(image_data, "gemini", config.prompt)

                return ImageResult(
                    image_url=self._get_image_url(filename),
                    image_id=filename.split(".")[0],
                    prompt_used=enhanced_prompt,
                    generation_time=time.time() - start_time,
                    metadata={"provider": "google", "model": "gemini-2.5-flash-image", "cost": "FREE"}
                )

    async def _generate_huggingface(self, config: ImageGenerationConfig) -> ImageResult:
        """Generate with Hugging Face."""
        if not self.hf_key:
            raise ValueError("HUGGINGFACE_API_KEY not configured")

        start_time = time.time()
        enhanced_prompt = self._enhance_prompt(config.prompt, config.style)

        url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {"Authorization": f"Bearer {self.hf_key}"}
        payload = {"inputs": enhanced_prompt}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"HF API error: {response.status}")

                image_data = await response.read()

                if config.apply_branding:
                    image_data = self.branding.apply_branding(image_data)

                filename = self._save_image(image_data, "hf", config.prompt)

                return ImageResult(
                    image_url=self._get_image_url(filename),
                    image_id=filename.split(".")[0],
                    prompt_used=enhanced_prompt,
                    generation_time=time.time() - start_time,
                    metadata={"provider": "huggingface", "model": "sdxl", "cost": "FREE"}
                )

    async def _generate_openai(self, config: ImageGenerationConfig) -> ImageResult:
        """Generate with OpenAI."""
        if not self.openai_client:
            raise ValueError("OPENAI_API_KEY not configured")

        start_time = time.time()
        enhanced_prompt = self._enhance_prompt(config.prompt, config.style)

        response = await self.openai_client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        # If branding requested, download and process
        if config.apply_branding:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(response.data[0].url) as resp:
                        if resp.status == 200:
                            image_data = await resp.read()
                            image_data = self.branding.apply_branding(image_data)
                            filename = self._save_image(image_data, "dalle", config.prompt)

                            return ImageResult(
                                image_url=self._get_image_url(filename),
                                image_id=filename.split(".")[0],
                                prompt_used=response.data[0].revised_prompt or enhanced_prompt,
                                generation_time=time.time() - start_time,
                                metadata={"provider": "openai", "model": "dall-e-3", "cost": 0.04, "branded": True}
                            )
            except Exception as e:
                logger.warning(f"Failed to brand OpenAI image: {e}")
                # Fallback to original URL

        return ImageResult(
            image_url=response.data[0].url,
            image_id=f"dalle_{int(time.time())}",
            prompt_used=response.data[0].revised_prompt or enhanced_prompt,
            generation_time=time.time() - start_time,
            metadata={"provider": "openai", "model": "dall-e-3", "cost": 0.04}
        )

    def _extract_google_image(self, data: dict) -> bytes:
        """Extract base64 image from Google response."""
        try:
            candidates = data.get("candidates", [])
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                if "inlineData" in part:
                    return base64.b64decode(part["inlineData"]["data"])
            raise Exception("No image found in response")
        except Exception as e:
            raise Exception(f"Failed to parse Google response: {e}")

    def _save_image(self, data: bytes, prefix: str, prompt: str) -> str:
        """Save image data to disk and return filename."""
        # Note: In production, this should upload to S3/GCS
        # For now, we assume a shared volume or local serving

        # Ensure directory exists
        save_dir = Path("media/generated")
        save_dir.mkdir(parents=True, exist_ok=True)

        hash_id = hashlib.md5(prompt.encode()).hexdigest()[:8]
        filename = f"{prefix}_{int(time.time())}_{hash_id}.png"
        file_path = save_dir / filename

        with open(file_path, "wb") as f:
            f.write(data)

        return filename

    def _get_image_url(self, filename: str) -> str:
        """Get full URL for saved image."""
        base_url = os.getenv("BASE_URL", "http://localhost:8002")
        return f"{base_url}/media/generated/{filename}"

    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance prompt based on style."""
        styles = {
            "professional": "professional corporate photography, high quality, 8k, clean lighting",
            "creative": "artistic, vibrant colors, creative composition, digital art",
            "minimalist": "minimalist design, clean lines, simple, flat design",
            "modern": "modern aesthetic, sleek, contemporary, lifestyle"
        }
        modifier = styles.get(style, styles["professional"])
        return f"{prompt}, {modifier}"
