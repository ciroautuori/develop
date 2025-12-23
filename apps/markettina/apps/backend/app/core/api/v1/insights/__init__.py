"""
Insights API Package

Analytics e metriche da piattaforme social.
"""

from app.core.api.v1.insights.instagram_router import router as instagram_router

__all__ = ["instagram_router"]
