# 🔌 Port Mapping Reference - markettina

## 📊 Port Allocation Strategy

Per evitare conflitti con i container **arch-gcp-*** già in esecuzione, le porte sono state riassegnate.

---

## 🚀 Development (Local)

Quando esegui i servizi **senza Docker** (con `uv run` o `pnpm dev`):

```
Backend API:      http://localhost:8000
AI Microservice:  http://localhost:8001
Frontend:         http://localhost:5173
PostgreSQL:       localhost:5432 (usa arch-gcp-postgres)
Redis:            localhost:6379 (usa arch-gcp o locale)
```

---

## 🐳 Docker Compose (Production)

Quando esegui `docker-compose up` con **markettina** stack:

### External Ports (Host → Container)

```
Service              External Port    Internal Port    URL
─────────────────────────────────────────────────────────────────
Backend API          8002            8000             http://localhost:8002
AI Microservice      8001            8001             http://localhost:8001
Frontend             3000            80               http://localhost:3000
PostgreSQL           5433            5432             localhost:5433
Redis                6380            6379             localhost:6380
Traefik Web          8090            80               http://localhost:8090
Traefik Secure       8443            443              https://localhost:8443
Traefik Dashboard    8091            8080             http://localhost:8091
```

### API Documentation

```
Backend Swagger UI:     http://localhost:8002/docs
Backend ReDoc:          http://localhost:8002/redoc
AI Service Swagger UI:  http://localhost:8001/docs
AI Service ReDoc:       http://localhost:8001/redoc
```

---

## ⚠️ Port Conflicts Avoided

### Existing arch-gcp-* Containers

```
Container Name         Port Used    Conflict Avoided
─────────────────────────────────────────────────────
arch-gcp-backend       8000         ✅ markettina-api usa 8002
arch-gcp-postgres      5432         ✅ markettina-db usa 5433
arch-gcp-frontend      5173         ✅ markettina-web usa 3000
```

### Common System Ports

```
Port    Service              Conflict Avoided
──────────────────────────────────────────────
80      HTTP                 ✅ Traefik usa 8090
443     HTTPS                ✅ Traefik usa 8443
5432    PostgreSQL           ✅ markettina-db usa 5433
6379    Redis                ✅ markettina-cache usa 6380
8000    Common API           ✅ markettina-api usa 8002
8080    Common Dashboard     ✅ Traefik usa 8091
```

---

## 🔍 Verifica Porte in Uso

### Check container attivi

```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

### Check porte sistema

```bash
# Linux
sudo lsof -i :8000
sudo lsof -i :8001
sudo lsof -i :5432

# Oppure con netstat
netstat -tuln | grep -E ':(8000|8001|8002|5432|5433|6379|6380)'
```

### Kill processo su porta specifica

```bash
# Trova PID
sudo lsof -t -i:8000

# Kill processo
kill -9 $(sudo lsof -t -i:8000)
```

---

## 🔄 Switch tra Ambienti

### Scenario 1: Solo Development (No Docker)

```bash
# Usa arch-gcp containers per DB
# Backend su 8000, AI su 8001, Frontend su 5173
cd apps/backend && uv run uvicorn app.main:app --reload --port 8000
cd apps/ai_microservice && uv run uvicorn app.main:app --reload --port 8001
cd apps/frontend && pnpm dev
```

**Accesso**:
- Backend: http://localhost:8000/docs
- AI: http://localhost:8001/docs
- Frontend: http://localhost:5173

---

### Scenario 2: Full Docker Stack

```bash
# Stop arch-gcp containers per liberare porte
docker stop arch-gcp-backend arch-gcp-postgres arch-gcp-frontend

# Start markettina stack
cd config/docker
docker-compose up -d
```

**Accesso**:
- Backend: http://localhost:8002/docs
- AI: http://localhost:8001/docs
- Frontend: http://localhost:3000
- Traefik: http://localhost:8091

---

### Scenario 3: Hybrid (Dev + arch-gcp DB)

```bash
# Mantieni arch-gcp-postgres attivo
# Stop solo arch-gcp-backend
docker stop arch-gcp-backend

# Backend locale usa arch-gcp-postgres:5432
cd apps/backend
export DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"
uv run uvicorn app.main:app --reload --port 8000
```

---

## 📝 Environment Variables

### Development (.env)

```bash
# Backend usa arch-gcp-postgres
DATABASE_URL=postgresql://markettina:password@localhost:5432/markettina
REDIS_URL=redis://:password@localhost:6379/0

# AI Microservice URL per backend
AI_MICROSERVICE_URL=http://localhost:8001
```

### Docker (.env)

```bash
# Backend usa markettina-db interno
DATABASE_URL=postgresql://markettina:password@postgres:5432/markettina
REDIS_URL=redis://:password@redis:6379/0

# AI Microservice URL per backend (network interno)
AI_MICROSERVICE_URL=http://ai_microservice:8001
```

---

## 🚨 Troubleshooting

### Errore: "Address already in use"

```bash
# 1. Identifica processo
sudo lsof -i :8000

# 2. Opzioni:
#    a) Kill processo
kill -9 <PID>

#    b) Usa porta diversa
uvicorn app.main:app --port 8003

#    c) Stop container Docker
docker stop <container_name>
```

### Errore: "Connection refused" tra servizi

```bash
# Verifica network Docker
docker network inspect markettina

# Verifica DNS interno
docker exec markettina-api ping postgres
docker exec markettina-api ping ai_microservice

# Usa nomi servizio, non localhost
# ✅ CORRECT: http://ai_microservice:8001
# ❌ WRONG:   http://localhost:8001 (in Docker)
```

### Database connection failed

```bash
# Development: usa porta esterna
DATABASE_URL=postgresql://user:pass@localhost:5433/db

# Docker: usa nome servizio e porta interna
DATABASE_URL=postgresql://user:pass@postgres:5432/db
```

---

## 📚 References

- **Docker Compose**: `config/docker/docker-compose.yml`
- **Apps README**: `apps/README.md`
- **Main README**: `README.md`
- **Setup Guide**: `docs/SETUP_AND_DEPLOYMENT_GUIDE.md`
