# Architettura di StudioCentOS

## Panoramica del Sistema

StudioCentOS è una piattaforma Enterprise Full-Stack che integra funzionalità avanzate di AI Generativa con una solida architettura backend e un frontend moderno. Il sistema segue una rigorosa separazione delle responsabilità (Separation of Concerns).

### 🏗️ Macro Architettura

Il sistema è composto da 3 pilastri principali:

1.  **Frontend (`apps/frontend`)**:
    *   **Tech Stack**: React 18, Vite, TypeScript, TailwindCSS, Radix UI.
    *   **Struttura**: Monorepo feature-based (`features/landing`, `features/admin`, `features/support`).
    *   **Entry Point**: `main.tsx` gestisce l'idratazione e il pre-rendering.
    *   **Core Components**:
        *   **Landing Page**: Vetrina pubblica ottimizzata SEO (`StudiocentosLanding.tsx`).
        *   **Admin Dashboard**: Pannello di controllo per la gestione del business e dei tool AI.
    *   **Integrazione API**: Client centralizzato in `shared/lib/api.ts` con gestione automatica Auth (JWT).

2.  **Backend (`apps/backend`)**:
    *   **Ruolo**: "Le Braccia" del sistema (Gestione dati, Business Logic, Persistenza).
    *   **Tech Stack**: Python 3.12, FastAPI, SQLAlchemy (Async), PostgreSQL, Redis.
    *   **Design Pattern**: Domain-Driven Design (DDD). I domini sono isolati in `app/domain/` (es. `auth`, `marketing`, `finance`).
    *   **Funzionalità Chiave**:
        *   Auth OAuth2 (Google, LinkedIn) + JWT.
        *   Gestione completa Marketing (Email, Social, Campagne).
        *   Scheduler per task ricorrenti (invio post, reminder).
        *   Integrazioni esterne (Stripe, Google APIs).

3.  **AI Microservice (`apps/ai_microservice`)**:
    *   **Ruolo**: "Il Cervello" (Generazione Contenuti, RAG, Analisi).
    *   **Tech Stack**: Python 3.12, FastAPI, LangChain.
    *   **Capabilities**:
        *   **Multi-Model**: Integra vari LLM (GROQ llama-3.3, Gemini, GPT).
        *   **Image Gen**: NanoBananaPRO, Pollinations.
        *   **Agenti Specializzati**: `ContentCreator`, `SEOSpecialist`, `SocialMediaManager`, etc.
    *   **Storage**: Serve file statici generati (immagini/video) da `/app/media/generated`.

---

## 🔄 Flusso dei Dati

1.  **Utente** interagisce con il **Frontend**.
2.  **Frontend** chiama il **Backend** (`/api/v1/...`) per operazioni CRUD (salvare un post, leggere analytics).
3.  Per operazioni "Intelligenti" (es. "Genera un post su LinkedIn"):
    *   L'utente richiede la generazione.
    *   Il **Frontend** (o il Backend stesso) invoca l'**AI Microservice**.
    *   L'AI Microservice elabora (LLM inference) e restituisce il risultato (testo, immagine).
    *   Il risultato viene salvato nel db del **Backend** o restituito al Frontend per la preview.

## 📂 Struttura Cartelle Chiave

```
studiocentos_ws/
├── apps/
│   ├── frontend/          # React App
│   │   ├── src/features/  # Moduli funzionali (Admin, Landing...)
│   │   └── src/shared/    # Componenti e lib condivise (api.ts)
│   ├── backend/           # FastAPI Core
│   │   ├── app/domain/    # Logica di business divisa per domini
│   │   └── app/main.py    # Entry point e routing globale
│   └── ai_microservice/   # AI Engine
│       ├── app/core/      # Configurazione AI
│       └── app/api/       # Endpoints specifici per task AI
└── config/                # Configurazioni Docker e Env
```
