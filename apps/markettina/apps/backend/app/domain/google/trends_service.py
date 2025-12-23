"""
Google Trends Service
Get trending keywords and SEO insights for marketing
"""
import logging
from datetime import datetime, timedelta
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Note: Google Trends doesn't have an official API
# We use the unofficial pytrends approach with direct HTTP requests
TRENDS_API_BASE = "https://trends.google.com/trends/api"


class GoogleTrendsService:
    """
    Service for Google Trends data.

    Note: This uses unofficial methods as Google doesn't provide a public Trends API.
    For production, consider using the pytrends library or SerpApi.
    """

    def __init__(self, geo: str = "IT", hl: str = "it"):
        """
        Initialize Trends service.

        Args:
            geo: Geographic region (IT = Italy)
            hl: Language (it = Italian)
        """
        self.geo = geo
        self.hl = hl
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }

    async def get_daily_trends(self) -> list[dict[str, Any]]:
        """
        Get daily trending searches.

        Returns:
            List of trending topics with title, traffic, and related queries
        """
        url = f"{TRENDS_API_BASE}/dailytrends"
        params = {
            "hl": self.hl,
            "geo": self.geo,
            "ns": 15
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Trends API error: {response.status_code}")
                    return []

                # Google Trends returns JSONP, need to parse
                text = response.text
                # Remove JSONP wrapper )]}',
                if text.startswith(")]}'"):
                    text = text[5:]

                import json
                data = json.loads(text)

                trends = []
                for day_data in data.get("default", {}).get("trendingSearchesDays", []):
                    for search in day_data.get("trendingSearches", []):
                        trends.append({
                            "title": search.get("title", {}).get("query", ""),
                            "traffic": search.get("formattedTraffic", ""),
                            "articles": [
                                {
                                    "title": art.get("title", ""),
                                    "url": art.get("url", ""),
                                    "source": art.get("source", "")
                                }
                                for art in search.get("articles", [])[:3]
                            ],
                            "related_queries": [
                                q.get("query", "")
                                for q in search.get("relatedQueries", [])[:5]
                            ]
                        })

                return trends[:20]  # Top 20 trends

        except Exception as e:
            logger.error(f"Error getting daily trends: {e}", exc_info=True)
            return []

    async def get_realtime_trends(self, category: str = "all") -> list[dict[str, Any]]:
        """
        Get real-time trending stories.

        Args:
            category: Category filter (all, business, entertainment, health, etc.)

        Returns:
            List of real-time trending stories
        """
        # Category mapping
        category_map = {
            "all": "",
            "business": "b",
            "entertainment": "e",
            "health": "m",
            "science": "t",
            "sports": "s",
            "top": "h"
        }

        cat = category_map.get(category, "")
        url = f"{TRENDS_API_BASE}/realtimetrends"
        params = {
            "hl": self.hl,
            "geo": self.geo,
            "cat": cat,
            "ns": 15
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code != 200:
                    return []

                text = response.text
                if text.startswith(")]}'"):
                    text = text[5:]

                import json
                data = json.loads(text)

                stories = []
                for story in data.get("storySummaries", {}).get("trendingStories", []):
                    stories.append({
                        "title": story.get("title", ""),
                        "entity_names": story.get("entityNames", []),
                        "articles": [
                            {
                                "title": art.get("articleTitle", ""),
                                "url": art.get("url", ""),
                                "source": art.get("source", ""),
                                "time": art.get("time", "")
                            }
                            for art in story.get("articles", [])[:3]
                        ]
                    })

                return stories[:15]

        except Exception as e:
            logger.error(f"Error getting realtime trends: {e}", exc_info=True)
            return []

    async def get_interest_over_time(
        self,
        keywords: list[str],
        timeframe: str = "today 3-m"  # Last 3 months
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Get interest over time for specific keywords.

        Args:
            keywords: List of keywords to compare (max 5)
            timeframe: Time range (today 1-m, today 3-m, today 12-m, today 5-y)

        Returns:
            Dict with keyword -> list of {date, value} data points
        """
        # This requires building the proper explore request
        # For simplicity, we'll return mock data structure
        # In production, use pytrends library

        logger.info(f"Getting interest over time for: {keywords}")

        # Placeholder - in production integrate with pytrends
        return {
            keyword: [
                {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), "value": 50 + (i % 50)}
                for i in range(90, 0, -1)
            ]
            for keyword in keywords[:5]
        }

    async def get_related_queries(
        self,
        keyword: str
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Get related queries for a keyword.

        Args:
            keyword: Search keyword

        Returns:
            Dict with 'top' and 'rising' related queries
        """
        logger.info(f"Getting related queries for: {keyword}")

        # Placeholder structure - integrate with pytrends for real data
        return {
            "top": [
                {"query": f"{keyword} tutorial", "value": 100},
                {"query": f"{keyword} examples", "value": 85},
                {"query": f"best {keyword}", "value": 70},
                {"query": f"{keyword} 2024", "value": 65},
                {"query": f"{keyword} vs", "value": 50},
            ],
            "rising": [
                {"query": f"{keyword} AI", "value": "+5000%"},
                {"query": f"{keyword} automation", "value": "+2500%"},
                {"query": f"{keyword} tool", "value": "+1000%"},
            ]
        }

    async def get_trending_topics_for_industry(
        self,
        industry: str = "technology"
    ) -> list[dict[str, Any]]:
        """
        Get trending topics relevant to a specific industry.

        Args:
            industry: Industry category

        Returns:
            List of relevant trending topics
        """
        # Industry keyword mapping
        industry_keywords = {
            "technology": ["AI", "software", "app", "digital", "tech"],
            "marketing": ["social media", "SEO", "advertising", "branding", "content"],
            "ecommerce": ["online shopping", "e-commerce", "marketplace", "delivery"],
            "finance": ["fintech", "banking", "investment", "crypto", "payment"],
            "healthcare": ["health tech", "telemedicine", "wellness", "medical"],
        }

        keywords = industry_keywords.get(industry, ["business", "innovation"])

        # Get daily trends and filter by relevance
        daily_trends = await self.get_daily_trends()

        relevant_trends = []
        for trend in daily_trends:
            title_lower = trend.get("title", "").lower()
            if any(kw.lower() in title_lower for kw in keywords):
                relevant_trends.append(trend)

        # If not enough relevant trends, return top general trends
        if len(relevant_trends) < 5:
            relevant_trends.extend(daily_trends[:10 - len(relevant_trends)])

        return relevant_trends[:10]


# =============================================================================
# Marketing Integration Functions
# =============================================================================

async def get_marketing_insights(
    keywords: list[str] | None = None,
    industry: str = "technology"
) -> dict[str, Any]:
    """
    Get comprehensive marketing insights from Google Trends.

    Args:
        keywords: Optional specific keywords to analyze
        industry: Industry for relevant trends

    Returns:
        Dict with daily_trends, realtime_trends, keyword_analysis
    """
    service = GoogleTrendsService(geo="IT", hl="it")

    insights = {
        "generated_at": datetime.now().isoformat(),
        "region": "Italy",
        "daily_trends": [],
        "realtime_trends": [],
        "keyword_analysis": {},
        "industry_trends": []
    }

    # Get daily trends
    daily = await service.get_daily_trends()
    insights["daily_trends"] = daily[:10]

    # Get realtime trends
    realtime = await service.get_realtime_trends(category="business")
    insights["realtime_trends"] = realtime[:10]

    # Get industry-specific trends
    industry_trends = await service.get_trending_topics_for_industry(industry)
    insights["industry_trends"] = industry_trends

    # Analyze specific keywords if provided
    if keywords:
        for keyword in keywords[:5]:
            related = await service.get_related_queries(keyword)
            insights["keyword_analysis"][keyword] = related

    return insights


async def suggest_content_topics(
    business_type: str = "web_agency",
    current_services: list[str] | None = None
) -> list[dict[str, Any]]:
    """
    Suggest content topics based on trends.

    Args:
        business_type: Type of business
        current_services: List of services offered

    Returns:
        List of suggested content topics with trend data
    """
    service = GoogleTrendsService()

    # Default services for web agency
    if not current_services:
        current_services = ["web development", "AI", "e-commerce", "mobile app", "SEO"]

    suggestions = []

    # Get trends for each service
    for service_name in current_services:
        related = await service.get_related_queries(service_name)

        # Get rising queries as content opportunities
        for rising in related.get("rising", []):
            suggestions.append({
                "topic": rising.get("query", ""),
                "growth": rising.get("value", ""),
                "related_service": service_name,
                "content_type": "blog_post",
                "priority": "high" if "+5000%" in str(rising.get("value", "")) else "medium"
            })

        # Get top queries for evergreen content
        for top in related.get("top", [])[:3]:
            suggestions.append({
                "topic": top.get("query", ""),
                "search_volume": top.get("value", 0),
                "related_service": service_name,
                "content_type": "evergreen",
                "priority": "medium"
            })

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))

    return suggestions[:20]
