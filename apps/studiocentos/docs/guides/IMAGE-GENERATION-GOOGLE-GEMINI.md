# 🎨 Image Generation con Google Gemini (Nano Banana)

> **Data Implementazione**: 28 Novembre 2025
> **Status**: ✅ PRODUCTION READY
> **Costo**: 🆓 FREE (Google AI Studio)

---

## 📋 Overview

CV-Lab utilizza **Google Gemini 2.5 Flash Image** (nome in codice: **Nano Banana**) per la generazione di immagini AI. Questo modello è disponibile gratuitamente tramite Google AI Studio.

### Perché Google Gemini?

| Provider | Costo | Qualità | Velocità | Limiti |
|----------|-------|---------|----------|--------|
| ~~OpenAI DALL-E 3~~ | $0.04/img | ⭐⭐⭐⭐⭐ | Medio | Pagamento |
| ~~Stability AI~~ | $0.02/img | ⭐⭐⭐⭐ | Veloce | Pagamento |
| ~~HuggingFace SDXL~~ | Free | ⭐⭐⭐ | Lento | Rate limits |
| **Google Gemini** ✅ | **FREE** | ⭐⭐⭐⭐⭐ | **Veloce** | Generoso |

---

## 🔧 Configurazione

### API Key Required

```bash
# .env o Docker secrets
GOOGLE_API_KEY=AIzaSy...your-key-here
# oppure
GOOGLE_AI_API_KEY=AIzaSy...your-key-here
```

### Come Ottenere la Key

1. Vai su [Google AI Studio](https://aistudio.google.com/)
2. Accedi con account Google
3. Clicca "Get API Key" → "Create API Key"
4. Copia la key e aggiungila all'environment

---

## 🏗️ Architettura

### File Principale
```
apps/ai-service/app/domain/marketing/auto_poster/platform_apis/image_generator.py
```

### Flusso di Generazione

```
┌─────────────────┐
│   User Request  │
│ "Modern website"│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ImageGenerator  │
│ _generate_google│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Google Gemini  │
│ 2.5-flash-image │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Base64 Image   │
│   Response      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Save to File   │
│ /media/generated│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Return URL    │
│ https://cv-lab. │
│ pro/api/v1/...  │
└─────────────────┘
```

---

## 📡 API Endpoint

### Modello Utilizzato

```
gemini-2.5-flash-image
```

### Endpoint Google

```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={API_KEY}
```

### Payload Request

```json
{
  "contents": [{
    "parts": [{
      "text": "Generate an image: [prompt enhanced]"
    }]
  }],
  "generationConfig": {
    "temperature": 1.0,
    "topP": 0.95,
    "topK": 40
  }
}
```

### Response Structure

```json
{
  "candidates": [{
    "content": {
      "parts": [{
        "inlineData": {
          "mimeType": "image/png",
          "data": "base64_encoded_image_data..."
        }
      }]
    }
  }]
}
```

---

## 🎯 Modelli Disponibili (Novembre 2025)

Query per listare modelli image:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY" | \
  jq '.models[] | select(.name | contains("image")) | .name'
```

### Risultato:
```
"models/gemini-2.5-flash-image-preview"
"models/gemini-2.5-flash-image"          ← USATO
"models/gemini-3-pro-image-preview"
"models/imagen-4.0-generate-preview-06-06"
"models/imagen-4.0-ultra-generate-preview-06-06"
"models/imagen-4.0-generate-001"
```

---

## 💻 Implementazione Codice

### Classe ImageGenerator

```python
async def _generate_google(
    self,
    request: ImageGenerationRequest,
    size: str
) -> ImageGenerationResponse:
    """Generate with Google Gemini 2.5 Flash Image (Nano Banana) - FREE!"""
    import base64

    google_key = self.google_key
    if not google_key:
        raise ValueError("GOOGLE_API_KEY not configured")

    gen_start = datetime.utcnow()
    enhanced_prompt = self._enhance_prompt(request.prompt, request.style)

    # Google Gemini 2.5 Flash Image API
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={google_key}"

    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [{
            "parts": [{"text": f"Generate an image: {enhanced_prompt}"}]
        }],
        "generationConfig": {
            "temperature": 1.0,
            "topP": 0.95,
            "topK": 40
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, headers=headers, json=payload,
                                timeout=aiohttp.ClientTimeout(total=120)) as response:
            if response.status != 200:
                text = await response.text()
                raise Exception(f"Google Gemini Image API error: {response.status} - {text}")

            result = await response.json()

            # Extract image from response
            candidates = result.get("candidates", [])
            parts = candidates[0].get("content", {}).get("parts", [])

            for part in parts:
                if "inlineData" in part:
                    image_data = base64.b64decode(part["inlineData"]["data"])
                    break

            # Save image to file
            image_path = Path(f"media/generated/gemini_{int(time.time())}.png")
            image_path.parent.mkdir(parents=True, exist_ok=True)

            with open(image_path, 'wb') as f:
                f.write(image_data)

            base_url = os.getenv('BASE_URL', 'https://cv-lab.pro')

            return ImageGenerationResponse(
                image_url=f"{base_url}/api/v1/ai-service/media/generated/{image_path.name}",
                image_id=f"gemini_{int(datetime.utcnow().timestamp())}",
                prompt_used=enhanced_prompt,
                generation_time=(datetime.utcnow() - gen_start).total_seconds(),
                metadata={
                    "provider": "google",
                    "model": "gemini-2.5-flash-image (Nano Banana)",
                    "cost": "FREE",
                    "size": size,
                    "quality": "high"
                }
            )
```

### Provider Priority

```python
# In __init__
self.providers = [
    ImageProvider.HUGGINGFACE,   # Maps to Google Gemini (FREE!)
    ImageProvider.OPENAI          # Fallback PAID (DALL-E 3)
]
```

---

## 🧪 Test

### Via cURL

```bash
curl -X POST "https://cv-lab.pro/api/v1/ai-service/auto-poster/posts" \
  -H "X-API-Key: cv-lab-internal-key" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "CV-Lab AI Portfolio!",
    "platforms": ["linkedin"],
    "image_prompt": "Modern portfolio website with AI technology"
  }'
```

### Response Attesa

```json
{
  "post": {
    "id": "post_1764322268_system",
    "content": "CV-Lab AI Portfolio!",
    "image_url": "https://cv-lab.pro/api/v1/ai-service/media/generated/gemini_1764322268.png",
    "status": "pending_approval"
  },
  "estimated_reach": 800,
  "best_time_to_post": "2025-11-29T10:00:00"
}
```

### Health Check

```bash
curl "https://cv-lab.pro/api/v1/ai-service/auto-poster/health" \
  -H "X-API-Key: cv-lab-internal-key"
```

```json
{
  "status": "healthy",
  "platforms": {
    "twitter": false,
    "linkedin": false,
    "image_generator": true  ← ✅
  }
}
```

---

## ⚠️ Troubleshooting

### Errore: 400 Invalid MIME Type

```
allowed mimetypes are `text/plain`, `application/json`...
```

**Causa**: `responseMimeType: "image/png"` non è supportato.

**Fix**: Rimuovi `responseMimeType` dal payload. L'immagine viene ritornata come `inlineData` base64.

### Errore: 404 Not Found

**Causa**: Modello sbagliato o endpoint errato.

**Fix**: Usa `gemini-2.5-flash-image` (non `gemini-2.0-flash-exp`).

### Errore: URL Validation Failed

```
Input should be a valid URL, relative URL without a base
```

**Causa**: `image_url` deve essere URL completo, non path relativo.

**Fix**:
```python
image_url=f"https://cv-lab.pro/api/v1/ai-service/media/generated/{filename}"
```

---

## 📊 Limiti e Quote

| Metrica | Limite Free Tier |
|---------|------------------|
| Requests/min | 60 |
| Requests/day | 1500 |
| Image size | Up to 4K |
| Timeout | 120s |

---

## 🔄 Fallback Chain

```
1. Google Gemini (gemini-2.5-flash-image) ← PRIMARY
   ↓ (se fallisce)
2. OpenAI DALL-E 3 ← FALLBACK (richiede OPENAI_API_KEY)
```

---

## 📁 File Generati

Le immagini vengono salvate in:
```
/app/media/generated/gemini_{timestamp}.png
```

E servite via URL:
```
https://cv-lab.pro/api/v1/ai-service/media/generated/gemini_{timestamp}.png
```

---

## 🔗 Riferimenti

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini Image Generation Docs](https://ai.google.dev/gemini-api/docs/image-generation)
- [Nano Banana Announcement](https://developers.googleblog.com/en/imagen-3-arrives-in-the-gemini-api/)

---

## 📝 Changelog

| Data | Versione | Modifiche |
|------|----------|-----------|
| 2025-11-28 | 1.0.0 | Implementazione iniziale con Google Gemini |
| 2025-11-28 | 1.0.1 | Fix modello: `gemini-2.0-flash-exp` → `gemini-2.5-flash-image` |
| 2025-11-28 | 1.0.2 | Fix URL validation per Pydantic |

---

*Documentazione generata automaticamente - CV-Lab AI Team*
