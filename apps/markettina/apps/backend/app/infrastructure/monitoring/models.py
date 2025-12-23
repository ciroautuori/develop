"""Monitoring Models - Database persistence for alerts and metrics."""

from enum import Enum as PyEnum

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.infrastructure.database import Base


class AlertSeverityEnum(str, PyEnum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertCategoryEnum(str, PyEnum):
    """Alert categories."""
    PAYMENT = "payment"
    SECURITY = "security"
    PERFORMANCE = "performance"
    AVAILABILITY = "availability"
    RESOURCE = "resource"


class AlertLog(Base):
    """Alert log for monitoring and tracking."""

    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Alert identification
    alert_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Classification
    severity = Column(Enum(AlertSeverityEnum), nullable=False, index=True)
    category = Column(Enum(AlertCategoryEnum), nullable=False, index=True)

    # Source
    source = Column(String(255), nullable=False)

    # Status
    resolved = Column(Boolean, default=False, nullable=False, index=True)
    acknowledged = Column(Boolean, default=False, nullable=False)
    escalated = Column(Boolean, default=False, nullable=False)

    # Metadata
    metadata = Column(JSON, nullable=True)

    # Timestamps
    timestamp = Column(DateTime, nullable=False, default=func.now(), index=True)
    resolved_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)

    # Resolution
    resolved_by = Column(String(255), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<AlertLog(id={self.alert_id}, severity={self.severity}, category={self.category})>"


class MetricLog(Base):
    """Time-series metric logging."""

    __tablename__ = "metric_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Metric identification
    metric_name = Column(String(100), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # counter, gauge, histogram

    # Value
    value = Column(Float, nullable=False)

    # Labels/Tags
    labels = Column(JSON, nullable=True)

    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=func.now(), index=True)

    def __repr__(self):
        return f"<MetricLog(metric={self.metric_name}, value={self.value})>"
