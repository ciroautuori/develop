# ============================================================================
# STUDIOCENTOS AI MICROSERVICE - UV-OPTIMIZED Dockerfile
# UV-ONLY | Layer Caching | Fast Build
# ============================================================================

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Enable UV cache
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/root/.cache/uv

# Copy workspace files (UV workspace)
COPY apps/pyproject.toml apps/uv.lock ./
COPY apps/ai_microservice/pyproject.toml ./ai_microservice/

# Install dependencies (cached layer) - solo ai_microservice package
RUN uv sync --package studiocentos-ai-service --no-dev --no-install-project

# Copy application code (separate layer)
COPY apps/ai_microservice/app /app/app

# Set environment
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Expose port
EXPOSE 8001

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "2"]
