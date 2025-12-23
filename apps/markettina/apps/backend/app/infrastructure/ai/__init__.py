"""
MARKETTINA v2.0 - AI Infrastructure Module

Unified AI infrastructure including:
- AI Agents (base, orchestrator, memory)
- AI Tools (file, git, database, quality)
- LLM Manager (multi-provider support)
- Collaboration framework
"""

# Agent infrastructure
from .agents.base_agent import BaseAgent
from .agents.cognitive_memory import CognitiveMemorySystem
from .agents.llm_manager import UnifiedLLMManager
from .agents.orchestrator import AgentOrchestrator
from .agents.state import AgentState
from .agents.task import Task

__all__ = [
    # Agents
    "BaseAgent",
    "UnifiedLLMManager",
    "AgentOrchestrator",
    "CognitiveMemorySystem",
    "AgentState",
    "Task",
]
