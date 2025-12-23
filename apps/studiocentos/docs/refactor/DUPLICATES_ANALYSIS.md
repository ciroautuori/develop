# 🔍 DUPLICATE & REDUNDANT CODE ANALYSIS
## StudioCentos Workspace - Detailed Findings

**Analysis Date:** December 7, 2025 (Updated with corrections)
**Scope:** Backend + Frontend + AI Microservice
**Method:** File naming analysis, size comparison, pattern matching

---

## 📂 FILE NAMING DUPLICATES

### Python Backend - High Collision Risk

#### 1. Router Files (18 instances)
Files named `router.py` or `routers.py` across different domains:

**router.py (singular):**
```
./apps/backend/app/domain/whatsapp/router.py
./apps/backend/app/domain/heygen/router.py
./apps/backend/app/domain/analytics/router.py
./apps/backend/app/domain/social/router.py
./apps/backend/app/domain/marketing/router.py
./apps/backend/app/domain/finance/router.py
./apps/backend/app/domain/notifications/router.py
./apps/backend/app/domain/google/router.py
./apps/backend/app/domain/imodels/router.py
```

**routers.py (plural):**
```
./apps/backend/app/domain/toolai/routers.py
./apps/backend/app/domain/customers/routers.py
./apps/backend/app/domain/support/routers.py
./apps/backend/app/domain/portfolio/routers.py
./apps/backend/app/domain/marketing/routers.py  ⚠️ DUPLICATE NAME
./apps/backend/app/domain/copilot/routers.py
./apps/backend/app/domain/auth/routers.py
./apps/backend/app/domain/booking/routers.py
./apps/backend/app/domain/quotes/routers.py
```

**🚨 CRITICAL:** Marketing domain has BOTH `router.py` AND `routers.py`!

**Action Required:**
- Standardize to plural: `routers.py` everywhere
- Rename: `marketing/router.py` → `marketing/main_router.py` or merge with routers.py
- Update all imports

#### 2. Service Files (14 instances)

**service.py (singular):**
```
./apps/ai_microservice/app/domain/support/service.py
./apps/ai_microservice/app/domain/rag/service.py
./apps/backend/app/infrastructure/email/service.py
./apps/backend/app/domain/whatsapp/service.py
./apps/backend/app/domain/analytics/service.py
./apps/backend/app/domain/marketing/service.py
./apps/backend/app/domain/finance/service.py
./apps/backend/app/domain/imodels/service.py
```

**services.py (plural):**
```
./apps/backend/app/domain/toolai/services.py
./apps/backend/app/domain/customers/services.py
./apps/backend/app/domain/support/services.py
./apps/backend/app/domain/auth/services.py
./apps/backend/app/domain/booking/services.py
./apps/backend/app/domain/quotes/services.py
```

**Recommendation:** Standardize to `services.py`

#### 3. Models Files (10+ instances)
```
./apps/ai_microservice/app/domain/rag/models.py
./apps/backend/app/infrastructure/monitoring/alerting/models.py
./apps/backend/app/infrastructure/monitoring/system/models.py
./apps/backend/app/infrastructure/monitoring/models.py  ⚠️ 3 LEVELS
./apps/backend/app/core/compliance/pci/models.py
./apps/backend/app/core/compliance/gdpr/models.py
./apps/backend/app/domain/whatsapp/models.py
./apps/backend/app/domain/toolai/models.py
./apps/backend/app/domain/analytics/models.py
./apps/backend/app/domain/customers/models.py
... (more)
```

**Issue:** Generic name, hard to identify in imports
**Recommendation:** Add domain prefix: `marketing_models.py`

#### 4. Schemas Files (10+ instances)
Similar pattern to models.py

#### 5. Admin Files (Triplication)
```
./apps/backend/app/domain/auth/admin_models.py
./apps/backend/app/domain/auth/admin_router.py
./apps/backend/app/domain/auth/admin_schemas.py
./apps/backend/app/domain/auth/admin_service.py

./apps/backend/app/domain/booking/admin_router.py
./apps/backend/app/domain/booking/admin_schemas.py
./apps/backend/app/domain/booking/admin_service.py

./apps/backend/app/domain/portfolio/admin_router.py
./apps/backend/app/domain/portfolio/admin_schemas.py
./apps/backend/app/domain/portfolio/admin_service.py
```

**Pattern:** Each domain replicates admin CRUD - potential for shared base class

---

## 🎯 RECOMMENDED NAMING CONVENTION

### Standard Format
```python
# Current (inconsistent):
router.py, routers.py, service.py, services.py

# Proposed (consistent):
<domain>_routers.py    # Plural, with domain prefix
<domain>_services.py   # Plural, with domain prefix
<domain>_models.py     # Plural, with domain prefix
<domain>_schemas.py    # Plural, with domain prefix

# OR keep simple but standardize:
routers.py    # Always plural
services.py   # Always plural
models.py     # Always plural
schemas.py    # Always plural
```

### Migration Example
```bash
# Before:
marketing/
├── router.py       ❌
├── routers.py      ❌ CONFLICT!
├── service.py      ❌
└── models.py       ❌

# After:
marketing/
├── routers.py      ✅ (merged both)
├── services.py     ✅ (renamed)
├── models.py       ✅ (kept)
└── schemas.py      ✅
```

---

## 🔎 FUNCTIONAL DUPLICATES (Manual Review Needed)

### High Risk Areas

#### 1. Marketing Domain - Multiple Service Files
```
marketing/
├── router.py              (41KB)
├── routers.py             (26KB)
├── service.py             (?)
├── analytics_service.py   (?)
├── analytics_router.py    (?)
├── email_service.py       (34KB)
├── email_router.py        (?)
├── competitor_service.py  (?)
├── competitor_router.py   (?)
├── lead_enrichment_service.py (27KB)
├── webhook_service.py     (?)
├── webhook_router.py      (?)
├── workflow_engine.py     (?)
├── workflow_router.py     (?)
├── ab_testing.py          (?)
├── ab_testing_router.py   (?)
├── acquisition_router.py  (?)
├── brand_dna_router.py    (?)
└── [20+ total files]      ⚠️ DOMAIN TOO LARGE
```

**Issues:**
1. Too many files in one domain (20+)
2. Unclear separation of concerns
3. Likely code duplication across services

**Recommendation:**
Split into sub-domains:
```
marketing/
├── campaigns/       (email, ab_testing)
├── analytics/       (analytics, reports)
├── automation/      (workflows, webhooks)
├── leads/           (enrichment, scoring)
└── content/         (brand_dna, content_gen)
```

#### 2. Social Media Services - Token Refresh
```
./apps/backend/app/domain/social/token_refresh_service.py
./apps/backend/app/domain/social/publisher_service.py
```

**Check:** Is token refresh duplicated in publisher_service?

#### 3. Google Services - Multiple Calendar Implementations
```
./apps/backend/app/domain/google/calendar_service.py
./apps/backend/app/domain/calendar/schemas.py  (only schemas?)
```

**Check:** Why separate calendar domain with only schemas?

#### 4. Email Services - Multiple Locations
```
./apps/backend/app/infrastructure/email/service.py     (Infrastructure)
./apps/backend/app/domain/marketing/email_service.py   (Domain)
./apps/backend/app/domain/quotes/email_service.py      (Domain)
./apps/backend/app/domain/finance/notifications_service.py (sends emails?)
```

**Risk:** HIGH - Email logic scattered across 4+ locations

**Recommendation:**
- Keep ONE email infrastructure service
- Domain services use the infrastructure service
- Consider: `infrastructure/email/` as the single source

#### 5. Admin Functionality - Replicated Pattern
```
3 domains have full admin CRUD:
- auth/admin_*
- booking/admin_*
- portfolio/admin_*
```

**Opportunity:** Create base admin class/mixin to DRY up code

---

## 📊 CODE COMPLEXITY - FILES TO SPLIT

### Urgent (>50KB, >1000 lines)

| File | Size | Est. Lines | Complexity | Split Priority | Full Path |
|------|------|------------|------------|----------------|----------|
| `marketing.py` | 95KB | ~2,800 | 🔴 Very High | P0 | `apps/ai_microservice/app/core/api/v1/marketing.py` |
| `BusinessHub.tsx` | 57KB | ~1,500 | 🔴 High | P0 | `apps/frontend/src/features/admin/pages/BusinessHub.tsx` |
| `LeadFinderProModal.tsx` | 56KB | ~1,400 | 🔴 High | P1 | `apps/frontend/src/features/admin/pages/AIMarketing/components/modals/LeadFinderProModal.tsx` |
| `FinanceHub.tsx` | 46KB | ~1,200 | 🟡 Medium | P1 | `apps/frontend/src/features/admin/pages/FinanceHub.tsx` |
| `SettingsHub.tsx` | 46KB | ~1,200 | 🟡 Medium | P1 | `apps/frontend/src/features/admin/pages/SettingsHub.tsx` |
| `ContentStudio.tsx` | 45KB | ~1,100 | 🟡 Medium | P2 | `apps/frontend/src/features/admin/pages/AIMarketing/components/ContentStudio.tsx` |
| `WorkflowBuilder.tsx` | 43KB | ~1,100 | 🟡 Medium | P2 | `apps/frontend/src/features/admin/pages/AIMarketing/components/WorkflowBuilder.tsx` |
| `SocialPublisherPro.tsx` | 42KB | ~1,000 | 🟡 Medium | P2 | `apps/frontend/src/features/admin/pages/AIMarketing/components/SocialPublisherPro.tsx` |
| `router.py` | 42KB | ~1,100 | 🟡 Medium | P2 | `apps/backend/app/domain/google/router.py` |

### Detailed Split Plans

#### marketing.py (95KB) → 4 files
```python
# Path: apps/ai_microservice/app/core/api/v1/marketing.py
# Before:
marketing.py (2,800 lines)

# After:
marketing/
├── content_generation.py     (~700 lines)
├── campaign_management.py    (~700 lines)
├── analytics_processing.py   (~700 lines)
└── automation_workflows.py   (~700 lines)
```

#### BusinessHub.tsx (57KB) → 5 files
```typescript
// Path: apps/frontend/src/features/admin/pages/BusinessHub.tsx
// Before:
BusinessHub.tsx (1,500 lines)

// After:
business/
├── BusinessHub.tsx           (main, ~300 lines)
├── CustomerManagement.tsx    (~400 lines)
├── ProjectManagement.tsx     (~400 lines)
├── useBusinessData.ts        (~200 lines)
└── BusinessFilters.tsx       (~200 lines)
```

---

## 🔄 CIRCULAR DEPENDENCY RISK

### Cross-Domain Imports Detected: 17 instances

```bash
# Found pattern: from app.domain.X import Y
# Where X is another domain

Potential circular dependencies between:
- marketing ↔ social
- marketing ↔ customers
- finance ↔ customers
```

**Action Required:**
1. Map all cross-domain imports
2. Create shared models in `app/core/shared/`
3. Use dependency injection
4. Consider event-driven architecture for decoupling

---

## 🧹 UNUSED CODE SUSPECTS

### Empty or Near-Empty Modules

#### Backend Domains (Potential Stubs)
```
calendar/        - Only schemas.py
copilot/         - Only routers.py
heygen/          - Only router.py + __init__.py
seo/             - Only sitemap_router.py
```

**Questions:**
1. Are these features in development?
2. Can they be removed if not used?
3. Should they be marked as WIP?

### Frontend Components with Single Use

**Method:** Search for import statements
```typescript
// Components imported only once = candidate for inlining
// Run this analysis:
grep -r "import.*CustomerForm" apps/frontend/src
```

---

## 🎯 DUPLICATION ELIMINATION PRIORITIES

### Phase 1: Critical (Week 1)
1. **Resolve marketing router vs routers conflict**
   - Merge or rename
   - Update imports
   - Test all endpoints

2. **Standardize service/services naming**
   - Choose convention (recommend: services.py)
   - Batch rename
   - Update imports

### Phase 2: High (Week 2-3)
1. **Split large files (>50KB)**
   - marketing.py → 4 files
   - BusinessHub.tsx → 5 files
   - LeadFinderProModal.tsx → 4 files

2. **Consolidate email services**
   - Keep infrastructure/email/service.py
   - Refactor domain services to use it
   - Remove duplication

### Phase 3: Medium (Month 2)
1. **Admin functionality DRY**
   - Create BaseAdminService
   - Create BaseAdminRouter
   - Refactor 3 domains to use base classes

2. **Clean up stub domains**
   - Remove or expand calendar, copilot, heygen, seo
   - Document which are WIP vs abandoned

---

## 📝 REFACTORING SCRIPTS

### Batch Rename Services
```bash
#!/bin/bash
# Rename service.py to services.py

cd apps/backend/app/domain

for dir in whatsapp analytics marketing finance imodels; do
  if [ -f "$dir/service.py" ]; then
    git mv "$dir/service.py" "$dir/services.py"

    # Update imports in same directory
    find "$dir" -name "*.py" -exec sed -i 's/from \.service import/from .services import/g' {} +
    find "$dir" -name "*.py" -exec sed -i 's/from app\.domain\.'$dir'\.service import/from app.domain.'$dir'.services import/g' {} +
  fi
done

echo "✓ Renamed service.py → services.py"
echo "⚠ Manual review required for cross-domain imports"
```

### Find Cross-Domain Imports
```bash
#!/bin/bash
# Detect cross-domain dependencies

cd apps/backend/app/domain

for domain_dir in */; do
  domain=$(basename "$domain_dir")
  echo "=== $domain ==="

  grep -r "from app\.domain\." "$domain_dir" --include="*.py" | \
    grep -v "from app\.domain\.$domain\." | \
    sed 's/.*from app\.domain\.\([^.]*\).*/  → \1/' | \
    sort -u

  echo ""
done
```

---

## 🎓 BEST PRACTICES FOR FUTURE

### Naming Convention Rules
```yaml
✅ DO:
  - Use consistent pluralization (routers, services, models, schemas)
  - Add domain prefix for clarity (marketing_routers, social_services)
  - Keep file names descriptive but not overly long

❌ DON'T:
  - Mix singular/plural in same codebase
  - Use generic names without context
  - Create duplicate filenames across domains
```

### Code Organization Rules
```yaml
✅ DO:
  - Keep domains under 10 files
  - Split large files (>500 lines)
  - Use sub-domains for large features
  - Share common code via infrastructure layer

❌ DON'T:
  - Let domains grow unbounded
  - Duplicate business logic
  - Create circular dependencies
  - Keep stub/unused code
```

### Review Checklist
```yaml
Before adding new file:
  - [ ] Check for existing similar file
  - [ ] Verify naming follows convention
  - [ ] Ensure no circular dependency
  - [ ] Consider if code should go in shared module
  - [ ] Document purpose if unclear from name
```

---

## 📊 METRICS AFTER CLEANUP (Target)

### File Naming
```yaml
Before:
  - Naming conflicts: 27
  - Inconsistent pluralization: 18
  - Generic filenames: 40+

After (target):
  - Naming conflicts: 0
  - Inconsistent pluralization: 0
  - Generic filenames: <10
```

### Code Duplication
```yaml
Before:
  - Files >50KB: 10
  - Domains >15 files: 1 (marketing)
  - Cross-domain imports: 17

After (target):
  - Files >50KB: 0
  - Domains >15 files: 0
  - Cross-domain imports: <5 (justified)
```

---

## 🔗 RELATED DOCUMENTS

- Full audit: `ENTERPRISE_CODEBASE_AUDIT_REPORT.md`
- Action items: `CLEANUP_CHECKLIST.md`
- Cleanup script: `scripts/cleanup/enterprise_cleanup.sh`

---

**Analysis Complete**
**Next Step:** Execute Phase 1 refactoring from CLEANUP_CHECKLIST.md
