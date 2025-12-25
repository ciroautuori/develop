"""
A/B Testing Framework per Marketing.

Features:
- Creazione test con varianti
- Distribuzione traffico
- Tracking conversioni
- Analisi statistica risultati
- Winner selection automatica
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
import logging
import uuid
import random
import math

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & MODELS
# ============================================================================

class TestType(str, Enum):
    EMAIL_SUBJECT = "email_subject"
    EMAIL_CONTENT = "email_content"
    LANDING_PAGE = "landing_page"
    CTA_BUTTON = "cta_button"
    SOCIAL_POST = "social_post"
    AD_COPY = "ad_copy"


class TestStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Variant(BaseModel):
    """Singola variante del test."""
    id: str
    name: str
    content: str
    traffic_percent: float = 50.0
    impressions: int = 0
    conversions: int = 0
    clicks: int = 0
    revenue: float = 0.0
    conversion_rate: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ABTest(BaseModel):
    """Definizione test A/B."""
    id: str
    name: str
    description: str = ""
    test_type: TestType
    variants: List[Variant]
    status: TestStatus = TestStatus.DRAFT
    goal: str = "conversions"  # conversions, clicks, revenue
    min_sample_size: int = 100
    confidence_level: float = 95.0
    winner_id: Optional[str] = None
    auto_select_winner: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_by: int = 1


class TestResult(BaseModel):
    """Risultati analisi test."""
    test_id: str
    winner: Optional[Variant] = None
    confidence: float = 0.0
    statistical_significance: bool = False
    lift_percent: float = 0.0
    p_value: float = 1.0
    sample_size_reached: bool = False
    recommendation: str = ""


# ============================================================================
# A/B TESTING SERVICE
# ============================================================================

class ABTestingService:
    """
    Service per A/B Testing marketing.

    Gestisce:
    - Creazione e gestione test
    - Assegnazione utenti a varianti
    - Tracking eventi
    - Calcolo risultati statistici
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._tests: Dict[str, ABTest] = {}
        self._user_assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {test_id: variant_id}
        self._initialized = True
        logger.info("ab_testing_service_initialized")

    # ========================================================================
    # TEST CRUD
    # ========================================================================

    def create_test(self, test: ABTest) -> ABTest:
        """Crea nuovo A/B test."""
        # Valida varianti (somma traffic = 100%)
        total_traffic = sum(v.traffic_percent for v in test.variants)
        if abs(total_traffic - 100.0) > 0.1:
            raise ValueError(f"Traffic percent must sum to 100%, got {total_traffic}")

        self._tests[test.id] = test
        logger.info(f"ab_test_created: {test.id} - {test.name}")
        return test

    def get_test(self, test_id: str) -> Optional[ABTest]:
        return self._tests.get(test_id)

    def list_tests(self, status: Optional[TestStatus] = None) -> List[ABTest]:
        tests = list(self._tests.values())
        if status:
            tests = [t for t in tests if t.status == status]
        return tests

    def update_test(self, test_id: str, updates: Dict[str, Any]) -> Optional[ABTest]:
        test = self._tests.get(test_id)
        if not test:
            return None

        for key, value in updates.items():
            if hasattr(test, key) and key not in ['id', 'created_at']:
                setattr(test, key, value)

        self._tests[test_id] = test
        return test

    def delete_test(self, test_id: str) -> bool:
        if test_id in self._tests:
            del self._tests[test_id]
            return True
        return False

    def start_test(self, test_id: str) -> bool:
        """Avvia test."""
        test = self._tests.get(test_id)
        if test and test.status == TestStatus.DRAFT:
            test.status = TestStatus.RUNNING
            test.started_at = datetime.utcnow()
            return True
        return False

    def pause_test(self, test_id: str) -> bool:
        """Pausa test."""
        test = self._tests.get(test_id)
        if test and test.status == TestStatus.RUNNING:
            test.status = TestStatus.PAUSED
            return True
        return False

    def stop_test(self, test_id: str) -> bool:
        """Termina test."""
        test = self._tests.get(test_id)
        if test and test.status in [TestStatus.RUNNING, TestStatus.PAUSED]:
            test.status = TestStatus.COMPLETED
            test.ended_at = datetime.utcnow()

            # Auto-select winner if enabled
            if test.auto_select_winner:
                result = self.analyze_test(test_id)
                if result.statistical_significance and result.winner:
                    test.winner_id = result.winner.id

            return True
        return False

    # ========================================================================
    # VARIANT ASSIGNMENT
    # ========================================================================

    def get_variant_for_user(self, test_id: str, user_id: str) -> Optional[Variant]:
        """
        Ottieni variante per utente (deterministic).
        Mantiene consistenza tra sessioni.
        """
        test = self._tests.get(test_id)
        if not test or test.status != TestStatus.RUNNING:
            return None

        # Check existing assignment
        if user_id in self._user_assignments:
            if test_id in self._user_assignments[user_id]:
                variant_id = self._user_assignments[user_id][test_id]
                return next((v for v in test.variants if v.id == variant_id), None)

        # New assignment based on traffic split
        variant = self._assign_variant(test, user_id)

        # Store assignment
        if user_id not in self._user_assignments:
            self._user_assignments[user_id] = {}
        self._user_assignments[user_id][test_id] = variant.id

        # Track impression
        variant.impressions += 1

        return variant

    def _assign_variant(self, test: ABTest, user_id: str) -> Variant:
        """Assegna variante basata su traffic split."""
        # Hash-based assignment per consistenza
        hash_value = hash(f"{test.id}:{user_id}") % 10000
        normalized = hash_value / 10000 * 100

        cumulative = 0.0
        for variant in test.variants:
            cumulative += variant.traffic_percent
            if normalized <= cumulative:
                return variant

        return test.variants[-1]

    # ========================================================================
    # EVENT TRACKING
    # ========================================================================

    def track_event(self, test_id: str, variant_id: str, event_type: str, value: float = 1.0):
        """
        Traccia evento per variante.

        Args:
            test_id: ID test
            variant_id: ID variante
            event_type: click, conversion, revenue
            value: valore evento (default 1)
        """
        test = self._tests.get(test_id)
        if not test:
            return

        variant = next((v for v in test.variants if v.id == variant_id), None)
        if not variant:
            return

        if event_type == "click":
            variant.clicks += 1
        elif event_type == "conversion":
            variant.conversions += int(value)
        elif event_type == "revenue":
            variant.revenue += value

        # Ricalcola conversion rate
        if variant.impressions > 0:
            variant.conversion_rate = (variant.conversions / variant.impressions) * 100

        logger.debug(f"ab_test_event: {test_id}/{variant_id} - {event_type}={value}")

    # ========================================================================
    # STATISTICAL ANALYSIS
    # ========================================================================

    def analyze_test(self, test_id: str) -> TestResult:
        """
        Analizza risultati test con calcolo statistico.

        Calcola:
        - Conversion rate per variante
        - Statistical significance (chi-squared)
        - Confidence interval
        - Lift percentage
        """
        test = self._tests.get(test_id)
        if not test or len(test.variants) < 2:
            return TestResult(test_id=test_id, recommendation="Test non valido")

        # Ordina varianti per metrica goal
        sorted_variants = sorted(
            test.variants,
            key=lambda v: v.conversion_rate if test.goal == "conversions"
                         else v.clicks if test.goal == "clicks"
                         else v.revenue,
            reverse=True
        )

        best = sorted_variants[0]
        control = sorted_variants[-1]  # Assume last is control

        # Check sample size
        total_impressions = sum(v.impressions for v in test.variants)
        sample_reached = total_impressions >= test.min_sample_size

        # Calculate statistical significance
        p_value = self._calculate_p_value(best, control)
        is_significant = p_value < (1 - test.confidence_level / 100)
        confidence = (1 - p_value) * 100

        # Calculate lift
        if control.conversion_rate > 0:
            lift = ((best.conversion_rate - control.conversion_rate) / control.conversion_rate) * 100
        else:
            lift = 0

        # Generate recommendation
        if not sample_reached:
            recommendation = f"Continua il test. Servono ancora {test.min_sample_size - total_impressions} impressions."
        elif is_significant:
            recommendation = f"✅ '{best.name}' è il vincitore con {confidence:.1f}% confidence e +{lift:.1f}% lift."
        else:
            recommendation = f"⚠️ Risultati non conclusivi. P-value: {p_value:.4f}. Continua il test."

        return TestResult(
            test_id=test_id,
            winner=best if is_significant else None,
            confidence=confidence,
            statistical_significance=is_significant,
            lift_percent=lift,
            p_value=p_value,
            sample_size_reached=sample_reached,
            recommendation=recommendation
        )

    def _calculate_p_value(self, variant_a: Variant, variant_b: Variant) -> float:
        """
        Calcola p-value usando chi-squared test.
        Simplified implementation.
        """
        if variant_a.impressions == 0 or variant_b.impressions == 0:
            return 1.0

        # Observed values
        a_conv = variant_a.conversions
        a_no_conv = variant_a.impressions - variant_a.conversions
        b_conv = variant_b.conversions
        b_no_conv = variant_b.impressions - variant_b.conversions

        total = variant_a.impressions + variant_b.impressions
        total_conv = a_conv + b_conv
        total_no_conv = a_no_conv + b_no_conv

        if total_conv == 0 or total_no_conv == 0:
            return 1.0

        # Expected values
        exp_a_conv = (variant_a.impressions * total_conv) / total
        exp_a_no_conv = (variant_a.impressions * total_no_conv) / total
        exp_b_conv = (variant_b.impressions * total_conv) / total
        exp_b_no_conv = (variant_b.impressions * total_no_conv) / total

        # Chi-squared
        chi2 = 0
        for obs, exp in [(a_conv, exp_a_conv), (a_no_conv, exp_a_no_conv),
                         (b_conv, exp_b_conv), (b_no_conv, exp_b_no_conv)]:
            if exp > 0:
                chi2 += ((obs - exp) ** 2) / exp

        # Approximate p-value (1 degree of freedom)
        # Using simple approximation
        if chi2 > 10.83:
            return 0.001
        elif chi2 > 6.64:
            return 0.01
        elif chi2 > 3.84:
            return 0.05
        elif chi2 > 2.71:
            return 0.10
        else:
            return 0.5

    def get_test_summary(self, test_id: str) -> Dict[str, Any]:
        """Ottieni summary test per dashboard."""
        test = self._tests.get(test_id)
        if not test:
            return {}

        result = self.analyze_test(test_id)

        return {
            "id": test.id,
            "name": test.name,
            "status": test.status.value,
            "type": test.test_type.value,
            "variants": [
                {
                    "id": v.id,
                    "name": v.name,
                    "impressions": v.impressions,
                    "conversions": v.conversions,
                    "conversion_rate": round(v.conversion_rate, 2),
                    "is_winner": v.id == test.winner_id
                }
                for v in test.variants
            ],
            "result": {
                "confidence": round(result.confidence, 1),
                "significant": result.statistical_significance,
                "lift": round(result.lift_percent, 1),
                "recommendation": result.recommendation
            },
            "started_at": test.started_at.isoformat() if test.started_at else None,
            "ended_at": test.ended_at.isoformat() if test.ended_at else None
        }


# Singleton instance
ab_testing_service = ABTestingService()


# ============================================================================
# QUICK CREATORS
# ============================================================================

def create_email_subject_test(name: str, subjects: List[str]) -> ABTest:
    """Crea test A/B per oggetto email."""
    traffic_per_variant = 100.0 / len(subjects)

    variants = [
        Variant(
            id=f"var_{i}",
            name=f"Variante {chr(65+i)}",
            content=subject,
            traffic_percent=traffic_per_variant
        )
        for i, subject in enumerate(subjects)
    ]

    return ABTest(
        id=f"test_{uuid.uuid4().hex[:12]}",
        name=name,
        description=f"Test A/B oggetto email con {len(subjects)} varianti",
        test_type=TestType.EMAIL_SUBJECT,
        variants=variants,
        goal="conversions"
    )


def create_cta_test(name: str, cta_texts: List[str]) -> ABTest:
    """Crea test A/B per CTA button."""
    traffic_per_variant = 100.0 / len(cta_texts)

    variants = [
        Variant(
            id=f"var_{i}",
            name=f"CTA {chr(65+i)}",
            content=cta,
            traffic_percent=traffic_per_variant
        )
        for i, cta in enumerate(cta_texts)
    ]

    return ABTest(
        id=f"test_{uuid.uuid4().hex[:12]}",
        name=name,
        description=f"Test A/B CTA con {len(cta_texts)} varianti",
        test_type=TestType.CTA_BUTTON,
        variants=variants,
        goal="clicks"
    )
