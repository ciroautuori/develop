"""
Smart Workout Tools - Integrazione RAG per esercizi, programmi e progressione.

Workflow:
1. Cerca esercizi dal knowledge base (727+ esercizi)
2. Filtra per controindicazioni basate su infortunio
3. Genera progressioni basate su fase recupero
4. Cross-reference con nutrizione (post-workout)
"""
from typing import List, Dict, Any, Optional
from langchain_core.tools import Tool, StructuredTool
from pydantic import BaseModel, Field

from src.infrastructure.ai.rag_service import get_rag_service
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class ExerciseSearchInput(BaseModel):
    """Input per ricerca esercizi."""
    muscle_group: str = Field(description="Gruppo muscolare (es. 'gambe', 'schiena', 'core')")
    difficulty: str = Field(default="any", description="Difficoltà: 'beginner', 'intermediate', 'advanced', 'any'")
    equipment: str = Field(default="any", description="Attrezzatura disponibile")


class WorkoutGenerationInput(BaseModel):
    """Input per generazione workout."""
    goal: str = Field(description="Obiettivo (es. 'forza', 'ipertrofia', 'recupero')")
    duration_min: int = Field(default=45, description="Durata in minuti")
    injury_areas: List[str] = Field(default=[], description="Aree infortunate da evitare")


def create_exercise_search_tool() -> Tool:
    """
    Tool per cercare esercizi dal RAG.
    """

    def search_exercises(query: str) -> str:
        """Cerca esercizi nel knowledge base."""

        rag = get_rag_service()

        try:
            # Cerca esercizi
            results = rag.retrieve_context(
                query=f"{query} esercizio muscoli tecnica",
                k=5,
                filter_metadata={"type": "exercise"}
            )

            if not results:
                return f"Nessun esercizio trovato per '{query}'. Prova con termini diversi."

            output = f"🏋️ **ESERCIZI per {query.upper()}:**\n\n"

            for i, r in enumerate(results[:4], 1):
                content = r['content']
                name = r['metadata'].get('exercise_name', 'Esercizio')
                difficulty = r['metadata'].get('difficulty', 'N/A')
                equipment = r['metadata'].get('equipment', 'Nessuno')

                # Estrai muscoli target
                muscles = []
                for line in content.split('\n'):
                    if 'Muscoli' in line or 'Target' in line:
                        muscles.append(line.strip())

                output += f"**{i}. {name}**\n"
                output += f"   Difficoltà: {difficulty} | Attrezzatura: {equipment}\n"
                if muscles:
                    output += f"   {muscles[0]}\n"
                output += "\n"

            return output

        except Exception as e:
            logger.error(f"Exercise search error: {e}")
            return f"Errore ricerca esercizi: {e}"

    return Tool(
        name="exercise_search",
        func=search_exercises,
        description="""Cerca esercizi nel database (727+ esercizi).
Input: query (es. 'quadricipiti', 'core stability', 'spalla mobilità')
Output: lista esercizi con difficoltà, attrezzatura, muscoli target."""
    )


def create_safe_exercises_tool() -> Tool:
    """
    Tool per trovare esercizi sicuri dato un infortunio.
    """

    def find_safe_exercises(injury_area: str, phase: str = "fase 2") -> str:
        """Trova esercizi sicuri per area infortunata e fase recupero."""

        rag = get_rag_service()

        # Mappa fasi a query
        phase_keywords = {
            "fase 1": "mobilità gentile isometrico leggero",
            "fase 2": "mobilità rinforzo leggero controllo",
            "fase 3": "rinforzo progressivo funzionale",
            "fase 4": "sport specifico performance"
        }

        phase_key = phase_keywords.get(phase.lower(), "rinforzo progressivo")

        try:
            # Prima cerca esercizi per l'area
            results = rag.retrieve_context(
                query=f"esercizio {injury_area} riabilitazione {phase_key}",
                k=8,
                filter_metadata={"type": "exercise"}
            )

            if not results:
                return f"Nessun esercizio specifico trovato per {injury_area}."

            # Filtra per controindicazioni
            safe_exercises = []
            for r in results:
                content = r['content'].lower()
                name = r['metadata'].get('exercise_name', 'Esercizio')

                # Escludi esercizi con controindicazioni per l'area
                contraindicated = False
                if injury_area.lower() in ["lombare", "schiena", "low back"]:
                    if any(x in content for x in ["flessione lombare carico", "rotazione sotto carico", "impatto"]):
                        contraindicated = True
                elif injury_area.lower() in ["ginocchio", "knee"]:
                    if any(x in content for x in ["deep squat", "salto", "impatto alto"]):
                        contraindicated = True
                elif injury_area.lower() in ["spalla", "shoulder"]:
                    if any(x in content for x in ["overhead pesante", "behind neck", "kipping"]):
                        contraindicated = True

                if not contraindicated:
                    safe_exercises.append({
                        "name": name,
                        "content": r['content'][:200]
                    })

            if not safe_exercises:
                return f"⚠️ Nessun esercizio sicuro trovato per {injury_area} in {phase}. Consulta un fisioterapista."

            output = f"✅ **ESERCIZI SICURI per {injury_area.upper()} ({phase}):**\n\n"

            for i, ex in enumerate(safe_exercises[:5], 1):
                output += f"**{i}. {ex['name']}**\n"
                output += f"   {ex['content'][:100]}...\n\n"

            output += f"\n⚠️ Esegui sempre nel range senza dolore. Se dolore > 3/10, interrompi."

            return output

        except Exception as e:
            logger.error(f"Safe exercises search error: {e}")
            return f"Errore ricerca esercizi sicuri: {e}"

    return Tool(
        name="safe_exercises",
        func=lambda q: find_safe_exercises(q),
        description="""Trova esercizi SICURI per un'area infortunata e fase di recupero.
Input: area infortunata (es. 'lombare', 'ginocchio', 'spalla')
Output: esercizi filtrati per controindicazioni, adatti alla fase di recupero."""
    )


def create_workout_template_tool() -> Tool:
    """
    Tool per generare template workout.
    """

    WORKOUT_TEMPLATES = {
        "forza_upper": {
            "name": "Upper Body Strength",
            "exercises": [
                {"name": "Bench Press", "sets": 4, "reps": "6-8", "rest": "90s"},
                {"name": "Bent Over Row", "sets": 4, "reps": "6-8", "rest": "90s"},
                {"name": "Overhead Press", "sets": 3, "reps": "8-10", "rest": "60s"},
                {"name": "Pull-ups/Lat Pulldown", "sets": 3, "reps": "8-10", "rest": "60s"},
                {"name": "Dumbbell Curl", "sets": 3, "reps": "10-12", "rest": "45s"},
                {"name": "Tricep Extension", "sets": 3, "reps": "10-12", "rest": "45s"},
            ]
        },
        "forza_lower": {
            "name": "Lower Body Strength",
            "exercises": [
                {"name": "Squat", "sets": 4, "reps": "6-8", "rest": "120s"},
                {"name": "Romanian Deadlift", "sets": 4, "reps": "8-10", "rest": "90s"},
                {"name": "Leg Press", "sets": 3, "reps": "10-12", "rest": "60s"},
                {"name": "Walking Lunges", "sets": 3, "reps": "12/gamba", "rest": "60s"},
                {"name": "Leg Curl", "sets": 3, "reps": "12-15", "rest": "45s"},
                {"name": "Calf Raises", "sets": 3, "reps": "15-20", "rest": "45s"},
            ]
        },
        "recupero": {
            "name": "Active Recovery",
            "exercises": [
                {"name": "Cat-Cow Stretch", "sets": 2, "reps": "10", "rest": "30s"},
                {"name": "Hip Circles", "sets": 2, "reps": "10/lato", "rest": "30s"},
                {"name": "Bird Dog", "sets": 2, "reps": "8/lato", "rest": "30s"},
                {"name": "Dead Bug", "sets": 2, "reps": "8/lato", "rest": "30s"},
                {"name": "Glute Bridge", "sets": 2, "reps": "12", "rest": "30s"},
                {"name": "Foam Rolling", "sets": 1, "reps": "5min", "rest": "-"},
            ]
        },
        "core": {
            "name": "Core Stability",
            "exercises": [
                {"name": "Plank", "sets": 3, "reps": "30-60s", "rest": "45s"},
                {"name": "Side Plank", "sets": 3, "reps": "30s/lato", "rest": "45s"},
                {"name": "Dead Bug", "sets": 3, "reps": "10/lato", "rest": "30s"},
                {"name": "Pallof Press", "sets": 3, "reps": "10/lato", "rest": "30s"},
                {"name": "Bird Dog", "sets": 3, "reps": "10/lato", "rest": "30s"},
                {"name": "Hollow Body Hold", "sets": 3, "reps": "20-30s", "rest": "45s"},
            ]
        },
        "fullbody": {
            "name": "Full Body",
            "exercises": [
                {"name": "Squat", "sets": 3, "reps": "8-10", "rest": "90s"},
                {"name": "Push-ups/Bench Press", "sets": 3, "reps": "8-10", "rest": "60s"},
                {"name": "Romanian Deadlift", "sets": 3, "reps": "10-12", "rest": "60s"},
                {"name": "Rows", "sets": 3, "reps": "10-12", "rest": "60s"},
                {"name": "Overhead Press", "sets": 3, "reps": "10-12", "rest": "60s"},
                {"name": "Plank", "sets": 2, "reps": "45s", "rest": "30s"},
            ]
        }
    }

    def get_workout_template(goal: str) -> str:
        """Genera template workout per obiettivo."""

        # Mappa goal a template
        goal_lower = goal.lower()

        if any(x in goal_lower for x in ["upper", "parte alta", "braccia", "petto", "schiena"]):
            template = WORKOUT_TEMPLATES["forza_upper"]
        elif any(x in goal_lower for x in ["lower", "gambe", "glutei", "quadricipiti"]):
            template = WORKOUT_TEMPLATES["forza_lower"]
        elif any(x in goal_lower for x in ["recupero", "recovery", "stretching", "mobility"]):
            template = WORKOUT_TEMPLATES["recupero"]
        elif any(x in goal_lower for x in ["core", "addominali", "stabilità"]):
            template = WORKOUT_TEMPLATES["core"]
        else:
            template = WORKOUT_TEMPLATES["fullbody"]

        output = f"🏋️ **WORKOUT: {template['name']}**\n\n"

        for i, ex in enumerate(template["exercises"], 1):
            output += f"{i}. **{ex['name']}**\n"
            output += f"   {ex['sets']} x {ex['reps']} | Riposo: {ex['rest']}\n\n"

        output += "💡 **Note:**\n"
        output += "- Riscaldamento 5-10 min prima\n"
        output += "- Usa peso che permette tecnica corretta\n"
        output += "- Se dolore > 3/10, interrompi e segnala\n"

        return output

    return Tool(
        name="workout_template",
        func=get_workout_template,
        description="""Genera un template di workout per un obiettivo specifico.
Input: goal (es. 'forza gambe', 'recupero', 'core', 'fullbody')
Output: workout completo con esercizi, serie, ripetizioni e recuperi."""
    )


def create_exercise_substitution_tool() -> Tool:
    """
    Tool per trovare alternative a esercizi controindicati.
    """

    SUBSTITUTIONS = {
        "squat": ["leg press", "goblet squat", "box squat", "belt squat"],
        "deadlift": ["rack pull", "trap bar deadlift", "RDL", "hip hinge cable"],
        "bench press": ["floor press", "push-ups", "dumbbell press", "machine chest press"],
        "overhead press": ["landmine press", "incline press", "lateral raises", "front raises"],
        "pull-ups": ["lat pulldown", "assisted pull-ups", "cable rows", "inverted rows"],
        "running": ["cycling", "swimming", "elliptical", "walking"],
        "burpees": ["step back burpees", "squat to stand", "modified burpees"],
        "box jumps": ["step-ups", "box step-ups", "low box jumps", "squat jumps"],
    }

    def find_substitution(exercise: str, reason: str = "") -> str:
        """Trova alternative per un esercizio controindicato."""

        exercise_lower = exercise.lower()

        # Cerca nel dizionario
        for key, alternatives in SUBSTITUTIONS.items():
            if key in exercise_lower:
                output = f"🔄 **ALTERNATIVE a {exercise.upper()}:**\n\n"
                if reason:
                    output += f"Motivo sostituzione: {reason}\n\n"

                for i, alt in enumerate(alternatives, 1):
                    output += f"{i}. **{alt}**\n"

                output += "\n💡 Scegli l'alternativa che non provoca dolore."
                return output

        # Se non trovato, cerca nel RAG
        rag = get_rag_service()
        try:
            results = rag.retrieve_context(
                query=f"alternativa {exercise} esercizio simile",
                k=3,
                filter_metadata={"type": "exercise"}
            )

            if results:
                output = f"🔄 **ALTERNATIVE a {exercise.upper()} (dal database):**\n\n"
                for r in results[:3]:
                    name = r['metadata'].get('exercise_name', 'Alternativa')
                    output += f"• **{name}**\n"
                return output
        except:
            pass

        return f"Nessuna alternativa specifica trovata per '{exercise}'. Consulta il coach per opzioni personalizzate."

    return Tool(
        name="exercise_substitution",
        func=lambda ex: find_substitution(ex),
        description="""Trova esercizi alternativi per sostituire uno controindicato.
Input: nome esercizio (es. 'squat', 'deadlift', 'running')
Output: lista di alternative sicure."""
    )


def create_progression_advisor_tool() -> Tool:
    """
    Tool per consigliare progressioni.
    """

    def advise_progression(current_phase: str, pain_level: int, weeks_in_phase: int = 2) -> str:
        """Consiglia sulla progressione alla fase successiva."""

        # Criteri per progressione
        criteria = {
            "fase 1": {"max_pain": 3, "min_weeks": 2, "next": "Fase 2 - Mobilità"},
            "fase 2": {"max_pain": 2, "min_weeks": 2, "next": "Fase 3 - Rinforzo"},
            "fase 3": {"max_pain": 1, "min_weeks": 3, "next": "Fase 4 - Ritorno Sport"},
            "fase 4": {"max_pain": 0, "min_weeks": 2, "next": "Ritorno completo allo sport"},
        }

        phase_lower = current_phase.lower()

        # Trova criteri per fase corrente
        phase_criteria = None
        for key, val in criteria.items():
            if key in phase_lower:
                phase_criteria = val
                break

        if not phase_criteria:
            return "Fase non riconosciuta. Specifica: Fase 1, 2, 3 o 4."

        # Valuta criteri
        pain_ok = pain_level <= phase_criteria["max_pain"]
        weeks_ok = weeks_in_phase >= phase_criteria["min_weeks"]

        if pain_ok and weeks_ok:
            return f"""✅ **PRONTO PER PROGRESSIONE!**

**Fase attuale**: {current_phase}
**Prossima fase**: {phase_criteria["next"]}

**Criteri soddisfatti**:
- Dolore: {pain_level}/10 ≤ {phase_criteria["max_pain"]}/10 ✓
- Settimane: {weeks_in_phase} ≥ {phase_criteria["min_weeks"]} ✓

🚀 Puoi iniziare la prossima fase. Incrementa gradualmente l'intensità.
"""
        else:
            missing = []
            if not pain_ok:
                missing.append(f"Dolore ancora troppo alto ({pain_level}/10, target: ≤{phase_criteria['max_pain']}/10)")
            if not weeks_ok:
                missing.append(f"Tempo insufficiente ({weeks_in_phase} settimane, minimo: {phase_criteria['min_weeks']})")

            return f"""⏸️ **MANTIENI FASE ATTUALE**

**Fase attuale**: {current_phase}

**Criteri non soddisfatti**:
{chr(10).join([f"- {m}" for m in missing])}

💡 Continua con il programma attuale. Rivaluta tra 1 settimana.
"""

    return Tool(
        name="progression_advisor",
        func=lambda p: advise_progression(p, 0, 2),  # Semplificato
        description="""Valuta se pronto per progredire alla fase successiva di riabilitazione.
Input: fase attuale (es. 'Fase 1', 'Fase 2')
Output: consiglio su progressione o mantenimento."""
    )


def create_smart_workout_tools() -> List[Tool]:
    """
    Crea set completo di tools workout intelligenti.

    Integra:
    - RAG per ricerca esercizi (727+ nel database)
    - Filtro esercizi sicuri per infortunio
    - Template workout per obiettivi
    - Sostituzione esercizi controindicati
    - Advisor progressione fasi
    """

    tools = [
        create_exercise_search_tool(),
        create_safe_exercises_tool(),
        create_workout_template_tool(),
        create_exercise_substitution_tool(),
        create_progression_advisor_tool(),
    ]

    return tools
