# 🎯 Global Agent Rules - Develop Monorepo

> **REGOLE NON NEGOZIABILI - CONSULTA SEMPRE PRIMA DI OGNI AZIONE**

---

## 🔴 PRINCIPI FONDAMENTALI

| Regola | Descrizione |
|--------|-------------|
| ❌ **FULL DELIVERY** | Implementazione completa e accurata |
| ❌ **ZERO ERRORI** | Massima precisione in ogni operazione |
| ❌ **ZERO ALLUCINAZIONI** | Solo informazioni verificate e reali |
| ❌ **ZERO COMPORTAMENTI IMPULSIVI** | Ogni azione deve essere ragionata |

---

## 🖥️ AMBIENTE - SIAMO GIÀ SUL SERVER!

⚠️ NON NEGOZIABILE: Siamo sul server GCP 35.195.232.166
NO SSH MAI - Tutte le operazioni sono DIRETTE!

**Percorso root**: `/home/autcir_gmail_com/develop/`

---

## 📁 STRUTTURA MONOREPO

```
develop/
├── services/                 # Infrastruttura centralizzata
│   ├── docker-compose.gateway.yml
│   └── nginx/conf.d/         # Config per dominio
├── apps/
│   ├── iss/                  → github.com/ciroautuori/iss_ws.git
│   ├── ironRep/              → github.com/ciroautuori/ironrep.git
│   ├── studiocentos/         → github.com/ciroautuori/studiocentos_ws.git
│   └── markettina/           → github.com/ciroautuori/markettina.git
├── .agent/                   # Memory + Rules + Workflows
├── Makefile                  # Comandi globali
└── .gitignore
```

---

## 🐳 STACK CENTRALIZZATO

| Servizio | Container | Porta | Uso |
|----------|-----------|-------|-----|
| **PostgreSQL** | central-postgres | 5432 | Tutti i DB |
| **Redis** | central-redis | 6379 | Cache (DB 0-4) |
| **Ollama** | central-ollama | 11434 | LLM PRIMARY |
| **ChromaDB** | central-chromadb | 8000 | Vector store |
| **Nginx** | nginx-gateway | 80,443 | Reverse proxy |

---

## 🤖 LLM FALLBACK CHAIN

1. OLLAMA (central-ollama:11434) - PRIMARY, FREE, locale
2. GROQ (cloud) - FALLBACK, FREE, 100k tokens/day
3. GEMINI (cloud) - ULTIMO RESORT, FREE

```yaml
USE_OLLAMA: true
OLLAMA_HOST: central-ollama
OLLAMA_PORT: 11434
OLLAMA_MODEL: llama3.2:latest
```

---

## 📤 GIT PUSH COMMANDS

```bash
make push-iss MSG="Fix bug"
make push-studiocentos MSG="New feature"
make push-markettina MSG="Styles"
make push-ironrep MSG="Refactor"
make push-all MSG="Sync all"
```

---

## 🚀 DEPLOY COMMANDS

```bash
docker compose -f services/docker-compose.gateway.yml up -d
docker compose -f apps/iss/docker-compose.yml up -d
docker compose -f apps/ironRep/config/docker/docker-compose.prod.yml up -d
docker compose -f apps/studiocentos/config/docker/docker-compose.production.yml up -d
docker compose -f apps/markettina/config/docker/docker-compose.production.yml up -d
```

---

## ❌ COSA NON FARE MAI

- SSH al server (siamo già qui!)
- Hardcode secrets (usa os.getenv())
- Postgres/Redis locale (usa central-*)
- Push senza test
- File .env in git (solo .env.example)
- Magic numbers (usa costanti)
- Codice duplicato (astrai in funzione)
- TODO/FIXME (implementa subito)

---

*Ultimo aggiornamento: 2025-12-23*
