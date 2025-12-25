"""
AI Feedback Loop Service - Performance-Driven Content Optimization.

Sistema che analizza le performance reali dei post pubblicati e ottimizza
automaticamente la generazione di contenuti futuri.

ARCHITETTURA:
    Instagram API ──► Feedback Loop ──► Content Creator Agent
         │                  │                    │
         │          Pattern Store                │
         │          (PostgreSQL)                 │
         └──────────────────┴────────────────────┘
                     Learning Signals

FEATURES:
- Ingestione dati performance da piattaforme social
- Pattern analysis (orari, giorni, tipi contenuto, stili)
- Learning signals generation per AI agents
- Prompt optimization basata su performance storiche
- Sync automatico da Instagram Insights

REFERENCE:
- Utilizza InstagramInsightsService per recupero metriche
- Integrazione con ContentCreatorAgent per prompt enhancement
"""

from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import json

import structlog
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
import uuid

from app.core.config import settings
from app.integrations.instagram_insights import (
    get_instagram_insights_service,
    InstagramAPIError,
    MediaInsights,
)

logger = structlog.get_logger(__name__)


# =============================================================================
# ENUMS
# =============================================================================


class Platform(str, Enum):
    """Piattaforme social supportate."""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    TIKTOK = "tiktok"


class ContentStyle(str, Enum):
    """Stili di contenuto identificabili."""
    EDUCATIONAL = "educational"
    ENTERTAINING = "entertaining"
    INSPIRATIONAL = "inspirational"
    PROMOTIONAL = "promotional"
    BEHIND_THE_SCENES = "behind_the_scenes"
    USER_GENERATED = "user_generated"
    TRENDING = "trending"
    STORYTELLING = "storytelling"


# =============================================================================
# PYDANTIC MODELS
# =============================================================================


class PostPerformance(BaseModel):
    """Dati performance singolo post per ingestione."""
    platform: str
    post_id: str
    post_type: str  # IMAGE, VIDEO, CAROUSEL, REELS
    content: Optional[str] = None
    hashtags: List[str] = Field(default_factory=list)
    posted_at: datetime

    # Metrics
    likes: int = 0
    comments: int = 0
    saves: int = 0
    shares: int = 0
    reach: int = 0
    impressions: int = 0

    # Optional metadata
    media_url: Optional[str] = None
    caption_length: Optional[int] = None
    has_cta: bool = False
    cta_type: Optional[str] = None


class ContentPatterns(BaseModel):
    """Pattern identificati dai contenuti performanti."""
    platform: str
    analyzed_posts: int = 0
    analysis_period_days: int = 30

    # Timing patterns
    best_posting_hours: List[int] = Field(default_factory=list)  # [9, 12, 18, 21]
    best_posting_days: List[str] = Field(default_factory=list)   # ["tuesday", "thursday"]

    # Content patterns
    top_content_types: List[str] = Field(default_factory=list)   # ["carousel", "reel"]
    avg_caption_length: int = 0
    optimal_caption_range: Tuple[int, int] = (100, 300)

    # Engagement patterns
    top_hashtags: List[str] = Field(default_factory=list)        # Top 10 hashtags
    hashtag_count_optimal: int = 5

    # Style patterns
    top_styles: List[str] = Field(default_factory=list)          # ["educational", "entertaining"]
    top_ctas: List[str] = Field(default_factory=list)            # ["link in bio", "save this"]

    # Performance benchmarks
    avg_engagement_rate: float = 0.0
    high_performance_threshold: float = 0.0  # Score sopra cui è "high performer"

    generated_at: datetime = Field(default_factory=datetime.utcnow)


class LearningSignals(BaseModel):
    """Segnali di apprendimento per Content Creator Agent."""
    platform: str
    confidence_score: float = 0.0  # 0-1, basato su quantità dati

    # Actionable signals
    do_more: List[str] = Field(default_factory=list)         # Cose da fare di più
    do_less: List[str] = Field(default_factory=list)         # Cose da evitare
    experiment_with: List[str] = Field(default_factory=list) # Nuove cose da provare

    # Content guidelines
    optimal_frequency: str = "1 post/day"
    content_mix: Dict[str, float] = Field(default_factory=dict)
    # {"carousel": 0.4, "reel": 0.3, "image": 0.3}

    # Prompt enhancements
    tone_recommendations: List[str] = Field(default_factory=list)
    topic_recommendations: List[str] = Field(default_factory=list)
    format_recommendations: List[str] = Field(default_factory=list)

    # Timing recommendations
    post_at_hours: List[int] = Field(default_factory=list)
    post_on_days: List[str] = Field(default_factory=list)

    generated_at: datetime = Field(default_factory=datetime.utcnow)


class OptimizedPrompt(BaseModel):
    """Prompt ottimizzato basato su learning signals."""
    original_prompt: str
    optimized_prompt: str
    enhancements_applied: List[str] = Field(default_factory=list)
    platform: str
    confidence: float = 0.0


class SyncResult(BaseModel):
    """Risultato sync da piattaforma."""
    platform: str
    posts_synced: int = 0
    posts_updated: int = 0
    posts_skipped: int = 0
    errors: List[str] = Field(default_factory=list)
    synced_at: datetime = Field(default_factory=datetime.utcnow)


class FeedbackLoopStatus(BaseModel):
    """Stato del Feedback Loop system."""
    enabled: bool = True
    platforms_configured: List[str] = Field(default_factory=list)
    total_posts_analyzed: int = 0
    last_sync: Optional[datetime] = None
    last_pattern_analysis: Optional[datetime] = None
    patterns_available: Dict[str, bool] = Field(default_factory=dict)


# =============================================================================
# PERFORMANCE SCORING
# =============================================================================


def calculate_performance_score(
    likes: int,
    comments: int,
    saves: int,
    shares: int,
    reach: int,
    followers: int
) -> float:
    """
    Calcola score 0-100 basato su metriche ponderate.

    Pesi:
    - Engagement Rate: 30%
    - Saves (intent): 25%
    - Shares (virality): 20%
    - Comments (interaction): 15%
    - Reach vs Followers: 10%

    Args:
        likes: Numero like
        comments: Numero commenti
        saves: Numero salvataggi
        shares: Numero condivisioni
        reach: Reach del post
        followers: Numero followers account

    Returns:
        Score 0-100
    """
    if followers == 0 or reach == 0:
        return 0.0

    # Calculate rates
    total_engagement = likes + comments + saves + shares
    engagement_rate = (total_engagement / reach) * 100
    saves_rate = (saves / reach) * 100
    shares_rate = (shares / reach) * 100
    comments_rate = (comments / reach) * 100
    reach_rate = (reach / followers) * 100

    # Normalize to 0-100 scale with realistic benchmarks
    normalized = {
        "engagement_rate": min(engagement_rate * 10, 100),    # 10% ER = 100
        "saves_rate": min(saves_rate * 50, 100),              # 2% save rate = 100
        "shares_rate": min(shares_rate * 100, 100),           # 1% share rate = 100
        "comments_rate": min(comments_rate * 100, 100),       # 1% comment rate = 100
        "reach_rate": min(reach_rate, 100),                   # 100% reach = 100
    }

    # Apply weights
    weights = {
        "engagement_rate": 0.30,
        "saves_rate": 0.25,
        "shares_rate": 0.20,
        "comments_rate": 0.15,
        "reach_rate": 0.10
    }

    score = sum(normalized[k] * weights[k] for k in weights)
    return round(score, 2)


# =============================================================================
# AI FEEDBACK LOOP SERVICE
# =============================================================================


class AIFeedbackLoopService:
    """
    Servizio centrale per il feedback loop AI.

    Connette le performance reali dei post alla generazione di contenuti,
    creando un ciclo di miglioramento continuo.

    Features:
    - Ingestione dati performance
    - Pattern analysis avanzata
    - Learning signals generation
    - Prompt optimization
    - Sync automatico da Instagram

    Usage:
        service = AIFeedbackLoopService()

        # Sync da Instagram
        await service.sync_from_instagram()

        # Ottieni patterns
        patterns = await service.analyze_patterns("instagram")

        # Ottimizza prompt
        optimized = await service.optimize_prompt(
            "Genera un post su AI marketing",
            "instagram"
        )
    """

    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.db = db_session
        self._patterns_cache: Dict[str, ContentPatterns] = {}
        self._signals_cache: Dict[str, LearningSignals] = {}
        self._cache_expiry: Dict[str, datetime] = {}

        # In-memory storage per development/testing
        self._performance_data: List[PostPerformance] = []

    # =========================================================================
    # STATUS
    # =========================================================================

    async def get_status(self) -> FeedbackLoopStatus:
        """Ottiene stato del sistema."""
        status = FeedbackLoopStatus(
            enabled=settings.FEEDBACK_LOOP_ENABLED if hasattr(settings, 'FEEDBACK_LOOP_ENABLED') else True
        )

        # Check configured platforms
        if settings.INSTAGRAM_ACCOUNT_ID and settings.INSTAGRAM_ACCESS_TOKEN:
            status.platforms_configured.append("instagram")
        if settings.FACEBOOK_PAGE_ID and settings.META_ACCESS_TOKEN:
            status.platforms_configured.append("facebook")
        if settings.LINKEDIN_ACCESS_TOKEN:
            status.platforms_configured.append("linkedin")

        # Count analyzed posts
        status.total_posts_analyzed = len(self._performance_data)

        # Check patterns availability
        for platform in status.platforms_configured:
            status.patterns_available[platform] = platform in self._patterns_cache

        return status

    # =========================================================================
    # DATA INGESTION
    # =========================================================================

    async def ingest_performance_data(
        self,
        posts: List[PostPerformance],
        followers_count: int = 0
    ) -> int:
        """
        Ingestisce dati performance per analisi.

        Args:
            posts: Lista di PostPerformance da ingestire
            followers_count: Numero followers per calcolo score

        Returns:
            Numero di post ingestiti con successo
        """
        ingested = 0

        for post in posts:
            try:
                # Calculate performance score
                score = calculate_performance_score(
                    likes=post.likes,
                    comments=post.comments,
                    saves=post.saves,
                    shares=post.shares,
                    reach=post.reach,
                    followers=followers_count
                )

                # Store in memory (in production: database)
                # Check for duplicates
                existing = next(
                    (p for p in self._performance_data if p.post_id == post.post_id),
                    None
                )

                if existing:
                    # Update existing
                    idx = self._performance_data.index(existing)
                    self._performance_data[idx] = post
                else:
                    self._performance_data.append(post)

                ingested += 1

            except Exception as e:
                logger.warning(
                    "feedback_loop_ingest_error",
                    post_id=post.post_id,
                    error=str(e)
                )

        # Invalidate caches
        self._patterns_cache.clear()
        self._signals_cache.clear()

        logger.info(
            "feedback_loop_data_ingested",
            ingested=ingested,
            total=len(posts)
        )

        return ingested

    async def sync_from_instagram(self, limit: int = 50) -> SyncResult:
        """
        Sincronizza dati performance da Instagram.

        Args:
            limit: Numero massimo post da sincronizzare

        Returns:
            SyncResult con statistiche sync
        """
        result = SyncResult(platform="instagram")

        try:
            ig_service = get_instagram_insights_service()

            # Verify connection
            status = await ig_service.verify_connection()
            if not status.connected:
                result.errors.append(f"Instagram non connesso: {status.error}")
                return result

            # Get account for followers count
            account = await ig_service.get_account_insights()
            followers = account.followers_count

            # Get all media insights
            media_insights = await ig_service.get_all_media_insights(limit=limit)

            # Convert to PostPerformance
            posts = []
            for media in media_insights:
                post = PostPerformance(
                    platform="instagram",
                    post_id=media.media_id,
                    post_type=media.media_type,
                    content=media.caption,
                    hashtags=self._extract_hashtags(media.caption or ""),
                    posted_at=media.timestamp or datetime.utcnow(),
                    likes=media.likes,
                    comments=media.comments,
                    saves=media.saves,
                    shares=media.shares,
                    reach=media.reach,
                    impressions=media.impressions,
                    media_url=media.media_url,
                    caption_length=len(media.caption) if media.caption else 0,
                    has_cta=self._detect_cta(media.caption or ""),
                    cta_type=self._extract_cta_type(media.caption or "")
                )
                posts.append(post)

            # Ingest data
            ingested = await self.ingest_performance_data(posts, followers)

            result.posts_synced = ingested
            result.posts_updated = len(self._performance_data)

            logger.info(
                "feedback_loop_instagram_sync_complete",
                synced=ingested,
                followers=followers
            )

        except InstagramAPIError as e:
            result.errors.append(str(e))
            logger.error("feedback_loop_instagram_sync_error", error=str(e))
        except Exception as e:
            result.errors.append(f"Unexpected error: {str(e)}")
            logger.exception("feedback_loop_instagram_sync_exception")

        return result

    def _extract_hashtags(self, text: str) -> List[str]:
        """Estrae hashtags da testo."""
        import re
        hashtags = re.findall(r'#(\w+)', text)
        return [h.lower() for h in hashtags]

    def _detect_cta(self, text: str) -> bool:
        """Rileva presenza di CTA nel testo."""
        cta_patterns = [
            "link in bio", "swipe up", "tap", "click", "save this",
            "share", "comment", "follow", "dm", "scopri", "clicca",
            "salva", "condividi"
        ]
        text_lower = text.lower()
        return any(cta in text_lower for cta in cta_patterns)

    def _extract_cta_type(self, text: str) -> Optional[str]:
        """Estrae tipo di CTA dal testo."""
        cta_mapping = {
            "link in bio": "link_in_bio",
            "swipe up": "swipe_up",
            "save this": "save",
            "salva": "save",
            "share": "share",
            "condividi": "share",
            "comment": "comment",
            "commenta": "comment",
            "follow": "follow",
            "segui": "follow",
            "dm": "direct_message"
        }
        text_lower = text.lower()
        for pattern, cta_type in cta_mapping.items():
            if pattern in text_lower:
                return cta_type
        return None

    # =========================================================================
    # PATTERN ANALYSIS
    # =========================================================================

    async def analyze_patterns(
        self,
        platform: str,
        days: int = 30,
        use_cache: bool = True
    ) -> ContentPatterns:
        """
        Analizza pattern dai contenuti performanti.

        Args:
            platform: Piattaforma da analizzare
            days: Giorni di dati da considerare
            use_cache: Se usare cache (1 ora)

        Returns:
            ContentPatterns con tutti i pattern identificati
        """
        # Check cache
        cache_key = f"{platform}_{days}"
        if use_cache and cache_key in self._patterns_cache:
            if self._cache_expiry.get(cache_key, datetime.min) > datetime.utcnow():
                return self._patterns_cache[cache_key]

        patterns = ContentPatterns(
            platform=platform,
            analysis_period_days=days
        )

        # Filter data by platform and date
        cutoff = datetime.utcnow() - timedelta(days=days)
        posts = [
            p for p in self._performance_data
            if p.platform == platform and p.posted_at >= cutoff
        ]

        if not posts:
            logger.warning(
                "feedback_loop_no_data",
                platform=platform,
                days=days
            )
            return patterns

        patterns.analyzed_posts = len(posts)

        # Get account followers for scoring
        try:
            ig_service = get_instagram_insights_service()
            account = await ig_service.get_account_insights(use_cache=True)
            followers = account.followers_count
        except Exception:
            followers = 1000  # Default fallback

        # Calculate scores for all posts
        scored_posts = []
        for post in posts:
            score = calculate_performance_score(
                likes=post.likes,
                comments=post.comments,
                saves=post.saves,
                shares=post.shares,
                reach=post.reach,
                followers=followers
            )
            scored_posts.append((post, score))

        # Sort by score
        scored_posts.sort(key=lambda x: x[1], reverse=True)

        # Calculate performance threshold (top 25%)
        scores = [s for _, s in scored_posts]
        if scores:
            patterns.avg_engagement_rate = sum(scores) / len(scores)
            percentile_75 = sorted(scores, reverse=True)[len(scores) // 4] if len(scores) >= 4 else scores[0]
            patterns.high_performance_threshold = percentile_75

        # Top performers (above threshold)
        top_performers = [
            p for p, s in scored_posts
            if s >= patterns.high_performance_threshold
        ]

        # Analyze timing patterns
        hour_counts: Dict[int, List[float]] = defaultdict(list)
        day_counts: Dict[int, List[float]] = defaultdict(list)

        for post, score in scored_posts:
            hour_counts[post.posted_at.hour].append(score)
            day_counts[post.posted_at.weekday()].append(score)

        # Best hours (by average score)
        hour_avgs = {h: sum(scores)/len(scores) for h, scores in hour_counts.items()}
        patterns.best_posting_hours = sorted(hour_avgs.keys(), key=lambda h: hour_avgs[h], reverse=True)[:5]

        # Best days
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_avgs = {d: sum(scores)/len(scores) for d, scores in day_counts.items()}
        best_days_idx = sorted(day_avgs.keys(), key=lambda d: day_avgs[d], reverse=True)[:3]
        patterns.best_posting_days = [day_names[d] for d in best_days_idx]

        # Content type patterns
        type_scores: Dict[str, List[float]] = defaultdict(list)
        for post, score in scored_posts:
            type_scores[post.post_type].append(score)

        type_avgs = {t: sum(scores)/len(scores) for t, scores in type_scores.items()}
        patterns.top_content_types = sorted(type_avgs.keys(), key=lambda t: type_avgs[t], reverse=True)

        # Caption length analysis
        caption_lengths = [p.caption_length or 0 for p, _ in scored_posts if p.caption_length]
        if caption_lengths:
            patterns.avg_caption_length = sum(caption_lengths) // len(caption_lengths)

            # Optimal range from top performers
            top_lengths = [p.caption_length or 0 for p in top_performers if p.caption_length]
            if top_lengths:
                patterns.optimal_caption_range = (min(top_lengths), max(top_lengths))

        # Hashtag analysis
        all_hashtags: Dict[str, int] = defaultdict(int)
        top_hashtags: Dict[str, int] = defaultdict(int)

        for post, score in scored_posts:
            for tag in post.hashtags:
                all_hashtags[tag] += 1
                if score >= patterns.high_performance_threshold:
                    top_hashtags[tag] += 1

        # Top hashtags by frequency in high performers
        patterns.top_hashtags = sorted(top_hashtags.keys(), key=lambda t: top_hashtags[t], reverse=True)[:10]

        # Optimal hashtag count
        hashtag_counts = [len(p.hashtags) for p in top_performers if p.hashtags]
        if hashtag_counts:
            patterns.hashtag_count_optimal = sum(hashtag_counts) // len(hashtag_counts)

        # CTA analysis
        cta_types: Dict[str, int] = defaultdict(int)
        for post in top_performers:
            if post.cta_type:
                cta_types[post.cta_type] += 1

        patterns.top_ctas = sorted(cta_types.keys(), key=lambda c: cta_types[c], reverse=True)[:5]

        # Cache results
        self._patterns_cache[cache_key] = patterns
        self._cache_expiry[cache_key] = datetime.utcnow() + timedelta(hours=1)

        logger.info(
            "feedback_loop_patterns_analyzed",
            platform=platform,
            posts=patterns.analyzed_posts,
            avg_engagement=patterns.avg_engagement_rate
        )

        return patterns

    # =========================================================================
    # LEARNING SIGNALS
    # =========================================================================

    async def generate_learning_signals(
        self,
        platform: str,
        use_cache: bool = True
    ) -> LearningSignals:
        """
        Genera segnali di apprendimento per Content Creator Agent.

        Args:
            platform: Piattaforma target
            use_cache: Se usare cache

        Returns:
            LearningSignals actionable
        """
        # Check cache
        if use_cache and platform in self._signals_cache:
            if self._cache_expiry.get(f"signals_{platform}", datetime.min) > datetime.utcnow():
                return self._signals_cache[platform]

        signals = LearningSignals(platform=platform)

        # Get patterns
        patterns = await self.analyze_patterns(platform, use_cache=use_cache)

        if patterns.analyzed_posts == 0:
            signals.confidence_score = 0.0
            signals.experiment_with = [
                "Pubblica più contenuti per generare dati",
                "Prova diversi formati: carousel, reels, immagini",
                "Testa diversi orari di pubblicazione"
            ]
            return signals

        # Calculate confidence based on data amount
        min_posts = 20  # Minimum for reliable patterns
        signals.confidence_score = min(patterns.analyzed_posts / min_posts, 1.0)

        # Generate "do more" signals
        if patterns.top_content_types:
            signals.do_more.append(f"Crea più contenuti {patterns.top_content_types[0]}")

        if patterns.best_posting_hours:
            hours_str = ", ".join([f"{h}:00" for h in patterns.best_posting_hours[:3]])
            signals.do_more.append(f"Pubblica negli orari: {hours_str}")

        if patterns.best_posting_days:
            signals.do_more.append(f"Concentrati su: {', '.join(patterns.best_posting_days[:2])}")

        if patterns.top_hashtags:
            signals.do_more.append(f"Usa hashtags: #{' #'.join(patterns.top_hashtags[:5])}")

        if patterns.top_ctas:
            cta_map = {
                "save": "Invita a salvare il post",
                "share": "Invita a condividere",
                "comment": "Fai domande per stimolare commenti",
                "link_in_bio": "Usa 'link in bio' per conversioni"
            }
            for cta in patterns.top_ctas[:2]:
                if cta in cta_map:
                    signals.do_more.append(cta_map[cta])

        # Generate "do less" signals
        if len(patterns.top_content_types) > 1:
            worst_type = patterns.top_content_types[-1]
            signals.do_less.append(f"Riduci contenuti {worst_type}")

        if patterns.avg_caption_length > 0:
            if patterns.avg_caption_length < 50:
                signals.do_less.append("Caption troppo corte - aggiungi contesto")
            elif patterns.avg_caption_length > 500:
                signals.do_less.append("Caption troppo lunghe - sii più conciso")

        # Generate "experiment with" signals
        all_types = ["IMAGE", "VIDEO", "CAROUSEL_ALBUM", "REELS"]
        missing_types = [t for t in all_types if t not in patterns.top_content_types]
        if missing_types:
            signals.experiment_with.append(f"Prova formato: {missing_types[0]}")

        signals.experiment_with.append("Testa nuovi hashtags di nicchia")
        signals.experiment_with.append("Prova contenuti collaborativi")

        # Content mix recommendation
        if patterns.top_content_types:
            total = len(patterns.top_content_types)
            for i, ctype in enumerate(patterns.top_content_types):
                # Higher weight for top performers
                weight = (total - i) / sum(range(1, total + 1))
                signals.content_mix[ctype.lower()] = round(weight, 2)

        # Timing recommendations
        signals.post_at_hours = patterns.best_posting_hours[:3]
        signals.post_on_days = patterns.best_posting_days[:3]

        # Frequency recommendation
        if patterns.analyzed_posts >= 30:
            daily_avg = patterns.analyzed_posts / 30
            if daily_avg >= 2:
                signals.optimal_frequency = "2 posts/day"
            elif daily_avg >= 1:
                signals.optimal_frequency = "1 post/day"
            else:
                signals.optimal_frequency = "4-5 posts/week"

        # Tone recommendations
        signals.tone_recommendations = [
            "Usa linguaggio conversazionale",
            "Aggiungi emoji per engagement",
            "Inizia con hook forte"
        ]

        # Cache results
        self._signals_cache[platform] = signals
        self._cache_expiry[f"signals_{platform}"] = datetime.utcnow() + timedelta(hours=1)

        logger.info(
            "feedback_loop_signals_generated",
            platform=platform,
            confidence=signals.confidence_score,
            do_more=len(signals.do_more)
        )

        return signals

    # =========================================================================
    # PROMPT OPTIMIZATION
    # =========================================================================

    async def optimize_prompt(
        self,
        base_prompt: str,
        platform: str
    ) -> OptimizedPrompt:
        """
        Ottimizza un prompt basandosi sui learning signals.

        Args:
            base_prompt: Prompt originale
            platform: Piattaforma target

        Returns:
            OptimizedPrompt con prompt arricchito
        """
        result = OptimizedPrompt(
            original_prompt=base_prompt,
            optimized_prompt=base_prompt,
            platform=platform
        )

        # Get signals
        signals = await self.generate_learning_signals(platform)
        result.confidence = signals.confidence_score

        if signals.confidence_score < 0.3:
            # Not enough data for optimization
            return result

        # Get patterns
        patterns = await self.analyze_patterns(platform)

        # Build enhancement sections
        enhancements = []

        # Content type preference
        if patterns.top_content_types:
            top_type = patterns.top_content_types[0]
            enhancements.append(f"Ottimizza per formato {top_type}")
            result.enhancements_applied.append(f"format:{top_type}")

        # Caption length guidance
        if patterns.optimal_caption_range:
            min_len, max_len = patterns.optimal_caption_range
            enhancements.append(f"Lunghezza caption ideale: {min_len}-{max_len} caratteri")
            result.enhancements_applied.append(f"length:{min_len}-{max_len}")

        # Hashtag guidance
        if patterns.top_hashtags:
            top_tags = patterns.top_hashtags[:5]
            enhancements.append(f"Hashtag suggeriti: #{' #'.join(top_tags)}")
            result.enhancements_applied.append(f"hashtags:{len(top_tags)}")

        if patterns.hashtag_count_optimal:
            enhancements.append(f"Usa circa {patterns.hashtag_count_optimal} hashtags")

        # CTA guidance
        if patterns.top_ctas:
            cta = patterns.top_ctas[0]
            cta_text_map = {
                "save": "Includi invito a salvare il post",
                "share": "Includi invito a condividere",
                "comment": "Includi domanda per stimolare commenti",
                "link_in_bio": "Rimanda al link in bio per approfondire"
            }
            if cta in cta_text_map:
                enhancements.append(cta_text_map[cta])
                result.enhancements_applied.append(f"cta:{cta}")

        # Timing hint
        if patterns.best_posting_hours:
            hour = patterns.best_posting_hours[0]
            enhancements.append(f"Orario pubblicazione consigliato: {hour}:00")

        # Build optimized prompt
        if enhancements:
            enhancement_block = "\n".join([f"- {e}" for e in enhancements])
            result.optimized_prompt = f"""{base_prompt}

---
OTTIMIZZAZIONI BASATE SU PERFORMANCE (confidence: {signals.confidence_score:.0%}):
{enhancement_block}
---"""

        logger.info(
            "feedback_loop_prompt_optimized",
            platform=platform,
            enhancements=len(result.enhancements_applied),
            confidence=result.confidence
        )

        return result

    # =========================================================================
    # CONTENT SUGGESTIONS
    # =========================================================================

    async def get_content_suggestions(
        self,
        platform: str,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Genera suggerimenti contenuto basati su patterns.

        Args:
            platform: Piattaforma target
            count: Numero suggerimenti

        Returns:
            Lista di suggerimenti con tipo, timing, topic
        """
        signals = await self.generate_learning_signals(platform)
        patterns = await self.analyze_patterns(platform)

        suggestions = []

        if not patterns.top_content_types:
            # Default suggestions
            return [{
                "type": "carousel",
                "topic": "Tips & tricks del tuo settore",
                "best_time": "09:00",
                "hashtag_count": 5,
                "cta": "Salva per dopo!"
            }]

        content_types = patterns.top_content_types[:3] or ["IMAGE"]
        hours = patterns.best_posting_hours[:3] or [9, 12, 18]

        topic_templates = [
            "Tutorial step-by-step su {topic}",
            "5 errori da evitare in {topic}",
            "Come ho ottenuto {result} con {topic}",
            "La guida definitiva a {topic}",
            "{topic}: prima vs dopo"
        ]

        for i in range(min(count, 5)):
            suggestion = {
                "type": content_types[i % len(content_types)],
                "topic_template": topic_templates[i % len(topic_templates)],
                "best_time": f"{hours[i % len(hours)]:02d}:00",
                "best_day": patterns.best_posting_days[i % len(patterns.best_posting_days)] if patterns.best_posting_days else "Tuesday",
                "hashtag_count": patterns.hashtag_count_optimal,
                "suggested_hashtags": patterns.top_hashtags[:5],
                "cta": patterns.top_ctas[0] if patterns.top_ctas else "save"
            }
            suggestions.append(suggestion)

        return suggestions


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_feedback_service: Optional[AIFeedbackLoopService] = None


def get_feedback_loop_service(db: Optional[AsyncSession] = None) -> AIFeedbackLoopService:
    """Get singleton instance of AIFeedbackLoopService."""
    global _feedback_service
    if _feedback_service is None:
        _feedback_service = AIFeedbackLoopService(db)
    return _feedback_service
