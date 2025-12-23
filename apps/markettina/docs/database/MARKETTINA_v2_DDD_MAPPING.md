# 🎯 MARKETTINA v2.0 - DDD Mapping Document

**Versione**: 2.0.0
**Data**: 2024-12-06

---

## 📋 BOUNDED CONTEXTS → AGGREGATES → ENTITIES

### 1. 🔐 IDENTITY CONTEXT

**Responsabilità**: Autenticazione, autorizzazione, gestione account social

| Aggregate Root  | Entities                          | Value Objects              |
| --------------- | --------------------------------- | -------------------------- |
| `Account`       | -                                 | AccountSettings, PlanTier  |
| `User`          | OAuthToken, TrustedDevice, APIKey | Email, Password, UserRole  |
| `AdminUser`     | AdminSession, AdminAuditLog       | MFASecret                  |
| `SocialAccount` | SocialAccountHealth               | Platform, OAuthCredentials |

**Domain Events**:

- `UserRegistered`
- `UserRoleChanged`
- `SocialAccountConnected`
- `SocialAccountDisconnected`
- `TokenRefreshed`
- `TokenExpired`

**Repositories**:

- `UserRepository`
- `AdminUserRepository`
- `SocialAccountRepository`

---

### 2. 💰 BILLING CONTEXT

**Responsabilità**: Gestione token, pagamenti, fatturazione, promozioni

| Aggregate Root    | Entities         | Value Objects               |
| ----------------- | ---------------- | --------------------------- |
| `TokenWallet`     | TokenTransaction | Balance, TransactionType    |
| `TokenPackage`    | -                | Price, TokenAmount          |
| `Invoice`         | InvoiceItem      | InvoiceNumber, BillingInfo  |
| `PromoCode`       | PromoRedemption  | DiscountType, DiscountValue |
| `ReferralProgram` | -                | ReferralCode, BonusTokens   |

**Domain Events**:

- `TokensPurchased`
- `TokensConsumed`
- `TokensRefunded`
- `InvoiceGenerated`
- `InvoicePaid`
- `PromoCodeRedeemed`
- `ReferralCompleted`

**Domain Services**:

- `TokenConsumptionService` - Calcola e deduce token per servizio
- `PricingService` - Recupera pricing dinamico da DB
- `InvoiceGenerationService` - Genera fatture

**Repositories**:

- `TokenWalletRepository`
- `TokenPackageRepository`
- `InvoiceRepository`
- `PromoCodeRepository`

---

### 3. 📝 CONTENT CONTEXT

**Responsabilità**: Gestione contenuti, post, campagne, template, media

| Aggregate Root    | Entities                       | Value Objects                      |
| ----------------- | ------------------------------ | ---------------------------------- |
| `Campaign`        | ScheduledPost                  | CampaignGoals, DateRange           |
| `ScheduledPost`   | ContentVersion, ContentVariant | PostContent, MediaUrls, Hashtags   |
| `ContentTemplate` | -                              | TemplateVariables, ContentType     |
| `MediaAsset`      | MediaTag                       | FileInfo, StorageLocation          |
| `Lead`            | -                              | ContactInfo, LeadScore, LeadStatus |
| `EmailCampaign`   | -                              | EmailContent, TargetAudience       |

**Domain Events**:

- `CampaignCreated`
- `CampaignActivated`
- `CampaignCompleted`
- `PostScheduled`
- `PostPublished`
- `PostFailed`
- `ContentVersionCreated`
- `LeadCreated`
- `LeadStatusChanged`
- `LeadScoreUpdated`

**Domain Services**:

- `ContentSchedulingService` - Gestisce scheduling post
- `ContentAdaptationService` - Adatta contenuto per piattaforma
- `LeadScoringService` - Calcola score lead

**Repositories**:

- `CampaignRepository`
- `ScheduledPostRepository`
- `ContentTemplateRepository`
- `MediaAssetRepository`
- `LeadRepository`

---

### 4. 📊 ANALYTICS CONTEXT

**Responsabilità**: Metriche social, sentiment analysis, competitor tracking, predizioni

| Aggregate Root          | Entities          | Value Objects                      |
| ----------------------- | ----------------- | ---------------------------------- |
| `SocialMetrics`         | -                 | EngagementMetrics, ReachMetrics    |
| `SentimentAnalysis`     | -                 | SentimentScore, Emotions           |
| `CompetitorProfile`     | CompetitorMetrics | SocialHandles, Industry            |
| `PerformancePrediction` | -                 | PredictedValue, ConfidenceInterval |

**Domain Events**:

- `MetricsSynced`
- `SentimentAnalyzed`
- `CompetitorMetricsUpdated`
- `PredictionGenerated`

**Domain Services**:

- `MetricsSyncService` - Sincronizza metriche da API social
- `SentimentAnalysisService` - Analizza sentiment commenti
- `CompetitorBenchmarkService` - Confronta con competitor
- `PredictionService` - Genera predizioni AI

**Repositories**:

- `SocialMetricsRepository`
- `SentimentAnalysisRepository`
- `CompetitorProfileRepository`
- `PerformancePredictionRepository`

---

### 5. 📱 SOCIAL CONTEXT

**Responsabilità**: Gestione account social, cross-posting, commenti, menzioni

| Aggregate Root    | Entities  | Value Objects                     |
| ----------------- | --------- | --------------------------------- |
| `CrossPostConfig` | CrossPost | PlatformRules, AdaptationSettings |
| `SocialComment`   | -         | CommentContent, AuthorInfo        |
| `SocialMention`   | -         | MentionType, MatchedKeyword       |

**Domain Events**:

- `CrossPostCreated`
- `CrossPostCompleted`
- `CrossPostFailed`
- `CommentReceived`
- `CommentReplied`
- `MentionDetected`
- `MentionResponded`

**Domain Services**:

- `CrossPostingService` - Gestisce pubblicazione multi-piattaforma
- `ContentAdaptationService` - Adatta contenuto per piattaforma
- `MentionMonitoringService` - Monitora menzioni brand

**Repositories**:

- `CrossPostConfigRepository`
- `SocialCommentRepository`
- `SocialMentionRepository`

---

### 6. 🤖 AI SERVICES CONTEXT

**Responsabilità**: Generazione contenuti AI, immagini, video, Brand DNA

| Aggregate Root      | Entities        | Value Objects                               |
| ------------------- | --------------- | ------------------------------------------- |
| `AIJob`             | AIJobLog        | JobType, JobStatus, Priority                |
| `ContentGeneration` | -               | Prompt, GeneratedContent, AIModel           |
| `ImageGeneration`   | -               | ImagePrompt, ImageParams, ImageUrl          |
| `VideoGeneration`   | -               | VideoPrompt, VideoParams, VideoUrl          |
| `BrandDNA`          | BrandDNAVersion | ToneOfVoice, VisualIdentity, TargetAudience |

**Domain Events**:

- `AIJobCreated`
- `AIJobStarted`
- `AIJobCompleted`
- `AIJobFailed`
- `ContentGenerated`
- `ImageGenerated`
- `VideoGenerated`
- `BrandDNAUpdated`
- `BrandDNAVersionCreated`

**Domain Services**:

- `ContentGenerationService` - Genera contenuti con AI
- `ImageGenerationService` - Genera immagini con AI
- `VideoGenerationService` - Genera video con AI
- `BrandDNAEnrichmentService` - Arricchisce prompt con DNA
- `AIJobQueueService` - Gestisce coda job asincroni

**Repositories**:

- `AIJobRepository`
- `ContentGenerationRepository`
- `ImageGenerationRepository`
- `VideoGenerationRepository`
- `BrandDNARepository`

---

### 7. ⚙️ WORKFLOW CONTEXT

**Responsabilità**: Automazione marketing, workflow configurabili, approvazioni

| Aggregate Root     | Entities                                         | Value Objects                |
| ------------------ | ------------------------------------------------ | ---------------------------- |
| `Workflow`         | WorkflowExecution, WorkflowLog, WorkflowSchedule | TriggerConfig, ActionConfig  |
| `ApprovalWorkflow` | ContentApproval                                  | ApprovalStep, ApprovalStatus |

**Domain Events**:

- `WorkflowCreated`
- `WorkflowActivated`
- `WorkflowPaused`
- `WorkflowExecutionStarted`
- `WorkflowExecutionCompleted`
- `WorkflowExecutionFailed`
- `ApprovalRequested`
- `ApprovalGranted`
- `ApprovalRejected`

**Domain Services**:

- `WorkflowEngineService` - Esegue workflow
- `WorkflowSchedulerService` - Schedula workflow
- `ApprovalService` - Gestisce approvazioni

**Repositories**:

- `WorkflowRepository`
- `WorkflowExecutionRepository`
- `ApprovalWorkflowRepository`
- `ContentApprovalRepository`

---

### 8. 📚 KNOWLEDGE BASE CONTEXT

**Responsabilità**: Gestione documenti, RAG, ricerca semantica

| Aggregate Root      | Entities      | Value Objects                     |
| ------------------- | ------------- | --------------------------------- |
| `KnowledgeDocument` | DocumentChunk | DocumentContent, ProcessingStatus |
| `DocumentCategory`  | -             | CategoryName, CategoryHierarchy   |
| `SearchHistory`     | -             | QueryText, SearchResults          |

**Domain Events**:

- `DocumentUploaded`
- `DocumentProcessed`
- `DocumentChunked`
- `EmbeddingsGenerated`
- `SearchPerformed`

**Domain Services**:

- `DocumentProcessingService` - Processa e chunka documenti
- `EmbeddingService` - Genera embeddings
- `SemanticSearchService` - Ricerca semantica

**Repositories**:

- `KnowledgeDocumentRepository`
- `DocumentCategoryRepository`
- `DocumentChunkRepository`
- `SearchHistoryRepository`

---

### 9. 🔧 SHARED KERNEL (Cross-Cutting)

**Responsabilità**: Infrastruttura condivisa, event sourcing, feature flags

| Component         | Purpose                 |
| ----------------- | ----------------------- |
| `DomainEvent`     | Event Sourcing centrale |
| `FeatureFlag`     | Feature toggles         |
| `Webhook`         | Notifiche esterne       |
| `WebhookDelivery` | Tracking delivery       |
| `APIRateLimit`    | Rate limiting           |
| `IdempotencyKey`  | Operazioni idempotenti  |
| `AsyncJob`        | Job queue generica      |

**Infrastructure Services**:

- `EventBusService` - Pubblica/sottoscrive eventi
- `FeatureFlagService` - Gestisce feature flags
- `WebhookDispatcherService` - Invia webhook
- `RateLimiterService` - Applica rate limits
- `IdempotencyService` - Gestisce idempotenza

---

## 🔄 CONTEXT MAP

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CONTEXT MAP                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│    ┌──────────────┐         ┌──────────────┐         ┌──────────────┐       │
│    │   IDENTITY   │◄───────►│   BILLING    │◄───────►│   CONTENT    │       │
│    │   Context    │  U/D    │   Context    │  U/D    │   Context    │       │
│    └──────┬───────┘         └──────┬───────┘         └──────┬───────┘       │
│           │                        │                        │                │
│           │ U/D                    │ U/D                    │ U/D            │
│           ▼                        ▼                        ▼                │
│    ┌──────────────┐         ┌──────────────┐         ┌──────────────┐       │
│    │    SOCIAL    │◄───────►│ AI SERVICES  │◄───────►│  ANALYTICS   │       │
│    │   Context    │  U/D    │   Context    │  U/D    │   Context    │       │
│    └──────┬───────┘         └──────┬───────┘         └──────┬───────┘       │
│           │                        │                        │                │
│           │ U/D                    │ U/D                    │ U/D            │
│           ▼                        ▼                        ▼                │
│    ┌──────────────┐         ┌──────────────┐         ┌──────────────┐       │
│    │   WORKFLOW   │◄───────►│  KNOWLEDGE   │         │    SHARED    │       │
│    │   Context    │  U/D    │    BASE      │◄───────►│    KERNEL    │       │
│    └──────────────┘         └──────────────┘         └──────────────┘       │
│                                                                              │
│    Legend: U/D = Upstream/Downstream (Published Language)                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 AGGREGATE BOUNDARIES

### Rules per Aggregate:

1. **Transactional Consistency**: Ogni aggregate è una unità transazionale
2. **Reference by ID**: Aggregates si riferiscono tra loro solo via ID
3. **Single Responsibility**: Ogni aggregate ha una sola responsabilità
4. **Eventual Consistency**: Tra aggregates diversi, consistenza eventuale via eventi

### Esempi:

```python
# ✅ CORRETTO: Reference by ID
class ScheduledPost:
    campaign_id: UUID  # Reference, non oggetto Campaign

# ❌ SBAGLIATO: Embedded aggregate
class ScheduledPost:
    campaign: Campaign  # Non fare questo!

# ✅ CORRETTO: Domain Event per sync
class PostPublishedEvent:
    post_id: UUID
    campaign_id: UUID
    platform: str
    published_at: datetime

# Handler in Analytics Context
async def handle_post_published(event: PostPublishedEvent):
    await social_metrics_service.schedule_sync(event.post_id)
```

---

## 🔐 INVARIANTS PER AGGREGATE

### TokenWallet

- `balance >= 0` (mai negativo)
- `total_used <= total_purchased + total_bonus`
- Ogni transazione deve aggiornare atomicamente balance

### Campaign

- `start_date <= end_date`
- `spent_tokens <= budget_tokens`
- Status transitions: `planning → active → paused → completed`

### Workflow

- Status transitions: `draft → active → paused → archived`
- Actions array non vuoto quando status = active
- Trigger config valido per trigger_type

### BrandDNA

- `account_id` UNIQUE (1:1 con Account)
- Ogni update crea nuova version
- `primary_color` formato hex valido

### ContentApproval

- `current_step <= len(workflow.steps)`
- Status transitions: `pending → in_review → approved/rejected`
- Non può essere approved se step precedenti non completati

---

## 📁 FOLDER STRUCTURE (DDD)

```
apps/backend/app/
├── domain/
│   ├── identity/
│   │   ├── models.py          # User, AdminUser, SocialAccount
│   │   ├── services.py        # AuthService, SocialAccountService
│   │   ├── repositories.py    # UserRepository, SocialAccountRepository
│   │   ├── events.py          # UserRegistered, SocialAccountConnected
│   │   └── exceptions.py      # AuthenticationError, TokenExpiredError
│   │
│   ├── billing/
│   │   ├── models.py          # TokenWallet, Invoice, PromoCode
│   │   ├── services.py        # TokenConsumptionService, PricingService
│   │   ├── repositories.py    # TokenWalletRepository, InvoiceRepository
│   │   ├── events.py          # TokensPurchased, TokensConsumed
│   │   └── exceptions.py      # InsufficientTokensError
│   │
│   ├── content/
│   │   ├── models.py          # Campaign, ScheduledPost, Lead
│   │   ├── services.py        # ContentSchedulingService, LeadScoringService
│   │   ├── repositories.py    # CampaignRepository, LeadRepository
│   │   ├── events.py          # PostPublished, LeadCreated
│   │   └── exceptions.py      # SchedulingConflictError
│   │
│   ├── analytics/
│   │   ├── models.py          # SocialMetrics, SentimentAnalysis
│   │   ├── services.py        # MetricsSyncService, SentimentService
│   │   ├── repositories.py    # SocialMetricsRepository
│   │   └── events.py          # MetricsSynced, SentimentAnalyzed
│   │
│   ├── social/
│   │   ├── models.py          # CrossPostConfig, SocialComment
│   │   ├── services.py        # CrossPostingService, MentionService
│   │   ├── repositories.py    # CrossPostRepository
│   │   └── events.py          # CrossPostCompleted, MentionDetected
│   │
│   ├── ai_services/
│   │   ├── models.py          # AIJob, ContentGeneration, BrandDNA
│   │   ├── services.py        # ContentGenerationService, BrandDNAService
│   │   ├── repositories.py    # AIJobRepository, BrandDNARepository
│   │   └── events.py          # ContentGenerated, BrandDNAUpdated
│   │
│   ├── workflow/
│   │   ├── models.py          # Workflow, WorkflowExecution
│   │   ├── services.py        # WorkflowEngineService, ApprovalService
│   │   ├── repositories.py    # WorkflowRepository
│   │   └── events.py          # WorkflowExecutionCompleted
│   │
│   └── knowledge_base/
│       ├── models.py          # KnowledgeDocument, DocumentChunk
│       ├── services.py        # DocumentProcessingService, SearchService
│       ├── repositories.py    # KnowledgeDocumentRepository
│       └── events.py          # DocumentProcessed, SearchPerformed
│
├── application/
│   ├── use_cases/             # Application services / Use cases
│   │   ├── generate_content.py
│   │   ├── schedule_post.py
│   │   ├── process_payment.py
│   │   └── execute_workflow.py
│   └── dtos/                  # Data Transfer Objects
│
├── infrastructure/
│   ├── database/
│   │   ├── session.py
│   │   └── repositories/      # SQLAlchemy implementations
│   ├── external/
│   │   ├── stripe_client.py
│   │   ├── openai_client.py
│   │   └── social_apis/
│   └── messaging/
│       ├── event_bus.py
│       └── job_queue.py
│
└── api/
    ├── v1/
    │   ├── identity/
    │   ├── billing/
    │   ├── content/
    │   ├── analytics/
    │   ├── social/
    │   ├── ai/
    │   ├── workflow/
    │   └── knowledge/
    └── middleware/
```

---

## ✅ CHECKLIST IMPLEMENTAZIONE

### Phase 1: Core Infrastructure

- [ ] Migrazioni Alembic per nuove tabelle
- [ ] Row Level Security policies
- [ ] Materialized Views + refresh jobs
- [ ] Event Bus setup

### Phase 2: Identity & Billing

- [ ] Social Account management
- [ ] Service Pricing dinamico
- [ ] Invoice generation
- [ ] Promo codes system

### Phase 3: Content & Social

- [ ] Campaigns con multi-post
- [ ] Content versioning
- [ ] Cross-posting
- [ ] Comment/Mention tracking

### Phase 4: AI & Analytics

- [ ] AI Job queue
- [ ] Content/Image/Video generation history
- [ ] Brand DNA versioning
- [ ] Social metrics sync
- [ ] Sentiment analysis

### Phase 5: Workflow & Knowledge

- [ ] Workflow persistence (da in-memory a DB)
- [ ] Approval workflows
- [ ] Knowledge documents
- [ ] Semantic search

### Phase 6: Shared Kernel

- [ ] Domain Events partitioning
- [ ] Feature flags
- [ ] Webhooks
- [ ] Rate limiting
