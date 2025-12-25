---
description: How to deploy the full StudioCentOS stack
---

# Deploy Workflow (Monorepo & Central Gateway)

1.  **Stop specific app (if needed)**:
    ```bash
    docker compose -f apps/studiocentos/config/docker/docker-compose.production.yml down
    ```

2.  **Verify Central Services** (Always Up):
    ```bash
    docker compose -f services/docker-compose.gateway.yml ps
    ```
    Ensure `central-postgres`, `central-redis`, `central-ollama`, and `nginx-gateway` are running.

3.  **Build & Start App**:
    ```bash
    docker compose -f apps/studiocentos/config/docker/docker-compose.production.yml up -d --build
    ```

4.  **Verify SSL & Nginx**:
    ```bash
    # Test HTTPS and Domain Certificates
    curl -vI https://studiocentos.it
    ```

5.  **Check Agent Health**:
    ```bash
    docker compose -f apps/studiocentos/config/docker/docker-compose.production.yml logs -f studiocentos-ai
    ```
