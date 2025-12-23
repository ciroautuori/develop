# 🚨 IronRep Critical System Analysis
## Date: 2025-11-26

---

## ❌ CRITICAL ISSUES

### 1. ChromaDB EMPTY
```
Collections found: 2
  - user_context: 0 documents
  - ironrep_knowledge: 0 documents
```
**Impact**: All AI agents fail - no knowledge to query

### 2. Exercises Database EMPTY
```sql
SELECT COUNT(*) FROM exercises; -- Returns 0
```
**Impact**: No exercises available for workout generation

### 3. Google API Key LEAKED
```
403 Your API key was reported as leaked. Please use another API key.
```
**Impact**: All LLM calls fail

---

## ⚠️ OBSOLETE "SCIATICA" REFERENCES

The system should be **GENERIC SPORTS MEDICINE**, not sciatica-specific.

### Files to UPDATE:

1. **`apps/backend/src/interfaces/api/main.py`**
   - Line 29: `description="AI-Powered Sciatica Recovery System for CrossFit Athletes"`
   - Line 70: `"message": "ironRep API - Sciatica Recovery System"`

2. **`apps/backend/src/application/dtos/dtos.py`**
   - Line 147: `diagnosis: str = Field(default="Sciatica")`

3. **`apps/backend/src/domain/entities/user.py`**
   - Line 50: `diagnosis: str = "Sciatica"`

4. **`apps/backend/src/domain/entities/user_profile.py`**
   - Line 37: `diagnosis: str = "Sciatica"`

5. **`apps/backend/src/infrastructure/persistence/models.py`**
   - Line 31: `diagnosis = Column(String(255), nullable=False, default='Sciatica')`
   - Line 234: `diagnosis = Column(String, default="Sciatica")`

6. **`apps/backend/alembic/versions/001_add_users_table.py`**
   - Line 34: `server_default='Sciatica'`

7. **`apps/backend/data/knowledge_base/sciatica_medical_knowledge.md`**
   - This file should be DELETED - replaced by `sports_medicine_knowledge_base.md`

---

## ✅ CORRECT FILES (Keep these)

1. **`apps/backend/data/sports_medicine_knowledge_base.md`**
   - Generic sports medicine knowledge
   - Supports: sciatica, pubalgia, shoulder_impingement, patellar_tendinitis, etc.

2. **`apps/backend/data/crossfit_knowledge_base.md`**
   - CrossFit movement standards

3. **`apps/backend/data/knowledge_base/fit_recipes.md`**
   - Nutrition recipes

4. **`apps/backend/data/knowledge_base/crossfit_movement_standards.md`**
   - Movement standards

---

## 🔧 REQUIRED ACTIONS (Priority Order)

### P0 - CRITICAL
1. [ ] Create new Google API key and update `.env`
2. [ ] Populate ChromaDB with knowledge base documents
3. [ ] Populate exercises database from `exercises.json` or `final/exercises_complete.json`

### P1 - HIGH
4. [ ] Update all "Sciatica" defaults to "" or "Generic Sports Injury"
5. [ ] Delete `sciatica_medical_knowledge.md` (obsolete)
6. [ ] Update API descriptions to be generic

### P2 - MEDIUM
7. [ ] Complete database migration 007 (injury_risk_profile)
8. [ ] Fix exercise_preferences table

---

## 📋 Database Migration Status

```
Current DB version: 006 (exercise_preferences created)
Pending: 007 (rename sciatica_risk to injury_risk_profile)
```

The 007 migration is BLOCKED because:
- Index name mismatch: `idx_exercises_sciatica_risk` vs `ix_exercises_sciatica_risk`

---

## 🗂️ Data Files Available

```
/apps/backend/data/
├── crossfit_knowledge_base.md      ✅ Keep
├── exercises.json                   ✅ Load into DB
├── sports_medicine_knowledge_base.md ✅ Keep (MAIN medical KB)
├── user_profile_ciro.md             ✅ Example user
├── final/
│   └── exercises_complete.json      ✅ Load into DB
└── knowledge_base/
    ├── crossfit_movement_standards.md ✅ Keep
    ├── fit_recipes.md                 ✅ Keep
    └── sciatica_medical_knowledge.md  ❌ DELETE (obsolete)
```
