"""
Pain Analyzer Domain Service

Analyzes pain patterns and trends to provide insights.
This is domain logic that doesn't naturally belong to a single entity.
"""
from typing import List, Dict
from datetime import datetime, timedelta
import statistics

from src.domain.entities.pain_assessment import PainAssessment


class PainAnalyzer:
    """
    Domain service for pain analysis.

    Provides sophisticated pain pattern analysis without dependencies
    on infrastructure (databases, external APIs, etc.)
    """

    def analyze_trend(self, assessments: List[PainAssessment]) -> Dict:
        """
        Analyze pain trend over time.

        Returns:
            dict with trend, variability, and insights
        """
        if not assessments:
            return {
                "trend": "insufficient_data",
                "message": "Necessari almeno 3 giorni di dati"
            }

        # Sort by date
        sorted_assessments = sorted(assessments, key=lambda x: x.date)
        pain_levels = [a.pain_level for a in sorted_assessments]

        # Calculate trend (simple linear regression slope)
        trend = self._calculate_trend(pain_levels)

        # Calculate variability
        variability = statistics.stdev(pain_levels) if len(pain_levels) > 1 else 0

        # Determine trend category
        if trend < -0.3:
            trend_label = "miglioramento"
        elif trend > 0.3:
            trend_label = "peggioramento"
        else:
            trend_label = "stabile"

        return {
            "trend": trend_label,
            "trend_score": round(trend, 2),
            "variability": round(variability, 2),
            "avg_pain": round(statistics.mean(pain_levels), 1),
            "max_pain": max(pain_levels),
            "min_pain": min(pain_levels),
            "num_assessments": len(pain_levels)
        }

    def identify_triggers(self, assessments: List[PainAssessment]) -> Dict:
        """
        Identify most common pain triggers.

        Returns:
            dict with trigger frequencies and recommendations
        """
        if not assessments:
            return {"triggers": [], "recommendation": "Insufficienti dati"}

        # Count trigger occurrences
        trigger_counts = {}
        total_with_triggers = 0

        for assessment in assessments:
            if assessment.triggers:
                total_with_triggers += 1
                for trigger in assessment.triggers:
                    trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1

        # Sort by frequency
        sorted_triggers = sorted(trigger_counts.items(),
                               key=lambda x: x[1], reverse=True)

        main_triggers = [trigger for trigger, _ in sorted_triggers[:3]]

        # Generate recommendation
        recommendation = self._generate_trigger_recommendation(main_triggers)

        return {
            "main_triggers": main_triggers,
            "trigger_frequencies": dict(sorted_triggers),
            "recommendation": recommendation
        }

    def find_best_time_of_day(self, assessments: List[PainAssessment]) -> str:
        """
        Find time of day with lowest average pain.
        """
        if not assessments:
            return "unknown"

        morning_pain = []  # 6-12
        afternoon_pain = []  # 12-18
        evening_pain = []  # 18-24

        for assessment in assessments:
            hour = assessment.date.hour

            if 6 <= hour < 12:
                morning_pain.append(assessment.pain_level)
            elif 12 <= hour < 18:
                afternoon_pain.append(assessment.pain_level)
            elif 18 <= hour < 24:
                evening_pain.append(assessment.pain_level)

        # Calculate averages
        averages = {}
        if morning_pain:
            averages["mattina"] = statistics.mean(morning_pain)
        if afternoon_pain:
            averages["pomeriggio"] = statistics.mean(afternoon_pain)
        if evening_pain:
            averages["sera"] = statistics.mean(evening_pain)

        if not averages:
            return "unknown"

        return min(averages, key=averages.get)

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate simple linear regression slope."""
        if len(values) < 2:
            return 0.0

        n = len(values)
        x = list(range(n))

        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _generate_trigger_recommendation(self, triggers: List[str]) -> str:
        """Generate recommendation based on triggers."""
        if not triggers:
            return "Continua a monitorare i fattori scatenanti"

        recommendations = {
            "seduto_prolungato": "Alzati ogni 30 minuti, usa standing desk",
            "flessione_lombare": "Evita flessioni profonde, usa hinge pattern",
            "estensione_lombare": "Limita estensioni, focus su stabilità core",
            "rotazione": "Evita rotazioni carico, lavora mobilità toracica",
            "carico_pesante": "Ridurre intensità carico, focus su tecnica"
        }

        main_trigger = triggers[0] if triggers else None
        return recommendations.get(main_trigger,
                                  f"Evita {main_trigger} fino a miglioramento")
