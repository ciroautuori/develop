"""
FastAPI Main Application

Entry point for the REST API.
"""
import os
import logging
from typing import Dict, Any

# ==============================================================================
# 🛠️ GLOBAL MONKEYPATCH: Resolve LangChain Introspection NameErrors (BaseTool/Runnable)
# ==============================================================================
import builtins
import typing
try:
    from langchain_core.tools import BaseTool, ToolCall
    from langchain_core.runnables import Runnable, RunnableSerializable
    from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
    
    builtins.BaseTool = BaseTool
    builtins.Runnable = Runnable
    builtins.BaseMessage = BaseMessage
    builtins.HumanMessage = HumanMessage
    builtins.SystemMessage = SystemMessage
    builtins.RunnableSerializable = RunnableSerializable
    builtins.ToolCall = ToolCall
    
    _orig_get_type_hints = typing.get_type_hints
    def _patched_get_type_hints(obj, globalns=None, localns=None, include_extras=False):
        # Always try to get a dictionary we can modify
        if globalns is None:
            globalns = getattr(obj, "__globals__", {})
        
        # Aggressive injection: if we have a dict, ensure LangChain primitives are there
        # Also inject into the typing module itself as a last resort
        for name, cls in [
            ("BaseTool", BaseTool), ("Runnable", Runnable), 
            ("BaseMessage", BaseMessage), ("HumanMessage", HumanMessage),
            ("SystemMessage", SystemMessage), ("RunnableSerializable", RunnableSerializable),
            ("ToolCall", ToolCall)
        ]:
            if isinstance(globalns, dict) and name not in globalns:
                globalns[name] = cls
            # Ultimate hack: inject into typing module
            setattr(typing, name, cls)
                
        return _orig_get_type_hints(obj, globalns, localns, include_extras)
    
    typing.get_type_hints = _patched_get_type_hints
except ImportError:
    pass
# ==============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.infrastructure.persistence.database import init_db
from src.infrastructure.config.settings import settings

# Import all models to register them with Base.metadata
from src.infrastructure.persistence import models  # noqa: F401
from src.infrastructure.persistence import nutrition_models  # noqa: F401
from src.infrastructure.persistence import food_models  # noqa: F401

# Configure logging
from src.infrastructure.logging.logger import setup_logging

# Configure logging
setup_logging(
    level=settings.log_level,
    enable_sentry=(settings.log_level == "INFO") # Assuming production if log level is INFO or controlled by env
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ironRep API",
    description="AI-Powered Sports Medicine & Recovery System for Athletes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Initialize application on startup.
    """
    logger.info("🚀 Starting ironRep API...")

    # Initialize database
    init_db()
    logger.info("✅ Database initialized")

    logger.info(f"✅ ironRep API running on http://{settings.backend_host}:{settings.backend_port}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ironRep API - Sports Medicine & Recovery System",
        "version": "1.0.0",
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "llm_service": "initialized"
    }


@app.get("/api/health")
async def api_health_check():
    return await health_check()


# Import and include routers
from .routers import review, progress, users, biometrics, exercises, medical, workout_coach, nutrition, foods, auth, wizard, streaming, exercise_preferences

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(biometrics.router, prefix="/api/biometrics", tags=["Biometrics"])
app.include_router(wizard.router)  # Wizard Agent (/api/wizard)
app.include_router(review.router, prefix="/api/review", tags=["Review"])
app.include_router(medical.router)  # Medical Agent (/api/medical)
app.include_router(workout_coach.router)  # Workout Coach (/api/workout-coach)
app.include_router(nutrition.router)  # Nutrition Agent (/api/nutrition)
app.include_router(foods.router)  # Foods API (/api/foods)
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(exercises.router)  # Exercises router (already has prefix)
app.include_router(exercise_preferences.router)  # Exercise Preferences (/api/exercises/preferences)
app.include_router(streaming.router)  # Streaming SSE (/api/stream)
from .routers import workouts, plans, knowledge_base, google
app.include_router(workouts.router, prefix="/api/workouts", tags=["Workouts"])
app.include_router(plans.router)  # Weekly Plans (/api/plans)
app.include_router(knowledge_base.router, prefix="/api")  # Knowledge Base Management (/api/knowledge-base)
app.include_router(google.router, prefix="/api/google", tags=["Google Integration"])

from .routers import recipes
app.include_router(recipes.router, prefix="/api/recipes", tags=["Recipes"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.backend_host,
        port=settings.backend_port,
        log_level=settings.log_level.lower()
    )
