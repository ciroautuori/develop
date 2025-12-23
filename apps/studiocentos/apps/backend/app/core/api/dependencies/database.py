"""
Database dependencies for FastAPI
"""

from app.infrastructure.database.session import get_db

# Re-export get_db function
__all__ = ["get_db"]
