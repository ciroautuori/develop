"""Enterprise Alerting & Incident Response System.

HIGH-005: Split from monolithic alerting.py (740 lines → 7 modular files)
"""

from .models import Alert, AlertCategory, AlertSeverity
from .alert_manager import AlertManager

# Backward compatibility exports
__all__ = [
    "Alert",
    "AlertCategory", 
    "AlertSeverity",
    "AlertManager",
]
