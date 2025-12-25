"""Redis Cache Manager

Addresses P2: Missing Caching Strategy.
Provides caching functionality with TTL and prefix management.
LOW-002: Enhanced with monitoring and statistics.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import pickle
import time
from functools import wraps
from typing import Any, Callable, Optional
from urllib.parse import urlparse

import redis
from redis.exceptions import ConnectionError, TimeoutError

from app.core.config import settings
from app.infrastructure.cache.cache_monitor import get_cache_monitor
from app.infrastructure.monitoring.logging import get_logger

logger = get_logger("cache")

class CacheConfig:
    """Cache configuration settings."""

    # Redis connection settings
    REDIS_URL = os.getenv("REDIS_URL")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

    # If REDIS_URL is provided (e.g., redis://user:pass@host:6379/0), parse and override
    if REDIS_URL:
        try:
            _u = urlparse(REDIS_URL)
            # Handle both redis and rediss schemes
            if _u.hostname:
                REDIS_HOST = _u.hostname
            if _u.port:
                REDIS_PORT = _u.port
            if _u.path and len(_u.path) > 1:
                # path like "/0"
                try:
                    REDIS_DB = int(_u.path.lstrip("/"))
                except ValueError:
                    pass
            if _u.password:
                REDIS_PASSWORD = _u.password
        except Exception:
            # Do not fail on URL parsing; fallback to individual vars
            pass

    # Cache settings
    DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", "3600"))  # 1 hour
    MAX_CONNECTIONS = int(os.getenv("CACHE_MAX_CONNECTIONS", "10"))
    CONNECTION_TIMEOUT = int(os.getenv("CACHE_CONNECTION_TIMEOUT", "5"))

    # Cache key prefixes (active)
    PREFIX_USER = "user:"
    PREFIX_API = "api:"
    
    # Portfolio cache prefixes
    PREFIX_EXPERIENCE = "exp:"
    PREFIX_EDUCATION = "edu:"
    PREFIX_SKILL = "skill:"
    PREFIX_PROJECT = "project:"
    PREFIX_LANGUAGE = "lang:"
    PREFIX_PORTFOLIO_PROFILE = "portfolio_profile:"

class RedisCache:
    """Redis cache manager with fallback handling."""

    def __init__(self):
        self.redis_client = None
        self.is_available = False
        self._connect()

    def _connect(self):
        """Establish Redis connection with retry + exponential backoff before warning."""
        retries = int(os.getenv("CACHE_REDIS_MAX_RETRIES", "2"))  # Reduced for faster startup
        initial_backoff = float(os.getenv("CACHE_REDIS_INITIAL_BACKOFF", "0.1"))
        backoff = initial_backoff

        last_error: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                self.redis_client = redis.Redis(
                    host=CacheConfig.REDIS_HOST,
                    port=CacheConfig.REDIS_PORT,
                    db=CacheConfig.REDIS_DB,
                    password=CacheConfig.REDIS_PASSWORD,
                    decode_responses=False,  # Handle binary data
                    socket_connect_timeout=CacheConfig.CONNECTION_TIMEOUT,
                    socket_timeout=CacheConfig.CONNECTION_TIMEOUT,
                    max_connections=CacheConfig.MAX_CONNECTIONS,
                    retry_on_timeout=True,
                )

                # Test connection
                self.redis_client.ping()
                self.is_available = True
                logger.info(
                    "Redis cache connected successfully",
                    extra={
                        "event_type": "cache_connected",
                        "host": CacheConfig.REDIS_HOST,
                        "port": CacheConfig.REDIS_PORT,
                        "db": CacheConfig.REDIS_DB,
                        "attempt": attempt,
                    },
                )
                return

            except (ConnectionError, TimeoutError) as e:
                last_error = e
                logger.debug(
                    "Redis connection attempt failed, will retry",
                    extra={
                        "event_type": "cache_connect_retry",
                        "attempt": attempt,
                        "max_retries": retries,
                        "backoff_seconds": backoff,
                        "error": str(e),
                    },
                )
                time.sleep(backoff)
                backoff = min(backoff * 2, 8.0)  # cap backoff

        # All retries exhausted
        logger.warning(
            "Redis cache unavailable after retries, falling back to no-cache mode",
            extra={
                "event_type": "cache_unavailable",
                "error": str(last_error) if last_error else None,
                "fallback_mode": True,
                "retries": retries,
            },
        )
        self.is_available = False

    def get(self, key: str) -> Any | None:
        """Get value from cache with deserialization."""
        if not self.is_available:
            return None

        start_time = time.perf_counter()
        monitor = get_cache_monitor()

        try:
            value = self.redis_client.get(key)
            operation_time_ms = (time.perf_counter() - start_time) * 1000

            if value is None:
                logger.debug(f"Cache miss for key: {key}")
                monitor.record_miss(key, operation_time_ms)
                return None

            # Try JSON first, fallback to pickle
            try:
                decoded_value = json.loads(value.decode("utf-8"))
                logger.debug(f"Cache hit (JSON) for key: {key}")
                monitor.record_hit(key, operation_time_ms)
                return decoded_value
            except (json.JSONDecodeError, UnicodeDecodeError):
                decoded_value = pickle.loads(value)
                logger.debug(f"Cache hit (pickle) for key: {key}")
                monitor.record_hit(key, operation_time_ms)
                return decoded_value

        except Exception as e:
            operation_time_ms = (time.perf_counter() - start_time) * 1000
            monitor.record_miss(key, operation_time_ms)
            logger.error(
                f"Cache get error for key {key}: {e}",
                extra={"event_type": "cache_get_error", "cache_key": key, "error": str(e)},
            )
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache with serialization."""
        if not self.is_available:
            return False

        monitor = get_cache_monitor()

        try:
            # Use JSON for simple types, pickle for complex objects
            try:
                serialized_value = json.dumps(value, default=str)
            except (TypeError, ValueError):
                serialized_value = pickle.dumps(value)

            ttl = ttl or CacheConfig.DEFAULT_TTL
            size_bytes = len(serialized_value) if isinstance(serialized_value, (str, bytes)) else 0
            success = self.redis_client.setex(key, ttl, serialized_value)

            if success:
                logger.debug(f"Cache set for key: {key}, TTL: {ttl}s")
                monitor.record_set(key, size_bytes, ttl)

            return bool(success)

        except Exception as e:
            logger.error(
                f"Cache set error for key {key}: {e}",
                extra={"event_type": "cache_set_error", "cache_key": key, "error": str(e)},
            )
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.is_available:
            return False

        try:
            result = self.redis_client.delete(key)
            if result:
                logger.debug(f"Cache delete for key: {key}")
            return bool(result)
        except Exception as e:
            logger.error(
                f"Cache delete error for key {key}: {e}",
                extra={"event_type": "cache_delete_error", "cache_key": key, "error": str(e)},
            )
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.is_available:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.debug(f"Cache deleted {deleted} keys matching pattern: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(
                f"Cache delete pattern error for {pattern}: {e}",
                extra={
                    "event_type": "cache_delete_pattern_error",
                    "pattern": pattern,
                    "error": str(e),
                },
            )
            return 0

    def clear_user_cache(self, user_id: int):
        """Clear all cache entries for a specific user."""
        # Only clear active cache prefixes (Portfolio not yet implemented)
        patterns = [
            f"{CacheConfig.PREFIX_USER}{user_id}:*",
        ]
        
        # Portfolio cache patterns
        patterns.extend([
            f"{CacheConfig.PREFIX_EXPERIENCE}{user_id}:*",
            f"{CacheConfig.PREFIX_EDUCATION}{user_id}:*",
            f"{CacheConfig.PREFIX_SKILL}{user_id}:*",
            f"{CacheConfig.PREFIX_PROJECT}{user_id}:*",
            f"{CacheConfig.PREFIX_LANGUAGE}{user_id}:*",
            f"{CacheConfig.PREFIX_PORTFOLIO_PROFILE}{user_id}:*",
        ])

        total_deleted = 0
        for pattern in patterns:
            total_deleted += self.delete_pattern(pattern)

        logger.info(
            f"Cleared cache for user {user_id}, deleted {total_deleted} entries",
            extra={
                "event_type": "cache_user_cleared",
                "user_id": user_id,
                "deleted_count": total_deleted,
            },
        )

        return total_deleted

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        if not self.is_available:
            return {"status": "unavailable", "is_available": False}

        try:
            info = self.redis_client.info()
            return {
                "status": "available",
                "is_available": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info),
                "total_commands_processed": info.get("total_commands_processed", 0),
            }
        except Exception as e:
            return {"status": "error", "is_available": False, "error": str(e)}

    def _calculate_hit_rate(self, info: dict) -> float:
        """Calculate cache hit rate percentage."""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0

# Global cache instance
cache = RedisCache()

def cache_key_builder(*args, **kwargs) -> str:
    """Build cache key from function arguments."""
    key_parts = []

    # Add positional args
    for arg in args:
        if hasattr(arg, "__dict__"):  # Skip complex objects
            key_parts.append(str(type(arg).__name__))
        else:
            key_parts.append(str(arg))

    # Add keyword args
    for k, v in sorted(kwargs.items()):
        if not k.startswith("_"):  # Skip private kwargs
            key_parts.append(f"{k}={v}")

    # Create hash of the key parts to avoid very long keys
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def cached(
    prefix: str = CacheConfig.PREFIX_API,
    ttl: Optional[int] = None,
    key_builder: Optional[Callable] = None,
):
    """Decorator for caching function results.

    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
        key_builder: Custom function to build cache key
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = f"{prefix}{key_builder(*args, **kwargs)}"
            else:
                cache_key = f"{prefix}{func.__name__}:{cache_key_builder(*args, **kwargs)}"

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(
                    f"Cache hit for {func.__name__}",
                    extra={
                        "event_type": "cache_hit",
                        "function": func.__name__,
                        "cache_key": cache_key,
                    },
                )
                return cached_result

            # Execute function
            logger.debug(
                f"Cache miss for {func.__name__}, executing function",
                extra={
                    "event_type": "cache_miss",
                    "function": func.__name__,
                    "cache_key": cache_key,
                },
            )

            result = func(*args, **kwargs)

            # Cache the result
            cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator

# Convenience decorators for different data types
def cache_profile(ttl: int = 1800):  # 30 minutes
    """Cache profile data."""
    return cached(prefix=CacheConfig.PREFIX_PROFILE, ttl=ttl)

def cache_user(ttl: int = 3600):  # 1 hour
    """Cache user data."""
    return cached(prefix=CacheConfig.PREFIX_USER, ttl=ttl)

def cache_api(ttl: int = 600):  # 10 minutes
    """Cache API responses."""
    return cached(prefix=CacheConfig.PREFIX_API, ttl=ttl)

# Export main components
__all__ = ["cache", "cached", "cache_profile", "cache_user", "cache_api", "CacheConfig"]
