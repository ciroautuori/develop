# 🐳 Docker - Centralized Configuration

**Purpose**: All Docker configurations centralized here (SINGLE SOURCE OF TRUTH)  
**Status**: ✅ Production Ready  
**Last Updated**: 2025-11-25

---

## 📁 Structure

```
config/docker/
├── README.md                        # This file
├── docker-compose.yml               # Development (infra only)
├── docker-compose.production.yml    # Production (full stack)
├── .env.production                  # Environment variables (gitignored)
│
├── dockerfiles/                     # All Dockerfiles centralized
│   ├── backend.Dockerfile           # FastAPI backend
│   ├── frontend.Dockerfile          # React frontend
│   └── ai_microservice.Dockerfile   # AI microservice
│
├── nginx/                           # Docker-specific Nginx configs
│   └── nginx.conf                   # Nginx for Docker environment
│
├── letsencrypt/                     # SSL certificates (gitignored)
│   ├── live/                        # Active certificates
│   └── renewal/                     # Renewal configuration
│
└── certbot_www/                     # Certbot challenge files
```

---

## 🚀 Quick Start

### Development Mode (Local Services)

In development, only infrastructure services run in Docker (PostgreSQL, Redis).  
Applications (Backend, Frontend, AI) run locally for hot-reload.

```bash
# From project root
make dev-up          # Start PostgreSQL + Redis
make dev-ps          # Check status

# Then run services locally:
cd apps/backend && uvicorn app.main:app --reload --port 8002
cd apps/frontend && pnpm dev --port 3000
cd apps/ai_microservice && uvicorn app.main:app --reload --port 8001
```

**Development Ports**:
- Backend API: http://localhost:8002
- Frontend: http://localhost:3000
- AI Service: http://localhost:8001
- PostgreSQL: localhost:5433
- Redis: localhost:6380

### Production Mode (Full Docker Stack)

In production, ALL services run containerized with Nginx reverse proxy + SSL.

```bash
# From project root
make prod-deploy     # Full deploy with SSL setup
# or step by step:
make prod-build      # Build all images
make prod-up         # Start all containers
make prod-ps         # Check status
```

**Production Services**:
- HTTPS: https://studiocentos.it
- API: https://studiocentos.it/api/v1
- AI: https://studiocentos.it/ai
- PostgreSQL: internal (port 5432)
- Redis: internal (port 6379)

---

## 📦 Dockerfiles

### Backend (`dockerfiles/backend.Dockerfile`)

**Base**: Python 3.12-slim  
**App**: FastAPI + SQLAlchemy + Alembic  
**Port**: 8002 (internal)

**Build**:
```bash
# From project root
docker build -f config/docker/dockerfiles/backend.Dockerfile \
  -t studiocentos/backend:latest .
```

### Frontend (`dockerfiles/frontend.Dockerfile`)

**Base**: Node 20 (build) + Nginx Alpine (runtime)  
**App**: React 19 + Vite + TypeScript  
**Port**: 80 (internal)

**Build**:
```bash
docker build -f config/docker/dockerfiles/frontend.Dockerfile \
  -t studiocentos/frontend:latest .
```

### AI Microservice (`dockerfiles/ai_microservice.Dockerfile`)

**Base**: Python 3.12-slim  
**App**: FastAPI + LLM integrations  
**Port**: 8001 (internal)

**Build**:
```bash
docker build -f config/docker/dockerfiles/ai_microservice.Dockerfile \
  -t studiocentos/ai-microservice:latest .
```

---

## 🔐 Environment Variables

All production secrets are stored in `.env.production` (this directory).

**Setup**:
```bash
# The symlink in project root points here
ls -la ../../.env.production
# -> config/docker/.env.production
```

**Required variables** (see .env.production for full list):
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `REDIS_PASSWORD`
- `JWT_SECRET`
- `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`, `GROQ_API_KEY`

---

## 🛠️ Make Commands

All Docker operations should be done via Makefile from project root:

```bash
# Development
make dev-up          # Start dev infrastructure
make dev-down        # Stop dev infrastructure
make dev-logs        # View dev logs

# Production
make prod-build      # Build all images
make prod-up         # Start production
make prod-down       # Stop production
make prod-logs       # View production logs
make prod-ps         # Check status

# Utilities
make clean           # Clean volumes and images
make help            # Show all commands
```

---

## 📊 Port Mapping

| Service      | Dev Port | Prod Port | Internal Port |
|--------------|----------|-----------|---------------|
| Frontend     | 3000     | 80/443    | 80            |
| Backend      | 8002     | -         | 8002          |
| AI Service   | 8001     | -         | 8001          |
| PostgreSQL   | 5433     | 5433      | 5432          |
| Redis        | 6380     | 6380      | 6379          |
| Nginx        | -        | 80/443    | 80/443        |

---

## 🔗 Related Documentation

- [Services Configuration](../services/README.md) - Service-specific configs
- [Makefile](../../Makefile) - All available commands
- [Deploy Guide](../../docs/guides/DEPLOYMENT.md) - Full deployment guide
