# 🏗️ Centralized Services Architecture

> **Server**: GCP VM `35.195.232.166`
> **Last Updated**: 2025-12-23

---

## 📦 Repository Structure

```
develop/                          ← MAIN REPO (github.com/ciroautuori/develop.git)
├── services/                     ← Centralized Infrastructure
│   ├── docker-compose.gateway.yml
│   ├── nginx/conf.d/            ← Per-domain configs
│   └── init-scripts/            ← DB init SQL
├── apps/
│   ├── iss/                     ← github.com/ciroautuori/iss_ws.git
│   ├── ironRep/                 ← github.com/ciroautuori/ironrep.git
│   ├── studiocentos/            ← github.com/ciroautuori/studiocentos_ws.git
│   └── markettina/              ← github.com/ciroautuori/markettina.git
├── Makefile                     ← Deploy & Git commands
└── .agent/                      ← Workflows & Memory
```

---

## 🐳 Central Stack (docker-compose.gateway.yml)

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| **PostgreSQL** | `central-postgres` | 5432 | All app databases |
| **Redis** | `central-redis` | 6379 | Cache (DB 0-4 per app) |
| **Ollama** | `central-ollama` | 11434 | LLM (llama3.2, all-minilm) |
| **ChromaDB** | `central-chromadb` | 8000 | Vector store |
| **Nginx** | `nginx-gateway` | 80, 443 | Reverse proxy + SSL |
| **Certbot** | `certbot-gateway` | - | SSL cert renewal |

---

## 🌐 Applications

| App | Domain | Backend | Frontend | DB |
|-----|--------|---------|----------|-----|
| **ISS** | innovazionesocialesalernitana.it | iss-backend:8000 | iss-frontend:3000 | iss_wbs |
| **IronRep** | ironrep.it | ironrep-backend:8000 | ironrep-frontend:80 | ironrep_db |
| **StudioCentos** | studiocentos.it | studiocentos-backend:8000 | studiocentos-frontend:80 | studiocentos |
| **Markettina** | markettina.com | markettina-backend:8000 | markettina-frontend:80 | markettina |

---

## 🔌 Connection Strings

```bash
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://admin:central_admin_password_2025@central-postgres:5432/{db_name}

# Redis (per app)
REDIS_URL=redis://:central_redis_password_2025@central-redis:6379/{0-4}

# Ollama
OLLAMA_HOST=central-ollama
OLLAMA_PORT=11434
OLLAMA_MODEL=llama3.2:latest
```

---

## 🚀 Docker Network

All containers connect via: **`web_gateway`** (external bridge network)

---

## 📋 Quick Commands

```bash
# Start everything
make deploy-all

# Check status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Logs
docker logs -f nginx-gateway
docker logs -f iss-backend

# Git push to all repos
make push-all MSG="Sync update"
```
