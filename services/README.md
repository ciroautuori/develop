
# Centralized Services & Applications

This repository hosts a centralized infrastructure for four applications: **IronRep**, **ISS**, **Markettina**, and **StudioCentos**.

## 🏗 System Architecture

All applications connect to a shared `web_gateway` network and use centralized services to reduce resource usage and simplify management.

### Central Components (services/)
- **Gateway (Nginx)**: The single entry point (Ports 80/443). Routes traffic to apps based on domain.
- **SSL (Certbot)**: Manages Let's Encrypt certificates.
- **Database (Postgres)**: Shared instance (Port 5432).
- **Cache (Redis)**: Shared instance (Port 6379).
- **AI Stack**:
  - **Ollama**: Local LLM server (Port 11434).
  - **ChromaDB**: Vector database (Port 8000).

---

## 🚀 Deployment Guide

### 1. Start Central Infrastructure
```bash
docker compose -f services/docker-compose.gateway.yml up -d
```

### 2. Deploy Applications
Each application handles its own backend/frontend but connects to the central services.

**IronRep**
```bash
docker compose -f apps/ironRep/config/docker/docker-compose.prod.yml up -d
```
**ISS**
```bash
docker compose -f apps/iss/docker-compose.yml up -d
```
**StudioCentos**
```bash
docker compose -f apps/studiocentos/config/docker/docker-compose.production.yml up -d
```
**Markettina**
```bash
docker compose -f apps/markettina/config/docker/docker-compose.production.yml up -d
```

---

## 🔐 SSL Configuration
Run the following command **only after** pointing your DNS records to the server IP:
```bash
docker compose -f services/docker-compose.gateway.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot -d markettina.com -d www.markettina.com -d ironrep.it -d www.ironrep.it -d studiocentos.it -d www.studiocentos.it -d innovazionesocialesalernitana.it -d www.innovazionesocialesalernitana.it
```

---

## 🛠 Troubleshooting
- **Logs**: `docker logs <container_name>`
- **Restart**: `docker restart <container_name>`
- **Databases**: Check `services/data` for persistent volumes.
