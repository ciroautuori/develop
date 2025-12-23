# 🎨 GOOGLE CREATIVE APIS - PIANO DI INTEGRAZIONE

**Data:** 3 Dicembre 2025
**Obiettivo:** Integrare le nuove Google Creative APIs nel Marketing Hub

---

## 📋 EXECUTIVE SUMMARY

Google ha rilasciato tre nuove API creative potentissime:

1. **Nano Banana / Gemini 2.5 Flash Image** - Generazione immagini GRATUITA, veloce
2. **Nano Banana Pro / Gemini 3 Pro Image** - Generazione professionale fino a 4K con "Thinking"
3. **Imagen 4** - Modello specializzato per immagini fotorealistiche e branding

**NOTA IMPORTANTE:** Whisk, Pomelli, Flow NON sono API pubbliche (404 su labs.google.com)
Sono strumenti sperimentali interni Google, NON ancora rilasciati come API.

---

## 🎯 API DISPONIBILI E CAPACITÀ

### 1. Gemini 2.5 Flash Image (Nano Banana) 🍌
**Modello:** `gemini-2.5-flash-image`
**Stato:** ✅ Production Ready - FREE tier disponibile!

#### Capacità:
- ✅ Text-to-Image (prompt → immagine)
- ✅ Image-to-Image editing (modifica immagini esistenti)
- ✅ Multi-turn conversational editing (modifica iterativa)
- ✅ Aspect ratios multipli (1:1, 16:9, 9:16, 4:3, 3:4, 4:5, 5:4, 21:9)
- ✅ Resolution: 1024px (varie dimensioni per aspect ratio)
- ✅ Veloce e ottimizzato per high-volume
- ✅ SynthID watermark automatico

#### Pricing:
- **FREE TIER:** Disponibile con quota giornaliera
- **Token-based:** $30 per 1M tokens output
- **1 immagine = 1290 tokens** (flat rate fino a 1024x1024px)

#### Use Cases Marketing:
- Social media posts (veloce, batch generation)
- Instagram stories, Facebook ads
- Varianti A/B testing
- Content calendar automation

---

### 2. Gemini 3 Pro Image (Nano Banana Pro) 🍌⭐
**Modello:** `gemini-3-pro-image-preview`
**Stato:** ⚠️ Preview (Production usage allowed)

#### Capacità ADVANCED:
- ✅ Tutto di Nano Banana +
- ✅ **Thinking Mode** - reasoning process per composizione ottimale
- ✅ **4K Resolution** (1K, 2K, 4K selezionabili)
- ✅ **Grounding con Google Search** (immagini basate su dati real-time!)
- ✅ **Multi-image input** (fino a 14 immagini di riferimento!)
  - 6 immagini oggetti high-fidelity
  - 5 immagini persone per character consistency
- ✅ **Professional text rendering** (loghi, infografiche, menu)
- ✅ **Style transfer** avanzato
- ✅ **Advanced composition** (combina elementi multipli)

#### Pricing:
- **Token-based:** $30 per 1M tokens output (1210 tokens per 1K, 2000 per 4K)

#### Use Cases Marketing:
- Asset professionali per clienti (loghi, brochure)
- Infografiche con dati real-time
- Campagne pubblicitarie premium
- Product mockups high-end
- Weather forecasts visuali, stock charts

---

### 3. Imagen 4 (Specialista Fotorealismo)
**Modelli:**
- `imagen-4.0-generate-001` (Standard)
- `imagen-4.0-ultra-generate-001` (Ultra quality)
- `imagen-4.0-fast-generate-001` (Fast)

**Stato:** ✅ Generally Available

#### Capacità:
- ✅ Fotorealismo estremo
- ✅ Dettagli artistici precisi
- ✅ Stili specifici (impressionismo, anime, etc.)
- ✅ Branding e logo generation
- ✅ Typography avanzata
- ✅ Latenza bassa (near-real-time)
- ✅ Aspect ratios: 1:1, 3:4, 4:3, 9:16, 16:9
- ✅ 1-4 immagini per request (Ultra: 1 sola)

#### Pricing:
- **Cost-effective:** $0.02/image (Fast) a $0.12/image (Ultra)

#### Use Cases Marketing:
- Product photography per e-commerce
- Advertising campaigns (qualità massima)
- Portraits professionali
- Food photography per ristoranti
- Real estate renders

---

## 🚀 PIANO DI INTEGRAZIONE NEL MARKETING HUB

### FASE 1: Upgrade Servizio Esistente (IMMEDIATO)

**Attuale:** AI Microservice usa Pollinations.ai (free, FLUX model)
**Location:** `/apps/ai_microservice/app/core/api/v1/marketing.py` (linea 194+)

#### 1.1 Aggiungere Nano Banana come Provider Primario

```python
# Priority order (aggiornato):
# 1. Google Gemini Nano Banana (gemini-2.5-flash-image) - FREE + FAST
# 2. Pollinations.ai (FLUX) - FREE fallback
# 3. HuggingFace SD-XL - FREE fallback
```

**Endpoint da implementare:**
```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent
Authorization: Bearer {GOOGLE_AI_API_KEY}
```

**Request body:**
```json
{
  "contents": [{
    "parts": [{"text": "enhanced_prompt"}]
  }],
  "generationConfig": {
    "response_modalities": ["IMAGE"],
    "image_config": {
      "aspect_ratio": "1:1"  // o 16:9, 9:16, etc
    }
  }
}
```

**Response:**
```json
{
  "candidates": [{
    "content": {
      "parts": [{
        "inline_data": {
          "mime_type": "image/png",
          "data": "<base64_image>"
        }
      }]
    }
  }]
}
```

#### 1.2 Modifiche al File `marketing.py`

**Nuovo provider order:**
```python
async def generate_image(request: ImageGenerationRequest):
    # Providers in priority order:
    # 1. Gemini Nano Banana (if API key available)
    # 2. Pollinations.ai (current, keep as fallback)
    # 3. HuggingFace (backup fallback)

    if request.provider in ["auto", "google", "gemini"]:
        try:
            return await _gemini_nano_banana_generate(request)
        except Exception as e:
            logger.warning("gemini_failed", error=str(e))

    if request.provider in ["auto", "pollinations"]:
        # current implementation...
```

**Nuova funzione:**
```python
async def _gemini_nano_banana_generate(request: ImageGenerationRequest):
    """Generate using Google Gemini Nano Banana (2.5 Flash Image)"""
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        raise Exception("GOOGLE_AI_API_KEY not configured")

    # Map aspect ratio
    aspect_ratio_map = {
        "1:1": "1:1",
        "16:9": "16:9",
        "9:16": "9:16",
        "4:3": "4:3",
        "3:4": "3:4"
    }
    aspect = aspect_ratio_map.get(request.aspect_ratio, "1:1")

    # Enhanced prompt with brand context (GOLD, BLACK, WHITE - NO BLU!)
    enhanced_prompt = f"""
    Create a professional marketing image for StudioCentOS digital agency.
    Content: {request.prompt}
    Style: {request.style} - modern, premium, tech-forward
    Brand colors: GOLD (#D4AF37), BLACK (#0A0A0A), WHITE (#FAFAFA)
    NO blue colors! Only gold, black, and white palette.
    High quality, 8k resolution, sharp focus.
    DO NOT include text, logos, or watermarks.
    """.strip()

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    payload = {
        "contents": [{
            "parts": [{"text": enhanced_prompt}]
        }],
        "generationConfig": {
            "response_modalities": ["IMAGE"],
            "image_config": {
                "aspect_ratio": aspect
            }
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=60)) as response:
            if response.status == 200:
                data = await response.json()
                # Extract base64 image from response
                image_data = data["candidates"][0]["content"]["parts"][0]["inline_data"]["data"]
                image_bytes = base64.b64decode(image_data)

                # Save and return
                return await save_image(image_bytes, "gemini-nano-banana", "gemini-2.5-flash-image")
            else:
                error_text = await response.text()
                raise Exception(f"Gemini API error: {response.status} - {error_text}")
```

---

### FASE 2: Aggiungere Nano Banana Pro per Asset Professionali

#### 2.1 Nuovo Endpoint `/image/generate/professional`

**Use case:** Quando il cliente vuole asset di alta qualità (loghi, brochure, infografiche)

```python
class ProfessionalImageRequest(BaseModel):
    prompt: str
    resolution: str = Field(default="1K", description="1K, 2K, or 4K")
    aspect_ratio: str = Field(default="1:1")
    use_google_search: bool = Field(default=False, description="Ground with real-time data")
    reference_images: List[str] = Field(default=[], description="URLs to reference images (max 14)")

@router.post("/image/generate/professional", response_model=ImageGenerationResponse)
async def generate_professional_image(request: ProfessionalImageRequest):
    """
    🍌⭐ Generate professional asset using Gemini 3 Pro Image (Nano Banana Pro).

    Features:
    - 4K resolution support
    - Thinking mode for optimal composition
    - Google Search grounding for real-time data
    - Multi-image reference support (up to 14)
    - Professional text rendering
    """
    # Implementation using gemini-3-pro-image-preview
```

#### 2.2 Use Cases Specifici

**Infografica con Dati Real-time:**
```python
prompt = "Create a vibrant infographic showing today's weather forecast for Salerno, Italy. 5-day outlook with temperature, conditions, and what to wear each day. Modern, clean design with gold accents."
use_google_search = True
resolution = "2K"
aspect_ratio = "16:9"
```

**Logo Generation:**
```python
prompt = 'Create a modern, minimalist logo with the text "FastBank" in a bold, tech-forward font. Gold (#D4AF37) on black background. Include a subtle geometric element representing speed and finance.'
resolution = "4K"
aspect_ratio = "1:1"
```

**Product Mockup con Character Consistency:**
```python
prompt = "Professional group photo of these people in a modern office, celebrating success with laptop showing FastBank dashboard"
reference_images = [
    "https://studiocentos.it/team/person1.jpg",
    "https://studiocentos.it/team/person2.jpg",
    "https://studiocentos.it/team/person3.jpg"
]
resolution = "2K"
aspect_ratio = "16:9"
```

---

### FASE 3: Integrare Imagen 4 per Fotorealismo

#### 3.1 Nuovo Endpoint `/image/generate/photorealistic`

**Use case:** Product photography, advertising, portraits

```python
class PhotorealisticImageRequest(BaseModel):
    prompt: str
    style: str = Field(default="standard", description="standard, ultra, fast")
    aspect_ratio: str = Field(default="1:1")
    number_of_images: int = Field(default=4, ge=1, le=4)

@router.post("/image/generate/photorealistic", response_model=List[ImageGenerationResponse])
async def generate_photorealistic_images(request: PhotorealisticImageRequest):
    """
    📸 Generate photorealistic images using Imagen 4.

    Best for:
    - Product photography
    - Food photography
    - Real estate renders
    - Advertising campaigns
    """
    # Implementation using imagen-4.0-generate-001 (or ultra/fast)
```

**Endpoint Imagen:**
```
POST https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict
```

---

### FASE 4: Upgrade Frontend Marketing Hub

#### 4.1 Aggiungere Opzioni Avanzate in AIMarketing.tsx

**Nel tab "Content" (Content Generation):**

```typescript
// Aggiungere selector per provider
const [imageProvider, setImageProvider] = useState<'auto' | 'gemini' | 'professional' | 'photorealistic'>('auto');
const [imageResolution, setImageResolution] = useState<'1K' | '2K' | '4K'>('1K');
const [useGoogleSearch, setUseGoogleSearch] = useState(false);

// UI Components da aggiungere:
<Select value={imageProvider} onValueChange={setImageProvider}>
  <SelectItem value="auto">🍌 Auto (Fast & Free)</SelectItem>
  <SelectItem value="gemini">🍌 Nano Banana (Standard)</SelectItem>
  <SelectItem value="professional">🍌⭐ Nano Banana Pro (4K, Thinking)</SelectItem>
  <SelectItem value="photorealistic">📸 Imagen 4 (Fotorealismo)</SelectItem>
</Select>

{imageProvider === 'professional' && (
  <>
    <Select value={imageResolution} onValueChange={setImageResolution}>
      <SelectItem value="1K">1K (1024px)</SelectItem>
      <SelectItem value="2K">2K (2048px)</SelectItem>
      <SelectItem value="4K">4K (4096px) - Premium</SelectItem>
    </Select>

    <Switch
      checked={useGoogleSearch}
      onCheckedChange={setUseGoogleSearch}
      label="🌐 Use Google Search (Real-time data)"
    />
  </>
)}
```

#### 4.2 Aggiungere Badge Informativi

```typescript
{imageProvider === 'professional' && (
  <Alert>
    <Sparkles className="h-4 w-4" />
    <AlertTitle>Professional Mode Active</AlertTitle>
    <AlertDescription>
      Using Gemini 3 Pro Image with Thinking mode for optimal composition.
      {useGoogleSearch && " Grounded with real-time Google Search data."}
    </AlertDescription>
  </Alert>
)}
```

---

## 🎨 MARKETING AGENT INTEGRATION

### Come gli Agenti Usano le Nuove API

#### Agent: Social Media Manager
```python
# Scenario: Creare 10 varianti per A/B testing Instagram
async def create_social_variants(topic: str, num_variants: int = 10):
    """Generate multiple social media image variants using Nano Banana"""
    prompts = [
        f"{topic} - modern minimalist design, gold accents",
        f"{topic} - vibrant creative composition, tech-forward",
        f"{topic} - professional photography style, dark premium",
        # ... more variations
    ]

    tasks = [
        generate_image(ImageGenerationRequest(
            prompt=p,
            aspect_ratio="1:1",  # Instagram square
            provider="gemini",
            style="modern"
        ))
        for p in prompts[:num_variants]
    ]

    images = await asyncio.gather(*tasks)
    return images
```

#### Agent: Lead Finder con Visual Intelligence
```python
# Scenario: Creare infografica personalizzata per lead
async def create_personalized_infographic(lead_data: dict):
    """Create infographic with real-time data using Nano Banana Pro"""
    prompt = f"""
    Create a professional infographic for {lead_data['company_name']} showing:
    - Current market trends in {lead_data['industry']}
    - Growth opportunities for 2025
    - Key digital transformation metrics
    Modern, premium design with gold accents on dark background.
    """

    image = await generate_professional_image(
        ProfessionalImageRequest(
            prompt=prompt,
            resolution="2K",
            aspect_ratio="16:9",
            use_google_search=True  # Get real-time market data!
        )
    )

    return image
```

#### Agent: Content Calendar Automation
```python
# Scenario: Pre-generate tutte le immagini per campagna mensile
async def generate_monthly_campaign_images(campaign: dict):
    """Batch generate all images for monthly social campaign"""
    dates = campaign['scheduled_dates']
    topics = campaign['topics']

    # Use Nano Banana for fast batch generation
    images = []
    for i, (date, topic) in enumerate(zip(dates, topics)):
        img = await generate_image(ImageGenerationRequest(
            prompt=f"Social media post about {topic} for digital marketing agency. Modern, professional, gold and black theme.",
            aspect_ratio="1:1",
            provider="gemini",  # Fast, free
            style="professional"
        ))

        # Save to calendar post
        await save_calendar_image(date, img, topic)
        images.append(img)

        # Rate limiting (if needed)
        if i % 10 == 0:
            await asyncio.sleep(1)

    return images
```

---

## 💰 COSTI E BUDGETING

### Confronto Pricing

| Provider | Tipo | Costo | Velocità | Qualità | Use Case |
|----------|------|-------|----------|---------|----------|
| **Pollinations** (attuale) | FREE | $0 | ⚡⚡⚡ Velocissimo | ⭐⭐⭐ Buono | Prototyping, batch |
| **Nano Banana** (Gemini 2.5 Flash) | FREE/Token | $0.04/immagine* | ⚡⚡ Veloce | ⭐⭐⭐⭐ Ottimo | Social media, A/B test |
| **Nano Banana Pro** (Gemini 3 Pro) | Token | $0.04-0.06/immagine* | ⚡ Medio | ⭐⭐⭐⭐⭐ Eccellente | Asset professionali |
| **Imagen 4 Standard** | Per-image | $0.04/immagine | ⚡⚡⚡ Veloce | ⭐⭐⭐⭐⭐ Fotorealismo | Product photography |
| **Imagen 4 Ultra** | Per-image | $0.12/immagine | ⚡ Lento | ⭐⭐⭐⭐⭐⭐ Massimo | Advertising premium |

*Calcolato: $30/1M tokens ÷ 1290 tokens per immagine = ~$0.039 per immagine

### Budget Stimato Mensile

**Scenario: 1000 immagini/mese**

```
Opzione A - Mix Smart (Raccomandato):
- 600 immagini Pollinations (FREE) = $0
- 300 immagini Nano Banana (social) = $12
- 100 immagini Nano Banana Pro (clienti) = $5
TOTALE: ~$17/mese
```

```
Opzione B - Premium Quality:
- 500 immagini Nano Banana = $20
- 400 immagini Imagen 4 Standard = $16
- 100 immagini Imagen 4 Ultra = $12
TOTALE: ~$48/mese
```

```
Opzione C - All Google (Balanced):
- 1000 immagini Nano Banana = $40/mese
TOTALE: $40/mese
```

**FREE TIER:** Google offre quota gratuita giornaliera per Nano Banana!
- Quota stimata: ~50-100 immagini/giorno FREE
- = ~1500-3000 immagini/mese GRATIS

---

## ⚙️ VARIABILI AMBIENTE DA AGGIUNGERE

### Backend `.env`
```bash
# Google AI API (per Gemini Nano Banana)
GOOGLE_AI_API_KEY=your_api_key_here

# Feature flags
ENABLE_GEMINI_IMAGE_GENERATION=true
ENABLE_PROFESSIONAL_IMAGE_MODE=true
ENABLE_IMAGEN_4=false  # Optional: attivare solo se serve fotorealismo estremo

# Rate limiting
GEMINI_IMAGE_DAILY_LIMIT=1000
GEMINI_PRO_MONTHLY_LIMIT=500
```

### AI Microservice `.env`
```bash
GOOGLE_AI_API_KEY=your_api_key_here
IMAGE_PROVIDER_PRIORITY=gemini,pollinations,huggingface
```

---

## 📊 METRICHE DA TRACCIARE

### Database: Tabella `image_generation_metrics`

```sql
CREATE TABLE image_generation_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    provider VARCHAR(50),  -- 'pollinations', 'gemini', 'gemini-pro', 'imagen4'
    model VARCHAR(100),
    prompt_length INT,
    generation_time_ms INT,
    resolution VARCHAR(20),
    aspect_ratio VARCHAR(10),
    cost_usd DECIMAL(10, 4),
    success BOOLEAN,
    error_message TEXT,
    admin_id INT REFERENCES admin_users(id),
    used_for VARCHAR(50)  -- 'social_post', 'client_asset', 'email_campaign', etc
);
```

### Dashboard Metriche

**KPIs da monitorare:**
- Immagini generate/giorno per provider
- Costo totale mensile
- Tempo medio generazione
- Success rate per provider
- Utilizzo per use case (social, client, email)
- Quota FREE tier utilizzata/disponibile

---

## 🚀 ROADMAP IMPLEMENTAZIONE

### SPRINT 1 (Questa Settimana) - MVP
- [ ] Aggiungere Nano Banana come provider in `marketing.py`
- [ ] Testare generazione base con GOOGLE_AI_API_KEY
- [ ] Configurare fallback chain: Gemini → Pollinations → HuggingFace
- [ ] Deploy e test in produzione
- [ ] Verificare FREE tier quotas

### SPRINT 2 (Prossima Settimana) - Professional Mode
- [ ] Implementare endpoint `/image/generate/professional`
- [ ] Aggiungere Nano Banana Pro con Thinking
- [ ] Testare Google Search grounding
- [ ] Testare multi-image reference
- [ ] Frontend: aggiungere selector provider in AIMarketing.tsx

### SPRINT 3 (Tra 2 Settimane) - Imagen 4 (Optional)
- [ ] Implementare endpoint `/image/generate/photorealistic`
- [ ] Integrare Imagen 4 Standard/Ultra/Fast
- [ ] A/B testing qualità vs costo
- [ ] Decidere se tenere Imagen o solo Gemini

### SPRINT 4 (Tra 3 Settimane) - Agent Integration
- [ ] Integrare API nei Marketing Agents
- [ ] Batch generation per Content Calendar
- [ ] Personalized infographics per Lead Finder
- [ ] A/B variants generator per Social Media Manager

### SPRINT 5 (Mese 2) - Analytics & Optimization
- [ ] Implementare metriche tracking
- [ ] Dashboard usage analytics
- [ ] Cost optimization strategies
- [ ] Quality benchmarking

---

## ❓ FAQ & TROUBLESHOOTING

### Q: Whisk, Pomelli, Flow non sono disponibili?
**A:** Esatto! Sono tools sperimentali interni Google, NON API pubbliche. Non ci sono endpoint disponibili. Usa invece Nano Banana (Gemini) o Imagen.

### Q: Quale API scegliere?
**A:**
- **Social media veloce:** Nano Banana (FREE, fast)
- **Asset professionali clienti:** Nano Banana Pro (4K, Thinking)
- **Product photography:** Imagen 4 Standard
- **Advertising premium:** Imagen 4 Ultra

### Q: Come funziona il FREE tier?
**A:** Google offre quota giornaliera gratuita per Nano Banana. Una volta esaurita, passa a token-based pricing ($0.04/immagine). Quota esatta non documentata pubblicamente, stimata ~50-100 img/giorno.

### Q: Pensando mode rallenta troppo?
**A:** Sì, Nano Banana Pro con Thinking è più lento (genera 2-3 immagini interim). Usa solo per asset critici. Per batch generation usa Nano Banana standard.

### Q: Google Search grounding costa extra?
**A:** No, incluso nel costo token. Ma usa con parsimonia perché aumenta latenza.

### Q: SynthID watermark è visibile?
**A:** No, è un watermark digitale invisibile all'occhio umano, rilevabile solo con tools Google. Serve per AI-generated content tracking.

---

## 🎯 CONCLUSIONI E RACCOMANDAZIONI

### Strategia Consigliata

1. **Implementare Nano Banana subito** (FREE tier, upgrade immediato da Pollinations)
2. **Aggiungere Nano Banana Pro per clienti premium** (4K, Thinking, Google Search)
3. **Tenere Pollinations come fallback** (ultra-affidabile, 100% FREE)
4. **Valutare Imagen 4 dopo 1 mese** (se serve fotorealismo estremo)

### Benefici Attesi

✅ **Qualità:** Upgrade significativo vs Pollinations/FLUX
✅ **Velocità:** Latenza simile, FREE tier generoso
✅ **Flessibilità:** Multi-resolution, thinking, grounding
✅ **Costo:** FREE tier copre 80% use cases, token-based per resto
✅ **Features:** Text rendering, style transfer, multi-image compositing
✅ **Integrazione:** API Google unificate (già usiamo Gemini per chat)

### Next Steps Immediati

1. Ottenere GOOGLE_AI_API_KEY da Google AI Studio
2. Testare Nano Banana in dev environment
3. Implementare fallback chain
4. Deploy in produzione
5. Monitor metriche per 1 settimana
6. Decidere se procedere con Pro e Imagen

---

## 📚 RIFERIMENTI

- [Gemini Image Generation Docs](https://ai.google.dev/gemini-api/docs/image-generation)
- [Imagen 4 Docs](https://ai.google.dev/gemini-api/docs/imagen)
- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Cookbook Examples](https://github.com/google-gemini/cookbook)

---

**Documento compilato da:** AI Agent
**Ultima modifica:** 3 Dicembre 2025
**Status:** ✅ Pronto per implementazione
