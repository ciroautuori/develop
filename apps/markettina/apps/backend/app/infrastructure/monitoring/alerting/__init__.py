"""Enterprise Alerting & Incident Response System.

HIGH-005: Split from monolithic alerting.py (740 lines → 7 modular files)
"""

from .alert_manager import AlertManager
from .models import Alert, AlertCategory, AlertSeverity

# Backward compatibility exports
__all__ = [
    "Alert",
    "AlertCategory",
    "AlertManager",
    "AlertSeverity",
]
