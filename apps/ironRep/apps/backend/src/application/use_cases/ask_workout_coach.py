"""
Ask Workout Coach Use Case

Handles chatbot interactions with workout coach agent for training programming.
"""
from typing import List
from datetime import datetime

from src.application.dtos.dtos import ChatMessageDTO, AskCoachResponseDTO


class AskWorkoutCoachUseCase:
    """
    Use case for chatbot Q&A with workout coach.

    Provides training programming advice with access to medical clearance and workout history.
    """

    def __init__(
        self,
        workout_repository,
        pain_repository,
        chat_repository,
        workout_coach_agent,
        user_id: str,
        session_id: str = None
    ):
        self.workout_repository = workout_repository
        self.pain_repository = pain_repository
        self.chat_repository = chat_repository
        self.workout_coach_agent = workout_coach_agent
        self.user_id = user_id

        # Create or use existing session
        if session_id:
            self.session_id = session_id
        else:
            self.session_id = self.chat_repository.create_new_session(user_id, session_type="coach")

    async def execute(self, question: str) -> AskCoachResponseDTO:
        """
        Get training advice from workout coach.

        Args:
            question: User's question about training

        Returns:
            AskCoachResponseDTO with answer and suggestions
        """
        # Step 1: Save user message
        self.chat_repository.save_message(
            user_id=self.user_id,
            session_id=self.session_id,
            role="user",
            content=question,
            metadata={"timestamp": datetime.now().isoformat(), "session_type": "coach"}
        )

        # Step 2: Build context (medical clearance + workout history)
        context = await self._build_context()

        # Step 3: Call workout coach agent
        agent_response = await self.workout_coach_agent.answer_question(
            question=question,
            user_id=self.user_id,
            context=context
        )

        # Step 4: Save assistant response
        self.chat_repository.save_message(
            user_id=self.user_id,
            session_id=self.session_id,
            role="assistant",
            content=agent_response["answer"],
            metadata={
                "timestamp": datetime.now().isoformat(),
                "tools_used": [step[0].tool for step in agent_response.get("intermediate_steps", [])],
                "success": agent_response.get("success", True),
                "session_type": "coach"
            }
        )

        # Step 5: Extract suggested actions
        suggested_actions = self._extract_suggested_actions(agent_response)

        return AskCoachResponseDTO(
            answer=agent_response["answer"],
            suggested_actions=suggested_actions,
            relevant_exercises=[],
            timestamp=datetime.now()
        )

    async def _build_context(self) -> dict:
        """Build context with medical clearance and workout history."""
        # Get recent pain assessments for medical status
        recent_pain = self.pain_repository.get_last_n_days(self.user_id, days=7)

        # Get recent workouts
        recent_workouts = self.workout_repository.get_last_n(self.user_id, n=5)

        # Build medical status summary
        medical_status = {}
        if recent_pain:
            latest_pain = recent_pain[0]
            avg_pain = sum(a.pain_level for a in recent_pain) / len(recent_pain)

            medical_status = {
                "pain_level": latest_pain.pain_level,
                "avg_pain_7days": avg_pain,
                "pain_locations": latest_pain.pain_locations,
                "triggers": latest_pain.triggers,
                "phase": self._determine_phase(avg_pain),
                "contraindications": self._get_contraindications(latest_pain.pain_locations)
            }

        context = {
            "user_id": self.user_id,
            "medical_status": medical_status,
            "recent_workouts": [
                {
                    "date": w.date.isoformat() if hasattr(w.date, 'isoformat') else str(w.date),
                    "phase": w.phase.value if hasattr(w.phase, 'value') else str(w.phase),
                    "completed": getattr(w, 'completed', False)
                }
                for w in recent_workouts
            ]
        }

        return context

    def _determine_phase(self, avg_pain: float) -> str:
        """Determine recovery phase based on pain."""
        if avg_pain >= 7:
            return "phase_1"
        elif avg_pain >= 5:
            return "phase_2"
        elif avg_pain >= 3:
            return "phase_3"
        else:
            return "phase_4"

    def _get_contraindications(self, pain_locations: List[str]) -> List[str]:
        """Get contraindicated movements based on pain locations."""
        contraindications = []

        for location in pain_locations:
            if "lombare" in location.lower() or "schiena" in location.lower():
                contraindications.extend(["flexion_under_load", "heavy_deadlifts", "sit_ups"])
            elif "spalla" in location.lower():
                contraindications.extend(["overhead_pressing", "kipping_pullups"])
            elif "ginocchio" in location.lower():
                contraindications.extend(["running", "box_jumps", "pistols"])
            elif "anca" in location.lower():
                contraindications.extend(["deep_squats", "running", "high_kicks"])

        return list(set(contraindications))

    def _extract_suggested_actions(self, agent_response: dict) -> List[str]:
        """Extract suggested actions from agent response."""
        actions = []

        for step in agent_response.get("intermediate_steps", []):
            tool_name = step[0].tool if hasattr(step[0], 'tool') else None

            if tool_name == "exercise_validator":
                actions.append("Verifica sicurezza esercizio")
            elif tool_name == "progression_calculator":
                actions.append("Valuta progressione")

        return actions

    def get_chat_history(self) -> List[ChatMessageDTO]:
        """Get chat history."""
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
        """Clear chat history."""
        self.chat_repository.delete_session(self.session_id)
        self.session_id = self.chat_repository.create_new_session(self.user_id, session_type="coach")

    def get_session_id(self) -> str:
        """Get current session ID."""
        return self.session_id
