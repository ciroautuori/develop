# 🏗️ ARCHITETTURA DDD - ironRep

## 📐 Domain-Driven Design Overview

Questo progetto segue i principi **Domain-Driven Design (DDD)** per separare chiaramente le responsabilità e rendere il codice manutenibile e scalabile.

## 🎯 Bounded Context

**ironRep** è un sistema di riabilitazione intelligente per sciatica con un unico bounded context:
- **Sciatica Recovery Management**

## 📁 Struttura Directory

```
ironRep/
├── src/
│   ├── domain/                      # CUORE DEL BUSINESS
│   │   ├── __init__.py
│   │   ├── entities/                # Entità del dominio
│   │   │   ├── __init__.py
│   │   │   ├── pain_assessment.py   # Entità valutazione dolore
│   │   │   ├── workout_session.py   # Entità sessione allenamento
│   │   │   ├── user_profile.py      # Entità utente
│   │   │   └── progress_kpi.py      # Entità indicatori progresso
│   │   ├── value_objects/           # Value Objects immutabili
│   │   │   ├── __init__.py
│   │   │   ├── pain_level.py        # VO: livello dolore (0-10)
│   │   │   ├── pain_location.py     # VO: localizzazione dolore
│   │   │   ├── exercise.py          # VO: esercizio
│   │   │   └── phase.py             # VO: fase riabilitazione
│   │   ├── repositories/            # Interfacce repository
│   │   │   ├── __init__.py
│   │   │   ├── pain_repository.py
│   │   │   ├── workout_repository.py
│   │   │   └── kpi_repository.py
│   │   ├── services/                # Domain Services
│   │   │   ├── __init__.py
│   │   │   ├── pain_analyzer.py     # Analisi pattern dolore
│   │   │   ├── progression_engine.py # Logica progressione
│   │   │   └── red_flags_checker.py # Controllo red flags
│   │   └── events/                  # Domain Events
│   │       ├── __init__.py
│   │       ├── pain_recorded.py
│   │       └── workout_completed.py
│   │
│   ├── application/                 # LOGICA APPLICATIVA
│   │   ├── __init__.py
│   │   ├── use_cases/               # Casi d'uso
│   │   │   ├── __init__.py
│   │   │   ├── daily_checkin.py     # UC: Check-in giornaliero
│   │   │   ├── generate_workout.py  # UC: Genera workout
│   │   │   ├── weekly_review.py     # UC: Revisione settimanale
│   │   │   └── ask_coach.py         # UC: Chatbot coach
│   │   ├── dtos/                    # Data Transfer Objects
│   │   │   ├── __init__.py
│   │   │   ├── pain_assessment_dto.py
│   │   │   ├── workout_dto.py
│   │   │   └── kpi_dto.py
│   │   └── services/                # Application Services
│   │       ├── __init__.py
│   │       └── workout_orchestrator.py
│   │
│   ├── infrastructure/              # IMPLEMENTAZIONI CONCRETE
│   │   ├── __init__.py
│   │   ├── persistence/             # Database
│   │   │   ├── __init__.py
│   │   │   ├── database.py          # Setup SQLAlchemy
│   │   │   ├── models.py            # ORM Models
│   │   │   └── repositories/        # Implementazioni repository
│   │   │       ├── __init__.py
│   │   │       ├── pain_repository_impl.py
│   │   │       ├── workout_repository_impl.py
│   │   │       └── kpi_repository_impl.py
│   │   ├── ai/                      # AI & LLM
│   │   │   ├── __init__.py
│   │   │   ├── llm_service.py       # LLM con fallback chain
│   │   │   ├── agents/              # AI Agents
│   │   │   │   ├── __init__.py
│   │   │   │   ├── sciatica_coach.py
│   │   │   │   └── education_assistant.py
│   │   │   └── tools/               # LangChain Tools
│   │   │       ├── __init__.py
│   │   │       ├── pain_analysis_tool.py
│   │   │       ├── workout_generator_tool.py
│   │   │       ├── progression_calculator_tool.py
│   │   │       ├── red_flags_detector_tool.py
│   │   │       └── exercise_validator_tool.py
│   │   ├── external/                # Servizi esterni
│   │   │   ├── __init__.py
│   │   │   └── exercise_library.py  # Libreria esercizi
│   │   └── config/                  # Configurazione
│   │       ├── __init__.py
│   │       ├── settings.py          # Settings da .env
│   │       └── dependencies.py      # Dependency Injection
│   │
│   └── interfaces/                  # INTERFACCE UTENTE E API
│       ├── __init__.py
│       ├── api/                     # REST API
│       │   ├── __init__.py
│       │   ├── main.py              # FastAPI app
│       │   ├── routers/             # API Routers
│       │   │   ├── __init__.py
│       │   │   ├── checkin.py       # /daily-checkin
│       │   │   ├── review.py        # /weekly-review
│       │   │   ├── coach.py         # /ask-coach
│       │   │   └── dashboard.py     # /progress-dashboard
│       │   └── schemas/             # Pydantic Schemas
│       │       ├── __init__.py
│       │       ├── pain_schema.py
│       │       ├── workout_schema.py
│       │       └── response_schema.py
│       └── ui/                      # User Interface
│           ├── __init__.py
│           └── streamlit_app.py     # Streamlit Dashboard
│
├── tests/                           # TEST SUITE
│   ├── __init__.py
│   ├── unit/                        # Unit tests
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── integration/                 # Integration tests
│   └── e2e/                         # End-to-end tests
│
├── data/                            # DATI STATICI
│   ├── exercises.json               # Database esercizi
│   ├── knowledge_base.json          # Contenuti educativi
│   └── phases.json                  # Fasi riabilitazione
│
├── .env                             # Environment variables
├── .env.example                     # Template .env
├── requirements.txt                 # Dipendenze Python
├── README.md                        # Documentazione
├── ARCHITECTURE.md                  # Questo file
└── pyproject.toml                   # Poetry config (opzionale)
```

## 🔵 Layer 1: DOMAIN (Business Logic Core)

### Entities
Oggetti con identità unica e ciclo di vita:
- `PainAssessment`: Valutazione dolore con timestamp
- `WorkoutSession`: Sessione allenamento con esercizi
- `UserProfile`: Profilo utente con storico
- `ProgressKPI`: Indicatori progresso settimanali

### Value Objects
Oggetti immutabili senza identità:
- `PainLevel`: Livello dolore (0-10) validato
- `PainLocation`: Enum localizzazioni
- `Exercise`: Esercizio con parametri
- `Phase`: Fase riabilitazione

### Domain Services
Logica business che non appartiene a una singola entità:
- `PainAnalyzer`: Analisi trend e pattern
- `ProgressionEngine`: Decisioni progressione
- `RedFlagsChecker`: Validazione sintomi allarmanti

### Repositories (Interfaces)
Contratti per persistenza (implementati in Infrastructure):
- `IPainRepository`
- `IWorkoutRepository`
- `IKPIRepository`

## 🟢 Layer 2: APPLICATION (Use Cases)

### Use Cases
Orchestrazione logica applicativa:
- `DailyCheckInUseCase`: Workflow check-in completo
- `GenerateWorkoutUseCase`: Generazione workout adattivo
- `WeeklyReviewUseCase`: Revisione settimanale automatica
- `AskCoachUseCase`: Interazione chatbot

### DTOs
Oggetti trasferimento dati tra layers:
- `PainAssessmentDTO`
- `WorkoutDTO`
- `KPIDTO`

## 🟡 Layer 3: INFRASTRUCTURE (Technical)

### Persistence
- SQLAlchemy setup e sessionmaker
- ORM Models (mappati da Domain Entities)
- Concrete Repository implementations

### AI & LLM
- `LLMService`: Gestione LLM con fallback chain
- `SciaticaCoachAgent`: Agente principale LangChain
- `EducationAssistant`: Chatbot educativo
- 5 Tools personalizzati

### External Services
- Exercise library loader
- Knowledge base retriever

## 🔴 Layer 4: INTERFACES (User-facing)

### REST API (FastAPI)
- Router modulari per dominio
- Pydantic schemas per validazione
- Dependency injection

### UI (Streamlit)
- Dashboard interattiva
- Forms e visualizzazioni

## 🔄 Flusso Tipico (Daily Check-in)

```
[USER] → Streamlit Form
    ↓
[INTERFACES] → POST /daily-checkin (FastAPI Router)
    ↓
[APPLICATION] → DailyCheckInUseCase.execute()
    ↓
[DOMAIN] → PainAnalyzer.analyze_trend()
    ↓
[INFRASTRUCTURE] → PainRepositoryImpl.get_last_7_days()
    ↓
[INFRASTRUCTURE] → LLMService.call_agent()
    ↓ (con Tools)
[INFRASTRUCTURE] → WorkoutGeneratorTool.run()
    ↓
[APPLICATION] → Return WorkoutDTO
    ↓
[INTERFACES] → JSON Response
    ↓
[USER] → Streamlit Display
```

## 📊 Dependency Flow

```
INTERFACES → APPLICATION → DOMAIN ← INFRASTRUCTURE
     ↓            ↓           ↑
     └──────────────────────────┘
         (Dependency Injection)
```

**Regola d'oro**:
- Domain NON dipende da nessuno (puro business logic)
- Infrastructure implementa interfacce del Domain
- Application orchestra Domain + Infrastructure
- Interfaces usa Application

## 🎯 Vantaggi DDD

1. **Testabilità**: Domain logic testabile senza DB/API
2. **Manutenibilità**: Responsabilità chiare
3. **Scalabilità**: Facile aggiungere features
4. **Indipendenza**: Domain disaccoppiato da tech stack

## 🚀 Next Steps

1. Creare directory structure
2. Implementare Domain entities e value objects
3. Implementare Repository interfaces
4. Implementare Use Cases
5. Implementare Infrastructure (DB, LLM, Tools)
6. Implementare Interfaces (API, UI)
7. Testing layer by layer
