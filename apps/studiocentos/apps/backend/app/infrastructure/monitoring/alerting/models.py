"""Alert models and enums.

HIGH-005: Extracted from alerting.py (split 1/7)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class AlertSeverity(str, Enum):
    """Livelli di severità alert."""

    CRITICAL = "critical"  # Impatto revenue/sicurezza immediato
    HIGH = "high"  # Degrado performance significativo
    MEDIUM = "medium"  # Issue che richiedono attenzione
    LOW = "low"  # Informational
    INFO = "info"  # Metriche normali


class AlertCategory(str, Enum):
    """Categorie di alert."""

    PAYMENT = "payment"  # Payment failures
    SECURITY = "security"  # Security breaches
    PERFORMANCE = "performance"  # Performance degradation
    UPTIME = "uptime"  # Service availability
    BUSINESS = "business"  # Business metrics
    INFRASTRUCTURE = "infrastructure"  # System health


@dataclass
class Alert:
    """Model per alert enterprise."""

    id: str
    title: str
    description: str
    severity: AlertSeverity
    category: AlertCategory
    timestamp: datetime
    source: str
    metadata: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    escalated: bool = False
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
