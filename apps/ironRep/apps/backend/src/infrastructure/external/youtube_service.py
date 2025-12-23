"""
YouTube Service - Exercise video search.
"""
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build

from src.infrastructure.logging import get_logger
from src.infrastructure.config.settings import settings

logger = get_logger(__name__)


class YouTubeService:
    """YouTube Data API for exercise videos."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.youtube_api_key
        if not self.api_key:
            logger.warning("YOUTUBE_API_KEY not configured.")
            self.service = None
        else:
            self.service = build("youtube", "v3", developerKey=self.api_key)

    def search_exercise_videos(self, exercise_name: str, language: str = "it", max_results: int = 5) -> List[Dict[str, Any]]:
        if not self.service:
            return []
        query = f"{exercise_name} esercizio tutorial form corretta"
        try:
            resp = self.service.search().list(part="snippet", q=query, type="video", maxResults=max_results,
                                              relevanceLanguage=language, videoDuration="medium",
                                              videoEmbeddable="true", safeSearch="strict", order="relevance").execute()
            return [{"video_id": i.get("id", {}).get("videoId"), "title": i.get("snippet", {}).get("title"),
                    "description": i.get("snippet", {}).get("description", "")[:200],
                    "thumbnail": i.get("snippet", {}).get("thumbnails", {}).get("high", {}).get("url"),
                    "channel": i.get("snippet", {}).get("channelTitle"),
                    "embed_url": f"https://www.youtube.com/embed/{i.get('id', {}).get('videoId')}",
                    "watch_url": f"https://www.youtube.com/watch?v={i.get('id', {}).get('videoId')}"} for i in resp.get("items", [])]
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            return []

    def get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        if not self.service:
            return None
        try:
            resp = self.service.videos().list(part="snippet,contentDetails,statistics", id=video_id).execute()
            if not resp.get("items"):
                return None
            item = resp["items"][0]
            return {"video_id": video_id, "title": item.get("snippet", {}).get("title"),
                   "thumbnail": item.get("snippet", {}).get("thumbnails", {}).get("high", {}).get("url"),
                   "channel": item.get("snippet", {}).get("channelTitle"),
                   "view_count": int(item.get("statistics", {}).get("viewCount", 0)),
                   "embed_url": f"https://www.youtube.com/embed/{video_id}"}
        except Exception as e:
            logger.error(f"Get video details failed: {e}")
            return None


youtube_service = YouTubeService()
