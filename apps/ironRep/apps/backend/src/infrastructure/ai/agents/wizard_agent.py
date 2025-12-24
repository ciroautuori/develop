"""
Wizard Agent - Conversational Onboarding Interviewer

Conducts dynamic interviews to gather user context (pain, goals, equipment)
and stores responses in UserContextRAG for personalized agent interactions.
Creates User in DB and triggers AgentOrchestrator for initial plans.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging

from src.infrastructure.ai.llm_service import LLMService
from src.infrastructure.ai.user_context_rag import UserContextRAG, ContextCategory

logger = logging.getLogger(__name__)


class InterviewPhase(str, Enum):
    """Phases of the wizard interview."""
    GREETING = "greeting"
    # Module Selection - User chooses what they need
    AGENT_SELECTION = "agent_selection"  # Which agents to activate
    SPORT_SELECTION = "sport_selection"  # What sport/training type
    # Medical (optional if no injury)
    PAIN_ASSESSMENT = "pain_assessment"
    INJURY_HISTORY = "injury_history"
    # Goals & Equipment
    GOALS = "goals"
    EQUIPMENT = "equipment"
    PREFERENCES = "preferences"
    # Nutrition mode
    NUTRITION_MODE = "nutrition_mode"  # Full plan vs recipes/tips
    NUTRITION_DETAILS = "nutrition_details"  # Allergies, preferences
    SUMMARY = "summary"
    COMPLETE = "complete"


class MedicalMode(str, Enum):
    """How user wants to use Medical agent."""
    INJURY_RECOVERY = "injury_recovery"  # Has injury, needs recovery plan
    WELLNESS_TIPS = "wellness_tips"      # No injury, just health advice
    DISABLED = "disabled"                # Doesn't want medical agent


class CoachMode(str, Enum):
    """Sport/training type for Coach agent."""
    CROSSFIT = "crossfit"
    BODYBUILDING = "bodybuilding"
    POWERLIFTING = "powerlifting"
    RUNNING = "running"
    FUNCTIONAL = "functional"
    GENERAL_FITNESS = "general_fitness"
    REHAB_FOCUSED = "rehab_focused"  # Recovery-oriented


class NutritionMode(str, Enum):
    """How user wants to use Nutrition agent."""
    FULL_DIET_PLAN = "full_diet_plan"    # Complete structured diet
    RECIPES_ONLY = "recipes_only"        # Just recipes and ideas
    TIPS_TRACKING = "tips_tracking"      # Tips + meal tracking
    DISABLED = "disabled"                # Doesn't want nutrition


class WizardAgent:
    """
    AI-powered conversational onboarding wizard.

    Conducts dynamic interviews based on user responses,
    extracting structured data and storing in RAG.
    """

    # ========== WIZARD v3 - FLUSSO COMPLETO CON DETTAGLI ==========
    SYSTEM_PROMPT = """Sei il Wizard di IronRep. Raccogli informazioni COMPLETE per personalizzare l'esperienza.

📋 REGOLA D'ORO:
Controlla SEMPRE i "DATI GIÀ RACCOLTI". Se un'informazione è già presente (es. infortunio, sport, obiettivi), NON chiederla di nuovo. Acknowledge l'informazione ("Ho visto che fai CrossFit...") e passa alla prossima domanda mancante.

📋 FLUSSO DOMANDE (in sequenza):
1. Infortunio/Dolore (se già noto, passa oltre)
2. Dettagli Infortunio (se già noti, passa oltre)
3. Sport + Obiettivo (se già noti, passa oltre)
4. Equipment/Location (se già noti, passa oltre)
5. Giorni + Durata (se già noti, passa oltre)
6. Nutrizione (Sì/No + Obiettivo)
7. Dettagli Nutrizione (Allergie/Preferenze)
8. Riepilogo + Conferma

⛔ REGOLE:
- MAX 2 frasi per risposta
- NON ripetere domande se il dato è già presente
- Se l'utente dà info extra, salvale subito
- Sii diretto e professionale, ma incoraggiante"""

    FEW_SHOT_EXAMPLES = """
=== FLUSSO CON INFORTUNIO ===
Wizard: "Ciao! Hai un infortunio attivo o dolore cronico?"
Utente: "Sì, ho un'ernia"
Wizard: "Capito. Dove esattamente? Da quanto tempo? Come valuteresti il dolore da 1 a 10?"
Utente: "Ernia L5-S1 con sciatica, da 6 mesi, dolore 5-6"
Wizard: "Ernia L5-S1, sciatica, 6 mesi, dolore 5-6/10. Che sport fai e qual è il tuo obiettivo?"
Utente: "CrossFit, voglio tornare a gareggiare"
Wizard: "CrossFit, obiettivo competizione. Dove ti alleni e che attrezzatura hai?"
Utente: "In box, c'è tutto"
Wizard: "Box completo. Quanti giorni riesci e quanto tempo per sessione?"
Utente: "4 giorni, 60-90 minuti"
Wizard: "4x/sett, 60-90min. Vuoi anche supporto nutrizionale? Obiettivo peso?"
Utente: "Sì, voglio perdere grasso mantenendo forza"
Wizard: "Deficit intelligente per perdere grasso. Hai allergie o cibi che eviti?"
Utente: "Niente lattosio, non mi piace il pesce"
Wizard: "No lattosio, no pesce. Riepilogo: Ernia L5-S1 (dolore 5-6/10), CrossFit competitivo 4x/sett 60-90min, box completo, deficit nutrizionale senza lattosio/pesce. Confermo?"

=== FLUSSO SENZA INFORTUNIO ===
Wizard: "Ciao! Hai infortuni o dolori attivi?"
Utente: "No, tutto ok"
Wizard: "Perfetto! Che sport fai e qual è il tuo obiettivo?"
Utente: "Palestra, voglio mettere massa muscolare"
Wizard: "Bodybuilding per ipertrofia. Dove ti alleni e che attrezzatura hai?"
Utente: "Palestra commerciale, tutto disponibile"
Wizard: "Palestra completa. Quanti giorni e quanto tempo per sessione?"
Utente: "5 giorni, 75 minuti circa"
Wizard: "5x/sett, 75min. Vuoi supporto nutrizionale per la crescita?"
Utente: "Sì, surplus calorico"
Wizard: "Surplus per massa. Allergie o cibi che eviti?"
Utente: "Sono celiaco"
Wizard: "No glutine. Riepilogo: Bodybuilding 5x/sett 75min, palestra completa, surplus calorico senza glutine. Confermo?"
"""

    # FASI COMPLETE
    PHASE_PROMPTS = {
        InterviewPhase.GREETING: "Saluta e chiedi se ha infortuni (se non già noto). Se sai già tutto, fai un piccolo riepilogo di benvenuto.",
        InterviewPhase.PAIN_ASSESSMENT: "Chiedi dettagli mancanti sull'infortunio: DOVE, CHE TIPO, DURATA, LIVELLO DOLORE 1-10.",
        InterviewPhase.SPORT_SELECTION: "Chiedi SPORT (CrossFit, Gym, Running, etc.) e OBIETTIVO principale.",
        InterviewPhase.EQUIPMENT: "Chiedi DOVE si allena (Box, Home Gym, Commercial) e che ATTREZZATURA ha.",
        InterviewPhase.PREFERENCES: "Chiedi GIORNI/settimana e DURATA sessione (es. 60 min).",
        InterviewPhase.NUTRITION_MODE: "Chiedi se vuole nutrizione e l'OBIETTIVO calorico (deficit/mantenimento/surplus).",
        InterviewPhase.NUTRITION_DETAILS: "Chiedi ALLERGIE, CIBI da evitare e PREFERENZE (Vegano, Keto, etc.).",
        InterviewPhase.SUMMARY: "Genera il RIEPILOGO COMPLETO e chiedi la conferma finale."
    }

    def __init__(
        self,
        llm_service: LLMService,
        user_context_rag: UserContextRAG,
        user_repository=None,
        orchestrator=None,
        session_repository=None  # NEW: DB persistence for production
    ):
        self.llm = llm_service
        self.rag = user_context_rag
        self.user_repository = user_repository
        self.orchestrator = orchestrator
        self.session_repository = session_repository

        # In-memory cache (falls back if no repository)
        self._sessions_cache: Dict[str, Dict] = {}

    def _get_session(self, session_id: str) -> Dict:
        """Get or create session state with DB persistence."""
        # Try DB first if repository available
        if self.session_repository:
            try:
                db_session = self.session_repository.get_session(session_id)
                if db_session:
                    # Convert phase string to enum
                    phase_str = db_session.get("phase", "greeting")
                    db_session["phase"] = InterviewPhase(phase_str) if phase_str else InterviewPhase.GREETING
                    # Convert agent_config modes to enums
                    ac = db_session.get("agent_config", {})
                    if isinstance(ac.get("medical_mode"), str):
                        ac["medical_mode"] = MedicalMode(ac["medical_mode"]) if ac["medical_mode"] else MedicalMode.WELLNESS_TIPS
                    if isinstance(ac.get("coach_mode"), str):
                        ac["coach_mode"] = CoachMode(ac["coach_mode"]) if ac["coach_mode"] else CoachMode.GENERAL_FITNESS
                    if isinstance(ac.get("nutrition_mode"), str):
                        ac["nutrition_mode"] = NutritionMode(ac["nutrition_mode"]) if ac["nutrition_mode"] else NutritionMode.TIPS_TRACKING
                    self._sessions_cache[session_id] = db_session
                    return db_session
            except Exception as e:
                logger.warning(f"Failed to get session from DB: {e}")

        # Fallback to in-memory
        if session_id not in self._sessions_cache:
            new_session = {
                "phase": InterviewPhase.GREETING,
                "collected_data": {},
                "conversation_history": [],
                "user_id": None,
                "email": None,
                "started_at": datetime.now().isoformat(),
                "agent_config": {
                    "medical_mode": MedicalMode.WELLNESS_TIPS,
                    "coach_mode": CoachMode.GENERAL_FITNESS,
                    "nutrition_mode": NutritionMode.TIPS_TRACKING,
                    "has_injury": False,
                    "sport_type": None
                }
            }
            self._sessions_cache[session_id] = new_session

            # Persist to DB if available
            if self.session_repository:
                try:
                    self.session_repository.create_session(session_id)
                except Exception as e:
                    logger.warning(f"Failed to create session in DB: {e}")

        return self._sessions_cache[session_id]

    def _save_session(self, session_id: str, session: Dict) -> None:
        """Persist session state to DB."""
        if not self.session_repository:
            return

        try:
            # Convert enums to strings for JSON storage
            phase_str = session["phase"].value if hasattr(session["phase"], 'value') else str(session["phase"])
            ac = session.get("agent_config", {})
            agent_config_serialized = {
                "medical_mode": ac.get("medical_mode").value if hasattr(ac.get("medical_mode"), 'value') else str(ac.get("medical_mode", "wellness_tips")),
                "coach_mode": ac.get("coach_mode").value if hasattr(ac.get("coach_mode"), 'value') else str(ac.get("coach_mode", "general_fitness")),
                "nutrition_mode": ac.get("nutrition_mode").value if hasattr(ac.get("nutrition_mode"), 'value') else str(ac.get("nutrition_mode", "tips_tracking")),
                "has_injury": ac.get("has_injury", False),
                "sport_type": ac.get("sport_type")
            }

            self.session_repository.update_session(
                session_id=session_id,
                phase=phase_str,
                collected_data=session.get("collected_data", {}),
                agent_config=agent_config_serialized,
                conversation_history=session.get("conversation_history", []),
                user_id=session.get("user_id"),
                email=session.get("email")
            )
        except Exception as e:
            logger.warning(f"Failed to save session to DB: {e}")

    async def _get_personalized_knowledge(self, session: Dict) -> Dict[str, str]:
        """
        Recupera conoscenze personalizzate dal RAG in base a TUTTI i dati raccolti.

        Personalizza per:
        - Infortuni → protocolli riabilitativi, esercizi sicuri
        - Sport → programmi specifici, esercizi tipici
        - Nutrizione → ricette, piani alimentari per obiettivi
        - Obiettivi → strategie specifiche
        """
        collected = session.get("collected_data", {})
        agent_config = session.get("agent_config", {})

        knowledge = {
            "injury": "",
            "training": "",
            "nutrition": ""
        }

        try:
            from src.infrastructure.ai.rag_service import get_rag_service
            rag_service = get_rag_service()

            # === 1. CONOSCENZE INFORTUNIO ===
            pain_locations = collected.get("pain_locations", [])
            if agent_config.get("has_injury") or pain_locations:
                injury_types = []
                for loc in pain_locations:
                    loc_lower = loc.lower() if isinstance(loc, str) else ""
                    if any(x in loc_lower for x in ["schiena", "lombare", "sciatica", "nervo"]):
                        injury_types.append("sciatica")
                    if any(x in loc_lower for x in ["inguine", "pube", "adduttori"]):
                        injury_types.append("pubalgia")
                    if any(x in loc_lower for x in ["spalla"]):
                        injury_types.append("shoulder_impingement")
                    if any(x in loc_lower for x in ["ginocchio"]):
                        injury_types.append("patellar_tendinitis")
                    if any(x in loc_lower for x in ["anca"]):
                        injury_types.append("hip_fai")
                    if any(x in loc_lower for x in ["tallone", "piede"]):
                        injury_types.append("plantar_fasciitis")

                if injury_types:
                    query = f"protocollo riabilitazione {' '.join(set(injury_types))} fase recupero esercizi sicuri"
                    results = rag_service.retrieve_context(query, k=3)
                    if results:
                        parts = ["🏥 PROTOCOLLI RIABILITAZIONE PER IL TUO INFORTUNIO:"]
                        for r in results:
                            parts.append(f"• {r.get('content', '')[:400]}")
                        knowledge["injury"] = "\n".join(parts)

            # === 2. CONOSCENZE ALLENAMENTO ===
            sport_type = agent_config.get("sport_type") or collected.get("sport_type")
            if sport_type:
                # Mappa sport a query specifiche
                sport_queries = {
                    "crossfit": "CrossFit WOD AMRAP EMOM functional fitness workout",
                    "bodybuilding": "bodybuilding ipertrofia split routine muscoli",
                    "powerlifting": "powerlifting forza squat deadlift bench press",
                    "running": "corsa running endurance cardio",
                    "functional": "functional training movimento funzionale",
                    "general_fitness": "fitness generale allenamento base",
                    "rehab_focused": "riabilitazione esercizi terapeutici recupero"
                }

                query = sport_queries.get(sport_type, f"{sport_type} allenamento esercizi")

                # Se ha infortunio, aggiungi contesto riabilitazione
                if agent_config.get("has_injury"):
                    query += " adattato infortunio modifiche sicure"

                results = rag_service.retrieve_context(query, k=3)
                if results:
                    parts = [f"🏋️ PROGRAMMI {sport_type.upper()} PERSONALIZZATI:"]
                    for r in results:
                        parts.append(f"• {r.get('content', '')[:400]}")
                    knowledge["training"] = "\n".join(parts)

            # === 3. CONOSCENZE NUTRIZIONE ===
            nutrition_mode = agent_config.get("nutrition_mode")
            goals = collected.get("goals") or collected.get("primary_goal")

            if nutrition_mode or goals:
                # Mappa obiettivi a query nutrizionali
                goal_nutrition = {
                    "recovery": "nutrizione recupero infortunio anti-infiammatorio proteine",
                    "muscle_gain": "dieta massa muscolare proteine ipertrofia",
                    "weight_loss": "dieta dimagrimento deficit calorico",
                    "strength": "nutrizione forza powerlifting carboidrati",
                    "return_to_sport": "nutrizione sportiva performance recupero"
                }

                query = goal_nutrition.get(goals, "nutrizione sportiva ricette fitness")

                # Aggiungi contesto sport se presente
                if sport_type:
                    query += f" per {sport_type}"

                results = rag_service.retrieve_context(
                    query,
                    k=3,
                    filter_metadata={"category": "nutrition"}
                )
                if results:
                    parts = ["🥗 NUTRIZIONE PERSONALIZZATA PER I TUOI OBIETTIVI:"]
                    for r in results:
                        parts.append(f"• {r.get('content', '')[:400]}")
                    knowledge["nutrition"] = "\n".join(parts)

            return knowledge

        except Exception as e:
            from src.infrastructure.logging import get_logger
            logger = get_logger(__name__)
            logger.warning(f"Failed to get personalized knowledge: {e}")
            return knowledge

    async def start_interview(
        self,
        user_id: str,
        session_id: str,
        user_email: str = None,
        user_name: str = None,
        biometrics: Dict[str, Any] = None,
        initial_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Start a new wizard interview.

        Args:
            user_id: User identifier
            session_id: Session identifier
            user_email: User email (already authenticated)
            user_name: User name if available
            biometrics: Initial biometric data
        """
        session = self._get_session(session_id)
        session["user_id"] = user_id
        session["email"] = user_email
        session["phase"] = InterviewPhase.GREETING

        # Store email in collected_data so we don't ask for it
        if user_email:
            session["collected_data"]["email"] = user_email
        if user_name:
            session["collected_data"]["name"] = user_name

        # Store biometrics
        if biometrics:
            session["collected_data"]["biometrics"] = biometrics
            # Also flatten useful fields
            for k, v in biometrics.items():
                session["collected_data"][k] = v

        # Store initial context (from Wizard UI steps)
        if initial_context:
            session["initial_context"] = initial_context
            # Map frontend names to backend names for better consistency
            mappings = {
                "trainingGoals": "training_goals",
                "lifestyle": "lifestyle",
                "nutritionGoals": "nutrition_goals",
                "foodPreferences": "food_preferences",
                "injury": "injury_details"
            }
            
            for fe_key, be_key in mappings.items():
                if fe_key in initial_context:
                    data = initial_context[fe_key]
                    session["collected_data"][be_key] = data
                    # Also flatten for the agent logic to find fields like 'primary_goal' directly
                    if isinstance(data, dict):
                        for k, v in data.items():
                            session["collected_data"][k] = v

        # CRITICAL: Trigger config update to detect modes from initial data
        self._update_agent_config(session, "", {})

        # Generate greeting - short and direct
        prompt = f"""
{self.SYSTEM_PROMPT}

L'utente si è già registrato con email: {user_email or 'sconosciuta'}
{f'Si chiama: {user_name}' if user_name else ''}
{f'Dati biometrici noti: {biometrics}' if biometrics else ''}
{f'Contesto iniziale: {initial_context}' if initial_context else ''}

ISTRUZIONI PER IL SALUTO:
1. Sii breve e diretto.
2. Salutalo per nome se lo conosci.
3. Se vedi dati importati da Google Fit (googleSyncFields nel contesto), faglielo sapere in modo magico ("Ho già importato il tuo peso da Google Fit!").
4. Non chiedere cose che già vedi qui sopra.

Fase attuale: SALUTO INIZIALE
{self.PHASE_PROMPTS[InterviewPhase.GREETING]}

Genera un saluto BREVE (max 2 frasi) che chiede subito cosa lo porta su IronRep.
NON chiedere email o nome, li hai già!
"""

        response = await self.llm.generate(prompt)

        # Save to history
        session["conversation_history"].append({
            "role": "assistant",
            "content": response,
            "phase": InterviewPhase.GREETING,
            "timestamp": datetime.now().isoformat()
        })

        # Get suggested replies for greeting phase
        suggested_replies = self._get_suggested_replies(InterviewPhase.GREETING, session)

        # Persist session state
        self._save_session(session_id, session)

        return {
            "success": True,
            "session_id": session_id,
            "message": response,
            "phase": InterviewPhase.GREETING,
            "suggested_replies": suggested_replies,
            "completed": False
        }

    async def process_message(
        self,
        session_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Process user message and continue interview.

        Args:
            session_id: Session identifier
            user_message: User's response

        Returns:
            Dict with agent response and interview status
        """
        session = self._get_session(session_id)
        user_id = session.get("user_id", "unknown")

        # Save user message
        session["conversation_history"].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })

        # Extract data from message and store in RAG
        extracted = await self._extract_and_store_data(user_id, user_message, session)

        # Determine next phase
        next_phase = self._determine_next_phase(session)
        session["phase"] = next_phase

        # Check if complete
        if next_phase == InterviewPhase.COMPLETE:
            return await self._finalize_interview(session_id)

        # Generate next question
        response = await self._generate_response(session, next_phase)

        # Save assistant response
        session["conversation_history"].append({
            "role": "assistant",
            "content": response,
            "phase": next_phase,
            "timestamp": datetime.now().isoformat()
        })

        # Generate smart suggested replies based on phase
        suggested_replies = self._get_suggested_replies(next_phase, session)

        # Persist session state after each message
        self._save_session(session_id, session)

        return {
            "success": True,
            "session_id": session_id,
            "message": response,
            "phase": next_phase,
            "extracted_data": extracted,
            "agent_config": session.get("agent_config", {}),
            "collected_data": session.get("collected_data", {}),
            "suggested_replies": suggested_replies,
            "completed": False
        }

    async def _extract_and_store_data(
        self,
        user_id: str,
        message: str,
        session: Dict
    ) -> Dict[str, Any]:
        """Extract structured data using FAST pattern matching (NO LLM call)."""
        import re

        current_phase = session["phase"]
        extracted = {}
        msg_lower = message.lower()

        # First, update agent config with keyword detection (fast)
        self._update_agent_config(session, message, {})

        # === PATTERN MATCHING VELOCE (NO LLM) ===

        # 1. Pain level (1-10)
        pain_match = re.search(r'(\d+)\s*(?:su\s*10|/10|su 10|out of 10)', msg_lower)
        if pain_match:
            extracted["pain_level"] = int(pain_match.group(1))
        elif re.search(r'\b(\d)\b.*(?:dolore|male|intensit)', msg_lower):
            num_match = re.search(r'\b([1-9]|10)\b', msg_lower)
            if num_match:
                extracted["pain_level"] = int(num_match.group(1))

        # 2. Pain locations
        locations = []
        body_parts = {
            "schiena": ["schiena", "lombare", "dorsale", "lombalgia"],
            "ginocchio": ["ginocchio", "ginocchia", "rotula"],
            "spalla": ["spalla", "spalle", "cuffia"],
            "anca": ["anca", "anche", "fai"],
            "collo": ["collo", "cervicale", "cervicali"],
            "polso": ["polso", "polsi"],
            "caviglia": ["caviglia", "caviglie"],
            "gomito": ["gomito", "gomiti"],
        }
        for loc, keywords in body_parts.items():
            if any(kw in msg_lower for kw in keywords):
                locations.append(loc)
        if locations:
            extracted["pain_locations"] = locations

        # 3. Training days
        days_match = re.search(r'(\d+)\s*(?:giorni|volte|x).*(?:settimana|week)', msg_lower)
        if days_match:
            extracted["training_days"] = int(days_match.group(1))

        # 4. Equipment
        if any(w in msg_lower for w in ["palestra completa", "gym", "palestra attrezzata"]):
            extracted["equipment"] = "palestra_completa"
        elif any(w in msg_lower for w in ["casa", "home", "domestico"]):
            extracted["equipment"] = "home_gym"
        elif any(w in msg_lower for w in ["corpo libero", "bodyweight", "calisthenics"]):
            extracted["equipment"] = "bodyweight"

        # 5. Goals
        goal_map = {
            "massa": ["massa", "muscoli", "ipertrofia", "bulk"],
            "dimagrimento": ["dimagr", "peso", "grasso", "cut", "definizione"],
            "forza": ["forza", "strength", "forte"],
            "recupero": ["recuper", "infortunio", "riabilit", "guarire"],
            "performance": ["performance", "prestazione", "competizione", "gara"]
        }
        for goal, keywords in goal_map.items():
            if any(kw in msg_lower for kw in keywords):
                extracted["goals"] = goal
                break

        # Merge with session
        session["collected_data"].update(extracted)

        # === RECUPERA CONOSCENZE PERSONALIZZATE DAL KNOWLEDGE BASE ===
        personalized_knowledge = await self._get_personalized_knowledge(session)
        session["personalized_knowledge"] = personalized_knowledge

        # Store extracted data in RAG
        category_mapping = {
            InterviewPhase.PAIN_ASSESSMENT: "pain",
            InterviewPhase.INJURY_HISTORY: "medical",
            InterviewPhase.GOALS: "goal",
            InterviewPhase.EQUIPMENT: "equipment",
            InterviewPhase.PREFERENCES: "preference",
            InterviewPhase.NUTRITION_DETAILS: "preference"  # CRITICAL: Food preferences go to RAG
        }

        category = category_mapping.get(current_phase, "history")

        # Store the raw message with context in ChromaDB
        if message.strip():
            self.rag.store_context(
                user_id=user_id,
                text=message,
                category=category,
                metadata={
                    "phase": current_phase.value if hasattr(current_phase, 'value') else str(current_phase),
                    "extracted": extracted
                }
            )

            logger.info(f"Stored wizard response in RAG - User: {user_id}, Phase: {current_phase}, Category: {category}, Extracted: {extracted}")

        return extracted

    def _update_agent_config(self, session: Dict, message: str, extracted: Dict) -> None:
        """
        Update agent configuration based on user responses.

        SMART DETECTION - works in ANY phase:
        - Detects injury/pain keywords → medical_mode = INJURY_RECOVERY
        - Detects sport type → coach_mode
        - Detects nutrition preferences → nutrition_mode
        - Detects goals, equipment, preferences
        """
        agent_config = session.get("agent_config", {})
        collected = session.get("collected_data", {})
        message_lower = message.lower()

        # ===== INJURY DETECTION (any phase) =====
        # Keywords che indicano SI un infortunio
        injury_keywords = [
            "infortunio", "dolore", "male", "infortunato", "fa male", "mi fa male",
            "injury", "pain", "hurt", "problema", "fastidio", "sciatica",
            "ernia", "lombalgia", "cervicale", "tendinite", "strappo",
            "distorsione", "frattura", "operazione", "intervento",
            "pubalgia", "nervo", "schiena", "inguine", "anca", "tallone",
            "gamba", "ginocchio", "spalla", "tira", "schiocca", "blocca",
            "protrusione", "bulging", "disco", "artrite", "artrosi"
        ]
        # Keywords che indicano NO infortunio (DEVE essere controllato PRIMA!)
        no_injury_keywords = ["non ho dolore", "sto bene", "nessun infortunio", "nessun dolore",
                              "tutto ok", "no infortunio", "no, nessun", "no dolore", "senza problemi"]

        # PRIMA controlla se dice NO infortunio (altrimenti "nessun infortunio" matcha "infortunio")
        if any(kw in message_lower for kw in no_injury_keywords):
            agent_config["has_injury"] = False
            agent_config["medical_mode"] = MedicalMode.WELLNESS_TIPS
        elif any(kw in message_lower for kw in injury_keywords):
            agent_config["has_injury"] = True
            agent_config["medical_mode"] = MedicalMode.INJURY_RECOVERY

            # ===== ESTRAI TIPO SPECIFICO DI INFORTUNIO =====
            injury_types = []
            pain_locs = []

            # Diagnosi specifiche
            if "ernia" in message_lower:
                injury_types.append("ernia")
                # Cerca livello spinale (L4-L5, L5-S1, etc)
                import re
                level_match = re.search(r'[lL]\d[\s\-]*[sS]?\d?', message_lower)
                if level_match:
                    injury_types.append(f"livello {level_match.group().upper()}")
            if "sciatica" in message_lower or "nervo sciatico" in message_lower:
                injury_types.append("sciatica")
                pain_locs.append("nervo sciatico")
            if "pubalgia" in message_lower:
                injury_types.append("pubalgia")
                pain_locs.append("inguine")
            if "protrusione" in message_lower or "bulging" in message_lower:
                injury_types.append("protrusione discale")
            if "tendinite" in message_lower or "tendinopatia" in message_lower:
                injury_types.append("tendinite")
            if "strappo" in message_lower:
                injury_types.append("strappo muscolare")
            if "artrite" in message_lower or "artrosi" in message_lower:
                injury_types.append("artrite/artrosi")

            # Localizzazione
            if "schiena" in message_lower or "lombare" in message_lower or "lombalgia" in message_lower:
                pain_locs.append("zona lombare")
            if "cervicale" in message_lower or "collo" in message_lower:
                pain_locs.append("cervicale")
            if "gamba" in message_lower:
                pain_locs.append("gamba")
            if "anca" in message_lower:
                pain_locs.append("anca")
            if "tallone" in message_lower or "piede" in message_lower:
                pain_locs.append("piede/tallone")
            if "ginocchio" in message_lower:
                pain_locs.append("ginocchio")
            if "spalla" in message_lower:
                pain_locs.append("spalla")
            if "polso" in message_lower:
                pain_locs.append("polso")

            # Salva
            if injury_types:
                collected["injury_type"] = ", ".join(injury_types)
            if pain_locs:
                collected["pain_locations"] = pain_locs

        # ===== SPORT DETECTION (any phase) =====
        sport_mapping = {
            "crossfit": CoachMode.CROSSFIT,
            "cross fit": CoachMode.CROSSFIT,
            "wod": CoachMode.CROSSFIT,
            "amrap": CoachMode.CROSSFIT,
            "bodybuilding": CoachMode.BODYBUILDING,
            "palestra": CoachMode.BODYBUILDING,
            "body building": CoachMode.BODYBUILDING,
            "ipertrofia": CoachMode.BODYBUILDING,
            "massa": CoachMode.BODYBUILDING,
            "powerlifting": CoachMode.POWERLIFTING,
            "power lifting": CoachMode.POWERLIFTING,
            "forza pura": CoachMode.POWERLIFTING,
            "stacco": CoachMode.POWERLIFTING,
            "running": CoachMode.RUNNING,
            "corsa": CoachMode.RUNNING,
            "correre": CoachMode.RUNNING,
            "maratona": CoachMode.RUNNING,
            "functional": CoachMode.FUNCTIONAL,
            "funzionale": CoachMode.FUNCTIONAL,
            "fitness": CoachMode.GENERAL_FITNESS,
            "generale": CoachMode.GENERAL_FITNESS,
            "dimagrire": CoachMode.GENERAL_FITNESS,
            "perdere peso": CoachMode.GENERAL_FITNESS,
            "tenermi in forma": CoachMode.GENERAL_FITNESS,
            "riabilitazione": CoachMode.REHAB_FOCUSED,
            "recupero": CoachMode.REHAB_FOCUSED,
            "rehab": CoachMode.REHAB_FOCUSED
        }

        for keyword, mode in sport_mapping.items():
            if keyword in message_lower:
                agent_config["coach_mode"] = mode
                agent_config["sport_type"] = mode.value
                collected["sport_type"] = mode.value
                break

        # ===== NUTRITION DETECTION (any phase) =====
        # Check for positive nutrition request first (order matters!)
        if any(kw in message_lower for kw in ["piano", "dieta completo", "dieta strutturata", "piano completo", "macro", "pasti pianificati", "dieta seria", "voglio dieta", "voglio piano"]):
            # When user says "sì voglio piano..." or "piano dieta" → FULL_DIET_PLAN
            agent_config["nutrition_mode"] = NutritionMode.FULL_DIET_PLAN
        elif any(kw in message_lower for kw in ["ricette", "idee", "solo ricette", "cosa mangiare"]):
            agent_config["nutrition_mode"] = NutritionMode.RECIPES_ONLY
        elif any(kw in message_lower for kw in ["consigli", "tips", "suggerimenti"]):
            agent_config["nutrition_mode"] = NutritionMode.TIPS_TRACKING
        elif any(kw in message_lower for kw in ["no dieta", "gestisco io", "da solo", "non mi serve", "no nutrizione"]):
            agent_config["nutrition_mode"] = NutritionMode.DISABLED

        # ===== GOALS DETECTION (any phase) =====
        goal_mapping = {
            "recupero": "recovery",
            "recuperare": "recovery",
            "guarire": "recovery",
            "dall'infortunio": "recovery",
            "forza": "strength",
            "più forte": "strength",
            "massa": "muscle_gain",
            "muscoli": "muscle_gain",
            "ipertrofia": "muscle_gain",
            "dimagrire": "weight_loss",
            "perdere peso": "weight_loss",
            "definizione": "weight_loss",
            "tornare a": "return_to_sport",
            "sport": "return_to_sport",
            "competizione": "return_to_sport",
            "mobilità": "mobility",
            "flessibilità": "mobility"
        }

        for keyword, goal in goal_mapping.items():
            if keyword in message_lower:
                collected["goals"] = goal
                collected["primary_goal"] = goal
                break

        # Detect "allenarmi per recuperare" pattern
        if "allenar" in message_lower and ("recuper" in message_lower or "infortunio" in message_lower):
            collected["goals"] = "recovery"
            collected["primary_goal"] = "recovery"

        # ===== EQUIPMENT & LOCATION DETECTION (any phase) =====
        equipment_found = []
        training_location = None
        equipment_keywords = {
            "palestra": ("full_gym", "gym"),
            "gym": ("full_gym", "gym"),
            "box": ("crossfit_box", "crossfit_box"),
            "casa": ("home", "home"),
            "appartamento": ("home", "home"),
            "garage": ("home", "home_gym"),
            "bilanciere": ("barbell", None),
            "manubri": ("dumbbells", None),
            "kettlebell": ("kettlebells", None),
            "corpo libero": ("bodyweight", None),
            "calisthenics": ("bodyweight", None),
            "niente": ("minimal", None),
            "pochi attrezzi": ("minimal", None),
            "tutto": ("full_equipment", None),
            "completa": ("full_equipment", None)
        }

        for keyword, (equip, loc) in equipment_keywords.items():
            if keyword in message_lower:
                equipment_found.append(equip)
                if loc:
                    training_location = loc

        if equipment_found:
            collected["equipment"] = list(set(equipment_found))
        if training_location:
            collected["training_location"] = training_location

        # ===== PAIN LEVEL DETECTION =====
        import re
        pain_match = re.search(r'(?:dolore|pain)\s*(?:di|al|level|livello)?\s*(\d+)', message_lower)
        if not pain_match:
            pain_match = re.search(r'(\d+)\s*(?:su|out of|\/)\s*10', message_lower)
        if pain_match:
            pain_level = int(pain_match.group(1))
            if pain_level <= 10:
                collected["pain_level"] = pain_level

        # ===== INJURY DURATION DETECTION =====
        duration_injury_match = re.search(r'(?:da|for)\s*(\d+)\s*(mesi|settimane|anni|months|weeks|years)', message_lower)
        if duration_injury_match:
            duration_val = int(duration_injury_match.group(1))
            duration_unit = duration_injury_match.group(2)
            collected["injury_duration"] = f"{duration_val} {duration_unit}"

        # ===== NUTRITION GOAL DETECTION =====
        if any(kw in message_lower for kw in ["deficit", "perdere", "dimagrire", "calare", "grasso"]):
            collected["nutrition_goal"] = "deficit"
        elif any(kw in message_lower for kw in ["surplus", "bulk", "massa", "aumentare peso", "mettere peso"]):
            collected["nutrition_goal"] = "surplus"
        elif any(kw in message_lower for kw in ["mantenimento", "maintenance", "mantenere", "ricomposizione"]):
            collected["nutrition_goal"] = "maintenance"

        # ===== ALLERGIES & FOOD RESTRICTIONS =====
        allergies_found = []
        disliked_foods = []

        allergy_keywords = {
            "lattosio": "lactose",
            "latte": "dairy",
            "glutine": "gluten",
            "celiaco": "gluten",
            "frutta secca": "nuts",
            "noci": "nuts",
            "arachidi": "peanuts",
            "crostacei": "shellfish",
            "uova": "eggs",
            "soia": "soy"
        }

        for keyword, allergy in allergy_keywords.items():
            if keyword in message_lower and ("allergia" in message_lower or "intollerante" in message_lower or "non posso" in message_lower or "evito" in message_lower or "niente" in message_lower):
                allergies_found.append(allergy)

        # Disliked foods
        dislike_patterns = [
            r"non mi piace[a-z]*\s+(?:il\s+|la\s+|lo\s+|l\')?(\w+)",
            r"odio\s+(?:il\s+|la\s+|lo\s+|l\')?(\w+)",
            r"no\s+(\w+)",
            r"evito\s+(?:il\s+|la\s+|lo\s+|l\')?(\w+)"
        ]

        for pattern in dislike_patterns:
            matches = re.findall(pattern, message_lower)
            for match in matches:
                if match not in ["dieta", "nutrizione", "infortunio", "dolore"]:
                    disliked_foods.append(match)

        if allergies_found:
            collected["allergies"] = list(set(allergies_found))
        if disliked_foods:
            collected["disliked_foods"] = list(set(disliked_foods))

        # ===== PREFERENCES DETECTION (any phase) =====
        # Days per week
        days_match = re.search(r'(\d+)\s*(giorni|volte|days)', message_lower)
        if days_match:
            collected["training_days"] = int(days_match.group(1))
            if "preferences" not in collected:
                collected["preferences"] = {}
            collected["preferences"]["days_per_week"] = int(days_match.group(1))

        # Duration
        duration_match = re.search(r'(\d+)\s*(minuti|min|ore|hour)', message_lower)
        if duration_match:
            duration = int(duration_match.group(1))
            if "ore" in duration_match.group(2) or "hour" in duration_match.group(2):
                duration *= 60
            collected["session_duration"] = duration
            if "preferences" not in collected:
                collected["preferences"] = {}
            collected["preferences"]["duration"] = duration

        # Update session
        session["agent_config"] = agent_config
        session["collected_data"] = collected

    def _get_suggested_replies(self, phase: InterviewPhase, session: Dict) -> List[Dict[str, str]]:
        """
        Restituisce suggerimenti di risposta INTELLIGENTI basati sulla fase corrente.
        Questi vengono mostrati come pulsanti nel frontend.
        """
        collected = session.get("collected_data", {})
        agent_config = session.get("agent_config", {})

        # Mapping fase → suggerimenti pertinenti
        phase_replies = {
            InterviewPhase.GREETING: [
                {"label": "Sì, ho un infortunio", "value": "sì, ho un infortunio attivo", "icon": "injury", "color": "red"},
                {"label": "No, tutto ok", "value": "no, nessun infortunio, sto bene", "icon": "ok", "color": "green"},
            ],
            InterviewPhase.PAIN_ASSESSMENT: [
                {"label": "Schiena/Lombare", "value": "dolore alla schiena zona lombare", "icon": "back", "color": "red"},
                {"label": "Ginocchio", "value": "dolore al ginocchio", "icon": "knee", "color": "orange"},
                {"label": "Spalla", "value": "dolore alla spalla", "icon": "shoulder", "color": "orange"},
                {"label": "Altro", "value": "dolore in altra zona", "icon": "other", "color": "gray"},
            ],
            InterviewPhase.SPORT_SELECTION: [
                {"label": "CrossFit", "value": "faccio CrossFit", "icon": "crossfit", "color": "orange"},
                {"label": "Palestra/Bodybuilding", "value": "mi alleno in palestra, bodybuilding", "icon": "gym", "color": "blue"},
                {"label": "Corsa/Running", "value": "faccio corsa, running", "icon": "running", "color": "green"},
                {"label": "Fitness Generale", "value": "fitness generale per stare in forma", "icon": "fitness", "color": "purple"},
            ],
            InterviewPhase.EQUIPMENT: [
                {"label": "Palestra Completa", "value": "palestra completa con tutti gli attrezzi", "icon": "gym", "color": "blue"},
                {"label": "Home Gym", "value": "mi alleno a casa con manubri e bilanciere", "icon": "home", "color": "green"},
                {"label": "Corpo Libero", "value": "solo corpo libero, calisthenics", "icon": "bodyweight", "color": "purple"},
            ],
            InterviewPhase.PREFERENCES: [
                {"label": "3 giorni", "value": "mi alleno 3 giorni a settimana, 45-60 minuti", "icon": "days", "color": "blue"},
                {"label": "4 giorni", "value": "4 giorni a settimana, circa 60 minuti", "icon": "days", "color": "green"},
                {"label": "5+ giorni", "value": "5 o più giorni, 60-90 minuti per sessione", "icon": "days", "color": "orange"},
            ],
            InterviewPhase.NUTRITION_MODE: [
                {"label": "Perdere peso", "value": "sì, voglio perdere peso, deficit calorico", "icon": "deficit", "color": "green"},
                {"label": "Mettere massa", "value": "sì, voglio mettere massa muscolare, surplus", "icon": "surplus", "color": "orange"},
                {"label": "Mantenimento", "value": "sì, mantenimento del peso attuale", "icon": "maintain", "color": "blue"},
                {"label": "No grazie", "value": "no, gestisco io la nutrizione", "icon": "no", "color": "gray"},
            ],
            InterviewPhase.NUTRITION_DETAILS: [
                {"label": "✓ Mangio tutto", "value": "nessuna allergia, nessun cibo da evitare, mangio di tutto", "icon": "ok", "color": "green"},
                {"label": "Intolleranze", "value": "ho intolleranze alimentari", "icon": "allergy", "color": "orange"},
                {"label": "Preferenze specifiche", "value": "ho preferenze alimentari da comunicare", "icon": "preferences", "color": "blue"},
            ],
            InterviewPhase.SUMMARY: [
                {"label": "✓ Confermo tutto!", "value": "sì, confermo tutto, è corretto", "icon": "confirm", "color": "green"},
                {"label": "Modifica qualcosa", "value": "vorrei modificare alcune informazioni", "icon": "edit", "color": "gray"},
            ],
        }

        return phase_replies.get(phase, [])

    def _determine_next_phase(self, session: Dict) -> InterviewPhase:
        """
        FLUSSO COMPLETO v3:

        1. GREETING → chiede infortunio (sì/no)
        2. PAIN_ASSESSMENT → SE ha infortunio, chiede dettagli completi
        3. SPORT_SELECTION → che sport + obiettivo
        4. EQUIPMENT → dove ti alleni + attrezzatura
        5. PREFERENCES → giorni + durata sessione
        6. NUTRITION_MODE → vuole nutrizione? + obiettivo (deficit/surplus/maint)
        7. NUTRITION_DETAILS → SE vuole nutrizione, chiedi allergie/preferenze
        8. SUMMARY → riepilogo completo e conferma
        """
        collected = session["collected_data"]
        current = session["phase"]
        agent_config = session.get("agent_config", {})

        # Data checks
        has_injury = agent_config.get("has_injury", False)
        # Check if injury details were collected via UI or previous chat
        has_injury_details = collected.get("injury_diagnosis") or collected.get("injury_type") or collected.get("pain_level")
        
        has_goals = collected.get("goals") or collected.get("primary_goal")
        has_equipment = collected.get("equipment") or collected.get("equipment_available") or collected.get("training_location")
        has_preferences = (collected.get("training_days") or collected.get("available_days")) and \
                          (collected.get("session_duration") or collected.get("session_duration_minutes"))
        
        nutrition_mode = agent_config.get("nutrition_mode")
        nutrition_enabled = nutrition_mode and nutrition_mode not in [NutritionMode.DISABLED, "disabled"]
        has_nutrition_details = collected.get("allergies") or collected.get("disliked_foods") or \
                                collected.get("diet_type") or collected.get("favorite_foods")

        # ===== FLUSSO COMPLETO CON SMART SKIP =====
        
        # 1. GREETING -> decide se chiedere infortuni o saltare
        if current == InterviewPhase.GREETING:
            if has_injury:
                if not has_injury_details:
                    return InterviewPhase.PAIN_ASSESSMENT
                return InterviewPhase.SPORT_SELECTION
            else:
                if agent_config.get("has_injury") is None:
                     return InterviewPhase.GREETING
                return InterviewPhase.SPORT_SELECTION

        # 2. PAIN_ASSESSMENT -> decide se saltare
        if current == InterviewPhase.PAIN_ASSESSMENT or (current == InterviewPhase.GREETING and has_injury):
            if has_injury_details:
                return InterviewPhase.SPORT_SELECTION
            return InterviewPhase.PAIN_ASSESSMENT

        # 3. SPORT_SELECTION -> decide se saltare
        if current == InterviewPhase.SPORT_SELECTION:
            if agent_config.get("sport_type") and has_goals:
                return InterviewPhase.EQUIPMENT
            return InterviewPhase.SPORT_SELECTION

        # 4. EQUIPMENT -> decide se saltare
        if current == InterviewPhase.EQUIPMENT:
            if has_equipment:
                return InterviewPhase.PREFERENCES
            return InterviewPhase.EQUIPMENT

        # 5. PREFERENCES -> decide se saltare
        if current == InterviewPhase.PREFERENCES:
            if has_preferences:
                return InterviewPhase.NUTRITION_MODE
            return InterviewPhase.PREFERENCES

        # 6. NUTRITION_MODE -> decide se saltare
        if current == InterviewPhase.NUTRITION_MODE:
            if nutrition_mode and nutrition_mode != "disabled":
                if has_nutrition_details:
                    return InterviewPhase.SUMMARY
                return InterviewPhase.NUTRITION_DETAILS
            elif nutrition_mode == "disabled" or nutrition_mode is not None:
                return InterviewPhase.SUMMARY
            return InterviewPhase.NUTRITION_MODE
        # NUTRITION_DETAILS → verifica se ha risposto alle allergie/intolleranze prima di andare al summary
        if current == InterviewPhase.NUTRITION_DETAILS:
            # Check if user mentioned intolerances/allergies but didn't specify which ones
            last_message = session["conversation_history"][-1]["content"] if session["conversation_history"] else ""
            last_msg_lower = last_message.lower()

            # Check if user is skipping allergy specification
            user_skipping = any(kw in last_msg_lower for kw in [
                "nessuna", "nessun", "no allergie", "no intolleranze",
                "passo", "skip", "non ho", "non ne ho"
            ])

            # If user is skipping, clear the clarification flag and proceed
            if user_skipping and session.get("needs_allergy_clarification"):
                session["needs_allergy_clarification"] = False
                return InterviewPhase.SUMMARY

            # Vague intolerance mentions that need clarification
            has_vague_intolerance = any(kw in last_msg_lower for kw in [
                "ho intolleranze", "intolleranze alimentari", "alcune intolleranze",
                "ho allergie", "allergie alimentari", "alcune allergie"
            ])

            # Check if specific intolerances were actually extracted
            has_specific_allergies = bool(collected.get("allergies"))

            # If they mentioned intolerances vaguely but we didn't extract specifics, stay in NUTRITION_DETAILS
            if has_vague_intolerance and not has_specific_allergies and not session.get("needs_allergy_clarification"):
                # Mark that we need to ask for clarification (will be handled in response generation)
                session["needs_allergy_clarification"] = True
                return InterviewPhase.NUTRITION_DETAILS

            # Otherwise proceed to summary
            session["needs_allergy_clarification"] = False
            return InterviewPhase.SUMMARY

        # SUMMARY → completo
        if current == InterviewPhase.SUMMARY:
            return InterviewPhase.COMPLETE

        return InterviewPhase.COMPLETE

    async def _generate_response(self, session: Dict, phase: InterviewPhase) -> str:
        """Generate agent response using few-shot + RAG context."""
        collected = session["collected_data"]
        agent_config = session.get("agent_config", {})

        # === SPECIAL CASE: Allergy Clarification ===
        if session.get("needs_allergy_clarification"):
            return (
                "Capisco! Puoi specificare quali intolleranze o allergie alimentari hai? "
                "Ad esempio: lattosio, glutine, frutta secca, crostacei, uova, soia, ecc.\n\n"
                "Se non hai intolleranze specifiche o preferisci non specificarle ora, "
                "scrivi 'nessuna' o 'passo'."
            )

        # === 1. CONTESTO CONVERSAZIONE (ultimi 4 messaggi) ===
        history = session["conversation_history"][-4:]
        history_text = "\n".join([
            f"{'Utente' if m['role'] == 'user' else 'Wizard'}: {m['content']}"
            for m in history
        ])

        # === 2. DATI GIÀ RACCOLTI + COSE DA NON CHIEDERE ===
        facts = []
        do_not_ask = []

        if agent_config.get("has_injury"):
            injury_desc = collected.get("injury_type") or collected.get("pain_locations") or "sì"
            facts.append(f"🏥 Infortunio: {injury_desc}")
            do_not_ask.append("se ha infortunio")
        if collected.get("injury_type"):
            do_not_ask.append("tipo/dettagli infortunio")
        if collected.get("pain_locations"):
            do_not_ask.append("localizzazione dolore")
        if agent_config.get("sport_type"):
            facts.append(f"🏋️ Sport: {agent_config.get('sport_type')}")
            do_not_ask.append("tipo di sport/allenamento")
        if collected.get("training_days"):
            facts.append(f"📅 Giorni: {collected.get('training_days')}/settimana")
            do_not_ask.append("giorni/settimana")
        if agent_config.get("nutrition_mode") and agent_config.get("nutrition_mode") != NutritionMode.TIPS_TRACKING:
            facts.append(f"🍎 Nutrizione: {agent_config.get('nutrition_mode')}")
            do_not_ask.append("supporto nutrizionale")
            do_not_ask.append("giorni/settimana")

        facts_text = " | ".join(facts) if facts else "Nessuno"
        do_not_ask_text = ", ".join(do_not_ask) if do_not_ask else ""

        # === 3. CONTESTO RAG (se presente) ===
        rag_context = ""
        pk = session.get("personalized_knowledge", {})
        if pk.get("injury"):
            rag_context += f"\n📋 Info infortunio: {pk['injury'][:200]}"
        if pk.get("training"):
            rag_context += f"\n📋 Info allenamento: {pk['training'][:200]}"

        # === 4. PROMPT COMPATTO CON FEW-SHOT ===
        prompt = f"""{self.SYSTEM_PROMPT}

{self.FEW_SHOT_EXAMPLES}

=== CONVERSAZIONE ATTUALE ===
{history_text}

DATI GIÀ RACCOLTI: {facts_text}
{f"⛔ NON CHIEDERE: {do_not_ask_text}" if do_not_ask_text else ""}
{rag_context}

FASE: {phase.value}
ISTRUZIONI: {self.PHASE_PROMPTS.get(phase, "Fai la prossima domanda logica.")}

Rispondi come Wizard (MAX 2 frasi, 1 domanda, NON ripetere domande già fatte):"""

        return await self.llm.generate(prompt)

    async def _finalize_interview(self, session_id: str) -> Dict[str, Any]:
        """
        Finalize the interview, create user, and initialize all agents.

        This is the critical handoff point where:
        1. User is created in DB with collected data
        2. AgentOrchestrator initializes Medical, Coach, Nutrition agents
        3. Initial plans are generated
        """
        session = self._get_session(session_id)
        user_id = session.get("user_id")
        collected = session["collected_data"]

        # Generate summary message with agent config
        agent_config = session.get("agent_config", {})
        collected_summary = "\n".join([
            f"- {k}: {v}" for k, v in collected.items()
        ])

        # Build agent activation summary
        agent_summary_parts = []
        medical_mode = agent_config.get("medical_mode")
        if medical_mode == MedicalMode.INJURY_RECOVERY or medical_mode == "injury_recovery":
            agent_summary_parts.append("Medico: pronto per il tuo recupero")
        elif medical_mode != MedicalMode.DISABLED and medical_mode != "disabled":
            agent_summary_parts.append("Medico: disponibile per consigli benessere")

        coach_mode = agent_config.get("coach_mode") or agent_config.get("sport_type")
        if coach_mode:
            sport_name = coach_mode.value if isinstance(coach_mode, CoachMode) else str(coach_mode).replace("_", " ").title()
            agent_summary_parts.append(f"Coach: specializzato in {sport_name}")

        nutrition_mode = agent_config.get("nutrition_mode")
        if nutrition_mode == NutritionMode.FULL_DIET_PLAN or nutrition_mode == "full_diet_plan":
            agent_summary_parts.append("Nutrizionista: piano dieta completo")
        elif nutrition_mode == NutritionMode.RECIPES_ONLY or nutrition_mode == "recipes_only":
            agent_summary_parts.append("Nutrizionista: ricette personalizzate")
        elif nutrition_mode != NutritionMode.DISABLED and nutrition_mode != "disabled":
            agent_summary_parts.append("Nutrizionista: consigli e tracking")

        agent_summary = "\n".join(agent_summary_parts) if agent_summary_parts else "Tutti gli agenti attivi"

        summary_prompt = f"""
Genera un riepilogo finale dell'intervista di onboarding.

Dati raccolti:
{collected_summary}

Configurazione Agenti:
{agent_summary}

Crea un messaggio che:
1. Ringrazia l'utente
2. Riepiloga le informazioni chiave raccolte
3. Conferma quali agenti sono stati attivati e come li userà
4. Ricorda che tutti gli agenti restano sempre disponibili se cambia idea
5. Invita a iniziare il percorso

Sii caloroso e motivante.
"""

        summary_message = await self.llm.generate(summary_prompt)

        # Store final summary in RAG
        self.rag.store_context(
            user_id=user_id,
            text=f"Riepilogo onboarding: {collected_summary}",
            category="history",
            metadata={
                "type": "onboarding_summary",
                "collected_data": collected
            }
        )

        logger.info(f"📋 FINALIZING WIZARD - Collected Data Keys: {list(collected.keys())}")
        logger.info(f"📋 Agent Config: {agent_config}")

        # Create/Update User in DB if repository available
        user_created = False
        if self.user_repository:
            try:
                user_data = self._prepare_user_data(collected, session)
                logger.info(f"📝 Prepared user data with {len(user_data)} fields: {list(user_data.keys())}")
                logger.info(f"🍎 Food data being saved: allergies={user_data.get('allergies')}, disliked={user_data.get('disliked_foods')}")

                user = await self._create_or_update_user(user_data)
                user_id = str(user.id)
                user_created = True
                logger.info(f"✅ User created/updated: {user_id} with is_onboarded=True")
            except Exception as e:
                logger.error(f"❌ Failed to create user: {e}", exc_info=True)

        # Initialize all agents via Orchestrator (respecting user's choices)
        initialization_result = None
        agent_config = session.get("agent_config", {})

        if self.orchestrator and user_id:
            try:
                initialization_result = await self.orchestrator.initialize_new_user(
                    user_id=user_id,
                    user_context=collected,
                    agent_config=agent_config  # Pass modular config
                )
                logger.info(f"Agents initialized for user {user_id} with config: {agent_config}")
            except Exception as e:
                logger.error(f"Failed to initialize agents: {e}")

        # Mark session as completed in DB
        if self.session_repository:
            try:
                self.session_repository.complete_session(session_id)
            except Exception as e:
                logger.warning(f"Failed to mark session complete in DB: {e}")

        return {
            "success": True,
            "session_id": session_id,
            "message": summary_message,
            "phase": InterviewPhase.COMPLETE,
            "completed": True,
            "collected_data": collected,
            "agent_config": agent_config,  # Include in response
            "user_created": user_created,
            "user_id": user_id,
            "initialization": initialization_result
        }

    def _prepare_user_data(self, collected: Dict[str, Any], session: Dict) -> Dict[str, Any]:
        """Prepare user data from collected wizard responses."""
        agent_config = session.get("agent_config", {})

        # Extract training days properly from multiple possible sources
        training_days_value = (
            collected.get("training_days") or
            collected.get("preferences", {}).get("days_per_week") or
            (collected.get("training_days") if isinstance(collected.get("training_days"), int) else None) or
            3
        )

        # Extract session duration
        session_duration_value = (
            collected.get("session_duration") or
            collected.get("preferences", {}).get("duration") or
            60
        )

        # Extract equipment properly - handle both list and string
        equipment_value = collected.get("equipment", [])
        if isinstance(equipment_value, str):
            equipment_value = [equipment_value]
        elif not isinstance(equipment_value, list):
            equipment_value = []

        return {
            "email": session.get("email") or collected.get("email", f"wizard_{session.get('user_id', 'unknown')}@ironrep.local"),
            "name": collected.get("name", "Utente"),
            "age": collected.get("age"),
            "weight_kg": collected.get("weight_kg"),
            "height_cm": collected.get("height_cm"),
            "sex": collected.get("sex"),
            "injury_date": collected.get("injury_date"),
            "diagnosis": collected.get("injury_type") or collected.get("diagnosis", ""),
            "injury_description": collected.get("injury_description", ""),
            "pain_locations": collected.get("pain_locations", []),
            "pain_level": collected.get("pain_level", 0) if agent_config.get("has_injury") else 0,
            "primary_goal": collected.get("goals") or collected.get("primary_goal"),
            "goals_description": collected.get("goals_description", ""),
            "equipment_available": equipment_value,
            "preferred_training_time": collected.get("preferred_training_time") or collected.get("preferences", {}).get("time", "morning"),
            "session_duration_minutes": session_duration_value,
            "training_days": training_days_value,
            "nutrition_goal": collected.get("nutrition_goal", "maintenance"),
            "diet_type": collected.get("diet_type", "balanced"),
            "activity_level": collected.get("activity_level", "moderate"),
            "training_location": collected.get("training_location"),
            # Food preferences and restrictions
            "allergies": collected.get("allergies", []),
            "disliked_foods": collected.get("disliked_foods", []),
            "favorite_foods": collected.get("favorite_foods", []),
            "is_onboarded": True,
            # Modular Agent Configuration
            "medical_mode": agent_config.get("medical_mode", MedicalMode.WELLNESS_TIPS).value if isinstance(agent_config.get("medical_mode"), MedicalMode) else agent_config.get("medical_mode", "wellness_tips"),
            "coach_mode": agent_config.get("coach_mode", CoachMode.GENERAL_FITNESS).value if isinstance(agent_config.get("coach_mode"), CoachMode) else agent_config.get("coach_mode", "general_fitness"),
            "nutrition_mode": agent_config.get("nutrition_mode", NutritionMode.TIPS_TRACKING).value if isinstance(agent_config.get("nutrition_mode"), NutritionMode) else agent_config.get("nutrition_mode", "tips_tracking"),
            "sport_type": agent_config.get("sport_type"),
            "has_injury": agent_config.get("has_injury", False),
            # CRITICAL FIX: Save nutrition preferences from wizard
            "allergies": collected.get("allergies", []),
            "disliked_foods": collected.get("disliked_foods", []),
            "favorite_foods": collected.get("favorite_foods", [])
        }

    async def _create_or_update_user(self, user_data: Dict[str, Any]):
        """Create or update user in database with ALL collected data."""
        from src.domain.entities.user import User, Sex
        from datetime import datetime

        # Check if user exists
        existing = self.user_repository.get_by_email(user_data["email"])

        if existing:
            # Update existing user with ALL fields from wizard
            for key, value in user_data.items():
                if value is not None and hasattr(existing, key):
                    # Special handling for lists - don't overwrite with empty
                    if isinstance(value, list) and len(value) == 0:
                        continue
                    setattr(existing, key, value)
            existing.is_onboarded = True
            existing.updated_at = datetime.now()

            logger.info(f"Updated existing user {existing.id} with wizard data: {list(user_data.keys())}")
            return self.user_repository.save(existing)

        # Create new user with ALL collected fields
        user = User(
            email=user_data["email"],
            name=user_data.get("name", "Utente"),
            age=user_data.get("age"),
            weight_kg=user_data.get("weight_kg"),
            height_cm=user_data.get("height_cm"),
            sex=Sex(user_data["sex"]) if user_data.get("sex") else None,
            injury_date=datetime.fromisoformat(user_data["injury_date"]) if user_data.get("injury_date") and isinstance(user_data["injury_date"], str) else user_data.get("injury_date"),
            diagnosis=user_data.get("diagnosis", ""),
            injury_description=user_data.get("injury_description", ""),
            pain_locations=user_data.get("pain_locations", []),
            primary_goal=user_data.get("primary_goal"),
            goals_description=user_data.get("goals_description", ""),
            equipment_available=user_data.get("equipment_available", []),
            preferred_training_time=user_data.get("preferred_training_time", "morning"),
            session_duration_minutes=user_data.get("session_duration_minutes", 60),
            is_onboarded=True,
            program_start_date=datetime.now()
        )

        logger.info(f"Created new user from wizard with data: {list(user_data.keys())}")
        return self.user_repository.save(user)

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status of interview session."""
        session = self._get_session(session_id)

        return {
            "session_id": session_id,
            "phase": session["phase"],
            "collected_data": session["collected_data"],
            "message_count": len(session["conversation_history"]),
            "started_at": session.get("started_at"),
            "completed": session["phase"] == InterviewPhase.COMPLETE
        }
