"""Metrics collection service.

HIGH-005: Extracted from system.py (split 3/3)
"""

import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and aggregate system metrics."""

    def __init__(self):
        self.metrics = {}

    async def collect_cpu_metrics(self) -> float:
        """Collect CPU metrics."""
        return 0.0

    async def collect_memory_metrics(self) -> float:
        """Collect memory metrics."""
        return 0.0

    async def collect_disk_metrics(self) -> float:
        """Collect disk metrics."""
        return 0.0
