# 🗄️ MARKETTINA v2.0 - Database Schema Documentation

## 📁 File Structure

```
docs/database/
├── README.md                          # This file
├── MARKETTINA_v2_ER_SCHEMA.md        # Overview + Risposte domande finali
├── MARKETTINA_v2_ER_DIAGRAM.mmd      # Mermaid ER Diagram
├── MARKETTINA_v2_DDD_MAPPING.md      # DDD Bounded Contexts mapping
├── MARKETTINA_v2_DDL_PART1.sql       # DDL: Accounts, Identity, Billing
├── MARKETTINA_v2_DDL_PART2.sql       # DDL: Content, Analytics
├── MARKETTINA_v2_DDL_PART3.sql       # DDL: Social, AI Services
├── MARKETTINA_v2_DDL_PART4.sql       # DDL: Workflow, Knowledge Base, Shared Kernel
└── MARKETTINA_v2_DDL_PART5_VIEWS.sql # Materialized Views, Triggers, RLS
```

---

## 🎯 Quick Summary

### Risposte alle Domande Finali

| Domanda                                   | Risposta                                                                                                 |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **A) DNA Branding multipli per account?** | **NO per v1.0** - Mantenere 1:1 (account_id UNIQUE). Per agenzie, usare sub-accounts.                    |
| **B) Stripe integration?**                | **SÌ** - Integrazione diretta Stripe + gestione token interna. Aggiungere `invoices`, `service_pricing`. |
| **C) Event Sourcing tabella unica?**      | **SÌ** - Tabella unica `domain_events` con **partitioning mensile** per performance.                     |

---

## 📊 Statistics

| Metric                 | Count |
| ---------------------- | ----- |
| **Bounded Contexts**   | 9     |
| **Nuove Tabelle**      | 45+   |
| **Materialized Views** | 6     |
| **Indici**             | 80+   |
| **Triggers**           | 5     |
| **RLS Policies**       | 10    |

---

## 🏗️ Bounded Contexts

1. **Identity Context** - Auth, Social Accounts, Permissions
2. **Billing Context** - Tokens, Payments, Invoices, Promos
3. **Content Context** - Campaigns, Posts, Templates, Media
4. **Analytics Context** - Metrics, Sentiment, Competitors
5. **Social Context** - Cross-posting, Comments, Mentions
6. **AI Services Context** - Jobs, Generations, Brand DNA
7. **Workflow Context** - Automation, Approvals
8. **Knowledge Base Context** - Documents, RAG, Search
9. **Shared Kernel** - Events, Flags, Webhooks, Rate Limits

---

## 🚀 How to Apply

### 1. Review existing migrations

```bash
cd apps/backend
ls alembic/versions/
```

### 2. Create new migration

```bash
cd apps/backend
uv run alembic revision --autogenerate -m "markettina_v2_schema"
```

### 3. Apply DDL manually (for new tables)

```bash
# Connect to PostgreSQL
psql -U postgres -d markettina

# Run DDL files in order
\i docs/database/MARKETTINA_v2_DDL_PART1.sql
\i docs/database/MARKETTINA_v2_DDL_PART2.sql
\i docs/database/MARKETTINA_v2_DDL_PART3.sql
\i docs/database/MARKETTINA_v2_DDL_PART4.sql
\i docs/database/MARKETTINA_v2_DDL_PART5_VIEWS.sql
```

### 4. View ER Diagram

```bash
# Install Mermaid CLI
pnpm add -g @mermaid-js/mermaid-cli

# Generate PNG
mmdc -i docs/database/MARKETTINA_v2_ER_DIAGRAM.mmd -o docs/database/er_diagram.png

# Or view in VS Code with Mermaid extension
```

---

## ⚠️ Important Notes

### Entità Esistenti (NON duplicare)

Le seguenti tabelle esistono già nella codebase:

- `users`, `admin_users`, `admin_sessions` (Identity)
- `leads`, `email_campaigns`, `scheduled_posts`, `brand_settings` (Marketing)
- `customers`, `customer_notes`, `customer_interactions` (CRM)
- `token_wallets`, `token_transactions`, `token_packages` (Billing)
- `analytics_events` (Analytics)

### Modifiche a tabelle esistenti

```sql
-- Aggiungere campaign_id a scheduled_posts
ALTER TABLE scheduled_posts ADD COLUMN campaign_id UUID REFERENCES campaigns(id);

-- Aggiungere account_id dove manca (per multi-tenancy)
ALTER TABLE leads ADD COLUMN account_id UUID REFERENCES accounts(id);
```

### Multi-Tenancy

Ogni query DEVE filtrare per `account_id`:

```python
# Con RLS attivo
await db.execute("SET app.current_account_id = :id", {"id": str(account_id)})

# Oppure manualmente
query = select(Lead).where(Lead.account_id == account_id)
```

---

## 📈 Performance Considerations

1. **Partitioning**: `domain_events` partizionato per mese
2. **Materialized Views**: Refresh ogni 15 minuti via Celery/pg_cron
3. **Indici**: Ottimizzati per query frequenti (account_id, status, created_at)
4. **Soft Delete**: Tutte le tabelle hanno `deleted_at` per GDPR compliance

---

## 🔗 Related Documentation

- [DDD Mapping](./MARKETTINA_v2_DDD_MAPPING.md) - Aggregates, Events, Services
- [ER Schema](./MARKETTINA_v2_ER_SCHEMA.md) - Overview completo
- [Main README](../../README.md) - Documentazione progetto
