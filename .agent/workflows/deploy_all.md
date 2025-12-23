---
description: How to deploy all services
---

# 🚀 Deploy All Services

## Prerequisites
- Docker & Docker Compose installed
- `web_gateway` network exists: `docker network create web_gateway`

---

## Step 1: Start Central Stack
```bash
cd /home/autcir_gmail_com/develop
docker compose -f services/docker-compose.gateway.yml up -d
```

Wait for healthy status:
```bash
docker ps | grep central
```

---

## Step 2: Deploy Applications

```bash
# ISS
docker compose -f apps/iss/docker-compose.yml up -d

# IronRep
docker compose -f apps/ironRep/config/docker/docker-compose.prod.yml up -d

# StudioCentos
docker compose -f apps/studiocentos/config/docker/docker-compose.production.yml up -d

# Markettina
docker compose -f apps/markettina/config/docker/docker-compose.production.yml up -d
```

---

## Step 3: Verify

```bash
# All containers healthy?
docker ps --format "table {{.Names}}\t{{.Status}}" | grep healthy

# Test endpoints
curl -k https://innovazionesocialesalernitana.it/health
curl -k https://ironrep.it/health
curl -k https://studiocentos.it/health
curl -k https://markettina.com/health
```

---

## Makefile Shortcuts

```bash
make deploy-all     # Run all above
make status         # Check system status
make push-all       # Git push to all repos
```
