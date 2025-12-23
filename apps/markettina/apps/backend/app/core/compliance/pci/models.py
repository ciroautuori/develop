"""PCI DSS models.

HIGH-005: Extracted from pci_dss.py (split 1/3)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PCIComplianceLevel(str, Enum):
    """Livelli di compliance PCI DSS."""

    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"
    LEVEL_4 = "level_4"


class PCIRequirement(str, Enum):
    """12 Requirements PCI DSS principali."""

    REQ_1 = "req_1"  # Install and maintain firewall
    REQ_2 = "req_2"  # No default passwords
    REQ_3 = "req_3"  # Protect stored cardholder data
    REQ_4 = "req_4"  # Encrypt transmission
    REQ_5 = "req_5"  # Use antivirus
    REQ_6 = "req_6"  # Develop secure systems
    REQ_7 = "req_7"  # Restrict access
    REQ_8 = "req_8"  # Assign unique ID
    REQ_9 = "req_9"  # Restrict physical access
    REQ_10 = "req_10"  # Track and monitor
    REQ_11 = "req_11"  # Test security systems
    REQ_12 = "req_12"  # Maintain information security policy


@dataclass
class PCIComplianceCheck:
    """Singolo check di compliance PCI DSS."""

    requirement: PCIRequirement
    description: str
    compliant: bool
    findings: list[str]
    remediation: str
    last_tested: datetime
    next_test_due: datetime
