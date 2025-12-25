"""GDPR models and schemas.

HIGH-005: Extracted from gdpr.py (split 1/4)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DataProcessingPurpose(str, Enum):
    """Scopi di trattamento dati secondo GDPR Art. 6."""

    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class ConsentStatus(str, Enum):
    """Stato del consenso GDPR."""

    GIVEN = "given"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"


@dataclass
class DataSubjectRight:
    """Diritti del soggetto interessato secondo GDPR."""

    right_name: str
    description: str
    article: str


# Diritti GDPR implementati
GDPR_RIGHTS = {
    "access": DataSubjectRight(
        "Right of Access", "Right to obtain confirmation and access to personal data", "Article 15"
    ),
    "rectification": DataSubjectRight(
        "Right to Rectification", "Right to rectification of inaccurate personal data", "Article 16"
    ),
    "erasure": DataSubjectRight(
        "Right to Erasure (Right to be Forgotten)",
        "Right to erasure of personal data",
        "Article 17",
    ),
    "restrict": DataSubjectRight(
        "Right to Restriction of Processing", "Right to restriction of processing", "Article 18"
    ),
    "portability": DataSubjectRight(
        "Right to Data Portability",
        "Right to receive personal data in structured format",
        "Article 20",
    ),
    "object": DataSubjectRight("Right to Object", "Right to object to processing", "Article 21"),
}


class ConsentModel(BaseModel):
    """Model per consenso GDPR."""

    user_id: str
    purpose: DataProcessingPurpose
    status: ConsentStatus = ConsentStatus.PENDING
    consent_text: str = Field(..., min_length=10)
    granted_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    ip_address: str
    user_agent: str


class DataExportRequest(BaseModel):
    """Richiesta esportazione dati (Art. 20)."""

    user_id: str
    requested_at: datetime
    format: str = Field(default="json", pattern="^(json|xml|csv)$")
    include_metadata: bool = False


class DataDeletionRequest(BaseModel):
    """Richiesta cancellazione dati (Art. 17)."""

    user_id: str
    requested_at: datetime
    reason: str = Field(..., min_length=5)
    hard_delete: bool = False
