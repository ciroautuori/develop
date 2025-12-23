"""
Ask Medical Agent Use Case

Handles chatbot interactions with medical agent for health monitoring.
"""
from typing import List
from datetime import datetime
import uuid

from src.application.dtos.dtos import ChatMessageDTO, AskCoachResponseDTO


class AskMedicalUseCase:
    """
    Use case for chatbot Q&A with medical agent.

    Provides context-aware answers with access to user's pain history and KPIs.
    Works with ANY injury type (sciatica, pubalgia, shoulder, knee, etc.)
    """

    def __init__(
        self,
        pain_repository,
        kpi_repository,
        chat_repository,
        medical_coach_agent,
        user_id: str,
        session_id: str = None
    ):
        self.pain_repository = pain_repository
        self.kpi_repository = kpi_repository
        self.chat_repository = chat_repository
        self.medical_coach_agent = medical_coach_agent
        self.user_id = user_id

        # Create or use existing session
        if session_id:
            self.session_id = session_id
        else:
            self.session_id = self.chat_repository.create_new_session(user_id)

    async def execute(self, question: str) -> AskCoachResponseDTO:
        """
        Get answer from medical coach with full context and persistent chat.

        The coach adapts to ANY injury type (sciatica, pubalgia, shoulder, etc.)

        Args:
            question: User's question

        Returns:
            AskCoachResponseDTO with answer and suggestions
        """
        # Step 1: Save user message to database
        self.chat_repository.save_message(
            user_id=self.user_id,
            session_id=self.session_id,
            role="user",
            content=question,
            metadata={"timestamp": datetime.now().isoformat()}
        )

        # Step 2: Build context from user data
        context = await self._build_context()

        # Step 3: Call medical coach agent with full context
        agent_response = await self.medical_coach_agent.answer_question(
            question=question,
            user_id=self.user_id,
            context=context
        )

        # Step 4: Save assistant response to database
        self.chat_repository.save_message(
            user_id=self.user_id,
            session_id=self.session_id,
            role="assistant",
            content=agent_response["answer"],
            metadata={
                "timestamp": datetime.now().isoformat(),
                "tools_used": [step[0].tool for step in agent_response.get("intermediate_steps", [])],
                "success": agent_response.get("success", True)
            }
        )

        # Step 5: Extract suggested actions (from tools used)
        suggested_actions = self._extract_suggested_actions(agent_response)
        relevant_exercises = []

        # Step 6: Return response
        return AskCoachResponseDTO(
            answer=agent_response["answer"],
            suggested_actions=suggested_actions,
            relevant_exercises=relevant_exercises,
            timestamp=datetime.now()
        )

    async def _build_context(self) -> dict:
        """Build context from user's pain history and KPIs."""
        # Get recent pain assessments
        recent_pain = self.pain_repository.get_last_n_days(self.user_id, days=7)

        # Get recent KPIs
        recent_kpis = self.kpi_repository.get_last_n_weeks(self.user_id, n=2)

        # Build context summary
        context = {
            "user_id": self.user_id,
            "recent_pain_summary": {
                "assessments_count": len(recent_pain),
                "avg_pain": sum(a.pain_level for a in recent_pain) / len(recent_pain) if recent_pain else 0,
                "common_triggers": self._extract_common_triggers(recent_pain),
                "common_locations": self._extract_common_locations(recent_pain)
            },
            "recent_kpis": [
                {
                    "week": kpi.week,
                    "avg_pain": kpi.avg_pain_level,
                    "compliance": kpi.compliance_rate
                }
                for kpi in recent_kpis
            ]
        }

        return context

    def _extract_common_triggers(self, assessments) -> List[str]:
        """Extract most common pain triggers."""
        trigger_counts = {}
        for assessment in assessments:
            for trigger in assessment.triggers:
                trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1

        # Return top 3
        sorted_triggers = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)
        return [trigger for trigger, _ in sorted_triggers[:3]]

    def _extract_common_locations(self, assessments) -> List[str]:
        """Extract most common pain locations."""
        location_counts = {}
        for assessment in assessments:
            for location in assessment.pain_locations:
                location_counts[location] = location_counts.get(location, 0) + 1

        # Return top 3
        sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
        return [location for location, _ in sorted_locations[:3]]

    def _extract_suggested_actions(self, agent_response: dict) -> List[str]:
        """
        Extract suggested actions from agent response and tools used.

        Args:
            agent_response: Response from agent

        Returns:
            List of suggested actions
        """
        actions = []

        # Check tools used
        for step in agent_response.get("intermediate_steps", []):
            tool_name = step[0].tool if hasattr(step[0], 'tool') else None

            if tool_name == "red_flags_detector":
                actions.append("Controlla red flags identificati")
            elif tool_name == "progression_calculator":
                actions.append("Valuta progressione fase")
            elif tool_name == "pain_analyzer":
                actions.append("Rivedi trend dolore")
            elif tool_name == "exercise_validator":
                actions.append("Verifica sicurezza esercizio")

        return actions

    def get_chat_history(self) -> List[ChatMessageDTO]:
        """Get full chat history from database."""
        messages = self.chat_repository.get_session_history(self.session_id)

        return [
            ChatMessageDTO(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"]
            )
            for msg in messages
        ]

    def clear_history(self):
        """Clear chat history (delete session)."""
        self.chat_repository.delete_session(self.session_id)
        # Create new session
        self.session_id = self.chat_repository.create_new_session(self.user_id)

    def get_session_id(self) -> str:
        """Get current session ID."""
        return self.session_id
