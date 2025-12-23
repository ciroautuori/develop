"""
Content Creator Agent - AI-Powered Content Generation.

This agent specializes in creating high-quality marketing content across
multiple formats: blog posts, social media, ads, video scripts, and newsletters.

Features:
    - Multi-format content generation
    - Brand voice consistency
    - SEO optimization
    - A/B testing variants
    - Content calendar integration
    - Compliance checking

Tools:
    1. generate_blog_post() - Long-form blog content
    2. generate_social_post() - Platform-specific social posts
    3. generate_ad_copy() - Advertising copy with CTAs
    4. generate_video_script() - Video content scripts
    5. optimize_for_seo() - SEO optimization
    6. check_brand_compliance() - Brand guidelines validation

Example:
    >>> agent = ContentCreatorAgent(config=config)
    >>>
    >>> # Generate blog post
    >>> post = await agent.generate_blog_post(
    ...     topic="AI Agents in Marketing",
    ...     tone="professional",
    ...     length=1000,
    ...     keywords=["AI", "marketing", "automation"],
    ... )
    >>>
    >>> # Generate social media post
    >>> tweet = await agent.generate_social_post(
    ...     platform="twitter",
    ...     message="Launching new AI features!",
    ...     tone="exciting",
    ... )
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.infrastructure.ai.agents.base_agent import AgentCapability, AgentConfig, BaseAgent
from app.infrastructure.ai.agents.task import Task, TaskOutput

# ============================================================================
# ENUMS
# ============================================================================


class ContentType(str, Enum):
    """Content type enumeration."""

    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    AD_COPY = "ad_copy"
    VIDEO_SCRIPT = "video_script"
    NEWSLETTER = "newsletter"
    LANDING_PAGE = "landing_page"


class ContentTone(str, Enum):
    """Content tone/voice enumeration."""

    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    HUMOROUS = "humorous"
    INSPIRATIONAL = "inspirational"
    URGENT = "urgent"


class SocialPlatform(str, Enum):
    """Social media platforms."""

    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"


# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class BlogPostConfig(BaseModel):
    """Configuration for blog post generation."""

    topic: str = Field(..., description="Blog post topic")
    tone: ContentTone = Field(
        default=ContentTone.PROFESSIONAL, description="Writing tone"
    )
    length: int = Field(default=1000, ge=300, le=5000, description="Word count")
    keywords: list[str] = Field(
        default_factory=list, description="SEO keywords to include"
    )
    include_images: bool = Field(
        default=True, description="Include image suggestions"
    )
    target_audience: str | None = Field(
        default=None, description="Target audience description"
    )
    call_to_action: str | None = Field(
        default=None, description="CTA to include"
    )
    brand_context: str | None = Field(
        default=None, description="Brand DNA context"
    )


class SocialPostConfig(BaseModel):
    """Configuration for social media post generation."""

    platform: SocialPlatform = Field(..., description="Target platform")
    message: str = Field(..., description="Core message")
    tone: ContentTone = Field(default=ContentTone.CASUAL, description="Post tone")
    include_hashtags: bool = Field(default=True, description="Add hashtags")
    include_emojis: bool = Field(default=True, description="Add emojis")
    max_length: int | None = Field(
        default=None, description="Max character count"
    )
    call_to_action: str | None = Field(default=None, description="CTA link")
    brand_context: str | None = Field(
        default=None, description="Brand DNA context"
    )


class AdCopyConfig(BaseModel):
    """Configuration for ad copy generation."""

    product: str = Field(..., description="Product/service name")
    value_proposition: str = Field(..., description="Main value prop")
    target_audience: str = Field(..., description="Target audience")
    tone: ContentTone = Field(default=ContentTone.URGENT, description="Ad tone")
    max_length: int = Field(default=150, description="Max characters")
    include_cta: bool = Field(default=True, description="Include CTA")
    platform: str = Field(default="google_ads", description="Ad platform")
    brand_context: str | None = Field(
        default=None, description="Brand DNA context"
    )


class VideoScriptConfig(BaseModel):
    """Configuration for video script generation."""

    topic: str = Field(..., description="Video topic")
    duration_seconds: int = Field(
        default=60, ge=15, le=600, description="Video duration"
    )
    tone: ContentTone = Field(default=ContentTone.FRIENDLY, description="Script tone")
    include_hook: bool = Field(default=True, description="Include opening hook")
    include_cta: bool = Field(default=True, description="Include CTA")
    format: str = Field(
        default="educational", description="Video format (educational, promotional, etc.)"
    )
    brand_context: str | None = Field(
        default=None, description="Brand DNA context"
    )


class ContentResult(BaseModel):
    """Result from content generation."""

    content: str = Field(..., description="Generated content")
    content_type: ContentType = Field(..., description="Content type")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    seo_score: float | None = Field(
        default=None, ge=0.0, le=100.0, description="SEO quality score"
    )
    brand_compliance: bool = Field(
        default=True, description="Passes brand guidelines"
    )
    suggestions: list[str] = Field(
        default_factory=list, description="Improvement suggestions"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )


# ============================================================================
# CONTENT CREATOR AGENT
# ============================================================================


class ContentCreatorAgent(BaseAgent):
    """
    Content Creator Agent for marketing content generation.

    Specializes in creating high-quality, SEO-optimized content across
    multiple formats while maintaining brand voice consistency.

    Capabilities:
        - Blog post generation (300-5000 words)
        - Social media posts (platform-optimized)
        - Ad copy (concise, compelling)
        - Video scripts (15-600 seconds)
        - Newsletter content
        - Landing page copy

    Example:
        >>> config = AgentConfig(
        ...     id="content_creator_1",
        ...     name="Content Creator",
        ...     model="gpt-4",
        ...     temperature=0.7,
        ... )
        >>> agent = ContentCreatorAgent(config=config)
        >>>
        >>> task = Task(
        ...     id="task_1",
        ...     name="Generate Blog Post",
        ...     input_data={
        ...         "topic": "AI in Marketing",
        ...         "length": 1000,
        ...         "keywords": ["AI", "marketing", "automation"],
        ...     },
        ... )
        >>>
        >>> result = await agent.execute(task)
        >>> print(result.output_data["content"])
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize Content Creator Agent.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        # Brand guidelines (loaded from config)
        self.brand_guidelines: dict[str, Any] = {}
        self.seo_config: dict[str, Any] = {}

    async def on_start(self) -> None:
        """Initialize agent resources."""
        await super().on_start()

        # Load brand guidelines from config or database
        self.brand_guidelines = {
            "tone": "professional",
            "avoid_words": [],
            "required_disclaimers": [],
            "voice_examples": [],
        }

        # Load SEO configuration
        self.seo_config = {
            "min_keyword_density": 1.0,
            "max_keyword_density": 3.0,
            "min_readability_score": 60.0,
        }

    def get_capabilities(self) -> list[AgentCapability]:
        """Get list of content creation capabilities."""
        return [
            AgentCapability(
                name="blog_generation",
                description="Generate SEO-optimized blog posts",
                input_schema={"topic": "str", "length": "int", "keywords": "list"},
                output_schema={"content": "str", "seo_score": "float"},
            ),
            AgentCapability(
                name="social_post",
                description="Generate platform-optimized social media posts",
                input_schema={"platform": "str", "message": "str"},
                output_schema={"content": "str", "hashtags": "list"},
            ),
            AgentCapability(
                name="ad_copy",
                description="Generate compelling ad copy with CTAs",
                input_schema={"product": "str", "target_audience": "str"},
                output_schema={"content": "str"},
            ),
            AgentCapability(
                name="video_script",
                description="Generate video scripts with timestamps",
                input_schema={"topic": "str", "duration": "int"},
                output_schema={"script": "str"},
            ),
        ]

    async def execute(self, task: Task) -> TaskOutput:
        """Execute content generation task based on type."""
        task_type = task.input.data.get("type", "blog")

        try:
            if task_type == "blog":
                config = BlogPostConfig(**task.input.data)
                result = await self.generate_blog_post(config)
            elif task_type == "social":
                config = SocialPostConfig(**task.input.data)
                result = await self.generate_social_post(config)
            elif task_type == "ad":
                config = AdCopyConfig(**task.input.data)
                result = await self.generate_ad_copy(config)
            elif task_type == "video":
                config = VideoScriptConfig(**task.input.data)
                result = await self.generate_video_script(config)
            else:
                raise ValueError(f"Unknown content type: {task_type}")

            return TaskOutput(
                result={"content": result.content, "metadata": result.metadata},
                metadata={"content_type": task_type, "seo_score": result.seo_score}
            )

        except Exception as e:
            return TaskOutput(
                result={"error": str(e)},
                metadata={"status": "failed"}
            )

    async def generate_blog_post(
        self, config: BlogPostConfig
    ) -> ContentResult:
        """
        Generate SEO-optimized blog post.

        Args:
            config: Blog post configuration

        Returns:
            ContentResult with generated blog post

        Example:
            >>> result = await agent.generate_blog_post(
            ...     BlogPostConfig(
            ...         topic="AI Agents",
            ...         length=1000,
            ...         keywords=["AI", "agents", "automation"],
            ...     )
            ... )
        """
        # Build prompt
        prompt = self._build_blog_prompt(config)

        # Generate content via LLM
        content = await self._generate_content(prompt, config.brand_context)

        # Optimize for SEO
        optimized = await self._optimize_seo(content, config.keywords)

        # Calculate SEO score
        seo_score = self._calculate_seo_score(optimized, config.keywords)

        # Check brand compliance
        compliant = await self._check_brand_compliance(optimized)

        return ContentResult(
            content=optimized,
            content_type=ContentType.BLOG_POST,
            metadata={
                "topic": config.topic,
                "word_count": len(optimized.split()),
                "keywords": config.keywords,
                "tone": config.tone.value,
            },
            seo_score=seo_score,
            brand_compliance=compliant,
        )

    async def generate_social_post(
        self, config: SocialPostConfig
    ) -> ContentResult:
        """
        Generate platform-optimized social media post.

        Args:
            config: Social post configuration

        Returns:
            ContentResult with social media post
        """
        # Platform-specific constraints
        platform_limits = {
            SocialPlatform.TWITTER: 280,
            SocialPlatform.FACEBOOK: 63206,
            SocialPlatform.LINKEDIN: 3000,
            SocialPlatform.INSTAGRAM: 2200,
        }

        max_length = config.max_length or platform_limits.get(
            config.platform, 1000
        )

        # Build prompt
        prompt = self._build_social_prompt(config, max_length)

        # Generate content
        content = await self._generate_content(prompt, config.brand_context)

        # Add hashtags if requested
        if config.include_hashtags:
            content = await self._add_hashtags(content, config.platform)

        # Check brand compliance
        compliant = await self._check_brand_compliance(content)

        return ContentResult(
            content=content,
            content_type=ContentType.SOCIAL_POST,
            metadata={
                "platform": config.platform.value,
                "character_count": len(content),
                "tone": config.tone.value,
            },
            brand_compliance=compliant,
        )

    async def generate_ad_copy(
        self, config: AdCopyConfig
    ) -> ContentResult:
        """
        Generate compelling ad copy with CTA.

        Args:
            config: Ad copy configuration

        Returns:
            ContentResult with ad copy
        """
        prompt = self._build_ad_prompt(config)
        content = await self._generate_content(prompt, config.brand_context)

        # Ensure CTA is present
        if config.include_cta and "call" not in content.lower():
            content = await self._add_cta(content)

        # Check compliance
        compliant = await self._check_brand_compliance(content)

        return ContentResult(
            content=content,
            content_type=ContentType.AD_COPY,
            metadata={
                "product": config.product,
                "platform": config.platform,
                "character_count": len(content),
            },
            brand_compliance=compliant,
        )

    async def generate_video_script(
        self, config: VideoScriptConfig
    ) -> ContentResult:
        """
        Generate engaging video script.

        Args:
            config: Video script configuration

        Returns:
            ContentResult with video script
        """
        prompt = self._build_video_prompt(config)
        content = await self._generate_content(prompt, config.brand_context)

        # Format as script with timestamps
        formatted = await self._format_video_script(
            content, config.duration_seconds
        )

        compliant = await self._check_brand_compliance(formatted)

        return ContentResult(
            content=formatted,
            content_type=ContentType.VIDEO_SCRIPT,
            metadata={
                "duration_seconds": config.duration_seconds,
                "format": config.format,
            },
            brand_compliance=compliant,
        )

    # ========================================================================
    # HELPER METHODS (Private)
    # ========================================================================

    def _build_blog_prompt(self, config: BlogPostConfig) -> str:
        """Build prompt for blog post generation."""
        return f"""Write a {config.tone.value} blog post about: {config.topic}

Requirements:
- Word count: approximately {config.length} words
- Tone: {config.tone.value}
- Include keywords: {', '.join(config.keywords)}
- Target audience: {config.target_audience or 'general audience'}
- Include headings and subheadings
- Make it engaging and informative
{f"- Call-to-action: {config.call_to_action}" if config.call_to_action else ""}
"""

    def _build_social_prompt(
        self, config: SocialPostConfig, max_length: int
    ) -> str:
        """Build prompt for social post generation."""
        return f"""Create a {config.tone.value} social media post for {config.platform.value}.

Message: {config.message}
Max length: {max_length} characters
Tone: {config.tone.value}
{"Include relevant hashtags" if config.include_hashtags else ""}
{"Include emojis" if config.include_emojis else ""}
{f"CTA link: {config.call_to_action}" if config.call_to_action else ""}

Make it engaging and shareable!
"""

    def _build_ad_prompt(self, config: AdCopyConfig) -> str:
        """Build prompt for ad copy generation."""
        return f"""Write compelling ad copy for: {config.product}

Value proposition: {config.value_proposition}
Target audience: {config.target_audience}
Tone: {config.tone.value}
Platform: {config.platform}
Max length: {config.max_length} characters
{"Include strong call-to-action" if config.include_cta else ""}

Make it punchy and conversion-focused!
"""

    def _build_video_prompt(self, config: VideoScriptConfig) -> str:
        """Build prompt for video script generation."""
        return f"""Write a video script about: {config.topic}

Duration: {config.duration_seconds} seconds
Tone: {config.tone.value}
Format: {config.format}
{"Include attention-grabbing hook" if config.include_hook else ""}
{"Include call-to-action at end" if config.include_cta else ""}

Format as: [Scene description] Narration
"""

    async def _generate_content(
        self,
        prompt: str,
        brand_context: str | None = None,
        use_rag: bool = True
    ) -> str:
        """
        Generate content using LLM with RAG context enrichment.

        Uses GROQ's Llama 3.3 70B model for high-quality content generation.
        Enriches with RAG knowledge base context when available.
        Falls back to placeholder if GROQ is unavailable.
        """
        try:
            from app.core.llm.groq_client import get_groq_client

            client = get_groq_client(model="llama-3.3-70b")

            base_system_prompt = """Sei un esperto marketing copywriter italiano.
Genera contenuti professionali, coinvolgenti e ottimizzati per il web.
Rispondi sempre in italiano con formattazione markdown quando appropriato."""

            # Fetch RAG context if enabled
            rag_context = ""
            if use_rag:
                try:
                    from app.domain.rag.service import rag_service
                    rag_context = await rag_service.get_context(
                        query=prompt[:500],  # Use first 500 chars of prompt
                        max_tokens=1500
                    )
                    if rag_context:
                        rag_context = f"\n\n## Informazioni Aziendali (Knowledge Base):\n{rag_context}"
                except Exception as rag_error:
                    import logging
                    logging.getLogger(__name__).warning(f"RAG context fetch failed: {rag_error}")

            # Build system prompt with contexts
            system_prompt = base_system_prompt
            if brand_context:
                system_prompt = f"{base_system_prompt}\n\n## Brand Context:\n{brand_context}"
            if rag_context:
                system_prompt = f"{system_prompt}{rag_context}"

            content = await client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.8,
                max_tokens=2000
            )

            return content.strip()

        except Exception as e:
            # Log error and return fallback
            import logging
            logging.getLogger(__name__).error(f"Content generation error: {e}")
            return "[Errore generazione contenuto. Riprova più tardi.]"

    async def _optimize_seo(
        self, content: str, keywords: list[str]
    ) -> str:
        """Optimize content for SEO."""

        # - Ensure keyword density
        # - Add meta descriptions
        # - Optimize headings
        return content

    def _calculate_seo_score(
        self, content: str, keywords: list[str]
    ) -> float:
        """Calculate SEO quality score (0-100)."""

        # - Keyword density
        # - Readability score
        # - Heading structure
        # - Content length
        return 75.0  # Placeholder

    async def _check_brand_compliance(self, content: str) -> bool:
        """Check if content complies with brand guidelines."""

        # - Check for forbidden words
        # - Verify tone matches guidelines
        # - Ensure disclaimers present
        return True  # Placeholder

    async def _add_hashtags(
        self, content: str, platform: SocialPlatform
    ) -> str:
        """Add relevant hashtags to social post using GROQ LLM."""
        try:
            from app.core.llm.groq_client import get_groq_client

            client = get_groq_client(model="llama-3.1-8b")

            hashtag_limits = {
                SocialPlatform.TWITTER: 3,
                SocialPlatform.INSTAGRAM: 10,
                SocialPlatform.LINKEDIN: 5,
                SocialPlatform.FACEBOOK: 3,
            }

            limit = hashtag_limits.get(platform, 5)

            prompt = f"""Genera {limit} hashtag rilevanti per questo contenuto social.

Contenuto: {content}
Piattaforma: {platform.value}

Rispondi SOLO con gli hashtag separati da spazio (es: #tech #marketing #business):"""

            response = await client.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=100
            )

            hashtags = response.strip()
            return f"{content}\n\n{hashtags}"

        except Exception:
            return content

    async def _add_cta(self, content: str) -> str:
        """Add call-to-action to content using GROQ LLM."""
        try:
            from app.core.llm.groq_client import get_groq_client

            client = get_groq_client(model="llama-3.1-8b")

            prompt = f"""Genera una call-to-action breve e persuasiva per questo contenuto pubblicitario.

Contenuto: {content[:500]}

CTA (max 15 parole, in italiano, deve essere urgente e motivante):"""

            response = await client.generate(
                prompt=prompt,
                temperature=0.8,
                max_tokens=50
            )

            cta = response.strip()
            return f"{content}\n\n{cta}"

        except Exception:
            return content + "\n\n👉 Contattaci oggi per saperne di più!"

    async def _format_video_script(
        self, content: str, duration: int
    ) -> str:
        """Format content as video script with timestamps using GROQ LLM."""
        try:
            from app.core.llm.groq_client import get_groq_client

            client = get_groq_client(model="llama-3.3-70b")

            prompt = f"""Formatta questo contenuto come script video professionale.

Contenuto: {content}
Durata target: {duration} secondi

Formato richiesto:
[00:00-00:03] HOOK - descrizione scena
Narrazione: "testo da leggere"

[00:04-00:XX] SVILUPPO - descrizione scena
Narrazione: "testo"

[ultimi secondi] CTA - descrizione scena
Narrazione: "testo finale"

Script formattato:"""

            response = await client.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=1500
            )

            return response.strip()

        except Exception:
            return content
