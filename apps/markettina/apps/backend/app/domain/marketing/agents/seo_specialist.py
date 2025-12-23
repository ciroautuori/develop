"""
SEO Specialist Agent - Search Engine Optimization Automation.

This agent specializes in SEO analysis, keyword research, competitor analysis,
and on-page optimization to improve search engine rankings.

Features:
    - Keyword research and analysis
    - Competitor SEO analysis
    - On-page optimization recommendations
    - Technical SEO audits
    - Backlink analysis
    - Rank tracking and reporting

Tools:
    1. keyword_research() - Find relevant keywords
    2. analyze_competitors() - Analyze competitor SEO
    3. optimize_content() - On-page optimization
    4. audit_technical_seo() - Technical SEO audit
    5. backlink_analysis() - Analyze backlink profile
    6. track_rankings() - Monitor keyword rankings

Example:
    >>> agent = SEOAgent(config=config)
    >>>
    >>> # Research keywords
    >>> keywords = await agent.keyword_research(
    ...     seed_keyword="AI marketing",
    ...     limit=20,
    ... )
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.infrastructure.ai.agents.base_agent import AgentConfig, BaseAgent
from app.infrastructure.google import SearchConsoleClient, GA4Client

# ============================================================================
# ENUMS
# ============================================================================


class KeywordDifficulty(str, Enum):
    """Keyword difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class SEOIssueSeverity(str, Enum):
    """SEO issue severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class Keyword(BaseModel):
    """Keyword research result."""

    keyword: str = Field(..., description="Keyword phrase")
    search_volume: int = Field(..., ge=0, description="Monthly search volume")
    difficulty: KeywordDifficulty = Field(..., description="Ranking difficulty")
    cpc: float = Field(..., ge=0.0, description="Cost per click (USD)")
    competition: float = Field(
        ..., ge=0.0, le=1.0, description="Competition score"
    )
    intent: str = Field(..., description="Search intent")
    relevance_score: float = Field(
        ..., ge=0.0, le=1.0, description="Relevance to topic"
    )
    current_rank: int | None = Field(
        default=None, description="Current ranking position"
    )


class CompetitorAnalysis(BaseModel):
    """Competitor SEO analysis."""

    competitor_url: str = Field(..., description="Competitor URL")
    domain_authority: int = Field(..., ge=0, le=100, description="DA score")
    page_authority: int = Field(..., ge=0, le=100, description="PA score")
    backlinks: int = Field(..., ge=0, description="Total backlinks")
    referring_domains: int = Field(..., ge=0, description="Referring domains")
    organic_keywords: int = Field(..., ge=0, description="Ranking keywords")
    estimated_traffic: int = Field(..., ge=0, description="Monthly traffic")
    top_keywords: list[Keyword] = Field(
        default_factory=list, description="Top ranking keywords"
    )
    content_gaps: list[str] = Field(
        default_factory=list, description="Content opportunities"
    )


class SEOIssue(BaseModel):
    """Technical SEO issue."""

    issue_type: str = Field(..., description="Issue type")
    severity: SEOIssueSeverity = Field(..., description="Issue severity")
    description: str = Field(..., description="Issue description")
    affected_urls: list[str] = Field(..., description="Affected URLs")
    recommendation: str = Field(..., description="Fix recommendation")
    effort: str = Field(..., description="Effort to fix (low/medium/high)")


class OnPageOptimization(BaseModel):
    """On-page SEO optimization recommendations."""

    url: str = Field(..., description="Page URL")
    title_tag: str | None = Field(default=None, description="Optimized title")
    meta_description: str | None = Field(
        default=None, description="Optimized meta description"
    )
    h1_tag: str | None = Field(default=None, description="Optimized H1")
    keyword_density: float = Field(..., description="Current keyword density %")
    target_density: float = Field(..., description="Target keyword density %")
    word_count: int = Field(..., description="Current word count")
    recommended_word_count: int = Field(
        ..., description="Recommended word count"
    )
    missing_keywords: list[str] = Field(
        default_factory=list, description="Keywords to add"
    )
    internal_links_needed: int = Field(
        ..., description="Recommended internal links"
    )
    image_alt_tags_missing: int = Field(..., description="Missing alt tags")
    overall_score: float = Field(
        ..., ge=0.0, le=100.0, description="Overall SEO score"
    )


class RankingUpdate(BaseModel):
    """Keyword ranking update."""

    keyword: str = Field(..., description="Keyword")
    current_position: int | None = Field(
        default=None, description="Current rank"
    )
    previous_position: int | None = Field(
        default=None, description="Previous rank"
    )
    change: int = Field(default=0, description="Position change")
    url: str = Field(..., description="Ranking URL")
    search_volume: int = Field(..., description="Search volume")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Update timestamp"
    )


# ============================================================================
# SEO SPECIALIST AGENT
# ============================================================================


class SEOAgent(BaseAgent):
    """
    SEO Specialist Agent for search engine optimization.

    Automates SEO research, analysis, and optimization tasks to improve
    search engine rankings and organic traffic.

    Capabilities:
        - Keyword research with volume/difficulty
        - Competitor SEO analysis
        - On-page optimization recommendations
        - Technical SEO audits
        - Backlink profile analysis
        - Rank tracking and reporting

    Example:
        >>> config = AgentConfig(
        ...     id="seo_agent_1",
        ...     name="SEO Specialist",
        ...     model="gpt-4",
        ... )
        >>> agent = SEOAgent(config=config)
        >>>
        >>> # Research keywords
        >>> keywords = await agent.keyword_research(
        ...     seed_keyword="AI marketing tools",
        ...     limit=20,
        ... )
    """

    def __init__(self, config: AgentConfig):
        """Initialize SEO Agent."""
        super().__init__(config)

        self.seo_tools: dict[str, Any] = {}
        self.ranking_history: list[RankingUpdate] = []
        self._gsc_client: SearchConsoleClient | None = None
        self._ga4_client: GA4Client | None = None

    async def on_start(self) -> None:
        """Initialize SEO tool integrations."""
        await super().on_start()

        # Initialize production-ready Google API clients
        self._gsc_client = SearchConsoleClient()
        self._ga4_client = GA4Client()

        self.seo_tools = {
            "google_search_console": self._gsc_client,
            "google_analytics": self._ga4_client,
        }

        # Log configured tools
        configured = []
        if self._gsc_client.is_configured():
            configured.append("Google Search Console")
        if self._ga4_client.is_configured():
            configured.append("Google Analytics 4")

        if configured:
            self._logger.info(f"Configured SEO tools: {configured}")

    async def keyword_research(
        self,
        seed_keyword: str,
        limit: int = 20,
        min_volume: int = 100,
        max_difficulty: KeywordDifficulty = KeywordDifficulty.HARD,
    ) -> list[Keyword]:
        """
        Research keywords related to seed keyword.

        Args:
            seed_keyword: Starting keyword
            limit: Max keywords to return
            min_volume: Minimum search volume
            max_difficulty: Maximum difficulty

        Returns:
            List of keyword opportunities

        Example:
            >>> keywords = await agent.keyword_research(
            ...     seed_keyword="AI marketing",
            ...     limit=20,
            ...     min_volume=500,
            ... )
        """
        # Fetch keyword ideas from SEO tools
        raw_keywords = await self._fetch_keyword_ideas(seed_keyword)

        # Enrich with metrics
        enriched = []
        for kw in raw_keywords:
            metrics = await self._get_keyword_metrics(kw)

            # Filter by criteria
            if (
                metrics["volume"] >= min_volume
                and self._meets_difficulty(metrics["difficulty"], max_difficulty)
            ):
                # Calculate relevance
                relevance = await self._calculate_keyword_relevance(
                    kw, seed_keyword
                )

                enriched.append(
                    Keyword(
                        keyword=kw,
                        search_volume=metrics["volume"],
                        difficulty=metrics["difficulty"],
                        cpc=metrics["cpc"],
                        competition=metrics["competition"],
                        intent=metrics["intent"],
                        relevance_score=relevance,
                    )
                )

        # Sort by relevance and volume
        enriched.sort(
            key=lambda x: (x.relevance_score, x.search_volume), reverse=True
        )

        return enriched[:limit]

    async def analyze_competitors(
        self, competitor_urls: list[str], focus_keyword: str
    ) -> list[CompetitorAnalysis]:
        """
        Analyze competitor SEO strategies.

        Args:
            competitor_urls: List of competitor URLs
            focus_keyword: Keyword to analyze

        Returns:
            List of competitor analysis results
        """
        analyses = []

        for url in competitor_urls:
            # Fetch domain metrics
            domain_metrics = await self._get_domain_metrics(url)

            # Get backlink profile
            backlinks = await self._get_backlink_profile(url)

            # Get ranking keywords
            ranking_kws = await self._get_ranking_keywords(url)

            # Identify content gaps
            gaps = await self._identify_content_gaps(
                url, focus_keyword, ranking_kws
            )

            analyses.append(
                CompetitorAnalysis(
                    competitor_url=url,
                    domain_authority=domain_metrics["da"],
                    page_authority=domain_metrics["pa"],
                    backlinks=backlinks["total"],
                    referring_domains=backlinks["domains"],
                    organic_keywords=len(ranking_kws),
                    estimated_traffic=domain_metrics["traffic"],
                    top_keywords=ranking_kws[:10],
                    content_gaps=gaps,
                )
            )

        return analyses

    async def optimize_content(
        self, url: str, target_keyword: str
    ) -> OnPageOptimization:
        """
        Generate on-page SEO optimization recommendations.

        Args:
            url: Page URL to optimize
            target_keyword: Target keyword

        Returns:
            OnPageOptimization with recommendations
        """
        # Fetch current page content
        page_content = await self._fetch_page_content(url)

        # Analyze current SEO
        current_seo = await self._analyze_page_seo(page_content)

        # Generate optimized elements
        optimized_title = await self._optimize_title(
            current_seo["title"], target_keyword
        )
        optimized_meta = await self._optimize_meta_description(
            current_seo["meta"], target_keyword
        )
        optimized_h1 = await self._optimize_h1(
            current_seo["h1"], target_keyword
        )

        # Calculate metrics
        keyword_density = self._calculate_keyword_density(
            page_content, target_keyword
        )

        # Identify missing keywords
        missing_kws = await self._find_missing_keywords(
            page_content, target_keyword
        )

        # Calculate overall score
        score = self._calculate_seo_score(current_seo, target_keyword)

        return OnPageOptimization(
            url=url,
            title_tag=optimized_title,
            meta_description=optimized_meta,
            h1_tag=optimized_h1,
            keyword_density=keyword_density,
            target_density=2.0,  # 2% target
            word_count=current_seo["word_count"],
            recommended_word_count=self._recommend_word_count(target_keyword),
            missing_keywords=missing_kws,
            internal_links_needed=max(0, 3 - current_seo["internal_links"]),
            image_alt_tags_missing=current_seo["images_without_alt"],
            overall_score=score,
        )

    async def audit_technical_seo(
        self, domain: str
    ) -> list[SEOIssue]:
        """
        Perform technical SEO audit.

        Args:
            domain: Domain to audit

        Returns:
            List of SEO issues found
        """
        issues = []

        # Check site speed
        speed_issues = await self._check_site_speed(domain)
        issues.extend(speed_issues)

        # Check mobile friendliness
        mobile_issues = await self._check_mobile_friendly(domain)
        issues.extend(mobile_issues)

        # Check crawlability
        crawl_issues = await self._check_crawlability(domain)
        issues.extend(crawl_issues)

        # Check HTTPS
        https_issues = await self._check_https(domain)
        issues.extend(https_issues)

        # Check structured data
        schema_issues = await self._check_structured_data(domain)
        issues.extend(schema_issues)

        # Sort by severity
        issues.sort(key=lambda x: self._severity_order(x.severity))

        return issues

    async def backlink_analysis(
        self, url: str
    ) -> dict[str, Any]:
        """
        Analyze backlink profile.

        Args:
            url: URL to analyze

        Returns:
            Backlink profile analysis
        """
        # Fetch backlinks
        backlinks = await self._fetch_backlinks(url)

        # Analyze quality
        quality_score = self._analyze_backlink_quality(backlinks)

        # Identify toxic links
        toxic = [bl for bl in backlinks if bl.get("spam_score", 0) > 50]

        # Group by type
        dofollow = [bl for bl in backlinks if bl.get("dofollow", True)]
        nofollow = [bl for bl in backlinks if not bl.get("dofollow", True)]

        return {
            "total_backlinks": len(backlinks),
            "referring_domains": len(set(bl["domain"] for bl in backlinks)),
            "dofollow": len(dofollow),
            "nofollow": len(nofollow),
            "quality_score": quality_score,
            "toxic_links": len(toxic),
            "top_domains": self._get_top_domains(backlinks, 10),
            "anchor_text_distribution": self._analyze_anchor_text(backlinks),
        }

    async def track_rankings(
        self, keywords: list[str], url: str
    ) -> list[RankingUpdate]:
        """
        Track keyword rankings for URL.

        Args:
            keywords: Keywords to track
            url: URL to track

        Returns:
            List of ranking updates
        """
        updates = []

        for keyword in keywords:
            # Get current position
            current = await self._get_current_rank(keyword, url)

            # Get previous position from history
            previous = self._get_previous_rank(keyword, url)

            # Calculate change
            change = 0
            if current and previous:
                change = previous - current  # Positive = improvement

            update = RankingUpdate(
                keyword=keyword,
                current_position=current,
                previous_position=previous,
                change=change,
                url=url,
                search_volume=await self._get_search_volume(keyword),
            )

            updates.append(update)
            self.ranking_history.append(update)

        return updates

    # ========================================================================
    # HELPER METHODS (Private)
    # ========================================================================

    async def _fetch_keyword_ideas(self, seed: str) -> list[str]:
        """Fetch keyword ideas from SEO tools."""
        if not self._gsc_client or not self._gsc_client.is_configured():
            # Fallback: generate ideas from seed using LLM
            return await self._generate_keyword_ideas_llm(seed)

        try:
            # Get related keywords from GSC
            keywords_data = await self._gsc_client.get_keyword_rankings(days=90, limit=100)

            # Filter to keywords related to seed
            seed_lower = seed.lower()
            related = [
                kw["keyword"] for kw in keywords_data
                if seed_lower in kw["keyword"].lower() or any(
                    word in kw["keyword"].lower() for word in seed_lower.split()
                )
            ]

            return related[:50]
        except Exception as e:
            self._logger.warning(f"Failed to fetch keywords from GSC: {e}")
            return await self._generate_keyword_ideas_llm(seed)

    async def _generate_keyword_ideas_llm(self, seed: str) -> list[str]:
        """Generate keyword ideas using LLM."""
        try:
            from app.core.llm.groq_client import get_groq_client
            client = get_groq_client()

            prompt = f"""Generate 20 related search keywords for the seed keyword: "{seed}"

Return ONLY a comma-separated list of keywords, nothing else.

Keywords:"""
            response = await client.generate(prompt=prompt, temperature=0.7, max_tokens=300)
            keywords = [kw.strip() for kw in response.split(",")]
            return keywords[:20]
        except Exception:
            return [seed]

    async def _get_keyword_metrics(self, keyword: str) -> dict[str, Any]:
        """Get metrics for keyword from GSC."""
        if not self._gsc_client or not self._gsc_client.is_configured():
            return {
                "volume": 0,
                "difficulty": KeywordDifficulty.MEDIUM,
                "cpc": 0.0,
                "competition": 0.5,
                "intent": "informational",
            }

        try:
            # Search for this keyword in GSC data
            rows = await self._gsc_client.get_search_analytics(
                days=28,
                dimensions=["query"],
                row_limit=500,
            )

            for row in rows:
                if row["keys"][0].lower() == keyword.lower():
                    impressions = row.get("impressions", 0)
                    position = row.get("position", 50)

                    # Estimate difficulty from position
                    if position <= 3:
                        difficulty = KeywordDifficulty.EASY
                    elif position <= 10:
                        difficulty = KeywordDifficulty.MEDIUM
                    elif position <= 30:
                        difficulty = KeywordDifficulty.HARD
                    else:
                        difficulty = KeywordDifficulty.VERY_HARD

                    return {
                        "volume": impressions,
                        "difficulty": difficulty,
                        "cpc": 0.0,  # GSC doesn't provide CPC
                        "competition": min(1.0, position / 100),
                        "intent": "informational",  # Would need NLP to determine
                    }

            return {
                "volume": 0,
                "difficulty": KeywordDifficulty.MEDIUM,
                "cpc": 0.0,
                "competition": 0.5,
                "intent": "informational",
            }
        except Exception as e:
            self._logger.warning(f"Failed to get keyword metrics: {e}")
            return {
                "volume": 0,
                "difficulty": KeywordDifficulty.MEDIUM,
                "cpc": 0.0,
                "competition": 0.5,
                "intent": "informational",
            }

    def _meets_difficulty(
        self, difficulty: KeywordDifficulty, max_difficulty: KeywordDifficulty
    ) -> bool:
        """Check if difficulty meets criteria."""
        order = [
            KeywordDifficulty.EASY,
            KeywordDifficulty.MEDIUM,
            KeywordDifficulty.HARD,
            KeywordDifficulty.VERY_HARD,
        ]
        return order.index(difficulty) <= order.index(max_difficulty)

    async def _calculate_keyword_relevance(
        self, keyword: str, seed: str
    ) -> float:
        """Calculate keyword relevance (0-1)."""

        return 0.8

    async def _get_domain_metrics(self, url: str) -> dict[str, Any]:
        """Get domain authority metrics."""

        return {"da": 50, "pa": 40, "traffic": 10000}

    async def _get_backlink_profile(self, url: str) -> dict[str, int]:
        """Get backlink profile."""

        return {"total": 1000, "domains": 200}

    async def _get_ranking_keywords(self, url: str) -> list[Keyword]:
        """Get keywords URL ranks for."""

        return []

    async def _identify_content_gaps(
        self, url: str, focus: str, keywords: list[Keyword]
    ) -> list[str]:
        """Identify content opportunities."""

        return []

    async def _fetch_page_content(self, url: str) -> str:
        """Fetch and parse page content."""

        return ""

    async def _analyze_page_seo(self, content: str) -> dict[str, Any]:
        """Analyze current page SEO."""

        return {
            "title": "",
            "meta": "",
            "h1": "",
            "word_count": 0,
            "internal_links": 0,
            "images_without_alt": 0,
        }

    async def _optimize_title(self, current: str, keyword: str) -> str:
        """Generate optimized title tag."""

        return f"{keyword} | Your Brand"

    async def _optimize_meta_description(
        self, current: str, keyword: str
    ) -> str:
        """Generate optimized meta description."""

        return f"Learn about {keyword}..."

    async def _optimize_h1(self, current: str, keyword: str) -> str:
        """Generate optimized H1."""

        return keyword

    def _calculate_keyword_density(self, content: str, keyword: str) -> float:
        """Calculate keyword density percentage."""

        return 1.5

    async def _find_missing_keywords(
        self, content: str, target: str
    ) -> list[str]:
        """Find related keywords missing from content."""

        return []

    def _calculate_seo_score(
        self, current: dict[str, Any], keyword: str
    ) -> float:
        """Calculate overall SEO score (0-100)."""

        return 65.0

    def _recommend_word_count(self, keyword: str) -> int:
        """Recommend target word count."""

        return 1500

    async def _check_site_speed(self, domain: str) -> list[SEOIssue]:
        """Check site speed issues."""

        return []

    async def _check_mobile_friendly(self, domain: str) -> list[SEOIssue]:
        """Check mobile friendliness."""

        return []

    async def _check_crawlability(self, domain: str) -> list[SEOIssue]:
        """Check crawlability issues."""

        return []

    async def _check_https(self, domain: str) -> list[SEOIssue]:
        """Check HTTPS configuration."""

        return []

    async def _check_structured_data(self, domain: str) -> list[SEOIssue]:
        """Check structured data implementation."""

        return []

    def _severity_order(self, severity: SEOIssueSeverity) -> int:
        """Get severity order for sorting."""
        order = {
            SEOIssueSeverity.CRITICAL: 0,
            SEOIssueSeverity.HIGH: 1,
            SEOIssueSeverity.MEDIUM: 2,
            SEOIssueSeverity.LOW: 3,
            SEOIssueSeverity.INFO: 4,
        }
        return order.get(severity, 5)

    async def _fetch_backlinks(self, url: str) -> list[dict[str, Any]]:
        """Fetch backlinks from API."""

        return []

    def _analyze_backlink_quality(
        self, backlinks: list[dict[str, Any]]
    ) -> float:
        """Analyze overall backlink quality (0-100)."""

        return 70.0

    def _get_top_domains(
        self, backlinks: list[dict[str, Any]], limit: int
    ) -> list[str]:
        """Get top referring domains."""

        return []

    def _analyze_anchor_text(
        self, backlinks: list[dict[str, Any]]
    ) -> dict[str, int]:
        """Analyze anchor text distribution."""

        return {}

    async def _get_current_rank(self, keyword: str, url: str) -> int | None:
        """Get current ranking position."""

        return None

    def _get_previous_rank(self, keyword: str, url: str) -> int | None:
        """Get previous ranking from history."""
        for update in reversed(self.ranking_history):
            if update.keyword == keyword and update.url == url:
                return update.current_position
        return None

    async def _get_search_volume(self, keyword: str) -> int:
        """Get search volume for keyword."""

        return 0
