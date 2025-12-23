# 🎯 Develop Monorepo - Global Rules

> **Server**: GCP VM `35.195.232.166`
> **Last Updated**: 2025-12-23

---

## 🔴 REGOLA D'ORO: SIAMO SUL SERVER!

⚠️ **NON NEGOZIABILE**: Siamo già sul server - **NO SSH MAI!**

Tutte le operazioni Docker vengono eseguite **DIRETTAMENTE**.

---

## � Project Structure

| Path | Purpose |
|------|---------|
| `/home/autcir_gmail_com/develop/` | Root monorepo |
| `services/` | Centralized infrastructure |
| `apps/iss/` | ISS WBS |
| `apps/ironRep/` | IronRep |
| `apps/studiocentos/` | StudioCentos |
| `apps/markettina/` | Markettina |

---

## � Centralized Services

| Service | Container | Config |
|---------|-----------|--------|
| PostgreSQL | `central-postgres` | User: `admin`, DBs per app |
| Redis | `central-redis` | DB 0-4 per app |
| Ollama | `central-ollama` | llama3.2, all-minilm |
| ChromaDB | `central-chromadb` | Vector storage |
| Nginx | `nginx-gateway` | SSL + Routing |

---

## � Deploy Commands

```bash
# Start everything
cd /home/autcir_gmail_com/develop
docker compose -f services/docker-compose.gateway.yml up -d
docker compose -f apps/iss/docker-compose.yml up -d
docker compose -f apps/ironRep/config/docker/docker-compose.prod.yml up -d
docker compose -f apps/studiocentos/config/docker/docker-compose.production.yml up -d
docker compose -f apps/markettina/config/docker/docker-compose.production.yml up -d
```

---

## 📤 Git Push Commands

```bash
# Push with message
make push-develop MSG="Fix bug"
make push-iss MSG="Update API"
make push-studiocentos MSG="New feature"
make push-markettina MSG="Styles"
make push-ironrep MSG="Refactor"

# Push ALL repos
make push-all MSG="Sync all"
```

---

## � Git Remotes

| Remote | Repo |
|--------|------|
| `origin` | develop.git |
| `iss-repo` | iss_ws.git |
| `studiocentos-repo` | studiocentos_ws.git |
| `markettina-repo` | markettina.git |
| `ironrep-repo` | ironrep.git |

---

## � Never Do

- ❌ SSH to server (already here)
- ❌ Hardcode API keys in committed files
- ❌ Use local Postgres/Redis (use central)
- ❌ Push without testing
- ❌ Edit .env files directly (use docker-compose env vars)

---

## ✅ Verification

```bash
# Health checks
docker ps --format "table {{.Names}}\t{{.Status}}"
curl -k https://markettina.com/health
curl -k https://innovazionesocialesalernitana.it/api/v1/health
```
