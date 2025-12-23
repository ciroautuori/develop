"""
Engagement Tracker - Track and compare social media engagement metrics.

Features:
- Track metrics per post (likes, comments, shares, saves)
- Compare periods (before/after enhancement)
- Calculate engagement rates
- Generate improvement reports
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class Platform(str, Enum):
    """Supported social platforms."""
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    TIKTOK = "tiktok"


@dataclass
class PostMetrics:
    """Metrics for a single post."""
    post_id: str
    platform: Platform
    published_at: datetime
    content_preview: str

    # Core metrics
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0

    # Reach metrics
    impressions: int = 0
    reach: int = 0

    # Click metrics
    clicks: int = 0
    profile_visits: int = 0

    # Derived
    @property
    def engagement_count(self) -> int:
        """Total engagement actions."""
        return self.likes + self.comments + self.shares + self.saves

    @property
    def engagement_rate(self) -> float:
        """Engagement rate as percentage of reach."""
        if self.reach == 0:
            return 0.0
        return (self.engagement_count / self.reach) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "post_id": self.post_id,
            "platform": self.platform.value,
            "published_at": self.published_at.isoformat(),
            "content_preview": self.content_preview,
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
            "saves": self.saves,
            "impressions": self.impressions,
            "reach": self.reach,
            "clicks": self.clicks,
            "profile_visits": self.profile_visits,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PostMetrics":
        """Create from dictionary."""
        return cls(
            post_id=data["post_id"],
            platform=Platform(data["platform"]),
            published_at=datetime.fromisoformat(data["published_at"]),
            content_preview=data["content_preview"],
            likes=data.get("likes", 0),
            comments=data.get("comments", 0),
            shares=data.get("shares", 0),
            saves=data.get("saves", 0),
            impressions=data.get("impressions", 0),
            reach=data.get("reach", 0),
            clicks=data.get("clicks", 0),
            profile_visits=data.get("profile_visits", 0),
        )


@dataclass
class PeriodComparison:
    """Comparison between two time periods."""
    period_a_name: str  # e.g., "Before Enhancement"
    period_b_name: str  # e.g., "After Enhancement"
    period_a_start: datetime
    period_a_end: datetime
    period_b_start: datetime
    period_b_end: datetime

    # Aggregated metrics
    period_a_posts: int = 0
    period_b_posts: int = 0
    period_a_avg_engagement: float = 0.0
    period_b_avg_engagement: float = 0.0
    period_a_avg_reach: float = 0.0
    period_b_avg_reach: float = 0.0

    @property
    def engagement_change_percent(self) -> float:
        """Change in engagement rate."""
        if self.period_a_avg_engagement == 0:
            return 0.0
        return ((self.period_b_avg_engagement - self.period_a_avg_engagement)
                / self.period_a_avg_engagement * 100)

    @property
    def reach_change_percent(self) -> float:
        """Change in average reach."""
        if self.period_a_avg_reach == 0:
            return 0.0
        return ((self.period_b_avg_reach - self.period_a_avg_reach)
                / self.period_a_avg_reach * 100)


class EngagementTracker:
    """
    Track and analyze social media engagement metrics.

    Usage:
        tracker = EngagementTracker()

        # Track a post
        tracker.track_post(PostMetrics(
            post_id="123",
            platform=Platform.INSTAGRAM,
            published_at=datetime.now(),
            content_preview="Our latest AI solution...",
            likes=150,
            comments=25,
            shares=10,
            reach=5000,
        ))

        # Compare periods
        comparison = tracker.compare_periods(
            before_date=datetime(2024, 12, 1),  # When enhancement was deployed
        )

        # Generate report
        print(tracker.generate_report())
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize tracker with optional storage path."""
        self.storage_path = storage_path or Path(__file__).parent.parent.parent / "data" / "engagement"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.posts: List[PostMetrics] = []
        self._load_data()

    def _data_file(self) -> Path:
        """Get path to data file."""
        return self.storage_path / "engagement_data.json"

    def _load_data(self):
        """Load existing data from disk."""
        if self._data_file().exists():
            with open(self._data_file(), 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.posts = [PostMetrics.from_dict(p) for p in data.get("posts", [])]
            logger.info(f"Loaded {len(self.posts)} existing posts")

    def _save_data(self):
        """Save data to disk."""
        with open(self._data_file(), 'w', encoding='utf-8') as f:
            json.dump({
                "posts": [p.to_dict() for p in self.posts],
                "last_updated": datetime.now().isoformat(),
            }, f, indent=2, ensure_ascii=False)

    def track_post(self, metrics: PostMetrics):
        """Add or update post metrics."""
        # Check if post already exists
        existing_idx = None
        for i, p in enumerate(self.posts):
            if p.post_id == metrics.post_id:
                existing_idx = i
                break

        if existing_idx is not None:
            self.posts[existing_idx] = metrics
            logger.info(f"Updated metrics for post {metrics.post_id}")
        else:
            self.posts.append(metrics)
            logger.info(f"Added new post {metrics.post_id}")

        self._save_data()

    def get_posts_in_range(
        self,
        start: datetime,
        end: datetime,
        platform: Optional[Platform] = None,
    ) -> List[PostMetrics]:
        """Get posts within a date range."""
        filtered = [
            p for p in self.posts
            if start <= p.published_at <= end
        ]
        if platform:
            filtered = [p for p in filtered if p.platform == platform]
        return filtered

    def calculate_averages(self, posts: List[PostMetrics]) -> Dict[str, float]:
        """Calculate average metrics for a list of posts."""
        if not posts:
            return {
                "avg_likes": 0,
                "avg_comments": 0,
                "avg_shares": 0,
                "avg_saves": 0,
                "avg_engagement": 0,
                "avg_reach": 0,
                "avg_engagement_rate": 0,
            }

        return {
            "avg_likes": sum(p.likes for p in posts) / len(posts),
            "avg_comments": sum(p.comments for p in posts) / len(posts),
            "avg_shares": sum(p.shares for p in posts) / len(posts),
            "avg_saves": sum(p.saves for p in posts) / len(posts),
            "avg_engagement": sum(p.engagement_count for p in posts) / len(posts),
            "avg_reach": sum(p.reach for p in posts) / len(posts),
            "avg_engagement_rate": sum(p.engagement_rate for p in posts) / len(posts),
        }

    def compare_periods(
        self,
        before_date: datetime,
        days_each: int = 30,
        platform: Optional[Platform] = None,
    ) -> PeriodComparison:
        """
        Compare engagement before and after a specific date.

        Args:
            before_date: The "cutoff" date (e.g., when enhancement was deployed)
            days_each: Number of days to compare in each period
            platform: Optional filter by platform

        Returns:
            PeriodComparison with detailed metrics
        """
        # Define periods
        period_a_end = before_date - timedelta(days=1)
        period_a_start = period_a_end - timedelta(days=days_each)
        period_b_start = before_date
        period_b_end = before_date + timedelta(days=days_each)

        # Get posts for each period
        period_a_posts = self.get_posts_in_range(period_a_start, period_a_end, platform)
        period_b_posts = self.get_posts_in_range(period_b_start, period_b_end, platform)

        # Calculate averages
        avg_a = self.calculate_averages(period_a_posts)
        avg_b = self.calculate_averages(period_b_posts)

        return PeriodComparison(
            period_a_name="Before Enhancement",
            period_b_name="After Enhancement",
            period_a_start=period_a_start,
            period_a_end=period_a_end,
            period_b_start=period_b_start,
            period_b_end=period_b_end,
            period_a_posts=len(period_a_posts),
            period_b_posts=len(period_b_posts),
            period_a_avg_engagement=avg_a["avg_engagement_rate"],
            period_b_avg_engagement=avg_b["avg_engagement_rate"],
            period_a_avg_reach=avg_a["avg_reach"],
            period_b_avg_reach=avg_b["avg_reach"],
        )

    def generate_report(self, platform: Optional[Platform] = None) -> str:
        """Generate a comprehensive engagement report."""
        filtered_posts = [p for p in self.posts if platform is None or p.platform == platform]

        if not filtered_posts:
            return "No posts tracked yet."

        avgs = self.calculate_averages(filtered_posts)

        # Best performers
        by_engagement = sorted(filtered_posts, key=lambda p: p.engagement_count, reverse=True)
        top_3 = by_engagement[:3]

        report = f"""
================================================================================
📊 ENGAGEMENT REPORT
================================================================================

OVERVIEW:
  Total posts tracked: {len(filtered_posts)}
  Platform: {platform.value if platform else 'All'}
  Date range: {min(p.published_at for p in filtered_posts).strftime('%Y-%m-%d')} to {max(p.published_at for p in filtered_posts).strftime('%Y-%m-%d')}

AVERAGES:
  📱 Reach: {avgs['avg_reach']:.0f}
  ❤️  Likes: {avgs['avg_likes']:.1f}
  💬 Comments: {avgs['avg_comments']:.1f}
  🔄 Shares: {avgs['avg_shares']:.1f}
  📌 Saves: {avgs['avg_saves']:.1f}
  📈 Engagement Rate: {avgs['avg_engagement_rate']:.2f}%

TOP PERFORMERS:
"""
        for i, post in enumerate(top_3, 1):
            report += f"""
  {i}. {post.content_preview[:50]}...
     📊 Engagement: {post.engagement_count} | Rate: {post.engagement_rate:.2f}%
"""

        report += """
================================================================================
"""
        return report

    def get_platform_breakdown(self) -> Dict[str, Dict[str, float]]:
        """Get engagement breakdown by platform."""
        breakdown = {}

        for platform in Platform:
            platform_posts = [p for p in self.posts if p.platform == platform]
            if platform_posts:
                breakdown[platform.value] = self.calculate_averages(platform_posts)

        return breakdown


# ============================================================================
# Singleton Instance
# ============================================================================

engagement_tracker = EngagementTracker()


def get_engagement_tracker() -> EngagementTracker:
    """Get singleton engagement tracker instance."""
    return engagement_tracker
