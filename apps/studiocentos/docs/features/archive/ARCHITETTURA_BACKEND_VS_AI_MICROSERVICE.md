# 📊 ANALISI ARCHITETTURA: Backend vs AI Microservice

> Documento generato: 29 Novembre 2025
> Aggiornato: 29 Novembre 2025 - DUPLICATI RISOLTI
> Autore: Cascade AI Analysis

---

## 🎯 EXECUTIVE SUMMARY

| Aspetto | Status | Note |
|---------|--------|------|
| **Architettura** | ✅ CORRETTA | Separazione responsabilità rispettata |
| **Duplicati** | ✅ RISOLTI | Backend ora proxya a AI Microservice |
| **Comunicazione** | ✅ CORRETTA | Backend proxya ad AI Service |
| **Database** | ✅ CORRETTA | Solo backend accede a PostgreSQL |

### ✅ FIX APPLICATI (29/11/2025)

1. **Support Chat**: `support/routers.py` ora usa `ai_proxy.py` → AI Microservice
2. **Marketing Content**: `copilot/routers.py` ora proxya a `/api/v1/marketing/content/generate`
3. **Copilot Chat**: `copilot/routers.py` ora proxya a `/api/v1/support/chat`

---

## 📁 STRUTTURA DOMINI

### Backend (`apps/backend/app/domain/`)

```
domain/
├── analytics/        # Analytics interni (eventi, stats)
├── auth/             # Autenticazione (JWT, OAuth, MFA)
├── booking/          # Prenotazioni (calendar, slots)
├── customers/        # CRM clienti
├── finance/          # Gestione finanziaria
├── google/           # ✨ NUOVO: GA4 + GMB integration
├── marketing/        # Lead management + Email campaigns
├── notifications/    # WebSocket + Email notifications
├── portfolio/        # Progetti + Servizi
├── quotes/           # Preventivi
├── support/          # Ticket support + AI chatbot
└── copilot/          # 🔄 PROXY: Instrada a AI Service
```

### AI Microservice (`apps/ai_microservice/app/domain/`)

```
domain/
├── marketing/        # Content generation + Image AI
├── rag/              # RAG embeddings + vector stores
└── support/          # Chatbot AI avanzato
```

---

## 🔍 ANALISI DETTAGLIATA PER DOMINIO

### 1. SUPPORT (Chatbot)

| Componente | Backend | AI Microservice | Status |
|------------|---------|-----------------|--------|
| File | `support/ai_service.py` | `support/chatbot.py` | ⚠️ DUPLICATO |
| Classe | `AICustomerSupport` | `AICustomerSupport` | ⚠️ STESSO NOME |
| Providers | gemini, openai, ollama | groq, huggingface, gemini, openrouter, ollama | ✅ AI ha più provider |
| Context | CV-Lab oriented | StudioCentOS oriented | ✅ Diverso context |

#### ⚠️ PROBLEMA IDENTIFICATO
```
Backend:      support/ai_service.py → AICustomerSupport
AI Service:   support/chatbot.py   → AICustomerSupport (versione aggiornata)
```

**RACCOMANDAZIONE**: Il backend dovrebbe usare SOLO il proxy al microservice.
Attualmente il backend ha una copia locale che potrebbe essere stale.

#### DIFFERENZE CHIAVE:

| Aspetto | Backend | AI Microservice |
|---------|---------|-----------------|
| Providers | 3 (gemini, openai, ollama) | 5 (groq, huggingface, gemini, openrouter, ollama) |
| Priority | gemini first | groq first (FREE!) |
| Key Rotation | ❌ No | ✅ Sì (GROQ keys) |
| Health Check | ❌ No | ✅ Sì |
| System Context | CV-Lab | StudioCentOS (aggiornato) |

---

### 2. MARKETING (Content + Images)

| Componente | Backend | AI Microservice | Status |
|------------|---------|-----------------|--------|
| Content Generation | `copilot/routers.py` | `marketing/content_creator.py` | ⚠️ OVERLAP |
| Image Generation | `copilot/routers.py` (proxy) | `marketing/image_generator_agent.py` | ✅ CORRETTA ARCH |
| Lead Management | `marketing/service.py` | ❌ Non presente | ✅ CORRETTO |
| Email Campaigns | `marketing/service.py` | ❌ Non presente | ✅ CORRETTO |

#### BACKEND - copilot/routers.py (856 linee)

```python
# Endpoint che genera contenuto LOCALMENTE (non proxy)
@router.post("/marketing/generate")
async def generate_marketing_content():
    # 317 linee di template marketing hardcoded
    # Prodotti StudioCentOS, prezzi, hashtag
    # NON USA AI! Solo template statici

# Endpoint che USA PROXY correttamente
@router.post("/image/generate")
async def generate_image():
    ai_service_url = os.getenv("AI_SERVICE_URL", "http://ai_microservice:8001")
    response = await client.post(f"{ai_service_url}/api/v1/marketing/image/generate")
```

#### AI MICROSERVICE - marketing/content_creator.py (697 linee)

```python
# Agent avanzato con LLM reale
class ContentCreatorAgent(BaseAgent):
    async def generate_blog_post()    # Con GROQ LLM
    async def generate_social_post()  # Con hashtags AI
    async def generate_ad_copy()      # Con CTA AI
    async def generate_video_script() # Formattato con timestamp
```

#### ⚠️ PROBLEMA IDENTIFICATO

```
Backend /api/v1/copilot/marketing/generate → Template STATICI (no AI)
AI Service /api/v1/marketing/content/* → LLM REALE (GROQ/Gemini)
```

**RACCOMANDAZIONE**: Backend copilot dovrebbe proxyare anche content generation
come già fa per image generation.

---

### 3. LEAD FINDER

| Componente | Backend | AI Microservice | Status |
|------------|---------|-----------------|--------|
| Lead Search | `copilot/routers.py` | `marketing/lead_intelligence_agent.py` | ⚠️ VERIFICARE |
| Lead Storage | `marketing/service.py` | ❌ Non presente | ✅ CORRETTO |

Il backend gestisce:
- Scraping Pagine Gialle
- Google Places API
- Local PMI Generator (fallback)
- Persistenza in PostgreSQL

L'AI Microservice ha un agent ma non è chiaro se è usato.

---

### 4. RAG (Retrieval Augmented Generation)

| Componente | Backend | AI Microservice | Status |
|------------|---------|-----------------|--------|
| Embeddings | ❌ Non presente | `rag/embeddings.py` | ✅ CORRETTO |
| Vector Store | ❌ Non presente | `rag/stores.py` | ✅ CORRETTO |
| Models | ❌ Non presente | `rag/models.py` | ✅ CORRETTO |

✅ **ARCHITETTURA CORRETTA**: RAG è solo nell'AI Microservice.

---

## 🔄 FLUSSO DI COMUNICAZIONE

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   AUTH      │  │  BOOKING    │  │      COPILOT           │ │
│  │   GOOGLE    │  │  MARKETING  │  │  (PROXY to AI Service) │ │
│  │   SUPPORT   │  │  CUSTOMERS  │  │                         │ │
│  └─────────────┘  └─────────────┘  └───────────┬─────────────┘ │
│         │                                       │               │
│         ▼                                       │               │
│  ┌─────────────┐                               │               │
│  │ PostgreSQL  │                               │               │
│  │   Redis     │                               │               │
│  └─────────────┘                               │               │
└────────────────────────────────────────────────┼───────────────┘
                                                 │
                                   HTTP POST to :8001
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│               AI MICROSERVICE (FastAPI :8001)                   │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  MARKETING  │  │    RAG      │  │       SUPPORT           │ │
│  │  - Content  │  │  - Embed    │  │  - Chatbot (GROQ)       │ │
│  │  - Images   │  │  - Vector   │  │  - Multi-provider       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    LLM PROVIDERS                            ││
│  │  GROQ (FREE) | HuggingFace | Gemini | OpenRouter | Ollama  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚠️ DUPLICATI IDENTIFICATI

### 1. AICustomerSupport (SUPPORT)

| Metric | Backend | AI Microservice |
|--------|---------|-----------------|
| Linee codice | 298 | 424 |
| Providers | 3 | 5 |
| Versione | Stale | Aggiornata |

**File duplicati:**
- `backend/app/domain/support/ai_service.py`
- `ai_microservice/app/domain/support/chatbot.py`

**AZIONE RICHIESTA**:
1. Backend support dovrebbe proxyare al microservice
2. Rimuovere `ai_service.py` dal backend oppure
3. Tenerlo come fallback locale

---

### 2. Content Generation (MARKETING)

| Endpoint | Backend | AI Microservice |
|----------|---------|-----------------|
| `/marketing/generate` | Template statici | Non esposto |
| `/content/*` | Non presente | LLM dinamico |

**AZIONE RICHIESTA**:
1. Esporre endpoint content nel microservice
2. Backend proxya a microservice
3. Rimuovere template statici dal copilot router

---

## ✅ AREE BEN ORGANIZZATE

### 1. Image Generation
```
Backend:  POST /api/v1/copilot/image/generate
          → Proxy a AI_SERVICE_URL/api/v1/marketing/image/generate

AI Svc:   ImageGenerationAgent con multi-provider (Gemini, HuggingFace, OpenAI)
```

### 2. Lead Management (Solo Backend)
```
Backend:  marketing/service.py → Lead CRUD
          copilot/routers.py → Lead Search (Pagine Gialle, Google Places)

Database: PostgreSQL leads table
```

### 3. RAG (Solo AI Microservice)
```
AI Svc:   rag/embeddings.py → Vector embeddings
          rag/stores.py → Vector store (ChromaDB/Pinecone)
```

### 4. Google Integration (Solo Backend)
```
Backend:  google/router.py → GA4 + GMB API
          google/analytics_service.py → GA4 Data API
          google/business_profile_service.py → Business Profile API
```

---

## 📋 AZIONI RACCOMANDATE

### PRIORITÀ ALTA

| # | Azione | File Coinvolti | Effort |
|---|--------|----------------|--------|
| 1 | Unificare AICustomerSupport | `backend/support/ai_service.py` | 2h |
| 2 | Proxyare content generation | `backend/copilot/routers.py` | 3h |

### PRIORITÀ MEDIA

| # | Azione | File Coinvolti | Effort |
|---|--------|----------------|--------|
| 3 | Esporre content endpoints in AI Svc | `ai_microservice/main.py` | 2h |
| 4 | Documentare API contracts | `docs/API_CONTRACTS.md` | 1h |

### PRIORITÀ BASSA

| # | Azione | File Coinvolti | Effort |
|---|--------|----------------|--------|
| 5 | Rimuovere template statici marketing | `backend/copilot/routers.py` | 1h |
| 6 | Aggiungere tests integrazione | `tests/` | 4h |

---

## 📊 RIEPILOGO FINALE

| Categoria | Valutazione | Dettagli |
|-----------|-------------|----------|
| **Separazione Responsabilità** | ⭐⭐⭐⭐ (4/5) | Buona, con 2 eccezioni |
| **Database Access** | ⭐⭐⭐⭐⭐ (5/5) | Solo backend accede a DB |
| **AI Logic** | ⭐⭐⭐⭐ (4/5) | Principalmente in microservice |
| **Code Duplication** | ⭐⭐⭐ (3/5) | 2 aree duplicate |
| **Proxy Pattern** | ⭐⭐⭐⭐ (4/5) | Usato per images, non per chat/content |

### VERDETTO: ✅ ARCHITETTURA SOLIDA CON MIGLIORAMENTI MINORI

L'architettura è **fondamentalmente corretta**. I microservice hanno responsabilità
ben definite. I duplicati identificati sono **gestibili** e non bloccanti per la
produzione.

---

## 📎 APPENDICE: File Count

### Backend Domain
```
auth/           35 files
booking/         7 files
marketing/       6 files
support/         8 files
google/          6 files (NUOVO)
analytics/       6 files
portfolio/       ? files
customers/       ? files
finance/         ? files
quotes/          ? files
notifications/   ? files
copilot/         2 files
─────────────────────────
TOTALE:        ~70+ files
```

### AI Microservice Domain
```
marketing/       7 files
rag/             3 files
support/         3 files
─────────────────────────
TOTALE:         13 files
```

**Ratio Backend:AI = 5:1** → Backend è il monolite principale, AI è microservice leggero ✅
