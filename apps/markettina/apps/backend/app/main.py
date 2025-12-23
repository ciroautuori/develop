"""MARKETTINA v2.0 - Main Entry Point
AI-Powered Marketing Automation Platform
Architettura modulare con Domain-Driven Design.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# AI API Routes (unified from ai_microservice)
# from app.core.api.v1.ai import ai_marketing_router, rag_router, ai_support_router
# app.include_router(ai_marketing_router, prefix="/api/v1/ai/marketing", tags=["AI Marketing"])
# app.include_router(rag_router, prefix="/api/v1/ai/rag", tags=["RAG"])
# app.include_router(ai_support_router, prefix="/api/v1/ai/support", tags=["AI Support"])
# CRITICAL: Import models registry to configure all SQLAlchemy relationships
from app.core.api.dependencies.auth_deps import get_current_user
from app.core.api.middleware import setup_middleware_stack
from app.core.api.v1 import api_router
from app.core.config import settings
from app.domain.analytics.router import router as analytics_router
from app.domain.auth.admin_router import router as admin_auth_router
from app.domain.auth.models import User, UserRole
from app.domain.auth.settings_router import router as admin_settings_router
from app.domain.auth.user_admin_router import router as user_admin_router
from app.domain.copilot.routers import router as copilot_router

# from app.domain.analytics.dashboard_router import router as analytics_dashboard_router
# app.include_router(analytics_dashboard_router, prefix="")
from app.domain.customers.routers import router as customers_router
from app.domain.finance.router import router as finance_router
from app.domain.google.router import router as google_router
from app.domain.heygen.router import router as heygen_router
from app.domain.marketing.brand_dna_router import router as brand_dna_router
from app.domain.marketing.email_router import router as email_marketing_router
from app.domain.marketing.lead_enrichment_router import router as lead_enrichment_router
from app.domain.marketing.router import router as marketing_router
from app.domain.marketing.routers import router as marketing_calendar_router
from app.domain.media.upload_router import router as upload_router
from app.domain.notifications.router import router as notifications_router
from app.domain.notifications.websocket_router import router as notifications_ws_router
from app.domain.seo.sitemap_router import router as sitemap_router
from app.domain.social.multi_platform_router import router as multi_platform_social_router
from app.domain.social.router import router as social_router
from app.domain.support.routers import router as support_router
from app.infrastructure.database.models_registry import configure_all_models
from app.infrastructure.monitoring import setup_logging
from app.infrastructure.scheduler import (
    start_all_schedulers,
    stop_all_schedulers,
)
from app.infrastructure.startup import startup_manager

# ============================================================================
# SENTRY INITIALIZATION - Error Monitoring
# ============================================================================

if settings.ENVIRONMENT == "production" and settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        before_send=lambda event, hint: event if settings.ENVIRONMENT == "production" else None,
    )
    logger_sentry = logging.getLogger("sentry")
    logger_sentry.info("Sentry initialized for production")

# Setup logging
setup_logging(level=settings.LOG_LEVEL, service_name="markettina-backend")
logger = logging.getLogger("markettina-backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.
    Handles startup and shutdown procedures.
    """
    # Startup procedures
    logger.info("Starting MARKETTINA Backend...")
    await startup_manager.initialize_database()
    logger.info("Database initialized")

    # CRITICAL: Configure all SQLAlchemy models and relationships
    configure_all_models()
    logger.info("SQLAlchemy models configured")

    # Start ALL schedulers (ToolAI, Marketing Content, Post Publishing, etc.)
    try:
        asyncio.create_task(start_all_schedulers())
        logger.info("All schedulers started (ToolAI, Marketing Content, Post Publishing)")
    except Exception as e:
        logger.error(f"Failed to start schedulers: {e}")
        # Don't crash the application, continue without scheduler

    yield  # Application runs here

    # Shutdown procedures
    logger.info("Shutting down MARKETTINA Backend...")
    await stop_all_schedulers()
    logger.info("All schedulers stopped")
    await startup_manager.shutdown_procedures()

app = FastAPI(
    title="MARKETTINA API",
    description="""
# MARKETTINA v2.0 - AI-Powered Marketing Automation

## Overview
MARKETTINA is an enterprise-grade SaaS platform for marketing automation with generative AI.

## Features
- 🔐 **Authentication**: JWT-based auth with OAuth (Google, LinkedIn) and MFA support
- 💳 **Billing**: Stripe integration with subscriptions and trials
- 📊 **Analytics**: Social metrics, sentiment analysis, competitor tracking
- 📅 **Editorial Calendar**: Multi-platform content scheduling
- 🛡️ **Security**: PCI DSS compliant, GDPR ready, enterprise encryption
- 🤖 **AI Support**: Intelligent customer support system

## Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

Get your token from `/api/v1/auth/login` or `/api/v1/auth/register`

## Rate Limiting
- **Anonymous**: 60 requests/minute
- **Authenticated**: 300 requests/minute
- **Premium users**: 1000 requests/minute

## Error Codes
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

## Support
- Documentation: `/docs` (Swagger) or `/redoc` (ReDoc) - **Admin only**
- Health check: `/health`
- Support: Contact via `/api/v1/support` endpoint
""",
    version="2.1.0",
    docs_url=None,  # Disable default docs - we'll create custom protected routes
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
    terms_of_service="https://markettina.it/terms",
    contact={
        "name": "MARKETTINA Support",
        "url": "https://markettina.it/support",
        "email": "info@markettina.it",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://markettina.it/license",
    },
    openapi_tags=[
        {"name": "auth", "description": "Authentication and authorization"},
        {"name": "users", "description": "User management"},
        {"name": "billing", "description": "Subscriptions and payments"},
        {"name": "admin", "description": "Admin operations (requires admin role)"},
        {"name": "support", "description": "Customer support and tickets"},
        {"name": "gdpr", "description": "GDPR compliance and data management"},
        {"name": "oauth", "description": "OAuth integrations (Google, LinkedIn)"},
        {"name": "mfa", "description": "Multi-factor authentication"},
    ],
)

# Setup middleware stack (includes CORS, rate limiting, security headers, etc.)
# NOTE: CORS is configured inside setup_middleware_stack with BACKEND_CORS_ORIGINS
setup_middleware_stack(app)

# Admin-only dependency
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role for protected endpoints"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user

# Include routers
app.include_router(api_router)

# Register Admin Authentication router
app.include_router(admin_auth_router)

# Register Admin Settings router
app.include_router(admin_settings_router, prefix="/api/v1/admin")

# Register User Management Admin router
app.include_router(user_admin_router)

# Register Support AI router
app.include_router(support_router)

# Register Copilot router (AI Assistant)
app.include_router(copilot_router)

# Register Notifications WebSocket router
app.include_router(notifications_ws_router)

# Register Notifications REST API router
app.include_router(notifications_router, prefix="/api/v1/admin")

# Register Analytics router
app.include_router(analytics_router)

# Register Analytics Dashboard router (KPI aggregati) - prefix già incluso nel router
# app.include_router(analytics_dashboard_router, prefix="")

# Register Finance router (Gestione Finanziaria) - BUSINESS CRITICAL!
app.include_router(finance_router)

# Register Customers router (CRM)
app.include_router(customers_router)

# Register Marketing Calendar router (Calendario Editoriale)
app.include_router(marketing_calendar_router, prefix="/api/v1")

# Register Marketing router (Leads & Email Campaigns)
app.include_router(marketing_router, prefix="/api/v1/marketing")

# Register Marketing Scheduler router (Batch Content Generation Control)
from app.domain.marketing.scheduler_router import router as marketing_scheduler_router

app.include_router(marketing_scheduler_router, prefix="/api/v1/marketing")

# Register Lead Enrichment router (Google Places, AI Scoring)
app.include_router(lead_enrichment_router, prefix="/api/v1/marketing")

# Register Email Marketing router (SendGrid/Mailgun/SMTP)
app.include_router(email_marketing_router, prefix="/api/v1/marketing")

# Register Brand DNA router (Brand Identity Settings)
app.include_router(brand_dna_router, prefix="/api/v1/marketing")

# Register Social Publishing router (Meta, LinkedIn, Twitter)
app.include_router(social_router, prefix="/api/v1")
app.include_router(multi_platform_social_router, prefix="/api/v1")

# Register LinkedIn Publishing router (API diretta)
from app.domain.social.linkedin_router import router as linkedin_router
app.include_router(linkedin_router, prefix="/api/v1/social")

# Register Upload router (Image uploads) - upload_router has prefix="/upload"
app.include_router(upload_router, prefix="/api/v1")

# Register Google Integrations router (GA4 + GMB)
app.include_router(google_router)

# Register SEO router (Sitemap & Robots.txt) - NO prefix for root paths
app.include_router(sitemap_router)

# Register HeyGen router (AI Avatar Video Generation)
app.include_router(heygen_router, prefix="/api/v1")

# Register Instagram Insights router (Performance Analytics)
from app.core.api.v1.insights.instagram_router import router as instagram_insights_router
app.include_router(instagram_insights_router, prefix="/api/v1/insights")

# Register AI Feedback Loop router (Learning from Performance)
from app.core.api.v1.ai.feedback_loop_router import router as feedback_loop_router
app.include_router(feedback_loop_router, prefix="/api/v1/ai")

# Register VEO Video router (AI Video Generation)
from app.core.api.v1.ai.veo_router import router as veo_router
app.include_router(veo_router, prefix="/api/v1/ai")

# Register Multi-Agent Orchestrator router (AI Agent Coordination)
from app.core.api.v1.ai.orchestrator_router import router as orchestrator_router
app.include_router(orchestrator_router, prefix="/api/v1/ai")

# WhatsApp RIMOSSO - Usiamo l'app mobile
# Per riattivare: decommentare le righe sotto
# app.include_router(whatsapp_router, prefix="/api/v1")
# app.include_router(whatsapp_webhook_router, prefix="/api/v1")

# ==========================================================================
# AI API Routes (unified from ai_microservice)
# ==========================================================================
# app.include_router(ai_marketing_router, prefix="/api/v1/ai/marketing", tags=["AI Marketing"])
# app.include_router(rag_router, prefix="/api/v1/ai/rag", tags=["RAG"])
# app.include_router(ai_support_router, prefix="/api/v1/ai/support", tags=["AI Support"])

# ==========================================================================
# Billing API Routes (Token economy, Invoices, Promo codes)
# ==========================================================================
from app.domain.billing.routers import (
    admin_router as billing_admin_router,
    router as billing_router,
)
from app.domain.billing.token_router import (
    admin_router as token_admin_router,
    router as token_router,
)

app.include_router(billing_router, tags=["Billing"])
app.include_router(billing_admin_router, tags=["Admin Billing"])
app.include_router(token_router, prefix="/api/v1", tags=["Tokens"])
app.include_router(token_admin_router, prefix="/api/v1", tags=["Admin Tokens"])

# ==========================================================================
# Identity API Routes (Accounts, Social Accounts, Permissions)
# ==========================================================================
from datetime import UTC

from app.domain.identity.routers import (
    admin_router as identity_admin_router,
    router as identity_router,
)

app.include_router(identity_router, tags=["Identity"])
app.include_router(identity_admin_router, tags=["Admin Identity"])

# ==========================================================================
# OAuth API Routes (Social Media OAuth Integration)
# ==========================================================================
from app.api.v1.endpoints.oauth import router as oauth_router
app.include_router(oauth_router, prefix="/api/v1", tags=["OAuth"])

# ==========================================================================
# Customer API Routes (Customer Portal)
# ==========================================================================
from app.domain.customer.routers import router as customer_router
app.include_router(customer_router, prefix="/api/v1/customer", tags=["Customer"])

# ==========================================================================
# Onboarding API Routes (Onboarding Wizard)
# ==========================================================================
from app.domain.onboarding.routers import router as onboarding_router
app.include_router(onboarding_router, prefix="/api/v1/onboarding", tags=["Onboarding"])

# Mount static files
static_path = settings.STATIC_FILES_DIR
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    logger.info(f"Static files mounted from: {static_path}")
else:
    logger.warning(f"Static files directory not found: {static_path}")

# Mount uploads directory (for social media, portfolio images, etc.)
uploads_path = "/app/uploads"
if os.path.exists(uploads_path):
    app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")
    logger.info(f"Uploads directory mounted from: {uploads_path}")
else:
    # Create uploads directory if it doesn't exist
    os.makedirs(uploads_path, exist_ok=True)
    os.makedirs(f"{uploads_path}/social", exist_ok=True)
    os.makedirs(f"{uploads_path}/projects", exist_ok=True)
    os.makedirs(f"{uploads_path}/thumbnails", exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")
    logger.info(f"Uploads directory created and mounted: {uploads_path}")

# Root endpoint
@app.get(
    "/",
    tags=["root"],
    summary="API Root",
    description="Get API information and available endpoints",
    response_description="API metadata and navigation links",
)
async def root():
    """
    # MARKETTINA API Root

    Welcome to the MARKETTINA Marketing Automation API!

    ## Quick Links
    - **Swagger Docs**: [/docs](/docs)
    - **ReDoc**: [/redoc](/redoc)

    ## Authentication
    1. Register at `/api/v1/auth/register`
    2. Login at `/api/v1/auth/login`
    3. Use JWT token in `Authorization: Bearer <token>` header

    ## Support
    Need help? Contact us at info@markettina.it
    """
    return {
        "name": "MARKETTINA API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
        },
        "endpoints": {
            "health": "/health",
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "billing": "/api/v1/billing",
            "support": "/api/v1/support",
        },
        "status": "operational",
    }

# Protected API Documentation endpoints (Admin only)
@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation(admin: User = Depends(require_admin)):
    """Swagger UI documentation - Admin only access"""
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - Swagger UI",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation(admin: User = Depends(require_admin)):
    """ReDoc documentation - Admin only access"""
    from fastapi.openapi.docs import get_redoc_html
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - ReDoc",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_schema(admin: User = Depends(require_admin)):
    """OpenAPI schema - Admin only access"""
    from fastapi.openapi.utils import get_openapi
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

# API Documentation compatibility endpoints
@app.get("/api/docs", include_in_schema=False)
async def api_docs_redirect(admin: User = Depends(require_admin)):
    """Redirect /api/docs to /docs for backwards compatibility - Admin only"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

@app.get("/api/redoc")
async def api_redoc_redirect():
    """Redirect /api/redoc to /redoc for backwards compatibility."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/redoc")

# Health check
@app.get(
    "/health",
    tags=["health"],
    summary="Health Check",
    description="Check if the API is running and healthy",
    response_description="Health status",
)
async def health():
    """
    # Health Check Endpoint

    Returns the health status of the API.

    ## Response
    - `status`: Overall health status ("healthy" or "unhealthy")
    - `version`: API version
    - `environment`: Current environment (development/staging/production)
    - `timestamp`: Current server timestamp

    ## Usage
    Use this endpoint for:
    - Load balancer health checks
    - Monitoring/alerting systems
    - Uptime monitoring services
    - Deployment verification
    """
    from datetime import datetime

    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(UTC).isoformat(),
        "service": "markettina-api",
    }
