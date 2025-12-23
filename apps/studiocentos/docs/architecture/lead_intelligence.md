# ML Lead Intelligence - Free Embeddings API Analysis (Nov 2025)

## 🎯 Objective
Implementare Lead Intelligence con embeddings gratuiti via API, riusando l'infrastruttura AI esistente del customer service.

---

## 📊 Comparison: Free Embeddings APIs

### ✅ **Google Gemini** (RACCOMANDATO)
**Model**: `text-embedding-004` / `gemini-embedding-001`

**Free Tier**:
- ✅ **1,500 requests/minute** (RPM)
- ✅ **Completamente GRATIS** via Google AI Studio
- ✅ **$0.15 per 1M tokens** se superi il free tier (molto economico)
- ✅ Reset automatico ogni 24h

**Pro**:
- Molto generoso (1500 req/min vs 50/day di altri)
- Embeddings di alta qualità (768 dimensioni)
- Supporto multilingue eccellente
- Nessun costo per File Search Tool

**Contro**:
- Google può usare i dati del free tier per migliorare prodotti

**API Key**: Gratis da [Google AI Studio](https://aistudio.google.com/app/apikey)

---

### ⚠️ **OpenRouter** (FALLBACK)
**Models**: `text-embedding-ada-002`, `text-embedding-3-large`, `gte-large`

**Free Tier**:
- ⚠️ Solo **50 requests/day** (ridotto da 200 ad aprile 2025)
- ✅ 20 requests/minute
- ✅ Modelli multipli disponibili

**Pro**:
- Supporta molti provider (fallback automatico)
- OpenAI embeddings compatibili

**Contro**:
- Limite giornaliero molto basso (50 req/day)
- Richiede $10 balance per 1000 req/day

**API Key**: Gratis da [OpenRouter](https://openrouter.ai/)

---

### ❌ **Hugging Face** (NON RACCOMANDATO)
**Free Tier**:
- ❌ Solo **$0.10/month** di crediti gratis
- ❌ Limite molto ridotto (si esaurisce rapidamente)

**Contro**:
- Crediti insufficienti per uso reale
- Pro account costa $9/mese per $2 crediti

---

### ❌ **Groq** (NO EMBEDDINGS)
**Status**:
- ❌ **Non supporta embeddings models** (confermato forum Aug 2025)
- ✅ Solo LLM inference (molto veloce ma non utile per embeddings)

---

## 🏗️ Architettura Proposta

### Sistema Esistente (Customer Service)
```python
# apps/backend/app/core/config.py
OPENAI_API_KEY: str = Field(default="")
GOOGLE_AI_API_KEY: str = Field(default="")
HUGGINGFACE_API_KEY: str = Field(default="")
```

### Nuovo Sistema (Lead Intelligence)
```
┌─────────────────────────────────────────────┐
│ Customer CRM Data (PostgreSQL)              │
│ - industry, location, size, lifetime_value  │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ Embedding Service (Google Gemini API)       │
│ - text-embedding-004 (768 dim)              │
│ - 1500 req/min free                         │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ Vector Database (ChromaDB)                  │
│ - In-memory per dev                         │
│ - Persistent per production                 │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ Lead Search API                             │
│ - Similarity search                         │
│ - Ranked by success patterns               │
│ - Auto-learning from acquisitions          │
└─────────────────────────────────────────────┘
```

---

## 📝 Implementation Plan

### Step 1: Aggiungere Credenziali
```python
# config.py
GOOGLE_AI_API_KEY: str = Field(default="")  # Already exists!
OPENROUTER_API_KEY: str = Field(default="")  # Fallback
```

### Step 2: Creare Embedding Service
```python
# app/services/embeddings.py
class EmbeddingService:
    def __init__(self):
        self.google_api_key = settings.GOOGLE_AI_API_KEY
        self.openrouter_api_key = settings.OPENROUTER_API_KEY
        
    async def get_embedding(self, text: str):
        # Try Google Gemini first (free tier)
        if self.google_api_key:
            return await self._google_embedding(text)
        # Fallback to OpenRouter
        return await self._openrouter_embedding(text)
```

### Step 3: Integrare ChromaDB
```python
# requirements.txt
chromadb==0.4.22

# app/services/vector_store.py
import chromadb

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection("leads")
```

### Step 4: Learning Loop
```python
# Auto-sync customers -> embeddings
@router.post("/customers/")
async def create_customer(customer: CustomerCreate):
    # 1. Save customer
    new_customer = service.create_customer(customer)
    
    # 2. Generate embedding
    embedding = await embeddings.get_embedding(
        f"{customer.industry} {customer.location} {customer.size}"
    )
    
    # 3. Store in vector DB
    vector_store.add(
        id=str(new_customer.id),
        embedding=embedding,
        metadata={"success": True, "ltv": customer.lifetime_value}
    )
```

### Step 5: Intelligent Search
```python
# Lead search with similarity
@router.post("/leads/search")
async def intelligent_lead_search(query: LeadSearchRequest):
    # 1. Generate query embedding
    query_text = f"{query.industry} {query.location} {query.size}"
    query_embedding = await embeddings.get_embedding(query_text)
    
    # 2. Find similar successful customers
    similar = vector_store.query(
        query_embedding,
        n_results=10,
        where={"success": True}
    )
    
    # 3. Generate leads matching pattern
    leads = await generate_leads_like(similar)
    return leads
```

---

## 💰 Cost Analysis

### Scenario: 1000 lead searches/month

**Google Gemini** (FREE):
- 1000 searches × 2 embeddings/search = 2000 req/month
- 2000 req ÷ 30 days = 66 req/day
- **Costo: $0** (ben sotto 1500 req/min)

**OpenRouter** (NON SUFFICIENTE):
- Limite: 50 req/day × 30 = 1500 req/month
- **Non sufficiente** per 2000 req/month

**Conclusione**: **Google Gemini è l'unica opzione gratuita viabile**

---

## 🎯 Raccomandazione Finale

1. **Primary**: **Google Gemini** (`text-embedding-004`)
   - Free tier generoso (1500 RPM)
   - Qualità eccellente
   - Già configurabile in [config.py](file:///home/autcir_gmail_com/studiocentos_ws/apps/backend/app/core/config.py)

2. **Fallback**: **OpenRouter** (solo se Gemini fallisce)
   - Per emergenze
   - Limite basso ma utile come backup

3. **Vector DB**: **ChromaDB**
   - Gratis, open source
   - Facile integrazione
   - Persistent storage

---

## 🚀 Next Steps

1. ✅ Verificare che `GOOGLE_AI_API_KEY` sia già in [config.py](file:///home/autcir_gmail_com/studiocentos_ws/apps/backend/app/core/config.py)
2. 🔄 Creare `EmbeddingService` riusando pattern di customer service
3. 🔄 Integrare ChromaDB
4. 🔄 Implementare learning loop
5. 🔄 Sostituire lead search simulato
