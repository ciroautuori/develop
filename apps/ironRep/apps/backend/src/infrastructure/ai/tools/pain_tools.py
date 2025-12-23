"""
Pain Analysis Tool for LangChain

Wraps PainAnalyzer domain service as a LangChain tool for AI agents.
"""
from langchain_core.tools import Tool
from typing import List

from src.domain.services.pain_analyzer import PainAnalyzer
from src.domain.repositories.pain_repository import IPainRepository


def create_pain_analysis_tool(pain_repository: IPainRepository) -> Tool:
    """
    Create pain analysis tool for LangChain agent.

    Args:
        pain_repository: Repository to fetch pain data

    Returns:
        LangChain Tool instance
    """
    analyzer = PainAnalyzer()

    def analyze_pain_trend(user_id: str, days: int = 7) -> str:
        """
        Analyze pain trend over last N days.

        Returns trend analysis with recommendations.
        """
        try:
            # Fetch pain history
            assessments = pain_repository.get_last_n_days(user_id, days)

            if not assessments:
                return "Nessun dato dolore disponibile per analisi."

            # Analyze trend
            trend_analysis = analyzer.analyze_trend(assessments)

            # Identify triggers
            trigger_analysis = analyzer.identify_triggers(assessments)

            # Find best time
            best_time = analyzer.find_best_time_of_day(assessments)

            # Format response
            response = f"""
📊 ANALISI DOLORE (ultimi {days} giorni):

Trend: {trend_analysis['trend'].upper()}
Dolore medio: {trend_analysis['avg_pain']}/10
Variabilità: {trend_analysis['variability']}
Range: {trend_analysis['min_pain']}-{trend_analysis['max_pain']}

🎯 Trigger principali: {', '.join(trigger_analysis['main_triggers']) if trigger_analysis['main_triggers'] else 'Nessuno identificato'}

⏰ Momento migliore: {best_time}

💡 Raccomandazione: {trigger_analysis['recommendation']}
            """.strip()

            return response

        except Exception as e:
            return f"Errore nell'analisi: {str(e)}"

    return Tool(
        name="pain_analyzer",
        func=analyze_pain_trend,
        description="""
Analizza il pattern del dolore dell'utente negli ultimi N giorni.
Restituisce trend, trigger ricorrenti, variabilità e raccomandazioni.
Input: user_id (str), days (int, default 7)
Usa questo tool quando devi capire l'andamento del dolore nel tempo.
        """.strip()
    )


def create_red_flags_detection_tool() -> Tool:
    """
    Create red flags detection tool.

    Checks for medical emergency symptoms.
    """
    from src.domain.services.red_flags_checker import RedFlagsChecker

    checker = RedFlagsChecker()

    def check_red_flags(symptoms_description: str) -> str:
        """
        Check for medical red flags in symptoms.

        Returns urgency level and recommendations.
        """
        try:
            result = checker.check_symptoms(symptoms_description, [])

            if result["red_flags_detected"]:
                flags_text = "\n".join([
                    f"- {flag['flag']}: {flag['message']}"
                    for flag in result["flags"]
                ])

                response = f"""
⚠️ RED FLAGS IDENTIFICATI:

{flags_text}

Urgenza: {result['max_urgency'].upper()}
Azione immediata richiesta: {'SÌ' if result['immediate_action_required'] else 'NO'}

{result['recommendation']}
                """.strip()
            else:
                response = "✅ Nessun red flag identificato. Sicuro procedere con il programma."

            return response

        except Exception as e:
            return f"Errore nel controllo red flags: {str(e)}"

    return Tool(
        name="red_flags_detector",
        func=check_red_flags,
        description="""
Controlla se i sintomi descritti contengono red flags medici che richiedono
attenzione immediata (es. sindrome cauda equina, debolezza progressiva).
Input: symptoms_description (str) - Descrizione dettagliata sintomi
USA SEMPRE questo tool quando l'utente descrive sintomi nuovi o preoccupanti.
        """.strip()
    )
