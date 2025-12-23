# 🐳 Docker Setup Guide - StudiocentOS

**Last Updated**: November 5, 2025  
**Version**: 1.0.0

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Services](#services)
4. [Port Mapping](#port-mapping)
5. [Configuration](#configuration)
6. [Commands](#commands)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

StudiocentOS uses Docker Compose for orchestrating multiple services:
- **NGINX** - Reverse proxy & load balancer
- **Backend API** - FastAPI application
- **AI Microservice** - AI agents & RAG system
- **Frontend** - React SPA
- **PostgreSQL** - Database
- **Redis** - Cache & session store

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    NGINX (Port 80)                      │
│              Reverse Proxy & Load Balancer              │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Frontend   │  │  Backend API │  │ AI Service   │
│  (React 19)  │  │  (FastAPI)   │  │  (FastAPI)   │
│   Port 3000  │  │   Port 8002  │  │   Port 8001  │
└──────────────┘  └──────────────┘  └──────────────┘
                         │                  │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
            ┌──────────────┐          ┌──────────────┐
            │  PostgreSQL  │          │    Redis     │
            │   Port 5433  │          │   Port 6380  │
            └──────────────┘          └──────────────┘
```

---

## 📦 Services

### 1. NGINX - Reverse Proxy

**Image**: `nginx:alpine`  
**Container**: `studiocentos-nginx`  
**Ports**: `80:80`, `443:443`

**Routing**:
- `/` → Frontend (React SPA)
- `/api/*` → Backend API
- `/ai/*` → AI Microservice
- `/docs` → Backend Swagger UI
- `/ai-docs` → AI Service Swagger UI

**Features**:
- Rate limiting (API: 100 req/s, AI: 50 req/s)
- Gzip compression
- Security headers
- Static asset caching
- WebSocket support

### 2. Backend API

**Build**: `config/docker/dockerfiles/backend.Dockerfile`  
**Container**: `studiocentos-api`  
**Ports**: `8002:8000` (external:internal)

**Features**:
- FastAPI 0.115+
- SQLAlchemy 2.0 ORM
- Alembic migrations
- JWT authentication
- Prometheus metrics

**Health Check**: `http://localhost:8002/health`

### 3. AI Microservice

**Build**: `config/docker/dockerfiles/ai_microservice.Dockerfile`  
**Container**: `studiocentos-ai`  
**Ports**: `8001:8001`

**Features**:
- Marketing agents
- RAG system (ChromaDB)
- Multi-provider AI (OpenAI, Groq, etc.)
- Document processing

**Health Check**: `http://localhost:8001/health`

### 4. Frontend

**Build**: `config/docker/dockerfiles/frontend.Dockerfile`  
**Container**: `studiocentos-web`  
**Ports**: `3000:80`

**Features**:
- React 19
- Vite build
- TailwindCSS
- shadcn/ui components

### 5. PostgreSQL

**Image**: `postgres:16-alpine`  
**Container**: `studiocentos-db`  
**Ports**: `5433:5432`

**Configuration**:
- Database: `studiocentos`
- User: `studiocentos`
- Password: `studiocentos2025` (change in production!)

### 6. Redis

**Image**: `redis:7-alpine`  
**Container**: `studiocentos-cache`  
**Ports**: `6380:6379`

**Configuration**:
- Password: `studiocentos2025` (change in production!)
- Persistence: Enabled

---

## 🔌 Port Mapping

### External Ports (Host → Container)

| Service | External | Internal | URL |
|---------|----------|----------|-----|
| NGINX | 80 | 80 | http://localhost |
| NGINX HTTPS | 443 | 443 | https://localhost |
| Backend | 8002 | 8000 | http://localhost:8002 |
| AI Service | 8001 | 8001 | http://localhost:8001 |
| Frontend | 3000 | 80 | http://localhost:3000 |
| PostgreSQL | 5433 | 5432 | localhost:5433 |
| Redis | 6380 | 6379 | localhost:6380 |

### Why Different Ports?

Ports are changed to avoid conflicts with existing services:
- **PostgreSQL**: 5433 instead of 5432 (conflicts with arch-gcp-postgres)
- **Redis**: 6380 instead of 6379 (prevention)
- **Backend**: 8002 instead of 8000 (conflicts with arch-gcp-backend)

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in `config/docker/`:

```bash
# PostgreSQL
POSTGRES_USER=studiocentos
POSTGRES_PASSWORD=studiocentos2025
POSTGRES_DB=studiocentos

# Redis
REDIS_PASSWORD=studiocentos2025

# Backend
DATABASE_URL=postgresql://studiocentos:studiocentos2025@postgres:5432/studiocentos
REDIS_URL=redis://:studiocentos2025@redis:6379/0
SECRET_KEY=your-secret-key-here

# AI Service
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key
```

### Docker Compose Files

- **`docker-compose.yml`** - Production configuration
- **`docker-compose.dev.yml`** - Development overrides (if needed)

---

## 🎮 Commands

### Basic Operations

```bash
cd /home/ciroautuori/Scrivania/studiocentos/config/docker

# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# View status
docker-compose ps

# View logs
docker-compose logs -f

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

### Build Commands

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build ai_microservice
docker-compose build frontend

# Build without cache
docker-compose build --no-cache

# Build and start
docker-compose up -d --build
```

### Service Management

```bash
# Restart specific service
docker-compose restart backend
docker-compose restart nginx

# Stop specific service
docker-compose stop backend

# Start specific service
docker-compose start backend

# Remove specific service
docker-compose rm backend
```

### Logs & Debugging

```bash
# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Logs for specific service
docker-compose logs backend
docker-compose logs -f ai_microservice

# Last 100 lines
docker-compose logs --tail=100 backend

# Logs since timestamp
docker-compose logs --since 2025-11-05T10:00:00
```

### Execute Commands in Containers

```bash
# Enter backend container
docker exec -it studiocentos-api bash

# Run migrations
docker exec -it studiocentos-api alembic upgrade head

# Enter PostgreSQL
docker exec -it studiocentos-db psql -U studiocentos -d studiocentos

# Enter Redis CLI
docker exec -it studiocentos-cache redis-cli -a studiocentos2025
```

### Health Checks

```bash
# Check all containers
docker ps --format "table {{.Names}}\t{{.Status}}"

# Test endpoints
curl http://localhost/health
curl http://localhost/api/v1/health
curl http://localhost/ai/health
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs <service_name>

# Check container status
docker ps -a

# Inspect container
docker inspect <container_name>

# Remove and recreate
docker-compose rm <service_name>
docker-compose up -d <service_name>
```

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :80
sudo lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Database Connection Issues

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Test connection
docker exec -it studiocentos-db psql -U studiocentos -d studiocentos

# Restart PostgreSQL
docker-compose restart postgres
```

### Build Failures

```bash
# Clean Docker system
docker system prune -a

# Remove all containers and volumes
docker-compose down -v

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### Network Issues

```bash
# Inspect network
docker network inspect studiocentos

# Recreate network
docker-compose down
docker network rm studiocentos
docker-compose up -d
```

---

## 📚 Next Steps

- **[Development Guide](../guides/development.md)** - Development workflow
- **[Deployment Guide](../guides/deployment.md)** - Production deployment
- **[Troubleshooting](troubleshooting.md)** - Common issues

---

## 🆘 Need Help?

- 📖 **[Docker Documentation](https://docs.docker.com/)**
- 🐛 **[GitHub Issues](https://github.com/yourusername/studiocentos/issues)**
- 📧 **Email**: ciro@studiocentos.it
