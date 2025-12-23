"""
🧠 AI Feedback Loop Service

Il CUORE dell'intelligenza di MARKETTINA.

Questo servizio:
1. Analizza performance storiche dei post (Instagram, LinkedIn, Facebook)
2. Identifica pattern di successo (orari, stili, hashtag, tone of voice)
3. Genera "learning signals" che influenzano la generazione AI futura
4. Ottimizza automaticamente la strategia content

Architettura:
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Performance    │────▶│  Pattern        │────▶│  AI Generation  │
│  Data           │     │  Analyzer       │     │  Optimizer      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        ▲                                                │
        │                                                │
        └────────────────────────────────────────────────┘
                        Feedback Loop
"""

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import httpx
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


# =============================================================================
# MODELS
# =============================================================================

class ContentType(str, Enum):
    """Tipo di contenuto."""
    POST_IMAGE = "post_image"
    POST_CAROUSEL = "post_carousel"
    REEL = "reel"
    STORY = "story"
    VIDEO = "video"
    TEXT_ONLY = "text_only"


class Platform(str, Enum):
    """Piattaforma social."""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    TWITTER = "twitter"


class PerformanceMetrics(BaseModel):
    """Metriche performance di un post."""
    post_id: str
    platform: Platform
    content_type: ContentType
    published_at: datetime

    # Raw metrics
    impressions: int = 0
    reach: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    clicks: int = 0
    video_views: int = 0

    # Calculated
    engagement_rate: float = 0.0
    virality_score: float = 0.0  # shares / reach

    # Content features
    caption_length: int = 0
    hashtag_count: int = 0
    has_emoji: bool = False
    has_question: bool = False
    has_cta: bool = False

    # Timing
    hour_posted: int = 0
    day_of_week: int = 0  # 0=Monday, 6=Sunday

    # Topic/Category
    topic: Optional[str] = None
    style: Optional[str] = None


class SuccessPattern(BaseModel):
    """Pattern di successo identificato."""
    pattern_type: str
    pattern_value: Any
    avg_engagement: float
    sample_size: int
    confidence: float  # 0-1, based on sample size and consistency
    recommendation: str


class LearningSignals(BaseModel):
    """Segnali di apprendimento per la generazione AI."""
    # Timing optimization
    best_hours: list[int] = Field(default_factory=list)
    best_days: list[int] = Field(default_factory=list)
    avoid_hours: list[int] = Field(default_factory=list)

    # Content style
    optimal_caption_length: tuple[int, int] = (100, 300)  # min, max
    optimal_hashtag_count: tuple[int, int] = (5, 15)
    use_emoji: bool = True
    use_questions: bool = True
    use_cta: bool = True

    # Content type preferences
    best_content_types: list[ContentType] = Field(default_factory=list)

    # Topic/Style performance
    top_topics: list[str] = Field(default_factory=list)
    top_styles: list[str] = Field(default_factory=list)
    avoid_topics: list[str] = Field(default_factory=list)

    # Tone
    preferred_tone: str = "professional"  # friendly, casual, professional, authoritative

    # Hashtag optimization
    best_hashtags: list[str] = Field(default_factory=list)
    avoid_hashtags: list[str] = Field(default_factory=list)

    # Platform-specific
    platform: Platform = Platform.INSTAGRAM

    # Meta
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    data_points_analyzed: int = 0
    confidence_score: float = 0.0


class ContentOptimizationSuggestion(BaseModel):
    """Suggerimento per ottimizzare contenuto."""
    suggestion_type: str
    original_value: Any
    suggested_value: Any
    reason: str
    expected_improvement: float  # % improvement expected


class OptimizedPrompt(BaseModel):
    """Prompt ottimizzato basato su learning."""
    original_prompt: str
    optimized_prompt: str
    applied_learnings: list[str]
    expected_engagement_boost: float


# =============================================================================
# FEEDBACK LOOP SERVICE
# =============================================================================

class FeedbackLoopService:
    """
    Servizio principale per il feedback loop AI.

    Analizza performance, identifica pattern, e ottimizza generazione futura.
    """

    def __init__(self):
        self._performance_cache: dict[str, list[PerformanceMetrics]] = {}
        self._learning_signals: dict[str, LearningSignals] = {}

    # =========================================================================
    # DATA INGESTION
    # =========================================================================

    async def ingest_performance_data(
        self,
        post_id: str,
        platform: Platform,
        metrics: dict[str, Any],
        content_features: dict[str, Any]
    ) -> PerformanceMetrics:
        """
        Ingerisce dati di performance da post reali.

        Chiamato dopo che un post ha accumulato dati sufficienti (24-48h).
        """
        # Extract timing
        published_at = content_features.get("published_at", datetime.utcnow())
        if isinstance(published_at, str):
            published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

        # Analyze caption
        caption = content_features.get("caption", "")

        performance = PerformanceMetrics(
            post_id=post_id,
            platform=platform,
            content_type=ContentType(content_features.get("content_type", "post_image")),
            published_at=published_at,

            # Metrics
            impressions=metrics.get("impressions", 0),
            reach=metrics.get("reach", 0),
            likes=metrics.get("likes", 0),
            comments=metrics.get("comments", 0),
            shares=metrics.get("shares", 0),
            saves=metrics.get("saves", 0),
            clicks=metrics.get("clicks", 0),
            video_views=metrics.get("video_views", 0),

            # Calculated
            engagement_rate=self._calculate_engagement_rate(metrics),
            virality_score=self._calculate_virality(metrics),

            # Content features
            caption_length=len(caption),
            hashtag_count=caption.count("#"),
            has_emoji=any(ord(c) > 127 for c in caption),
            has_question="?" in caption,
            has_cta=any(cta in caption.lower() for cta in ["link in bio", "scopri", "clicca", "visita", "acquista"]),

            # Timing
            hour_posted=published_at.hour,
            day_of_week=published_at.weekday(),

            # Topic
            topic=content_features.get("topic"),
            style=content_features.get("style")
        )

        # Add to cache
        cache_key = f"{platform.value}"
        if cache_key not in self._performance_cache:
            self._performance_cache[cache_key] = []
        self._performance_cache[cache_key].append(performance)

        # Keep last 500 posts
        self._performance_cache[cache_key] = self._performance_cache[cache_key][-500:]

        logger.info(
            "performance_data_ingested",
            post_id=post_id,
            platform=platform.value,
            engagement_rate=performance.engagement_rate
        )

        return performance

    def _calculate_engagement_rate(self, metrics: dict) -> float:
        """Calcola engagement rate."""
        reach = metrics.get("reach", 0)
        if reach == 0:
            return 0.0

        interactions = (
            metrics.get("likes", 0) +
            metrics.get("comments", 0) * 2 +  # Comments weighted more
            metrics.get("shares", 0) * 3 +    # Shares weighted most
            metrics.get("saves", 0) * 2
        )

        return (interactions / reach) * 100

    def _calculate_virality(self, metrics: dict) -> float:
        """Calcola virality score."""
        reach = metrics.get("reach", 0)
        shares = metrics.get("shares", 0)

        if reach == 0:
            return 0.0

        return (shares / reach) * 100

    # =========================================================================
    # PATTERN ANALYSIS
    # =========================================================================

    async def analyze_patterns(
        self,
        platform: Platform,
        min_data_points: int = 20
    ) -> list[SuccessPattern]:
        """
        Analizza pattern di successo da dati storici.
        """
        cache_key = f"{platform.value}"
        data = self._performance_cache.get(cache_key, [])

        if len(data) < min_data_points:
            logger.warning(
                "insufficient_data_for_analysis",
                platform=platform.value,
                data_points=len(data),
                min_required=min_data_points
            )
            return []

        patterns = []

        # Analyze hour patterns
        hour_patterns = await self._analyze_hour_patterns(data)
        patterns.extend(hour_patterns)

        # Analyze day patterns
        day_patterns = await self._analyze_day_patterns(data)
        patterns.extend(day_patterns)

        # Analyze content type patterns
        type_patterns = await self._analyze_content_type_patterns(data)
        patterns.extend(type_patterns)

        # Analyze caption length patterns
        caption_patterns = await self._analyze_caption_patterns(data)
        patterns.extend(caption_patterns)

        # Analyze hashtag patterns
        hashtag_patterns = await self._analyze_hashtag_patterns(data)
        patterns.extend(hashtag_patterns)

        # Analyze style patterns
        style_patterns = await self._analyze_style_patterns(data)
        patterns.extend(style_patterns)

        logger.info(
            "patterns_analyzed",
            platform=platform.value,
            patterns_found=len(patterns)
        )

        return patterns

    async def _analyze_hour_patterns(self, data: list[PerformanceMetrics]) -> list[SuccessPattern]:
        """Analizza pattern per ora di pubblicazione."""
        hour_performance: dict[int, list[float]] = defaultdict(list)

        for p in data:
            hour_performance[p.hour_posted].append(p.engagement_rate)

        patterns = []
        overall_avg = sum(p.engagement_rate for p in data) / len(data)

        for hour, rates in hour_performance.items():
            if len(rates) >= 3:  # Need at least 3 data points
                avg = sum(rates) / len(rates)
                if avg > overall_avg * 1.2:  # 20% above average
                    patterns.append(SuccessPattern(
                        pattern_type="best_hour",
                        pattern_value=hour,
                        avg_engagement=avg,
                        sample_size=len(rates),
                        confidence=min(len(rates) / 10, 1.0),
                        recommendation=f"Pubblica più spesso alle {hour}:00 - engagement {((avg/overall_avg)-1)*100:.0f}% sopra la media"
                    ))
                elif avg < overall_avg * 0.7:  # 30% below average
                    patterns.append(SuccessPattern(
                        pattern_type="avoid_hour",
                        pattern_value=hour,
                        avg_engagement=avg,
                        sample_size=len(rates),
                        confidence=min(len(rates) / 10, 1.0),
                        recommendation=f"Evita di pubblicare alle {hour}:00 - engagement basso"
                    ))

        return patterns

    async def _analyze_day_patterns(self, data: list[PerformanceMetrics]) -> list[SuccessPattern]:
        """Analizza pattern per giorno della settimana."""
        day_names = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        day_performance: dict[int, list[float]] = defaultdict(list)

        for p in data:
            day_performance[p.day_of_week].append(p.engagement_rate)

        patterns = []
        overall_avg = sum(p.engagement_rate for p in data) / len(data)

        for day, rates in day_performance.items():
            if len(rates) >= 3:
                avg = sum(rates) / len(rates)
                if avg > overall_avg * 1.15:
                    patterns.append(SuccessPattern(
                        pattern_type="best_day",
                        pattern_value=day,
                        avg_engagement=avg,
                        sample_size=len(rates),
                        confidence=min(len(rates) / 5, 1.0),
                        recommendation=f"{day_names[day]} è il giorno migliore per pubblicare"
                    ))

        return patterns

    async def _analyze_content_type_patterns(self, data: list[PerformanceMetrics]) -> list[SuccessPattern]:
        """Analizza pattern per tipo di contenuto."""
        type_performance: dict[ContentType, list[float]] = defaultdict(list)

        for p in data:
            type_performance[p.content_type].append(p.engagement_rate)

        patterns = []
        overall_avg = sum(p.engagement_rate for p in data) / len(data)

        for content_type, rates in type_performance.items():
            if len(rates) >= 3:
                avg = sum(rates) / len(rates)
                if avg > overall_avg * 1.2:
                    patterns.append(SuccessPattern(
                        pattern_type="best_content_type",
                        pattern_value=content_type.value,
                        avg_engagement=avg,
                        sample_size=len(rates),
                        confidence=min(len(rates) / 10, 1.0),
                        recommendation=f"I {content_type.value} performano meglio della media"
                    ))

        return patterns

    async def _analyze_caption_patterns(self, data: list[PerformanceMetrics]) -> list[SuccessPattern]:
        """Analizza pattern per lunghezza caption."""
        length_buckets = {
            "short": (0, 100),
            "medium": (100, 300),
            "long": (300, 500),
            "very_long": (500, 2200)
        }

        bucket_performance: dict[str, list[float]] = defaultdict(list)

        for p in data:
            for bucket_name, (min_len, max_len) in length_buckets.items():
                if min_len <= p.caption_length < max_len:
                    bucket_performance[bucket_name].append(p.engagement_rate)
                    break

        patterns = []
        overall_avg = sum(p.engagement_rate for p in data) / len(data)

        for bucket, rates in bucket_performance.items():
            if len(rates) >= 5:
                avg = sum(rates) / len(rates)
                if avg > overall_avg * 1.15:
                    length_range = length_buckets[bucket]
                    patterns.append(SuccessPattern(
                        pattern_type="best_caption_length",
                        pattern_value=bucket,
                        avg_engagement=avg,
                        sample_size=len(rates),
                        confidence=min(len(rates) / 10, 1.0),
                        recommendation=f"Caption {bucket} ({length_range[0]}-{length_range[1]} caratteri) performano meglio"
                    ))

        return patterns

    async def _analyze_hashtag_patterns(self, data: list[PerformanceMetrics]) -> list[SuccessPattern]:
        """Analizza pattern per numero hashtag."""
        hashtag_buckets = {
            "few": (0, 5),
            "moderate": (5, 15),
            "many": (15, 30)
        }

        bucket_performance: dict[str, list[float]] = defaultdict(list)

        for p in data:
            for bucket_name, (min_count, max_count) in hashtag_buckets.items():
                if min_count <= p.hashtag_count < max_count:
                    bucket_performance[bucket_name].append(p.engagement_rate)
                    break

        patterns = []
        overall_avg = sum(p.engagement_rate for p in data) / len(data)

        for bucket, rates in bucket_performance.items():
            if len(rates) >= 5:
                avg = sum(rates) / len(rates)
                if avg > overall_avg * 1.1:
                    count_range = hashtag_buckets[bucket]
                    patterns.append(SuccessPattern(
                        pattern_type="best_hashtag_count",
                        pattern_value=bucket,
                        avg_engagement=avg,
                        sample_size=len(rates),
                        confidence=min(len(rates) / 10, 1.0),
                        recommendation=f"Usa {count_range[0]}-{count_range[1]} hashtag per migliori risultati"
                    ))

        return patterns

    async def _analyze_style_patterns(self, data: list[PerformanceMetrics]) -> list[SuccessPattern]:
        """Analizza pattern per stile contenuto."""
        patterns = []
        overall_avg = sum(p.engagement_rate for p in data) / len(data)

        # Analyze emoji usage
        with_emoji = [p for p in data if p.has_emoji]
        without_emoji = [p for p in data if not p.has_emoji]

        if len(with_emoji) >= 5 and len(without_emoji) >= 5:
            emoji_avg = sum(p.engagement_rate for p in with_emoji) / len(with_emoji)
            no_emoji_avg = sum(p.engagement_rate for p in without_emoji) / len(without_emoji)

            if emoji_avg > no_emoji_avg * 1.1:
                patterns.append(SuccessPattern(
                    pattern_type="use_emoji",
                    pattern_value=True,
                    avg_engagement=emoji_avg,
                    sample_size=len(with_emoji),
                    confidence=0.8,
                    recommendation="Usa emoji nelle caption - aumentano l'engagement"
                ))

        # Analyze questions
        with_question = [p for p in data if p.has_question]
        without_question = [p for p in data if not p.has_question]

        if len(with_question) >= 5 and len(without_question) >= 5:
            question_avg = sum(p.engagement_rate for p in with_question) / len(with_question)
            no_question_avg = sum(p.engagement_rate for p in without_question) / len(without_question)

            if question_avg > no_question_avg * 1.15:
                patterns.append(SuccessPattern(
                    pattern_type="use_question",
                    pattern_value=True,
                    avg_engagement=question_avg,
                    sample_size=len(with_question),
                    confidence=0.8,
                    recommendation="Includi domande nelle caption - stimolano i commenti"
                ))

        # Analyze CTA
        with_cta = [p for p in data if p.has_cta]
        without_cta = [p for p in data if not p.has_cta]

        if len(with_cta) >= 5:
            cta_avg = sum(p.engagement_rate for p in with_cta) / len(with_cta)
            if cta_avg > overall_avg * 1.1:
                patterns.append(SuccessPattern(
                    pattern_type="use_cta",
                    pattern_value=True,
                    avg_engagement=cta_avg,
                    sample_size=len(with_cta),
                    confidence=0.7,
                    recommendation="Le call-to-action aumentano le conversioni"
                ))

        return patterns

    # =========================================================================
    # LEARNING SIGNALS GENERATION
    # =========================================================================

    async def generate_learning_signals(
        self,
        platform: Platform
    ) -> LearningSignals:
        """
        Genera learning signals da pattern analizzati.

        Questi segnali vengono usati per ottimizzare la generazione AI.
        """
        patterns = await self.analyze_patterns(platform)

        signals = LearningSignals(platform=platform)

        for pattern in patterns:
            if pattern.pattern_type == "best_hour":
                signals.best_hours.append(pattern.pattern_value)
            elif pattern.pattern_type == "avoid_hour":
                signals.avoid_hours.append(pattern.pattern_value)
            elif pattern.pattern_type == "best_day":
                signals.best_days.append(pattern.pattern_value)
            elif pattern.pattern_type == "best_content_type":
                try:
                    signals.best_content_types.append(ContentType(pattern.pattern_value))
                except ValueError:
                    pass
            elif pattern.pattern_type == "best_caption_length":
                if pattern.pattern_value == "short":
                    signals.optimal_caption_length = (50, 100)
                elif pattern.pattern_value == "medium":
                    signals.optimal_caption_length = (100, 300)
                elif pattern.pattern_value == "long":
                    signals.optimal_caption_length = (300, 500)
            elif pattern.pattern_type == "best_hashtag_count":
                if pattern.pattern_value == "few":
                    signals.optimal_hashtag_count = (3, 5)
                elif pattern.pattern_value == "moderate":
                    signals.optimal_hashtag_count = (8, 15)
                elif pattern.pattern_value == "many":
                    signals.optimal_hashtag_count = (15, 25)
            elif pattern.pattern_type == "use_emoji":
                signals.use_emoji = pattern.pattern_value
            elif pattern.pattern_type == "use_question":
                signals.use_questions = pattern.pattern_value
            elif pattern.pattern_type == "use_cta":
                signals.use_cta = pattern.pattern_value

        cache_key = platform.value
        data = self._performance_cache.get(cache_key, [])
        signals.data_points_analyzed = len(data)
        signals.confidence_score = min(len(data) / 50, 1.0)  # Full confidence at 50+ posts
        signals.last_updated = datetime.utcnow()

        # Cache signals
        self._learning_signals[platform.value] = signals

        logger.info(
            "learning_signals_generated",
            platform=platform.value,
            data_points=signals.data_points_analyzed,
            confidence=signals.confidence_score
        )

        return signals

    # =========================================================================
    # PROMPT OPTIMIZATION
    # =========================================================================

    async def optimize_prompt(
        self,
        original_prompt: str,
        platform: Platform,
        content_type: ContentType = ContentType.POST_IMAGE
    ) -> OptimizedPrompt:
        """
        Ottimizza un prompt AI basandosi sui learning signals.

        Aggiunge context e constraints basati su performance passate.
        """
        signals = self._learning_signals.get(platform.value)

        if not signals or signals.confidence_score < 0.3:
            # Not enough data, return original
            return OptimizedPrompt(
                original_prompt=original_prompt,
                optimized_prompt=original_prompt,
                applied_learnings=[],
                expected_engagement_boost=0.0
            )

        optimizations = []
        applied_learnings = []

        # Add caption length guidance
        min_len, max_len = signals.optimal_caption_length
        optimizations.append(f"La caption deve essere tra {min_len} e {max_len} caratteri.")
        applied_learnings.append(f"Lunghezza caption ottimale: {min_len}-{max_len} caratteri")

        # Add hashtag guidance
        min_hashtags, max_hashtags = signals.optimal_hashtag_count
        optimizations.append(f"Includi {min_hashtags}-{max_hashtags} hashtag rilevanti.")
        applied_learnings.append(f"Numero hashtag ottimale: {min_hashtags}-{max_hashtags}")

        # Add style guidance
        if signals.use_emoji:
            optimizations.append("Usa emoji per rendere il testo più engaging.")
            applied_learnings.append("Uso emoji raccomandato")

        if signals.use_questions:
            optimizations.append("Includi una domanda per stimolare l'interazione.")
            applied_learnings.append("Domande aumentano engagement")

        if signals.use_cta:
            optimizations.append("Aggiungi una call-to-action chiara.")
            applied_learnings.append("CTA migliora conversioni")

        # Best times info
        if signals.best_hours:
            hours_str = ", ".join(f"{h}:00" for h in signals.best_hours[:3])
            optimizations.append(f"Nota: Gli orari migliori per pubblicare sono: {hours_str}")

        # Build optimized prompt
        optimization_block = "\n".join(optimizations)
        optimized_prompt = f"""{original_prompt}

---
OTTIMIZZAZIONI BASATE SU PERFORMANCE (confidence: {signals.confidence_score:.0%}):
{optimization_block}
---"""

        # Estimate boost based on confidence and number of optimizations
        expected_boost = min(signals.confidence_score * len(applied_learnings) * 3, 25)  # Max 25%

        return OptimizedPrompt(
            original_prompt=original_prompt,
            optimized_prompt=optimized_prompt,
            applied_learnings=applied_learnings,
            expected_engagement_boost=expected_boost
        )

    # =========================================================================
    # CONTENT OPTIMIZATION SUGGESTIONS
    # =========================================================================

    async def suggest_optimizations(
        self,
        content: dict[str, Any],
        platform: Platform
    ) -> list[ContentOptimizationSuggestion]:
        """
        Suggerisce ottimizzazioni per contenuto specifico.
        """
        signals = self._learning_signals.get(platform.value)

        if not signals:
            return []

        suggestions = []
        caption = content.get("caption", "")
        hashtag_count = caption.count("#")

        # Caption length
        min_len, max_len = signals.optimal_caption_length
        if len(caption) < min_len:
            suggestions.append(ContentOptimizationSuggestion(
                suggestion_type="caption_length",
                original_value=len(caption),
                suggested_value=f"{min_len}-{max_len}",
                reason="Caption troppo corta basandosi su performance passate",
                expected_improvement=10.0
            ))
        elif len(caption) > max_len:
            suggestions.append(ContentOptimizationSuggestion(
                suggestion_type="caption_length",
                original_value=len(caption),
                suggested_value=f"{min_len}-{max_len}",
                reason="Caption troppo lunga - potrebbe perdere engagement",
                expected_improvement=5.0
            ))

        # Hashtag count
        min_hash, max_hash = signals.optimal_hashtag_count
        if hashtag_count < min_hash:
            suggestions.append(ContentOptimizationSuggestion(
                suggestion_type="hashtag_count",
                original_value=hashtag_count,
                suggested_value=f"{min_hash}-{max_hash}",
                reason="Troppi pochi hashtag per massima visibilità",
                expected_improvement=8.0
            ))
        elif hashtag_count > max_hash:
            suggestions.append(ContentOptimizationSuggestion(
                suggestion_type="hashtag_count",
                original_value=hashtag_count,
                suggested_value=f"{min_hash}-{max_hash}",
                reason="Troppi hashtag possono sembrare spam",
                expected_improvement=5.0
            ))

        # Emoji
        has_emoji = any(ord(c) > 127 for c in caption)
        if signals.use_emoji and not has_emoji:
            suggestions.append(ContentOptimizationSuggestion(
                suggestion_type="add_emoji",
                original_value=False,
                suggested_value=True,
                reason="I post con emoji performano meglio sul tuo profilo",
                expected_improvement=7.0
            ))

        # Question
        has_question = "?" in caption
        if signals.use_questions and not has_question:
            suggestions.append(ContentOptimizationSuggestion(
                suggestion_type="add_question",
                original_value=False,
                suggested_value=True,
                reason="Le domande aumentano i commenti",
                expected_improvement=12.0
            ))

        return suggestions


# =============================================================================
# SINGLETON & HELPERS
# =============================================================================

feedback_loop = FeedbackLoopService()


async def get_optimized_prompt_for_platform(
    prompt: str,
    platform: str
) -> str:
    """
    Helper per ottenere prompt ottimizzato.

    Usato dal content generator per applicare learnings.
    """
    try:
        platform_enum = Platform(platform.lower())
        result = await feedback_loop.optimize_prompt(prompt, platform_enum)
        return result.optimized_prompt
    except ValueError:
        return prompt
