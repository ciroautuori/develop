# 🔍 ToolAI Discovery System - Analisi e Miglioramenti

**Data Analisi:** 3 Dicembre 2025
**Problema Segnalato:** DeepSeek-V3 e altri tool importanti non vengono scoperti
**Autore:** Sistema di Analisi

---

## 🚨 PROBLEMA IDENTIFICATO

### Caso Specifico: DeepSeek-V3 / DeepSeek-R1

**DeepSeek-R1** è attualmente **#1 su HuggingFace** con:
- ❤️ **12,889 likes**
- 📥 **1,208,477 downloads**
- 🗓️ Rilasciato recentemente

**Il nostro sistema NON lo ha rilevato** perché:
1. ❌ Non cerca nei modelli TRENDING (ordinati per likes/downloads)
2. ❌ Cerca solo modelli modificati nelle ultime 24h
3. ❌ Prende troppo pochi risultati dai daily papers (10 su 50 disponibili)

---

## 📊 Analisi Fonti Attuali

### 1. HuggingFace Daily Papers ✅ OK (ma limitato)

**API Attuale:**
```python
GET https://huggingface.co/api/daily_papers
Limit: 10 (di 50 disponibili)
```

**Risultati Test (3 Dic 2025):**
```
Totale papers disponibili: 50
Paper presi: 10

Top paper per upvotes:
1. ToolOrchestra - 45 upvotes ✅
2. InnoGym - 28 upvotes ✅
3. PixelDiT - 10 upvotes ✅
4. WUSH - 10 upvotes ✅

Paper persi (11-50): 40 paper NON analizzati
```

**PROBLEMA:** Prendiamo solo i primi 10 in ordine di pubblicazione, non i più votati!

---

### 2. HuggingFace Models ❌ PROBLEMA CRITICO

**API Attuale:**
```python
GET https://huggingface.co/api/models
Params:
  sort: "lastModified"  # ❌ SBAGLIATO!
  direction: -1
  limit: 30
```

**Risultati Test:**
```
Primi 10 modelli per lastModified:
1. qopertouy/blockassist - 0 likes, 0 downloads ❌
2. jopylop/blockassist - 0 likes, 0 downloads ❌
3. exurbiaroom0v/blockassist - 0 likes, 0 downloads ❌
4. rewardfm/ant-rfm-qwen... - 0 likes, 0 downloads ❌
5. vopoikuo/blockassist - 0 likes, 0 downloads ❌
...

TUTTI SPAM/TEST MODELS CON 0 ENGAGEMENT!
```

**API CORRETTA (non usata):**
```python
GET https://huggingface.co/api/models
Params:
  sort: "likes"  # ✅ CORRETTO!
  direction: -1
  limit: 30
```

**Risultati API Corretta:**
```
TOP 10 modelli TRENDING per likes:
1. deepseek-ai/DeepSeek-R1 - ❤️12,889, 📥1.2M ✅✅✅
2. FLUX.1-dev - ❤️11,949, 📥1.3M ✅
3. stable-diffusion-xl - ❤️7,185, 📥2.7M ✅
4. stable-diffusion-v1-4 - ❤️6,940, 📥628K ✅
5. Meta-Llama-3-8B - ❤️6,396, 📥2.1M ✅
6. Kokoro-82M - ❤️5,352, 📥3.8M ✅
7. whisper-large-v3 - ❤️5,160, 📥4.8M ✅
8. Llama-3.1-8B-Instruct - ❤️5,058, 📥5M ✅
9. bloom - ❤️4,961, 📥2,562 ✅
10. stable-diffusion-3 - ❤️4,874, 📥10,755 ✅

TUTTI MODELLI IMPORTANTI CON ALTO ENGAGEMENT!
```

---

### 3. GitHub Trending ⚠️ PARZIALMENTE OK

**API Attuale:**
```python
GET https://api.github.com/search/repositories
Query: "(topic:ml OR topic:dl OR topic:llm OR topic:ai) pushed:>2025-12-02"
Sort: "updated"
Limit: 10
```

**PROBLEMA:**
- Query troppo generica cattura molti repo non rilevanti
- Sort per "updated" invece di "stars"
- Non cerca specifici nomi di tool famosi (DeepSeek, LLama, etc.)

**SOLUZIONE:**
- Aggiungere query specifiche per tool noti
- Sort per stars con filtro temporale
- Aumentare varietà query

---

### 4. ArXiv Papers ✅ OK

API funziona correttamente per paper accademici.

---

## 🎯 FONTI MANCANTI (da aggiungere)

### 1. HuggingFace Spaces 🌟
```python
GET https://huggingface.co/api/spaces
Sort: "likes" o "trending"
```
**Perché:** Molti tool popolari hanno Spaces (demo interattive)
**Esempi:** ChatGPT clones, Stable Diffusion web UI, etc.

### 2. HuggingFace Datasets 📊
```python
GET https://huggingface.co/api/datasets
Sort: "downloads"
```
**Perché:** Dataset innovativi sono tool importanti
**Esempi:** Llama-3 training data, vision benchmarks

### 3. Papers with Code 📄
```python
GET https://paperswithcode.com/api/v1/papers/
Sort: "stars"
```
**Perché:** Implementazioni ufficiali di paper
**Verificare:** Repository associati ai paper

### 4. AI News Aggregators 📰
- **Hugging Face Daily** (già usato)
- **AI News** RSS feeds
- **Reddit r/MachineLearning** top posts
- **Twitter/X** AI influencers

### 5. Model Leaderboards 🏆
```python
# Open LLM Leaderboard
https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard

# MTEB Leaderboard (embeddings)
https://huggingface.co/spaces/mteb/leaderboard
```

---

## 💡 SOLUZIONE PROPOSTA

### Fase 1: FIX IMMEDIATO (1 ora)

#### 1.1 Modificare HuggingFace Models Discovery

**File:** `apps/backend/app/infrastructure/ai/toolai_scraper.py`

```python
async def fetch_huggingface_trending_models(self, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch TRENDING MODELS da HuggingFace - Ordinati per LIKES (popolarità).
    """
    tools = []

    try:
        # ✅ NUOVO: Sort by LIKES invece di lastModified
        response = await self.client.get(
            self.HUGGINGFACE_MODELS,
            params={
                "sort": "likes",  # ✅ CAMBIATO DA lastModified
                "direction": -1,
                "limit": limit * 2,  # Prendiamo più risultati
                "full": "true"
            }
        )

        if response.status_code == 200:
            models = response.json()

            for model in models[:limit]:
                model_id = model.get("modelId", "")
                tags = model.get("tags", [])
                pipeline_tag = model.get("pipeline_tag", "")

                # ✅ NUOVO: Filtra spam models (0 likes e 0 downloads)
                likes = model.get("likes", 0)
                downloads = model.get("downloads", 0)

                if likes == 0 and downloads == 0:
                    continue  # Skip spam

                # Skip models without useful info
                if not model_id:
                    continue

                tools.append({
                    "name": model_id.split("/")[-1] if "/" in model_id else model_id,
                    "source": "huggingface_models",
                    "source_url": f"https://huggingface.co/{model_id}",
                    "description_it": f"🤖 Modello {pipeline_tag}: {model_id}. Downloads: {downloads:,}, Likes: {likes:,}",
                    "description_en": f"🤖 {pipeline_tag} Model: {model_id}. Downloads: {downloads:,}, Likes: {likes:,}",
                    "category": self._categorize_tool(model_id, pipeline_tag, tags),
                    "tags": tags[:5],
                    "downloads": downloads,
                    "stars": likes,
                    "trending_score": likes * 10 + (downloads // 1000),  # ✅ Peso maggiore ai likes
                    "pipeline_tag": pipeline_tag
                })

        logger.info("huggingface_models_complete", count=len(tools))

    except Exception as e:
        logger.error("huggingface_models_error", error=str(e))

    return tools
```

#### 1.2 Aumentare Limit Daily Papers

```python
async def fetch_huggingface_daily_papers(self, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Fetch DAILY PAPERS da HuggingFace - Paper pubblicati OGGI!
    ✅ AUMENTATO: da 10 a 20 per catturare più paper
    """
    tools = []

    try:
        response = await self.client.get(self.HUGGINGFACE_DAILY_PAPERS)

        if response.status_code == 200:
            papers = response.json()

            # ✅ NUOVO: Ordina per upvotes prima di prendere i top
            papers_sorted = sorted(
                papers,
                key=lambda x: x.get("paper", {}).get("upvotes", 0),
                reverse=True
            )

            for paper in papers_sorted[:limit]:  # ✅ Ora prendiamo i top 20 per upvotes
                # ... resto del codice
```

#### 1.3 Migliorare GitHub Search

```python
async def fetch_github_trending_ai(self, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch TRENDING AI repos da GitHub - Con query multiple mirate.
    """
    tools = []

    try:
        # ✅ NUOVO: Multiple query per diversi tipi di tool
        queries = [
            # Query 1: Tool generali AI
            "topic:llm OR topic:large-language-model stars:>100 pushed:>2025-12-01",
            # Query 2: Tool specifici
            "deepseek OR llama OR mistral OR qwen stars:>50 pushed:>2025-12-01",
            # Query 3: AI frameworks
            "topic:transformers OR topic:pytorch-lightning stars:>100 pushed:>2025-11-15",
        ]

        for query in queries:
            response = await self.client.get(
                f"{self.GITHUB_API}/search/repositories",
                params={
                    "q": query,
                    "sort": "stars",  # ✅ CAMBIATO: stars invece di updated
                    "order": "desc",
                    "per_page": limit // len(queries) + 2
                }
            )

            # ... processa risultati
```

---

### Fase 2: NUOVE FONTI (1 settimana)

#### 2.1 Aggiungere HuggingFace Spaces

```python
async def fetch_huggingface_spaces(self, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch TRENDING SPACES da HuggingFace.
    """
    tools = []

    try:
        response = await self.client.get(
            "https://huggingface.co/api/spaces",
            params={
                "sort": "likes",
                "direction": -1,
                "limit": limit * 2
            }
        )

        if response.status_code == 200:
            spaces = response.json()

            for space in spaces[:limit]:
                space_id = space.get("id", "")
                likes = space.get("likes", 0)

                if likes < 10:  # Filtra spaces poco popolari
                    continue

                tools.append({
                    "name": space_id.split("/")[-1],
                    "source": "huggingface_spaces",
                    "source_url": f"https://huggingface.co/spaces/{space_id}",
                    "description_it": f"🎨 Space interattivo: {space.get('cardData', {}).get('title', space_id)}",
                    "category": self._categorize_tool(space_id, "", []),
                    "stars": likes,
                    "trending_score": likes * 5  # Spaces hanno meno likes, peso maggiore
                })

        logger.info("huggingface_spaces_complete", count=len(tools))

    except Exception as e:
        logger.error("huggingface_spaces_error", error=str(e))

    return tools
```

#### 2.2 Aggiungere Papers with Code

```python
async def fetch_papers_with_code(self, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch paper con implementazione da Papers with Code.
    """
    tools = []

    try:
        response = await self.client.get(
            "https://paperswithcode.com/api/v1/papers/",
            params={
                "ordering": "-stars",
                "page_size": limit
            }
        )

        if response.status_code == 200:
            papers = response.json().get("results", [])

            for paper in papers:
                repo_url = paper.get("official", {}).get("url", "")
                if not repo_url:
                    continue

                tools.append({
                    "name": paper.get("title", "")[:100],
                    "source": "papers_with_code",
                    "source_url": repo_url,
                    "description_it": f"📄 Paper + Codice: {paper.get('abstract', '')[:200]}",
                    "category": "llm",  # Categorizzazione da migliorare
                    "stars": paper.get("stars", 0),
                    "trending_score": paper.get("stars", 0)
                })

        logger.info("papers_with_code_complete", count=len(tools))

    except Exception as e:
        logger.error("papers_with_code_error", error=str(e))

    return tools
```

#### 2.3 Modificare `discover_tools()` per includere nuove fonti

```python
async def discover_tools(
    self,
    num_tools: int = 5,
    categories: Optional[List[str]] = None,
    sources: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Scopri tool AI REALI da multiple fonti con TIMESTAMP.

    Fonti disponibili:
    - huggingface_papers: Daily Papers (ordinate per upvotes)
    - huggingface_models: Trending Models (ordinate per likes) ✅ MIGLIORATO
    - huggingface_spaces: Trending Spaces (nuova demo) ✅ NUOVO
    - github: Trending AI Repos (query multiple) ✅ MIGLIORATO
    - arxiv: Latest Papers
    - papers_with_code: Paper con codice ✅ NUOVO
    """
    sources = sources or [
        "huggingface_models",  # Priorità 1: Modelli trending
        "huggingface_papers",  # Priorità 2: Paper del giorno
        "github",              # Priorità 3: GitHub repos
        "huggingface_spaces",  # Priorità 4: Spaces (se implementato)
        "arxiv"                # Priorità 5: Paper accademici
    ]

    all_tools = []

    async with self:
        tasks = []

        if "huggingface_models" in sources:
            tasks.append(self.fetch_huggingface_trending_models(num_tools * 2))  # ✅ Più risultati

        if "huggingface_papers" in sources:
            tasks.append(self.fetch_huggingface_daily_papers(20))  # ✅ Aumentato

        if "huggingface_spaces" in sources:
            tasks.append(self.fetch_huggingface_spaces(num_tools))  # ✅ NUOVO

        if "github" in sources:
            tasks.append(self.fetch_github_trending_ai(num_tools))

        if "arxiv" in sources:
            tasks.append(self.fetch_arxiv_latest(num_tools // 2))

        if "papers_with_code" in sources:
            tasks.append(self.fetch_papers_with_code(5))  # ✅ NUOVO

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_tools.extend(result)

    # ✅ MIGLIORATO: Scoring algorithm
    for tool in all_tools:
        # Calcola score composito
        likes = tool.get("stars", 0)
        downloads = tool.get("downloads", 0)
        upvotes = tool.get("upvotes", 0)

        # Peso diverso per fonte
        source_weight = {
            "huggingface_models": 2.0,  # Modelli hanno priorità alta
            "huggingface_papers": 1.5,  # Paper importanti
            "huggingface_spaces": 1.2,  # Spaces demo
            "github": 1.0,              # GitHub repo
            "arxiv": 0.8,               # Paper accademici
            "papers_with_code": 1.3     # Paper + codice
        }

        weight = source_weight.get(tool.get("source", ""), 1.0)

        tool["trending_score"] = int(
            (likes * 10 + upvotes * 5 + downloads // 1000) * weight
        )

    # Sort by trending score
    all_tools.sort(key=lambda x: x.get("trending_score", 0), reverse=True)

    # Deduplica
    seen_names = set()
    unique_tools = []
    for tool in all_tools:
        name_key = tool.get("name", "").lower()[:50]
        if name_key and name_key not in seen_names:
            seen_names.add(name_key)
            unique_tools.append(tool)

    return unique_tools[:num_tools]
```

---

### Fase 3: INTELLIGENZA AVANZATA (2 settimane)

#### 3.1 Named Entity Recognition per Tool Famosi

```python
FAMOUS_TOOLS = {
    "deepseek": ["deepseek-ai", "DeepSeek"],
    "llama": ["meta-llama", "Llama-3", "Llama-2"],
    "mistral": ["mistralai", "Mistral-7B"],
    "qwen": ["Qwen", "Qwen2"],
    "stable-diffusion": ["stabilityai", "stable-diffusion"],
    "whisper": ["openai/whisper"],
    "flux": ["black-forest-labs/FLUX"],
}

async def fetch_specific_tools(self) -> List[Dict[str, Any]]:
    """
    Cerca specificamente tool famosi per assicurarsi che non vengano persi.
    """
    tools = []

    for tool_name, identifiers in FAMOUS_TOOLS.items():
        for identifier in identifiers:
            # Cerca su HuggingFace
            response = await self.client.get(
                f"https://huggingface.co/api/models/{identifier}"
            )
            if response.status_code == 200:
                model = response.json()
                # Aggiungi ai risultati con high priority
                tools.append(self._format_model(model, priority=True))

    return tools
```

#### 3.2 Monitoring e Alerting

```python
async def check_missed_important_tools(self, discovered_tools: List[Dict]) -> List[str]:
    """
    Controlla se abbiamo perso tool importanti confrontando con leaderboard.
    """
    # Fetch top 20 da HuggingFace likes
    top_models = await self.fetch_top_models_by_likes(20)

    discovered_names = {t.get("name", "").lower() for t in discovered_tools}
    missed = []

    for model in top_models:
        if model.get("name", "").lower() not in discovered_names:
            missed.append(model.get("name"))

    if missed:
        logger.warning("missed_important_tools", tools=missed)

    return missed
```

---

## 📈 METRICHE DI SUCCESSO

### Before (Attuale)
- ❌ DeepSeek-R1 (12K likes) - NON rilevato
- ❌ FLUX.1-dev (11K likes) - NON rilevato
- ❌ Stable Diffusion XL (7K likes) - NON rilevato
- ✅ Solo paper del giorno (limitati a 10)
- ✅ Modelli spam con 0 engagement

**Coverage:** ~20% dei top tool

### After (Proposto)
- ✅ Top 10 HuggingFace models per likes
- ✅ Top 20 Daily Papers per upvotes
- ✅ Trending Spaces
- ✅ GitHub repos per stars
- ✅ Papers with Code

**Coverage Atteso:** ~80-90% dei top tool

---

## 🚀 IMPLEMENTAZIONE

### Priority 1 - FIX IMMEDIATO (Deploy oggi)
1. ✅ Cambiare sort HF models: `lastModified` → `likes`
2. ✅ Aumentare limit daily papers: 10 → 20
3. ✅ Ordinare papers per upvotes
4. ✅ Filtrare spam models (0 likes + 0 downloads)
5. ✅ Migliorare scoring algorithm

**Tempo stimato:** 1-2 ore
**Impatto:** Immediato - DeepSeek-R1 verrà rilevato domani

### Priority 2 - NUOVE FONTI (Deploy settimana prossima)
1. ⏳ Implementare HuggingFace Spaces
2. ⏳ Implementare Papers with Code
3. ⏳ Migliorare GitHub query (multiple searches)
4. ⏳ Aggiungere source weights al scoring

**Tempo stimato:** 1 settimana
**Impatto:** +40% coverage

### Priority 3 - INTELLIGENZA (Deploy entro 2 settimane)
1. ⏳ Named Entity Recognition tool famosi
2. ⏳ Monitoring missed tools
3. ⏳ Alert system
4. ⏳ Dashboard analytics

**Tempo stimato:** 2 settimane
**Impatto:** Coverage 90%+

---

## 📋 CHECKLIST IMPLEMENTAZIONE

### Fase 1 - Fix Immediato
- [ ] Modificare `fetch_huggingface_trending_models()` con sort="likes"
- [ ] Aggiungere filtro spam models (0 engagement)
- [ ] Aumentare `fetch_huggingface_daily_papers()` limit a 20
- [ ] Ordinare papers per upvotes
- [ ] Aggiornare scoring algorithm con source weights
- [ ] Test manuale con API HuggingFace
- [ ] Deploy su production
- [ ] Verificare post ToolAI domani (4 Dicembre)

### Fase 2 - Nuove Fonti
- [ ] Implementare `fetch_huggingface_spaces()`
- [ ] Implementare `fetch_papers_with_code()`
- [ ] Aggiungere multiple query GitHub
- [ ] Integrare in `discover_tools()`
- [ ] Unit tests per nuove funzioni
- [ ] Integration test completo
- [ ] Deploy su production

### Fase 3 - Intelligenza
- [ ] Creare dizionario FAMOUS_TOOLS
- [ ] Implementare `fetch_specific_tools()`
- [ ] Implementare `check_missed_important_tools()`
- [ ] Setup Prometheus metrics
- [ ] Setup alerting
- [ ] Dashboard Grafana

---

## 🎯 CONCLUSIONI

### Root Cause
Il problema principale è che **stiamo cercando tool NUOVI invece di tool POPOLARI**.

### Fix Principale
Cambiare da `sort=lastModified` a `sort=likes` risolve l'80% del problema.

### Impatto Atteso
- ✅ DeepSeek-R1, FLUX, Stable Diffusion verranno rilevati
- ✅ Coverage passa da ~20% a ~80%
- ✅ Qualità dei post aumenta significativamente
- ✅ Utenti vedranno tool veramente rilevanti

### Next Steps
1. **Oggi:** Implementare Priority 1 (2 ore)
2. **Questa settimana:** Testing approfondito
3. **Prossima settimana:** Implementare Priority 2
4. **Entro 2 settimane:** Priority 3 completa

---

**Report generato il:** 3 Dicembre 2025
**Prossima revisione:** Dopo implementazione Phase 1
**Versione:** 1.0.0
