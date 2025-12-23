"""
Core Configuration Module

Centralized configuration for templates, constants, and settings.
"""

from .settings import settings, Settings
from .marketing_templates import (
    get_fallback_template,
    get_fallback_chat_response,
    HASHTAGS,
    LEAD_NEED_REASONS,
    CITY_COORDINATES,
    INDUSTRY_PLACE_TYPES
)

__all__ = [
    "settings",
    "Settings",
    "get_fallback_template",
    "get_fallback_chat_response",
    "HASHTAGS",
    "LEAD_NEED_REASONS",
    "CITY_COORDINATES",
    "INDUSTRY_PLACE_TYPES"
]
