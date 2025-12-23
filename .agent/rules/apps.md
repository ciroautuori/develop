# 📱 Application Rules

## ISS (Innovazione Sociale Salernitana)
- **Domain**: innovazionesocialesalernitana.it
- **Path**: `apps/iss/`
- **Repo**: github.com/ciroautuori/iss_ws.git
- **Backend Port**: 8000
- **Frontend Port**: 3000
- **Database**: `iss_wbs` on central-postgres
- **Redis DB**: 0
- **Docker**: `apps/iss/docker-compose.yml`

## IronRep
- **Domain**: ironrep.it
- **Path**: `apps/ironRep/`
- **Repo**: github.com/ciroautuori/ironrep.git
- **Backend Port**: 8000
- **Frontend Port**: 80
- **Database**: `ironrep_db` on central-postgres
- **Redis DB**: 4
- **Docker**: `apps/ironRep/config/docker/docker-compose.prod.yml`
- **LLM**: Ollama PRIMARY + Groq/Gemini fallback

## StudioCentos
- **Domain**: studiocentos.it
- **Path**: `apps/studiocentos/`
- **Repo**: github.com/ciroautuori/studiocentos_ws.git
- **Backend Port**: 8000
- **Frontend Port**: 80
- **AI Microservice Port**: 8001
- **Database**: `studiocentos` on central-postgres
- **Redis DB**: 2
- **Docker**: `apps/studiocentos/config/docker/docker-compose.production.yml`
- **Features**: AI content generation, RAG, Custom HuggingFace model

## Markettina
- **Domain**: markettina.com
- **Path**: `apps/markettina/`
- **Repo**: github.com/ciroautuori/markettina.git
- **Backend Port**: 8000
- **Frontend Port**: 80
- **Database**: `markettina` on central-postgres
- **Redis DB**: 3
- **Docker**: `apps/markettina/config/docker/docker-compose.production.yml`

## Push Commands
```bash
make push-iss MSG="message"
make push-ironrep MSG="message"
make push-studiocentos MSG="message"
make push-markettina MSG="message"
```

*Ultimo aggiornamento: 2025-12-23*
