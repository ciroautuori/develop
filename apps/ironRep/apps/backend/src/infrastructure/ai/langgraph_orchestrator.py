"""
LangGraph Orchestrator - Multi-Agent Workflow with State Management.

Implements a graph-based agent orchestration using LangGraph.
Agents can collaborate, validate each other's outputs, and maintain state.
"""
from typing import Dict, Any, List, Optional, Annotated, TypedDict, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import operator
import asyncio
import logging

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# STATE DEFINITIONS
# ============================================================================

class AgentState(TypedDict):
    """State shared between all agents in the graph."""
    # User info
    user_id: str
    session_id: str

    # Messages
    messages: Annotated[List[BaseMessage], operator.add]

    # Medical state
    pain_level: int
    pain_locations: List[str]
    clearance_level: str  # red, yellow, green
    recovery_phase: str
    constraints: List[str]
    avoid_movements: List[str]

    # Context from RAG
    user_context: Dict[str, Any]
    rag_context: str

    # Current request
    current_question: str
    current_agent: str

    # Outputs
    medical_response: Optional[str]
    workout_response: Optional[str]
    nutrition_response: Optional[str]
    final_response: str

    # Validation
    needs_medical_validation: bool
    validation_result: Optional[Dict[str, Any]]

    # Decisions log
    decisions: List[Dict[str, Any]]


# ============================================================================
# AGENT NODES
# ============================================================================

class RouterNode:
    """Routes incoming requests to appropriate agent."""

    def __init__(self, llm_service):
        self.llm = llm_service

    async def __call__(self, state: AgentState) -> AgentState:
        """Determine which agent should handle the request."""
        question = state.get("current_question", "")

        # Simple keyword-based routing (can be enhanced with LLM classification)
        question_lower = question.lower()

        if any(kw in question_lower for kw in ["dolore", "male", "pain", "fastidio", "bruciore", "formicolio"]):
            agent = "medical"
        elif any(kw in question_lower for kw in ["allenamento", "workout", "esercizio", "wod", "training", "forza"]):
            agent = "workout"
        elif any(kw in question_lower for kw in ["dieta", "cibo", "mangiare", "ricetta", "calorie", "proteine", "nutri"]):
            agent = "nutrition"
        else:
            # Default to workout coach
            agent = "workout"

        state["current_agent"] = agent
        state["decisions"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "router",
            "decision": f"Routed to {agent}",
            "reason": f"Question: {question[:50]}..."
        })

        logger.info(f"🔀 Router: {agent} selected for question")
        return state


class MedicalAgentNode:
    """Medical assessment and monitoring agent."""

    def __init__(self, medical_agent, user_context_rag):
        self.agent = medical_agent
        self.rag = user_context_rag

    async def __call__(self, state: AgentState) -> AgentState:
        """Process medical-related questions."""
        logger.info("🏥 Medical Agent processing...")

        question = state.get("current_question", "")
        user_id = state.get("user_id", "")

        try:
            # Get user context
            context = await self.rag.get_user_profile_context(user_id) if self.rag else {}

            # Build context-aware prompt
            pain_level = state.get("pain_level", context.get("current_pain_level", 0))
            phase = state.get("recovery_phase", context.get("recovery_phase", "unknown"))

            # Call medical agent
            if self.agent:
                response = await self.agent.ask(
                    question=question,
                    user_id=user_id,
                    pain_level=pain_level,
                    phase=phase
                )
                answer = response.get("answer", "Non ho potuto elaborare la risposta.")
            else:
                answer = "Medical agent non disponibile."

            state["medical_response"] = answer
            state["final_response"] = answer

            # Check for red flags
            if any(flag in question.lower() for flag in ["urgente", "grave", "emergenza", "incontinenza", "paralisi"]):
                state["clearance_level"] = "red"
                state["decisions"].append({
                    "timestamp": datetime.now().isoformat(),
                    "node": "medical",
                    "decision": "RED FLAG detected",
                    "reason": "Urgent symptoms mentioned"
                })

            state["decisions"].append({
                "timestamp": datetime.now().isoformat(),
                "node": "medical",
                "decision": "Response generated",
                "pain_level": pain_level,
                "phase": phase
            })

        except Exception as e:
            logger.error(f"Medical agent error: {e}")
            state["final_response"] = f"Errore nel processamento: {str(e)}"

        return state


class WorkoutAgentNode:
    """Workout planning and coaching agent."""

    def __init__(self, workout_coach, user_context_rag):
        self.coach = workout_coach
        self.rag = user_context_rag

    async def __call__(self, state: AgentState) -> AgentState:
        """Process workout-related questions."""
        logger.info("💪 Workout Coach processing...")

        question = state.get("current_question", "")
        user_id = state.get("user_id", "")

        try:
            # Check medical clearance first
            clearance = state.get("clearance_level", "yellow")
            if clearance == "red":
                state["final_response"] = (
                    "⚠️ Non posso generare un workout in questo momento. "
                    "Il tuo livello di dolore è troppo alto. "
                    "Ti consiglio di consultare un medico prima di allenarti."
                )
                state["workout_response"] = state["final_response"]
                return state

            # Get user context
            context = await self.rag.get_user_profile_context(user_id) if self.rag else {}

            # Get constraints
            constraints = state.get("constraints", [])
            avoid_movements = state.get("avoid_movements", [])

            # Call workout coach
            if self.coach:
                response = await self.coach.ask(
                    question=question,
                    user_id=user_id,
                    medical_clearance={
                        "clearance_level": clearance,
                        "constraints": constraints,
                        "avoid_movements": avoid_movements,
                        "phase": state.get("recovery_phase", "phase_2")
                    }
                )
                answer = response.get("answer", "Non ho potuto elaborare la risposta.")
            else:
                answer = "Workout coach non disponibile."

            state["workout_response"] = answer
            state["final_response"] = answer

            # Check if we need medical validation for workout
            if any(mv in question.lower() for mv in ["deadlift", "squat pesante", "stacco"]):
                state["needs_medical_validation"] = True

            state["decisions"].append({
                "timestamp": datetime.now().isoformat(),
                "node": "workout",
                "decision": "Workout response generated",
                "clearance": clearance,
                "needs_validation": state.get("needs_medical_validation", False)
            })

        except Exception as e:
            logger.error(f"Workout coach error: {e}")
            state["final_response"] = f"Errore nel processamento: {str(e)}"

        return state


class NutritionAgentNode:
    """Nutrition planning agent."""

    def __init__(self, nutrition_agent, user_context_rag):
        self.agent = nutrition_agent
        self.rag = user_context_rag

    async def __call__(self, state: AgentState) -> AgentState:
        """Process nutrition-related questions."""
        logger.info("🥗 Nutrition Agent processing...")

        question = state.get("current_question", "")
        user_id = state.get("user_id", "")

        try:
            # Get user context
            context = await self.rag.get_user_profile_context(user_id) if self.rag else {}

            # Call nutrition agent
            if self.agent:
                response = await self.agent.ask(
                    question=question,
                    user_id=user_id
                )
                answer = response.get("answer", "Non ho potuto elaborare la risposta.")
            else:
                answer = "Nutrition agent non disponibile."

            state["nutrition_response"] = answer
            state["final_response"] = answer

            state["decisions"].append({
                "timestamp": datetime.now().isoformat(),
                "node": "nutrition",
                "decision": "Nutrition response generated"
            })

        except Exception as e:
            logger.error(f"Nutrition agent error: {e}")
            state["final_response"] = f"Errore nel processamento: {str(e)}"

        return state


class MedicalValidatorNode:
    """Validates workout suggestions against medical constraints."""

    def __init__(self, medical_agent):
        self.agent = medical_agent

    async def __call__(self, state: AgentState) -> AgentState:
        """Validate workout response against medical constraints."""
        logger.info("🔍 Medical Validator checking workout...")

        workout_response = state.get("workout_response", "")
        constraints = state.get("constraints", [])
        avoid_movements = state.get("avoid_movements", [])

        # Simple validation - check for forbidden movements
        issues = []
        for movement in avoid_movements:
            if movement.lower() in workout_response.lower():
                issues.append(f"⚠️ Movimento da evitare rilevato: {movement}")

        if issues:
            state["validation_result"] = {
                "valid": False,
                "issues": issues
            }
            # Append warning to response
            warning = "\n\n⚠️ **Nota del Medical Agent:**\n" + "\n".join(issues)
            state["final_response"] = workout_response + warning

            state["decisions"].append({
                "timestamp": datetime.now().isoformat(),
                "node": "medical_validator",
                "decision": "Validation failed",
                "issues": issues
            })
        else:
            state["validation_result"] = {"valid": True, "issues": []}
            state["decisions"].append({
                "timestamp": datetime.now().isoformat(),
                "node": "medical_validator",
                "decision": "Validation passed"
            })

        return state


# ============================================================================
# ROUTING FUNCTIONS
# ============================================================================

def route_to_agent(state: AgentState) -> str:
    """Route to appropriate agent based on state."""
    return state.get("current_agent", "workout")


def should_validate(state: AgentState) -> str:
    """Determine if medical validation is needed."""
    if state.get("needs_medical_validation", False):
        return "validate"
    return "end"


# ============================================================================
# GRAPH BUILDER
# ============================================================================

class LangGraphOrchestrator:
    """
    LangGraph-based orchestrator for multi-agent workflows.

    Graph Structure:

        START
          │
          ▼
       [Router]
          │
          ├──medical──► [Medical Agent] ──► END
          │
          ├──workout──► [Workout Agent] ──┬──validate──► [Validator] ──► END
          │                               └──end──────────────────────► END
          │
          └──nutrition─► [Nutrition Agent] ──► END
    """

    def __init__(
        self,
        llm_service,
        medical_agent=None,
        workout_coach=None,
        nutrition_agent=None,
        user_context_rag=None
    ):
        self.llm_service = llm_service
        self.medical_agent = medical_agent
        self.workout_coach = workout_coach
        self.nutrition_agent = nutrition_agent
        self.user_context_rag = user_context_rag

        # Build the graph
        self.graph = self._build_graph()

        # Memory for checkpointing
        self.memory = MemorySaver()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""

        # Create nodes
        router = RouterNode(self.llm_service)
        medical_node = MedicalAgentNode(self.medical_agent, self.user_context_rag)
        workout_node = WorkoutAgentNode(self.workout_coach, self.user_context_rag)
        nutrition_node = NutritionAgentNode(self.nutrition_agent, self.user_context_rag)
        validator_node = MedicalValidatorNode(self.medical_agent)

        # Create graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("router", router)
        workflow.add_node("medical", medical_node)
        workflow.add_node("workout", workout_node)
        workflow.add_node("nutrition", nutrition_node)
        workflow.add_node("validator", validator_node)

        # Set entry point
        workflow.set_entry_point("router")

        # Add conditional edges from router
        workflow.add_conditional_edges(
            "router",
            route_to_agent,
            {
                "medical": "medical",
                "workout": "workout",
                "nutrition": "nutrition"
            }
        )

        # Medical goes to end
        workflow.add_edge("medical", END)

        # Workout can go to validator or end
        workflow.add_conditional_edges(
            "workout",
            should_validate,
            {
                "validate": "validator",
                "end": END
            }
        )

        # Validator goes to end
        workflow.add_edge("validator", END)

        # Nutrition goes to end
        workflow.add_edge("nutrition", END)

        # Compile
        return workflow.compile(checkpointer=self.memory)

    async def process(
        self,
        question: str,
        user_id: str,
        session_id: str,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user question through the graph.

        Args:
            question: User's question
            user_id: User ID
            session_id: Session ID for conversation continuity
            initial_state: Optional initial state values

        Returns:
            Dict with response, agent used, and decisions
        """
        # Build initial state
        state: AgentState = {
            "user_id": user_id,
            "session_id": session_id,
            "messages": [HumanMessage(content=question)],
            "pain_level": 0,
            "pain_locations": [],
            "clearance_level": "yellow",
            "recovery_phase": "phase_2",
            "constraints": [],
            "avoid_movements": [],
            "user_context": {},
            "rag_context": "",
            "current_question": question,
            "current_agent": "",
            "medical_response": None,
            "workout_response": None,
            "nutrition_response": None,
            "final_response": "",
            "needs_medical_validation": False,
            "validation_result": None,
            "decisions": []
        }

        # Merge with any initial state provided
        if initial_state:
            for key, value in initial_state.items():
                if key in state:
                    state[key] = value

        # Run the graph
        config = {"configurable": {"thread_id": session_id}}

        try:
            result = await self.graph.ainvoke(state, config)

            return {
                "success": True,
                "response": result.get("final_response", ""),
                "agent": result.get("current_agent", ""),
                "decisions": result.get("decisions", []),
                "validation": result.get("validation_result"),
                "session_id": session_id
            }

        except Exception as e:
            logger.error(f"Graph execution error: {e}")
            return {
                "success": False,
                "response": f"Errore nell'elaborazione: {str(e)}",
                "agent": "error",
                "decisions": [],
                "validation": None,
                "session_id": session_id
            }

    def get_graph_visualization(self) -> str:
        """Get ASCII visualization of the graph."""
        return """
        ┌─────────────┐
        │    START    │
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │   ROUTER    │
        └──────┬──────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌───▼───┐  ┌───▼───┐
│MEDICAL│  │WORKOUT│  │NUTRIT.│
└───┬───┘  └───┬───┘  └───┬───┘
    │          │          │
    │     ┌────▼────┐     │
    │     │VALIDATE?│     │
    │     └────┬────┘     │
    │          │          │
    │     ┌────▼────┐     │
    │     │VALIDATOR│     │
    │     └────┬────┘     │
    │          │          │
    └──────────┼──────────┘
               │
        ┌──────▼──────┐
        │     END     │
        └─────────────┘
        """


def create_langgraph_orchestrator(
    llm_service,
    medical_agent=None,
    workout_coach=None,
    nutrition_agent=None,
    user_context_rag=None
) -> LangGraphOrchestrator:
    """Factory function to create orchestrator."""
    return LangGraphOrchestrator(
        llm_service=llm_service,
        medical_agent=medical_agent,
        workout_coach=workout_coach,
        nutrition_agent=nutrition_agent,
        user_context_rag=user_context_rag
    )
