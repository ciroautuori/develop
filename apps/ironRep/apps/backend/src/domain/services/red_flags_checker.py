"""
Red Flags Checker Domain Service

Identifies medical red flags that require immediate professional attention.
"""
from typing import List, Dict
import re


class RedFlagsChecker:
    """
    Domain service for detecting medical red flags.

    Red flags are symptoms that indicate potentially serious conditions
    requiring immediate medical evaluation.
    """

    # Critical red flags for sciatica/lower back pain
    RED_FLAGS = {
        "cauda_equina": {
            "keywords": [
                "incontinenza", "perdita controllo vescica", "difficoltà urinare",
                "perdita controllo intestino", "anestesia sella", "formicolio perineo"
            ],
            "urgency": "immediate",
            "message": "⚠️ URGENTE: Possibile Sindrome Cauda Equina - Consultare IMMEDIATAMENTE PS"
        },
        "progressive_weakness": {
            "keywords": [
                "debolezza progressiva", "non riesco camminare", "piede cadente",
                "perdita forza gamba", "difficoltà salire scale crescente"
            ],
            "urgency": "high",
            "message": "⚠️ Debolezza neurologica progressiva - Consultare medico 24h"
        },
        "night_pain": {
            "keywords": [
                "dolore notturno intenso", "sveglia di notte dolore",
                "dolore costante notte", "non riesco dormire dolore"
            ],
            "urgency": "medium",
            "message": "⚠️ Dolore notturno persistente - Consultare medico entro 48h"
        },
        "systemic_symptoms": {
            "keywords": [
                "febbre", "perdita peso inspiegabile", "sudorazione notturna",
                "malessere generale", "stanchezza estrema"
            ],
            "urgency": "high",
            "message": "⚠️ Sintomi sistemici - Consultare medico 24-48h"
        },
        "trauma": {
            "keywords": [
                "caduta", "trauma diretto", "incidente", "colpo schiena"
            ],
            "urgency": "medium",
            "message": "⚠️ Dolore post-trauma - Valutare imaging diagnostico"
        },
        "bilateral_symptoms": {
            "keywords": [
                "dolore entrambe gambe", "formicolio bilaterale",
                "debolezza bilaterale", "sintomi due gambe"
            ],
            "urgency": "high",
            "message": "⚠️ Sintomi bilaterali - Consultare medico urgentemente"
        }
    }

    def check_symptoms(self, symptoms_description: str,
                      symptoms_list: List[str]) -> Dict:
        """
        Check for red flags in symptom description.

        Args:
            symptoms_description: Free text description of symptoms
            symptoms_list: List of specific symptoms

        Returns:
            dict with red flags detected and recommendations
        """
        detected_flags = []
        max_urgency = "none"

        # Combine all text for checking
        all_text = (symptoms_description + " " + " ".join(symptoms_list)).lower()

        # Check each red flag category
        for flag_name, flag_data in self.RED_FLAGS.items():
            if self._contains_keywords(all_text, flag_data["keywords"]):
                detected_flags.append({
                    "flag": flag_name,
                    "urgency": flag_data["urgency"],
                    "message": flag_data["message"]
                })

                # Track highest urgency
                if self._urgency_level(flag_data["urgency"]) > self._urgency_level(max_urgency):
                    max_urgency = flag_data["urgency"]

        return {
            "red_flags_detected": len(detected_flags) > 0,
            "flags": detected_flags,
            "max_urgency": max_urgency,
            "immediate_action_required": max_urgency == "immediate",
            "recommendation": self._generate_recommendation(max_urgency)
        }

    def check_pain_pattern(self, pain_level: int, duration_days: int) -> Dict:
        """
        Check if pain pattern is concerning.

        Args:
            pain_level: Current pain level (0-10)
            duration_days: Days since onset

        Returns:
            dict with assessment and recommendations
        """
        concerns = []

        # Severe pain for extended period
        if pain_level >= 8 and duration_days > 7:
            concerns.append({
                "concern": "severe_persistent_pain",
                "message": "Dolore severo persistente da oltre 7 giorni",
                "action": "Consultare medico per rivalutazione"
            })

        # Moderate pain for very long period
        if pain_level >= 5 and duration_days > 30:
            concerns.append({
                "concern": "chronic_pain",
                "message": "Dolore da oltre 30 giorni senza miglioramento",
                "action": "Valutare imaging diagnostico e consulto specialistico"
            })

        return {
            "concerns_detected": len(concerns) > 0,
            "concerns": concerns
        }

    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the keywords."""
        for keyword in keywords:
            # Simple word boundary matching
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text):
                return True
        return False

    def _urgency_level(self, urgency: str) -> int:
        """Convert urgency to numeric level for comparison."""
        levels = {
            "none": 0,
            "low": 1,
            "medium": 2,
            "high": 3,
            "immediate": 4
        }
        return levels.get(urgency, 0)

    def _generate_recommendation(self, urgency: str) -> str:
        """Generate recommendation based on urgency level."""
        recommendations = {
            "immediate": "🚨 CONSULTARE PRONTO SOCCORSO IMMEDIATAMENTE",
            "high": "⚠️ Consultare medico entro 24 ore",
            "medium": "⚠️ Consultare medico entro 48-72 ore",
            "low": "Monitorare sintomi, consulto se peggioramento",
            "none": "✅ Nessun red flag identificato, procedere con programma"
        }
        return recommendations.get(urgency, "Consultare medico se dubbi")
