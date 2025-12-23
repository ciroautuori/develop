# 🤖 CV-Lab AI Microservice

Unified AI service for Frontend, Mobile, and Backend.

## Quick Start

```bash
# Install dependencies
poetry install

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run service
poetry run python -m app.main
```

## API Endpoints

- `/health` - Health check
- `/api/v1/rag/*` - RAG services
- `/api/v1/support/*` - Customer support
- `/api/v1/debug/*` - Debug services
- `/api/v1/cv/*` - CV intelligence
- `/api/v1/marketing/*` - Marketing agents
- `/docs` - Swagger documentation (dev only)
- `/metrics` - Prometheus metrics

## Docker

```bash
docker build -t cv-lab-ai-service .
docker run -p 8001:8001 --env-file .env cv-lab-ai-service
```

## Documentation

See `/docs/architecture/AI-MICROSERVICE-DESIGN.md` for complete architecture.
