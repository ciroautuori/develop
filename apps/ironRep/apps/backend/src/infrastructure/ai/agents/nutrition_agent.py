"""
Nutrition Agent
"""
from typing import Dict, Any, List
try:
    from langchain.agents import AgentExecutor, create_tool_calling_agent
except ImportError:
    # Fallback for broken langchain installation
    class AgentExecutor:
        def __init__(self, *args, **kwargs): pass
        def invoke(self, *args, **kwargs): return {"output": "Agent unavailable due to dependency error"}
        async def ainvoke(self, *args, **kwargs): return {"output": "Agent unavailable due to dependency error"}

    def create_tool_calling_agent(*args, **kwargs): return None
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..llm_service import LLMService
from ..rag_service import get_rag_service

class NutritionAgent:
    """
    Nutrition AI Agent - Specialista Nutrizione Sportiva.
    """

    SYSTEM_PROMPT = """Sei un Nutrizionista Sportivo specializzato in performance e recupero.

BACKGROUND:
- Laurea in Dietistica e Nutrizione Sportiva
- Esperto in dietoterapia per infortuni (anti-infiammatoria)
- Focus su macronutrienti e timing dei pasti (peri-workout)

TUO RUOLO:
Guidare l'atleta verso i suoi obiettivi (peso, performance, recupero) tramite l'alimentazione.
Collabori con il MEDICO (per restrizioni/allergie) e il COACH (per supporto energetico all'allenamento).

COMPITI:
1. Creare piani alimentari settimanali personalizzati.
2. Consigliare alimenti specifici per il recupero (es. Omega-3, Vitamina C, Proteine).
3. Analizzare log pasti e dare feedback.
4. Rispondere a domande su integratori e cibo.
5. Suggerire combinazioni di cibi salutari basandoti sui dati FatSecret.
6. Registrare i pasti dell'utente nel diario alimentare quando richiesto.

STRATEGIE NUTRIZIONALI:
- Infortunio acuto: Focus anti-infiammatorio, proteine alte per riparazione, calorie mantenimento.
- Rientro sport: Focus carboidrati peri-workout, idratazione.
- Perdita peso: Deficit calorico moderato (300-500kcal), proteine alte.

TOOLS DISPONIBILI:
- food_search: Cerca valori nutrizionali reali da FatSecret API (UNICA fonte dati cibi).
- nutrition_guidelines: Linee guida per obiettivo e contesto allenamento.
- user_preferences: Recupera preferenze utente.
- track_meal: Registra cibo mangiato nel diario (SOLO su richiesta esplicita).

IMPORTANTE:
- TUTTI i dati nutrizionali devono provenire da FatSecret API tramite food_search.
- Non prescrivere diete mediche per patologie gravi (rimanda al medico).
- Sii flessibile (regola 80/20).
- Incoraggia cibo vero vs integratori.
"""

    def __init__(
        self,
        llm_service: LLMService,
        tools: List,
        nutrition_repository=None
    ):
        self.llm_service = llm_service
        self.tools = tools
        self.nutrition_repository = nutrition_repository
        self.rag_service = get_rag_service()

        self.llm = llm_service.get_client_for_agent()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            return_intermediate_steps=True
        )

    async def answer_question(self, question: str, user_id: str = None, context: dict = None) -> Dict[str, Any]:
        input_parts = []

        # Add user context from RAG (only for user preferences/history, NOT food data)
        if user_id:
            user_context = await self._get_user_context(user_id, question)
            if user_context:
                input_parts.append(f"CONTESTO UTENTE (dalla memoria):\n{user_context}")

        # Additional context if provided
        if context:
            input_parts.append(f"CONTESTO AGGIUNTIVO: {context}")

        input_parts.append(f"DOMANDA UTENTE:\n{question}")
        input_text = "\n\n".join(input_parts)

        try:
            result = await self.agent_executor.ainvoke({"input": input_text})
            return {
                "answer": result["output"],
                "success": True
            }
        except Exception as e:
            return {"answer": f"Errore nutrizionista: {str(e)}", "success": False}

    async def _get_user_context(self, user_id: str, query: str) -> str:
        """Retrieve relevant user context from RAG."""
        try:
            from src.infrastructure.ai.user_context_rag import get_user_context_rag
            user_rag = get_user_context_rag()

            context_chunks = user_rag.retrieve_context(
                user_id=user_id,
                query=query,
                categories=["preference", "goal", "medical"],
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

    async def generate_weekly_plan(self, profile: dict) -> Dict[str, Any]:
        """Generate weekly nutrition plan using FatSecret API data EXCLUSIVELY."""
        prompt = f"""
GENERA PIANO NUTRIZIONALE SETTIMANALE

PROFILO UTENTE:
- Obiettivo: {profile.get('goal')}
- Dieta preferita: {profile.get('diet_type')}
- Calorie target: {profile.get('target_calories', 'Calcola tu')}
- Attività: {profile.get('activity_level')}
- Infortuni: {profile.get('injuries', 'Nessuno')}
- Allergie: {profile.get('allergies', [])}
- Cibi da evitare: {profile.get('disliked_foods', [])}
- Cibi preferiti: {profile.get('favorite_foods', [])}

⚠️ REGOLE OBBLIGATORIE:
1. DEVI usare il tool 'food_search' per OGNI alimento che inserisci nel piano
2. NON inventare MAI valori nutrizionali - usa SOLO dati da FatSecret API
3. Se non trovi un alimento, cercane uno simile o indica "valori da verificare"
4. Includi SEMPRE calorie e macro (P/C/F) da FatSecret per ogni alimento

STRUTTURA RICHIESTA:
Per ogni giorno (Lunedì-Domenica):
- Colazione: [alimenti con macro da food_search]
- Pranzo: [alimenti con macro da food_search]
- Cena: [alimenti con macro da food_search]
- Snack: [alimenti con macro da food_search]
- Totale giorno: kcal, proteine, carboidrati, grassi

PRIMO PASSO: Usa food_search per cercare gli alimenti principali che inserirai nel piano.
"""
        try:
            result = await self.agent_executor.ainvoke({"input": prompt})
            return {"plan": result["output"], "success": True}
        except Exception as e:
            return {"plan": f"Errore generazione piano: {str(e)}", "success": False}
