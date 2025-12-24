# 🥗 Workflow Intelligente Nutrizione

## Architettura Integrata

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     WORKFLOW NUTRIZIONE INTELLIGENTE                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │   FRONTEND   │     │   BACKEND    │     │   CHROMADB   │            │
│  │   (React)    │────▶│   (FastAPI)  │────▶│    (RAG)     │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│         │                    │                    │                     │
│         ▼                    ▼                    ▼                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │  FatSecret   │     │ Smart Tools  │     │   9459 docs  │            │
│  │  API (Wizard)│     │  (Unified)   │     │ USDA + OFF   │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│         │                    │                    │                     │
│         └────────────┬───────┴───────────────────┘                     │
│                      ▼                                                  │
│              ┌──────────────┐                                          │
│              │ NutritionAgent│                                          │
│              │  (LangChain) │                                          │
│              └──────────────┘                                          │
│                      │                                                  │
│                      ▼                                                  │
│              ┌──────────────┐                                          │
│              │ Piano/Ricette│                                          │
│              │ Personalizzati│                                          │
│              └──────────────┘                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🔧 Componenti

### 1. Frontend - Wizard Preferenze
**File:** `apps/frontend/src/features/wizard/steps/FoodPreferencesStep.tsx`

- Usa FatSecret API per ricerca alimenti
- Salva preferenze utente (cibi preferiti/da evitare)
- I dati vengono passati all'agente tramite `plansApi.savePreferences()`

### 2. Backend - Smart Nutrition Tools
**File:** `apps/backend/src/infrastructure/ai/tools/smart_nutrition_tools.py`

**Strategia Unificata:**

| Tool | Funzione | Sorgente Dati |
|------|----------|---------------|
| `food_search` | Cerca valori nutrizionali | **FatSecret API (Geolocalized)** ONLY |
| `recipe_search` | Cerca ricette fitness | RAG (Ricette Certificate) |
| `user_preferences` | Recupera preferenze utente | User Context |
| `nutrition_guidelines` | Linee guida per obiettivo | RAG knowledge base |

> [!IMPORTANT]
> **FatSecret Only**: Non facciamo affidamento su database locali per i valori nutrizionali degli alimenti. Usiamo solo dati live e geolocalizzati di FatSecret per garantire precisione assoluta.

### 3. RAG - ChromaDB Knowledge Base
**Documenti totali:** ~200 (Solo Ricette e Guidelines)

| Sorgente | Contenuto | Uso |
|----------|-----------|-----|
| Ricette Fitness | 123 | Piani pasto per sportivi |
| Medical Info | 141 | Restrizioni alimentari |
| Training | 727 | Cross-reference |

> [!NOTE]
> I database generici (USDA/OpenFoodFacts) sono stati rimossi in favore dell'API live.

### 4. NutritionAgent
**File:** `apps/backend/src/infrastructure/ai/agents/nutrition_agent.py`

**Capacità:**
- Genera piani settimanali personalizzati
- Suggerisce ricette basate su obiettivi
- Risponde a domande nutrizionali
- Considera preferenze utente e restrizioni mediche

## 🔄 Flusso Dati

```
1. WIZARD (Frontend)
   │
   ├─ Utente cerca alimenti → FatSecret API
   ├─ Salva preferiti/evitare
   └─ Passa a backend via savePreferences()

2. BACKEND (API)
   │
   ├─ Riceve richiesta nutrizionista
   ├─ Carica preferenze utente
   └─ Chiama NutritionAgent

3. NUTRITION AGENT
   │
   ├─ Riceve contesto utente
   ├─ Usa smart tools:
   │   ├─ food_search → RAG (9459 alimenti)
   │   ├─ recipe_search → RAG (123 ricette)
   │   └─ user_preferences → User Context
   └─ Genera risposta personalizzata

4. RISPOSTA
   │
   └─ Piano/ricette/consigli → Frontend
```

## 📝 Ricette Fitness Enhanced

**File:** `apps/backend/data/rag/nutrition/fit_recipes_enhanced.json`

**8 Ricette Ottimizzate:**

1. **Bowl Proteico Post-Workout** - 650kcal, 45g proteine
2. **Overnight Oats Energetici** - 480kcal, pre-workout
3. **Salmone al Forno con Verdure** - 580kcal, anti-infiammatorio
4. **Shake Proteico Fatto in Casa** - 420kcal, 35g proteine
5. **Insalata Proteica Mediterranea** - 520kcal, cutting
6. **Pasta Integrale con Tonno** - 550kcal, training day
7. **Pancakes Proteici** - 380kcal, colazione
8. **Buddha Bowl Vegano** - 620kcal, 38g proteine vegetali

**Caratteristiche:**
- Istruzioni passo-passo dettagliate
- Macro ratio ottimizzati per obiettivo
- Timing consigliato (pre/post workout)
- Sport-specific tags
- Benefici per recupero/energia

## 🚀 Come Usare

### Test ricerca alimenti
```bash
curl -X POST http://localhost:8000/api/knowledge-base/search \
  -H "Content-Type: application/json" \
  -d '{"query": "pollo proteine", "k": 5, "category": "nutrition"}'
```

### Test via NutritionAgent
```python
from src.infrastructure.config.dependencies import Dependencies

deps = Dependencies()
agent = deps.get_nutrition_agent(db, user_id="123")

response = await agent.answer_question(
    "Suggeriscimi una ricetta post-workout ad alto contenuto proteico"
)
```

## 📊 Metriche

| Metrica | Prima | Dopo |
|---------|-------|------|
| Alimenti searchabili | 0 (API live) | **9459** (RAG locale) |
| Ricette fitness | 115 (base) | **123** (enhanced) |
| Preferenze utente | ❌ Non usate | ✅ Integrate |
| Fonti dati unificate | ❌ 3 separate | ✅ 1 workflow |

---

*Ultimo aggiornamento: Novembre 2025*
