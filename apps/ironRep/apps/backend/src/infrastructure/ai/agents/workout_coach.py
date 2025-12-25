"""
Workout Coach Agent

AI agent specializzato nella programmazione e coaching degli allenamenti.
Focus su: periodizzazione, progressione, tecnica, esercizi sicuri.
"""
from typing import List, Dict, Any
try:
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain.agents.format_scratchpad.tools import format_to_tool_messages
    from langchain.agents.output_parsers.tools import ToolsAgentOutputParser
except ImportError:
    # Fallback for broken langchain installation
    class AgentExecutor:
        def __init__(self, *args, **kwargs): pass
        def invoke(self, *args, **kwargs): return {"output": "Agent unavailable due to dependency error"}
        async def ainvoke(self, *args, **kwargs): return {"output": "Agent unavailable due to dependency error"}

    def create_tool_calling_agent(*args, **kwargs): return None
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool

from ..llm_service import LLMService


class WorkoutCoachAgent:
    """
    Workout Coach AI Agent - Specialista Programmazione Allenamenti.

    RUOLO: Allenatore CrossFit/Strength & Conditioning
    FOCUS: Programmazione, progressione, tecnica, periodizzazione

    NON gestisce: Diagnosi mediche, dolore acuto, red flags (quello è MedicalAgent)
    """

    SYSTEM_PROMPT = """Sei un Master CrossFit Coach & Strength Conditioning Specialist.

BACKGROUND:
- 15 anni di esperienza nella programmazione per atleti CrossFit/Weightlifting
- Certificato CF-L4, USAW, CSCS
- Programmato per 1000+ atleti (dal principiante all'elite)
- Specializzato in ritorno allo sport post-infortunio

EXPERTISE:
- Periodizzazione (lineare, ondulata, coniugata)
- Progressione esercizi (scaling, modifications)
- Tecnica Olympic Lifts & Gymnastics
- Energy systems training
- Mobility & Prehab
- Adattamenti per limitazioni fisiche

TUO RUOLO:
Sei l'ALLENATORE che programma i workout in base alla cartella medica dell'utente.
Il MEDICO (MedicalAgent) ti dice:
- Livello dolore attuale
- Localizzazioni problematiche
- Esercizi controindicati
- Fase recupero (1-4)

Tu PROGRAMMI:
- Workout settimanali adattati
- Progressione esercizi sicura
- Scaling options
- Tecnica e cues
- Periodizzazione long-term

APPROCCIO PROGRAMMAZIONE:

1. **ASSESSMENT CAPACITÀ**:
   - Livello tecnico (principiante/intermedio/avanzato)
   - Limitazioni attuali (da cartella medica)
   - Obiettivi (ritorno sport, performance, salute)
   - Disponibilità (giorni/settimana, tempo/sessione)

2. **PERIODIZZAZIONE**:
   - Fase 1 (Settimane 1-4): Foundation + Tecnica
   - Fase 2 (Settimane 5-8): Volume + Capacity
   - Fase 3 (Settimane 9-12): Intensità + Skill
   - Fase 4 (Settimane 13+): Performance + Sport-Specific

3. **STRUTTURA WORKOUT**:
   ```
   WARM-UP (10-15min):
   - General: Cardio leggero
   - Specific: Prep movimenti workout
   - Mobility: Focus aree problematiche

   SKILL/STRENGTH (20-30min):
   - Tecnica: Olympic lifts, gymnastics
   - Strength: Squat, press, pull patterns
   - Progressione: Sets x Reps @ %1RM

   CONDITIONING (15-25min):
   - MetCon: AMRAP, EMOM, For Time
   - Energy system: Aerobic/Anaerobic/Mixed
   - Scaling: Pesi, reps, movimenti

   COOL-DOWN (10min):
   - Stretching statico
   - Foam rolling
   - Breathing
   ```

4. **ADATTAMENTI PER INFORTUNIO**:
   - Se dolore lombare: No flexion under load, focus hinge pattern
   - Se dolore spalla: No overhead pressing, focus pulling
   - Se dolore ginocchio: No impact, focus strength end-range
   - Se dolore anca: No deep flexion, focus stability

   **SEMPRE chiedi al MedicalAgent se non sei sicuro!**

5. **PROGRESSIONE**:
   - Aumenta volume prima di intensità
   - Master tecnica prima di caricare
   - Testa esercizi progressivi (es: Box Squat → Back Squat → Front Squat)
   - Rispetta timeline recupero

STILE COMUNICAZIONE:
- Motivante ma realistico
- Tecnico quando serve (cues, biomeccanica)
- Fornisci SEMPRE alternatives/scaling
- Spiega il PERCHÉ della programmazione
- Celebra progressi, anche piccoli

TOOLS DISPONIBILI:
- exercise_search: Cerca esercizi nel database (727+ esercizi con muscoli target)
- safe_exercises: Trova esercizi sicuri per area infortunata e fase recupero
- workout_template: Genera template workout per obiettivo (forza, recupero, core)
- exercise_substitution: Trova alternative per esercizi controindicati
- progression_advisor: Valuta se pronto per progredire alla fase successiva

IMPORTANTE:
- NON dare consigli medici (quello è MedicalAgent)
- Se utente riporta dolore nuovo/acuto → "Consulta il Medical Agent"
- Focus su ALLENAMENTO, non diagnosi
- Rispetta sempre controindicazioni mediche
- Progressione graduale > Performance immediata

ESEMPI DOMANDE CHE GESTISCI:
✅ "Che workout faccio oggi?"
✅ "Posso fare deadlift con il mio infortunio?"
✅ "Come progredisco verso pull-ups?"
✅ "Che scaling per questo WOD?"
✅ "Come miglioro il mio snatch?"

ESEMPI DOMANDE DA REDIRIGERE:
❌ "Ho dolore acuto alla schiena" → Medical Agent
❌ "Devo preoccuparmi di questo sintomo?" → Medical Agent
❌ "Il mio dolore sta peggiorando" → Medical Agent
"""

    def __init__(
        self,
        llm_service: LLMService,
        tools: List,
        user_repository=None,
        workout_repository=None,
        exercise_library=None,
        rag_service=None
    ):
        """
        Initialize workout coach agent.

        Args:
            llm_service: LLM service
            tools: LangChain tools (exercise_validator, progression_calculator, etc.)
            user_repository: User data
            workout_repository: Workout history
            exercise_library: Exercise database
            rag_service: RAG for exercise knowledge
        """
        self.llm_service = llm_service
        self.tools = tools
        self.user_repository = user_repository
        self.workout_repository = workout_repository
        self.exercise_library = exercise_library
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
        # Manually create the tool calling agent to avoid introspection bugs
        try:
            self.llm_with_tools = self.llm.bind_tools(self.tools)
        except (NotImplementedError, AttributeError):
            from src.infrastructure.logging import get_logger
            logger = get_logger(__name__)
            logger.warning(f"LLM {type(self.llm).__name__} does not support bind_tools. Tools disabled.")
            self.llm_with_tools = self.llm
        
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

    async def answer_question(
        self,
        question: str,
        user_id: str,
        context: dict = None
    ) -> Dict[str, Any]:
        """
        Answer workout/training related question with user context from RAG.

        Args:
            question: User's question
            user_id: User ID
            context: Additional context (medical status, workout history)

        Returns:
            dict with answer and intermediate steps
        """
        # Build enhanced input with context
        input_parts = []

        # Add user context from RAG
        user_context = await self._get_user_context(user_id, question)
        if user_context:
            input_parts.append(f"CONTESTO UTENTE (dalla memoria):\n{user_context}")

        # Add medical context if provided
        if context:
            medical_status = context.get("medical_status", {})
            if medical_status:
                input_parts.append(f"""
CONTESTO MEDICO (da Medical Agent):
- Dolore attuale: {medical_status.get('pain_level', 'N/A')}/10
- Localizzazioni: {', '.join(medical_status.get('pain_locations', []))}
- Fase recupero: {medical_status.get('phase', 'N/A')}
- Controindicazioni: {', '.join(medical_status.get('contraindications', []))}""")

        input_parts.append(f"DOMANDA UTENTE:\n{question}")
        input_text = "\n\n".join(input_parts)

        try:
            result = await self.agent_executor.ainvoke({
                "input": input_text
            })

            return {
                "answer": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
                "success": True
            }

        except Exception as e:
            return {
                "answer": f"Errore: {str(e)}. Riprova o contatta supporto.",
                "success": False,
                "error": str(e)
            }

    async def _get_user_context(self, user_id: str, query: str) -> str:
        """Retrieve relevant user context from RAG."""
        try:
            from src.infrastructure.ai.user_context_rag import get_user_context_rag
            user_rag = get_user_context_rag()

            context_chunks = user_rag.retrieve_context(
                user_id=user_id,
                query=query,
                categories=["goal", "equipment", "preference", "history"],
                k=5
            )

            if not context_chunks:
                return ""

            context_parts = []
            for chunk in context_chunks:
                context_parts.append(f"- [{chunk['category']}] {chunk['content'][:200]}")

            return "\n".join(context_parts)

        except Exception as e:
            from src.infrastructure.logging import get_logger
            logger = get_logger(__name__)
            logger.warning(f"Failed to get user context: {e}")
            return ""

    async def generate_weekly_program(
        self,
        user_id: str,
        medical_clearance: dict,
        training_days: int = 4,
        sport_type: str = None
    ) -> Dict[str, Any]:
        """
        Generate full weekly training program.

        Args:
            user_id: User ID
            medical_clearance: Medical status from MedicalAgent
            training_days: Days per week (default 4)
            sport_type: Sport specialization (crossfit, bodybuilding, etc.)

        Returns:
            dict with weekly program
        """
        sport_context = f"- Sport: {sport_type.replace('_', ' ').title()}" if sport_type else "- Sport: Fitness Generale"

        input_text = f"""
GENERA PROGRAMMA SETTIMANALE

CONTESTO MEDICO:
- Dolore: {medical_clearance.get('pain_level')}/10
- Fase: {medical_clearance.get('phase')}
- Controindicazioni: {', '.join(medical_clearance.get('contraindications', []))}

PARAMETRI:
- Giorni allenamento: {training_days}/settimana
- Durata sessione: 60min
{sport_context}

Crea programma completo con:
1. Struttura settimanale (quali giorni, focus)
2. Workout dettagliati per ogni giorno
3. Progressione settimana-su-settimana
4. Scaling options
5. Note tecniche importanti
"""

        try:
            result = await self.agent_executor.ainvoke({
                "input": input_text
            })

            return {
                "program": result["output"],
                "success": True
            }

        except Exception as e:
            return {
                "program": f"Errore generazione programma: {str(e)}",
                "success": False,
                "error": str(e)
            }
