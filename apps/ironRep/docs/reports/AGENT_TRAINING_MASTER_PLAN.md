# 🎓 AGENT TRAINING MASTER PLAN

## Piano Completo per Trainare l'Agente come Medico Sportivo + Trainer CrossFit + Fisioterapista

**Data Creazione**: 23 Novembre 2025
**Versione**: 1.0
**Autore**: AI Medical Coach Team

---

## 📊 EXECUTIVE SUMMARY

### **Obiettivo**

Trasformare l'attuale `MedicalCoachAgent` in un **Elite Sports Medicine AI** con competenze di:

- 🩺 **Medico Sportivo** - Diagnosi, trattamento, gestione infortuni
- 🏋️ **Trainer CrossFit L3** - Programmazione, tecnica, scaling
- 💪 **Fisioterapista** - Riabilitazione, terapia manuale, return-to-sport

### **Stato Attuale**

- ✅ Architettura agent funzionante (LangChain + LLM fallback)
- ✅ RAG system operativo (ChromaDB + HuggingFace embeddings)
- ✅ Context-aware (user profile, pain history, biometrics)
- ✅ Tool system (4 tools specializzati)
- ⚠️ Knowledge base limitata (solo sciatica + CrossFit basics)
- ⚠️ Exercise library piccola (20 esercizi)
- ❌ Nessun fine-tuning
- ❌ Nessuna evaluation sistematica

### **Gap Principali**

1. **Knowledge**: Mancano 18+ documenti su altre patologie
2. **Exercises**: Servono 180+ esercizi aggiuntivi
3. **Training**: Agent usa solo prompt engineering
4. **Quality**: Nessun benchmark o metrica

### **Risultato Atteso**

Un agent che:

- Riconosce e tratta **10+ tipi di infortuni** (non solo sciatica)
- Prescrive da un database di **200+ esercizi** evidence-based
- Ha **92%+ accuracy** su diagnosi e trattamento
- Fornisce risposte **safety-first** (100% red flags detection)
- Impara continuamente da feedback utenti

### **Timeline**

- **Fase 1** (Week 1-2): Knowledge Base Expansion → +18 documenti
- **Fase 2** (Week 3): Exercise Library → +180 esercizi
- **Fase 3** (Week 4-5): Fine-Tuning → Dataset + training
- **Fase 4** (Week 6): Evaluation → Benchmark + testing
- **Fase 5** (Ongoing): Continuous Learning → Feedback loop

### **Risorse Necessarie**

- **Tempo**: 6 settimane full-time
- **Expertise**: Medico sportivo + Fisioterapista + CrossFit L3
- **Compute**: GPU per fine-tuning (opzionale, può usare cloud)
- **Budget**: $500-1000 per API credits (OpenAI fine-tuning)

---

## 📋 TABLE OF CONTENTS

1. [Analisi Stato Attuale](#1-analisi-stato-attuale)
2. [Gap Analysis](#2-gap-analysis)
3. [Strategia Training](#3-strategia-training)
4. [Fase 1: Knowledge Base Expansion](#4-fase-1-knowledge-base-expansion)
5. [Fase 2: Exercise Library Expansion](#5-fase-2-exercise-library-expansion)
6. [Fase 3: Fine-Tuning](#6-fase-3-fine-tuning)
7. [Fase 4: Evaluation & Benchmarking](#7-fase-4-evaluation-benchmarking)
8. [Fase 5: Continuous Learning](#8-fase-5-continuous-learning)
9. [Implementazione Pratica](#9-implementazione-pratica)
10. [Metriche di Successo](#10-metriche-di-successo)

---

## 1. ANALISI STATO ATTUALE

### 1.1 Architettura Agent

#### **MedicalCoachAgent**

```python
Location: src/infrastructure/ai/agents/medical_coach.py
Lines: 417 righe
```

**Capabilities**:

- Generico per qualsiasi infortunio (non solo sciatica)
- System prompt con 15 anni esperienza simulata
- Multi-injury expertise (sciatica, pubalgia, spalla, ginocchio, etc.)
- Assessment iniziale obbligatorio
- Context-aware (user profile, pain, biometrics, RAG)
- Tool integration (4 specialized tools)
- LangChain AgentExecutor con function calling

**System Prompt Highlights**:

```
- 15 anni esperienza riabilitazione atleti
- 500+ casi gestiti
- 92% success rate
- Expertise: lombari, inguinali, spalla, ginocchio, anca, caviglia, gomito
- Protocol dolore universale (7 livelli)
- Red flags detection
```

#### **LLM Service**

```python
Location: src/infrastructure/ai/llm_service.py
Lines: 209 righe
```

**Features**:

- Fallback chain: Groq → OpenRouter → Google Gemini
- Unlimited credits strategy (free models)
- Temperature: 0.7 (bilanciato)
- Max tokens: 2048
- Async support
- Error handling robusto

**Models**:

1. **Primary**: Groq llama-3.3-70b-versatile (100k tokens/day)
2. **Fallback 1**: OpenRouter llama-4-maverick:free (UNLIMITED)
3. **Fallback 2**: Google gemini-2.0-flash-exp (UNLIMITED)

#### **RAG System**

```python
Location: src/infrastructure/ai/rag_service.py
Lines: 220 righe
```

**Components**:

- ChromaDB HTTP client (vector store)
- HuggingFace embeddings (all-MiniLM-L6-v2)
- Semantic search con relevance scores
- Document ingestion automatico
- Metadata filtering

**Current Knowledge Base**:

```
data/knowledge_base/
├── sciatica_medical_knowledge.md (450+ righe)
├── crossfit_movement_standards.md (650+ righe)
└── [MISSING: 18+ altri documenti]
```

#### **Tool System**

```python
Location: src/infrastructure/ai/tools/agent_tools.py
Lines: 479 righe
```

**4 Tools Disponibili**:

1. **pain_analyzer** - Analizza trend dolore ultimi N giorni
2. **red_flags_detector** - Controlla sintomi allarmanti
3. **progression_calculator** - Valuta readiness per fase successiva
4. **exercise_validator** - Valida sicurezza esercizio per injury type

#### **Context System**

**Dati Disponibili per Agent**:

```python
# 1. User Profile
- Nome, età, injury_diagnosis
- Fase attuale, settimane in fase
- Baseline (deadlift, squat)
- Obiettivi, attrezzatura

# 2. Pain History (7 giorni)
- Media dolore
- Localizzazioni comuni
- Trigger comuni
- Trend

# 3. Biometrics
- Latest deadlift (kg, reps)
- Latest squat (kg, reps)
- ROM, body composition

# 4. RAG Knowledge
- Top 5 chunks rilevanti per query
- Injury-specific enhancement

# 5. Chat History
- Persistent in database
- Session management
```

### 1.2 Exercise Library

```json
Location: data/exercises.json
Size: 20 esercizi
```

**Categorie Attuali**:

- Mobility: 6 esercizi
- Strength: 8 esercizi
- Therapeutic: 4 esercizi
- Conditioning: 2 esercizi

**Gap**: Servono 180+ esercizi aggiuntivi

### 1.3 Database Schema

**Tables**:

- `users` - Profili utente
- `pain_assessments` - Check-in giornalieri
- `workout_sessions` - Workouts generati
- `progress_kpis` - KPI settimanali
- `biometric_entries` - Test forza/ROM
- `chat_history` - Conversazioni persistenti

---

## 2. GAP ANALYSIS

### 2.1 Knowledge Base - CRITICO ❌

**Attuale**: 2 documenti (1,100 righe totali)
**Target**: 20+ documenti (10,000+ righe)
**Gap**: 18 documenti mancanti

#### **Documenti Mancanti**:

**Medical Knowledge** (10 documenti):

1. ❌ Pubalgia & Core Injuries (⚠️ PRIORITÀ ALTA)
2. ❌ Shoulder Injuries (impingement, rotator cuff, labrum)
3. ❌ Knee Injuries (patellar tendinitis, meniscus, ACL)
4. ❌ Hip Injuries (FAI, labrum, hip flexor)
5. ❌ Ankle/Foot Injuries (sprains, Achilles, plantar fasciitis)
6. ❌ Elbow/Wrist Injuries (epicondylitis, wrist tendinitis)
7. ❌ Spine Injuries (disc herniation, stenosis, SI joint)
8. ❌ Muscle Strains (hamstring, quad, calf, groin)
9. ❌ Overuse Syndromes (stress fractures, compartment syndrome)
10. ❌ Recovery Science (tissue healing, inflammation, pain science)

**CrossFit Training** (5 documenti):

1. ❌ Olympic Weightlifting Progressions
2. ❌ Gymnastics Progressions
3. ❌ Metabolic Conditioning
4. ❌ Strength & Conditioning Periodization
5. ❌ CrossFit Programming

**Fisioterapia** (5 documenti):

1. ❌ Assessment Protocols
2. ❌ Therapeutic Exercises
3. ❌ Manual Therapy Concepts
4. ❌ Pain Management
5. ❌ Return-to-Sport Protocols

**Impatto**: Agent non può trattare efficacemente 90% degli infortuni

### 2.2 Exercise Library - CRITICO ❌

**Attuale**: 20 esercizi
**Target**: 200+ esercizi
**Gap**: 180 esercizi mancanti

#### **Categorie Mancanti**:

**Therapeutic Exercises** (50 esercizi):

- Isometric holds (Copenhagen plank, wall sit, etc.)
- Eccentric loading (Nordic curl, heel drops, etc.)
- Stability drills (single-leg balance, BOSU)
- Mobility drills (90/90 hip, thoracic rotations)
- Core anti-rotation (Pallof press, dead bug variations)

**CrossFit Movements** (100 esercizi):

- Olympic lifts + variations (20)
- Gymnastics (muscle-up, HSPU, rope climb) (30)
- Monostructural (row, bike, run, ski) (20)
- Strongman (sled, farmer carry, yoke) (15)
- Accessory (15)

**Prehab/Rehab** (30 esercizi):

- Rotator cuff strengthening (10)
- Scapular stability (8)
- Glute activation (7)
- Foot intrinsic (5)

**Impatto**: Prescrizioni limitate, non personalizzate

### 2.3 Fine-Tuning - MEDIO ⚠️

**Attuale**: Solo prompt engineering
**Target**: Fine-tuned model su dominio medical/CrossFit
**Gap**: Nessun training specifico

**Problemi**:

- Agent "improvvisa" risposte basandosi solo su prompt
- Nessuna specializzazione su casi reali
- Qualità inconsistente tra diverse injury types
- Nessun apprendimento da errori

**Impatto**: Accuracy 70-80% invece di 92%+

### 2.4 Evaluation - CRITICO ❌

**Attuale**: Nessun sistema di valutazione
**Target**: Benchmark suite + metriche
**Gap**: 100%

**Mancano**:

- Test set (50-100 casi)
- Metriche qualità (safety, accuracy, completeness)
- Benchmark scores
- A/B testing framework
- Human evaluation

**Impatto**: Non sappiamo se agent funziona bene

### 2.5 Continuous Learning - BASSO ⚠️

**Attuale**: Agent statico
**Target**: Learning loop con feedback
**Gap**: Nessun meccanismo di miglioramento

**Mancano**:

- Feedback collection
- Active learning
- Retraining pipeline
- Performance monitoring

**Impatto**: Agent non migliora nel tempo

### 2.6 Summary Gap Prioritization

| Gap                 | Priorità | Effort  | Impact | Timeline    |
| ------------------- | -------- | ------- | ------ | ----------- |
| Knowledge Base      | 🔴 ALTA  | 2 weeks | ALTO   | Week 1-2    |
| Exercise Library    | 🔴 ALTA  | 1 week  | ALTO   | Week 3      |
| Fine-Tuning         | 🟡 MEDIA | 2 weeks | MEDIO  | Week 4-5    |
| Evaluation          | 🔴 ALTA  | 1 week  | ALTO   | Week 6      |
| Continuous Learning | 🟢 BASSA | Ongoing | MEDIO  | Post-launch |

---

## 3. STRATEGIA TRAINING

### 3.1 Approccio Multi-Layer

```
Layer 1: KNOWLEDGE BASE (Foundation)
   ↓
Layer 2: EXERCISE LIBRARY (Tools)
   ↓
Layer 3: PROMPT ENGINEERING (Behavior)
   ↓
Layer 4: FINE-TUNING (Specialization)
   ↓
Layer 5: EVALUATION (Quality)
   ↓
Layer 6: CONTINUOUS LEARNING (Improvement)
```

### 3.2 Principi Guida

1. **Safety First** - Red flags detection è priorità #1
2. **Evidence-Based** - Ogni raccomandazione basata su ricerca
3. **Personalization** - Adatta a injury type, fase, dolore
4. **Education** - Spiega sempre il "perché"
5. **Measurable** - Metriche chiare per valutare successo

### 3.3 Success Criteria

| Metrica           | Baseline | Target | Critical |
| ----------------- | -------- | ------ | -------- |
| Safety Score      | N/A      | >95%   | YES      |
| Accuracy          | ~70%     | >90%   | YES      |
| Completeness      | ~60%     | >85%   | NO       |
| User Satisfaction | N/A      | >4.5/5 | NO       |
| Response Time     | ~3s      | <2s    | NO       |

---

## 4. FASE 1: KNOWLEDGE BASE EXPANSION

**Timeline**: Week 1-2 (10-14 giorni)
**Effort**: 80-100 ore
**Priority**: 🔴 CRITICA

### 4.1 Obiettivo

Espandere knowledge base da **2 a 20+ documenti** (1,100 → 10,000+ righe)

### 4.2 Documento Template

```markdown
# [INJURY NAME] - Complete Medical Guide

## 1. Anatomy & Pathophysiology

### Anatomia Coinvolta

[Strutture anatomiche, innervazione, vascolarizzazione]

### Meccanismo Infortunio

[Come avviene, fattori di rischio, biomeccanica]

### Pathophysiology

[Processo infiammatorio, tissue damage, healing cascade]

## 2. Clinical Presentation

### Sintomi Tipici

- Dolore: [localizzazione, caratteristiche, timing]
- Funzionalità: [limitazioni, compensi]
- Segni: [gonfiore, rossore, calore]

### Physical Exam

- Inspection
- Palpation
- Range of Motion
- Strength testing
- Special tests

## 3. Diagnosis

### Differential Diagnosis

[Altre condizioni da escludere]

### Imaging

- X-ray: [quando, cosa mostra]
- MRI: [indicazioni, findings]
- Ultrasound: [utilità]

### Grading/Classification

[Sistema di classificazione severità]

## 4. Treatment Phases

### Phase 1: Acute (0-2 weeks)

**Goals**:

- Ridurre infiammazione
- Proteggere tessuto
- Mantenere ROM pain-free

**Exercises**:

1. [Exercise 1] - Sets/reps, coaching cues
2. [Exercise 2]
3. [Exercise 3]

**Contraindications**:

- ❌ [Movement 1]
- ❌ [Movement 2]

**Expected Progress**:

- Dolore: 7-8/10 → 4-5/10
- Funzione: 40% → 60%

### Phase 2: Subacute (2-6 weeks)

[Simile struttura]

### Phase 3: Strengthening (6-12 weeks)

[Simile struttura]

### Phase 4: Return-to-Sport (12-16 weeks)

[Simile struttura]

## 5. CrossFit Movement Modifications

### Squat Variations

- **Controindicato**: [Quando e perché]
- **Modifiche**: [Box squat, ROM limitato, etc.]
- **Progressione**: [Step by step]

### Deadlift Variations

[Simile]

### Olympic Lifts

[Simile]

### Gymnastics

[Simile]

### Conditioning

[Simile]

## 6. Red Flags

🚨 **EMERGENCY** (Immediate medical attention):

- [Red flag 1]
- [Red flag 2]

⚠️ **WARNING** (Medical consultation within 24-48h):

- [Warning sign 1]
- [Warning sign 2]

## 7. Evidence-Based Protocols

### Research Summary

- [Study 1]: [Key findings]
- [Study 2]: [Key findings]

### Clinical Guidelines

- [Guideline 1]
- [Guideline 2]

### Success Rates

- Conservative treatment: [%]
- Surgical intervention: [%]
- Recurrence rate: [%]

## 8. Case Studies

### Case 1: [Athlete Type]

**Presentation**: [Sintomi iniziali]
**Treatment**: [Approccio usato]
**Outcome**: [Risultato, timeline]
**Lessons**: [Cosa abbiamo imparato]

### Case 2: [Different scenario]

[Simile]

## 9. Prevention

### Risk Factors

- Modificabili: [Lista]
- Non modificabili: [Lista]

### Prevention Strategies

1. [Strategy 1]
2. [Strategy 2]

### Screening Tools

- [Test 1]
- [Test 2]

## 10. References

1. [Citation 1]
2. [Citation 2]
   ...
```

### 4.3 Priority Documents (Week 1)

#### **Day 1-2: Pubalgia** (⚠️ PRIORITÀ MASSIMA)

```bash
File: data/knowledge_base/medical/pubalgia_complete_guide.md
Target: 800-1000 righe
```

**Sezioni Chiave**:

- Anatomia: sinfisi pubica, adduttori, retto addominale
- Meccanismo: overuse, muscle imbalance, core weakness
- Fasi: Acute → Subacute → Strengthening → RTS
- Esercizi: Copenhagen plank, Pallof press, dead bug
- CrossFit mods: Box squat, no running, no jumping
- Timeline: 8-12 settimane

#### **Day 3-4: Shoulder Impingement**

```bash
File: data/knowledge_base/medical/shoulder_impingement_guide.md
Target: 700-900 righe
```

**Focus**:

- Subacromial space, rotator cuff, scapular dyskinesis
- CrossFit: Strict press OK, kipping NO, HSPU modifications

#### **Day 5-6: Patellar Tendinitis**

```bash
File: data/knowledge_base/medical/patellar_tendinitis_guide.md
Target: 700-900 righe
```

**Focus**:

- Jumper's knee, eccentric loading protocol
- CrossFit: Box jumps NO, step-ups OK, squat depth management

#### **Day 7: Review & Ingest**

```bash
# Ingest documenti in RAG
python scripts/populate_rag.py --category medical

# Test retrieval
python scripts/test_rag_quality.py
```

### 4.4 Remaining Documents (Week 2)

**Day 8-14**: Completare rimanenti 17 documenti

- 2 documenti/giorno
- Focus su qualità > quantità
- Peer review tra documenti

### 4.5 Quality Checklist

Ogni documento DEVE avere:

- ☑️ Anatomia dettagliata
- ☑️ 4 fasi treatment con esercizi specifici
- ☑️ CrossFit modifications per 5+ movimenti
- ☑️ Red flags chiari
- ☑️ 3+ case studies
- ☑️ 10+ references scientifiche
- ☑️ Timeline realistiche

### 4.6 Tools per Creazione

````python
# Script helper per generare template
python scripts/generate_kb_template.py \
  --injury_type "pubalgia" \
  --output data/knowledge_base/medical/pubalgia_template.md

# Validatore completezza
python scripts/validate_kb_document.py \
  --file data/knowledge_base/medical/pubalgia_complete_guide.md

# Output:
# ✅ Anatomy section: COMPLETE
# ✅ Treatment phases: 4/4 COMPLETE
---

## 5. FASE 2: EXERCISE LIBRARY EXPANSION

**Timeline**: Week 3 (5-7 giorni)
**Effort**: 40-50 ore
**Priority**: CRITICA

### 5.1 Obiettivo

Espandere exercise library da **20 a 200+ esercizi**

### 5.2 Exercise JSON Schema

```json
{
  "id": "copenhagen_plank",
  "name": "Copenhagen Plank",
  "category": "therapeutic",
  "subcategory": "adductor_strengthening",
  "movement_pattern": "isometric_hold",
  "target_muscles": ["adductors", "core", "hip_abductors"],
  "equipment": ["bench"],
  "difficulty": "intermediate",
  "phases": ["Fase 1", "Fase 2"],

  "injury_specific": {
    "pubalgia": {
      "therapeutic_value": "very_high",
      "progression": ["knee_supported", "straight_leg", "weighted"],
      "dosage": "3x15-20 sec holds",
      "notes": "Gold standard per rinforzo adduttori"
    },
    "sciatica": {
      "therapeutic_value": "low",
      "notes": "Neutro per sciatica"
    }
  },

  "contraindications": ["acute_groin_pain", "hernia"],
  "progressions": ["copenhagen_raises", "weighted_copenhagen"],
  "regressions": ["side_lying_leg_lift", "adductor_squeeze"],

  "coaching_cues": [
    "Corpo in linea retta",
    "Gamba superiore tesa",
    "Core attivo"
  ],

  "video_url": "https://youtube.com/...",
  "sets_range": [2, 4],
  "reps_range": ["15-30 sec hold"],
  "rest_seconds": 60,

  "modifications": {
    "pain_7-10": "Knee supported, 10 sec",
    "pain_5-7": "Straight leg, 15 sec",
    "pain_<5": "Full progression, 20-30 sec"
  },

  "evidence": {
    "research_support": "high",
    "citations": ["Ishøi et al. 2016"]
  }
}
````

### 5.3 Breakdown per Categoria

**Therapeutic (50 esercizi)**:

- Isometric holds: 15
- Eccentric loading: 12
- Stability drills: 10
- Mobility: 8
- Core anti-rotation: 5

**CrossFit (100 esercizi)**:

- Olympic lifts: 20
- Gymnastics: 30
- Monostructural: 20
- Strongman: 15
- Accessory: 15

**Prehab/Rehab (30 esercizi)**:

- Rotator cuff: 10
- Scapular: 8
- Glute: 7
- Foot: 5

**Stretching/Mobility (20 esercizi)**:

- Dynamic: 10
- Static: 10

### 5.4 Implementation

```bash
# Day 1-2: Therapeutic exercises
python scripts/generate_exercises.py \
  --category therapeutic \
  --count 50 \
  --output data/exercises_therapeutic.json

# Day 3-5: CrossFit movements
python scripts/generate_exercises.py \
  --category crossfit \
  --count 100 \
  --output data/exercises_crossfit.json

# Day 6: Prehab + Mobility
python scripts/generate_exercises.py \
  --categories prehab,mobility \
  --count 50 \
  --output data/exercises_prehab_mobility.json

# Day 7: Merge + Validate + Import
python scripts/merge_exercise_libraries.py
python scripts/validate_exercises.py
python scripts/import_exercises_to_db.py
```

---

## 6. FASE 3: FINE-TUNING

**Timeline**: Week 4-5 (10-14 giorni)
**Effort**: 60-80 ore
**Priority**: MEDIA

### 6.1 Approccio 1: Prompt Engineering Avanzato (RACCOMANDATO)

**Pro**: Veloce, no training costs, iterabile
**Contro**: Limitato da capacità base model

#### **Enhanced System Prompt**

```python
ENHANCED_PROMPT = """
Sei un ELITE Sports Medicine Physician & CrossFit L3 Trainer.

CREDENTIALS:
- MD Sports Medicine (Johns Hopkins)
- CSCS (Certified Strength & Conditioning Specialist)
- CrossFit Level 3 Trainer
- SFMA (Selective Functional Movement Assessment)
- 15 anni esperienza, 500+ atleti, 92% success rate

DECISION FRAMEWORK:
1. ASSESS: History + current status
2. DIAGNOSE: Injury type, severity, stage
3. EDUCATE: Anatomy, mechanism, prognosis
4. PRESCRIBE: Evidence-based treatment
5. MONITOR: Track progress, adjust
6. PREVENT: Address root causes

SAFETY PROTOCOLS:
- ALWAYS screen red flags first
- When doubt, refer to specialist
- Never minimize pain
- Respect tissue healing timelines

TOOLS:
- pain_analyzer: Trend analysis
- red_flags_detector: Emergency screening
- progression_calculator: Readiness check
- exercise_validator: Safety validation

USE TOOLS PROACTIVELY before recommendations.
"""
```

#### **Few-Shot Examples** (10-20 esempi)

```python
EXAMPLES = [
    {
        "user": "Dolore inguine 3 settimane, peggiora con squat",
        "assistant": """[Risposta expert-validated completa]"""
    },
    # ... 19 altri esempi
]
```

#### **Chain-of-Thought Prompting**

```python
COT = """
Prima di rispondere:
1. INFO GATHERING: Cosa ho? Cosa manca?
2. PATTERN RECOGNITION: Quali sintomi? Injury pattern?
3. KNOWLEDGE RETRIEVAL: RAG docs? Esercizi? Evidenze?
4. REASONING: Fase? Esercizi sicuri? Progressione?
5. RESPONSE: Spiegazione + Piano + Educazione
"""
```

### 6.2 Approccio 2: Fine-Tuning OpenAI (AVANZATO)

**Pro**: Specializzazione massima
**Contro**: Costo ($500-1000), tempo, complessità

#### **Dataset Creation**

**Fonti** (Target: 500+ esempi):

1. Casi clinici reali (100)
2. Conversazioni simulate (200)
3. Q&A da forum (200)
4. Expert annotations (50+)

**Formato**:

```json
{
  "messages": [
    { "role": "system", "content": "[SYSTEM_PROMPT]" },
    { "role": "user", "content": "[USER_QUESTION]" },
    { "role": "assistant", "content": "[IDEAL_RESPONSE]" }
  ]
}
```

#### **Training Process**

````bash
# 1. Prepare dataset
python scripts/prepare_training_data.py \
  --sources clinical,simulated,forum \
  --output training_data.jsonl \
  --min_quality 8.0

# 2. Upload to OpenAI
openai api fine_tunes.create \
  -t training_data.jsonl \
  -m gpt-4o-mini \
  --suffix "medical-crossfit-v1"

# 3. Monitor
openai api fine_tunes.follow -i ft-xxx

# 4. Update llm_service.py
---

## 8. FASE 5: CONTINUOUS LEARNING

**Timeline**: Ongoing (post-launch)
**Priority**: 🟢 BASSA (ma importante long-term)

### 8.1 Feedback Loop

```python
class FeedbackSystem:
    def collect_feedback(self, session_id):
        return {
            "rating": 1-5,
            "helpful": True/False,
            "comments": "...",
            "followed_advice": True/False,
            "outcome": "improved/same/worse"
        }
````

### 8.2 Active Learning

```python
# Identificare casi difficili
difficult_cases = db.query("""
    SELECT * FROM chat_history
    WHERE user_rating < 3 OR agent_confidence < 0.7
""")

# Expert annotation
for case in difficult_cases:
    expert_response = get_expert_annotation(case)
    training_data.append(case)

# Retrain periodicamente
if len(training_data) > 100:
    retrain_model(training_data)
```

### 8.3 A/B Testing

```python
class ABTest:
    def __init__(self):
        self.variant_a = MedicalCoachAgent(prompt=PROMPT_V1)
        self.variant_b = MedicalCoachAgent(prompt=PROMPT_V2)

    def compare_results(self):
        # Dopo 100+ interazioni
        return winner  # variant con avg_rating più alto
```

---

## 9. IMPLEMENTAZIONE PRATICA

### 9.1 Roadmap 6 Settimane

#### **Week 1: Knowledge Base (Part 1)**

- ☐ Day 1-2: Pubalgia document (⚠️ PRIORITÀ)
- ☐ Day 3-4: Shoulder injuries
- ☐ Day 5-6: Knee injuries
- ☐ Day 7: Ingest + test RAG

#### **Week 2: Knowledge Base (Part 2)**

- ☐ Day 8-9: Hip + Ankle injuries
- ☐ Day 10-11: Elbow + Spine injuries
- ☐ Day 12-13: Muscle strains + Overuse
- ☐ Day 14: CrossFit + Physio docs

#### **Week 3: Exercise Library**

- ☐ Day 15-16: Therapeutic exercises (50)
- ☐ Day 17-19: CrossFit movements (100)
- ☐ Day 20: Prehab + Mobility (50)
- ☐ Day 21: Merge + Validate + Import

#### **Week 4: Prompt Engineering**

- ☐ Day 22-23: Enhanced system prompt
- ☐ Day 24-25: Few-shot examples (20)
- ☐ Day 26-27: Chain-of-thought integration
- ☐ Day 28: Testing + iteration

#### **Week 5: Fine-Tuning (Optional)**

- ☐ Day 29-30: Dataset creation (500+ examples)
- ☐ Day 31-32: Training preparation
- ☐ Day 33-34: Fine-tuning execution
- ☐ Day 35: Model deployment

#### **Week 6: Evaluation**

- ☐ Day 36-37: Test set creation (100 cases)
- ☐ Day 38-39: Automated benchmark
- ☐ Day 40-41: Human evaluation
- ☐ Day 42: Final report + launch

### 9.2 Team Requirements

**Core Team**:

- **1x Sports Medicine Physician** (20h/week) - Content creation, validation
- **1x CrossFit L3 Trainer** (15h/week) - Exercise library, programming
- **1x Physiotherapist** (15h/week) - Rehab protocols, assessment
- **1x ML Engineer** (40h/week) - Implementation, fine-tuning, evaluation

**Optional**:

- **1x Technical Writer** (10h/week) - Documentation
- **1x QA Tester** (10h/week) - Testing, bug reporting

### 9.3 Budget Estimate

| Item               | Cost               | Notes         |
| ------------------ | ------------------ | ------------- |
| Expert Consultants | $5,000             | 50h @ $100/h  |
| ML Engineer        | $8,000             | 240h @ $33/h  |
| OpenAI Fine-tuning | $500-1000          | If needed     |
| Compute (GPU)      | $200               | Cloud credits |
| Tools/Software     | $100               | Misc          |
| **TOTAL**          | **$13,800-14,300** | 6 weeks       |

### 9.4 Success Metrics

| Metric            | Baseline | Target | Achieved |
| ----------------- | -------- | ------ | -------- |
| Knowledge Docs    | 2        | 20+    | ☐        |
| Exercise Library  | 20       | 200+   | ☐        |
| Safety Score      | N/A      | >95%   | ☐        |
| Accuracy Score    | ~70%     | >90%   | ☐        |
| User Satisfaction | N/A      | >4.5/5 | ☐        |
| Response Time     | ~3s      | <2s    | ☐        |

---

## 10. METRICHE DI SUCCESSO

### 10.1 Technical Metrics

**Safety** (⚠️ CRITICAL):

- ✅ Red flags detection: 100%
- ✅ Contraindications respected: 100%
- ✅ Appropriate referrals: >95%

**Accuracy**:

- ✅ Injury identification: >90%
- ✅ Phase assessment: >85%
- ✅ Exercise prescription: >90%

**Completeness**:

- ✅ Assessment questions: >80%
- ✅ Treatment plan detail: >85%
- ✅ Education provided: >80%

### 10.2 User Metrics

**Satisfaction**:

- ✅ Overall rating: >4.5/5
- ✅ Would recommend: >90%
- ✅ Followed advice: >80%

**Engagement**:

- ✅ Messages per session: >5
- ✅ Return rate: >70%
- ✅ Completion rate: >85%

### 10.3 Business Metrics

**Outcomes**:

- ✅ Pain reduction: >50% in 4 weeks
- ✅ Function improvement: >40% in 8 weeks
- ✅ Return to sport: >80% in 12-16 weeks

**Efficiency**:

- ✅ Response time: <2s
- ✅ Cost per interaction: <$0.10
- ✅ Uptime: >99.5%

---

## 🎯 CONCLUSIONI

### Priorità Immediate (Week 1-2)

1. 🔴 **Pubalgia document** - MASSIMA PRIORITÀ
2. 🔴 **Shoulder + Knee docs** - Alta priorità
3. 🟡 **Ingest in RAG** - Abilitare retrieval

### Quick Wins

- ⚡ Enhanced system prompt (2 giorni)
- ⚡ Few-shot examples (3 giorni)
- ⚡ Therapeutic exercises (3 giorni)

### Long-term Investment

- 📈 Fine-tuning (se necessario)
- 📈 Continuous learning loop
- 📈 A/B testing framework

### Success Criteria

- ✅ Safety score >95% (NON NEGOZIABILE)
- ✅ Accuracy >90%
- ✅ User satisfaction >4.5/5
- ✅ 200+ exercises
- ✅ 20+ knowledge docs

### Next Steps

1. ☑️ Review questo documento con team
2. ☐ Assign roles e responsabilità
3. ☐ Setup development environment
4. ☐ Start Week 1: Pubalgia document
5. ☐ Daily standups per tracking progress

---

**DOCUMENTO COMPLETO** ✅
**PRONTO PER IMPLEMENTAZIONE** 🚀
