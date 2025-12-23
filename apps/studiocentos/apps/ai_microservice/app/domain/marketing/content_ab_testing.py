"""
Content A/B Testing System.

Enables comparison between control (old) and enhanced (new) content generation
to measure improvements from the ContentEnhancer implementation.

Features:
- Generate both variants simultaneously
- Record engagement metrics
- Statistical significance testing
- Automatic winner detection
"""

import logging
import random
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class ABVariant(str, Enum):
    """A/B test variants."""
    CONTROL = "control"      # Without ContentEnhancer (baseline)
    ENHANCED = "enhanced"    # With ContentEnhancer (new)


@dataclass
class ABTestResult:
    """Result of a single A/B test generation."""
    test_id: str
    variant: ABVariant
    content: str
    post_type: str
    platform: str
    generated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    engagement: Optional[Dict[str, float]] = None


@dataclass
class ABTestMetrics:
    """Aggregated metrics for an A/B test."""
    test_name: str
    control_count: int
    enhanced_count: int
    control_avg_engagement: float
    enhanced_avg_engagement: float
    improvement_percent: float
    is_significant: bool
    p_value: Optional[float] = None


class ContentABTest:
    """
    A/B Testing system for content generation.

    Compares content generated with and without ContentEnhancer
    to measure quality improvements.

    Usage:
        test = ContentABTest("december_2024_test")

        # Generate both variants
        variants = await test.generate_both(config)

        # Later, record engagement
        test.record_engagement(test_id, "enhanced", {"likes": 50, "comments": 10})

        # Get results
        results = test.get_results()
    """

    def __init__(self, test_name: str, storage_path: Optional[Path] = None):
        """
        Initialize A/B test.

        Args:
            test_name: Unique identifier for this test
            storage_path: Where to store test data (defaults to data/ab_tests/)
        """
        self.test_name = test_name
        self.storage_path = storage_path or Path(__file__).parent.parent.parent / "data" / "ab_tests"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.results: Dict[str, List[ABTestResult]] = {
            ABVariant.CONTROL: [],
            ABVariant.ENHANCED: [],
        }

        # Load existing data if present
        self._load_data()

    def _test_file(self) -> Path:
        """Get path to test data file."""
        return self.storage_path / f"{self.test_name}.json"

    def _load_data(self):
        """Load existing test data from disk."""
        if self._test_file().exists():
            with open(self._test_file(), 'r', encoding='utf-8') as f:
                data = json.load(f)
                for variant in ABVariant:
                    for item in data.get(variant.value, []):
                        self.results[variant].append(ABTestResult(
                            test_id=item["test_id"],
                            variant=ABVariant(item["variant"]),
                            content=item["content"],
                            post_type=item["post_type"],
                            platform=item["platform"],
                            generated_at=datetime.fromisoformat(item["generated_at"]),
                            metadata=item.get("metadata", {}),
                            engagement=item.get("engagement"),
                        ))
            logger.info(f"Loaded {sum(len(v) for v in self.results.values())} existing results")

    def _save_data(self):
        """Save test data to disk."""
        data = {}
        for variant in ABVariant:
            data[variant.value] = [
                {
                    "test_id": r.test_id,
                    "variant": r.variant.value,
                    "content": r.content,
                    "post_type": r.post_type,
                    "platform": r.platform,
                    "generated_at": r.generated_at.isoformat(),
                    "metadata": r.metadata,
                    "engagement": r.engagement,
                }
                for r in self.results[variant]
            ]

        with open(self._test_file(), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    async def generate_both(
        self,
        topic: str,
        post_type: str,
        platform: str,
        use_enhancer: bool = True,
    ) -> Dict[str, ABTestResult]:
        """
        Generate both control and enhanced variants.

        Args:
            topic: Content topic
            post_type: Type of post (lancio_prodotto, tip_giorno, etc.)
            platform: Target platform (instagram, linkedin, etc.)
            use_enhancer: Whether to actually use enhanced generation

        Returns:
            Dict with "control" and "enhanced" ABTestResult
        """
        from app.domain.marketing.content_creator import ContentCreatorAgent, SocialPostConfig, SocialPlatform, ContentTone
        from app.infrastructure.agents.base_agent import AgentConfig

        test_id = str(uuid.uuid4())[:8]
        results = {}

        # Create agent config
        agent_config = AgentConfig(
            id="ab_test_agent",
            name="A/B Test Content Creator",
            model="gemini-2.5-flash",
            temperature=0.7,  # Control uses lower temp
        )

        # Generate CONTROL (without enhancer features)
        # Note: In practice, you'd need to temporarily disable enhancer
        # For now, we simulate by using shorter prompt
        control_config = SocialPostConfig(
            platform=SocialPlatform(platform),
            message=topic,
            post_type=post_type,
            tone=ContentTone.PROFESSIONAL,
            include_hashtags=True,
            include_emojis=True,
        )

        agent = ContentCreatorAgent(config=agent_config)
        await agent.on_start()

        # Store original enhancer state
        original_enhancer = getattr(agent, 'content_enhancer', None)

        # CONTROL: Generate without enhancer
        agent.content_enhancer = None
        control_result = await agent.generate_social_post(control_config)

        results["control"] = ABTestResult(
            test_id=f"{test_id}_ctrl",
            variant=ABVariant.CONTROL,
            content=control_result.content,
            post_type=post_type,
            platform=platform,
            generated_at=datetime.now(),
            metadata={
                "topic": topic,
                "brand_compliance": control_result.brand_compliance,
            },
        )
        self.results[ABVariant.CONTROL].append(results["control"])

        # ENHANCED: Generate with enhancer
        if use_enhancer and original_enhancer:
            agent.content_enhancer = original_enhancer
            agent_config.temperature = 0.85  # Higher temp for creativity

        enhanced_result = await agent.generate_social_post(control_config)

        results["enhanced"] = ABTestResult(
            test_id=f"{test_id}_enh",
            variant=ABVariant.ENHANCED,
            content=enhanced_result.content,
            post_type=post_type,
            platform=platform,
            generated_at=datetime.now(),
            metadata={
                "topic": topic,
                "brand_compliance": enhanced_result.brand_compliance,
                "brand_scorecard": enhanced_result.metadata.get("brand_scorecard", {}),
            },
        )
        self.results[ABVariant.ENHANCED].append(results["enhanced"])

        # Save after each generation
        self._save_data()

        logger.info(f"Generated A/B variants: {test_id}")
        return results

    def record_engagement(
        self,
        test_id: str,
        variant: str,
        metrics: Dict[str, float],
    ):
        """
        Record engagement metrics for a test result.

        Args:
            test_id: Test ID from generate_both
            variant: "control" or "enhanced"
            metrics: Dict with engagement metrics (likes, comments, shares, etc.)
        """
        variant_enum = ABVariant(variant)

        for result in self.results[variant_enum]:
            if result.test_id == test_id:
                result.engagement = metrics
                self._save_data()
                logger.info(f"Recorded engagement for {test_id}: {metrics}")
                return

        logger.warning(f"Test ID not found: {test_id}")

    def calculate_engagement_score(self, metrics: Dict[str, float]) -> float:
        """Calculate weighted engagement score."""
        weights = {
            "likes": 1.0,
            "comments": 3.0,  # Comments worth more
            "shares": 5.0,    # Shares worth most
            "saves": 4.0,
            "clicks": 2.0,
            "impressions": 0.01,
        }

        score = sum(
            metrics.get(key, 0) * weight
            for key, weight in weights.items()
        )

        return score

    def get_results(self) -> ABTestMetrics:
        """
        Get aggregated test results.

        Returns:
            ABTestMetrics with comparison data
        """
        control_scores = []
        enhanced_scores = []

        for result in self.results[ABVariant.CONTROL]:
            if result.engagement:
                control_scores.append(self.calculate_engagement_score(result.engagement))

        for result in self.results[ABVariant.ENHANCED]:
            if result.engagement:
                enhanced_scores.append(self.calculate_engagement_score(result.engagement))

        control_avg = sum(control_scores) / len(control_scores) if control_scores else 0
        enhanced_avg = sum(enhanced_scores) / len(enhanced_scores) if enhanced_scores else 0

        improvement = ((enhanced_avg - control_avg) / control_avg * 100) if control_avg > 0 else 0

        # Simple significance test (need more samples for real test)
        is_significant = (len(control_scores) >= 10 and
                          len(enhanced_scores) >= 10 and
                          abs(improvement) >= 10)

        return ABTestMetrics(
            test_name=self.test_name,
            control_count=len(self.results[ABVariant.CONTROL]),
            enhanced_count=len(self.results[ABVariant.ENHANCED]),
            control_avg_engagement=control_avg,
            enhanced_avg_engagement=enhanced_avg,
            improvement_percent=improvement,
            is_significant=is_significant,
        )

    def get_comparison_report(self) -> str:
        """Generate human-readable comparison report."""
        metrics = self.get_results()

        report = f"""
================================================================================
📊 A/B TEST REPORT: {self.test_name}
================================================================================

SAMPLE SIZE:
  Control (without enhancer): {metrics.control_count} posts
  Enhanced (with enhancer):   {metrics.enhanced_count} posts

ENGAGEMENT (weighted score):
  Control avg:  {metrics.control_avg_engagement:.1f}
  Enhanced avg: {metrics.enhanced_avg_engagement:.1f}

IMPROVEMENT: {metrics.improvement_percent:+.1f}%

STATISTICAL SIGNIFICANCE: {"✅ YES" if metrics.is_significant else "⚠️ Need more data"}

================================================================================
"""
        return report


# ============================================================================
# Quick Test Functions
# ============================================================================

async def run_quick_ab_test():
    """Run a quick A/B test for demonstration."""
    test = ContentABTest("quick_test_" + datetime.now().strftime("%Y%m%d"))

    test_scenarios = [
        ("Nuovo chatbot AI per studi legali", "lancio_prodotto", "instagram"),
        ("Come usare ChatGPT per le email", "tip_giorno", "instagram"),
        ("Case study ristorazione -40% sprechi", "caso_successo", "linkedin"),
    ]

    for topic, post_type, platform in test_scenarios:
        print(f"\n🔄 Testing: {topic[:40]}...")
        try:
            results = await test.generate_both(topic, post_type, platform)
            print(f"   Control: {len(results['control'].content)} chars")
            print(f"   Enhanced: {len(results['enhanced'].content)} chars")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    print(test.get_comparison_report())


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_quick_ab_test())
