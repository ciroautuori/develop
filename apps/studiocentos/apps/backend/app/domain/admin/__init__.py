"""
Admin Domain Module
Contains admin-specific routers and services
"""

from .inbox_router import router as inbox_router

__all__ = ["inbox_router"]
