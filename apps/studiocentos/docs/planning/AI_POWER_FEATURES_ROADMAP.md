# 🚀 AI POWER FEATURES ROADMAP - StudioCentOS

> **Documento di Roadmap per l'implementazione delle 5 AI Power Features**
>
> Data: 10 Dicembre 2025
> Team: StudioCentOS Development
> Stato: ✅ **COMPLETATO AL 100%**

---

## 🎉 IMPLEMENTATION STATUS

| Feature | Status | Files Created |
|---------|--------|---------------|
| 1. Instagram Insights API | ✅ COMPLETE | `integrations/instagram_insights.py`, `core/api/v1/insights/instagram_router.py` |
| 2. AI Feedback Loop | ✅ COMPLETE | `services/ai_feedback_loop.py`, `core/api/v1/ai/feedback_loop_router.py` |
| 3. LinkedIn API Publishing | ✅ COMPLETE | `integrations/linkedin_publishing.py`, `core/api/v1/social/linkedin_router.py` |
| 4. VEO Video Complete | ✅ COMPLETE | `services/veo_video_service.py`, `core/api/v1/ai/veo_router.py` |
| 5. Multi-Agent Orchestrator | ✅ COMPLETE | `ai_microservice/.../workflows.py`, `core/api/v1/ai/orchestrator_router.py` |

**Routers registered in `main.py` ✅**
**Settings updated with new env vars ✅**

---

## 📋 INDICE

1. [Overview Architettura Esistente](#overview-architettura-esistente)
2. [Feature 1: Instagram Insights API](#feature-1-instagram-insights-api)
3. [Feature 2: AI Feedback Loop](#feature-2-ai-feedback-loop)
4. [Feature 3: LinkedIn API Publishing](#feature-3-linkedin-api-publishing)
5. [Feature 4: VEO Video Complete](#feature-4-veo-video-complete)
6. [Feature 5: Multi-Agent Orchestrator Upgrade](#feature-5-multi-agent-orchestrator-upgrade)
7. [Variabili d'Ambiente](#variabili-dambiente)
8. [Testing e Deployment](#testing-e-deployment)
9. [Timeline Suggerita](#timeline-suggerita)

---

## 🏗️ Overview Architettura Esistente

### Struttura Backend Attuale

```
apps/backend/app/
├── core/                    # Core settings, API, security
│   └── api/v1/              # API Routers versione 1
├── domain/                  # Domain-Driven Design modules
│   ├── social/              # ✅ ESISTE: Social publishing (Meta, LinkedIn, Twitter)
│   ├── marketing/           # ✅ ESISTE: Lead enrichment, email, calendar
│   ├── analytics/           # ✅ ESISTE: Dashboard analytics
│   ├── toolai/              # ✅ ESISTE: AI Tools discovery
│   └── ...
├── integrations/            # External API integrations
│   ├── social_media.py      # ✅ ESISTE: Twitter, Facebook, Instagram base
│   ├── seo_tools.py         # ✅ ESISTE: SEO integrations
│   └── ...
├── services/                # Business logic services
│   ├── calendar_service.py  # ✅ ESISTE
│   └── notification_service.py
└── main.py                  # FastAPI application entry
```

### Struttura AI Microservice Attuale

```
apps/ai_microservice/app/
├── domain/marketing/        # ✅ Agenti Marketing esistenti
│   ├── content_creator.py   # ✅ ContentCreatorAgent
│   ├── social_media_manager.py # ✅ SocialMediaManagerAgent
│   ├── campaign_manager.py  # ✅ CampaignManagerAgent
│   ├── seo_specialist.py    # ✅ SEOSpecialistAgent
│   ├── email_marketing.py   # ✅ EmailMarketingAgent
│   ├── image_generator_agent.py # ✅ ImageGeneratorAgent
│   └── lead_intelligence_agent.py # ✅ LeadIntelligenceAgent
├── infrastructure/agents/   # ✅ Framework Agenti
│   ├── base_agent.py        # ✅ BaseAgent (abstract)
│   ├── orchestrator.py      # ✅ AgentOrchestrator BASE
│   ├── task.py              # ✅ Task, TaskInput, TaskOutput
│   ├── state.py             # ✅ StateManager
│   └── cognitive_memory.py  # ✅ CognitiveMemorySystem
└── infrastructure/tools/    # Tools per agenti
```

### Servizi Social Esistenti

**File: `apps/backend/app/domain/social/publisher_service.py`**
- ✅ `MetaPublisher` - Facebook + Instagram Publishing
- ✅ `LinkedInPublisher` - LinkedIn Company Page
- ✅ `TwitterPublisher` - Twitter/X via API v2

**File: `apps/backend/app/integrations/social_media.py`**
- ✅ `SocialMediaIntegration` - Stats aggregation

---

## 🔥 Feature 1: Instagram Insights API

### Obiettivo
Recupero completo delle metriche Instagram Business Account tramite Graph API.

### Prerequisiti
- Instagram Business Account collegato a Facebook Page
- Meta App con permessi `instagram_basic`, `instagram_manage_insights`, `pages_show_list`
- Long-lived access token

### File da Creare

#### 1.1 Servizio Instagram Insights
```
apps/backend/app/integrations/instagram_insights.py
```

**Classi e Metodi:**

```python
class InstagramInsightsService:
    """Servizio per recupero metriche Instagram."""

    # Configurazione
    BASE_URL = "https://graph.facebook.com/v18.0"

    # Metodi principali
    async def get_account_insights(days: int = 30) -> AccountInsights
    async def get_media_insights(media_id: str) -> MediaInsights
    async def get_story_insights(story_id: str) -> StoryInsights
    async def get_audience_demographics() -> AudienceData
    async def generate_performance_report(start_date, end_date) -> Report
```

**Schema Response:**

```python
class AccountInsights(BaseModel):
    followers_count: int
    follows_count: int
    media_count: int
    reach: int  # 28 days
    impressions: int  # 28 days
    profile_views: int
    website_clicks: int

class MediaInsights(BaseModel):
    post_id: str
    post_type: str  # IMAGE, VIDEO, CAROUSEL
    timestamp: datetime
    likes: int
    comments: int
    saves: int
    shares: int
    reach: int
    impressions: int
    engagement_rate: float
```

#### 1.2 Router API
```
apps/backend/app/core/api/v1/insights/instagram_router.py
```

**Endpoints:**

| Metodo | Path | Descrizione |
|--------|------|-------------|
| GET | `/api/v1/insights/instagram/status` | Stato connessione |
| GET | `/api/v1/insights/instagram/account` | Metriche account |
| GET | `/api/v1/insights/instagram/media` | Performance post (ultimi 50) |
| GET | `/api/v1/insights/instagram/media/{id}` | Dettaglio singolo post |
| GET | `/api/v1/insights/instagram/stories` | Performance stories |
| GET | `/api/v1/insights/instagram/demographics` | Dati demografici audience |
| GET | `/api/v1/insights/instagram/report` | Report completo PDF/JSON |

#### 1.3 Registrazione in main.py

```python
from app.core.api.v1.insights.instagram_router import router as instagram_insights_router

app.include_router(instagram_insights_router, prefix="/api/v1/insights")
```

### Variabili Ambiente Richieste
```env
INSTAGRAM_ACCOUNT_ID=17841400000000000
INSTAGRAM_ACCESS_TOKEN=EAAxxxxxxxxx
META_APP_ID=123456789
META_APP_SECRET=xxxxxxxx
```

### Instagram Graph API Reference

**Account Insights (GET /{ig-user-id}/insights):**
- `follower_count`, `reach`, `impressions`, `profile_views`
- Period: `day`, `week`, `days_28`

**Media Insights (GET /{media-id}/insights):**
- `engagement`, `impressions`, `reach`, `saved`, `shares`
- Per VIDEO: `video_views`, `plays`
- Per REELS: `comments`, `likes`, `shares`, `plays`, `reach`

---

## 🧠 Feature 2: AI Feedback Loop

### Obiettivo
Sistema che collega le performance reali dei post alla generazione di contenuti futuri, creando un ciclo di apprendimento continuo.

### Architettura

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Instagram API  │────▶│  Feedback Loop   │────▶│ Content Creator │
│  (Insights)     │     │  Service         │     │ Agent           │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                      │                        │
         │              ┌───────▼───────┐                │
         │              │ Pattern Store │                │
         │              │ (PostgreSQL)  │                │
         │              └───────┬───────┘                │
         │                      │                        │
         └──────────────────────┴────────────────────────┘
                     Learning Signals
```

### File da Creare

#### 2.1 Core Service
```
apps/backend/app/services/ai_feedback_loop.py
```

**Classi e Metodi:**

```python
class AIFeedbackLoopService:
    """
    Servizio che analizza performance passate e ottimizza
    le generazioni future di contenuti.
    """

    # Ingestione dati
    async def ingest_performance_data(posts: List[PostPerformance]) -> bool

    # Analisi Pattern
    async def analyze_patterns(platform: str) -> ContentPatterns

    # Generazione Signals
    async def generate_learning_signals(platform: str) -> LearningSignals

    # Ottimizzazione Prompt
    async def optimize_prompt(base_prompt: str, platform: str) -> OptimizedPrompt

    # Sync da Instagram
    async def sync_from_instagram() -> SyncResult


class ContentPatterns(BaseModel):
    """Pattern identificati dai contenuti performanti."""
    best_posting_hours: List[int]  # [9, 12, 18, 21]
    best_posting_days: List[str]   # ["tuesday", "thursday"]
    top_content_types: List[str]   # ["carousel", "reel"]
    top_topics: List[str]          # ["AI", "marketing", "tips"]
    avg_caption_length: int        # Lunghezza media caption performanti
    top_hashtags: List[str]        # Hashtag con più engagement
    top_ctas: List[str]            # Call-to-action più efficaci
    visual_style: str              # "minimalist", "vibrant", etc.


class LearningSignals(BaseModel):
    """Segnali di apprendimento per Content Creator."""
    do_more: List[str]       # Cose da fare di più
    do_less: List[str]       # Cose da evitare
    experiment_with: List[str]  # Nuove cose da provare
    optimal_frequency: str   # "2 posts/day", "1 post/day"
    content_mix: Dict[str, float]  # {"carousel": 0.4, "reel": 0.3, "image": 0.3}
```

#### 2.2 Database Models
```
apps/backend/app/domain/marketing/feedback_models.py
```

```python
class ContentPerformanceHistory(Base):
    """Storico performance contenuti per training."""
    __tablename__ = "content_performance_history"

    id = Column(UUID, primary_key=True)
    platform = Column(String(50), index=True)
    post_id = Column(String(100), unique=True)
    post_type = Column(String(50))
    content = Column(Text)
    hashtags = Column(ARRAY(String))
    posted_at = Column(DateTime)
    hour_posted = Column(Integer)
    day_of_week = Column(Integer)

    # Metrics
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)

    # Calculated
    performance_score = Column(Float, default=0.0)  # 0-100 normalized

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

#### 2.3 Router API
```
apps/backend/app/core/api/v1/ai/feedback_loop_router.py
```

**Endpoints:**

| Metodo | Path | Descrizione |
|--------|------|-------------|
| GET | `/api/v1/ai/feedback-loop/status` | Stato del sistema |
| POST | `/api/v1/ai/feedback-loop/ingest` | Ingestione manuale dati |
| GET | `/api/v1/ai/feedback-loop/patterns/{platform}` | Pattern identificati |
| GET | `/api/v1/ai/feedback-loop/signals/{platform}` | Learning signals |
| POST | `/api/v1/ai/feedback-loop/optimize-prompt` | Ottimizza un prompt |
| POST | `/api/v1/ai/feedback-loop/sync-from-instagram` | Sync dati da IG |
| GET | `/api/v1/ai/feedback-loop/history` | Storico analisi |

### Algoritmo di Scoring

```python
def calculate_performance_score(post: PostMetrics) -> float:
    """
    Calcola score 0-100 basato su metriche ponderate.

    Pesi:
    - Engagement Rate: 30%
    - Saves (intent): 25%
    - Shares (virality): 20%
    - Comments (interaction): 15%
    - Reach vs Followers: 10%
    """
    weights = {
        "engagement_rate": 0.30,
        "saves_rate": 0.25,
        "shares_rate": 0.20,
        "comments_rate": 0.15,
        "reach_rate": 0.10
    }

    # Normalizza ciascuna metrica su scala 0-100
    normalized = {
        "engagement_rate": min(post.engagement_rate * 10, 100),  # 10% ER = 100
        "saves_rate": min((post.saves / post.reach) * 500, 100),  # 20% save rate = 100
        "shares_rate": min((post.shares / post.reach) * 200, 100),  # 50% share rate = 100
        "comments_rate": min((post.comments / post.reach) * 100, 100),  # 1% = 100
        "reach_rate": min((post.reach / followers) * 100, 100),  # 100% reach = 100
    }

    return sum(normalized[k] * weights[k] for k in weights)
```

### Integrazione con Content Creator Agent

Modificare `apps/ai_microservice/app/domain/marketing/content_creator.py`:

```python
class ContentCreatorAgent(BaseAgent):
    def __init__(self, config: AgentConfig, feedback_service: AIFeedbackLoopService = None):
        super().__init__(config)
        self.feedback_service = feedback_service

    async def generate_social_post(self, request: SocialPostRequest) -> SocialPost:
        # 1. Recupera learning signals
        if self.feedback_service:
            signals = await self.feedback_service.generate_learning_signals(
                platform=request.platform
            )

            # 2. Arricchisci il prompt con i signals
            enhanced_prompt = await self.feedback_service.optimize_prompt(
                base_prompt=request.prompt,
                platform=request.platform
            )
        else:
            enhanced_prompt = request.prompt

        # 3. Genera contenuto con prompt ottimizzato
        return await self._generate(enhanced_prompt)
```

---

## 💼 Feature 3: LinkedIn API Publishing

### Obiettivo
Pubblicazione nativa su LinkedIn Personal Profile e Company Pages tramite LinkedIn Marketing API.

### Prerequisiti
- LinkedIn Developer App con prodotti:
  - Share on LinkedIn
  - Marketing Developer Platform (opzionale per analytics)
- OAuth 2.0 flow implementato
- Scopes: `w_member_social`, `r_liteprofile`, `r_organization_social` (per company)

### File da Creare/Modificare

#### 3.1 Servizio LinkedIn Publishing
```
apps/backend/app/integrations/linkedin_publishing.py
```

**Classi e Metodi:**

```python
class LinkedInPublishingService:
    """Servizio completo per pubblicazione LinkedIn."""

    BASE_URL = "https://api.linkedin.com/v2"

    # OAuth
    def get_authorization_url(state: str) -> str
    async def exchange_code_for_token(code: str) -> TokenResponse
    async def refresh_access_token(refresh_token: str) -> TokenResponse

    # Profile
    async def get_profile() -> LinkedInProfile
    async def get_organizations() -> List[Organization]

    # Publishing
    async def publish_text_post(text: str, visibility: str = "PUBLIC") -> PostResult
    async def publish_image_post(text: str, image_url: str) -> PostResult
    async def publish_article_post(text: str, article_url: str, title: str) -> PostResult
    async def publish_document_post(text: str, document_url: str) -> PostResult
    async def publish_to_company(org_id: str, content: PostContent) -> PostResult

    # Analytics (richiede Marketing Developer Platform)
    async def get_post_analytics(post_urn: str) -> PostAnalytics
```

**LinkedIn API Specifics:**

```python
# UGC Post API (User Generated Content)
POST https://api.linkedin.com/v2/ugcPosts

# Payload per Text Post
{
    "author": "urn:li:person:{PERSON_ID}",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": "Il tuo testo qui #hashtag"
            },
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}

# Payload per Image Post (richiede upload prima)
# Step 1: Register Upload
POST https://api.linkedin.com/v2/assets?action=registerUpload

# Step 2: Upload binary to presigned URL
PUT {uploadUrl} with image binary

# Step 3: Create post with asset
{
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": "..."},
            "shareMediaCategory": "IMAGE",
            "media": [{
                "status": "READY",
                "media": "urn:li:digitalmediaAsset:{ASSET_ID}"
            }]
        }
    }
}
```

#### 3.2 Router API
```
apps/backend/app/domain/social/linkedin_router.py
```

**Endpoints:**

| Metodo | Path | Descrizione |
|--------|------|-------------|
| GET | `/api/v1/social/linkedin/auth/url` | URL per OAuth |
| GET | `/api/v1/social/linkedin/auth/callback` | Callback OAuth |
| GET | `/api/v1/social/linkedin/status` | Stato connessione |
| GET | `/api/v1/social/linkedin/profile` | Profilo utente |
| GET | `/api/v1/social/linkedin/organizations` | Company pages gestite |
| POST | `/api/v1/social/linkedin/publish/text` | Pubblica testo |
| POST | `/api/v1/social/linkedin/publish/image` | Pubblica con immagine |
| POST | `/api/v1/social/linkedin/publish/article` | Pubblica con link preview |
| POST | `/api/v1/social/linkedin/publish` | Pubblicazione unificata |
| POST | `/api/v1/social/linkedin/company/{id}/publish` | Pubblica su Company |

### Variabili Ambiente Richieste
```env
LINKEDIN_CLIENT_ID=86xxxxxxxxx
LINKEDIN_CLIENT_SECRET=xxxxxxxxxxxx
LINKEDIN_REDIRECT_URI=https://api.studiocentos.it/api/v1/social/linkedin/auth/callback
LINKEDIN_ACCESS_TOKEN=AQVxxxxxxxxx  # (dopo OAuth)
LINKEDIN_PERSON_ID=xxxxxxxx
```

### LinkedIn API Rate Limits
- **UGC Posts**: 100 posts/day per member
- **API Calls**: 100,000 calls/day
- **Image Upload**: Max 8MB per image
- **Video Upload**: Max 200MB, 10 min duration

---

## 🎬 Feature 4: VEO Video Complete

### Obiettivo
Generazione video AI completa con Google VEO 2, incluso polling, download e storage.

### Prerequisiti
- Google Cloud Project con Vertex AI abilitato
- API Key o Service Account con ruolo `Vertex AI User`
- Billing abilitato su Google Cloud

### Architettura

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Frontend       │────▶│  VEO Router      │────▶│ VEO Service     │
│  Request        │     │  (FastAPI)       │     │                 │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                        ┌─────────────────────────────────┼─────────┐
                        │                                 ▼         │
                        │  ┌──────────────┐     ┌─────────────────┐ │
                        │  │ Job Tracker  │◀────│ Vertex AI VEO   │ │
                        │  │ (Redis/DB)   │     │ Predict API     │ │
                        │  └──────┬───────┘     └─────────────────┘ │
                        │         │                                 │
                        │         ▼                                 │
                        │  ┌──────────────┐     ┌─────────────────┐ │
                        │  │ Background   │────▶│ Storage         │ │
                        │  │ Polling Task │     │ (uploads/video) │ │
                        │  └──────────────┘     └─────────────────┘ │
                        │                                           │
                        └───────────────────────────────────────────┘
```

### File da Creare

#### 4.1 VEO Video Service
```
apps/backend/app/services/veo_video_service.py
```

**Classi e Metodi:**

```python
class VEOVideoService:
    """Servizio completo per generazione video con Google VEO."""

    # Vertex AI Endpoint
    ENDPOINT = "https://us-central1-aiplatform.googleapis.com/v1"

    # Generazione
    async def generate_video(
        prompt: str,
        duration: int = 8,  # seconds
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        style: Optional[str] = None
    ) -> VideoGenerationJob

    async def generate_from_image(
        prompt: str,
        image_url: str,
        duration: int = 8
    ) -> VideoGenerationJob

    # Job Management
    async def get_job_status(job_id: str) -> JobStatus
    async def poll_until_complete(job_id: str, timeout: int = 300) -> VideoResult
    async def cancel_job(job_id: str) -> bool

    # Download & Storage
    async def download_video(video_url: str, job_id: str) -> str  # local path
    async def cleanup_old_videos(days: int = 7) -> int  # deleted count

    # Templates
    async def generate_marketing_video(template: MarketingTemplate) -> VideoGenerationJob


class VideoGenerationJob(BaseModel):
    job_id: str
    status: str  # "PENDING", "PROCESSING", "COMPLETED", "FAILED"
    prompt: str
    duration: int
    resolution: str
    video_url: Optional[str] = None
    local_path: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class MarketingTemplate(BaseModel):
    template_id: str
    name: str
    base_prompt: str
    duration: int = 8
    style: str
    variables: Dict[str, str]  # Variabili da sostituire nel prompt
```

#### 4.2 VEO API Integration

```python
# Vertex AI VEO API Call
async def _call_veo_api(self, prompt: str, config: VideoConfig) -> str:
    """
    Chiama Vertex AI VEO per generazione video.

    Returns: operation_name for polling
    """
    endpoint = f"{self.ENDPOINT}/projects/{self.project_id}/locations/us-central1/publishers/google/models/veo-001:predict"

    payload = {
        "instances": [{
            "prompt": prompt,
            "video_generation_config": {
                "duration_seconds": config.duration,
                "resolution": config.resolution,
                "aspect_ratio": config.aspect_ratio,
                "num_videos": 1
            }
        }],
        "parameters": {
            "temperature": 0.7,
            "seed": config.seed or random.randint(0, 999999)
        }
    }

    headers = {
        "Authorization": f"Bearer {await self._get_access_token()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(endpoint, json=payload, headers=headers)
        result = response.json()

        # VEO returns operation for async processing
        return result.get("name")  # "projects/.../operations/..."


async def _poll_operation(self, operation_name: str) -> Dict:
    """Poll operation fino a completamento."""
    endpoint = f"{self.ENDPOINT}/{operation_name}"

    while True:
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, headers=self._get_headers())
            result = response.json()

            if result.get("done"):
                if "error" in result:
                    raise VEOError(result["error"]["message"])
                return result.get("response", {})

            await asyncio.sleep(5)  # Poll ogni 5 secondi
```

#### 4.3 Router API
```
apps/backend/app/core/api/v1/ai/veo_router.py
```

**Endpoints:**

| Metodo | Path | Descrizione |
|--------|------|-------------|
| GET | `/api/v1/ai/video/status` | Stato servizio VEO |
| POST | `/api/v1/ai/video/generate` | Genera video (sync) |
| POST | `/api/v1/ai/video/generate-async` | Genera video (async) |
| POST | `/api/v1/ai/video/generate-from-image` | Video da immagine |
| GET | `/api/v1/ai/video/jobs` | Lista job attivi |
| GET | `/api/v1/ai/video/jobs/{job_id}` | Stato job specifico |
| DELETE | `/api/v1/ai/video/jobs/{job_id}` | Cancella job |
| GET | `/api/v1/ai/video/templates` | Template marketing |
| POST | `/api/v1/ai/video/templates/{id}/generate` | Genera da template |

### Variabili Ambiente Richieste
```env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
# Oppure
GOOGLE_API_KEY=AIzaSyxxxxxxxxx
VEO_DEFAULT_RESOLUTION=720p
VEO_MAX_DURATION=10
```

### Template Marketing Predefiniti

```python
MARKETING_TEMPLATES = [
    {
        "id": "product_showcase",
        "name": "Product Showcase",
        "base_prompt": "Cinematic product showcase of {product_name}, elegant lighting, smooth camera movement, luxury feel, 4K quality",
        "duration": 8,
        "style": "cinematic"
    },
    {
        "id": "brand_intro",
        "name": "Brand Introduction",
        "base_prompt": "Dynamic brand introduction for {brand_name}, modern typography, energetic transitions, corporate yet creative",
        "duration": 6,
        "style": "dynamic"
    },
    {
        "id": "testimonial",
        "name": "Testimonial Background",
        "base_prompt": "Abstract flowing background for testimonial video, soft gradients in {brand_colors}, gentle movement, professional",
        "duration": 10,
        "style": "abstract"
    },
    {
        "id": "social_hook",
        "name": "Social Media Hook",
        "base_prompt": "Attention-grabbing opening for social video about {topic}, bold visuals, quick cuts, trending style",
        "duration": 3,
        "style": "energetic"
    }
]
```

---

## 🤖 Feature 5: Multi-Agent Orchestrator Upgrade

### Obiettivo
Potenziare l'orchestratore esistente con shared memory, workflow predefiniti e coordinazione avanzata tra agenti.

### Stato Attuale
L'orchestratore base esiste già in:
```
apps/ai_microservice/app/infrastructure/agents/orchestrator.py
```

### Upgrade da Implementare

#### 5.1 Upgrade Orchestrator
```
apps/ai_microservice/app/infrastructure/agents/orchestrator.py
```

**Nuove Funzionalità:**

```python
class EnhancedAgentOrchestrator(AgentOrchestrator):
    """Orchestratore potenziato con workflow e shared memory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shared_memory: Dict[str, Any] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self._load_default_workflows()

    # Shared Memory
    def set_memory(self, key: str, value: Any, scope: str = "global") -> None
    def get_memory(self, key: str, scope: str = "global") -> Any
    def clear_memory(self, scope: Optional[str] = None) -> None

    # Event System
    def on_event(self, event_type: str, handler: Callable) -> None
    async def emit_event(self, event_type: str, data: Any) -> None

    # Predefined Workflows
    async def execute_workflow_by_name(self, name: str, params: Dict) -> WorkflowResult
    async def execute_daily_content_workflow(self, params: DailyContentParams) -> WorkflowResult
    async def execute_campaign_launch_workflow(self, params: CampaignParams) -> WorkflowResult

    # Pipeline Execution
    async def execute_pipeline(self, pipeline: List[PipelineStep]) -> PipelineResult
```

#### 5.2 Workflow Definitions
```
apps/ai_microservice/app/infrastructure/agents/workflows.py
```

```python
class WorkflowDefinition(BaseModel):
    """Definizione di un workflow riutilizzabile."""

    name: str
    description: str
    steps: List[WorkflowStep]
    triggers: List[str] = []  # Trigger automatici
    schedule: Optional[str] = None  # Cron expression


class WorkflowStep(BaseModel):
    """Singolo step di un workflow."""

    step_id: str
    agent_type: str
    action: str
    input_mapping: Dict[str, str]  # Come mappare input dal contesto
    output_key: str  # Dove salvare output nella shared memory
    depends_on: List[str] = []  # Step precedenti richiesti
    retry_on_failure: bool = True
    timeout: int = 60


# Workflow Predefiniti
DAILY_CONTENT_WORKFLOW = WorkflowDefinition(
    name="daily_content",
    description="Genera contenuto giornaliero per tutti i canali",
    steps=[
        WorkflowStep(
            step_id="analyze_performance",
            agent_type="performance_analyzer",
            action="get_yesterday_performance",
            input_mapping={},
            output_key="performance_data"
        ),
        WorkflowStep(
            step_id="get_trends",
            agent_type="seo_specialist",
            action="get_trending_topics",
            input_mapping={"niche": "config.niche"},
            output_key="trends"
        ),
        WorkflowStep(
            step_id="create_content",
            agent_type="content_creator",
            action="generate_daily_content",
            input_mapping={
                "performance": "memory.performance_data",
                "trends": "memory.trends"
            },
            output_key="content",
            depends_on=["analyze_performance", "get_trends"]
        ),
        WorkflowStep(
            step_id="create_images",
            agent_type="image_generator",
            action="generate_images_for_content",
            input_mapping={"content": "memory.content"},
            output_key="images",
            depends_on=["create_content"]
        ),
        WorkflowStep(
            step_id="schedule_posts",
            agent_type="social_manager",
            action="schedule_multi_platform",
            input_mapping={
                "content": "memory.content",
                "images": "memory.images"
            },
            output_key="scheduled_posts",
            depends_on=["create_images"]
        )
    ],
    schedule="0 7 * * *"  # Ogni giorno alle 7:00
)


CAMPAIGN_LAUNCH_WORKFLOW = WorkflowDefinition(
    name="campaign_launch",
    description="Lancia una nuova campagna marketing",
    steps=[
        WorkflowStep(
            step_id="create_campaign_strategy",
            agent_type="campaign_manager",
            action="create_strategy",
            input_mapping={"brief": "input.campaign_brief"},
            output_key="strategy"
        ),
        WorkflowStep(
            step_id="generate_all_content",
            agent_type="content_creator",
            action="generate_campaign_content",
            input_mapping={"strategy": "memory.strategy"},
            output_key="all_content",
            depends_on=["create_campaign_strategy"]
        ),
        WorkflowStep(
            step_id="generate_visuals",
            agent_type="image_generator",
            action="generate_campaign_visuals",
            input_mapping={"content": "memory.all_content"},
            output_key="visuals",
            depends_on=["generate_all_content"]
        ),
        WorkflowStep(
            step_id="create_email_sequence",
            agent_type="email_marketer",
            action="create_drip_campaign",
            input_mapping={"strategy": "memory.strategy"},
            output_key="email_sequence",
            depends_on=["create_campaign_strategy"]
        ),
        WorkflowStep(
            step_id="optimize_for_seo",
            agent_type="seo_specialist",
            action="optimize_campaign_content",
            input_mapping={"content": "memory.all_content"},
            output_key="seo_content",
            depends_on=["generate_all_content"]
        ),
        WorkflowStep(
            step_id="schedule_everything",
            agent_type="social_manager",
            action="schedule_campaign",
            input_mapping={
                "content": "memory.seo_content",
                "visuals": "memory.visuals",
                "strategy": "memory.strategy"
            },
            output_key="schedule",
            depends_on=["optimize_for_seo", "generate_visuals"]
        )
    ]
)
```

#### 5.3 Router API per Orchestrator
```
apps/backend/app/core/api/v1/ai/orchestrator_router.py
```

**Endpoints:**

| Metodo | Path | Descrizione |
|--------|------|-------------|
| GET | `/api/v1/ai/orchestrator/status` | Stato orchestratore |
| GET | `/api/v1/ai/orchestrator/agents` | Lista agenti registrati |
| POST | `/api/v1/ai/orchestrator/tasks` | Esegui singolo task |
| POST | `/api/v1/ai/orchestrator/pipelines` | Esegui pipeline custom |
| GET | `/api/v1/ai/orchestrator/workflows` | Lista workflow disponibili |
| POST | `/api/v1/ai/orchestrator/workflows/{name}/execute` | Esegui workflow |
| POST | `/api/v1/ai/orchestrator/workflows/daily-content` | Workflow giornaliero |
| POST | `/api/v1/ai/orchestrator/workflows/campaign-launch` | Workflow campagna |
| GET | `/api/v1/ai/orchestrator/memory` | Visualizza shared memory |
| DELETE | `/api/v1/ai/orchestrator/memory` | Pulisci shared memory |
| GET | `/api/v1/ai/orchestrator/executions` | Storico esecuzioni |
| GET | `/api/v1/ai/orchestrator/executions/{id}` | Dettaglio esecuzione |

### Registrazione Agenti

```python
# Registrazione automatica all'avvio
def setup_orchestrator() -> EnhancedAgentOrchestrator:
    orchestrator = EnhancedAgentOrchestrator(
        strategy=OrchestrationStrategy.DEPENDENCY
    )

    # Registra tutti gli agenti
    orchestrator.register_agent(ContentCreatorAgent(config=content_config))
    orchestrator.register_agent(SocialMediaManagerAgent(config=social_config))
    orchestrator.register_agent(CampaignManagerAgent(config=campaign_config))
    orchestrator.register_agent(SEOSpecialistAgent(config=seo_config))
    orchestrator.register_agent(EmailMarketingAgent(config=email_config))
    orchestrator.register_agent(ImageGeneratorAgent(config=image_config))
    orchestrator.register_agent(LeadIntelligenceAgent(config=lead_config))

    return orchestrator
```

---

## 🔧 Variabili d'Ambiente

### File: `.env` (da aggiungere)

```env
# ============================================================================
# INSTAGRAM INSIGHTS
# ============================================================================
INSTAGRAM_ACCOUNT_ID=17841400000000000
INSTAGRAM_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxx
META_APP_ID=123456789012345
META_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx

# ============================================================================
# LINKEDIN PUBLISHING
# ============================================================================
LINKEDIN_CLIENT_ID=86xxxxxxxxxx
LINKEDIN_CLIENT_SECRET=xxxxxxxxxxxxxxxx
LINKEDIN_REDIRECT_URI=https://api.studiocentos.it/api/v1/social/linkedin/auth/callback
LINKEDIN_ACCESS_TOKEN=AQVxxxxxxxxxxxxxxxxxx  # Popolato dopo OAuth
LINKEDIN_REFRESH_TOKEN=AQVxxxxxxxxxxxxxxxxxx
LINKEDIN_PERSON_ID=xxxxxxxxx

# ============================================================================
# GOOGLE VEO / VERTEX AI
# ============================================================================
GOOGLE_CLOUD_PROJECT=studiocentos-prod
GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/gcp-service-account.json
# Oppure API Key
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxx
VEO_ENABLED=true
VEO_DEFAULT_RESOLUTION=720p
VEO_MAX_DURATION_SECONDS=10
VEO_STORAGE_PATH=/app/uploads/videos

# ============================================================================
# AI FEEDBACK LOOP
# ============================================================================
FEEDBACK_LOOP_ENABLED=true
FEEDBACK_SYNC_INTERVAL_HOURS=6
FEEDBACK_MIN_POSTS_FOR_PATTERNS=20
FEEDBACK_PERFORMANCE_THRESHOLD=50  # Score minimo per pattern

# ============================================================================
# ORCHESTRATOR
# ============================================================================
ORCHESTRATOR_MAX_CONCURRENT_TASKS=5
ORCHESTRATOR_DEFAULT_TIMEOUT=120
ORCHESTRATOR_ENABLE_DAILY_WORKFLOW=true
ORCHESTRATOR_DAILY_WORKFLOW_TIME=07:00
```

---

## 🧪 Testing e Deployment

### Unit Tests da Creare

```
apps/backend/tests/
├── integrations/
│   ├── test_instagram_insights.py
│   └── test_linkedin_publishing.py
├── services/
│   ├── test_ai_feedback_loop.py
│   └── test_veo_video_service.py
└── ai/
    └── test_orchestrator_upgrade.py
```

### Test Checklist

#### Instagram Insights
- [ ] Test connessione API
- [ ] Test recupero account insights
- [ ] Test recupero media insights
- [ ] Test rate limiting handling
- [ ] Test token refresh

#### AI Feedback Loop
- [ ] Test ingestione dati
- [ ] Test calcolo performance score
- [ ] Test pattern analysis
- [ ] Test prompt optimization
- [ ] Test integrazione con Content Creator

#### LinkedIn Publishing
- [ ] Test OAuth flow
- [ ] Test pubblicazione testo
- [ ] Test pubblicazione immagine
- [ ] Test pubblicazione articolo
- [ ] Test Company Page publishing

#### VEO Video
- [ ] Test generazione video
- [ ] Test polling operation
- [ ] Test download e storage
- [ ] Test cleanup
- [ ] Test templates

#### Orchestrator
- [ ] Test registrazione agenti
- [ ] Test shared memory
- [ ] Test workflow execution
- [ ] Test dependency resolution
- [ ] Test error handling

### Docker Compose Updates

```yaml
# docker-compose.production.yml
services:
  backend:
    environment:
      # Nuove variabili
      - INSTAGRAM_ACCOUNT_ID=${INSTAGRAM_ACCOUNT_ID}
      - INSTAGRAM_ACCESS_TOKEN=${INSTAGRAM_ACCESS_TOKEN}
      - LINKEDIN_CLIENT_ID=${LINKEDIN_CLIENT_ID}
      - LINKEDIN_CLIENT_SECRET=${LINKEDIN_CLIENT_SECRET}
      - GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
      - VEO_ENABLED=${VEO_ENABLED}
      - FEEDBACK_LOOP_ENABLED=${FEEDBACK_LOOP_ENABLED}
    volumes:
      # Per video storage
      - ./uploads/videos:/app/uploads/videos
      # Per GCP credentials
      - ./secrets:/app/secrets:ro
```

---

## 📅 Timeline Suggerita

### Settimana 1: Fondamenta
| Giorno | Task | Owner |
|--------|------|-------|
| Lun | Setup variabili ambiente, test connessioni API | DevOps |
| Mar | Instagram Insights Service + Tests | Backend Dev |
| Mer | Instagram Insights Router + Integration | Backend Dev |
| Gio | AI Feedback Loop Service base | Backend Dev |
| Ven | AI Feedback Loop Integration + Tests | Backend Dev |

### Settimana 2: Publishing
| Giorno | Task | Owner |
|--------|------|-------|
| Lun | LinkedIn OAuth Flow | Backend Dev |
| Mar | LinkedIn Publishing Service | Backend Dev |
| Mer | LinkedIn Router + Tests | Backend Dev |
| Gio | VEO Video Service base | Backend Dev |
| Ven | VEO Polling + Storage + Tests | Backend Dev |

### Settimana 3: Orchestration
| Giorno | Task | Owner |
|--------|------|-------|
| Lun | Orchestrator Upgrade - Shared Memory | AI Dev |
| Mar | Orchestrator Upgrade - Workflows | AI Dev |
| Mer | Workflow Definitions + Tests | AI Dev |
| Gio | Orchestrator Router | Backend Dev |
| Ven | Integration Testing | QA |

### Settimana 4: Polish & Deploy
| Giorno | Task | Owner |
|--------|------|-------|
| Lun | Bug fixes, edge cases | All |
| Mar | Performance optimization | Backend Dev |
| Mer | Documentation update | Tech Lead |
| Gio | Staging deployment | DevOps |
| Ven | Production deployment | DevOps |

---

## 📝 Note Finali

### Priorità di Implementazione
1. **ALTA**: Instagram Insights + Feedback Loop (base per tutto)
2. **ALTA**: VEO Video (richiesto per contenuti visual)
3. **MEDIA**: LinkedIn Publishing (estensione social)
4. **MEDIA**: Orchestrator Upgrade (automazione)

### Dipendenze
```
Instagram Insights ◀──── AI Feedback Loop
                              │
                              ▼
                    Content Creator Agent
                              │
                              ▼
VEO Video ◀──────── Orchestrator Workflows
     │
     ▼
LinkedIn Publishing ◀── Social Manager Agent
```

### Rischi e Mitigazioni
| Rischio | Probabilità | Mitigazione |
|---------|-------------|-------------|
| Rate limits Instagram | Alta | Cache aggressiva, sync batch |
| VEO latency | Media | Background jobs, polling async |
| LinkedIn OAuth expiry | Media | Refresh token automatico |
| Orchestrator deadlock | Bassa | Timeout per task, circuit breaker |

---

**Documento creato il**: 10 Dicembre 2025
**Ultimo aggiornamento**: 10 Dicembre 2025
**Versione**: 1.0.0
