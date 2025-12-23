"""Prometheus-style Metrics Collection.

LOW-007: Custom metrics for enhanced monitoring.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any


@dataclass
class MetricValue:
    """Individual metric value with timestamp."""

    value: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    labels: dict[str, str] = field(default_factory=dict)


class Counter:
    """Counter metric - monotonically increasing value."""

    def __init__(self, name: str, description: str):
        """Initialize counter.

        Args:
            name: Metric name
            description: Metric description
        """
        self.name = name
        self.description = description
        self._value = 0
        self._lock = Lock()

    def inc(self, amount: float = 1.0):
        """Increment counter.

        Args:
            amount: Amount to increment (default: 1.0)
        """
        with self._lock:
            self._value += amount

    def get(self) -> float:
        """Get current counter value."""
        with self._lock:
            return self._value

    def reset(self):
        """Reset counter to zero."""
        with self._lock:
            self._value = 0


class Gauge:
    """Gauge metric - value that can go up and down."""

    def __init__(self, name: str, description: str):
        """Initialize gauge.

        Args:
            name: Metric name
            description: Metric description
        """
        self.name = name
        self.description = description
        self._value = 0.0
        self._lock = Lock()

    def set(self, value: float):
        """Set gauge value.

        Args:
            value: New value
        """
        with self._lock:
            self._value = value

    def inc(self, amount: float = 1.0):
        """Increment gauge.

        Args:
            amount: Amount to increment
        """
        with self._lock:
            self._value += amount

    def dec(self, amount: float = 1.0):
        """Decrement gauge.

        Args:
            amount: Amount to decrement
        """
        with self._lock:
            self._value -= amount

    def get(self) -> float:
        """Get current gauge value."""
        with self._lock:
            return self._value


class Histogram:
    """Histogram metric - tracks distribution of values."""

    def __init__(self, name: str, description: str, buckets: list[float] = None):
        """Initialize histogram.

        Args:
            name: Metric name
            description: Metric description
            buckets: Bucket boundaries (default: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10])
        """
        self.name = name
        self.description = description
        self.buckets = buckets or [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
        self._observations = []
        self._bucket_counts = defaultdict(int)
        self._sum = 0.0
        self._count = 0
        self._lock = Lock()

    def observe(self, value: float):
        """Observe a value.

        Args:
            value: Value to observe
        """
        with self._lock:
            self._observations.append(value)
            self._sum += value
            self._count += 1

            # Update bucket counts
            for bucket in self.buckets:
                if value <= bucket:
                    self._bucket_counts[bucket] += 1

    def get_stats(self) -> dict[str, Any]:
        """Get histogram statistics.

        Returns:
            Dictionary with count, sum, and bucket counts
        """
        with self._lock:
            return {
                "count": self._count,
                "sum": self._sum,
                "buckets": dict(self._bucket_counts),
            }


class Summary:
    """Summary metric - calculates quantiles over time window."""

    def __init__(self, name: str, description: str, max_age_seconds: int = 600):
        """Initialize summary.

        Args:
            name: Metric name
            description: Metric description
            max_age_seconds: Maximum age of observations (default: 600)
        """
        self.name = name
        self.description = description
        self.max_age_seconds = max_age_seconds
        self._observations: list[MetricValue] = []
        self._lock = Lock()

    def observe(self, value: float):
        """Observe a value.

        Args:
            value: Value to observe
        """
        with self._lock:
            # Add new observation
            self._observations.append(MetricValue(value=value))

            # Remove old observations
            cutoff_time = datetime.now(UTC).timestamp() - self.max_age_seconds
            self._observations = [
                obs
                for obs in self._observations
                if obs.timestamp.timestamp() >= cutoff_time
            ]

    def get_quantile(self, q: float) -> float:
        """Get quantile value.

        Args:
            q: Quantile (0.0 - 1.0)

        Returns:
            Quantile value
        """
        with self._lock:
            if not self._observations:
                return 0.0

            values = sorted([obs.value for obs in self._observations])
            index = int(len(values) * q)
            return values[min(index, len(values) - 1)]

    def get_stats(self) -> dict[str, Any]:
        """Get summary statistics.

        Returns:
            Dictionary with count and quantiles
        """
        with self._lock:
            if not self._observations:
                return {
                    "count": 0,
                    "sum": 0.0,
                    "quantiles": {},
                }

            values = [obs.value for obs in self._observations]

            return {
                "count": len(values),
                "sum": sum(values),
                "quantiles": {
                    "0.5": self.get_quantile(0.5),
                    "0.9": self.get_quantile(0.9),
                    "0.95": self.get_quantile(0.95),
                    "0.99": self.get_quantile(0.99),
                },
            }


class MetricsRegistry:
    """Central registry for all metrics."""

    def __init__(self):
        """Initialize metrics registry."""
        self._metrics: dict[str, Any] = {}
        self._lock = Lock()

    def register_counter(self, name: str, description: str) -> Counter:
        """Register and return a counter.

        Args:
            name: Metric name
            description: Metric description

        Returns:
            Counter instance
        """
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Counter(name, description)
            return self._metrics[name]

    def register_gauge(self, name: str, description: str) -> Gauge:
        """Register and return a gauge.

        Args:
            name: Metric name
            description: Metric description

        Returns:
            Gauge instance
        """
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Gauge(name, description)
            return self._metrics[name]

    def register_histogram(
        self, name: str, description: str, buckets: list[float] = None
    ) -> Histogram:
        """Register and return a histogram.

        Args:
            name: Metric name
            description: Metric description
            buckets: Bucket boundaries

        Returns:
            Histogram instance
        """
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Histogram(name, description, buckets)
            return self._metrics[name]

    def register_summary(
        self, name: str, description: str, max_age_seconds: int = 600
    ) -> Summary:
        """Register and return a summary.

        Args:
            name: Metric name
            description: Metric description
            max_age_seconds: Maximum age of observations

        Returns:
            Summary instance
        """
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Summary(name, description, max_age_seconds)
            return self._metrics[name]

    def get_all_metrics(self) -> dict[str, Any]:
        """Get all metrics and their current values.

        Returns:
            Dictionary of all metrics
        """
        with self._lock:
            result = {}

            for name, metric in self._metrics.items():
                if isinstance(metric, (Counter, Gauge)):
                    result[name] = {
                        "type": metric.__class__.__name__.lower(),
                        "description": metric.description,
                        "value": metric.get(),
                    }
                elif isinstance(metric, (Histogram, Summary)):
                    result[name] = {
                        "type": metric.__class__.__name__.lower(),
                        "description": metric.description,
                        **metric.get_stats(),
                    }

            return result


# Global registry instance
metrics_registry = MetricsRegistry()

# Pre-register common metrics
request_count = metrics_registry.register_counter(
    "http_requests_total", "Total HTTP requests"
)
request_duration = metrics_registry.register_histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
)
active_requests = metrics_registry.register_gauge(
    "http_requests_active", "Number of active HTTP requests"
)
database_connections = metrics_registry.register_gauge(
    "database_connections_active", "Number of active database connections"
)
cache_hits = metrics_registry.register_counter("cache_hits_total", "Total cache hits")
cache_misses = metrics_registry.register_counter(
    "cache_misses_total", "Total cache misses"
)


def get_metrics_registry() -> MetricsRegistry:
    """Get global metrics registry instance."""
    return metrics_registry
