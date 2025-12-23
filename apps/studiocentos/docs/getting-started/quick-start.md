# ⚡ Quick Start Guide - StudiocentOS

**Last Updated**: November 5, 2025  
**Time to Complete**: 10 minutes

---

## 🎯 Goal

Get StudiocentOS running locally in **under 10 minutes** using Docker.

---

## 📋 Prerequisites

- ✅ [Installation Guide](installation.md) completed
- ✅ Docker & Docker Compose installed
- ✅ PostgreSQL & Redis running
- ✅ Environment variables configured

---

## 🚀 Quick Start (Docker)

### Option 1: Automated Script (Recommended)

```bash
cd /home/ciroautuori/Scrivania/studiocentos/docs/scripts
chmod +x quick-start-docker.sh
./quick-start-docker.sh
```

This will:
1. Start all Docker containers
2. Run database migrations
3. Seed initial data
4. Open browser to http://localhost

**Estimated Time**: 5 minutes

### Option 2: Manual Docker Compose

```bash
cd /home/ciroautuori/Scrivania/studiocentos/config/docker

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

---

## 🔍 Verify Services

### Check Running Containers

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Expected output:
```
NAMES                   STATUS              PORTS
studiocentos-nginx      Up 2 minutes        0.0.0.0:80->80/tcp
studiocentos-api        Up 2 minutes        0.0.0.0:8002->8000/tcp
studiocentos-ai         Up 2 minutes        0.0.0.0:8001->8001/tcp
studiocentos-web        Up 2 minutes        0.0.0.0:3000->80/tcp
studiocentos-db         Up 2 minutes        0.0.0.0:5433->5432/tcp
studiocentos-cache      Up 2 minutes        0.0.0.0:6380->6379/tcp
```

### Test Endpoints

```bash
# NGINX Health Check
curl http://localhost/health

# Backend API
curl http://localhost/api/v1/health

# AI Microservice
curl http://localhost/ai/health

# Frontend
curl http://localhost
```

---

## 🌐 Access Applications

### Web Interfaces

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost | React SPA |
| **Backend API Docs** | http://localhost/docs | Swagger UI |
| **Backend ReDoc** | http://localhost/redoc | Alternative API docs |
| **AI Service Docs** | http://localhost/ai-docs | AI API documentation |

### Direct Service Access (Development)

| Service | URL | Port |
|---------|-----|------|
| Backend API | http://localhost:8002 | 8002 |
| AI Microservice | http://localhost:8001 | 8001 |
| Frontend | http://localhost:3000 | 3000 |
| PostgreSQL | localhost:5433 | 5433 |
| Redis | localhost:6380 | 6380 |

---

## 🗄️ Database Setup

### Run Migrations

```bash
# Enter backend container
docker exec -it studiocentos-api bash

# Inside container
alembic upgrade head

# Exit container
exit
```

### Seed Initial Data

```bash
# Enter backend container
docker exec -it studiocentos-api bash

# Run seed script
python scripts/seed_portfolio.py

# Exit
exit
```

---

## 🧪 Test the System

### Test Backend API

```bash
# Health check
curl http://localhost/api/v1/health

# Get portfolio projects
curl http://localhost/api/v1/portfolio/public/projects | jq

# Get services
curl http://localhost/api/v1/portfolio/public/services | jq

# Get booking availability
curl "http://localhost/api/v1/booking/calendar/availability?year=2025&month=11" | jq
```

### Test AI Microservice

```bash
# Health check
curl http://localhost/ai/health

# Test AI endpoint (requires API key)
curl -X POST http://localhost/ai/marketing/content/create \
  -H "Content-Type: application/json" \
  -d '{"type": "blog_post", "topic": "AI in Business"}'
```

### Test Frontend

Open browser: http://localhost

You should see the StudiocentOS landing page.

---

## 🛑 Stop Services

```bash
cd /home/ciroautuori/Scrivania/studiocentos/config/docker

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

---

## 🔄 Restart Services

```bash
cd /home/ciroautuori/Scrivania/studiocentos/config/docker

# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart ai_microservice
docker-compose restart frontend
```

---

## 📊 View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f ai_microservice
docker-compose logs -f nginx

# Last 100 lines
docker-compose logs --tail=100 backend
```

---

## 🐛 Common Issues

### Port Already in Use

```bash
# Check what's using the port
sudo lsof -i :80
sudo lsof -i :8000
sudo lsof -i :8001

# Kill the process
kill -9 <PID>

# Or use different ports in docker-compose.yml
```

### Database Connection Failed

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Build Failed

```bash
# Clean build
docker-compose down
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

---

## 📚 Next Steps

Now that you have StudiocentOS running:

1. **[Development Guide](../guides/development.md)** - Start developing
2. **[API Documentation](../api/)** - Explore API endpoints
3. **[Features Guide](../features/)** - Learn about features
4. **[Deployment Guide](../guides/deployment.md)** - Deploy to production

---

## 🆘 Need Help?

- 📖 **[Troubleshooting Guide](troubleshooting.md)**
- 🐛 **[GitHub Issues](https://github.com/yourusername/studiocentos/issues)**
- 💬 **[Discussions](https://github.com/yourusername/studiocentos/discussions)**
- 📧 **Email**: ciro@studiocentos.it
