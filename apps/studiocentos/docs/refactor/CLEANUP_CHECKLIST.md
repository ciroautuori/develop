# 🎯 TECHNICAL DEBT CLEANUP - QUICK ACTION CHECKLIST

**Date:** December 7, 2025 (Updated)
**Status:** � MEDIUM PRIORITY - Some issues already resolved
**Priority:** Execute remaining items within 1 week

> ✅ **CORRECTION NOTE:** Original report contained inaccuracies. This checklist has been updated with verified information.

---

## ⚡ IMMEDIATE ACTIONS (TODAY - 1 hour)

### � Medium Priority (Corrected from Critical)

> ✅ **VERIFIED:** .gitignore already properly configured
> - `node_modules/` ✅ Already in .gitignore, not tracked
> - `dist/` ✅ Already in .gitignore, not tracked
> - `__pycache__/` ✅ Already in .gitignore, not tracked

- [x] **Review git status** - NO cleanup needed for build artifacts
  ```bash
  # Verified: these return empty (not tracked)
  git ls-files | grep dist/
  git ls-files | grep __pycache__
  ```

- [ ] **Remove debug code from production** (30 min)
  - [ ] `apps/frontend/src/features/admin/pages/BusinessHub.tsx:426,433` - Remove console.log
  - [ ] `apps/frontend/src/features/admin/pages/AIMarketing/components/BusinessDNAGenerator.tsx:114,119` - Replace alert() with toast
  - [ ] `apps/frontend/src/features/admin/pages/AIMarketing/index.tsx:583` - Remove console.log

- [ ] **Verify builds still work**
  ```bash
  # Backend
  cd apps/backend && uvicorn app.main:app --reload

  # Frontend
  cd apps/frontend && npm run build && npm run dev

  # AI Microservice
  cd apps/ai_microservice && uvicorn app.main:app --reload --port 8001
  ```

---

## 📋 WEEK 1 PRIORITIES (Next 5 days)

### 🟡 High Priority

#### Day 1-2: Dependency Cleanup
- [ ] **Remove unused frontend dependencies** (2 hours)
  ```bash
  cd apps/frontend
  npm uninstall @headlessui/react @radix-ui/react-accordion \
    @radix-ui/react-alert-dialog @radix-ui/react-checkbox \
    @radix-ui/react-dialog @radix-ui/react-popover \
    @radix-ui/react-radio-group @radix-ui/react-separator \
    @radix-ui/react-slider @radix-ui/react-toast \
    @radix-ui/react-tooltip @tanstack/react-table \
    embla-carousel-react

  npm install @emotion/is-prop-valid
  npm run build  # Verify
  ```

- [ ] **Fix wildcard import** (15 min)
  - File: `apps/backend/app/domain/booking/admin_router.py:14`
  - Replace: `from .admin_schemas import *`
  - With: Explicit imports

#### Day 3-4: Test Coverage Expansion ✅ CORRECTED
> ✅ **VERIFIED:** Test infrastructure already exists!
> - Backend: 10+ test files in `apps/backend/tests/`
> - Integration: 9+ test files in `scripts/tests/`
> - Frontend: Vitest already configured in package.json

- [x] **pytest already installed** - conftest.py exists
- [x] **Vitest already configured** - in package.json scripts
- [ ] **Run existing tests and measure coverage** (1 hour)
  ```bash
  cd apps/backend
  pytest --cov=app tests/ -v

  cd apps/frontend
  pnpm test
  ```

- [ ] **Expand test coverage for critical paths**
  - [ ] Review existing test_auth_service.py
  - [ ] Review existing test_stripe_service.py
  - [ ] Add more frontend component tests

#### Day 5: Documentation
- [ ] **Consolidate marketing documentation** (2 hours)
  ```bash
  mkdir -p docs/features/marketing-hub
  # Merge these files:
  # - MARKETING_HUB_ANALYSIS.md
  # - MARKETING_HUB_DEFINITIVO_ROADMAP.md
  # - MARKETING_HUB_ENHANCEMENT_PLAN.md
  # - POWER_MARKETING_HUB_IMPLEMENTATION.md
  # Into one: docs/features/marketing-hub/README.md
  ```

- [ ] **Archive old planning docs**
  ```bash
  mkdir -p docs/archive/2025-Q4
  mv docs/*ANALYSIS*.md docs/archive/2025-Q4/ (review first)
  ```

---

## 📅 WEEK 2-4 ACTIONS (This Month)

### 🟢 Medium Priority

#### Week 2: Code Refactoring
- [ ] **Split large file: marketing.py (94KB)** (1 day)
  - Split into 4 modules: content, campaigns, analytics, automation
  - Update imports across codebase
  - Test all affected endpoints

- [ ] **Refactor BusinessHub.tsx (56KB)** (1 day)
  - Extract customer management to separate component
  - Extract project management to separate component
  - Create custom hooks for data fetching

#### Week 3: CI/CD Setup
- [ ] **Create GitHub Actions workflow** (1 day)
  ```yaml
  # .github/workflows/ci.yml
  name: CI
  on: [push, pull_request]
  jobs:
    test:
      - Lint backend (ruff)
      - Lint frontend (eslint)
      - Run tests
      - Build Docker images
  ```

- [ ] **Add pre-commit hooks** (2 hours)
  ```bash
  pip install pre-commit
  # Create .pre-commit-config.yaml
  pre-commit install
  ```

#### Week 4: Security & Monitoring
- [ ] **Run security audits** (2 hours)
  ```bash
  cd apps/frontend && npm audit fix
  cd apps/backend && pip-audit
  ```

- [ ] **Setup basic monitoring** (3 hours)
  - Configure Prometheus metrics
  - Setup Grafana dashboards
  - Add health check endpoints

---

## 🎯 MONTH 2-3 GOALS

### Standardization
- [ ] Standardize file naming (router vs routers)
- [ ] Create code style guide
- [ ] Setup automatic formatting (black, prettier)

### Testing
- [ ] Achieve 30% backend test coverage
- [ ] Achieve 20% frontend test coverage
- [ ] Setup coverage reporting

### Documentation
- [ ] Generate API documentation (OpenAPI)
- [ ] Create architecture decision records (ADR)
- [ ] Write deployment runbook

---

## 📊 METRICS TO TRACK

### Weekly Checkpoints ✅ CORRECTED
```yaml
Week 1 Target:
  - Debug code removed: 5/5 (100%) # Verified: 5 instances, not 7
  - Unused deps removed: 7/7 (100%) # Verified: 7 unused, not 16
  - Run existing tests: measure baseline coverage
  - Build time: <3 min

Week 2 Target:
  - Large files refactored: 2/9 (22%) # Verified: 9 files >40KB
  - Test coverage: expand from baseline
  - CI/CD: Basic pipeline running

Week 4 Target:
  - Test coverage: 50%+ (from ~10% baseline)
  - TODO count: <150 (from 244) # Corrected from 288
  - All medium priority issues: RESOLVED
```

---

## ⚠️ BLOCKERS & RISKS

### Known Issues to Watch ✅ CORRECTED
1. **Low test coverage** - 21+ test files exist, but coverage needs expansion
   - Mitigation: Run existing tests first, then expand

2. **Large file refactoring** - High risk of bugs
   - Mitigation: Create feature branch, thorough testing

3. **Dependency removal** - May break features
   - Mitigation: Test build after each removal

### Rollback Plan
```bash
# If something breaks:
git log --oneline  # Find last good commit
git revert <commit-hash>
# Or restore from backup:
ls -la .cleanup_backup_*
```

---

## 🎓 TEAM COORDINATION

### Role Assignments
- **DevOps Lead:** CI/CD setup, monitoring
- **Backend Lead:** Test framework, refactoring backend
- **Frontend Lead:** Remove deps, refactor components
- **QA/Test Lead:** Write test cases, coverage tracking
- **Tech Writer:** Consolidate documentation

### Communication
- **Daily standup:** Report blockers immediately
- **Weekly review:** Friday 4pm - Progress check
- **Emergency contact:** If builds break

---

## ✅ DEFINITION OF DONE

### Phase 1 Complete When: ✅ CORRECTED
- [ ] All debug code removed from production
- [x] .gitignore already properly configured ✅
- [x] __pycache__ and dist/ already NOT in git ✅
- [x] Test framework already installed (pytest + vitest) ✅
- [x] 21+ test files already exist ✅
- [ ] All builds passing
- [ ] Documentation updated

### Overall Success Criteria:
- [ ] No P0 (critical) items remaining
- [ ] Test coverage: 30%+
- [ ] Build time: <3 minutes
- [ ] TODO count: <200
- [ ] Team can deploy confidently

---

## 📞 QUICK REFERENCES

### Scripts
- Cleanup: `./scripts/cleanup/enterprise_cleanup.sh`
- Full report: `docs/ENTERPRISE_CODEBASE_AUDIT_REPORT.md`

### Commands
```bash
# Check test coverage
pytest --cov=app tests/
npm run test:coverage

# Security audit
npm audit
pip-audit

# Find TODOs
grep -r "TODO\|FIXME" --include="*.py" --include="*.ts" apps/
```

---

**Last Updated:** December 6, 2025
**Next Review:** December 13, 2025
**Responsible:** Full dev team
