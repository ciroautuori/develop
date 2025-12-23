# 🚀 MARKETING HUB DEFINITIVO - ROADMAP v4.0

> **Obiettivo**: Hub marketing enterprise-grade con integrazione completa frontend-backend

**Data Creazione**: 2025-12-05
**Ultima Modifica**: 2025-12-06 08:15 UTC
**Versione**: v6.0 (Sprint 1-6 Completati)
**Stato**: ✅ PRODUCTION READY - Sprint 1-6

---

## 🎯 SPRINT 6 - UI CONSOLIDATION + SOCIAL MEDIA (2025-12-06)

### ✅ COMPLETATO

#### UI Marketing Hub Consolidata (12 → 6 Tab)
| Prima | Dopo | Note |
|-------|------|------|
| Dashboard | ✅ Dashboard | - |
| Trova Clienti | ✅ Trova Clienti | - |
| Crea Contenuti | ✅ Crea Contenuti | Sub-tabs: Templates, Video, Social, Email |
| Analytics | ✅ Analytics | Sub-tabs: Performance, A/B Testing, Competitors |
| AI Assistant | ✅ AI Assistant | Sub-tabs: Chat, Knowledge Base |
| Calendario | → Impostazioni | Spostato in sub-tab |
| Knowledge Base | → AI Assistant | Spostato in sub-tab |
| Automazioni | → Impostazioni | Spostato in sub-tab |
| A/B Testing | → Analytics | Spostato in sub-tab |
| Competitor | → Analytics | Spostato in sub-tab |
| Webhooks | → Impostazioni | Spostato in sub-tab |
| Impostazioni | ✅ Impostazioni | Sub-tabs: Brand DNA, Automazioni, Webhooks, Calendario |

#### Image Resize Service (Backend)
- ✅ `infrastructure/media/image_service.py` - Ridimensionamento automatico
- ✅ Supporto piattaforme: Facebook, Instagram, LinkedIn, Twitter, TikTok, Pinterest, Threads, Google Business
- ✅ Endpoint API: `POST /social/image/resize`, `GET /social/image/sizes`

#### Dimensioni Social Aggiornate (Frontend)
- ✅ TikTok: 1080x1920
- ✅ Pinterest: 1000x1500
- ✅ Threads: 1080x1080
- ✅ Google Business: 1200x900

---

## 📊 ANALISI STATO REALE (Post-Audit)

### ✅ BACKEND - COMPLETAMENTE IMPLEMENTATO

| Modulo | File | Status |
|--------|------|--------|
| **Lead CRM** | `domain/marketing/models.py` | ✅ Lead con status, scoring, tags |
| **Email Campaign** | `domain/marketing/models.py` | ✅ CRUD, stats, AI generation |
| **Calendar** | `domain/marketing/models.py` | ✅ ScheduledPost, EditorialCalendar |
| **Brand DNA** | `domain/marketing/models.py` | ✅ BrandSettings completo |
| **Customer CRM** | `domain/customers/models.py` | ✅ Customer, Notes, Interactions, PII encryption |
| **RAG Vector Store** | `ai_microservice/domain/rag/` | ✅ Pinecone, Chroma, FAISS |
| **Lead Intelligence** | `ai_microservice/domain/marketing/` | ✅ ML Agent con embeddings |
| **Image Generation** | `ai_microservice/domain/marketing/` | ✅ Multi-provider (Gemini, HF, DALL-E) |

### ✅ FRONTEND HOOKS - IMPLEMENTATI

| Hook | File | Status |
|------|------|--------|
| `useLeadSearch` | `hooks/marketing/` | ✅ Ricerca lead |
| `useEmailCampaign` | `hooks/marketing/` | ✅ Email AI |
| `useScheduledPosts` | `hooks/marketing/` | ✅ Calendario |
| `useBrandSettings` | `hooks/marketing/` | ✅ Brand DNA |
| `useContentGeneration` | `hooks/marketing/` | ✅ Contenuti AI |
| `useVideoGeneration` | `hooks/marketing/` | ✅ Video AI |
| `useImageGeneration` | `hooks/marketing/` | ✅ Immagini AI |
| `useMarketingAnalytics` | `hooks/marketing/` | ✅ Analytics |
| `useAIChat` | `hooks/marketing/` | ✅ Chat AI |

### ✅ GAP RISOLTI (Sprint 1 - 2025-12-05)

| Area | Gap | Status | Note |
|------|-----|--------|------|
| **Frontend-Backend Sync** | Hooks non usavano tutte le API | ✅ RISOLTO | Hook integrati |
| **Lead Persistenza** | LeadFinderPro non salvava in DB | ✅ RISOLTO | useLeadSearch collegato |
| **RAG Knowledge Base** | Non indicizzati docs aziendali | ✅ RISOLTO | 3 docs indicizzati |
| **Workflow Automation** | No automazioni attive | ⏳ Sprint 2 | Da implementare |
| **Report Export** | No PDF/Excel | ⏳ Sprint 4 | Da implementare |

---

## 🎯 FASE 1: INTEGRAZIONE FRONTEND-BACKEND

### 1.1 Database Lead & CRM ✅ GIÀ IMPLEMENTATO

**Backend esistente** (`apps/backend/app/domain/marketing/models.py`):
- ✅ `Lead` - company_name, email, phone, city, region, industry, score, status, tags
- ✅ `EmailCampaign` - CRUD completo con stats
- ✅ `ScheduledPost` - Calendario editoriale
- ✅ `BrandSettings` - Brand DNA completo

**Customer CRM** (`apps/backend/app/domain/customers/models.py`):
- ✅ `Customer` - CRM completo con PII encryption
- ✅ `CustomerNote` - Note su clienti
- ✅ `CustomerInteraction` - Timeline interazioni

**API già disponibili:**
```
✅ POST   /api/v1/marketing/leads                # Create lead
✅ GET    /api/v1/marketing/leads/{id}           # Get lead
✅ GET    /api/v1/marketing/leads/search/salerno-campania
✅ POST   /api/v1/marketing/emails/generate      # AI email generation
✅ POST   /api/v1/marketing/brand-dna            # Brand settings
✅ POST   /api/v1/social/publish                 # Social publishing
✅ POST   /api/v1/social/schedule                # Scheduling
```

**✅ COMPLETATO: LeadFinderProModal collegato al backend**
```typescript
// LeadFinderProModal.tsx - IMPLEMENTATO
import { useLeadSearch } from '../../../../hooks/marketing/useLeadSearch';
const { saveToCRM: saveToCRMHook } = useLeadSearch();

// handleSaveToCRM ora salva in DB via hook
await saveToCRMHook(leadsForHook);
```

---

### 1.2 RAG Knowledge Base ✅ INFRASTRUTTURA ESISTENTE

**Backend RAG esistente** (`apps/ai_microservice/app/domain/rag/`):
- ✅ `stores.py` - Pinecone, Chroma, FAISS vector stores
- ✅ `embeddings.py` - OpenAI embeddings
- ✅ `models.py` - Document, SearchResult, SearchFilter
- ✅ `lead_intelligence_agent.py` - ML Agent per lead matching

**API esistenti:**
```
✅ POST /api/v1/rag/documents/upload   # Upload documento
✅ POST /api/v1/rag/search             # Query knowledge base
```

**✅ COMPLETATO: Documenti aziendali indicizzati (2025-12-05)**

Knowledge base creata e indicizzata:
```
docs/marketing/knowledge/
├── brand_dna.md      ✅ Indicizzato (Chi siamo, valori, tone of voice)
├── servizi.md        ✅ Indicizzato (Catalogo servizi con prezzi)
└── faq_vendite.md    ✅ Indicizzato (FAQ per vendite)
```

**Comando usato per indicizzazione:**
```bash
curl -X POST "http://localhost:8001/api/v1/rag/documents/upload" \
  -H "Authorization: Bearer $AI_SERVICE_API_KEY" \
  -F "file=@docs/marketing/knowledge/brand_dna.md"
```

**API Endpoints:**
```python
POST   /api/v1/marketing/rag/ingest    # Indicizza documento
POST   /api/v1/marketing/rag/query     # Query knowledge base
GET    /api/v1/marketing/rag/documents # Lista documenti
DELETE /api/v1/marketing/rag/documents/{id}
```

---

### 1.3 Impostazioni Hub Centralizzate

```typescript
// Frontend: components/HubSettings.tsx

interface MarketingHubSettings {
  // Brand Identity
  brand: {
    company_name: string;
    tagline: string;
    tone_of_voice: 'professional' | 'friendly' | 'bold';
    primary_color: string;
    logo_url: string;
  };

  // Target Audience
  target: {
    industries: string[];
    regions: string[];
    company_sizes: string[];
    decision_makers: string[];
  };

  // Content Preferences
  content: {
    languages: string[];
    hashtags_default: string[];
    cta_templates: string[];
    emoji_usage: 'none' | 'minimal' | 'moderate' | 'heavy';
  };

  // Integrations
  integrations: {
    google_analytics_id: string;
    facebook_pixel_id: string;
    linkedin_insight_tag: string;
    email_provider: 'resend' | 'sendgrid' | 'ses';
    crm_sync: boolean;
  };

  // Automation
  automation: {
    auto_schedule_best_time: boolean;
    auto_hashtags: boolean;
    auto_respond_comments: boolean;
    lead_auto_enrich: boolean;
  };

  // Notifications
  notifications: {
    email_weekly_report: boolean;
    slack_channel: string;
    alert_low_engagement: boolean;
  };
}
```

---

## 🎯 FASE 2: FUNZIONALITÀ AVANZATE

### 2.1 Workflow Automatizzati

```typescript
// Workflow Builder - Automazioni marketing

interface MarketingWorkflow {
  id: string;
  name: string;
  trigger: WorkflowTrigger;
  actions: WorkflowAction[];
  conditions: WorkflowCondition[];
  active: boolean;
}

// Esempi di workflow:

const WORKFLOW_TEMPLATES = [
  {
    name: "Lead Nurturing Automatico",
    trigger: { type: "lead_created", filters: { score: ">70" } },
    actions: [
      { type: "wait", delay: "1d" },
      { type: "send_email", template: "welcome_lead" },
      { type: "wait", delay: "3d" },
      { type: "send_email", template: "case_study" },
      { type: "wait", delay: "7d" },
      { type: "create_task", assignee: "sales", title: "Followup lead" }
    ]
  },
  {
    name: "Post Social Ricorrente",
    trigger: { type: "schedule", cron: "0 9 * * 1" }, // Ogni lunedì 9:00
    actions: [
      { type: "generate_content", template: "tip_of_week" },
      { type: "generate_image", style: "professional" },
      { type: "publish", platforms: ["linkedin", "instagram"] }
    ]
  },
  {
    name: "Risposta Automatica Engagement",
    trigger: { type: "social_mention", platforms: ["instagram"] },
    actions: [
      { type: "analyze_sentiment" },
      { type: "conditional", if: "sentiment > 0.5", then: [
        { type: "generate_reply", tone: "grateful" },
        { type: "reply" }
      ]}
    ]
  }
];
```

**API Endpoints:**
```python
POST   /api/v1/marketing/workflows           # Create workflow
GET    /api/v1/marketing/workflows           # List workflows
PUT    /api/v1/marketing/workflows/{id}      # Update
DELETE /api/v1/marketing/workflows/{id}      # Delete
POST   /api/v1/marketing/workflows/{id}/run  # Manual trigger
GET    /api/v1/marketing/workflows/{id}/logs # Execution logs
```

---

### 2.2 A/B Testing Framework

```typescript
interface ABTest {
  id: string;
  name: string;
  type: 'email_subject' | 'email_content' | 'social_content' | 'cta' | 'image';
  variants: ABVariant[];
  traffic_split: number[]; // [50, 50] or [33, 33, 34]
  metric: 'open_rate' | 'click_rate' | 'conversion' | 'engagement';
  status: 'draft' | 'running' | 'completed';
  winner?: string;
  results: ABResult[];
}

interface ABVariant {
  id: string;
  name: string;
  content: any; // Dipende dal type
}

interface ABResult {
  variant_id: string;
  impressions: number;
  metric_value: number;
  confidence: number;
}
```

**Componente Frontend:**
```tsx
// ABTestCreator.tsx
<ABTestBuilder
  type="email_subject"
  variants={[
    { name: "A", content: "🚀 Scopri il nostro nuovo servizio" },
    { name: "B", content: "Trasforma il tuo business con l'AI" }
  ]}
  audience={selectedLeads}
  metric="open_rate"
  duration="7d"
  onComplete={(winner) => applyWinner(winner)}
/>
```

---

### 2.3 Content Calendar Avanzato

```typescript
// Calendario editoriale con AI suggestions

interface CalendarEntry {
  id: string;
  date: Date;
  time: string;
  type: 'social' | 'email' | 'video' | 'blog';
  platforms: string[];
  content: {
    title: string;
    body: string;
    media?: string[];
    hashtags?: string[];
  };
  status: 'idea' | 'draft' | 'approved' | 'scheduled' | 'published';
  performance?: {
    impressions: number;
    engagement: number;
    clicks: number;
  };
  ai_suggestions?: {
    best_time: string;
    alternative_content: string[];
    trending_hashtags: string[];
  };
}

// AI suggerisce:
// 1. Orari migliori per pubblicare (basato su analytics)
// 2. Gap nel calendario (giorni senza contenuti)
// 3. Bilanciamento tipologie contenuti
// 4. Trending topics da cavalcare
// 5. Ricorrenze da non perdere (festività, eventi settore)
```

---

### 2.4 Competitor Intelligence

```typescript
// Monitoraggio competitor

interface CompetitorProfile {
  id: string;
  name: string;
  website: string;
  social_profiles: {
    platform: string;
    handle: string;
    followers: number;
  }[];
  tracking: {
    social_posts: boolean;    // Monitora nuovi post
    website_changes: boolean; // Monitora cambiamenti sito
    pricing_changes: boolean; // Monitora prezzi
    news_mentions: boolean;   // Monitora menzioni news
  };
}

interface CompetitorInsight {
  competitor_id: string;
  date: Date;
  type: 'new_post' | 'campaign' | 'pricing' | 'product_launch';
  summary: string;
  ai_analysis: string;
  action_suggestions: string[];
}
```

**API (usando web scraping + AI):**
```python
POST   /api/v1/marketing/competitors              # Add competitor
GET    /api/v1/marketing/competitors              # List
GET    /api/v1/marketing/competitors/{id}/insights # Get insights
POST   /api/v1/marketing/competitors/analyze      # Force analysis
```

---

## 🎯 FASE 3: REPORTING & ANALYTICS

### 3.1 Dashboard Unificata

```typescript
// KPIs in tempo reale

interface MarketingDashboard {
  // Overview
  total_leads: number;
  leads_this_month: number;
  conversion_rate: number;

  // Content Performance
  posts_published: number;
  total_reach: number;
  engagement_rate: number;

  // Email
  emails_sent: number;
  open_rate: number;
  click_rate: number;

  // Pipeline
  leads_by_stage: {
    new: number;
    contacted: number;
    qualified: number;
    proposal: number;
    closed: number;
  };

  // ROI
  marketing_spend: number;
  revenue_attributed: number;
  roi_percentage: number;

  // Trends
  lead_trend_30d: number[];
  engagement_trend_30d: number[];

  // Top Performers
  best_content: ContentItem[];
  best_campaigns: Campaign[];
  hottest_leads: Lead[];
}
```

### 3.2 Report Generator

```typescript
// Generazione report automatici

interface ReportConfig {
  type: 'weekly' | 'monthly' | 'quarterly' | 'custom';
  sections: ReportSection[];
  format: 'pdf' | 'excel' | 'html';
  recipients: string[];
  schedule?: string; // cron
}

type ReportSection =
  | 'executive_summary'
  | 'lead_generation'
  | 'content_performance'
  | 'email_campaigns'
  | 'social_analytics'
  | 'roi_analysis'
  | 'competitor_comparison'
  | 'recommendations';

// AI genera:
// 1. Executive summary con insights chiave
// 2. Analisi trend e anomalie
// 3. Raccomandazioni actionable
// 4. Previsioni prossimo periodo
```

**API:**
```python
POST   /api/v1/marketing/reports/generate   # Generate report
GET    /api/v1/marketing/reports            # List reports
GET    /api/v1/marketing/reports/{id}/download # Download
POST   /api/v1/marketing/reports/schedule   # Schedule recurring
```

---

## 🎯 FASE 4: INTEGRAZIONI ESTERNE

### 4.1 CRM Sync

```typescript
// Sincronizzazione bidirezionale con CRM esterni

interface CRMIntegration {
  provider: 'hubspot' | 'salesforce' | 'pipedrive' | 'zoho';
  config: {
    api_key: string;
    sync_direction: 'import' | 'export' | 'bidirectional';
    field_mapping: Record<string, string>;
    sync_frequency: 'realtime' | '15min' | '1h' | 'daily';
  };
  last_sync: Date;
  status: 'active' | 'error' | 'paused';
}
```

### 4.2 Webhook System

```typescript
// Webhooks per integrazioni custom

interface Webhook {
  id: string;
  name: string;
  url: string;
  events: WebhookEvent[];
  secret: string;
  active: boolean;
}

type WebhookEvent =
  | 'lead.created'
  | 'lead.updated'
  | 'lead.converted'
  | 'campaign.sent'
  | 'content.published'
  | 'engagement.high';
```

### 4.3 Zapier/Make Integration

```typescript
// Trigger e azioni per Zapier

// TRIGGERS (eventi che Zapier può ascoltare)
const ZAPIER_TRIGGERS = [
  'new_lead',
  'lead_score_changed',
  'campaign_completed',
  'high_engagement_post',
  'new_competitor_insight'
];

// ACTIONS (azioni che Zapier può eseguire)
const ZAPIER_ACTIONS = [
  'create_lead',
  'update_lead_status',
  'schedule_post',
  'send_email',
  'generate_content'
];
```

---

## 📋 ROADMAP IMPLEMENTAZIONE

### ✅ Sprint 1 (COMPLETATO - 2025-12-05) - Database & CRM Base
- [x] ~~Migrazione Alembic per tabelle lead~~ (già esistente)
- [x] ~~API CRUD leads~~ (già esistente)
- [x] Frontend hooks collegati a backend
- [x] LeadFinderProModal → useLeadSearch
- [x] EmailCampaignPro → useEmailCampaign
- [x] MarketingAnalyticsPro → useMarketingAnalytics
- [x] Knowledge base documenti creati e indicizzati
- [x] Docker rebuild e deploy

### ✅ Sprint 2 (COMPLETATO - 2025-12-05) - RAG Integration Avanzata
- [x] ~~Setup ChromaDB in ai_microservice~~ (già esistente)
- [x] ~~Endpoint ingest documenti~~ (già esistente)
- [x] ~~Indicizzazione Brand DNA~~ (fatto Sprint 1)
- [x] RAG service completo con chunking e search
- [x] Integrazione generazione contenuti con RAG context automatico
- [x] UI KnowledgeBaseManager per gestione documenti
- [x] Tab Knowledge Base nel Marketing Hub

### ✅ Sprint 3 (COMPLETATO - 2025-12-05) - Workflow & Automazioni CONFIGURABILI
- [x] Workflow Engine backend DINAMICO (workflow_engine.py)
- [x] API REST per workflow CRUD (workflow_router.py)
- [x] 3 workflow templates (valori default, tutti MODIFICABILI da UI):
  - Lead Nurturing Automatico
  - Post Social Programmato
  - Re-engagement Lead Freddi
- [x] **WorkflowBuilder COMPLETO con:**
  - Trigger configurabile (giorni, orari, frequenza)
  - Azioni drag & drop con parametri personalizzabili
  - Piattaforme social multi-select
  - Delay configurabili (giorni + ore)
  - Templates email selezionabili
  - Tono contenuto selezionabile
  - NESSUN valore hardcoded
- [x] Tab Automazioni nel Marketing Hub

### ✅ Sprint 4 (COMPLETATO - 2025-12-05) - Analytics & Reporting
- [x] **Dashboard unificata** (analytics_service.py)
  - KPIs con trend e variazione %
  - Chart lead e conversioni
  - Metriche per piattaforma social
  - Top content e attività recenti
- [x] **Report generator** (JSON/PDF)
  - Configurazione sezioni
  - Periodo personalizzabile
- [x] **Weekly report automatico**
  - Scheduling configurabile
  - Invio immediato on-demand
- [x] **Export dati** (CSV/Excel/JSON)
  - Export leads, campaigns, social
  - Download diretto

### ✅ Sprint 5 (COMPLETATO - 2025-12-05) - Features Avanzate
- [x] **A/B Testing framework** (ab_testing.py)
  - Test email subject, CTA, landing page
  - Distribuzione traffico configurabile
  - Calcolo statistical significance
  - Auto-winner selection
- [x] **Competitor monitoring** (competitor_service.py)
  - Tracciamento competitor multi-piattaforma
  - Metriche social (followers, engagement)
  - Content tracking con keyword alerts
  - Confronto metriche
- [x] **Webhook system** (webhook_service.py)
  - Registrazione endpoint
  - 9 tipi di eventi
  - HMAC signature
  - Retry automatico
  - Test endpoint

### Sprint 6 (1 settimana) - Polish & Deploy
- [ ] Testing E2E
- [ ] Documentazione
- [ ] Performance optimization
- [ ] Deploy production

---

## 💡 AZIONI IMMEDIATE (Backend esiste, solo Frontend)

### 1. ✅ Collegare LeadFinderPro a Lead API - COMPLETATO
```typescript
// LeadFinderProModal.tsx - Hook integrato
import { useLeadSearch } from '../../../../hooks/marketing/useLeadSearch';
const { saveToCRM: saveToCRMHook } = useLeadSearch();
// Lead salvati in DB via hook + API
```

### 2. ✅ Usare hooks esistenti nei componenti - COMPLETATO
Componenti aggiornati:
- ✅ `EmailCampaignPro` → usa `useEmailCampaign` per generazione AI
- ✅ `MarketingAnalyticsPro` → usa `useMarketingAnalytics` per stats
- ✅ `LeadFinderProModal` → usa `useLeadSearch` per CRM persistence

### 3. ✅ Indicizzare Brand DNA in RAG - COMPLETATO (2025-12-05)
```bash
# Documenti indicizzati:
# - brand_dna.md ✅
# - servizi.md ✅
# - faq_vendite.md ✅
```

### 4. ✅ Creare docs marketing da indicizzare - COMPLETATO
```
docs/marketing/knowledge/
├── brand_dna.md      ✅ Creato (Brand DNA completo)
├── servizi.md        ✅ Creato (Catalogo servizi)
└── faq_vendite.md    ✅ Creato (FAQ vendite)
```

---

## 🔧 API GIÀ DISPONIBILI (Non serve implementare!)

### ✅ Lead Management
| Endpoint | Status |
|----------|--------|
| `POST /api/v1/marketing/leads` | ✅ Esistente |
| `GET /api/v1/marketing/leads/{id}` | ✅ Esistente |
| `POST /api/v1/marketing/leads/google-places` | ✅ Esistente |

### ✅ Email Campaigns
| Endpoint | Status |
|----------|--------|
| `POST /api/v1/marketing/emails/generate` | ✅ AI Generation |
| `POST /api/v1/marketing/email/campaigns` | ✅ CRUD |

### ✅ Social Publishing
| Endpoint | Status |
|----------|--------|
| `POST /api/v1/social/publish` | ✅ Multi-platform |
| `POST /api/v1/social/schedule` | ✅ Scheduling |

### ✅ RAG
| Endpoint | Status |
|----------|--------|
| `POST /api/v1/rag/documents/upload` | ✅ Esistente |
| `POST /api/v1/rag/search` | ✅ Esistente |

---

## 📊 STATO IMPLEMENTAZIONE (Aggiornato 2025-12-05 22:15)

| Area | Backend | Frontend | Status |
|------|---------|----------|--------|
| Lead CRM | ✅ 100% | ✅ 95% | Hook collegato |
| Email Campaign | ✅ 100% | ✅ 95% | Hook integrato |
| Social Publish | ✅ 100% | ✅ 90% | OK |
| Calendar | ✅ 100% | ✅ 85% | OK |
| Brand DNA | ✅ 100% | ✅ 90% | OK |
| RAG | ✅ 100% | ✅ 100% | Service + UI completi |
| Analytics | ✅ 100% | ✅ 90% | Hook integrato |
| **Workflow Engine** | ✅ 100% | ✅ 100% | Configurabile da UI |
| **Knowledge Base** | ✅ 100% | ✅ 100% | UI gestione completa |
| **Analytics Dashboard** | ✅ 100% | 🔄 80% | KPIs, report, export |
| **A/B Testing** | ✅ 100% | ✅ 100% | ABTestingManager |
| **Competitor Monitor** | ✅ 100% | ✅ 100% | CompetitorMonitor |
| **Webhook System** | ✅ 100% | ✅ 100% | WebhookManager |

---

> **SPRINT 1-5 COMPLETATI + UI** (2025-12-05 22:30):
> ✅ 12 Tabs nel Marketing Hub
> ✅ RAG service + KnowledgeBaseManager
> ✅ Workflow Engine CONFIGURABILE + WorkflowBuilder
> ✅ Analytics Dashboard (backend completo)
> ✅ A/B Testing + ABTestingManager
> ✅ Competitor Monitor + CompetitorMonitor
> ✅ Webhook System + WebhookManager
