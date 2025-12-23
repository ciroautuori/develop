from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import time
import logging
from .core.config import settings
from .api.v1.api import api_router
from .database import engine, Base
from .core.rate_limiter import limiter, custom_rate_limit_exceeded_handler, security_middleware
from slowapi.errors import RateLimitExceeded
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as redis
from prometheus_fastapi_instrumentator import Instrumentator
import sentry_sdk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    debug=not settings.is_production
)

# Startup hooks: Observability and Caching
@app.on_event("startup")
async def startup_events():
    # Sentry (optional)
    if getattr(settings, "sentry_dsn", ""):
        try:
            sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=0.2)
            logger.info("Sentry initialized")
        except Exception as e:
            logger.warning(f"Sentry init failed: {e}")

    # Prometheus metrics
    try:
        Instrumentator().instrument(app).expose(app, endpoint="/metrics")
        logger.info("Prometheus metrics exposed at /metrics")
    except Exception as e:
        logger.warning(f"Prometheus instrumentation failed: {e}")

    # Redis cache for FastAPI
    try:
        r = redis.from_url(getattr(settings, 'redis_url', 'redis://localhost:6379'), encoding="utf-8", decode_responses=True)
        await r.ping()
        FastAPICache.init(RedisBackend(r), prefix="iss-cache")
        logger.info("FastAPI Cache initialized with Redis")
    except Exception as e:
        logger.warning(f"Redis cache not available: {e}")

    # Bando monitoring scheduler
    try:
        from .services.scheduler import scheduler_service
        await scheduler_service.start()
        logger.info("Bando monitoring scheduler started")
    except Exception as e:
        logger.warning(f"Bando scheduler failed to start: {e}")

    # AI Semantic Search initialization (ASYNC MODE)
    # async def initialize_ai_async():
    #     try:
    #         from .services.semantic_search import semantic_search_service
    #         await semantic_search_service.initialize()
    #         logger.info("🤖 AI Semantic Search initialized successfully!")
    #     except Exception as e:
    #         logger.error(f"❌ AI Semantic Search initialization failed: {e}")

    # # Start AI initialization in background without blocking startup
    # import asyncio
    # asyncio.create_task(initialize_ai_async())
    # logger.info("🚀 AI Semantic Search initialization started in background")


@app.on_event("shutdown")
async def shutdown_events():
    # Stop bando monitoring scheduler
    try:
        from .services.scheduler import scheduler_service
        await scheduler_service.stop()
        logger.info("Bando monitoring scheduler stopped")
    except Exception as e:
        logger.warning(f"Bando scheduler shutdown error: {e}")

# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    # Security activity detection
    await security_middleware.detect_suspicious_activity(request)

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Process-Time"] = str(process_time)

    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Public caching for GET requests on list/detail endpoints (non-admin)
    if (
        request.method == "GET"
        and request.url.path.startswith((
            f"{settings.api_v1_prefix}/projects",
            f"{settings.api_v1_prefix}/events",
            f"{settings.api_v1_prefix}/news",
        ))
        and "authorization" not in (h.lower() for h in request.headers.keys())
    ):
        response.headers["Cache-Control"] = "public, max-age=600, s-maxage=600, stale-while-revalidate=86400"

    return response

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)

# Trusted hosts (production only)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "innovazionesocialesalernitana.it",
            "*.innovazionesocialesalernitana.it",
            "localhost",
            "127.0.0.1",
            "iss-backend"
        ]
    )

# CORS - Enhanced for multi-browser compatibility with explicit preflight handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production else settings.origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRFToken",
        "Origin",
        "Referer",
        "User-Agent",
        "*"
    ],
    expose_headers=["X-Process-Time", "Set-Cookie", "*"],
    max_age=86400
)

# Explicit OPTIONS handling for all auth endpoints
@app.options("/api/v1/admin/{path:path}")
async def handle_auth_preflight():
    """Handle preflight requests for admin endpoints"""
    return JSONResponse(
        content={"status": "ok"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Origin, X-Requested-With",
            "Access-Control-Max-Age": "86400"
        }
    )

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)

@app.get("/")
async def root():
    return {
        "message": "ISS WBS API - Innovazione Sociale Salernitana APS-ETS",
        "version": "1.0.0",
        "environment": settings.environment
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.environment
    }
