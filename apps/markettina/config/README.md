# ⚙️ markettina - Configuration

**Made in Italy** 🇮🇹 | Powered by [DataPizza AI](https://github.com/datapizza-labs/datapizza-ai)

Complete configuration for markettina enterprise framework.

---

## 📁 Directory Structure

```
config/
├── README.md                           # This file
│
├── docker/                             # Docker Compose configurations
│   ├── docker-compose-dev.yml          # Development stack (current)
│   ├── docker-compose.prod.yml         # Production deployment
│   ├── docker-compose.local-prod.yml   # Local production testing
│   └── docker-compose.simple.yml       # Minimal stack
│
├── env/                                # Environment variables
│   ├── development.env                 # Docker development
│   ├── local.env                       # Local development (outside Docker)
│   ├── production.env                  # Production configuration
│   ├── .env.backend.example            # Backend example
│   ├── .env.frontend.example           # Frontend example
│   ├── .env.mobile.example             # Mobile example
│   └── .env.ai.example                 # AI Microservice example
│
└── services/                           # Service-specific configurations
    ├── nginx/                          # Reverse Proxy & SSL
    ├── prometheus/                     # Monitoring & Metrics
    ├── backend/                        # Backend configs
    ├── frontend/                       # Frontend configs
    └── ai-service/                     # AI service configs
```

---

## 🚀 Quick Start

### Development with Docker

```bash
# 1. Use development environment
cp config/env/development.env docker/develop/.env

# 2. Start services
cd docker/develop
docker compose up -d

# 3. Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8001
# Traefik: http://localhost:9090
```

### Local Development (Outside Docker)

```bash
# 1. Start Docker services (DB + Redis only)
cd docker/develop
docker compose up -d postgres redis

# 2. Setup backend
cd apps/backend
cp ../../config/env/.env.backend.example .env
# Edit .env with your values
poetry install
poetry run uvicorn app.main:app --reload

# 3. Setup frontend
cd apps/frontend
cp ../../config/env/.env.frontend.example .env
npm install
npm run dev
```

---

## 📋 Environment Files

### development.env
Use with Docker Compose for development.
- Database: `postgres:5432` (internal Docker network)
- Redis: `redis:6379` (internal Docker network)

### local.env
Use for local development outside Docker.
- Database: `localhost:5435` (Docker exposed port)
- Redis: `localhost:6382` (Docker exposed port)

### production.env
Production configuration template.
- ⚠️ Update all secrets before deploying\!
- Use strong random keys (min 32 chars)
- Configure SSL/TLS
- Enable monitoring

---

## 🐳 Docker Compose Files

### docker-compose-dev.yml (Current)
Development stack with:
- PostgreSQL 16
- Redis 7
- Backend (FastAPI)
- Frontend (React)
- Traefik (Reverse Proxy)

**Ports**:
- Frontend: 3000
- Backend: 8001
- PostgreSQL: 5435
- Redis: 6382
- Traefik Web: 9080
- Traefik Dashboard: 9090

### docker-compose.prod.yml
Production-ready stack with:
- SSL/TLS termination
- Health checks
- Resource limits
- Logging
- Monitoring

---

## 🔐 Security

### Secrets Management

**Development**:
- Use `.env` files (gitignored)
- Weak passwords OK for local dev

**Production**:
- Use environment variables
- Use secrets management (Docker Secrets, Vault, etc.)
- Strong random keys (min 32 chars)
- Rotate secrets regularly

### Generate Secure Keys

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY
openssl rand -hex 32
```

---

## 📊 Services Configuration

### Backend
- **Port**: 8001 (external), 8000 (internal)
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Framework**: FastAPI 0.115+

### Frontend
- **Port**: 3000
- **Framework**: React 18
- **Build**: Vite 6.0

### AI Microservice
- **Port**: 8002
- **Framework**: FastAPI
- **Features**: RAG, Multi-agent, Auto-debug
- **Powered by**: DataPizza AI 🇮🇹

---

## �� Customization

### Add New Service

1. Create service directory in `config/services/`
2. Add Dockerfile if needed
3. Update `docker-compose-dev.yml`
4. Add environment variables
5. Document in this README

### Modify Ports

Edit `docker-compose-dev.yml`:
```yaml
ports:
  - "NEW_PORT:INTERNAL_PORT"
```

Update environment files accordingly.

---

## 📖 Documentation

- **Main README**: [../README.md](../README.md)
- **Contributing**: [../CONTRIBUTING.md](../CONTRIBUTING.md)
- **API Docs**: http://localhost:8001/docs (when running)

---

## 🇮🇹 Made in Italy

markettina is proudly **Made in Italy** and uses:
- [DataPizza AI](https://github.com/datapizza-labs/datapizza-ai) - Enterprise AI agents system

---

**Version**: 1.0.0  
**Last Updated**: 18 October 2025
