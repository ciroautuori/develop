# 🤖 LLM Configuration Rules

## Priority Chain

| Priority | Provider | Host | Free | Rate Limit |
|----------|----------|------|------|------------|
| 1️⃣ PRIMARY | Ollama | central-ollama:11434 | ✅ | Unlimited |
| 2️⃣ FALLBACK | Groq | api.groq.com | ✅ | 100k/day |
| 3️⃣ LAST | Google Gemini | generativelanguage.googleapis.com | ✅ | Soft limit |

## Ollama Configuration

```yaml
USE_OLLAMA: true
OLLAMA_HOST: central-ollama
OLLAMA_PORT: 11434
OLLAMA_MODEL: llama3.2:latest
OLLAMA_EMBED_MODEL: all-minilm
```

## Models Available on Ollama

| Model | Size | Speed | Use Case |
|-------|------|-------|----------|
| llama3.2:latest | 2GB | ~2s/response | Chat, generation |
| all-minilm | 45MB | ~0.3s | Embeddings (384 dim) |

## API Endpoints

```bash
# Health check
curl http://central-ollama:11434/api/tags

# Generate
curl http://central-ollama:11434/api/chat -d '{
  "model": "llama3.2:latest",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": false
}'

# Embeddings
curl http://central-ollama:11434/api/embeddings -d '{
  "model": "all-minilm",
  "prompt": "Your text here"
}'
```

## Code Integration

### StudioCentos (ai_microservice)
```python
from app.core.llm.unified_llm import get_unified_llm

llm = get_unified_llm()
result = await llm.generate(prompt="Hello", system_prompt="You are helpful")
```

### IronRep
```python
from src.infrastructure.ai.llm_service import LLMService

service = LLMService()  # Auto-initializes Ollama + fallbacks
result = await service.generate(prompt="Hello", system_prompt="You are helpful")
```

## Fallback Behavior

1. Check if Ollama available (5s timeout)
2. If yes → use Ollama
3. If no → try Groq with key rotation
4. If Groq fails → try Google Gemini
5. If all fail → raise exception

## Performance Benchmarks (Current Hardware)

- CPU: Intel Xeon 2.8GHz (8 threads)
- RAM: 32GB
- GPU: None

| Operation | Time |
|-----------|------|
| Ollama chat | ~2-5s |
| Ollama embedding | ~0.3s |
| Groq chat | ~1-2s |

*Ultimo aggiornamento: 2025-12-23*
