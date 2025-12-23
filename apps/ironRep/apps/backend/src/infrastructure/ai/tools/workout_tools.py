"""
Workout and Progression Tools for LangChain
"""
from langchain_core.tools import Tool
from typing import List

from src.domain.services.progression_engine import ProgressionEngine
from src.domain.repositories.kpi_repository import IKPIRepository
from src.domain.entities.workout_session import WorkoutPhase


def create_progression_calculator_tool(kpi_repository: IKPIRepository) -> Tool:
    """
    Create progression calculator tool.

    Determines if user should progress to next phase.
    """
    engine = ProgressionEngine()

    def calculate_progression(user_id: str) -> str:
        """
        Calculate if user should progress to next rehabilitation phase.

        Returns progression decision with rationale.
        """
        try:
            # Get recent KPIs (last 4 weeks)
            recent_kpis = kpi_repository.get_last_n_weeks(user_id, n=4)

            if not recent_kpis:
                return "Dati insufficienti per valutare progressione. Necessari almeno 2 settimane."

            # Get current phase (simplified - would come from user profile)
            current_phase = WorkoutPhase.PHASE_1_DECOMPRESSION
            weeks_in_phase = len(recent_kpis)

            # Evaluate progression
            decision = engine.evaluate_progression(
                recent_kpis,
                current_phase,
                weeks_in_phase
            )

            # Format response
            if decision["action"] == "progress":
                response = f"""
✅ PRONTO PER PROGRESSIONE!

Fase successiva: {decision['next_phase']}
Aggiustamento intensità: {decision['intensity_adjustment']}
Nuovi esercizi raccomandati:
{chr(10).join([f'- {ex}' for ex in decision.get('new_exercises', [])])}

{decision.get('message', '')}
                """.strip()

            elif decision["action"] == "maintain":
                response = f"""
⏸️ MANTIENI FASE ATTUALE

Motivo: {decision.get('reason', 'Criteri non ancora soddisfatti')}
Focus su: {', '.join(decision.get('focus_areas', []))}

Continua il lavoro attuale prima di progredire.
                """.strip()

            else:
                response = f"""
⚠️ MODIFICA NECESSARIA

Motivo: {decision.get('reason', 'Alcuni criteri non soddisfatti')}
Aree focus: {', '.join(decision.get('focus_areas', []))}

Raccomandazioni:
{chr(10).join([f'- {rec}' for rec in decision.get('recommendations', [])])}
                """.strip()

            return response

        except Exception as e:
            return f"Errore nel calcolo progressione: {str(e)}"

    return Tool(
        name="progression_calculator",
        func=calculate_progression,
        description="""
Calcola se l'utente è pronto per progredire alla prossima fase di riabilitazione
basandosi sui KPI delle ultime settimane (dolore, compliance, funzionalità).
Input: user_id (str)
Usa questo tool per decidere se aumentare intensità o passare fase successiva.
        """.strip()
    )


def create_exercise_validator_tool(exercise_library) -> Tool:
    """
    Create exercise contraindications validator tool.
    """
    def validate_exercises(pain_locations_str: str, phase: str = "Fase 1: Decompressione") -> str:
        """
        Validate which exercises are safe given pain locations.

        Returns list of safe and contraindicated exercises.
        """
        try:
            # Parse pain locations
            pain_locations = [loc.strip() for loc in pain_locations_str.split(",")]

            # Get safe exercises for phase
            safe_exercises = exercise_library.get_safe_exercises(
                pain_locations,
                phase
            )

            # Get all exercises for phase
            all_exercises = exercise_library.get_exercises_for_phase(phase)

            # Find contraindicated
            contraindicated = [
                ex for ex in all_exercises
                if ex not in safe_exercises
            ]

            # Format response
            response = f"""
VALIDAZIONE ESERCIZI per {phase}
Localizzazioni dolore: {', '.join(pain_locations)}

✅ ESERCIZI SICURI ({len(safe_exercises)}):
{chr(10).join([f'- {ex["name"]}' for ex in safe_exercises[:10]])}

❌ ESERCIZI DA EVITARE ({len(contraindicated)}):
{chr(10).join([f'- {ex["name"]}: {", ".join(ex.get("contraindications", []))}' for ex in contraindicated[:5]])}
            """.strip()

            return response

        except Exception as e:
            return f"Errore nella validazione esercizi: {str(e)}"

    return Tool(
        name="exercise_validator",
        func=validate_exercises,
        description="""
Valida quali esercizi sono sicuri data la localizzazione del dolore dell'utente.
Filtra esercizi con controindicazioni per le aree dolorose.
Input: pain_locations_str (str) - Localizzazioni separate da virgola, phase (str)
Usa questo tool prima di prescrivere esercizi per garantire sicurezza.
        """.strip()
    )
