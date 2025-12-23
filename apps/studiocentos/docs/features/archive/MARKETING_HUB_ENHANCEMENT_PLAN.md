# 🚀 Marketing Hub - Piano di Potenziamento Completo

> **Documento di Analisi e Sviluppo per StudioCentOS**
>
> Obiettivo: Trasformare il Marketing Hub in uno strumento definitivo e professionale per la crescita del business, coprendo:
> - ✅ Acquisizione clienti (Lead Generation)
> - ✅ Gestione campagne social
> - ✅ Creazione contenuti (video, foto, stories)
> - ✅ Branding
> - ✅ Sponsorizzazioni
> - ✅ Analytics e Automazione

---

## 📊 ANALISI STATO ATTUALE

### Componenti Frontend Esistenti (8 Tab)

| Tab | Componente | Funzionalità | Stato |
|-----|-----------|--------------|-------|
| Contenuti | `ContentGenerator.tsx` | Genera contenuti AI (social, ads, blog, video script) | ✅ Funzionante |
| DNA | `BusinessDNAGenerator.tsx` | Genera identità visiva brand | ✅ Funzionante |
| Video & Stories | `VideoStoryCreator.tsx` | 5 modalità: HeyGen, Stories, Video Editor, Carousel, Auto | 🆕 Nuovo |
| Email | `EmailCampaignGenerator.tsx` | Campagne email HTML/Text | ✅ Funzionante |
| Analytics | `MarketingAnalyticsDashboard.tsx` | Statistiche post/piattaforme | ⚠️ Basico |
| Chat | `ChatInterface.tsx` | Chatbot AI per consigli marketing | ✅ Funzionante |
| Lead | `LeadFinder.tsx` | Ricerca lead PMI italiane | ⚠️ Solo UI |
| Calendario | `CalendarManager.tsx` | Gestione post programmati | ✅ Funzionante |

### Backend Services Esistenti

| Servizio | Endpoint | Stato |
|----------|----------|-------|
| Content Generation | `/api/v1/copilot/marketing/generate` | ✅ |
| Image Generation | `/api/v1/copilot/image/generate` | ✅ |
| Social Publishing | `/api/v1/copilot/marketing/publish` | ⚠️ Mock |
| Scheduled Posts | `/api/v1/marketing/calendar/posts` | ✅ |
| Email Generation | `/api/v1/marketing/emails/generate` | ⚠️ Template |
| Business DNA | `/api/v1/marketing/business-dna/generate` | ✅ |
| Video Generation | `/api/v1/marketing/video/generate` | 🔴 TODO |
| Batch Content | `/api/v1/marketing/content/batch/generate` | ⚠️ Basico |
| Scheduler | `/api/v1/marketing/scheduler/*` | ✅ |
| HeyGen | `/api/v1/admin/heygen/*` | ✅ |

### Integrazioni Esistenti

- **AI Models**: Groq, OpenRouter, Gemini, OpenAI
- **Image Gen**: Google Imagen 3, DALL-E 3, Pollinations
- **Video**: HeyGen (avatar + voice "Ciro Autuori")
- **Google APIs**: Analytics, Search Console, Calendar, Gmail, Trends

---

## 🎯 PIANO DI POTENZIAMENTO

### FASE 1: LEAD GENERATION PROFESSIONALE (Priorità Alta)

#### 1.1 Lead Finder Potenziato

**Problema Attuale:**
- Solo UI mockup, nessuna integrazione reale
- Ricerca lead basata solo su DB interno

**Potenziamenti:**

```typescript
// Nuove funzionalità LeadFinder
interface EnhancedLeadFinder {
  // Fonti dati reali
  sources: {
    googleMaps: true,      // Google Places API
    linkedIn: true,        // LinkedIn Sales Navigator
    cciaa: true,           // Camera Commercio API
    whois: true,           // Domain lookups
    crunchbase: true       // Company data
  },

  // Arricchimento automatico
  enrichment: {
    email: true,           // Hunter.io, Clearbit
    phone: true,           // Phonenumber verification
    social: true,          // Social profiles discovery
    website: true,         // Website scraping
    revenue: true          // Estimated revenue
  },

  // Scoring AI
  scoring: {
    needsScore: true,      // AI-based needs detection
    budgetScore: true,     // Budget estimation
    timingScore: true,     // Purchase timing
    decisionMaker: true    // Contact level detection
  }
}
```

**Implementazione Backend:**

```python
# apps/backend/app/domain/marketing/lead_enrichment_service.py

class LeadEnrichmentService:
    """Servizio per arricchimento lead con API esterne."""

    async def enrich_from_google_places(self, business_name: str, location: str) -> dict:
        """Cerca attività su Google Places API."""
        pass

    async def enrich_from_linkedin(self, company_name: str) -> dict:
        """Ottieni dati company da LinkedIn."""
        pass

    async def find_email(self, domain: str, name: str) -> str:
        """Trova email con Hunter.io/Clearbit."""
        pass

    async def calculate_lead_score(self, lead_data: dict) -> int:
        """Calcola score AI-based 0-100."""
        pass
```

#### 1.2 CRM Integrato

**Nuovo Componente: `CRMDashboard.tsx`**

```typescript
interface CRMFeatures {
  // Pipeline visuale
  pipeline: {
    stages: ['nuovo', 'contattato', 'interessato', 'proposta', 'negoziazione', 'chiuso'],
    kanbanView: true,
    dragDrop: true
  },

  // Attività
  activities: {
    calls: true,
    emails: true,
    meetings: true,
    notes: true,
    reminders: true
  },

  // Automazioni
  automations: {
    followUpReminders: true,
    emailSequences: true,
    leadScoring: true,
    dealAlerts: true
  }
}
```

---

### FASE 2: SOCIAL MEDIA MANAGEMENT AVANZATO (Priorità Alta)

#### 2.1 Pubblicazione Multi-Platform Reale

**Problema Attuale:**
- Pubblicazione social è solo mock
- Nessuna integrazione API reale

**Integrazioni da Implementare:**

| Platform | API | Funzionalità |
|----------|-----|--------------|
| Meta (FB/IG) | Graph API | Post, Stories, Reels, Analytics |
| LinkedIn | Marketing API | Post, Articles, Company Page |
| TikTok | Business API | Video, Analytics |
| Twitter/X | API v2 | Tweets, Threads |
| Google Business | Business Profile API | Posts, Reviews |

**Backend Service:**

```python
# apps/backend/app/domain/social/publisher_service.py

class SocialPublisherService:
    """Servizio pubblicazione multi-piattaforma."""

    async def publish_to_instagram(self, content: PostContent) -> PublishResult:
        """Pubblica su Instagram (Graph API)."""
        pass

    async def publish_to_facebook(self, content: PostContent) -> PublishResult:
        """Pubblica su Facebook Page."""
        pass

    async def publish_story(self, platform: str, media_url: str) -> PublishResult:
        """Pubblica Story (IG/FB)."""
        pass

    async def schedule_post(self, content: PostContent, scheduled_at: datetime) -> str:
        """Programma post (usa API native quando disponibile)."""
        pass
```

#### 2.2 Social Calendar Migliorato

**Potenziamenti `CalendarManager.tsx`:**

```typescript
interface EnhancedCalendar {
  // Viste multiple
  views: {
    day: true,
    week: true,
    month: true,
    timeline: true
  },

  // Drag & Drop
  interactions: {
    dragToReschedule: true,
    dragToCreate: true,
    multiSelect: true
  },

  // Suggerimenti AI
  aiFeatures: {
    bestTimeToPost: true,     // Orari migliori per engagement
    contentSuggestions: true, // Cosa postare oggi
    hashtagSuggestions: true, // Hashtag trending
    captionOptimizer: true    // Ottimizza caption
  },

  // Integrazione
  integrations: {
    googleCalendar: true,     // Sync con Google Calendar
    importFromCSV: true,      // Import bulk
    exportICS: true           // Export calendario
  }
}
```

#### 2.3 Analytics Social Avanzato

**Nuovo Tab: `SocialAnalytics.tsx`**

```typescript
interface SocialAnalyticsFeatures {
  // Metriche per piattaforma
  platformMetrics: {
    followers: true,
    engagement: true,
    reach: true,
    impressions: true,
    clicks: true
  },

  // Analisi contenuti
  contentAnalysis: {
    topPerformingPosts: true,
    bestHashtags: true,
    bestTimes: true,
    audienceGrowth: true
  },

  // Competitor Analysis
  competitors: {
    tracking: true,
    benchmarking: true,
    alerts: true
  },

  // Report
  reporting: {
    weeklyDigest: true,
    monthlyReport: true,
    customDateRange: true,
    exportPDF: true
  }
}
```

---

### FASE 3: VIDEO & STORIES PROFESSIONALE (Priorità Alta)

#### 3.1 Video Generator Completo

**Potenziamenti `VideoStoryCreator.tsx`:**

```typescript
interface VideoFeatures {
  // Avatar Video (HeyGen)
  avatarVideo: {
    personalAvatar: 'Ciro Autuori',
    customVoices: ['voice_1', 'voice_2', 'voice_3'],
    templates: ['sales', 'tutorial', 'promo', 'testimonial'],
    languages: ['it', 'en', 'es', 'de', 'fr']
  },

  // Story Designer
  storyDesigner: {
    templates: 50,           // 50+ template stories
    animations: true,        // Animazioni predefinite
    textStyles: 20,          // Stili testo
    musicLibrary: true,      // Libreria musica royalty-free
    brandKit: true           // Colori/font aziendali
  },

  // Video Editor
  videoEditor: {
    trimming: true,
    merging: true,
    transitions: true,
    textOverlay: true,
    subtitles: {
      autoGenerate: true,    // AI speech-to-text
      multiLanguage: true
    },
    export: {
      formats: ['mp4', 'webm', 'gif'],
      qualities: ['720p', '1080p', '4K'],
      aspectRatios: ['16:9', '9:16', '1:1', '4:5']
    }
  },

  // AI Generation
  aiGeneration: {
    scriptFromTopic: true,
    videoFromScript: true,
    imageToVideo: true,
    textToVideo: true
  }
}
```

#### 3.2 Asset Library

**Nuovo Componente: `AssetLibrary.tsx`**

```typescript
interface AssetLibrary {
  // Media storage
  storage: {
    images: true,
    videos: true,
    audio: true,
    documents: true
  },

  // Organization
  organization: {
    folders: true,
    tags: true,
    favorites: true,
    recentlyUsed: true
  },

  // AI Features
  aiFeatures: {
    autoTag: true,           // Tag automatici con AI vision
    search: true,            // Ricerca semantica
    similarImages: true,     // Trova immagini simili
    backgroundRemove: true   // Rimuovi sfondo
  },

  // Stock Integration
  stock: {
    unsplash: true,
    pexels: true,
    pixabay: true
  }
}
```

---

### FASE 4: BRANDING & DESIGN (Priorità Media)

#### 4.1 Business DNA Avanzato

**Potenziamenti `BusinessDNAGenerator.tsx`:**

```typescript
interface EnhancedBrandingFeatures {
  // Brand Book Generator
  brandBook: {
    logoUsage: true,         // Regole uso logo
    colorPalette: true,      // Palette completa
    typography: true,        // Gerarchia tipografica
    iconography: true,       // Icone brand
    photography: true,       // Stile fotografico
    voiceGuidelines: true,   // Tono di voce
    exportPDF: true          // Esporta brand book PDF
  },

  // Template Generator
  templates: {
    socialPosts: true,       // Template post social
    stories: true,           // Template stories
    presentations: true,     // Template presentazioni
    businessCards: true,     // Biglietti da visita
    emailSignature: true,    // Firma email
    letterhead: true         // Carta intestata
  },

  // AI Suggestions
  aiSuggestions: {
    colorHarmony: true,      // Suggerimenti colori
    fontPairing: true,       // Abbinamento font
    logoIdeas: true,         // Idee logo AI
    nameGenerator: true      // Generatore nomi brand
  }
}
```

#### 4.2 Design System Builder

**Nuovo Componente: `DesignSystemBuilder.tsx`**

```typescript
interface DesignSystemBuilder {
  // Componenti
  components: {
    buttons: true,
    cards: true,
    forms: true,
    navigation: true,
    modals: true
  },

  // Tokens
  tokens: {
    colors: true,
    spacing: true,
    typography: true,
    shadows: true,
    borderRadius: true
  },

  // Export
  export: {
    css: true,
    tailwind: true,
    figma: true,
    sketch: true
  }
}
```

---

### FASE 5: ADVERTISING & SPONSORIZZAZIONI (Priorità Media)

#### 5.1 Ad Campaign Manager

**Nuovo Tab: `AdCampaignManager.tsx`**

```typescript
interface AdCampaignFeatures {
  // Piattaforme
  platforms: {
    meta: {
      facebook: true,
      instagram: true,
      messenger: true,
      audience: true
    },
    google: {
      search: true,
      display: true,
      youtube: true,
      shopping: true
    },
    linkedin: true,
    tiktok: true
  },

  // Campaign Builder
  campaignBuilder: {
    objectives: ['awareness', 'traffic', 'engagement', 'leads', 'conversions'],
    targeting: {
      demographics: true,
      interests: true,
      behaviors: true,
      lookalike: true,
      retargeting: true
    },
    budgeting: {
      daily: true,
      lifetime: true,
      optimization: true
    },
    scheduling: {
      startDate: true,
      endDate: true,
      dayParting: true
    }
  },

  // Creative Tools
  creativeTools: {
    adPreview: true,         // Preview per formato
    aiCopywriting: true,     // Copy AI per ads
    imageOptimizer: true,    // Ottimizza immagini
    abTesting: true          // A/B test creatività
  },

  // Analytics
  analytics: {
    realtime: true,
    roas: true,
    costPerResult: true,
    attribution: true,
    reporting: true
  }
}
```

#### 5.2 Budget Manager

**Nuovo Componente: `AdBudgetManager.tsx`**

```typescript
interface BudgetManager {
  // Budget Tracking
  tracking: {
    spendByPlatform: true,
    spendByCAMpaign: true,
    budgetAlerts: true,
    forecastSpend: true
  },

  // ROI Calculator
  roi: {
    revenueTracking: true,
    conversionValue: true,
    roasCalculation: true,
    ltv: true
  },

  // Optimization
  optimization: {
    budgetAllocation: true,  // AI-based allocation
    bidStrategies: true,
    pauseUnderperforming: true
  }
}
```

---

### FASE 6: ANALYTICS UNIFIED (Priorità Alta)

#### 6.1 Marketing Dashboard Completo

**Potenziamenti `MarketingAnalyticsDashboard.tsx`:**

```typescript
interface UnifiedAnalytics {
  // KPI Overview
  kpiDashboard: {
    totalReach: true,
    totalEngagement: true,
    totalLeads: true,
    totalConversions: true,
    totalRevenue: true,
    cac: true,               // Customer Acquisition Cost
    ltv: true                // Lifetime Value
  },

  // Channel Performance
  channels: {
    organic: {
      seo: true,
      social: true,
      referral: true,
      direct: true
    },
    paid: {
      searchAds: true,
      socialAds: true,
      displayAds: true
    },
    email: {
      openRate: true,
      clickRate: true,
      conversionRate: true
    }
  },

  // Funnel Analytics
  funnel: {
    awareness: true,
    interest: true,
    consideration: true,
    conversion: true,
    retention: true
  },

  // Attribution
  attribution: {
    firstTouch: true,
    lastTouch: true,
    linear: true,
    timeDecay: true,
    dataDriver: true
  },

  // Reporting
  reports: {
    customDashboards: true,
    scheduledReports: true,
    exportFormats: ['PDF', 'Excel', 'CSV'],
    sharing: true
  }
}
```

#### 6.2 AI Insights

**Nuovo Componente: `AIInsights.tsx`**

```typescript
interface AIInsights {
  // Trend Detection
  trends: {
    performanceTrends: true,
    anomalyDetection: true,
    seasonalPatterns: true,
    predictiveAnalytics: true
  },

  // Recommendations
  recommendations: {
    contentOptimization: true,
    budgetAllocation: true,
    targetingImprovements: true,
    bestPractices: true
  },

  // Natural Language
  nlQuery: {
    askQuestions: true,      // "Qual è stato il post migliore?"
    voiceInput: true,
    chatInterface: true
  }
}
```

---

### FASE 7: AUTOMAZIONE AVANZATA (Priorità Media)

#### 7.1 Marketing Automation Workflows

**Nuovo Tab: `AutomationHub.tsx`**

```typescript
interface AutomationFeatures {
  // Workflow Builder (Visual)
  workflows: {
    triggers: [
      'newLead',
      'formSubmission',
      'pageVisit',
      'emailOpen',
      'cartAbandonment',
      'anniversary',
      'customEvent'
    ],
    actions: [
      'sendEmail',
      'sendSMS',
      'addToList',
      'updateCRM',
      'assignTask',
      'postToSocial',
      'sendNotification',
      'webhook'
    ],
    conditions: [
      'ifThen',
      'abSplit',
      'waitFor',
      'filter'
    ]
  },

  // Pre-built Templates
  templates: {
    welcomeSeries: true,
    leadNurturing: true,
    cartRecovery: true,
    reEngagement: true,
    birthdayWishes: true,
    feedbackRequest: true
  },

  // Analytics
  analytics: {
    workflowPerformance: true,
    conversionRates: true,
    dropOffPoints: true
  }
}
```

#### 7.2 Content Scheduler Potenziato

**Potenziamenti Scheduler Backend:**

```python
# apps/backend/app/infrastructure/scheduler/enhanced_scheduler.py

class EnhancedMarketingScheduler:
    """Scheduler avanzato con AI optimization."""

    async def optimize_posting_times(self, platform: str) -> list[datetime]:
        """Calcola orari ottimali basati su analytics."""
        pass

    async def auto_generate_week_content(self) -> list[ScheduledPost]:
        """Genera automaticamente contenuti per settimana."""
        pass

    async def content_recycling(self, post_id: int) -> ScheduledPost:
        """Ripropone contenuti evergreen."""
        pass

    async def smart_hashtag_rotation(self, topic: str) -> list[str]:
        """Ruota hashtag per evitare shadow-ban."""
        pass
```

---

## 📋 ROADMAP IMPLEMENTAZIONE

### Sprint 1 (Settimana 1-2): Lead Generation Pro ✅ COMPLETATO

| Task | Ore Stimate | Priorità | Status |
|------|-------------|----------|--------|
| Backend: Google Places integration | 8h | Alta | ✅ DONE |
| Backend: Email finder (Hunter.io) | 4h | Alta | ✅ DONE |
| Backend: Lead scoring AI | 6h | Alta | ✅ DONE |
| Frontend: LeadFinderPro component | 12h | Alta | ✅ DONE |
| Backend: Lead enrichment router | 4h | Alta | ✅ DONE |
| **Totale** | **34h** | | ✅ |

**File Creati/Modificati:**
- `apps/backend/app/domain/marketing/lead_enrichment_service.py` - Servizio arricchimento
- `apps/backend/app/domain/marketing/lead_enrichment_router.py` - API endpoints
- `apps/frontend/src/features/admin/pages/AIMarketing/components/LeadFinderPro.tsx` - UI potenziata
- `apps/backend/app/main.py` - Registrazione router

### Sprint 2 (Settimana 3-4): Social Publishing Reale

| Task | Ore Stimate | Priorità |
|------|-------------|----------|
| Backend: Meta Graph API integration | 16h | Alta |
| Backend: LinkedIn API integration | 8h | Alta |
| Backend: Story publishing | 8h | Alta |
| Frontend: Enhanced Calendar views | 8h | Media |
| Testing & OAuth flows | 8h | Alta |
| **Totale** | **48h** | |

### Sprint 3 (Settimana 5-6): Video & Stories Pro

| Task | Ore Stimate | Priorità |
|------|-------------|----------|
| HeyGen: Use personal avatar | 4h | Alta |
| Frontend: Story templates | 12h | Alta |
| Frontend: Video editor (trimming) | 16h | Media |
| Backend: Video processing service | 12h | Media |
| Asset Library component | 8h | Media |
| **Totale** | **52h** | |

### Sprint 4 (Settimana 7-8): Analytics & Ads

| Task | Ore Stimate | Priorità |
|------|-------------|----------|
| Backend: Social metrics aggregation | 12h | Alta |
| Frontend: Unified analytics dashboard | 16h | Alta |
| Backend: Meta Ads API integration | 12h | Media |
| Frontend: Ad campaign builder | 16h | Media |
| **Totale** | **56h** | |

### Sprint 5 (Settimana 9-10): Automation & Polish

| Task | Ore Stimate | Priorità |
|------|-------------|----------|
| Workflow builder component | 24h | Media |
| Email sequences automation | 8h | Media |
| AI Insights component | 12h | Media |
| Testing & Bug fixes | 16h | Alta |
| Documentation | 8h | Media |
| **Totale** | **68h** | |

---

## 🔧 CONFIGURAZIONI RICHIESTE

### API Keys Necessarie

```env
# .env.production

# Social Publishing
META_APP_ID=
META_APP_SECRET=
META_ACCESS_TOKEN=
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
TIKTOK_CLIENT_KEY=
TIKTOK_CLIENT_SECRET=

# Lead Enrichment
HUNTER_API_KEY=
CLEARBIT_API_KEY=
GOOGLE_PLACES_API_KEY=

# Advertising
META_ADS_ACCESS_TOKEN=
GOOGLE_ADS_DEVELOPER_TOKEN=
GOOGLE_ADS_CLIENT_ID=
GOOGLE_ADS_CLIENT_SECRET=

# Video
HEYGEN_API_KEY=✅ (già configurata)
CLOUDINARY_URL=              # Per video processing

# Analytics
GOOGLE_ANALYTICS_PROPERTY_ID=
GOOGLE_SEARCH_CONSOLE_SITE=
```

### Database Migrations

```sql
-- Nuove tabelle necessarie

CREATE TABLE crm_activities (
  id SERIAL PRIMARY KEY,
  lead_id INTEGER REFERENCES leads(id),
  type VARCHAR(50),
  title VARCHAR(255),
  description TEXT,
  scheduled_at TIMESTAMP,
  completed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ad_campaigns (
  id SERIAL PRIMARY KEY,
  platform VARCHAR(50),
  external_id VARCHAR(255),
  name VARCHAR(255),
  objective VARCHAR(50),
  budget_daily DECIMAL(10,2),
  budget_total DECIMAL(10,2),
  status VARCHAR(50),
  start_date DATE,
  end_date DATE,
  targeting JSONB,
  creatives JSONB,
  metrics JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE marketing_automation_workflows (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  trigger_type VARCHAR(50),
  trigger_config JSONB,
  actions JSONB,
  is_active BOOLEAN DEFAULT true,
  stats JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE media_assets (
  id SERIAL PRIMARY KEY,
  type VARCHAR(50),
  url TEXT,
  thumbnail_url TEXT,
  name VARCHAR(255),
  folder VARCHAR(255),
  tags TEXT[],
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 📊 METRICHE DI SUCCESSO

### KPI per Sprint

| Sprint | Metrica | Target |
|--------|---------|--------|
| 1 | Lead arricchiti/giorno | 50+ |
| 2 | Post pubblicati automaticamente | 100% piattaforme |
| 3 | Video generati/settimana | 10+ |
| 4 | Report automatici | Settimanale |
| 5 | Workflow attivi | 5+ |

### KPI Globali Marketing Hub

- **Lead Generation**: 100+ lead qualificati/mese
- **Content Creation**: 30+ contenuti AI/settimana
- **Social Engagement**: +50% engagement rate
- **Time Saved**: -80% tempo gestione manuale
- **ROI**: 5x ritorno investimento advertising

---

## ✅ CONCLUSIONI

Il Marketing Hub attuale ha una solida base con:
- ✅ Design System coerente (light/dark mode)
- ✅ WCAG AA compliance
- ✅ Architettura modulare
- ✅ Integrazioni AI multiple

Con le implementazioni proposte, diventerà:
- 🎯 **All-in-one Marketing Suite** completa
- 🤖 **AI-First** con automazione intelligente
- 📊 **Data-Driven** con analytics unificati
- ⚡ **Efficiente** con workflow automatizzati

**Stima totale sviluppo**: 258 ore (~6-7 settimane full-time)

---

*Documento generato: 2024*
*Versione: 1.0*
*Autore: AI Assistant per StudioCentOS*
