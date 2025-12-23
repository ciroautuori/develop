# 🐛 Troubleshooting Guide - StudiocentOS

**Last Updated**: November 5, 2025

---

## 📋 Table of Contents

1. [Installation Issues](#installation-issues)
2. [Docker Issues](#docker-issues)
3. [Database Issues](#database-issues)
4. [Network Issues](#network-issues)
5. [Build Issues](#build-issues)
6. [Runtime Issues](#runtime-issues)

---

## 🔧 Installation Issues

### UV Installation Failed

**Problem**: `curl -LsSf https://astral.sh/uv/install.sh | sh` fails

**Solution**:
```bash
# Try manual installation
wget https://astral.sh/uv/install.sh
chmod +x install.sh
./install.sh

# Or use pip
pip install uv
```

### pnpm Installation Failed

**Problem**: `npm install -g pnpm` fails

**Solution**:
```bash
# Use corepack (recommended)
corepack enable
corepack prepare pnpm@latest --activate

# Verify
pnpm --version
```

### PostgreSQL Won't Start

**Problem**: `sudo systemctl start postgresql` fails

**Solution**:
```bash
# Check status
sudo systemctl status postgresql

# Initialize database (if not initialized)
sudo -u postgres initdb -D /var/lib/postgres/data

# Check logs
sudo journalctl -u postgresql -n 50

# Fix permissions
sudo chown -R postgres:postgres /var/lib/postgres/data
sudo chmod 700 /var/lib/postgres/data
```

---

## 🐳 Docker Issues

### Permission Denied

**Problem**: `docker: permission denied while trying to connect to the Docker daemon socket`

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply changes
newgrp docker

# Or logout and login again
```

### Port Already in Use

**Problem**: `Error starting userland proxy: listen tcp4 0.0.0.0:80: bind: address already in use`

**Solution**:
```bash
# Find process using port
sudo lsof -i :80
sudo lsof -i :8000
sudo lsof -i :5432

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8080:80"  # Use 8080 instead of 80
```

### Container Keeps Restarting

**Problem**: Container status shows "Restarting"

**Solution**:
```bash
# Check logs
docker-compose logs <service_name>

# Common causes:
# 1. Missing environment variables
# 2. Database connection failed
# 3. Port conflict
# 4. Application crash

# Fix and restart
docker-compose restart <service_name>
```

### Build Fails with "No Space Left"

**Problem**: `no space left on device`

**Solution**:
```bash
# Clean Docker system
docker system prune -a

# Remove unused volumes
docker volume prune

# Remove unused images
docker image prune -a

# Check disk space
df -h
```

---

## 🗄️ Database Issues

### Connection Refused

**Problem**: `psql: error: connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused`

**Solution**:
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Check port
sudo netstat -tuln | grep 5432

# Test connection
psql -U studiocentos -d studiocentos -h localhost
```

### Authentication Failed

**Problem**: `psql: error: FATAL: password authentication failed for user "studiocentos"`

**Solution**:
```bash
# Reset password
sudo -u postgres psql
ALTER USER studiocentos WITH PASSWORD 'studiocentos2025';
\q

# Or recreate user
sudo -u postgres psql
DROP USER IF EXISTS studiocentos;
CREATE USER studiocentos WITH PASSWORD 'studiocentos2025';
GRANT ALL PRIVILEGES ON DATABASE studiocentos TO studiocentos;
\q
```

### Migration Failed

**Problem**: `alembic upgrade head` fails

**Solution**:
```bash
# Check current revision
alembic current

# Check migration history
alembic history

# Downgrade and retry
alembic downgrade -1
alembic upgrade head

# Or stamp to specific revision
alembic stamp head
```

### Database Doesn't Exist

**Problem**: `FATAL: database "studiocentos" does not exist`

**Solution**:
```bash
# Create database
sudo -u postgres psql
CREATE DATABASE studiocentos OWNER studiocentos;
\q

# Or use createdb
sudo -u postgres createdb -O studiocentos studiocentos
```

---

## 🌐 Network Issues

### CORS Errors

**Problem**: `Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution**:

Check backend CORS configuration in `apps/backend/app/core/config.py`:

```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost",
]
```

### Cannot Access Service

**Problem**: `curl: (7) Failed to connect to localhost port 8000: Connection refused`

**Solution**:
```bash
# Check if service is running
docker ps | grep studiocentos

# Check logs
docker-compose logs backend

# Check port mapping
docker port studiocentos-api

# Test from inside container
docker exec -it studiocentos-api curl localhost:8000/health
```

### DNS Resolution Failed

**Problem**: `Could not resolve host: backend`

**Solution**:
```bash
# Check Docker network
docker network inspect studiocentos

# Verify service names in docker-compose.yml
# Use service names, not localhost

# Correct:
DATABASE_URL=postgresql://user:pass@postgres:5432/db

# Wrong:
DATABASE_URL=postgresql://user:pass@localhost:5432/db
```

---

## 🏗️ Build Issues

### Dependency Installation Failed

**Problem**: `ERROR: Could not find a version that satisfies the requirement`

**Solution**:
```bash
# Update UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clear cache
uv cache clean

# Retry installation
cd apps/backend
uv sync

# Or use specific Python version
uv venv --python 3.12
source .venv/bin/activate
uv sync
```

### Frontend Build Failed

**Problem**: `pnpm build` fails

**Solution**:
```bash
# Clear node_modules and lock file
rm -rf node_modules pnpm-lock.yaml

# Reinstall
pnpm install

# Clear pnpm cache
pnpm store prune

# Retry build
pnpm build
```

### Docker Build Timeout

**Problem**: Build hangs or times out downloading packages

**Solution**:
```bash
# Increase timeout
export DOCKER_CLIENT_TIMEOUT=300
export COMPOSE_HTTP_TIMEOUT=300

# Or edit docker-compose.yml
build:
  context: .
  args:
    HTTP_TIMEOUT: 300
```

---

## ⚡ Runtime Issues

### High Memory Usage

**Problem**: Container using too much memory

**Solution**:
```bash
# Check memory usage
docker stats

# Limit memory in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### Slow Response Times

**Problem**: API responses are slow

**Solution**:
```bash
# Check logs for slow queries
docker-compose logs backend | grep "slow"

# Add database indexes
# Check connection pool settings
# Enable caching (Redis)

# Monitor with:
docker stats
```

### Application Crashes

**Problem**: Application crashes unexpectedly

**Solution**:
```bash
# Check logs
docker-compose logs --tail=100 backend

# Common causes:
# 1. Unhandled exceptions
# 2. Memory leaks
# 3. Database connection pool exhausted
# 4. Missing environment variables

# Enable debug mode
DEBUG=True

# Add more logging
LOG_LEVEL=DEBUG
```

### Redis Connection Lost

**Problem**: `Error: Redis connection lost`

**Solution**:
```bash
# Check Redis status
docker-compose logs redis

# Test connection
docker exec -it studiocentos-cache redis-cli -a studiocentos2025 ping

# Restart Redis
docker-compose restart redis

# Check Redis memory
docker exec -it studiocentos-cache redis-cli -a studiocentos2025 INFO memory
```

---

## 🔍 Debugging Tips

### Enable Debug Mode

```bash
# Backend
DEBUG=True
LOG_LEVEL=DEBUG

# Frontend
VITE_DEBUG=true
```

### Check Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Filter logs
docker-compose logs backend | grep ERROR
```

### Enter Container

```bash
# Backend
docker exec -it studiocentos-api bash

# PostgreSQL
docker exec -it studiocentos-db psql -U studiocentos

# Redis
docker exec -it studiocentos-cache redis-cli -a studiocentos2025
```

### Test Connectivity

```bash
# From host to container
curl http://localhost:8000/health

# From container to container
docker exec -it studiocentos-api curl postgres:5432
docker exec -it studiocentos-api curl redis:6379
```

---

## 📚 Additional Resources

- **[Docker Documentation](https://docs.docker.com/)**
- **[PostgreSQL Documentation](https://www.postgresql.org/docs/)**
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)**
- **[GitHub Issues](https://github.com/yourusername/studiocentos/issues)**

---

## 🆘 Still Need Help?

If you can't find a solution:

1. **Search existing issues**: [GitHub Issues](https://github.com/yourusername/studiocentos/issues)
2. **Create new issue**: Include logs, error messages, and steps to reproduce
3. **Email support**: ciro@studiocentos.it

**When reporting issues, include**:
- Operating system and version
- Docker version
- Error messages (full stack trace)
- Steps to reproduce
- Relevant logs
