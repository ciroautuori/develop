# Backend - Enterprise Framework

FastAPI backend con architettura DDD (Domain-Driven Design).

## Features

- 11 Domini Business (Auth, Billing, Admin, GDPR, Support, Tenant, Analytics, Enrichment, Themes, Meta, Portfolio)
- JWT Authentication + OAuth2 (Google, LinkedIn)
- Stripe Integration
- PostgreSQL + Redis
- Alembic Migrations
- Structured Logging (structlog)
- Prometheus Metrics
- GDPR + PCI DSS Compliance

## Setup

```bash
poetry install
cp .env.example .env
# Edit .env with your credentials
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

## Testing

```bash
poetry run pytest --cov=app
poetry run ruff check .
poetry run mypy app/
```

## API Documentation

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
