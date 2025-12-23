# ================================
# Stage 1: Builder - Install dependencies with uv
# ================================
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Create venv
RUN uv venv /opt/venv

# Activate venv for subsequent commands
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy project files
COPY pyproject.toml README.md ./

# Install dependencies first (without the package itself)
# This ensures all dependencies including uvicorn are installed
RUN uv pip install \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.32.0 \
    pydantic>=2.10.0 \
    pydantic-settings>=2.6.0 \
    python-dotenv>=1.0.0 \
    sqlalchemy>=2.0.36 \
    alembic>=1.14.0 \
    python-jose[cryptography]>=3.3.0 \
    passlib[argon2,bcrypt]>=1.7.4 \
    email-validator>=2.1.0 \
    python-multipart>=0.0.9 \
    psycopg2-binary>=2.9.10 \
    langchain==0.2.16 \
    langchain-core==0.2.38 \
    langchain-community==0.2.16 \
    langchain-groq>=0.2.0 \
    langchain-google-genai>=2.0.0 \
    groq>=0.12.0 \
    google-generativeai>=0.8.0 \
    chromadb>=0.5.23 \
    httpx>=0.28.0 \
    requests>=2.32.0 \
    python-dateutil>=2.9.0 \
    pytz>=2024.2 \
    google-auth>=2.25.0 \
    google-auth-oauthlib>=1.2.0 \
    google-api-python-client>=2.110.0 \
    google-auth-httplib2>=0.2.0

# Force cleanup of langchain and reinstall (include google/groq)
RUN rm -rf /opt/venv/lib/python3.11/site-packages/langchain*
RUN uv pip install --force-reinstall langchain==0.2.16 langchain-core==0.2.38 langchain-community==0.2.16 langchain-groq>=0.2.0 langchain-google-genai>=2.0.0

# Cleanup
RUN find /opt/venv -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find /opt/venv -type f -name "*.pyc" -delete

# ================================
# Stage 2: Runtime
# ================================
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 ironrep && \
    mkdir -p /app /app/chroma_db /app/data && \
    chown -R ironrep:ironrep /app

WORKDIR /app

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV="/opt/venv"

# Copy application code
COPY --chown=ironrep:ironrep . .

# Switch to non-root user
USER ironrep

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (use python -m to ensure module is found)
CMD ["python", "-m", "uvicorn", "src.interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
