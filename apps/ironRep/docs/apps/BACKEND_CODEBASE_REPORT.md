# IronRep Backend (apps/backend/src) — Codebase Audit & Modernization Report (Progressivo)

Ultimo aggiornamento: 2025-12-19

## Obiettivo
Documento **progressivo** e **verificabile** per:
- Mappatura completa della struttura backend (`apps/backend/src`)
- Runtime tracing (cosa viene caricato/usato davvero)
- Backlog miglioramenti **prioritizzato** per rendere il backend “Ferrari-level” (2025): robusto, osservabile, sicuro, performante

## Regole di audit (non negoziabili)
- ✅ Solo informazioni **verificate** su file reali
- ❌ Niente hardcoded (URL/credenziali/magic numbers/stringhe duplicate)
- ❌ Niente dead/old code
- ❌ Niente duplicate code
- ❌ Niente spaghetti code (funzioni eccessive / logica non separata)

---

## 1) Mappatura struttura (prima passata)
### 1.1 Root `apps/backend/src`
- `src/interfaces/` — API REST (FastAPI) + routers
- `src/application/` — use-cases / services / DTO
- `src/domain/` — entities / value objects / repository interfaces / domain services
- `src/infrastructure/` — persistence (SQLAlchemy), AI/RAG, config, logging, external integrations

> Nota: questa è una mappa **iniziale** basata sul listing del filesystem. Verrà completata “file-by-file” nelle sezioni successive.

---

## 2) Entry-point & Routing
### 2.1 `src/interfaces/api/main.py`
**Ruolo:** entrypoint FastAPI; registra CORS; startup event; include routers.

**Evidenze (file):** `apps/backend/src/interfaces/api/main.py`

#### 2.1.1 Punti forti
- ✅ `FastAPI` centralizzato e routing esplicito
- ✅ endpoint `/health`

#### 2.1.2 Problemi/verifiche (da sistemare)
- ⚠️ **CORS hardcoded**: lista `allow_origins` contiene domini e localhost inline. Migliorare con configurazione via `settings` e policy per ambienti (dev/staging/prod).
- ⚠️ `logging.basicConfig(...)` in entrypoint: rischio doppia configurazione / conflitto con uvicorn/gunicorn. Va standardizzata una pipeline logging unica (structlog/json, correlation id, request logs).
- ⚠️ Import router “massivo” in una riga unica (`from .routers import ...`): aumenta coupling e costo import. Possibile refactor verso auto-discovery o import più modulare.
- ⚠️ Import “forzato” di modelli per `Base.metadata` (`models`, `nutrition_models`, `food_models`): utile, ma va controllato impatto su boot time e side-effects.

---

## 3) Runtime tracing (PENDING)
Obiettivo: misurare e registrare cosa viene importato in `from src.interfaces.api.main import app` e i costi di import.

- Stato: **completato** ✅

### 3.1 Tracing import-time (container produzione)
**Comando eseguito (verificato):**

```bash
docker exec -i ironrep-backend-prod sh -lc \
  "/opt/venv/bin/python -X importtime -c 'from src.interfaces.api.main import app; print(\"app_loaded\", bool(app))' \
   2> /tmp/importtime.log; tail -n 60 /tmp/importtime.log"
```

**Note importanti:**
- ✅ Il Python corretto nel container è `/opt/venv/bin/python` (non `/usr/local/bin/python`).
- ✅ `pydantic` è presente nel venv (`2.12.5`). Un primo tentativo errato su Python di sistema aveva generato un falso negativo.

**Output (estratto tail, verificato):**
- ✅ `app_loaded True`
- ✅ Risultano importati e inizializzati moduli chiave: `passlib` con `argon2` e `bcrypt`, routers FastAPI, e integrazioni Google.

### 3.2 Moduli con costo import elevato (priorità ottimizzazione boot)
Dall’estratto import-time (ultime righe), emergono costi significativi su:
- `src.interfaces.api.routers.knowledge_base` ≈ **163ms** (alto)
- `src.infrastructure.persistence.repositories.weekly_plans_repository` ≈ **54ms**
- `src.infrastructure.external.google_fit_service` ≈ **33ms**
- `src.interfaces.api.routers.users` ≈ **29ms**
- `src.interfaces.api.routers.streaming` ≈ **24ms**

> Questi numeri sono un *segnale*, non una colpa: indicano dove concentrare refactor “Ferrari-level” (lazy imports, split moduli, evitare side-effects in import-time, caching/config init).

---

## 4) Backlog miglioramenti (bozza, da confermare via analisi completa)
> Questa sezione verrà popolata solo con finding verificati file-by-file.

- (PENDING) Config: eliminare hardcoded e duplicazioni in config/docker/app.
- (PENDING) Observability: logging strutturato + tracing OpenTelemetry.
- (PENDING) Architettura: riduzione coupling tra `interfaces` e `infrastructure`.
- (PENDING) Test: coverage su use-cases core.

---

## 5) Diario analisi (progressivo)
- 2025-12-19: creato report base; identificato entrypoint FastAPI e primi punti critici (CORS hardcoded, logging basicConfig, import massivo routers).
- 2025-12-19: eseguito runtime tracing import-time nel container prod con `/opt/venv/bin/python`; identificati moduli con import-cost elevato (knowledge_base, weekly_plans_repository, google_fit_service, streaming).

---

## 6) Finding architetturali iniziali (verificati)
### 6.1 `src/__init__.py` importa tutto (wildcard)
**Evidenza:** `apps/backend/src/__init__.py`

```python
from .domain import *
from .application import *
from .infrastructure import *
from .interfaces import *
```

**Impatto (2025, Ferrari-level):**
- ❌ Aumenta coupling e rende l’import di `src` *side-effectful*.
- ❌ Peggiora boot-time e rende difficile il “dead code detection” perché molte cose risultano importate indirettamente.
- ❌ Amplifica rischi di circular imports.

**Direzione miglioramento (senza implementare ora):**
- Preferire `__all__` espliciti e/o rimuovere wildcard export.
- Garantire che gli import di package non triggerino logiche applicative.

### 6.2 `src/application/__init__.py` importa use-cases (side-effect di package import)
**Evidenza:** `apps/backend/src/application/__init__.py` importa direttamente use-cases.

**Impatto:**
- ❌ Importare `src.application` trascina dipendenze (DTO, pydantic, ecc.) anche quando non servono.
- ✅ Migliorabile con export espliciti o evitando import “eager” in `__init__.py`.

---

## 7) Mappa API — Routers (prima iterazione, verificata)

### 7.1 Inventario files `src/interfaces/api/routers/`
**Evidenza:** directory `apps/backend/src/interfaces/api/routers/`

Routers presenti (file):
- `auth.py`
- `users.py`
- `biometrics.py`
- `wizard.py`
- `medical.py`
- `workout_coach.py`
- `nutrition.py`
- `foods.py`
- `google.py`
- `knowledge_base.py`
- `plans.py`
- `progress.py`
- `review.py`
- `streaming.py`
- `exercises.py`
- `exercise_preferences.py`
- `workouts.py`

> Nota: l’entrypoint include anche altri router; la lista completa “attiva” va consolidata incrociando `main.py` + import-time.

### 7.2 `routers/__init__.py` (import parziale)
**Evidenza:** `apps/backend/src/interfaces/api/routers/__init__.py`

```python
from . import review, progress, users, biometrics, exercises, medical, workout_coach, nutrition, foods, google
```

**Finding:**
- ⚠️ Import parziale e *non allineato* alla realtà dei router usati in `main.py` (es. `auth`, `wizard`, `streaming`, `plans`, `knowledge_base`, `exercise_preferences`, `workouts` non sono importati qui).
- ⚠️ Pattern “import eager” (anche se parziale) aumenta import-cost quando si importa `src.interfaces.api.routers`.

**Direzione miglioramento:**
- Standardizzare un solo meccanismo: o `main.py` include esplicitamente i router, oppure una registry/auto-discovery coerente.

---

## 8) Router: Knowledge Base (RAG)
### 8.1 `routers/knowledge_base.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/knowledge_base.py`

**Endpoints (verificati):**
- `GET /knowledge-base/status`
- `POST /knowledge-base/search`
- `POST /knowledge-base/update` (BackgroundTasks)
- `GET /knowledge-base/update-status`
- `POST /knowledge-base/reinitialize`

**Finding critici (regole non negoziabili):**
- ❌ **Hardcoded path**: `rag.reinitialize_knowledge_base('/app/data')` appare in più punti (update e reinitialize). Da spostare in `settings` (es. `settings.data_dir`) e riusare costante unica.
- ❌ **Global mutable state**: `_update_status` è dizionario globale in memoria (non safe in multi-worker, non persistente, race conditions).
- ⚠️ Error handling: `HTTPException(500, detail=str(e))` espone dettagli eccezione (potenzialmente sensibili) al client.
- ⚠️ TODO espliciti: USDA/OFF “delegato a script” (incompletezza funzionale, rischio drift).

**Direzione miglioramento 2025:**
- Spostare tracking update su storage persistente (DB/Redis) + job queue (es. RQ/Celery/Arq) invece di `BackgroundTasks` in-process.
- Sanitizzare error response (messaggio generico) e loggare dettagli solo server-side.
- Rendere idempotenti gli update e aggiungere locking distribuito.

---

## 9) Router: Google Integration
### 9.1 `routers/google.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/google.py`

**Endpoints (verificati):**
- `GET /api/google/auth/url`
- `POST /api/google/auth/callback`
- `GET /api/google/auth/status`
- `DELETE /api/google/auth/disconnect`
- `POST /api/google/fit/sync`
- `GET /api/google/fit/weight`
- `GET /api/google/fit/steps`
- `POST /api/google/calendar/events`
- `GET /api/google/calendar/events`
- `GET /api/google/youtube/search`
- `GET /api/google/youtube/video/{video_id}`

**Finding critici (regole non negoziabili):**
- ⚠️ `_get_credentials(account)` **modifica token in memoria** se scaduto, ma non fa `db.commit()` in quel punto.
  - Conseguenza: refresh token/access token possono non essere persistiti e ricadere in refresh loop.
- ⚠️ Tipi “magic string” ripetuti: `BiometricEntryModel.type == "BODY_COMP"` e `notes="Google Fit"`.

**Direzione miglioramento 2025:**
- Centralizzare refresh+persist token in un service “token manager” con transazione DB.
- Aggiungere rate limiting e circuit breaker verso API Google/YouTube.
- Aggiungere auditing (quando un account viene collegato/disconnesso) con event log.

---

## 10) Router: Weekly Plans
### 10.1 `routers/plans.py` (file molto grande)
**Evidenza:** `apps/backend/src/interfaces/api/routers/plans.py` (~900 linee)

**Finding critici (regole non negoziabili):**
- ❌ **Spaghetti risk**: file monolitico con molte responsabilità (coach plan, medical protocol, nutrition, preferences, parsing AI, template fallback).
- ❌ **Hardcoded / magic numbers**:
  - `base_calories = ... or 2200`
  - split macro `0.30/0.40/0.30` e conversioni `/4` `/9`
  - `days = ["monday", ...]` ripetuto
  - esercizi default hardcoded (es. “Back Squat”, “Deadlift”, …)
- ❌ **Duplicate logic**: calcolo macro e struttura pasti appaiono come logica embedded nel router (dovrebbe vivere in service/use-case).
- ⚠️ `_parse_exercises_from_ai(...)` è una funzione “di parsing” dentro router con regex + fallback: va separata in modulo dedicato e testata.

**Direzione miglioramento 2025:**
- Estrarre: `PlanGenerationService` / `MacroCalculator` / `AIProgramParser` in `application/services` + test unitari.
- Parametrizzare in `settings` (calorie base, macro split, default days, templates).
- Definire DTO/Pydantic per strutture `preferences` (al posto di `Dict[str, Any]` raw) e validare in ingresso.

### 10.2 `plans.py` — persistenza preferenze in UserContextRAG (parte finale)
**Evidenza:** `apps/backend/src/interfaces/api/routers/plans.py` (righe finali ~840+)

**Osservazioni verificate:**
- ✅ C’è un tentativo esplicito di “memoria agente” salvando preferenze nutrizionali in RAG (favorite/disliked/allergies) tramite `user_rag.store_context(...)`.
- ⚠️ Il payload di preferenze è accettato come `Dict[str, Any]` e “flattenato” a mano.

**Finding critici:**
- ❌ **No schema forte**: `preferences: Dict[str, Any]` rende difficile garantire coerenza, validazione, versioning.
- ⚠️ Logging/errore: salvataggio RAG fallisce in `except` e continua (ok), ma serve audit strutturato (event log) per capire quando la memoria non si aggiorna.

---

## 11) Router: Users
### 11.1 `routers/users.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/users.py`

**Endpoints (verificati):**
- `POST /api/users/onboarding` (response 201)
- `GET /api/users/me` (auth)
- `PUT /api/users/me` (auth)
- `GET /api/users/{user_id}`
- `GET /api/users/{user_id}/stats`
- `POST /api/users/{user_id}/phase/advance`

**Finding critici (regole non negoziabili):**
- ❌ **Hardcoded phases** in `advance_phase`: lista `valid_phases = [...]` include stringhe (anche miste IT/EN, es. `"Strengthening"`). Questo è fragile e va centralizzato (Enum unico nel domain).
- ⚠️ `update_user_profile`: `allowed_fields` è una lista enorme “embedded” nel router.
  - Rischio: divergenza rispetto a `UserModel`/domain entity; difficile manutenzione.
- ❌ Error handling espone `str(e)` al client in più punti (500 con detail = errore interno).
- ❌ Presenza di `print(...)` per errori RAG (es. `print(f"⚠️ Failed to update RAG context: {e}")`) invece di logger strutturato.
- ⚠️ `PUT /me` accetta `updates: Dict[str, Any]`: mancano DTO/versioning; rischio input non previsto e difficoltà “no hardcoded/no duplicate”.

**Direzione miglioramento 2025:**
- Portare la whitelist campi + validazione in `application/use_case` con schema Pydantic “UpdateUserProfileRequest” versionato.
- Centralizzare fasi recupero in `domain` (Enum) e non duplicarle in router.
- Standardizzare error responses (messaggio generico) + logging dettagliato server-side.

---

## 12) Router: Streaming (SSE)
### 12.1 `routers/streaming.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/streaming.py`

**Endpoints (verificati):**
- `GET /api/stream/medical`
- `GET /api/stream/workout`
- `GET /api/stream/nutrition`
- `GET /api/stream/chat` (router su `mode`)

**Finding critici (regole non negoziabili):**
- ❌ **System prompt hardcoded** (multi-line string) ripetuti per medical/workout/nutrition: viola “NO HARDCODED / stringhe duplicate”.
- ❌ `HTTPException(status_code=500, detail=str(e))` espone dettagli errore internamente.
- ⚠️ Dipendenze non usate: `db: Session = Depends(get_db)` è presente ma il DB non è usato dentro gli handler (overhead + coupling inutili).
- ⚠️ `session_id` accettato ma non usato nella logica (almeno nel file mostrato): rischio dead parameter.

**Direzione miglioramento 2025:**
- Centralizzare prompt in un “Prompt Registry” (file/config) + versioning.
- Aggiungere rate limiting per endpoint streaming (protezione costo LLM).
- Propagare `request_id/correlation_id` negli eventi SSE e nei log.

---

## 13) Router: Authentication
### 13.1 `routers/auth.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/auth.py`

**Endpoints (verificati):**
- `POST /api/auth/login` (OAuth2PasswordRequestForm)
- `POST /api/auth/register`

**Finding critici (regole non negoziabili):**
- ⚠️ `register_user`: non normalizza `email` (lower/trim) prima del check -> rischio duplicati logici (case-insensitive).
- ⚠️ `register_user`: non impone policy password (min length/strength) a livello API.
- ✅ `login_access_token`: ora gestisce assenza hash / verify error e risponde 401 (robusto vs 500).

**Direzione miglioramento 2025:**
- Rate limiting / lockout su login (brute force).
- Migrare a schema Pydantic v2 `ConfigDict(from_attributes=True)` (coerenza) e uniformare modelli response.
- Considerare audit log “auth events” (login success/failure) senza PII sensibile.

---

## 14) Config, Secrets & Hardcoded Inventory (verificato)

### 14.1 `infrastructure/config/settings.py`
**Evidenza:** `apps/backend/src/infrastructure/config/settings.py`

**Finding critici (produzione):**
- ❌ `secret_key` ha un default **hardcoded**: `"dev-only-key-change-in-production"`.
  - Rischio: avvio in prod con chiave debole se ENV non settata.
- ❌ `database_url` ha default hardcoded: `postgresql://ironrep:ironrep@localhost:5432/ironrep`.
  - Rischio: credenziali/host involontari, drift tra ambienti.
- ❌ `google_redirect_uri` default hardcoded `http://localhost:8000/api/google/auth/callback`.
  - Rischio: OAuth broken in prod se non override.
- ⚠️ `debug: bool = True` default.
  - Rischio: comportamenti non-prod (logging verbose, stack trace, ecc.).

**Direzione miglioramento 2025 (best practice):**
- Rendere **obbligatorie** in prod: `SECRET_KEY`, `DATABASE_URL`, `GOOGLE_REDIRECT_URI` (fail-fast se mancanti).
- Separare settings per ambiente (dev/staging/prod) e validazione runtime (Pydantic settings con checks).
- Evitare default “pericolosi” per secrets/connessioni.

### 14.2 `infrastructure/security/security.py`
**Evidenza:** `apps/backend/src/infrastructure/security/security.py`

**Finding:**
- ⚠️ `OAuth2PasswordBearer(tokenUrl="/api/auth/login")` è hardcoded.
  - Non è un segreto, ma va centralizzato per evitare divergenze tra path reali e doc.

### 14.3 `infrastructure/external/google_oauth_service.py`
**Evidenza:** `apps/backend/src/infrastructure/external/google_oauth_service.py`

**Finding (hardcoded, ma accettabile se centralizzato):**
- ⚠️ Scopes OAuth sono hardcoded in costante `SCOPES` (fit/calendar/youtube/profile) con URL Google.
- ⚠️ Endpoints OAuth hardcoded: `auth_uri`, `token_uri`, `revoke`.

**Direzione miglioramento:**
- Tenere scopes in config/versioning (per rollout controllato) e documentare quali scopes sono minimi per feature.
- Aggiungere feature flags per abilitare/disabilitare FIT/YouTube/Calendar per utente.

### 14.4 `infrastructure/external/youtube_service.py`
**Evidenza:** `apps/backend/src/infrastructure/external/youtube_service.py`

**Finding:**
- ⚠️ Query di ricerca hardcoded: `f"{exercise_name} esercizio tutorial form corretta"`.
- ⚠️ URL embed/watch hardcoded (non segreti, ma duplicabili): `https://www.youtube.com/embed/...` e `https://www.youtube.com/watch?v=...`.

**Direzione miglioramento:**
- Centralizzare template query e localizzazione (IT/EN) in config.
- Cache lato server per query ripetute + rate limit.

### 14.5 `infrastructure/ai/google_embeddings.py`
**Evidenza:** `apps/backend/src/infrastructure/ai/google_embeddings.py`

**Finding:**
- ⚠️ Model name embeddings hardcoded: `models/text-embedding-004`.
- ⚠️ `raise e` dopo logging: ok per vedere errori, ma va gestito per resilienza (retry/backoff/circuit breaker).

**Direzione miglioramento:**
- Parametrizzare `model_name` in settings.
- Implementare retry con backoff e limiti (quota Google).

### 14.6 `infrastructure/ai/llm_service.py`
**Evidenza:** `apps/backend/src/infrastructure/ai/llm_service.py`

**Finding:**
- ⚠️ Model name hardcoded: `gemini-2.0-flash` e metadata provider_name.
- ⚠️ `temperature=0.7`, `max_tokens/max_output_tokens=2048` hardcoded.

**Direzione miglioramento:**
- Rendere parametri runtime configurabili per endpoint/use-case (settings + override per request).
- Telemetria costo/token per provider (observability).

---

## 15) Persistence Layer (SQLAlchemy) — audit verificato

### 15.1 `infrastructure/persistence/database.py`
**Evidenza:** `apps/backend/src/infrastructure/persistence/database.py`

**Finding critici (regole non negoziabili):**
- ❌ `DATABASE_URL` ha un fallback hardcoded: `postgresql://ironrep:ironrep@localhost:5432/ironrep`.
- ⚠️ `init_db()` chiama `Base.metadata.create_all(bind=engine)`.
  - Rischio: in prod/multi-istanza non è un workflow di migrazione; può creare drift rispetto ad Alembic.
- ⚠️ `reset_db()` è presente e distruttivo (drop_all).
  - Rischio: se importato/usato accidentalmente in ambiente non-dev.
- ⚠️ Import `declarative_base` da `sqlalchemy.ext.declarative` (legacy).

**Direzione miglioramento 2025:**
- Rimuovere default “pericolosi” e rendere `DATABASE_URL` obbligatorio in prod.
- Migrazioni: usare Alembic come unica fonte di verità (niente `create_all` in runtime prod).
- Isolare funzioni distruttive (reset) dietro guardrail (solo dev/test) e non esportarle in runtime.

### 15.2 `infrastructure/persistence/models.py`
**Evidenza:** `apps/backend/src/infrastructure/persistence/models.py` (~665 linee)

**Finding critici (dati, coerenza, maintainability):**
- ❌ **Duplicazione concettuale**: esistono sia `UserModel` (tabella `users`) sia `UserProfileModel` (tabella `user_profile`) con campi sovrapposti (`diagnosis`, `current_phase`, `goals`, ecc.).
  - Rischio: due “fonti di verità” → bug silenziosi, drift, query incoerenti.
- ⚠️ Defaults non coerenti e potenzialmente pericolosi:
  - `program_start_date = default=datetime.now` e in altri punti `server_default=func.now()` → semantica diversa.
  - `diagnosis` default `''` e `current_phase` default stringa hardcoded (anche già emersa in `users.py`).
- ⚠️ Molti campi “categorici” sono `String` free-form (es. `diet_type`, `nutrition_goal`, `difficulty`, `phase`, `status`).
  - Rischio: dati sporchi e branching duplicato nel codice.
- ⚠️ Uso estensivo di `JSON` senza schema/versioning (`equipment_available`, `pain_locations`, `sessions`, `daily_meals`, ecc.).
  - Rischio: rotture retrocompatibilità e migrazioni complesse.

**Direzione miglioramento 2025:**
- Consolidare profilo utente: **una sola tabella** (o separazione netta con FK 1:1 e ownership chiara) + migrazione.
- Introdurre Enum/Value Objects a livello domain e mapping coerente nel persistence layer.
- Stabilire una policy unica per timestamp (`timezone-aware` consigliato) e unificare `datetime.now` vs `func.now()`.

### 15.3 `infrastructure/persistence/food_models.py`
**Evidenza:** `apps/backend/src/infrastructure/persistence/food_models.py`

**Finding:**
- ⚠️ Campo `data = Column(JSON)` contiene risposta completa API (ok come cache), ma richiede policy: TTL/invalidazione/size.
- ✅ `UniqueConstraint('user_id', 'food_id', ...)` presente per preferiti (buono).

### 15.4 `infrastructure/persistence/nutrition_models.py`
**Evidenza:** `apps/backend/src/infrastructure/persistence/nutrition_models.py`

**Finding:**
- ⚠️ Importa `DietType, GoalType` dal domain ma i campi DB sono `Column(String)` (non `Enum`).
  - Rischio: disallineamento domain/persistence.
- ⚠️ `created_at = default=datetime.utcnow` è timezone-naive (come altrove).

---

## 16) Dependency Injection Container (side-effects / thread-safety) — verificato

### 16.1 `infrastructure/config/dependencies.py`
**Evidenza:** `apps/backend/src/infrastructure/config/dependencies.py`

**Finding critici (produzione):**
- ❌ **Side-effects all’import**: `container = DependencyContainer()` viene creato a import time.
  - Rischio: costi di startup elevati, crash in import (es. se manca config), e behavior non deterministico in worker multipli.
- ❌ Hardcoded path: `self.rag_service.initialize_knowledge_base('/app/data')`.
- ❌ Logging: diversi `print(...)` (es. knowledge base / RAG / user_context_rag) invece di logger strutturato.
- ❌ **Singleton mutabile per request**: `_wizard_agent` viene creato una volta e poi vengono riassegnati `user_repository`, `session_repository`, `orchestrator` ad ogni richiesta.
  - Rischio: race condition / cross-request data leak in ambiente concorrente (Uvicorn workers/threads).
- ⚠️ Funzioni helper in fondo hanno firme incoerenti con le method:
  - `get_generate_workout_use_case(db)` chiama `container.get_generate_workout_usecase(db)` ma il method richiede `user_id`.
  - `get_weekly_review_use_case(db)` idem.
  - Questo è un potenziale bug runtime (TypeError) quando usati come Depends.
- ⚠️ Nel file è presente `get_ask_coach_usecase` che ritorna `AskCoachUseCase(...)`, ma l’import di `AskCoachUseCase` non è visibile nelle righe iniziali mostrate.
  - Rischio: `NameError` se il path è effettivamente eseguito.

**Direzione miglioramento 2025:**
- Rendere il container **lazy** (inizializzazione on-demand) e spostare init pesanti in startup event controllato.
- Rimuovere singleton mutabili o renderli per-request (o per-user) con storage persistente (DB/Redis), non oggetti globali.
- Centralizzare path e configurazioni (niente `'/app/data'` embedded).

---

## 17) Coverage 100% — stato
**Inventario file (verificato):** `apps/backend/src` contiene **113 file** (esclusi `__pycache__` e `.pyc`). ✅

**Prossimo passo coverage:** produrre nel report una checklist “file-by-file” (113 righe) con stato: `NON ANALIZZATO` / `ANALIZZATO` / `DA RIFATTORIZZARE`.

---

## 18) Persistence Repositories — audit verificato

### 18.1 `repositories/user_repository_impl.py`
**Evidenza:** `apps/backend/src/infrastructure/persistence/repositories/user_repository_impl.py`

**Finding critici:**
- ⚠️ `get_by_email(email)` non normalizza (lower/trim) → stesso rischio già visto in `auth.py`.
- ⚠️ Mapping `sex` gestisce stringhe `male/female` + fallback a `'O'`.
  - Rischio: **silenzioso** (valori sporchi vengono “forzati”).
- ⚠️ Timestamp: `user_model.updated_at = datetime.now()` (timezone-naive) e altrove si usa default diversi.

**Direzione miglioramento 2025:**
- Normalizzazione `email` centrale (domain/service) e non duplicata.
- Validazione/Enum per `sex` e campi categorici; niente fallback “silenziosi”.

### 18.2 `repositories/weekly_plans_repository.py`
**Evidenza:** `apps/backend/src/infrastructure/persistence/repositories/weekly_plans_repository.py`

**Finding critici:**
- ❌ Logica calendario hardcoded/fragile: `get_week_start_end(...)` calcola “first Monday” manualmente.
  - Rischio: edge cases ISO week (week 1 che inizia l’anno precedente), timezone.
- ⚠️ `status='active'` hardcoded in creazioni (`WeeklyPlanModel`, `CoachWeeklyPlanModel`, `MedicalProtocolModel`, `NutritionWeeklyPlanModel`).
- ⚠️ `total_sessions` esclude `name == 'Rest'` → stringa magic.
- ⚠️ Scritture JSON mutate in-place (es. `sessions[session_index]['completed']=True`) e poi riassegnate.

**Direzione miglioramento 2025:**
- Usare `date.isocalendar()` per start/end week con libreria/utility robusta e test.
- Centralizzare gli status/enum (domain) e vietare magic strings.

### 18.3 `repositories/wizard_session_repository.py`
**Evidenza:** `apps/backend/src/infrastructure/persistence/repositories/wizard_session_repository.py`

**Finding critici:**
- ❌ Config default hardcoded in `agent_config` (`medical_mode`, `coach_mode`, `nutrition_mode`, ecc.).
- ❌ `cleanup_old_sessions(...).delete()` senza `synchronize_session` esplicito.
  - Può essere ok, ma va chiarito/standardizzato.

**Direzione miglioramento 2025:**
- Versionare `agent_config` e spostare default in settings (o dominio) con migrazioni.

### 18.4 `repositories/chat_repository_impl.py`
**Evidenza:** `apps/backend/src/infrastructure/persistence/repositories/chat_repository_impl.py`

**Finding critici:**
- ⚠️ `get_user_sessions()` usa `.distinct().order_by(desc(timestamp))` su Postgres: può non garantire “most recent per session” in modo deterministico.
- ⚠️ `get_sessions_by_type()` usa `ChatHistoryModel.message_metadata['session_type'].astext`.
  - Rischio: compatibilità SQLAlchemy/Postgres e performance se non indicizzato (GIN su JSONB).
- ✅ `delete_session()` fa rollback in except (buono).

**Direzione miglioramento 2025:**
- Introdurre tabella `chat_sessions` (1 row per session) invece di dedurre la sessione dal “primo messaggio”.
- Aggiungere indici: `(user_id, session_id, timestamp)` e GIN su `message_metadata` se necessario.

### 18.5 `repositories/workout_repository_impl.py`
**Evidenza:** `apps/backend/src/infrastructure/persistence/repositories/workout_repository_impl.py`

**Finding critici:**
- ❌ `get_by_week()` usa `session_id.like(f"W{week}%")` ed è dichiarato “simplified”.
  - Rischio: comportamento errato e non scalabile.
- ⚠️ `get_for_date()` usa `date.replace(... second=59)` con timezone-naive; boundary non robusti.
- ⚠️ Default embedded per `Exercise` (`sets=2`, `reps='10'`, `rest_seconds=60`).

**Direzione miglioramento 2025:**
- Query per settimana su `date` con range calcolato + indice su `(user_id, date)`.
- Parametrizzare default exercise o renderli obbligatori (evitare magic defaults).

### 18.6 `repositories/pain_repository_impl.py`
**Evidenza:** `apps/backend/src/infrastructure/persistence/repositories/pain_repository_impl.py`

**Finding:**
- ⚠️ `get_last_n_days()` usa `datetime.now()` timezone-naive.
- ✅ Repository semplice e coerente.

### 18.7 `repositories/kpi_repository_impl.py`
**Evidenza:** `apps/backend/src/infrastructure/persistence/repositories/kpi_repository_impl.py`

**Finding:**
- ⚠️ `get_by_week(user_id, week)` non include `year` → collisioni possibili tra anni.

### 18.8 `repositories/biometric_repository_impl.py`
**Evidenza:** `apps/backend/src/infrastructure/persistence/repositories/biometric_repository_impl.py`

**Finding:**
- ⚠️ `estimated_1rm` calcolato nel repository (`calculate_1rm_epley`) → logica domain che “trapela” nel persistence.
- ✅ Query ben indicizzabili (filtri su `user_id`, `type`, `date`, `exercise_id`).

### 18.9 `repositories/nutrition_repository_impl.py`
**Evidenza:** `apps/backend/src/infrastructure/persistence/repositories/nutrition_repository_impl.py`

**Finding critici:**
- ❌ Serializzazione JSON “double encode/decode”: `json.loads(json.dumps(...))`.
  - Rischio: performance + perdita tipi.
- ❌ Logging con `print(...)` in `_deserialize_meals`.
- ⚠️ `GoalType(model.goal)` / `DietType(model.diet_type)` presuppone valori validi DB.
  - Rischio: crash se DB contiene stringhe non conformi.

### 18.10 `repositories/food_repository_impl.py`
**Evidenza:** `apps/backend/src/infrastructure/persistence/repositories/food_repository_impl.py`

**Finding critici:**
- ⚠️ `cache_food`/`cache_food_details` non gestiscono concurrency: due richieste parallele possono violare unique su `fatsecret_id`.
- ⚠️ `get_user_favorites()` fa N+1 query (per ogni fav fa query su `FoodCacheModel`).
  - Rischio: performance degradata.

**Direzione miglioramento 2025:**
- UPSERT/`ON CONFLICT` (o merge) per cache, e join per evitare N+1.

---

## 19) Domain Layer — audit verificato

### 19.1 Entità: `domain/entities/user.py`
**Evidenza:** `apps/backend/src/domain/entities/user.py`

**Finding critici:**
- ❌ **Hardcoded phase**: `current_phase: str = "Fase 1: Decompressione"` è stringa (non Enum) → mismatch con `WorkoutPhase` che è Enum in `workout_session.py`.
- ⚠️ Incoerenza enums: esiste `ActivityLevel(Enum)` ma nel dataclass `User.activity_level` è `Optional[str]` (non `ActivityLevel`).
- ⚠️ Timestamp timezone-naive: usa `datetime.now` ovunque.

### 19.2 Entità: `domain/entities/user_profile.py`
**Evidenza:** `apps/backend/src/domain/entities/user_profile.py`

**Finding critici:**
- ❌ **Duplicazione** rispetto a `User`: esistono due entity separate che modellano il profilo (e nel persistence esistono due tabelle correlate: `users` e `user_profile`).
  - Rischio: doppia source-of-truth end-to-end.
- ⚠️ Valori hardcoded: `goals` default “Ritorno al CrossFit intermedio senza dolore”.

### 19.3 Entità: `domain/entities/workout_session.py`
**Evidenza:** `apps/backend/src/domain/entities/workout_session.py`

**Finding critici (NO hardcoded/duplicate):**
- ❌ Enum `WorkoutPhase` ha valori stringa hardcoded che compaiono anche in altri layer (`users.py`, `models.py`).
- ⚠️ `WorkoutSession.user_id: str = "default_user"` (MVP) → rischio leakage/multi-tenant non-safe.
- ⚠️ Heuristic hardcoded in `get_estimated_duration()` (`work_time=45`, “2 mins per set”).

### 19.4 Entità: `domain/entities/pain_assessment.py`
**Evidenza:** `apps/backend/src/domain/entities/pain_assessment.py`

**Finding critici:**
- ⚠️ `user_id: str = "default_user"` (MVP).
- ✅ Validazioni in `__post_init__` (range pain 0-10, almeno 1 location).

### 19.5 Entità: `domain/entities/progress_kpi.py`
**Evidenza:** `apps/backend/src/domain/entities/progress_kpi.py`

**Finding critici:**
- ❌ Criteri hardcoded: soglie (pain<=4, compliance>=80, pain_free>=18) embedded nella entity.
  - Questo è domain logic ok, ma va **versionato/configurabile** per evoluzione protocollo clinico.
- ⚠️ `week` non include `year` (già visto nel repository).

### 19.6 Entità: `domain/entities/nutrition.py` + `domain/entities/food.py`
**Evidenza:**
- `apps/backend/src/domain/entities/nutrition.py`
- `apps/backend/src/domain/entities/food.py`

**Finding critici:**
- ❌ Duplicazione `FoodItem`: esiste sia in `nutrition.py` sia in `food.py` con campi diversi.
  - Rischio: mismatch di serializzazione e conversioni ad-hoc.
- ⚠️ Coerenza Pydantic: in `nutrition.py` si usa `BaseModel` per alcuni tipi e classi “plain” per altri (`DailyNutritionLog`, `NutritionPlan`).

### 19.7 Domain Services
**Evidenza:**
- `apps/backend/src/domain/services/pain_analyzer.py`
- `apps/backend/src/domain/services/red_flags_checker.py`
- `apps/backend/src/domain/services/progression_engine.py`

**Finding critici:**
- ❌ `ProgressionEngine.PHASE_CRITERIA` hardcoded con soglie e durata settimane.
- ❌ `ProgressionEngine._get_phase_exercises()` hardcoded con exercise ids (es. `cat_cow`, `dead_bug`, `back_squat`).
- ⚠️ `ProgressionEngine` contiene placeholder: `criteria_met["strength"] = True  # Placeholder`.
  - Rischio: decisioni errate in produzione.
- ⚠️ `RedFlagsChecker.RED_FLAGS` hardcoded con keyword/urgency/message. È domain knowledge corretta da avere, ma serve governance/versioning.

### 19.8 Repository Interfaces (domain)
**Evidenza:** `apps/backend/src/domain/repositories/*.py`

**Finding:**
- ⚠️ Interfacce ok, ma alcune firme mancano concetti necessari:
  - KPI: manca `year`.
  - Workout: `get_by_week` non specifica anno/ISO-week.

**Direzione miglioramento 2025 (domain-first):**
- Consolidare `User` vs `UserProfile` e introdurre `ValueObjects/Enums` unici (fasi, status, diet, goal, activity).
- Eliminare `default_user` dal domain (multi-tenant safety).
- Versionare protocolli (progression criteria, red flags) e renderli configurabili/aggiornabili.
- Unificare `FoodItem` in un solo modello domain e definire mapping esplicito verso persistence.

---

## 20) Application Layer (use cases, DTO, orchestrazione) — audit verificato

### 20.1 DTO: `application/dtos/dtos.py`
**Evidenza:** `apps/backend/src/application/dtos/dtos.py`

**Finding critici:**
- ⚠️ `ChatMessageDTO.role` accetta solo `user|assistant`, ma in persistence viene salvato anche `role="system"` (vedi `ChatRepositoryImpl.create_new_session`).
  - Rischio: `get_chat_history()` può rompere (validation error) se include messaggi system.
- ⚠️ DTO “ricchi” con campi duplicati già esistenti nel domain (`UserDTO` replica quasi interamente `User.to_dict`).
  - Rischio: drift e manutenzione alta.

### 20.2 Use case: `application/use_cases/generate_workout.py`
**Evidenza:** `apps/backend/src/application/use_cases/generate_workout.py`

**Finding critici (NO hardcoded/NO dead):**
- ❌ `user_id: str = "default_user"` default nel costruttore → rischio multi-tenant.
- ❌ Side-effect/infra nel use-case: lazy import `get_rag_service()` + `print(...)` in caso errore.
- ❌ URL hardcoded: `video_url` fallback a `https://www.youtube.com/results?...`.
- ❌ `session_id` generator hardcoded/errato: `return f"W1D{datetime.now().day}"`.
  - Non rappresenta `week` reale; collisioni possibili.
- ⚠️ `phase.value` viene usato per chiamare `exercise_library.get_exercises_for_phase(phase.value)`.
  - Se `exercise_library` usa altri id, c’è coupling fragile.

### 20.3 Use case: `application/use_cases/checkin_conversational.py`
**Evidenza:** `apps/backend/src/application/use_cases/checkin_conversational.py`

**Finding critici:**
- ❌ Prompt hardcoded multi-line (`initial_prompt`, `prompt`, `workout_prompt`) embedded nel use case.
- ❌ Parsing regex hardcoded per estrarre dolore e dizionari hardcoded per location/trigger.
  - Rischio: NLP fragile + duplicazione con `domain/services` (red flags/pain analyzer).
- ⚠️ Gestione dati: `PainAssessment` richiede `pain_locations` non vuoto (validazione). La logica `complete` lo garantisce, ok.

### 20.4 Use case: `application/use_cases/onboarding.py`
**Evidenza:** `apps/backend/src/application/use_cases/onboarding.py`

**Finding critici:**
- ❌ Default hardcoded `diagnosis=..."Sciatica"` se non presente.
- ❌ Logging con `print(...)` su errore dieta iniziale.
- ⚠️ `validate_onboarding_data()` fa validazione manuale parziale, ma l’API usa anche `OnboardingRequestDTO` (duplica regole).

### 20.5 Use case: `application/use_cases/weekly_review.py`
**Evidenza:** `apps/backend/src/application/use_cases/weekly_review.py`

**Finding critici (bug ad alto rischio):**
- ❌ Mapping enum incoerente: usa `WorkoutPhase.PHASE_3_STRENGTH` e `WorkoutPhase.PHASE_4_PERFORMANCE`, ma l’enum in `domain/entities/workout_session.py` espone `PHASE_3_STRENGTHENING` e `PHASE_4_RETURN_TO_SPORT`.
  - Rischio: crash runtime (AttributeError) o decisione fase errata.
- ❌ Calcolo KPI hardcoded/semplificato:
  - `week_start = now - 7 days` ignora `week_number` reale.
  - `pain_free_time_hours = 24 - (avg_pain/10*24)` è una formula arbitraria.
  - `planned_sessions default=3` se nessun workout.
- ❌ Generazione next week hardcoded: assume `current_pain=2` e `pain_locations=['lombare']`.
- ❌ Logging con `print(...)` su errori.

### 20.6 Use cases: Q&A agents
**Evidenze:**
- `apps/backend/src/application/use_cases/ask_medical.py`
- `apps/backend/src/application/use_cases/ask_workout_coach.py`
- `apps/backend/src/application/use_cases/ask_nutritionist.py`

**Finding critici:**
- ⚠️ Incoerenza interfaccia agent:
  - `AskMedicalUseCase` chiama `medical_coach_agent.answer_question(question, user_id, context)`.
  - `AskNutritionistUseCase` chiama `agent.answer_question(question, context)` (manca `user_id`) → potenziale bug/incompatibilità.
- ⚠️ Duplicazione logica di “suggested actions” basata sui tool names.

### 20.7 Use case: `generate_diet.py`
**Evidenza:** `apps/backend/src/application/use_cases/generate_diet.py`

**Finding:**
- ❌ Placeholder / dead-path: se `result["success"]` fa `pass` con commento “In real app...”.
  - Rischio: feature incompleta mascherata da successo.

### 20.8 Service: `application/services/agent_orchestrator.py`
**Evidenza:** `apps/backend/src/application/services/agent_orchestrator.py` (~992 linee)

**Finding critici (NO hardcoded / NO spaghetti):**
- ❌ Monolite molto grande con:
  - criteri medici hardcoded (pain thresholds, fasi, constraints)
  - liste `days=["monday",...]`, stringhe `"Rest"`, macro split 30/40/30 e `base_calories=2200`
  - esercizi default hardcoded per protocolli
- ❌ Persistenza “dentro” orchestrator: scrive direttamente su repository DB; mescola applicazione + persistence.
- ❌ Duplicazioni con router `plans.py` e repository weekly plans (stessa logica macro, stessa struttura giorni).
- ❌ Logging non strutturato: `logging.getLogger(__name__)` ma in molti punti error handling usa stringhe non normalizzate; altrove nel codebase c’è `get_logger()`.

**Direzione miglioramento 2025:**
- Spezzare `agent_orchestrator.py` in:
  - `MedicalReportBuilder`
  - `PlanPersistenceService`
  - `WorkoutPlanAssembler` / `NutritionPlanAssembler`
- Eliminare hardcoded (calorie/macro/days/rest/exercises) → settings + versioning.
- Uniformare l’interfaccia agent (`answer_question(question, user_id, context)`) e tipizzare i payload.

---

## 21) Routers rimanenti (interfaces/api) — audit verificato

### 21.1 `routers/biometrics.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/biometrics.py`

**Finding critici:**
- ❌ **Route duplicate**: `@router.get("/history", ...)` è definita **due volte**:
  - una ritorna `List[BiometricEntryDTO]` (prima)
  - una ritorna `Dict[str, Any]` con `{success, biometrics}` (seconda)
  - Rischio: shadowing / comportamento non deterministico (una sovrascrive l’altra).
- ❌ Error leak: molti `HTTPException(500, detail=f"...{str(e)}")`.
- ⚠️ `get_latest_biometric_for_current_user`: prende `entries[-1]` ma la query in repository ordina ASC → ok solo se garantito sempre ASC; fragile.
- ⚠️ `get_biometric_dashboard`: fa split per tipo in Python (ok per 30 giorni), ma è inefficiente se cresce.

**Direzione miglioramento 2025:**
- Eliminare route duplicate e standardizzare response schema.
- Centralizzare error handling (messaggi generici) + logging server-side.

### 21.2 `routers/exercises.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/exercises.py`

**Finding critici:**
- ❌ `get_all_exercises`: in caso di errore ritorna `[]` (silenzia bug e nasconde problemi dati/DB).
- ⚠️ `get_exercises_by_phase`: carica **tutti** gli esercizi e filtra in Python (`phase_name in ex.phases`).
  - Rischio: performance (N cresce) e manca indice lato DB.

### 21.3 `routers/foods.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/foods.py`

**Finding critici (security):**
- ❌ Endpoint preferiti (`POST /favorites/{food_id}`, `GET /favorites`) accetta `user_id` come query param senza `CurrentUser`.
  - Rischio: un utente può leggere/scrivere preferiti di un altro (IDOR).
- ❌ Error leak: `detail=f"Search failed: {str(e)}"`.
- ⚠️ Caching: `search_foods` salva in cache ogni risultato senza policy/limiti.

### 21.4 `routers/nutrition.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/nutrition.py`

**Finding critici:**
- ❌ Error leak sistematico: `HTTPException(500, detail=str(e))`.
- ⚠️ Repo istanziato direttamente (`NutritionRepositoryImpl(db)`) invece di DI coerente.
- ⚠️ Serializzazione manuale meal/food duplicata (mapping a mano) → rischio drift.

### 21.5 `routers/medical.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/medical.py`

**Finding critici (bug runtime):**
- ❌ `CheckInMessageRequest` **manca** del campo `message`, ma `send_checkin_message` usa `request.message`.
  - Rischio: 422 validation o AttributeError.
- ❌ `PainCheckinRequest` include `mobility_score`, ma la domain entity `PainAssessment` non prevede quel campo.
  - Rischio: `TypeError` in `PainAssessment(...)`.
- ⚠️ Import e uso “mixed style” (`from datetime import datetime` dentro function) + error leak.

**Direzione miglioramento 2025:**
- Allineare i request models ai domain models (o introdurre un DTO specifico con mapping esplicito).
- Uniformare tutto a `CurrentUser` (niente user_id da query per dati utente) e usare policy di autorizzazione.

### 21.6 `routers/progress.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/progress.py`

**Finding critici:**
- ❌ KPI e compliance hardcoded: assume `3 workouts/week` (`workouts_scheduled = int(weeks * 3)`), indipendente da profilo/programma reale.
- ❌ Formula `mobility_score` hardcoded (pain_factor 0.8, consistency_factor 0.5, cap 3).
- ❌ Error leak: `detail=f"Error ...: {str(e)}"`.
- ⚠️ `get_workout_history`: scarica tutti i completed e poi sort/limit in Python (potenzialmente costoso).

### 21.7 `routers/review.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/review.py`

**Finding critici:**
- ❌ Error leak sistematico.
- ⚠️ Rischio coerenza: usa `review_usecase = container.get_weekly_review_usecase(db, user_id=...)` (ok), ma il use case (`weekly_review.py`) contiene bug enum già segnalati.

### 21.8 `routers/wizard.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/wizard.py`

**Finding critici:**
- ⚠️ `start_wizard_interview` accetta `current_user: CurrentUser = None` ma lo usa immediatamente (`current_user.id`).
  - Rischio: se la dependency non viene risolta correttamente → `NoneType`.
- ❌ Error leak: `detail=f"Error ...: {str(e)}"`.
- ⚠️ Il wizard agent è ottenuto via `get_wizard_from_container(db, str(current_user.id))`, che (da audit DI) è un singleton mutabile: rischio cross-request data leak.

### 21.9 `routers/workout_coach.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/workout_coach.py`

**Finding critici:**
- ❌ Logica medical clearance duplicata e hardcoded: `_determine_phase()` e `_get_contraindications()` replicano (e divergono da) orchestrator/domain.
- ❌ Error leak sistematico.
- ⚠️ `GenerateProgramRequest.training_days` non è validato (nessun `ge/le`).

### 21.10 `routers/workouts.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/workouts.py`

**Finding critici (security):**
- ❌ `get_workout_by_id`, `update_exercise_status`, `complete_workout`: non verificano ownership (che `workout.user_id == current_user.id`).
  - Rischio: IDOR su workout id.
- ❌ Error leak sistematico.

### 21.11 `routers/exercise_preferences.py`
**Evidenza:** `apps/backend/src/interfaces/api/routers/exercise_preferences.py`

**Finding critici:**
- ⚠️ Naming collision: campo `metadata` nel request/response, ma nel modello ORM la colonna è `extra_data` (da `models.py`) — rischio runtime (AttributeError / silent drop) a seconda dell’ORM.
- ❌ Error leak: `HTTPException(500, detail=str(e))`.
- ✅ `rollback()` su errore in `set_exercise_preference` (buono).

**Direzione miglioramento 2025 (routers):**
- Standardizzare schema errori + logging.
- Eliminare duplicazioni di logica clinica nei router (spostare in services/use-cases).
- Security: enforcement ownership su risorse (`workout_id`, favorites, ecc.).

---

## 22) Infrastructure rimanente (AI / External / Logging / Security) — audit verificato

### 22.1 Security: duplicazione `security.py` vs `security/deps.py`
**Evidenze:**
- `apps/backend/src/infrastructure/security/security.py`
- `apps/backend/src/infrastructure/security/deps.py`

**Finding critici:**
- ❌ Doppia implementazione di `OAuth2PasswordBearer(tokenUrl="/api/auth/login")` e `get_current_user`.
  - Rischio: divergenza di behavior/error messages e confusione su quale dependency usare.
- ⚠️ In `deps.py` i messaggi sono in inglese (`"Could not validate credentials"`), mentre altrove sono IT.

### 22.2 Logging: side-effects su import
**Evidenza:** `apps/backend/src/infrastructure/logging/logger.py`

**Finding critici:**
- ❌ `setup_logging(...)` viene eseguito a import time (inizializza root logger e svuota handlers).
  - Rischio: interferenze con logging di Uvicorn/Gunicorn e con librerie; non deterministic in multi-worker.
- ⚠️ “ColoredFormatter” usa escape ANSI; ok dev, ma va evitato se log aggregators non gestiscono escape.

### 22.3 AI: `UserContextRAG` (Chroma) come singleton globale
**Evidenza:** `apps/backend/src/infrastructure/ai/user_context_rag.py`

**Finding critici:**
- ⚠️ Singleton globale `_user_context_rag`.
  - Rischio: lifecycle non controllato, crash durante import/inizializzazione.
- ⚠️ Defaults hardcoded: `CHROMA_HOST=localhost`, `CHROMA_PORT=8000`.
- ⚠️ `doc_id` basato su timestamp `YYYYmmdd_HHMMSS` → collisione possibile se più store nello stesso secondo.
- ⚠️ `get_user_profile_context()` genera embedding per la stringa `category` e query per categoria: è un hack; qualità retrieval incerta.

### 22.4 AI: `langgraph_orchestrator.py`
**Evidenza:** `apps/backend/src/infrastructure/ai/langgraph_orchestrator.py`

**Finding critici:**
- ❌ Routing keyword-based hardcoded.
- ❌ Error leak: in `except` ritorna `"Errore nell'elaborazione: {str(e)}"` al client.
- ⚠️ Default state hardcoded (`clearance_level='yellow'`, `recovery_phase='phase_2'`).

### 22.5 External: `fatsecret_service.py`
**Evidenza:** `apps/backend/src/infrastructure/external/fatsecret_service.py`

**Finding critici:**
- ❌ In assenza credenziali usa `mock_token` e **mock responses** in modo silenzioso (con `print`).
  - Rischio: prod che sembra funzionare ma serve dati finti.
- ❌ `print(...)` per errori token/API.
- ⚠️ `get_food_categories()` hardcoded con emoji (UI concern in backend) e non configurabile.

### 22.6 External: `exercise_library.py`
**Evidenza:** `apps/backend/src/infrastructure/external/exercise_library.py`

**Finding critici (bug runtime):**
- ❌ Bug: `get_exercises_for_phase` usa `if phase in ex.phase` ma il campo è `ex.phases`.
  - Rischio: AttributeError o nessun esercizio ritornato.
- ❌ `print(...)` + fallback `_create_default_exercises()`.
- ⚠️ Path default `data/exercises.json` hardcoded (dipende da cwd).

### 22.7 External: Google Fit / Calendar
**Evidenze:**
- `apps/backend/src/infrastructure/external/google_fit_service.py`
- `apps/backend/src/infrastructure/external/google_calendar_service.py`

**Finding critici:**
- ⚠️ Google Fit: dataSourceId hardcoded (ok, ma da centralizzare) + timezone-naive.
- ⚠️ Google Calendar: timezone hardcoded `Europe/Rome` e `colorId='11'` hardcoded.
  - Rischio: utenti fuori EU/Rome.

**Direzione miglioramento 2025 (infrastructure):**
- Eliminare `print` e usare logger unico (`get_logger`).
- Fail-fast in produzione per provider esterni quando feature è abilitata (FatSecret/Chroma/Google).
- Centralizzare config in `settings` + feature flags + sane defaults per dev.

### 22.8 AI Tools (LangChain): duplicazioni, bug runtime e signature incoerenti
**Evidenze:**
- `apps/backend/src/infrastructure/ai/tools/agent_tools.py`
- `apps/backend/src/infrastructure/ai/tools/smart_medical_tools.py`
- `apps/backend/src/infrastructure/ai/tools/smart_workout_tools.py`
- `apps/backend/src/infrastructure/ai/tools/smart_nutrition_tools.py`
- `apps/backend/src/infrastructure/ai/tools/pain_tools.py`
- `apps/backend/src/infrastructure/ai/tools/workout_tools.py`

**Finding BLOCCANTI (runtime):**
- ❌ `agent_tools.py` → in `validate_exercise(...)` usa `for loc in pain_locations:` ma `pain_locations` **non è definita** nel scope.
  - Impatto: crash del tool `exercise_validator` al primo uso.
- ❌ `agent_tools.py` → chiama `exercise_library.get_exercise_by_name(...)` ma in `ExerciseLibrary` esiste `get_by_id`/`get_by_category`/`get_safe_exercises` (non `get_exercise_by_name`).
  - Impatto: AttributeError o fallback non gestito.

**Finding critici (design/collisioni):**
- ❌ Duplicazione nomi tool: esistono più implementazioni con lo stesso `name` (`pain_analyzer`, `red_flags_detector`, `progression_calculator`, `exercise_validator`) in moduli diversi.
  - Impatto: comportamento non deterministico a seconda di quale set tools viene caricato; difficile debugging.
- ⚠️ `smart_medical_tools.create_pain_trend_tool` restituisce `Tool(... func=lambda uid: analyze_pain_trend(uid))` → perde il parametro `days` (hardcoded 7).
- ⚠️ `smart_workout_tools.create_safe_exercises_tool` usa `func=lambda q: find_safe_exercises(q)` → perde `phase` (hardcoded `fase 2`).
- ⚠️ `smart_workout_tools.create_progression_advisor_tool` usa `func=lambda p: advise_progression(p, 0, 2)` → ignora `pain_level` e `weeks_in_phase` reali (hardcoded).
- ⚠️ `smart_nutrition_tools.create_smart_food_search_tool` dichiara `include_api` ma poi imposta `func=lambda q: search_food_smart(q, include_api=False)` → flag incoerente (di fatto ignorato).

**Finding qualitativi (prod 2025):**
- ⚠️ Molto contenuto hardcoded (template workout, sostituzioni, criteri) dentro i tools → difficoltà di versioning e A/B test.
- ⚠️ Output dei tool include emoji e testo “presentazionale” (ok UX), ma dovrebbe essere separato da “structured output” per orchestrazione/validazione.

### 22.9 AI: SSE `streaming_service.py` (observability + error leak)
**Evidenza:** `apps/backend/src/infrastructure/ai/streaming_service.py`

**Finding critici:**
- ⚠️ Timestamp timezone-naive (`datetime.now().isoformat()`).
- ❌ Error leak parziale: invia al client `"Switching provider: {str(e)[:50]}"`.
  - Impatto: può rivelare dettagli di provider/keys/config o errori interni.
- ⚠️ `settings` importato ma non usato (segnale di drift e confusione di config).
- ⚠️ Nessun keep-alive/ping SSE, nessun retry/backoff esplicito, e nessuna gestione di disconnessione client.

**Direzione miglioramento 2025 (tools/streaming):**
- Unificare toolset: una sola sorgente di verità per `pain_analyzer`/`red_flags_detector`/`progression_calculator`/`exercise_validator`.
- Rendere i tool `StructuredTool` con input/output tipizzati (Pydantic) e JSON deterministico (niente lambdas che perdono args).
- Streaming: usare timestamp aware, mascherare errori verso client, aggiungere keepalive SSE, e correlazione request_id/session_id nei log.

---

## 23) Checklist file-by-file (coverage 100%) — stato audit

Legenda stato:
- **ANALIZZATO**: letto e auditato nel report.
- **DA RIFATTORIZZARE**: non bloccante ma priorità alta (design/quality/perf/security).
- **BLOCCANTE**: bug/runtime o rischio produzione immediato.
- **TODO**: letto parzialmente o da rivedere con più dettaglio.

### 23.1 Root
| File | Stato |
| --- | --- |
| `apps/backend/src/__init__.py` | ANALIZZATO |

### 23.2 Application
| File | Stato |
| --- | --- |
| `apps/backend/src/application/__init__.py` | ANALIZZATO |
| `apps/backend/src/application/dtos/__init__.py` | ANALIZZATO |
| `apps/backend/src/application/dtos/dtos.py` | DA RIFATTORIZZARE |
| `apps/backend/src/application/services/__init__.py` | ANALIZZATO |
| `apps/backend/src/application/services/agent_orchestrator.py` | DA RIFATTORIZZARE |
| `apps/backend/src/application/use_cases/__init__.py` | ANALIZZATO |
| `apps/backend/src/application/use_cases/ask_medical.py` | DA RIFATTORIZZARE |
| `apps/backend/src/application/use_cases/ask_nutritionist.py` | DA RIFATTORIZZARE |
| `apps/backend/src/application/use_cases/ask_workout_coach.py` | DA RIFATTORIZZARE |
| `apps/backend/src/application/use_cases/checkin_conversational.py` | DA RIFATTORIZZARE |
| `apps/backend/src/application/use_cases/generate_diet.py` | DA RIFATTORIZZARE |
| `apps/backend/src/application/use_cases/generate_workout.py` | DA RIFATTORIZZARE |
| `apps/backend/src/application/use_cases/onboarding.py` | DA RIFATTORIZZARE |
| `apps/backend/src/application/use_cases/record_biometric.py` | DA RIFATTORIZZARE |
| `apps/backend/src/application/use_cases/weekly_review.py` | DA RIFATTORIZZARE |

### 23.3 Domain
| File | Stato |
| --- | --- |
| `apps/backend/src/domain/__init__.py` | ANALIZZATO |
| `apps/backend/src/domain/entities/__init__.py` | ANALIZZATO |
| `apps/backend/src/domain/entities/biometric.py` | DA RIFATTORIZZARE |
| `apps/backend/src/domain/entities/food.py` | ANALIZZATO |
| `apps/backend/src/domain/entities/nutrition.py` | DA RIFATTORIZZARE |
| `apps/backend/src/domain/entities/pain_assessment.py` | DA RIFATTORIZZARE |
| `apps/backend/src/domain/entities/progress_kpi.py` | DA RIFATTORIZZARE |
| `apps/backend/src/domain/entities/user.py` | DA RIFATTORIZZARE |
| `apps/backend/src/domain/entities/user_profile.py` | DA RIFATTORIZZARE |
| `apps/backend/src/domain/entities/workout_session.py` | DA RIFATTORIZZARE |
| `apps/backend/src/domain/events/__init__.py` | TODO |
| `apps/backend/src/domain/repositories/__init__.py` | ANALIZZATO |
| `apps/backend/src/domain/repositories/biometric_repository.py` | ANALIZZATO |
| `apps/backend/src/domain/repositories/chat_repository.py` | ANALIZZATO |
| `apps/backend/src/domain/repositories/food_repository.py` | ANALIZZATO |
| `apps/backend/src/domain/repositories/kpi_repository.py` | ANALIZZATO |
| `apps/backend/src/domain/repositories/nutrition_repository.py` | ANALIZZATO |
| `apps/backend/src/domain/repositories/pain_repository.py` | ANALIZZATO |
| `apps/backend/src/domain/repositories/user_repository.py` | ANALIZZATO |
| `apps/backend/src/domain/repositories/workout_repository.py` | ANALIZZATO |
| `apps/backend/src/domain/services/__init__.py` | ANALIZZATO |
| `apps/backend/src/domain/services/pain_analyzer.py` | DA RIFATTORIZZARE |
| `apps/backend/src/domain/services/progression_engine.py` | DA RIFATTORIZZARE |
| `apps/backend/src/domain/services/red_flags_checker.py` | DA RIFATTORIZZARE |
| `apps/backend/src/domain/value_objects/__init__.py` | TODO |

### 23.4 Interfaces (API)
| File | Stato |
| --- | --- |
| `apps/backend/src/interfaces/__init__.py` | ANALIZZATO |
| `apps/backend/src/interfaces/api/__init__.py` | ANALIZZATO |
| `apps/backend/src/interfaces/api/main.py` | DA RIFATTORIZZARE |
| `apps/backend/src/interfaces/api/routers/__init__.py` | ANALIZZATO |
| `apps/backend/src/interfaces/api/routers/auth.py` | DA RIFATTORIZZARE |
| `apps/backend/src/interfaces/api/routers/biometrics.py` | BLOCCANTE |
| `apps/backend/src/interfaces/api/routers/exercise_preferences.py` | DA RIFATTORIZZARE |
| `apps/backend/src/interfaces/api/routers/exercises.py` | DA RIFATTORIZZARE |
| `apps/backend/src/interfaces/api/routers/foods.py` | BLOCCANTE |
| `apps/backend/src/interfaces/api/routers/google.py` | DA RIFATTORIZZARE |
| `apps/backend/src/interfaces/api/routers/knowledge_base.py` | DA RIFATTORIZZARE |
| `apps/backend/src/interfaces/api/routers/medical.py` | BLOCCANTE |
| `apps/backend/src/interfaces/api/routers/nutrition.py` | DA RIFATTORIZZARE |
| `apps/backend/src/interfaces/api/routers/plans.py` | DA RIFATTORIZZARE |
| `apps/backend/src/interfaces/api/routers/progress.py` | DA RIFATTORIZZARE |
| `apps/backend/src/interfaces/api/routers/review.py` | DA RIFATTORIZZARE |
| `apps/backend/src/interfaces/api/routers/streaming.py` | DA RIFATTORIZZARE |
| `apps/backend/src/interfaces/api/routers/users.py` | DA RIFATTORIZZARE |
| `apps/backend/src/interfaces/api/routers/wizard.py` | DA RIFATTORIZZARE |
| `apps/backend/src/interfaces/api/routers/workout_coach.py` | DA RIFATTORIZZARE |
| `apps/backend/src/interfaces/api/routers/workouts.py` | BLOCCANTE |
| `apps/backend/src/interfaces/api/schemas/__init__.py` | TODO |

### 23.5 Infrastructure
| File | Stato |
| --- | --- |
| `apps/backend/src/infrastructure/__init__.py` | ANALIZZATO |
| `apps/backend/src/infrastructure/config/__init__.py` | ANALIZZATO |
| `apps/backend/src/infrastructure/config/settings.py` | BLOCCANTE |
| `apps/backend/src/infrastructure/config/dependencies.py` | BLOCCANTE |
| `apps/backend/src/infrastructure/logging/__init__.py` | ANALIZZATO |
| `apps/backend/src/infrastructure/logging/logger.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/security/security.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/security/deps.py` | DA RIFATTORIZZARE |

#### 23.5.1 Infrastructure — AI
| File | Stato |
| --- | --- |
| `apps/backend/src/infrastructure/ai/__init__.py` | ANALIZZATO |
| `apps/backend/src/infrastructure/ai/llm_service.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/ai/rag_service.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/ai/google_embeddings.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/ai/user_context_rag.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/ai/langgraph_orchestrator.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/ai/streaming_service.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/ai/agents/__init__.py` | ANALIZZATO |
| `apps/backend/src/infrastructure/ai/agents/medical_agent.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/ai/agents/nutrition_agent.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/ai/agents/workout_coach.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/ai/agents/wizard_agent.py` | TODO |
| `apps/backend/src/infrastructure/ai/tools/__init__.py` | TODO |
| `apps/backend/src/infrastructure/ai/tools/agent_tools.py` | BLOCCANTE |
| `apps/backend/src/infrastructure/ai/tools/pain_tools.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/ai/tools/workout_tools.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/ai/tools/smart_medical_tools.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/ai/tools/smart_workout_tools.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/ai/tools/smart_nutrition_tools.py` | DA RIFATTORIZZARE |

#### 23.5.2 Infrastructure — External
| File | Stato |
| --- | --- |
| `apps/backend/src/infrastructure/external/__init__.py` | ANALIZZATO |
| `apps/backend/src/infrastructure/external/fatsecret_service.py` | BLOCCANTE |
| `apps/backend/src/infrastructure/external/exercise_library.py` | BLOCCANTE |
| `apps/backend/src/infrastructure/external/google_oauth_service.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/external/google_fit_service.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/external/google_calendar_service.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/external/youtube_service.py` | DA RIFATTORIZZARE |

#### 23.5.3 Infrastructure — Persistence
| File | Stato |
| --- | --- |
| `apps/backend/src/infrastructure/persistence/__init__.py` | ANALIZZATO |
| `apps/backend/src/infrastructure/persistence/database.py` | BLOCCANTE |
| `apps/backend/src/infrastructure/persistence/models.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/persistence/food_models.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/persistence/nutrition_models.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/persistence/repositories/__init__.py` | ANALIZZATO |
| `apps/backend/src/infrastructure/persistence/repositories/user_repository_impl.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/persistence/repositories/chat_repository_impl.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/persistence/repositories/workout_repository_impl.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/persistence/repositories/pain_repository_impl.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/persistence/repositories/kpi_repository_impl.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/persistence/repositories/biometric_repository_impl.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/persistence/repositories/nutrition_repository_impl.py` | BLOCCANTE |
| `apps/backend/src/infrastructure/persistence/repositories/food_repository_impl.py` | BLOCCANTE |
| `apps/backend/src/infrastructure/persistence/repositories/weekly_plans_repository.py` | DA RIFATTORIZZARE |
| `apps/backend/src/infrastructure/persistence/repositories/wizard_session_repository.py` | DA RIFATTORIZZARE |

## 24) Conclusion & Recommendations 2025

Based on the comprehensive audit of the `ironRep` backend codebase, the following strategic recommendations are proposed to elevate the system to a production-ready, enterprise-grade ("Ferrari-level") standard by 2025.

### 24.1 High Priority: Architecture & Configuration
- **Centralized Configuration**: Eliminate all hardcoded values (URLs, credentials, magic numbers, prompts). Refactor `settings.py` to be the single source of truth, utilizing Pydantic `BaseSettings` for strict environment validation (fail-fast in strict modes).
- **Dependency Injection**: Refactor `dependencies.py` to support lazy initialization and prevent side-effects at import time. Ensure `container` usage is thread-safe and request-scoped where appropriate.
- **Domain Consolidation**: Merge `User` and `UserProfile` entities to eliminate conceptual duplication. Enforce the use of `Enum` and `ValueObjects` across the Domain layer to replace loose string typing (e.g., Phases, Diet Types).

### 24.2 High Priority: Security & Reliability
- **Auth Hardening**: Centralize authentication logic. Implement rate limiting on sensitive endpoints (Login, Register). Enforce ownership checks (IDOR protection) on all resource access (Workouts, Favorites, Profiles).
- **Error Handling**: Standardize system-wide error responses. Prevent leaking internal exception details (`str(e)`) to clients. Implement structured, server-side logging with correlation IDs for full traceability.

### 24.3 High Priority: AI & Data Integrity
- **RAG & Tools Robustness**: Decouple "presentation" (emoji/text) from "logic" in AI tools. Use structured schemas (Pydantic) for all Tool inputs/outputs. Ensure `rag_service.py` has clear, idempotent ingestion pipelines (or is strictly disabled for specific domains like Nutrition).
- **FatSecret Consolidation**: Strictly enforce FatSecret as the *sole* source of truth for food data. Ensure deep integration with proper caching (UPSERT strategies) and fail-safe nutrient parsing (kJ/kcal).

### 24.4 Medium Priority: Observability & Quality
- **Structured Logging**: Replace all `print()` statements with a unified structured logger (JSON format in prod).
- **Test Coverage**: Expand unit and integration tests to cover critical use-cases (Onboarding, Plan Generation, Payment Flow) to achieve >80% effective coverage.

### 24.5 Roadmap
1.  **Phase 1 (Immediate)**: Security fixes (IDOR, Secrets), Config centralization, FatSecret enforcement. (Completed/In-progress).
2.  **Phase 2**: Domain refactor (User/Profile merge), Enum adoption, Logging standardization.
3.  **Phase 3**: Performance optimization (Lazy imports, Database indexing, N+1 query elimination).
