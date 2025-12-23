# ============================================================================
# markettina BACKEND - UV-OPTIMIZED Dockerfile
# UV-ONLY | Layer Caching | Fast Build
# ============================================================================

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Enable UV cache
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/root/.cache/uv

# Copy workspace files (UV workspace)
COPY apps/pyproject.toml apps/uv.lock ./
COPY apps/backend/pyproject.toml ./backend/

# Install dependencies (cached layer) - solo backend package
RUN uv sync --package markettina-backend --no-dev

# Copy application code (separate layer)
COPY apps/backend/app /app/app
COPY apps/backend/alembic /app/alembic
COPY apps/backend/alembic.ini /app/alembic.ini

# Set environment
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
