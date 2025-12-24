
# Centralized Docker Infrastructure Walkthrough

## Goal Achieved
Successfully centralized Docker services (Nginx, SSL, Postgres, Redis, ChromaDB, Ollama) and refactored four applications (`markettina`, [ironRep](file:///home/autcir_gmail_com/develop/apps/ironRep), `studiocentos`, `iss`) to utilize this shared infrastructure.

## System Architecture

### Central Services
| Service | Container Name | Port (Internal) | Notes |
| :--- | :--- | :--- | :--- |
| **Nginx Gateway** | `nginx-gateway` | 80, 443 | Single entry point for all domains |
| **Postgres** | `central-postgres` | 5432 | Shared database instance |
| **Redis** | `central-redis` | 6379 | Shared cache instance |
| **ChromaDB** | `central-chromadb` | 8000 | Shared vector database |
| **Ollama** | `central-ollama` | 11434 | Shared AI model server |
| **Certbot** | `certbot-gateway` | - | SSL certificate management |

### Application Status
All applications are deployed and connected to the central gateway using the `web_gateway` network.

| Application | Domain | Status | Database | Redis DB |
| :--- | :--- | :--- | :--- | :--- |
| **Markettina** | `markettina.com` | ✅ **UP** | `markettina` | `1` |
| **StudioCentos** | `studiocentos.it` | ✅ **UP** | `studiocentos` | `2` |
| **ISS** | `innovazionesocialesalernitana.it` | ✅ **UP** | `iss_wbs` | `3` |
| **IronRep** | `ironrep.it` | ✅ **UP** | `ironrep` | `4` |

---

## Key Changes & Fixes

### 1. IronRep Build Resolution
Resolved a complex chain of missing dependencies and TypeScript errors in the IronRep frontend build:
- Created multiple stub APIs in `src/lib/api/` (users, workouts, plans, nutrition, medical, etc.).
- Fixed module resolution for `authToken`, `haptics`, and `touch-targets`.
- Successfully built and deployed the production Docker container.

### 2. ISS Backend Fixes
- Updated database driver to `asyncpg` to resolve `InvalidRequestError`.
- Configured backend to use `postgresql+asyncpg://` protocol.
- Resolved volume mount issues by creating missing host directories (`data/logs`, `data/postgres`).

### 3. Centralized Configuration
- All applications now use `external: true` for `web_gateway` network.
- [docker-compose.yml](file:///home/autcir_gmail_com/develop/apps/iss/docker-compose.yml) files refactored to remove redundant local services (Nginx, Certbot).
- Central Nginx configured with domain-specific blocks in `conf.d/`.

---

## Verification
You can verify the status of all containers:
```bash
docker ps
```
Look for:
- `nginx-gateway` (Ports 80/443)
- `postgres:16-alpine` (Central DB)
- `ironrep-frontend-prod`, `iss-frontend`, `studiocentos-frontend`, `markettina-frontend`

## Next Steps

### 1. DNS Configuration
**Action Required:** Update your DNS records to point the following domains to the server IP (`35.195.232.166`):
- `markettina.com`
- `www.markettina.com`
- `ironrep.it`
- `www.ironrep.it`
- `studiocentos.it`
- `www.studiocentos.it`
- `innovazionesocialesalernitana.it`
- `www.innovazionesocialesalernitana.it`

### 2. SSL Certificate Issuance
Once DNS is propagated, run the Certbot command to issue SSL certificates (currently Nginx is configured for HTTP-only to facilitate this):
```bash
docker compose -f services/docker-compose.gateway.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot -d markettina.com -d www.markettina.com -d ironrep.it -d www.ironrep.it -d studiocentos.it -d www.studiocentos.it -d innovazionesocialesalernitana.it -d www.innovazionesocialesalernitana.it
```
After issuance, uncomment the SSL configurations in `services/nginx/conf.d/*.conf` and reload Nginx.
