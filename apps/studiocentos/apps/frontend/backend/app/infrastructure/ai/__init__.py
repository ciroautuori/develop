"""
AI Infrastructure Module

Real AI data fetching from HuggingFace, GitHub, ArXiv.
Centralized AI microservice client.
"""

from .toolai_scraper import ToolAIScraper
from .client import AIClient, ai_client, get_ai_client, AIServiceError

__all__ = [
    "ToolAIScraper",
    "AIClient",
    "ai_client",
    "get_ai_client",
    "AIServiceError"
]
