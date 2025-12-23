# 🐳 Infrastructure Rules

## Central Stack

### PostgreSQL (central-postgres:5432)
- User: `admin`
- Password: `central_admin_password_2025`
- Databases per app:
  - `iss_wbs` (ISS)
  - `ironrep_db` (IronRep)
  - `studiocentos` (StudioCentos)
  - `markettina` (Markettina)

### Redis (central-redis:6379)
- Password: `central_redis_password_2025`
- DB allocation:
  - DB 0: ISS
  - DB 1: IronRep
  - DB 2: StudioCentos
  - DB 3: Markettina
  - DB 4: Reserved

### Ollama (central-ollama:11434)
- Models loaded:
  - `llama3.2:latest` (2GB) - Primary LLM
  - `all-minilm` (45MB) - Embeddings
- Priority: PRIMARY (before cloud APIs)

### ChromaDB (central-chromadb:8000)
- Used for vector storage
- No auth required

### Nginx Gateway (nginx-gateway:80,443)
- SSL termination
- Domains:
  - innovazionesocialesalernitana.it → ISS
  - ironrep.it → IronRep
  - studiocentos.it → StudioCentos
  - markettina.com → Markettina

## Network
- `web_gateway` (external bridge)
- All containers MUST connect to this network

## Health Checks
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep healthy
curl http://localhost:5432  # PostgreSQL (via container)
curl http://localhost:6379  # Redis (via container)
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:8000/api/v1/heartbeat  # ChromaDB
```

*Ultimo aggiornamento: 2025-12-23*
