# 🗄️ MARKETTINA v2.0 - Schema ER Enterprise-Grade

**Versione**: 2.0.0
**Data**: 2024-12-06
**Autore**: AI Architect
**Stack**: PostgreSQL 16 + SQLAlchemy ORM + Alembic

---

## 📋 INDICE

1. [Risposte alle Domande Finali](#risposte-alle-domande-finali)
2. [Bounded Contexts Overview](#bounded-contexts-overview)
3. [Entità Esistenti (NON Duplicare)](#entità-esistenti)
4. [Nuove Entità per Context](#nuove-entità)
5. [Pattern Architetturali](#pattern-architetturali)
6. [Diagramma ER Mermaid](#diagramma-er)
7. [DDL SQL Completo](#ddl-sql)
8. [Materialized Views](#materialized-views)
9. [Indici e Performance](#indici)

---

## 🎯 RISPOSTE ALLE DOMANDE FINALI

### **A) DNA Branding - Multipli DNA per Account**

**RACCOMANDAZIONE**: Per v1.0, mantenere **1 DNA = 1 Account** (relazione 1:1).

**Motivazioni**:

- La codebase esistente (`BrandSettings`) ha già `admin_id` con `unique=True`
- Semplifica la logica di prompt enrichment AI
- Per agenzie multi-cliente, usare **sub-accounts** (account figli con proprio DNA)

**Evoluzione v2.0**: Se necessario, aggiungere `brand_profiles` (1:N) per gestire multipli brand per account.

```sql
-- v1.0: 1:1 (esistente)
brand_dna.account_id UNIQUE → accounts.id

-- v2.0 (futuro): 1:N
brand_profiles.account_id → accounts.id (NON unique)
```

---

### **B) Sistema Pagamento - Stripe Integration**

**RACCOMANDAZIONE**: **Integrazione Stripe diretta** con gestione token interna.

La codebase `Token-Payments` ha già:

- `TokenWallet`, `TokenTransaction`, `TokenPackage` ✅
- `Subscription`, `Payment` con Stripe integration ✅

**Da aggiungere**:

- `Invoice` per billing history
- `PromoCode` per referral/sconti
- `ServicePricing` per costi dinamici per servizio

```sql
-- Flow: User → Stripe Checkout → Webhook → TokenTransaction → TokenWallet
```

---

### **C) Event Sourcing - Tabella Unica vs Separate**

**RACCOMANDAZIONE**: **Tabella unica `domain_events`** con partitioning.

**Motivazioni**:

- Flessibilità per nuovi aggregati senza DDL changes
- Query cross-aggregate (audit trail completo)
- Partitioning per `created_at` (monthly) per performance

```sql
-- Partitioning strategy
CREATE TABLE domain_events (
    ...
) PARTITION BY RANGE (created_at);

CREATE TABLE domain_events_2024_12 PARTITION OF domain_events
    FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');
```

---

## 🏗️ BOUNDED CONTEXTS OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MARKETTINA v2.0 DDD                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   IDENTITY   │  │   BILLING    │  │   CONTENT    │  │  ANALYTICS   │   │
│  │   Context    │  │   Context    │  │   Context    │  │   Context    │   │
│  │              │  │              │  │              │  │              │   │
│  │ • User       │  │ • TokenWallet│  │ • Lead       │  │ • SocialMetr │   │
│  │ • AdminUser  │  │ • TokenTrans │  │ • Campaign   │  │ • Sentiment  │   │
│  │ • SocialAcct │  │ • TokenPkg   │  │ • Post       │  │ • Competitor │   │
│  │ • OAuthToken │  │ • Invoice    │  │ • Template   │  │ • Prediction │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │    SOCIAL    │  │ AI SERVICES  │  │   WORKFLOW   │  │  KNOWLEDGE   │   │
│  │   Context    │  │   Context    │  │   Context    │  │    BASE      │   │
│  │              │  │              │  │              │  │              │   │
│  │ • SocialAcct │  │ • AIJob      │  │ • Workflow   │  │ • Document   │   │
│  │ • CrossPost  │  │ • ContentGen │  │ • Execution  │  │ • Chunk      │   │
│  │ • Comment    │  │ • ImageGen   │  │ • Schedule   │  │ • Category   │   │
│  │ • Mention    │  │ • DNAAnalysis│  │ • Action     │  │ • SearchHist │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SHARED KERNEL (Cross-Cutting)                     │   │
│  │  • domain_events • feature_flags • webhooks • api_rate_limits       │   │
│  │  • idempotency_keys • async_jobs                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ✅ ENTITÀ ESISTENTI (NON DUPLICARE)

### Identity Context (apps/backend)

| Tabella            | File                          | Note                        |
| ------------------ | ----------------------------- | --------------------------- |
| `users`            | `domain/auth/models.py`       | User con roles              |
| `admin_users`      | `domain/auth/admin_models.py` | Admin separati              |
| `admin_sessions`   | `domain/auth/admin_models.py` | Session tracking            |
| `admin_audit_logs` | `domain/auth/admin_models.py` | Audit trail                 |
| `oauth_tokens`     | `domain/auth/models.py`       | OAuth tokens (relationship) |

### Marketing Context (apps/backend)

| Tabella               | File                         | Note             |
| --------------------- | ---------------------------- | ---------------- |
| `leads`               | `domain/marketing/models.py` | Lead con scoring |
| `email_campaigns`     | `domain/marketing/models.py` | Email marketing  |
| `scheduled_posts`     | `domain/marketing/models.py` | Post programmati |
| `editorial_calendars` | `domain/marketing/models.py` | Calendari        |
| `brand_settings`      | `domain/marketing/models.py` | Brand DNA base   |

### CRM Context (apps/backend)

| Tabella                 | File                         | Note            |
| ----------------------- | ---------------------------- | --------------- |
| `customers`             | `domain/customers/models.py` | Anagrafica CRM  |
| `customer_notes`        | `domain/customers/models.py` | Note clienti    |
| `customer_interactions` | `domain/customers/models.py` | Log interazioni |

### Billing Context (Token-Payments)

| Tabella              | File                               | Note             |
| -------------------- | ---------------------------------- | ---------------- |
| `token_wallets`      | `billing/entities/token_models.py` | Wallet token     |
| `token_transactions` | `billing/entities/token_models.py` | Transazioni      |
| `token_packages`     | `billing/entities/token_models.py` | Pacchetti        |
| `subscriptions`      | `billing/entities/models.py`       | Abbonamenti      |
| `payments`           | `billing/entities/models.py`       | Pagamenti Stripe |
| `usage_records`      | `billing/entities/models.py`       | Usage tracking   |

### Analytics Context (apps/backend)

| Tabella            | File                         | Note            |
| ------------------ | ---------------------------- | --------------- |
| `analytics_events` | `domain/analytics/models.py` | Eventi tracking |

---

## 🆕 NUOVE ENTITÀ PER CONTEXT

### 1. Identity Context - Estensioni

```
┌─────────────────────────────────────────────────────────────────┐
│                    IDENTITY CONTEXT                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [users] ←──────── [social_accounts] ←──── [social_account_health]
│     │                     │                                      │
│     │                     └──────────────── [oauth_connections]  │
│     │                                                            │
│     └──────────── [user_permissions]                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Billing Context - Estensioni

```
┌─────────────────────────────────────────────────────────────────┐
│                    BILLING CONTEXT                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [token_wallets] ←── [token_transactions]                        │
│        │                    │                                    │
│        │                    └──── [service_pricing]              │
│        │                                                         │
│        └──────────── [invoices] ←── [invoice_items]              │
│                                                                  │
│  [promo_codes] ←──── [promo_redemptions]                         │
│                                                                  │
│  [referral_program]                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Content Context - Estensioni

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTENT CONTEXT                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [campaigns] ←──────── [scheduled_posts]                         │
│       │                      │                                   │
│       │                      ├──── [content_versions]            │
│       │                      │                                   │
│       │                      └──── [content_approvals]           │
│       │                                                          │
│       └──────────── [content_variants] (A/B Testing)             │
│                                                                  │
│  [content_templates]                                             │
│                                                                  │
│  [media_assets] ←──── [media_tags]                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4. Analytics Context - Estensioni

```
┌─────────────────────────────────────────────────────────────────┐
│                   ANALYTICS CONTEXT                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [scheduled_posts] ←── [social_metrics]                          │
│                              │                                   │
│                              └──── [sentiment_analysis]          │
│                                                                  │
│  [competitor_profiles] ←── [competitor_metrics]                  │
│                                                                  │
│  [performance_predictions]                                       │
│                                                                  │
│  [aggregated_metrics] (Materialized View)                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5. Social Context - Estensioni

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOCIAL CONTEXT                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [social_accounts] ←── [social_account_health]                   │
│        │                                                         │
│        └──────────── [cross_post_configs]                        │
│                            │                                     │
│                            └──── [cross_posts]                   │
│                                                                  │
│  [social_comments]                                               │
│                                                                  │
│  [social_mentions]                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6. AI Services Context - Estensioni

```
┌─────────────────────────────────────────────────────────────────┐
│                   AI SERVICES CONTEXT                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [ai_jobs] ←──────── [ai_job_logs]                               │
│                                                                  │
│  [content_generations]                                           │
│                                                                  │
│  [image_generations]                                             │
│                                                                  │
│  [video_generations]                                             │
│                                                                  │
│  [brand_dna] ←──── [brand_dna_versions]                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7. Workflow Context - Estensioni

```
┌─────────────────────────────────────────────────────────────────┐
│                   WORKFLOW CONTEXT                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [workflows] ←──────── [workflow_executions]                     │
│       │                       │                                  │
│       │                       └──── [workflow_logs]              │
│       │                                                          │
│       ├──────────── [workflow_actions]                           │
│       │                                                          │
│       ├──────────── [workflow_conditions]                        │
│       │                                                          │
│       └──────────── [workflow_schedules]                         │
│                                                                  │
│  [workflow_templates]                                            │
│                                                                  │
│  [approval_workflows] ←── [content_approvals]                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8. Knowledge Base Context

```
┌─────────────────────────────────────────────────────────────────┐
│                  KNOWLEDGE BASE CONTEXT                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [knowledge_documents] ←── [document_chunks]                     │
│           │                                                      │
│           └──────────── [document_categories]                    │
│                                                                  │
│  [search_history]                                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 9. Shared Kernel (Cross-Cutting)

```
┌─────────────────────────────────────────────────────────────────┐
│                    SHARED KERNEL                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [domain_events]          - Event Sourcing                       │
│                                                                  │
│  [feature_flags]          - Feature toggles                      │
│                                                                  │
│  [webhooks] ←── [webhook_deliveries]                             │
│                                                                  │
│  [api_rate_limits]        - Rate limiting                        │
│                                                                  │
│  [idempotency_keys]       - Idempotent operations                │
│                                                                  │
│  [async_jobs]             - Background job queue                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 PATTERN ARCHITETTURALI

### Multi-Tenancy

Ogni tabella (eccetto lookup globali) ha:

```sql
account_id UUID NOT NULL REFERENCES accounts(id)
```

Con Row Level Security:

```sql
ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;
CREATE POLICY {table}_isolation ON {table}
    USING (account_id = current_setting('app.current_account_id')::uuid);
```

### Soft Delete

```sql
deleted_at TIMESTAMP,
deleted_by UUID REFERENCES users(id)
```

### Optimistic Locking

```sql
version INTEGER DEFAULT 1
```

### Audit Fields

```sql
created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW(),
created_by UUID REFERENCES users(id)
```

---

## 📊 DIAGRAMMA ER MERMAID

Vedi file separato: `MARKETTINA_v2_ER_DIAGRAM.mmd`

---

## 📝 DDL SQL COMPLETO

Vedi file separato: `MARKETTINA_v2_DDL.sql`

---

## 📈 MATERIALIZED VIEWS

Vedi sezione dedicata nel DDL SQL.

---

## 🔍 INDICI E PERFORMANCE

Vedi sezione dedicata nel DDL SQL.
