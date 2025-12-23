# 📋 IronRep - TODO List Completa

> Stato attuale: ✅ 100% COMPLETATO
> Ultimo aggiornamento: 25 Nov 2025 - CONSEGNA FINALE

---

## 🔴 PRIORITÀ ALTA - Architettura Core Mancante

### 1. Wizard Agent (Interviewer) - ✅ COMPLETATO
L'onboarding attuale è un form statico. Serve una chat conversazionale dinamica.

- [x] **Creare `WizardAgent`** in `apps/backend/src/infrastructure/ai/agents/wizard_agent.py`
  - [x] Logica per domande dinamiche basate su risposte precedenti
  - [x] Estrazione strutturata dei dati (pain, goals, equipment)
  - [x] Integrazione con ChromaDB per salvare contesto utente

- [x] **Creare endpoint `/api/wizard/`** in `apps/backend/src/interfaces/api/routers/wizard.py`
  - [x] `POST /start` - Inizia intervista
  - [x] `POST /message` - Continua conversazione
  - [x] `GET /status/{session_id}` - Stato intervista

- [x] **Creare `WizardChat` component** in `apps/frontend/src/features/wizard/`
  - [x] UI chat simile a WhatsApp/ChatGPT
  - [x] Route `/wizard` disponibile

---

### 2. User Context RAG - ✅ COMPLETATO
Le risposte utente devono essere embeddate e salvate in ChromaDB.

- [x] **Creare `UserContextRAG`** in `apps/backend/src/infrastructure/ai/user_context_rag.py`
  - [x] Schema metadata: `user_id`, `category`, `timestamp`
  - [x] Categories: `pain`, `goal`, `equipment`, `history`, `medical`, `preference`

- [x] **Metodi implementati:**
  - [x] `store_context(user_id, text, category)`
  - [x] `retrieve_context(user_id, query, categories)`
  - [x] `get_user_profile_context(user_id)`
  - [x] `store_wizard_answer(user_id, question, answer, category)`

- [x] **Integrato nel Wizard Agent**
  - [x] Ogni risposta utente → embedding → ChromaDB

---

### 3. Agent Pipeline (Medical → Coach) - ✅ COMPLETATO
Gli agenti ora comunicano tramite orchestrator.

- [x] **Creato `MedicalReport` dataclass** con constraints formali
  ```python
  @dataclass
  class MedicalReport:
      constraints: List[str]
      clearance_level: ClearanceLevel  # RED, YELLOW, GREEN
      phase: RecoveryPhase
      max_intensity_percent: int
      avoid_movements: List[str]
  ```

- [x] **Creato `AgentOrchestrator`** in `apps/backend/src/application/services/agent_orchestrator.py`
  - [x] Pipeline: Medical → Coach con constraints
  - [x] `generate_medical_report()` da pain data
  - [x] `orchestrate_workout_generation()` con clearance check
  - [x] `validate_exercise_against_constraints()`
  - [x] Decision logging

- [x] **Constraint types definiti:**
  - NO_SPINAL_LOADING, NO_FLEXION_UNDER_LOAD, NO_HEAVY_DEADLIFTS
  - NO_OVERHEAD_PRESSING, NO_KIPPING, NO_RUNNING, NO_BOX_JUMPS
  - NO_DEEP_SQUATS, KNEE_FLEXION_MAX_90, REDUCE_INTENSITY

---

## 🟡 PRIORITÀ MEDIA - Funzionalità Incomplete

### 4. Autenticazione JWT - ✅ COMPLETATO
L'auth esiste ma non è integrata ovunque.

- [x] **Estrarre `user_id` da JWT token** (rimosso hardcoded `"default_user"`)
  - [x] `apps/backend/src/interfaces/api/routers/users.py` - usa `CurrentUser`
  - [x] `apps/backend/src/interfaces/api/routers/biometrics.py` - usa `CurrentUser`
  - [x] `apps/backend/src/interfaces/api/routers/workout_coach.py` - usa `CurrentUser`
  - [x] `apps/backend/src/interfaces/api/routers/medical.py` - usa `CurrentUser`
  - [x] `apps/backend/src/interfaces/api/routers/nutrition.py` - usa `CurrentUser`
  - [x] `apps/backend/src/interfaces/api/routers/progress.py` - usa `CurrentUser`
  - [x] `apps/backend/src/interfaces/api/routers/workouts.py` - usa `CurrentUser`

- [x] **Creato `CurrentUser` type alias** in `security.py`
  ```python
  CurrentUser = Annotated[UserModel, Depends(get_current_user)]
  ```

- [x] **Endpoint `/api/users/me`** funzionante
  - [x] Usa JWT per identificare utente

---

### 5. Frontend - Chat Agents Non Collegati - ✅ COMPLETATO
`UnifiedChatInterface.tsx` ora usa API reali.

- [x] **Collegare Workout Coach**
  - [x] Rimosso mock response
  - [x] Chiama `workoutCoachApi.ask()`

- [x] **Collegare Nutrition Coach**
  - [x] Rimosso mock response
  - [x] Chiama `nutritionApi.ask()`

- [ ] **Implementare `getCurrentPlan`** per nutrition context (opzionale)

---

### 6. Knowledge Base RAG + User Context - ✅ COMPLETATO

- [x] **UserContextRAG integrato in tutti gli agenti:**
  - [x] `MedicalAgent._get_user_context()` - legge pain, medical, history, goal
  - [x] `WorkoutCoach._get_user_context()` - legge goal, equipment, preference, history
  - [x] `NutritionAgent._get_user_context()` - legge preference, goal, medical

- [x] **Ogni agente ora:**
  - [x] Recupera contesto utente da ChromaDB prima di rispondere
  - [x] Arricchisce il prompt con informazioni personalizzate
  - [x] Usa categorie specifiche per tipo di query

- [x] **Sports Medicine Knowledge Base - COMPLETATO**
  - [x] Creato `data/sports_medicine_knowledge_base.md` (10.7KB, 8 injury types)
  - [x] `populate_rag.py` aggiornato per ingestire in ChromaDB
  - [x] Supporta: sciatica, pubalgia, shoulder, knee, hip, ankle, lumbar, cervical

---

## 🟢 PRIORITÀ BASSA - Miglioramenti - ✅ TUTTI COMPLETATI

### 7. Database Schema - ✅ COMPLETATO
- [x] **Creata tabella `workout_plans`** in `models.py`
  - [x] Campi: id, user_id, date, status, exercises, constraints, clearance_level
  - [x] Tracking completamento: completed_at, feedback, pain_after

- [x] **`is_onboarded` già presente** in UserModel

---

### 8. Nutrition Repository - ✅ COMPLETATO
- [x] **Fixata deserializzazione meals** (`nutrition_repository_impl.py`)
  - [x] Aggiunto metodo `_deserialize_meals()`
  - [x] Converte JSON → Meal/FoodItem objects

---

### 9. Chat Repository - Session Type - ✅ COMPLETATO
- [x] **Session type salvato in metadata** (`chat_repository_impl.py`)
  - [x] `create_new_session()` salva session_type come primo messaggio
  - [x] Aggiunto `get_sessions_by_type()` per filtrare

---

### 10. Weekly Review - User Phase - ✅ COMPLETATO
- [x] **Fase recuperata da profilo utente** (`weekly_review.py`)
  - [x] Aggiunto `user_repository` al costruttore
  - [x] Metodo `_get_user_phase()` legge da UserModel

---

## 📊 Riepilogo Effort Stimato

| Area | Task | Effort |
|------|------|--------|
| Wizard Agent | Backend + Frontend | 3-4 giorni |
| User Context RAG | ChromaDB integration | 1-2 giorni |
| Agent Pipeline | Orchestrator | 2-3 giorni |
| JWT Integration | Middleware + refactor | 1 giorno |
| Frontend Chat | Collegare API | 0.5 giorni |
| Knowledge Base | Sciatica docs | 1 giorno |
| Database Schema | Migrations | 0.5 giorni |
| Bug fixes | Vari TODO | 1 giorno |

**Totale stimato: 10-13 giorni di lavoro**

---

## 🎯 Ordine Consigliato di Implementazione

1. **JWT Integration** - Prerequisito per tutto (user_id reale)
2. **User Context RAG** - Fondamentale per memoria agenti
3. **Wizard Agent** - Sostituisce onboarding statico
4. **Agent Pipeline** - Orchestrazione Medical → Coach
5. **Frontend Chat** - Collegare API esistenti
6. **Knowledge Base** - Migliorare risposte agenti
7. **Database Schema** - Allineare a architettura
8. **Bug fixes** - Cleanup finale

---

## ✅ Già Completato

- [x] Autenticazione base (login/register)
- [x] Medical Agent (chat + checkin)
- [x] Workout Coach Agent (backend)
- [x] Nutrition Agent (backend)
- [x] ChromaDB setup (per knowledge base)
- [x] Chat UI component
- [x] Pain tracking
- [x] Biometrics tracking
- [x] Progress/KPI system

---

## 🚀 ENHANCEMENT SESSION - 25 Nov 2025

### RAG Knowledge Base - MASSIVELY ENHANCED ✅
| Dataset | Chunks | Content |
|---------|--------|---------|
| Free Exercise DB NEW | 88 | 873 esercizi con dettagli completi |
| Free Exercise DB Legacy | 30 | 300 esercizi aggiuntivi |
| CrossFit WODs | 8 | Workout completi |
| UCO PhyRehab | 10 | 16 esercizi riabilitazione |
| Sports Medicine | 18 | Protocolli multi-infortunio |
| CrossFit KB | 15 | Movement standards |
| Sciatica Medical | 12 | Recupero sciatica |
| CrossFit Standards | 21 | Tecnica movimenti |
| Fit Recipes | 21 | Ricette fitness |
| Local Exercises | 5 | Rehab specifici |
| **TOTALE** | **228** | **1,173+ esercizi** |

### FatSecret API - LIVE ✅
- ✅ OAuth 2.0 authentication
- ✅ Search foods endpoint `/api/foods/search`
- ✅ Food details endpoint `/api/foods/details/{id}`
- ✅ Categories endpoint `/api/foods/categories`
- ✅ Database caching
- ✅ IP whitelisted: `34.140.158.2`

### Frontend UI Polish - MOBILE FIRST ✅
- ✅ CSS animations (fade-in, slide-up, bounce, shimmer)
- ✅ Glass morphism effects
- ✅ Touch optimizations
- ✅ Safe area utilities
- ✅ New components: Skeleton, Sheet, Toast
- ✅ FoodSearchPanel redesign con debounce
- ✅ FoodItemCard redesign con macro icons
- ✅ Haptic feedback su interazioni
- ✅ Horizontal scroll categories
- ✅ Production-ready mobile UX
