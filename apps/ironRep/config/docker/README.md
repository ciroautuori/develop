# 🐳 ironRep Docker Setup

Gestione completa dell'applicazione ironRep con Docker, supportando sia sviluppo locale che produzione.

## 🏗️ Architettura

- **Backend**: FastAPI + Python con `uv` (package manager veloce)
- **Frontend**: React + Vite
- **Redis**: Caching e sessioni
- **ChromaDB**: Vector database per RAG embeddings (persistente)

## 🚀 Quick Start - Development

### 1. Setup Iniziale

```bash
# Copia il template delle variabili d'ambiente
cp config/docker/.env.example config/docker/.env

# Modifica .env con le tue API keys
nano config/docker/.env
```

### 2. Avvia l'ambiente di sviluppo

```bash
# Usa lo script helper
./scripts/docker/dev.sh up

# OPPURE manualmente
cd config/docker
docker-compose up -d
```

### 3. Inizializza RAG Knowledge Base

```bash
# La prima volta, inizializza gli embeddings
./scripts/docker/dev.sh init-rag
```

### 4. Accedi alle applicazioni

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173
- **Redis**: localhost:6379

## 📝 Comandi Principali

### Script Helper (`./scripts/docker/dev.sh`)

```bash
# Start development
./scripts/docker/dev.sh up

# Stop services
./scripts/docker/dev.sh down

# Rebuild (dopo modifiche a dipendenze o Dockerfile)
./scripts/docker/dev.sh rebuild

# View logs
./scripts/docker/dev.sh logs          # Tutti i servizi
./scripts/docker/dev.sh logs backend  # Solo backend

# Shell access
./scripts/docker/dev.sh shell backend   # Backend shell
./scripts/docker/dev.sh shell frontend  # Frontend shell

# Restart services
./scripts/docker/dev.sh restart         # Tutti
./scripts/docker/dev.sh restart backend # Solo backend

# Initialize RAG
./scripts/docker/dev.sh init-rag

# Clean everything (ATTENZIONE: rimuove anche i volumi!)
./scripts/docker/dev.sh clean
```

### Comandi Docker Compose Diretti

```bash
cd config/docker

# Start
docker-compose up -d

# Stop
docker-compose down

# Rebuild dopo modifiche
docker-compose build --no-cache
docker-compose up -d

# Logs
docker-compose logs -f backend

# Status
docker-compose ps
```

## 🔧 Hot Reload

Entrambi backend e frontend supportano hot-reload:

- **Backend**: Modifica file in `apps/backend/src/` → uvicorn ricarica automaticamente
- **Frontend**: Modifica file in `apps/frontend/src/` → Vite HMR aggiorna il browser

## 💾 Persistenza Dati

I seguenti dati sono persistiti tramite Docker volumes:

- **chroma_data**: Embeddings ChromaDB (RAG knowledge base)
- **backend_data**: Database SQLite e file applicazione
- **redis_data**: Snapshot Redis

```bash
# Lista volumi
docker volume ls | grep ironrep

# Rimuovi volumi (ATTENZIONE: perdi tutti i dati!)
docker-compose down -v
```

## 🏭 Produzione

### Build Immagini

```bash
cd config/docker

# Build con versione
VERSION=1.0.0 docker-compose -f docker-compose.prod.yml build

# Tag per registry (opzionale)
docker tag ironrep-backend:1.0.0 your-registry.com/ironrep-backend:1.0.0
docker tag ironrep-frontend:1.0.0 your-registry.com/ironrep-frontend:1.0.0
```

### Deploy Produzione

```bash
# Assicurati che .env sia configurato correttamente
cp .env.example .env
nano .env  # Configura con credenziali produzione

# Start produzione
docker-compose -f docker-compose.prod.yml up -d

# Logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop
docker-compose -f docker-compose.prod.yml down
```

## 🐛 Troubleshooting

### Backend non si avvia

```bash
# Verifica logs
./scripts/docker/dev.sh logs backend

# Verifica API keys in .env
cat config/docker/.env

# Rebuild completo
./scripts/docker/dev.sh rebuild
```

### Frontend non si connette al backend

```bash
# Verifica che VITE_API_URL sia corretto in .env
# Verifica che il backend sia in running
docker-compose ps

# Restart frontend
./scripts/docker/dev.sh restart frontend
```

### ChromaDB vuoto / RAG non funziona

```bash
# Inizializza RAG knowledge base
./scripts/docker/dev.sh init-rag

# Verifica che i file in apps/backend/data/ esistano
ls -la apps/backend/data/

# Verifica volume ChromaDB
docker volume inspect ironrep_chroma_data
```

### Modifiche al codice non si riflettono

```bash
# Per modifiche alle dipendenze (requirements.txt, package.json)
./scripts/docker/dev.sh rebuild

# Per modifiche al codice, dovrebbe essere automatico
# Se non funziona, restart del servizio
./scripts/docker/dev.sh restart backend
```

## 📊 Monitoraggio

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Redis health
docker-compose exec redis redis-cli ping

# Container status
docker-compose ps
```

### Resource Usage

```bash
# Stats real-time
docker stats

# Logs specifici
docker-compose logs -f --tail=100 backend
```

## 🔐 Sicurezza

- **.env** non è mai committato (in .gitignore)
- Container backend usa **user non-root**
- Redis configurabile con password (prod)
- Nginx con security headers in produzione

## 📁 Struttura File

```
ironRep/
├── apps/
│   ├── backend/              # Python FastAPI
│   └── frontend/             # React Vite
├── config/
│   ├── docker/
│   │   ├── docker-compose.yml       # Development
│   │   ├── docker-compose.prod.yml  # Production
│   │   ├── .env.example             # Template
│   │   └── README.md                # Questa guida
│   └── services/
│       ├── backend/
│       │   └── Dockerfile           # Backend con uv
│       ├── frontend/
│       │   ├── Dockerfile           # Frontend multi-stage
│       │   └── nginx.conf           # Nginx config
│       └── redis/
│           └── redis.conf           # Redis config
├── scripts/
│   └── docker/
│       └── dev.sh                   # Helper script
└── .dockerignore
```

## 💡 Best Practices

1. **Sempre usa .env** per le configurazioni
2. **Rebuild dopo  modifiche a dipendenze** (requirements.txt, package.json)
3. **Fai backup dei volumi** prima di `docker-compose down -v`
4. **Verifica health** dopo ogni deploy
5. **Usa lo script helper** per operazioni comuni

## 🆘 Supporto

Per problemi:
1. Controlla logs: `./scripts/docker/dev.sh logs`
2. Verifica .env configurato correttamente
3. Prova rebuild: `./scripts/docker/dev.sh rebuild`
4. Clean start: `./scripts/docker/dev.sh clean && ./scripts/docker/dev.sh up`
