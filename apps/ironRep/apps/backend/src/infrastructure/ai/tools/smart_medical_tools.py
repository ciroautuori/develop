"""
Smart Medical Tools - Integrazione RAG per diagnosi, protocolli e linee guida.

Workflow:
1. Cerca protocolli riabilitazione dal knowledge base
2. Identifica red flags basati su linee guida mediche
3. Fornisce timeline recupero evidence-based
4. Cross-reference sintomi con diagnosi
"""
from typing import List, Dict, Any
from datetime import date, timedelta
from langchain_core.tools import Tool, StructuredTool
from pydantic import BaseModel, Field

from src.infrastructure.ai.rag_service import get_rag_service
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class PainAnalysisInput(BaseModel):
    """Input per analisi dolore."""
    pain_level: int = Field(description="Livello dolore 0-10")
    location: str = Field(description="Localizzazione (es. 'lombare', 'ginocchio')")
    duration_days: int = Field(default=7, description="Durata in giorni")


class RedFlagsInput(BaseModel):
    """Input per controllo red flags."""
    symptoms: str = Field(description="Sintomi attuali separati da virgola")
    pain_level: int = Field(description="Livello dolore 0-10")
    night_pain: bool = Field(default=False, description="Dolore notturno")


def create_rehab_protocol_tool() -> Tool:
    """
    Tool per cercare protocolli riabilitazione dal RAG.
    """

    def search_rehab_protocol(injury_type: str) -> str:
        """Cerca protocollo riabilitazione per tipo infortunio."""

        rag = get_rag_service()

        try:
            # Cerca protocolli specifici
            results = rag.retrieve_context(
                query=f"protocollo riabilitazione {injury_type} fasi esercizi timeline",
                k=3,
                filter_metadata={"type": "rehab_protocol"}
            )

            # Se non trova protocolli specifici, cerca nelle linee guida mediche
            if not results:
                results = rag.retrieve_context(
                    query=f"{injury_type} recupero trattamento riabilitazione",
                    k=3,
                    filter_metadata={"category": "medical"}
                )

            if not results:
                return f"""
📋 PROTOCOLLO STANDARD per {injury_type.upper()}:

**FASE 1 - Protezione (1-2 settimane)**
- Riposo relativo, evitare movimenti dolorosi
- Ghiaccio 15-20 min ogni 2-3 ore
- Mobilità gentile nel range senza dolore

**FASE 2 - Mobilità (3-4 settimane)**
- ROM progressivo
- Esercizi isometrici leggeri
- Iniziare rinforzo muscolare base

**FASE 3 - Rinforzo (5-8 settimane)**
- Esercizi di forza progressivi
- Controllo motorio
- Propriocezione

**FASE 4 - Ritorno Sport (9+ settimane)**
- Esercizi sport-specifici
- Test funzionali prima del ritorno completo

⚠️ Consulta un fisioterapista per un programma personalizzato.
"""

            output = f"📋 **PROTOCOLLI RIABILITAZIONE per {injury_type.upper()}:**\n\n"

            for i, r in enumerate(results, 1):
                content = r['content']
                source = r['metadata'].get('source', 'KB')

                # Estrai fasi e timeline
                output += f"**Protocollo {i}** (Fonte: {source})\n"
                output += f"{content[:600]}...\n\n"

            return output

        except Exception as e:
            logger.error(f"Rehab protocol search error: {e}")
            return f"Errore ricerca protocollo: {e}"

    return Tool(
        name="rehab_protocol",
        func=search_rehab_protocol,
        description="""Cerca protocolli riabilitazione per un tipo di infortunio.
Input: tipo infortunio (es. 'lombalgia', 'distorsione caviglia', 'tendinite spalla')
Output: fasi riabilitazione, timeline, esercizi consigliati."""
    )


def create_red_flags_tool() -> Tool:
    """
    Tool per identificare red flags medici.
    """

    # Red flags predefiniti (evidence-based)
    RED_FLAGS = {
        "neurologici": {
            "sintomi": ["formicolio", "intorpidimento", "debolezza", "perdita sensibilità", "incontinenza"],
            "azione": "VISITA MEDICA URGENTE - possibile coinvolgimento nervoso"
        },
        "infezione": {
            "sintomi": ["febbre", "rossore", "gonfiore caldo", "brividi", "sudorazione notturna"],
            "azione": "VISITA MEDICA URGENTE - possibile infezione"
        },
        "trauma": {
            "sintomi": ["trauma recente", "caduta", "incidente", "colpo diretto", "frattura sospetta"],
            "azione": "VISITA MEDICA - escludere frattura o lesione grave"
        },
        "sistemici": {
            "sintomi": ["perdita peso", "stanchezza estrema", "dolore costante", "peggioramento notturno"],
            "azione": "VISITA MEDICA - escludere patologie sistemiche"
        },
        "cardiovascolari": {
            "sintomi": ["dolore toracico", "difficoltà respiratorie", "palpitazioni", "gonfiore gambe"],
            "azione": "VISITA MEDICA URGENTE - escludere patologie cardiovascolari"
        }
    }

    def check_red_flags(symptoms: str, pain_level: int = 0, night_pain: bool = False) -> str:
        """Controlla presenza red flags nei sintomi."""

        symptoms_lower = symptoms.lower()
        detected_flags = []

        # Controlla ogni categoria di red flags
        for category, data in RED_FLAGS.items():
            for sintomo in data["sintomi"]:
                if sintomo in symptoms_lower:
                    detected_flags.append({
                        "categoria": category,
                        "sintomo": sintomo,
                        "azione": data["azione"]
                    })

        # Red flags aggiuntivi basati su dolore
        if pain_level >= 9:
            detected_flags.append({
                "categoria": "dolore severo",
                "sintomo": f"Dolore {pain_level}/10",
                "azione": "VALUTAZIONE MEDICA - dolore molto elevato"
            })

        if night_pain:
            detected_flags.append({
                "categoria": "dolore notturno",
                "sintomo": "Dolore che sveglia di notte",
                "azione": "VALUTAZIONE MEDICA - escludere cause organiche"
            })

        # Formatta output
        if detected_flags:
            output = "🚨 **RED FLAGS RILEVATI:**\n\n"
            for flag in detected_flags:
                output += f"⚠️ **{flag['categoria'].upper()}**: {flag['sintomo']}\n"
                output += f"   → {flag['azione']}\n\n"

            output += "**RACCOMANDAZIONE**: Consulta un medico prima di continuare qualsiasi attività.\n"
            return output
        else:
            return """✅ **NESSUN RED FLAG RILEVATO**

I sintomi riportati non indicano necessità di visita medica urgente.
Continua a monitorare e segnala eventuali cambiamenti.

⚠️ Se il dolore persiste oltre 2 settimane o peggiora, consulta un professionista."""

    return StructuredTool.from_function(
        func=check_red_flags,
        name="red_flags_detector",
        description="Controlla se i sintomi indicano red flags medici che richiedono attenzione immediata.",
        args_schema=RedFlagsInput
    )


def create_pain_trend_tool(pain_repository=None) -> Tool:
    """
    Tool per analizzare trend del dolore.
    """

    def analyze_pain_trend(user_id: str, days: int = 7) -> str:
        """Analizza trend dolore negli ultimi N giorni."""

        try:
            if pain_repository:
                # Recupera dati reali
                end_date = date.today()
                start_date = end_date - timedelta(days=days)
                logs = pain_repository.get_logs_range(user_id, start_date, end_date)

                if not logs:
                    return f"Nessun dato dolore trovato per gli ultimi {days} giorni."

                # Calcola trend
                pain_levels = [log.pain_level for log in logs if hasattr(log, 'pain_level')]

                if len(pain_levels) < 2:
                    return f"Dati insufficienti per calcolare trend. Registra almeno 2 check-in."

                avg_first_half = sum(pain_levels[:len(pain_levels)//2]) / (len(pain_levels)//2)
                avg_second_half = sum(pain_levels[len(pain_levels)//2:]) / (len(pain_levels) - len(pain_levels)//2)

                diff = avg_second_half - avg_first_half

                if diff < -1:
                    trend = "📉 IN MIGLIORAMENTO"
                    msg = "Il dolore sta diminuendo! Ottimo progresso."
                elif diff > 1:
                    trend = "📈 IN PEGGIORAMENTO"
                    msg = "Il dolore sta aumentando. Valuta ridurre attività."
                else:
                    trend = "➡️ STABILE"
                    msg = "Il dolore è stabile. Continua con il programma attuale."

                return f"""📊 **ANALISI TREND DOLORE** (ultimi {days} giorni)

**Trend**: {trend}
**Media inizio periodo**: {avg_first_half:.1f}/10
**Media fine periodo**: {avg_second_half:.1f}/10
**Variazione**: {diff:+.1f}

💡 {msg}
"""
            else:
                return "Repository dolore non disponibile. Impossibile analizzare trend."

        except Exception as e:
            logger.error(f"Pain trend analysis error: {e}")
            return f"Errore analisi trend: {e}"

    return Tool(
        name="pain_analyzer",
        func=lambda uid: analyze_pain_trend(uid),
        description="""Analizza il trend del dolore negli ultimi 7 giorni.
Input: user_id
Output: trend (miglioramento/peggioramento/stabile) con statistiche."""
    )


def create_injury_guidelines_tool() -> Tool:
    """
    Tool per ottenere linee guida specifiche per infortunio.
    """

    def get_injury_guidelines(injury_type: str, phase: str = "") -> str:
        """Ottieni linee guida per gestione infortunio."""

        rag = get_rag_service()

        # Costruisci query
        query = f"{injury_type} linee guida trattamento gestione"
        if phase:
            query += f" {phase}"

        try:
            results = rag.retrieve_context(
                query=query,
                k=3,
                filter_metadata={"category": "medical"}
            )

            if not results:
                return f"""📚 **LINEE GUIDA GENERALI per {injury_type.upper()}:**

**Fase Acuta (0-72 ore)**
- Protezione: evita attività che aumentano dolore
- Riposo ottimale (non completo, movimento leggero OK)
- Ghiaccio: 15-20 min ogni 2-3 ore
- Compressione: se gonfiore presente
- Elevazione: se estremità interessata

**Fase Subacuta (3-14 giorni)**
- Movimento progressivo nel range senza dolore
- Esercizi isometrici leggeri
- Evitare immobilizzazione prolungata

**Fase di Recupero (2+ settimane)**
- Rinforzo muscolare progressivo
- Esercizi di controllo motorio
- Ritorno graduale alle attività

⚠️ Consulta un fisioterapista per un piano personalizzato.
"""

            output = f"📚 **LINEE GUIDA per {injury_type.upper()}:**\n\n"

            for r in results:
                content = r['content'][:400]
                output += f"• {content}...\n\n"

            return output

        except Exception as e:
            logger.error(f"Injury guidelines error: {e}")
            return f"Errore recupero linee guida: {e}"

    return Tool(
        name="injury_guidelines",
        func=get_injury_guidelines,
        description="""Ottieni linee guida evidence-based per gestione di un infortunio.
Input: tipo infortunio (es. 'lombalgia', 'tendinite')
Output: raccomandazioni trattamento, timeline, cosa evitare."""
    )


def create_smart_medical_tools(pain_repository=None) -> List[Tool]:
    """
    Crea set completo di tools medici intelligenti.

    Integra:
    - RAG per protocolli riabilitazione
    - Red flags detection
    - Analisi trend dolore
    - Linee guida infortuni
    """

    tools = [
        create_rehab_protocol_tool(),
        create_red_flags_tool(),
        create_pain_trend_tool(pain_repository),
        create_injury_guidelines_tool(),
    ]

    return tools
