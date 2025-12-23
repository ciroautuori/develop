---
description: How to deploy all services
---

1. Ensure the central gateway is running:
   ```bash
   docker compose -f services/docker-compose.gateway.yml up -d
   ```

2. Deploy each application:
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

3. Verify status:
   ```bash
   docker ps
   ```
