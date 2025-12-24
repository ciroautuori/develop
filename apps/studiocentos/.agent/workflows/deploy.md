---
description: How to deploy the full StudioCentOS stack
---

# Deploy Workflow

1.  **Stop existing containers**:
    ```bash
    docker compose down
    ```

2.  **Pull/Build latest images**:
    ```bash
    docker compose build
    ```

3.  **Start services**:
    ```bash
    docker compose up -d
    ```

4.  **Verify Status**:
    ```bash
    docker compose ps
    ```
    Ensure `backend`, `frontend`, `ai_microservice`, and `nginx` are `Up`.

5.  **Check Logs** (Optional):
    ```bash
    docker compose logs -f ai_microservice
    ```
