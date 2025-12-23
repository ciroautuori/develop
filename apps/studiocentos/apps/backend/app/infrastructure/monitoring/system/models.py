"""System monitoring models.

HIGH-005: Extracted from system.py (split 1/3)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Alert:
    id: str
    level: AlertLevel
    title: str
    message: str
    source: str
    timestamp: datetime
    metadata: dict
    resolved: bool = False
    resolved_at: datetime | None = None


@dataclass
class PerformanceMetric:
    name: str
    value: float
    unit: str
    timestamp: datetime
    labels: dict[str, str]


@dataclass
class SystemHealth:
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_connections: int
    request_rate: float
    error_rate: float
    uptime_seconds: float
    timestamp: datetime
