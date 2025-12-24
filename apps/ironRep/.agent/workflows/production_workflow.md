# Production Workflow - Backend

## Objective
To safely apply changes, rebuild code, and verify functionality without downtime or regression.

## Steps

### 1. Code Modification
- Apply changes using `replace_file_content` or `multi_replace_file_content`.
- **Constraint**: Ensure imports are valid and no `TODOs` remain.

### 2. Rebuild Process
- Use the `Makefile` alias for consistency.
- **Command**:
  ```bash
  make rebuild-backend
  ```
  *(This runs `docker compose ... build backend && docker compose ... up -d backend`)*

### 3. Verification (MANDATORY)
- **Wait**: Allow 5-10 seconds for the service to start (`sleep 10`).
- **Health Check**:
  ```bash
  docker compose -f config/docker/docker-compose.prod.yml exec backend curl http://localhost:8000/health
  ```
- **Functional Test**: Use an internal python script to test the specific endpoint modified.
  ```bash
  docker compose -f config/docker/docker-compose.prod.yml exec backend python -c "import httpx; ..."
  ```

### 4. Rollback (If FAILED)
- If the new container fails to start, revert the code changes and rebuild immediately.
- **Command**:
  ```bash
  git checkout <file>
  make rebuild-backend
  ```
