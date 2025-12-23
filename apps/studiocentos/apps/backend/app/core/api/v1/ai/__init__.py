"""
AI API Module.

Espone i router per le API AI:
- AI Feedback Loop
- VEO Video Generation
- Multi-Agent Orchestrator
"""

from app.core.api.v1.ai.feedback_loop_router import router as feedback_loop_router
from app.core.api.v1.ai.veo_router import router as veo_router
from app.core.api.v1.ai.orchestrator_router import router as orchestrator_router

__all__ = ["feedback_loop_router", "veo_router", "orchestrator_router"]
