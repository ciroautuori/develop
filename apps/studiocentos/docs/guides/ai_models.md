# 🤖 AI Models & Provider Configuration

> **Documentazione completa per l'utilizzo gratuito di modelli AI enterprise**

## 📋 Overview

Il sistema StudioCentOS utilizza un'architettura **multi-provider** con fallback automatico per garantire massima disponibilità dei servizi AI senza costi.

### Provider Supportati

| Provider | Status | Costo | Modello | Velocità |
|----------|--------|-------|---------|----------|
| **GROQ** | 🔴 Blocked* | FREE | Llama 3, Mixtral | ⚡⚡⚡ Ultra-fast |
| **HuggingFace** | 🟢 Active | FREE | Llama 3.2-3B | ⚡⚡ Fast |
| **Gemini** | 🟡 Rate Limited | FREE | Gemini Flash | ⚡⚡ Fast |
| **OpenRouter** | 🔴 Needs Credits | Paid | Multiple | ⚡⚡ Fast |
| **Ollama** | ⚪ Local | FREE | Any local | ⚡ Local |

> *GROQ account temporaneamente bloccato (contattare supporto GROQ)

---

## 🔑 API Keys Configuration

### HuggingFace (PRIMARY - WORKING)

```bash
# Token gratuito da https://huggingface.co/settings/tokens
# Permessi: "Make calls to Inference Providers"
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HUGGINGFACE_TOKEN_2=hf_yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy  # backup
```

**Come ottenere:**
1. Registrati su [huggingface.co](https://huggingface.co/join)
2. Vai su Settings → Access Tokens
3. Crea token "Fine-grained" con permesso "Make calls to Inference Providers"
4. Il tier gratuito include accesso a molti modelli via `router.huggingface.co`

### GROQ (5 Keys - Currently Blocked)

```bash
# 5 API keys per rotazione automatica
# Ottieni da https://console.groq.com/keys
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_API_KEY_2=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_API_KEY_3=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_API_KEY_4=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_API_KEY_5=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Vantaggi GROQ:**
- Inferenza ultra-veloce (hardware LPU)
- Supporta Llama 3, Mixtral, Gemma
- Rate limit generoso sul free tier

### Gemini (Google)

```bash
# Da https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Limiti Free Tier:**
- 15 RPM (requests per minute)
- 1M tokens/mese
- Quota resetta ogni minuto

### OpenRouter (Optional - Paid)

```bash
# Da https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Note:**
- Richiede acquisto crediti ($5 minimo)
- Accesso a 100+ modelli
- Utile come fallback premium

---

## 🏗️ Architettura AI Service

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI Microservice (Port 8001)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Fallback Chain                        │   │
│  │                                                          │   │
│  │   GROQ ──▶ HuggingFace ──▶ Gemini ──▶ OpenRouter ──▶ Ollama │
│  │    ❌        ✅            ⏳          💰           ⚪       │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Support    │  │  Marketing   │  │     RAG      │          │
│  │   Chatbot    │  │   Content    │  │   Documents  │          │
│  │              │  │              │  │              │          │
│  │ /support/chat│  │ /marketing/  │  │ /rag/search  │          │
│  │              │  │ content/gen  │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📡 Endpoint API

### Support Chatbot

```bash
# Chat con AI
curl -X POST http://localhost:8001/api/v1/support/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-api-key-change-in-production" \
  -d '{
    "message": "Ciao, mi puoi aiutare?",
    "context": "cliente interessato a sviluppo web"
  }'

# Response
{
  "response": "Ciao! Sono l'assistente AI di StudioCentOS...",
  "confidence": 90,
  "sentiment": "neutral",
  "provider": "huggingface",
  "processing_time": 2500
}
```

### Marketing Content Generator

```bash
# Genera contenuti marketing
curl -X POST http://localhost:8001/api/v1/marketing/content/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-api-key-change-in-production" \
  -d '{
    "type": "social",           # blog, social, ad, video
    "topic": "Servizi AI",
    "tone": "professional",     # professional, friendly, creative
    "platform": "linkedin"      # optional
  }'

# Response
{
  "content": "🚀 Trasforma il tuo business con l'AI...",
  "metadata": {
    "type": "social",
    "tone": "professional",
    "platform": "linkedin",
    "topic": "Servizi AI"
  },
  "provider": "huggingface"
}
```

### Content Types

| Type | Description | Output |
|------|-------------|--------|
| `blog` | Articolo SEO-optimized | Titolo + 3-4 paragrafi + CTA |
| `social` | Post social media | Testo + hashtag + emoji |
| `ad` | Copy pubblicitaria | Headline + body + CTA |
| `video` | Script video | Hook + contenuto + CTA |

---

## 🔧 Configurazione Files

### `config/docker/.env.production`

```bash
# === AI PROVIDERS ===

# HuggingFace - PRIMARY (FREE)
HUGGINGFACE_TOKEN=hf_xxxxx
HUGGINGFACE_TOKEN_2=hf_yyyyy

# GROQ - 5 Keys for rotation (FREE)
GROQ_API_KEY=gsk_xxxxx
GROQ_API_KEY_2=gsk_xxxxx
GROQ_API_KEY_3=gsk_xxxxx
GROQ_API_KEY_4=gsk_xxxxx
GROQ_API_KEY_5=gsk_xxxxx

# Gemini (FREE with rate limits)
GOOGLE_API_KEY=AIzaSyxxxxx

# OpenRouter (Optional - Paid)
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Ollama (Local)
OLLAMA_BASE_URL=http://host.docker.internal:11434

# RAG - ChromaDB
CHROMADB_HOST=chromadb
CHROMADB_PORT=8000
```

### `apps/ai_microservice/app/core/config.py`

```python
class Settings(BaseSettings):
    # HuggingFace
    huggingface_token: str = ""
    huggingface_token_2: str = ""

    # GROQ (5 keys)
    groq_api_key: str = ""
    groq_api_key_2: str = ""
    groq_api_key_3: str = ""
    groq_api_key_4: str = ""
    groq_api_key_5: str = ""

    @property
    def groq_api_keys_list(self) -> list:
        """Lista di tutte le GROQ API keys disponibili"""
        keys = [
            self.groq_api_key,
            self.groq_api_key_2,
            self.groq_api_key_3,
            self.groq_api_key_4,
            self.groq_api_key_5,
        ]
        return [k for k in keys if k]
```

---

## 🌐 HuggingFace Router (New API)

HuggingFace ha deprecato `api-inference.huggingface.co` e ora usa `router.huggingface.co`.

### Formato OpenAI-Compatible

```python
# Endpoint
api_url = "https://router.huggingface.co/v1/chat/completions"

# Headers
headers = {
    "Authorization": f"Bearer {HUGGINGFACE_TOKEN}",
    "Content-Type": "application/json"
}

# Payload (OpenAI format)
payload = {
    "model": "meta-llama/Llama-3.2-3B-Instruct",
    "messages": [
        {"role": "system", "content": "Sei un assistente..."},
        {"role": "user", "content": "Ciao!"}
    ],
    "max_tokens": 500,
    "temperature": 0.7
}
```

### Modelli Gratuiti Disponibili

| Modello | Parametri | Use Case |
|---------|-----------|----------|
| `meta-llama/Llama-3.2-3B-Instruct` | 3B | Chat, assistenza |
| `meta-llama/Llama-3.2-1B-Instruct` | 1B | Chat veloce |
| `meta-llama/Llama-3.1-8B-Instruct` | 8B | Compiti complessi |
| `Qwen/Qwen2.5-7B-Instruct` | 7B | Multilingua |
| `google/gemma-3-27b-it` | 27B | Alta qualità |
| `HuggingFaceTB/SmolLM3-3B` | 3B | Efficiente |

### Provider Selection

```python
# Auto-select (default)
"model": "meta-llama/Llama-3.2-3B-Instruct"

# Più veloce
"model": "meta-llama/Llama-3.2-3B-Instruct:fastest"

# Più economico
"model": "meta-llama/Llama-3.2-3B-Instruct:cheapest"
```

---

## 🔄 Fallback Logic

```python
# apps/ai_microservice/app/domain/support/chatbot.py

fallback_order = ["groq", "huggingface", "gemini", "openrouter", "ollama"]

async def get_response(self, message: str):
    for provider in self.fallback_order:
        try:
            return await self._call_provider(provider, message)
        except Exception as e:
            logger.warning(f"Provider {provider} failed: {e}")
            continue

    # All failed - return fallback message
    return {
        "response": "Mi dispiace, sto avendo difficoltà tecniche...",
        "provider": "fallback"
    }
```

---

## 📊 Monitoring & Health

### Health Check

```bash
curl http://localhost:8001/health | jq .
```

```json
{
  "status": "healthy",
  "providers": {
    "groq": "available (5 keys)",
    "huggingface": "available",
    "gemini": "available",
    "openrouter": "available",
    "ollama": "available"
  },
  "fallback_order": ["groq", "huggingface", "gemini", "openrouter", "ollama"]
}
```

### Provider Status

```bash
curl http://localhost:8001/api/v1/support/providers \
  -H "Authorization: Bearer dev-api-key-change-in-production" | jq .
```

---

## 💰 Costi Effettivi (November 2025)

| Provider | Free Tier | Limite | Costo Extra |
|----------|-----------|--------|-------------|
| HuggingFace | ✅ Generoso | Rate limited | $0.00 |
| GROQ | ✅ 30 RPM | 500K tokens/day | $0.00 |
| Gemini | ✅ 15 RPM | 1M tokens/month | $0.00 |
| OpenRouter | ❌ | - | $0.0001-0.01/1K tokens |
| Ollama | ✅ Unlimited | Local only | $0.00 (hardware) |

**Costo mensile stimato: $0.00** 🎉

---

## 🚀 Quick Start

### 1. Verifica servizi attivi

```bash
docker ps | grep -E "ai|backend|frontend"
```

### 2. Test chatbot

```bash
curl -X POST http://localhost:8001/api/v1/support/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-api-key-change-in-production" \
  -d '{"message": "Ciao!"}'
```

### 3. Test marketing

```bash
curl -X POST http://localhost:8001/api/v1/marketing/content/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-api-key-change-in-production" \
  -d '{"type": "social", "topic": "AI Services", "tone": "professional"}'
```

### 4. Accedi al backoffice

- URL: `http://localhost:3000/admin/ai-marketing`
- Features: Chat AI, Content Generator, Provider Status

---

## 🔐 Security Notes

1. **API Keys**: Non committare mai le API keys nel repo
2. **Rate Limiting**: Implementato lato provider
3. **Auth**: Tutti gli endpoint richiedono `Authorization: Bearer <token>`
4. **CORS**: Configurato per domini specifici in produzione

---

## 📝 Changelog

### v1.0.0 (November 2025)
- ✅ Multi-provider fallback system
- ✅ HuggingFace router.huggingface.co integration
- ✅ 5 GROQ API keys rotation
- ✅ Marketing content generator (blog, social, ad, video)
- ✅ Support chatbot with context
- ✅ Admin backoffice AI page
- ✅ Full Italian language support

---

## 📚 References

- [HuggingFace Inference Providers](https://huggingface.co/docs/inference-providers)
- [GROQ Documentation](https://console.groq.com/docs)
- [Gemini API](https://ai.google.dev/docs)
- [OpenRouter Docs](https://openrouter.ai/docs)
