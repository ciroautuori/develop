"""
Medical Agent

AI agent specializzato nel monitoraggio medico e recupero da infortuni.
Focus su: diagnosi, dolore, red flags, check-in giornaliero, progressione recupero.
"""
from typing import List, Dict, Any
try:
    from langchain.agents import AgentExecutor
    from langchain.agents.format_scratchpad.tools import format_to_tool_messages
    from langchain.agents.output_parsers.tools import ToolsAgentOutputParser
    # create_tool_calling_agent is bypassed, so it's not strictly needed here,
    # but keeping it for the fallback structure if it were used elsewhere.
    from langchain.agents import create_tool_calling_agent as _create_tool_calling_agent_placeholder
except ImportError:
    # Fallback for broken langchain installation
    class AgentExecutor:
        def __init__(self, *args, **kwargs): pass
        def invoke(self, *args, **kwargs): return {"output": "Agent unavailable due to dependency error"}
        async def ainvoke(self, *args, **kwargs): return {"output": "Agent unavailable due to dependency error"}

    def _create_tool_calling_agent_placeholder(*args, **kwargs): return None # Placeholder for the bypassed function
    # Define necessary components for the manual agent construction as mocks
    def format_to_tool_messages(*args, **kwargs): return []
    class ToolsAgentOutputParser:
        def __init__(self, *args, **kwargs): pass
        def parse(self, *args, **kwargs): return {"output": "Agent unavailable due to dependency error"}


from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool

from ..llm_service import LLMService


class MedicalAgent:
    """
    Medical Agent - Specialista Monitoraggio Medico Infortuni.

    RUOLO: Medico Sportivo / Fisioterapista
    FOCUS: Dolore, sintomi, red flags, recupero, check-in giornaliero

    NON gestisce: Programmazione workout (quello è WorkoutCoachAgent)
    """

    SYSTEM_PROMPT = """Sei un Sports Medicine Specialist & Physical Therapist.

BACKGROUND:
- Medico specializzato in medicina dello sport
- 15 anni esperienza riabilitazione atleti
- Gestiti 500+ casi infortuni sportivi
- Tasso successo 92% ritorno completo allo sport
- Expertise anatomia, biomeccanica, patologie muscoloscheletriche

PATOLOGIE EXPERTISE:
- Lombari: Sciatica, ernia discale, stenosi, spondilolistesi
- Inguinali: Pubalgia, tendinite adduttori, core instability
- Spalla: Impingement, labrum, cuffia rotatori
- Ginocchio: Menisco, LCA/LCP, tendinite rotulea, condropatia
- Anca: FAI, labrum, tendinite psoas, borsite trocanterica
- Caviglia: Distorsioni, tendinite achillea, instabilità
- Gomito: Epicondilite, tendinite bicipite

TUO RUOLO:
Sei il MEDICO che monitora lo stato di salute dell'atleta infortunato.
Il COACH (WorkoutCoachAgent) programma gli allenamenti basandosi sulle tue indicazioni.

TU GESTISCI:
1. **CHECK-IN GIORNALIERO**:
   - Livello dolore (0-10)
   - Localizzazioni dolore
   - Trigger identificati
   - Sintomi associati
   - Qualità sonno/riposo

2. **ANALISI TREND**:
   - Dolore in miglioramento/peggioramento/stabile
   - Pattern trigger
   - Efficacia trattamenti
   - Timeline recupero

3. **RED FLAGS DETECTION**:
   - Sintomi neurologici (formicolio, debolezza)
   - Dolore notturno che sveglia
   - Peggioramento nonostante riposo
   - Febbre/infezione
   - Trauma recente significativo
   - → Se red flag: CONSIGLIA VISITA MEDICA URGENTE

4. **CLEARANCE MEDICA**:
   - Esercizi controindicati
   - Movimenti da evitare
   - Range motion sicuro
   - Intensità massima permessa
   - Fase recupero (1-4)

5. **EDUCAZIONE PAZIENTE**:
   - Anatomia infortunio
   - Meccanismo lesione
   - Timeline recupero realistica
   - Prevenzione recidive
   - Self-management strategie

FASI RECUPERO:

**FASE 1: PROTEZIONE (Settimane 1-2)**
- Dolore: 7-10/10
- Focus: Ridurre infiammazione, proteggere tessuti
- Clearance: Solo mobilità gentile, no carico
- Controindicazioni: Movimenti dolorosi, carico, impact

**FASE 2: MOBILITÀ (Settimane 3-4)**
- Dolore: 4-6/10
- Focus: Recuperare ROM, iniziare rinforzo leggero
- Clearance: Movimenti controllati, carico minimo
- Controindicazioni: Carico pesante, movimenti balistici

**FASE 3: RINFORZO (Settimane 5-8)**
- Dolore: 2-3/10
- Focus: Strength building, controllo motorio
- Clearance: Carico progressivo, esercizi funzionali
- Controindicazioni: Movimenti estremi, carico massimale

**FASE 4: RITORNO SPORT (Settimane 9+)**
- Dolore: 0-1/10
- Focus: Sport-specific, performance
- Clearance: Tutti movimenti se tecnica corretta
- Controindicazioni: Overtraining, tecnica scadente

PROTOCOLLO CHECK-IN GIORNALIERO:

1. **SALUTO EMPATICO**:
   "Ciao! Come ti senti oggi? Raccontami del tuo dolore."

2. **RACCOLTA DATI**:
   - Dolore 0-10?
   - Dove esattamente?
   - Cosa lo peggiora?
   - Sintomi associati?

3. **ANALISI TREND** (usa tool pain_analyzer):
   - Confronta con giorni precedenti
   - Identifica pattern
   - Valuta efficacia trattamento

4. **RED FLAGS CHECK** (usa tool red_flags_detector):
   - Sintomi neurologici?
   - Dolore notturno?
   - Peggioramento?
   - → Se SÌ: consiglia visita medica

5. **CLEARANCE GIORNALIERA**:
   - Fase recupero attuale
   - Esercizi controindicati oggi
   - Intensità massima permessa
   - Movimenti da evitare

6. **COMUNICAZIONE AL COACH**:
   "Oggi sei in Fase X, dolore Y/10. Il Coach può programmare workout con queste limitazioni: [...]"

7. **EDUCAZIONE**:
   - Spiega perché certi movimenti sono controindicati
   - Rassicura su timeline recupero
   - Fornisci self-management tips

STILE COMUNICAZIONE:
- Empatico e rassicurante
- Tecnico quando serve (anatomia, patologia)
- NON minimizzare il dolore
- Focus su PROGRESSO, non perfezione
- Celebra miglioramenti anche piccoli
- Realistico su timeline

TOOLS DISPONIBILI:
- pain_analyzer: Analizza trend dolore ultimi N giorni
- red_flags_detector: Controlla sintomi allarmanti (neurologici, infezione, trauma)
- rehab_protocol: Cerca protocolli riabilitazione dal knowledge base (8+ protocolli)
- injury_guidelines: Ottieni linee guida evidence-based per gestione infortunio

IMPORTANTE:
- NON programmare workout (quello è WorkoutCoachAgent)
- Se utente chiede "che workout faccio?" → "Consulta il Coach, io ti do clearance medica"
- Focus su SALUTE e RECUPERO, non performance
- Sempre priorità sicurezza > velocità recupero
- Se dubbio su red flag → consiglia visita medica

ESEMPI DOMANDE CHE GESTISCI:
✅ "Come sta andando il mio recupero?"
✅ "Il dolore sta migliorando?"
✅ "Devo preoccuparmi di questo sintomo?"
✅ "Quando posso tornare a correre?"
✅ "Perché ho ancora dolore dopo 2 settimane?"

ESEMPI DOMANDE DA REDIRIGERE:
❌ "Che workout faccio oggi?" → Workout Coach
❌ "Come miglioro il mio snatch?" → Workout Coach
❌ "Che programma settimanale mi consigli?" → Workout Coach
"""

    def __init__(
        self,
        llm_service: LLMService,
        tools: List,
        user_repository=None,
        pain_repository=None,
        biometric_repository=None,
        rag_service=None
    ):
        """
        Initialize medical agent.

        Args:
            llm_service: LLM service
            tools: LangChain tools (pain_analyzer, red_flags_detector, etc.)
            user_repository: User data
            pain_repository: Pain history
            biometric_repository: Biometric data
            rag_service: RAG for medical knowledge
        """
        self.llm_service = llm_service
        self.tools = tools
        self.user_repository = user_repository
        self.pain_repository = pain_repository
        self.biometric_repository = biometric_repository
        self.rag_service = rag_service

        # Get LLM client
        self.llm = llm_service.get_client_for_agent()

        # Create prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # Create agent
        # self.agent = create_tool_calling_agent(llm=self.llm, tools=self.tools, prompt=self.prompt)
        
        # Manually create the tool calling agent to avoid introspection bugs in create_tool_calling_agent
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_tool_messages(x["intermediate_steps"]),
            }
            | self.prompt
            | self.llm_with_tools
            | ToolsAgentOutputParser()
        )
        
        # Create executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            return_intermediate_steps=True
        )

    async def process_daily_checkin(
        self,
        pain_level: int,
        pain_locations: List[str],
        triggers: List[str],
        user_id: str,  # Mandatory user_id
        notes: str = ""
    ) -> Dict[str, Any]:
        """
        Process daily medical check-in.

        Args:
            pain_level: Current pain 0-10
            pain_locations: Pain locations
            triggers: Known triggers
            notes: Additional notes
            user_id: User ID for context retrieval

        Returns:
            dict with medical analysis and clearance
        """
        # Get user context from RAG to provide history
        user_context = await self._get_user_context(user_id, f"pain in {', '.join(pain_locations)}")

        input_text = f"""
DAILY MEDICAL CHECK-IN:

CONTESTO STORICO UTENTE (RAG):
{user_context}

DATI OGGI:
- Dolore: {pain_level}/10
- Localizzazioni: {', '.join(pain_locations)}
- Trigger: {', '.join(triggers) if triggers else 'Nessuno'}
- Note: {notes if notes else 'Nessuna'}

ANALISI RICHIESTA:
1. Analizza trend dolore (ultimi 7 giorni) - usa pain_analyzer
2. Controlla red flags - usa red_flags_detector
3. Determina fase recupero attuale
4. Fornisci clearance medica per oggi:
   - Esercizi controindicati
   - Movimenti da evitare
   - Intensità massima permessa
5. Valuta se pronto per progredire fase - usa progression_calculator
6. Fornisci educazione pertinente

FORMATO RISPOSTA:
📊 ANALISI TREND: [risultato pain_analyzer]
⚠️ RED FLAGS: [risultato red_flags_detector]
🏥 FASE RECUPERO: [1/2/3/4]
✅ CLEARANCE OGGI: [cosa può fare]
❌ CONTROINDICAZIONI: [cosa evitare]
📈 PROGRESSIONE: [pronto per fase successiva? quando?]
💡 EDUCAZIONE: [consigli self-management]
"""

        try:
            result = await self.agent_executor.ainvoke({
                "input": input_text,
                "chat_history": [],  # Initialize empty history for tool calls
            })

            return {
                "output": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
                "success": True,
                "medical_clearance": self._extract_clearance(result["output"])
            }

        except Exception as e:
            return {
                "output": f"Errore check-in medico: {str(e)}",
                "success": False,
                "error": str(e)
            }

    async def answer_question(
        self,
        question: str,
        user_id: str,
        context: dict = None
    ) -> Dict[str, Any]:
        """
        Answer medical/recovery question with user context from RAG.

        Args:
            question: User's question
            user_id: User ID
            context: Additional context

        Returns:
            dict with answer and intermediate steps
        """
        try:
            # Build enriched input with user context
            enriched_input = question

            # Add user context from RAG if available
            user_context = await self._get_user_context(user_id, question)
            if user_context:
                enriched_input = f"""
CONTESTO UTENTE (dalla memoria):
{user_context}

DOMANDA UTENTE:
{question}
"""

            result = await self.agent_executor.ainvoke({
                "input": enriched_input
            })

            return {
                "answer": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
                "success": True
            }

        except Exception as e:
            return {
                "answer": f"Errore: {str(e)}",
                "success": False,
                "error": str(e)
            }

    async def _get_user_context(self, user_id: str, query: str) -> str:
        """
        Retrieve relevant user context from RAG.

        Args:
            user_id: User identifier
            query: Query to find relevant context

        Returns:
            Formatted context string
        """
        try:
            # Try to get UserContextRAG
            from src.infrastructure.ai.user_context_rag import get_user_context_rag
            from src.infrastructure.logging import get_logger

            logger = get_logger(__name__)
            user_rag = get_user_context_rag()

            # Retrieve relevant context for medical queries
            context_chunks = user_rag.retrieve_context(
                user_id=user_id,
                query=query,
                categories=["pain", "medical", "history", "goal"],
                k=5
            )

            if not context_chunks:
                return ""

            # Format context
            context_parts = []
            for chunk in context_chunks:
                context_parts.append(f"- [{chunk['category']}] {chunk['content'][:200]}")

            return "\n".join(context_parts)

        except Exception as e:
            logger.warning(f"Failed to get user context: {e}")
            return ""

    def _extract_clearance(self, output: str) -> dict:
        """Extract medical clearance from agent output."""
        # Simple extraction - can be enhanced with structured output
        clearance = {
            "phase": "unknown",
            "contraindications": [],
            "max_intensity": "unknown",
            "ready_to_progress": False
        }

        # Extract phase
        if "FASE 1" in output or "Fase 1" in output:
            clearance["phase"] = "phase_1"
        elif "FASE 2" in output or "Fase 2" in output:
            clearance["phase"] = "phase_2"
        elif "FASE 3" in output or "Fase 3" in output:
            clearance["phase"] = "phase_3"
        elif "FASE 4" in output or "Fase 4" in output:
            clearance["phase"] = "phase_4"

        return clearance
