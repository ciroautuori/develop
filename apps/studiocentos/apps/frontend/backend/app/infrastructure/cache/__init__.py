"""Cache Infrastructure
Gestisce Redis e cache manager.
"""

from .manager import RedisCache, cache

__all__ = ["RedisCache", "cache"]
