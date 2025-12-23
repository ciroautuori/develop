"""Cache monitoring and statistics.

LOW-002: Caching strategy review and monitoring.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock
from typing import Any


@dataclass
class CacheStats:
    """Cache statistics."""

    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    total_keys: int = 0
    memory_bytes: int = 0


@dataclass
class KeyStats:
    """Statistics for individual cache key."""

    key: str
    hits: int = 0
    misses: int = 0
    last_access: datetime | None = None
    ttl: int | None = None
    size_bytes: int = 0


class CacheMonitor:
    """Monitor cache operations and collect statistics."""

    def __init__(self):
        """Initialize cache monitor."""
        self._global_stats = CacheStats()
        self._key_stats: dict[str, KeyStats] = {}
        self._operation_times = defaultdict(list)
        self._lock = Lock()

    def record_hit(self, key: str, operation_time_ms: float = 0):
        """Record cache hit.

        Args:
            key: Cache key
            operation_time_ms: Operation time in milliseconds
        """
        with self._lock:
            self._global_stats.hits += 1

            if key not in self._key_stats:
                self._key_stats[key] = KeyStats(key=key)

            self._key_stats[key].hits += 1
            self._key_stats[key].last_access = datetime.now(UTC)

            if operation_time_ms > 0:
                self._operation_times["get"].append(operation_time_ms)

    def record_miss(self, key: str, operation_time_ms: float = 0):
        """Record cache miss.

        Args:
            key: Cache key
            operation_time_ms: Operation time in milliseconds
        """
        with self._lock:
            self._global_stats.misses += 1

            if key not in self._key_stats:
                self._key_stats[key] = KeyStats(key=key)

            self._key_stats[key].misses += 1
            self._key_stats[key].last_access = datetime.now(UTC)

            if operation_time_ms > 0:
                self._operation_times["get"].append(operation_time_ms)

    def record_set(self, key: str, size_bytes: int = 0, ttl: int = None):
        """Record cache set operation.

        Args:
            key: Cache key
            size_bytes: Size of cached value in bytes
            ttl: Time-to-live in seconds
        """
        with self._lock:
            self._global_stats.sets += 1

            if key not in self._key_stats:
                self._key_stats[key] = KeyStats(key=key)

            self._key_stats[key].size_bytes = size_bytes
            self._key_stats[key].ttl = ttl

    def record_delete(self, key: str):
        """Record cache delete operation.

        Args:
            key: Cache key
        """
        with self._lock:
            self._global_stats.deletes += 1

            if key in self._key_stats:
                del self._key_stats[key]

    def record_eviction(self, key: str):
        """Record cache eviction.

        Args:
            key: Cache key
        """
        with self._lock:
            self._global_stats.evictions += 1

            if key in self._key_stats:
                del self._key_stats[key]

    def get_stats(self) -> dict[str, Any]:
        """Get current cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_operations = (
                self._global_stats.hits
                + self._global_stats.misses
                + self._global_stats.sets
                + self._global_stats.deletes
            )

            hit_rate = (
                self._global_stats.hits / (self._global_stats.hits + self._global_stats.misses)
                if (self._global_stats.hits + self._global_stats.misses) > 0
                else 0.0
            )

            return {
                "global": {
                    "hits": self._global_stats.hits,
                    "misses": self._global_stats.misses,
                    "sets": self._global_stats.sets,
                    "deletes": self._global_stats.deletes,
                    "evictions": self._global_stats.evictions,
                    "total_operations": total_operations,
                    "hit_rate": round(hit_rate * 100, 2),
                    "total_keys": len(self._key_stats),
                },
                "performance": self._calculate_performance_stats(),
            }

    def get_hottest_keys(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get most frequently accessed keys.

        Args:
            limit: Maximum number of keys to return

        Returns:
            List of hottest keys with statistics
        """
        with self._lock:
            sorted_keys = sorted(
                self._key_stats.values(),
                key=lambda x: x.hits + x.misses,
                reverse=True,
            )[:limit]

            return [
                {
                    "key": key.key,
                    "hits": key.hits,
                    "misses": key.misses,
                    "total_accesses": key.hits + key.misses,
                    "hit_rate": round(
                        (key.hits / (key.hits + key.misses) * 100)
                        if (key.hits + key.misses) > 0
                        else 0,
                        2,
                    ),
                    "size_bytes": key.size_bytes,
                    "ttl": key.ttl,
                }
                for key in sorted_keys
            ]

    def get_coldest_keys(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get least frequently accessed keys (candidates for eviction).

        Args:
            limit: Maximum number of keys to return

        Returns:
            List of coldest keys with statistics
        """
        with self._lock:
            sorted_keys = sorted(
                self._key_stats.values(),
                key=lambda x: x.hits + x.misses,
            )[:limit]

            return [
                {
                    "key": key.key,
                    "hits": key.hits,
                    "misses": key.misses,
                    "total_accesses": key.hits + key.misses,
                    "last_access": key.last_access.isoformat() if key.last_access else None,
                    "size_bytes": key.size_bytes,
                }
                for key in sorted_keys
            ]

    def _calculate_performance_stats(self) -> dict[str, Any]:
        """Calculate performance statistics."""
        stats = {}

        for operation, times in self._operation_times.items():
            if not times:
                continue

            sorted_times = sorted(times)
            count = len(sorted_times)

            stats[operation] = {
                "count": count,
                "avg_ms": round(sum(times) / count, 2),
                "min_ms": round(min(times), 2),
                "max_ms": round(max(times), 2),
                "p50_ms": round(sorted_times[count // 2], 2),
                "p95_ms": round(
                    sorted_times[int(count * 0.95)] if count > 20 else max(times), 2
                ),
                "p99_ms": round(
                    sorted_times[int(count * 0.99)] if count > 100 else max(times), 2
                ),
            }

        return stats

    def reset_stats(self):
        """Reset all statistics."""
        with self._lock:
            self._global_stats = CacheStats()
            self._key_stats.clear()
            self._operation_times.clear()

    def identify_cache_misses_hotspots(self, threshold: int = 10) -> list[dict[str, Any]]:
        """Identify keys with high miss rates (optimization candidates).

        Args:
            threshold: Minimum number of accesses to consider

        Returns:
            List of keys with high miss rates
        """
        with self._lock:
            hotspots = []

            for key, stats in self._key_stats.items():
                total_accesses = stats.hits + stats.misses

                if total_accesses < threshold:
                    continue

                miss_rate = (stats.misses / total_accesses * 100) if total_accesses > 0 else 0

                if miss_rate > 50:  # More than 50% misses
                    hotspots.append(
                        {
                            "key": key,
                            "total_accesses": total_accesses,
                            "misses": stats.misses,
                            "miss_rate": round(miss_rate, 2),
                            "recommendation": "Consider cache warming or longer TTL",
                        }
                    )

            return sorted(hotspots, key=lambda x: x["miss_rate"], reverse=True)


# Global cache monitor instance
cache_monitor = CacheMonitor()


def get_cache_monitor() -> CacheMonitor:
    """Get global cache monitor instance."""
    return cache_monitor
