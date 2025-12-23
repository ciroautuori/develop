"""
CV-Lab AI Microservice - Main Application
FastAPI application serving all AI services
"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.api.v1 import rag, support, marketing, health, demo, toolai

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown"""
    # Startup
    logger.info(
        "ai_service_startup",
        version="1.0.0",
        environment=settings.AI_SERVICE_ENV,
        port=settings.AI_SERVICE_PORT
    )

    # Initialize services
    logger.info("services_initialization_started")
    # Add service initializers here as needed
    logger.info("services_initialization_complete")

    yield

    # Shutdown
    logger.info("ai_service_shutdown")


# Create FastAPI application
app = FastAPI(
    title="CV-Lab AI Microservice",
    description="Unified AI service for Frontend, Mobile, and Backend",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, tags=["Health"])
app.include_router(demo.router, prefix="/api/v1", tags=["Demo"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"])
app.include_router(support.router, prefix="/api/v1/support", tags=["Support"])
# TODO: Re-enable when domain is implemented
# app.include_router(debug.router, prefix="/api/v1/debug", tags=["Debug"])
# app.include_router(cv_intelligence.router, prefix="/api/v1/cv", tags=["CV Intelligence"])
app.include_router(marketing.router, prefix="/api/v1/marketing", tags=["Marketing"])

# ToolAI - Daily AI Tools Discovery
app.include_router(toolai.router, prefix="/api/v1/toolai", tags=["ToolAI"])

# Prometheus metrics
if settings.ENABLE_METRICS:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

# Static files for generated images
media_dir = Path("/app/media/generated")
media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media/generated", StaticFiles(directory=str(media_dir)), name="generated_images")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if not settings.is_production else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.AI_SERVICE_HOST,
        port=settings.AI_SERVICE_PORT,
        reload=not settings.is_production,
        log_level=settings.LOG_LEVEL.lower()
    )
