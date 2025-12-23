"""
Social API Module.

Router per integrazioni social media:
- LinkedIn Publishing
"""

from app.core.api.v1.social.linkedin_router import router as linkedin_router

__all__ = ["linkedin_router"]
