"""
LangChain Tools for Sciatica Coach Agent

Custom tools that give the agent access to user data and domain logic.
"""
from typing import List, Dict, Any, Optional
from langchain_core.tools import Tool, StructuredTool, BaseTool
from pydantic import BaseModel, Field
from datetime import datetime, timedelta


def create_pain_analyzer_tool(pain_repository, user_id: str) -> Tool:
    """
    Create tool for analyzing pain trends.

    Args:
        pain_repository: Repository for pain assessments
        user_id: User ID to analyze

    Returns:
        LangChain Tool
    """
    def analyze_pain_trend(days: int = 7) -> str:
        """
        Analyze pain trend over last N days.

        Args:
            days: Number of days to analyze (default 7)

        Returns:
            Formatted analysis of pain trends
        """
        try:
            # Get recent pain assessments
            assessments = pain_repository.get_last_n_days(user_id, days)

            if not assessments:
                return f"Nessun dato dolore disponibile negli ultimi {days} giorni."

            # Calculate statistics
            pain_levels = [a.pain_level for a in assessments]
            avg_pain = sum(pain_levels) / len(pain_levels)
            max_pain = max(pain_levels)
            min_pain = min(pain_levels)

            # Trend analysis
            recent_pain = pain_levels[-3:] if len(pain_levels) >= 3 else pain_levels
            older_pain = pain_levels[:3] if len(pain_levels) >= 3 else pain_levels

            recent_avg = sum(recent_pain) / len(recent_pain)
            older_avg = sum(older_pain) / len(older_pain)

            if recent_avg < older_avg - 0.5:
                trend = "in miglioramento ✅"
            elif recent_avg > older_avg + 0.5:
                trend = "in peggioramento ⚠️"
            else:
                trend = "stabile"

            # Common triggers
            all_triggers = []
            for a in assessments:
                all_triggers.extend(a.triggers)

            trigger_counts = {}
            for trigger in all_triggers:
                trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1

            top_triggers = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:3]

            # Common locations
            all_locations = []
            for a in assessments:
                all_locations.extend(a.pain_locations)

            location_counts = {}
            for loc in all_locations:
                location_counts[loc] = location_counts.get(loc, 0) + 1

            top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:3]

            # Format response
            result = f"""
📊 ANALISI DOLORE (Ultimi {days} giorni):

Statistiche:
- Media: {avg_pain:.1f}/10
- Range: {min_pain}-{max_pain}/10
- Trend: {trend}
- Valutazioni: {len(assessments)}

Localizzazioni più comuni:
{chr(10).join([f"- {loc}: {count} volte" for loc, count in top_locations])}

Trigger più frequenti:
{chr(10).join([f"- {trigger}: {count} volte" for trigger, count in top_triggers]) if top_triggers else "- Nessun trigger identificato"}

💡 Insight:
{"Il dolore sta migliorando, continua così!" if trend == "in miglioramento ✅" else ""}
{"Attenzione: dolore in aumento. Considera di ridurre intensità." if trend == "in peggioramento ⚠️" else ""}
{"Dolore stabile. Valuta se è il momento di progredire." if trend == "stabile" and avg_pain < 4 else ""}
"""
            return result.strip()

        except Exception as e:
            return f"Errore nell'analisi dolore: {str(e)}"

    return Tool(
        name="pain_analyzer",
        func=analyze_pain_trend,
        description="Analizza il trend del dolore dell'utente negli ultimi N giorni. Input: numero di giorni (default 7). Output: statistiche dettagliate, trend, trigger comuni."
    )


def create_red_flags_detector_tool() -> Tool:
    """
    Create tool for detecting medical red flags.

    Returns:
        LangChain Tool
    """
    def detect_red_flags(symptoms: str) -> str:
        """
        Check for medical red flags in symptoms.

        Args:
            symptoms: Description of current symptoms

        Returns:
            Red flag analysis and recommendations
        """
        symptoms_lower = symptoms.lower()

        # Critical red flags (emergency)
        critical_flags = []
        if any(word in symptoms_lower for word in ['vescica', 'bladder', 'incontinenza', 'feci']):
            critical_flags.append("🚨 CAUDA EQUINA: Disfunzione vescica/intestino")

        if any(word in symptoms_lower for word in ['sella', 'saddle', 'genitali', 'perineo']):
            critical_flags.append("🚨 CAUDA EQUINA: Anestesia a sella")

        if 'debolezza bilaterale' in symptoms_lower or 'bilateral weakness' in symptoms_lower:
            critical_flags.append("🚨 CAUDA EQUINA: Debolezza bilaterale gambe")

        # Warning signs (non-emergency but concerning)
        warning_signs = []
        if any(word in symptoms_lower for word in ['piede cadente', 'foot drop', 'non riesco sollevare piede']):
            warning_signs.append("⚠️ Possibile deficit neurologico progressivo")

        if any(word in symptoms_lower for word in ['peggiora notte', 'worse at night', 'dolore notturno']):
            warning_signs.append("⚠️ Dolore notturno (possibile patologia seria)")

        if any(word in symptoms_lower for word in ['febbre', 'fever', 'brividi']):
            warning_signs.append("⚠️ Febbre con dolore lombare (possibile infezione)")

        if any(word in symptoms_lower for word in ['perdita peso', 'weight loss', 'dimagrimento']):
            warning_signs.append("⚠️ Perdita peso inspiegata")

        if any(word in symptoms_lower for word in ['trauma', 'caduta', 'incidente']):
            warning_signs.append("⚠️ Trauma recente")

        # Format response
        if critical_flags:
            return f"""
🚨 RED FLAGS CRITICI RILEVATI:

{chr(10).join(critical_flags)}

⚠️ AZIONE IMMEDIATA RICHIESTA:
- INTERROMPI ogni attività fisica
- Vai al PRONTO SOCCORSO entro 24-48 ore
- Questi sintomi possono indicare Sindrome della Cauda Equina
- Richiede valutazione neurochirurgica urgente

NON CONTINUARE con il programma di allenamento.
"""

        elif warning_signs:
            return f"""
⚠️ SEGNALI DI ALLERTA RILEVATI:

{chr(10).join(warning_signs)}

📋 RACCOMANDAZIONI:
- Consulta il medico entro 48-72 ore
- Riduci intensità allenamento del 50%
- Monitora attentamente i sintomi
- Se peggiorano, valutazione medica urgente

Puoi continuare con esercizi gentili, ma con cautela.
"""

        else:
            return """
✅ NESSUN RED FLAG RILEVATO

I sintomi descritti non presentano segnali di allarme immediati.

Puoi continuare con il programma di recupero seguendo le linee guida basate sul livello di dolore.

Monitora comunque i sintomi e segnala qualsiasi cambiamento improvviso.
"""

    return Tool(
        name="red_flags_detector",
        func=detect_red_flags,
        description="Controlla se i sintomi dell'utente presentano red flags medici che richiedono attenzione urgente. Input: descrizione sintomi. Output: analisi red flags e raccomandazioni."
    )


def create_progression_calculator_tool(kpi_repository, user_repository, user_id: str) -> Tool:
    """
    Create tool for calculating if user should progress to next phase.

    Args:
        kpi_repository: Repository for KPIs
        user_repository: Repository for user data
        user_id: User ID

    Returns:
        LangChain Tool
    """
    def calculate_progression() -> str:
        """
        Calculate if user is ready to progress to next phase.

        Returns:
            Progression analysis and recommendation
        """
        try:
            # Get user
            user = user_repository.get_by_id(user_id)
            if not user:
                return "Errore: utente non trovato"

            # Get recent KPIs (last 2 weeks)
            recent_kpis = kpi_repository.get_last_n_weeks(user_id, n=2)

            if not recent_kpis:
                return "Dati insufficienti per valutare progressione. Completa almeno 2 settimane."

            latest_kpi = recent_kpis[-1]

            # Progression criteria
            criteria = {
                "pain_low": latest_kpi.avg_pain_level < 4,
                "compliance_high": latest_kpi.compliance_rate >= 80,
                "pain_trend_improving": len(recent_kpis) >= 2 and recent_kpis[-1].avg_pain_level < recent_kpis[0].avg_pain_level,
                "weeks_sufficient": user.weeks_in_current_phase >= 2
            }

            criteria_met = sum(criteria.values())
            total_criteria = len(criteria)

            # Determine recommendation
            current_phase = user.current_phase
            next_phase_map = {
                "Fase 1: Decompressione": "Fase 2: Stabilizzazione",
                "Fase 2: Stabilizzazione": "Fase 3: Strengthening",
                "Fase 3: Strengthening": "Fase 4: Return to Sport"
            }

            next_phase = next_phase_map.get(current_phase, "Completato")

            result = f"""
📈 VALUTAZIONE PROGRESSIONE

Fase Attuale: {current_phase}
Settimane in fase: {user.weeks_in_current_phase}

Criteri Progressione:
{'✅' if criteria['pain_low'] else '❌'} Dolore medio < 4/10 (attuale: {latest_kpi.avg_pain_level:.1f}/10)
{'✅' if criteria['compliance_high'] else '❌'} Compliance ≥ 80% (attuale: {latest_kpi.compliance_rate:.0f}%)
{'✅' if criteria['pain_trend_improving'] else '❌'} Trend dolore in miglioramento
{'✅' if criteria['weeks_sufficient'] else '❌'} Minimo 2 settimane in fase

Criteri soddisfatti: {criteria_met}/{total_criteria}

"""

            if criteria_met >= 3:
                result += f"""
🎉 RACCOMANDAZIONE: PROGRESSIONE A {next_phase}

Hai soddisfatto {criteria_met}/{total_criteria} criteri.
Sei pronto per avanzare alla prossima fase!

Prossimi step:
1. Conferma con valutazione biometrica
2. Inizia {next_phase} settimana prossima
3. Monitora attentamente prime 2 settimane
"""
            elif criteria_met == 2:
                result += f"""
⏳ RACCOMANDAZIONE: CONTINUA FASE ATTUALE

Hai soddisfatto {criteria_met}/{total_criteria} criteri.
Sei vicino ma non ancora pronto.

Focus:
"""
                if not criteria['pain_low']:
                    result += "- Riduci dolore sotto 4/10 prima di progredire\n"
                if not criteria['compliance_high']:
                    result += "- Aumenta compliance (fai tutti i workout)\n"
                if not criteria['weeks_sufficient']:
                    result += "- Completa almeno 2 settimane in questa fase\n"

                result += f"\nRivaluta tra 1 settimana."

            else:
                result += f"""
❌ RACCOMANDAZIONE: NON PROGREDIRE

Hai soddisfatto solo {criteria_met}/{total_criteria} criteri.
È troppo presto per avanzare.

Priorità:
"""
                if not criteria['pain_low']:
                    result += "- PRIORITÀ 1: Ridurre dolore\n"
                if not criteria['compliance_high']:
                    result += "- PRIORITÀ 2: Aumentare compliance\n"
                if not criteria['pain_trend_improving']:
                    result += "- PRIORITÀ 3: Invertire trend dolore\n"

                result += f"\nRivaluta tra 2 settimane."

            return result.strip()

        except Exception as e:
            return f"Errore nel calcolo progressione: {str(e)}"

    return Tool(
        name="progression_calculator",
        func=calculate_progression,
        description="Calcola se l'utente è pronto per progredire alla fase successiva basandosi su KPI, dolore, compliance. Non richiede input. Output: analisi dettagliata e raccomandazione."
    )


def create_exercise_validator_tool(exercise_library, user_repository, pain_repository, user_id: str) -> StructuredTool:
    """
    Create tool for validating exercise safety.

    Args:
        exercise_library: Exercise library service
        user_repository: Repository for user data
        pain_repository: Repository for pain assessments
        user_id: User ID

    Returns:
        LangChain StructuredTool
    """
    class ExerciseValidatorInput(BaseModel):
        """Input schema for exercise validator."""
        exercise_name: str = Field(description="Nome dell'esercizio da validare")
        current_pain: int = Field(default=5, description="Livello dolore 0-10")

    def validate_exercise(exercise_name: str, current_pain: int = 5) -> str:
        """
        Validate if an exercise is safe for current pain level.

        Args:
            exercise_name: Name of exercise to validate
            current_pain: Current pain level 0-10

        Returns:
            Safety analysis and modifications
        """
        try:
            # Get user
            user = user_repository.get_by_id(user_id)
            if not user:
                return "Errore: utente non trovato"

            # Find exercise
            exercise = exercise_library.get_exercise_by_name(exercise_name)

            if not exercise:
                return f"Esercizio '{exercise_name}' non trovato nel database."

            # Check if exercise is appropriate for current phase
            current_phase = user.current_phase
            if current_phase not in exercise.get('phases', []):
                return f"""
❌ ESERCIZIO NON APPROPRIATO PER FASE ATTUALE

Esercizio: {exercise['name']}
Fase attuale: {current_phase}
Fasi appropriate: {', '.join(exercise.get('phases', []))}

Questo esercizio non è raccomandato per la tua fase di recupero.
Cerca alternative nella tua fase.
"""

            # Get injury risk profile (multi-injury support)
            injury_risk_profile = exercise.get('injury_risk_profile', {})
            modifications = exercise.get('modifications', {})

            # Determine user's injury type from pain locations
            user_injury_types = []
            
            # Get recent pain assessments to find active locations
            pain_locations = []
            try:
                assessments = pain_repository.get_last_n_days(user_id, 7)
                for a in assessments:
                    pain_locations.extend(a.pain_locations)
                pain_locations = list(set(pain_locations)) # deduplicate
            except Exception as e:
                print(f"Error fetching pain locations: {e}")
                pain_locations = []

            for loc in pain_locations:
                loc_lower = loc.lower()
                if any(x in loc_lower for x in ['lombare', 'schiena', 'sciatica', 'nervo']):
                    user_injury_types.append('sciatica')
                if any(x in loc_lower for x in ['inguine', 'pube', 'adduttori']):
                    user_injury_types.append('pubalgia')
                if any(x in loc_lower for x in ['spalla', 'deltoide', 'cuffia']):
                    user_injury_types.append('shoulder_impingement')
                if any(x in loc_lower for x in ['ginocchio', 'rotula', 'patella']):
                    user_injury_types.append('patellar_tendinitis')
                if any(x in loc_lower for x in ['anca', 'femore']):
                    user_injury_types.append('hip_fai')
                if any(x in loc_lower for x in ['caviglia', 'achille']):
                    user_injury_types.append('ankle_sprain')

            # Default to general assessment if no specific injury detected
            if not user_injury_types:
                user_injury_types = ['general']

            # Get pain-based modification key
            if current_pain >= 7:
                pain_key = 'pain_7-10'
            elif current_pain >= 5:
                pain_key = 'pain_5-7'
            else:
                pain_key = 'pain_<5'

            # Collect injury-specific assessments
            injury_assessments = []
            overall_risk = 'low'

            for injury_type in user_injury_types:
                injury_data = injury_risk_profile.get(injury_type, modifications.get(injury_type, {}))
                if injury_data:
                    risk = injury_data.get('therapeutic_value', 'low')
                    # Inverse: low therapeutic = high risk
                    if risk in ['very_low', 'low']:
                        overall_risk = 'high' if overall_risk != 'high' else overall_risk
                    elif risk == 'medium':
                        overall_risk = 'medium' if overall_risk == 'low' else overall_risk

                    mod = injury_data.get('modifications', {}).get(pain_key, '')
                    if mod:
                        injury_assessments.append(f"- {injury_type}: {mod}")

            modification = '\n'.join(injury_assessments) if injury_assessments else 'Nessuna modifica specifica'

            # Safety assessment based on overall risk
            if overall_risk == 'high' and current_pain >= 5:
                safety = "❌ NON SICURO"
                recommendation = "EVITA questo esercizio con dolore ≥5/10"
            elif overall_risk == 'medium' and current_pain >= 7:
                safety = "⚠️ SCONSIGLIATO"
                recommendation = "Sconsigliato con dolore ≥7/10, usa alternative"
            else:
                safety = "✅ SICURO CON MODIFICHE"
                recommendation = "Sicuro se segui le modifiche indicate"

            result = f"""
🏋️ VALIDAZIONE ESERCIZIO: {exercise['name']}

Sicurezza: {safety}
Infortuni rilevati: {', '.join(user_injury_types)}
Rischio complessivo: {overall_risk.upper()}
Categoria: {exercise.get('category', 'N/A')}
Difficoltà: {exercise.get('difficulty', 'N/A')}

Modifiche per dolore {current_pain}/10:
{modification}

Coaching Cues:
{chr(10).join([f"- {cue}" for cue in exercise.get('coaching_cues', [])])}

Controindicazioni:
{chr(10).join([f"- {ci}" for ci in exercise.get('contraindications', [])]) if exercise.get('contraindications') else "Nessuna"}

Raccomandazione: {recommendation}

Progressioni (quando pronto):
{', '.join(exercise.get('progressions', [])) if exercise.get('progressions') else 'Nessuna'}

Regressioni (se troppo difficile):
{', '.join(exercise.get('regressions', [])) if exercise.get('regressions') else 'Nessuna'}
"""

            return result.strip()

        except Exception as e:
            return f"Errore nella validazione esercizio: {str(e)}"

    return StructuredTool.from_function(
        func=validate_exercise,
        name="exercise_validator",
        description="Valida se un esercizio è sicuro per l'utente basandosi su fase attuale, dolore e controindicazioni.",
        args_schema=ExerciseValidatorInput
    )


def create_agent_tools(
    pain_repository,
    kpi_repository,
    user_repository,
    exercise_library,
    user_id: str
) -> List[Tool]:
    """
    Create all tools for the agent.

    Args:
        pain_repository: Pain assessment repository
        kpi_repository: KPI repository
        user_repository: User repository
        exercise_library: Exercise library service
        user_id: User ID

    Returns:
        List of LangChain Tools
    """
    return [
        create_pain_analyzer_tool(pain_repository, user_id),
        create_red_flags_detector_tool(),
        create_progression_calculator_tool(kpi_repository, user_repository, user_id),
        create_exercise_validator_tool(exercise_library, user_repository, pain_repository, user_id)
    ]
