"""
Conversational Check-In Use Case

Orchestrates AI-driven conversational check-in workflow using MedicalCoachAgent.
This replaces the old form-based check-in with an intelligent conversation.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json
import re

from src.domain.entities.pain_assessment import PainAssessment
from src.domain.entities.workout_session import WorkoutPhase
from src.domain.repositories.pain_repository import IPainRepository
from src.domain.repositories.workout_repository import IWorkoutRepository
from src.domain.repositories.chat_repository import IChatRepository
from src.application.dtos.dtos import WorkoutDTO


class CheckInConversationalUseCase:
    """
    Conversational medical check-in orchestrated by MedicalAgent.

    This use case manages the multi-turn conversation for daily medical check-in,
    extracting structured data from natural language and saving to database.
    """

    def __init__(
        self,
        medical_agent,
        pain_repository: IPainRepository,
        workout_repository: IWorkoutRepository,
        chat_repository: IChatRepository,
        user_id: str
    ):
        self.agent = medical_agent
        self.pain_repo = pain_repository
        self.workout_repo = workout_repository
        self.chat_repo = chat_repository
        self.user_id = user_id

    async def start_checkin(self) -> Dict[str, Any]:
        """
        Start conversational check-in session.

        Returns:
            dict with session_id and initial agent message
        """
        # Create new check-in session
        session_id = self.chat_repo.create_new_session(
            user_id=self.user_id,
            session_type="checkin"
        )

        # Get initial greeting from agent
        initial_prompt = """
Inizia un check-in giornaliero conversazionale.
Saluta l'utente e chiedi come si sente oggi.
Sii empatico e professionale.
"""

        # Call agent
        result = await self.agent.answer_question(
            question=initial_prompt,
            user_id=self.user_id,
            context={"session_type": "checkin", "step": "greeting"}
        )

        # Save agent message
        self.chat_repo.save_message(
            user_id=self.user_id,
            session_id=session_id,
            role="assistant",
            content=result["answer"],
            metadata={
                "timestamp": datetime.now().isoformat(),
                "session_type": "checkin",
                "step": "greeting"
            }
        )

        return {
            "success": True,
            "session_id": session_id,
            "message": result["answer"],
            "completed": False
        }

    async def continue_conversation(
        self,
        session_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Continue check-in conversation.

        Args:
            session_id: Check-in session ID
            user_message: User's message

        Returns:
            dict with agent response and completion status
        """
        # Save user message
        self.chat_repo.save_message(
            user_id=self.user_id,
            session_id=session_id,
            role="user",
            content=user_message,
            metadata={"timestamp": datetime.now().isoformat()}
        )

        # Get conversation history
        history = self.chat_repo.get_session_history(session_id)

        # Build context with history
        context = {
            "session_type": "checkin",
            "conversation_history": history,
            "user_id": self.user_id
        }

        # Determine if we have enough info to complete check-in
        extracted_data = self._extract_pain_data_from_history(history)

        if extracted_data["complete"]:
            # We have all data, finalize check-in
            return await self._finalize_checkin(session_id, extracted_data)

        # Continue conversation - ask for missing info
        prompt = f"""
Continua il check-in giornaliero. L'utente ha detto: "{user_message}"

Dati raccolti finora:
- Dolore: {extracted_data.get('pain_level', 'NON SPECIFICATO')}
- Localizzazioni: {extracted_data.get('pain_locations', 'NON SPECIFICATE')}
- Trigger: {extracted_data.get('triggers', 'NON SPECIFICATI')}

Se mancano informazioni essenziali (dolore, localizzazioni), chiedi in modo naturale.
Se hai tutte le info, analizza con i tools e fornisci raccomandazioni.
"""

        result = await self.agent.answer_question(
            question=prompt,
            user_id=self.user_id,
            context=context
        )

        # Save agent response
        self.chat_repo.save_message(
            user_id=self.user_id,
            session_id=session_id,
            role="assistant",
            content=result["answer"],
            metadata={
                "timestamp": datetime.now().isoformat(),
                "tools_used": [step[0].tool for step in result.get("intermediate_steps", [])],
                "extracted_data": extracted_data
            }
        )

        return {
            "success": True,
            "session_id": session_id,
            "message": result["answer"],
            "completed": False,
            "extracted_data": extracted_data
        }

    async def _finalize_checkin(
        self,
        session_id: str,
        extracted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Finalize check-in: save pain assessment and generate workout.

        Args:
            session_id: Check-in session ID
            extracted_data: Extracted pain data from conversation

        Returns:
            dict with completion status and workout
        """
        # Create pain assessment entity
        pain_assessment = PainAssessment(
            user_id=self.user_id,
            date=datetime.now(),
            pain_level=extracted_data["pain_level"],
            pain_locations=extracted_data["pain_locations"],
            triggers=extracted_data.get("triggers", []),
            medication_taken=extracted_data.get("medication_taken", False),
            notes=extracted_data.get("notes", "")
        )

        # Save pain assessment
        saved_assessment = self.pain_repo.save(pain_assessment)

        # Generate adapted workout using agent
        workout_prompt = f"""
Genera un workout adattato per oggi basato su:
- Dolore: {extracted_data['pain_level']}/10
- Localizzazioni: {', '.join(extracted_data['pain_locations'])}
- Trigger: {', '.join(extracted_data.get('triggers', []))}

Usa i tools per validare esercizi sicuri e fornisci un workout strutturato.
"""

        workout_result = await self.agent.process_daily_checkin(
            pain_level=extracted_data["pain_level"],
            pain_locations=extracted_data["pain_locations"],
            triggers=extracted_data.get("triggers", []),
            notes=extracted_data.get("notes", "")
        )

        # Save final agent message
        self.chat_repo.save_message(
            user_id=self.user_id,
            session_id=session_id,
            role="assistant",
            content=workout_result["output"],
            metadata={
                "timestamp": datetime.now().isoformat(),
                "session_type": "checkin",
                "step": "finalized",
                "pain_assessment_id": saved_assessment.id if hasattr(saved_assessment, 'id') else None
            }
        )

        return {
            "success": True,
            "session_id": session_id,
            "message": workout_result["output"],
            "completed": True,
            "pain_assessment_saved": True,
            "pain_assessment_id": saved_assessment.id if hasattr(saved_assessment, 'id') else None
        }

    def _extract_pain_data_from_history(
        self,
        history: list
    ) -> Dict[str, Any]:
        """
        Extract structured pain data from conversation history using NLP.

        Args:
            history: List of conversation messages

        Returns:
            dict with extracted data and completeness flag
        """
        extracted = {
            "pain_level": None,
            "pain_locations": [],
            "triggers": [],
            "notes": "",
            "complete": False
        }

        # Combine all user messages
        user_messages = [
            msg["content"] for msg in history
            if msg["role"] == "user"
        ]
        full_text = " ".join(user_messages).lower()

        # Extract pain level (0-10)
        pain_patterns = [
            r'dolore\s+(\d+)',
            r'(\d+)/10',
            r'(\d+)\s+su\s+10',
            r'livello\s+(\d+)'
        ]
        for pattern in pain_patterns:
            match = re.search(pattern, full_text)
            if match:
                pain_level = int(match.group(1))
                if 0 <= pain_level <= 10:
                    extracted["pain_level"] = pain_level
                    break

        # Extract pain locations
        location_keywords = {
            "lombare": ["lombare", "schiena bassa", "zona lombare"],
            "gluteo": ["gluteo", "natica"],
            "gamba": ["gamba", "coscia"],
            "ginocchio": ["ginocchio"],
            "caviglia": ["caviglia"],
            "spalla": ["spalla"],
            "collo": ["collo", "cervicale"],
            "anca": ["anca"]
        }

        for location, keywords in location_keywords.items():
            if any(kw in full_text for kw in keywords):
                extracted["pain_locations"].append(location)

        # Extract triggers
        trigger_keywords = {
            "seduto_prolungato": ["seduto", "sedia", "scrivania"],
            "flessione": ["piegamento", "flessione", "chinarsi"],
            "corsa": ["corsa", "correre", "running"],
            "sollevamento": ["sollevamento", "alzare", "deadlift"]
        }

        for trigger, keywords in trigger_keywords.items():
            if any(kw in full_text for kw in keywords):
                extracted["triggers"].append(trigger)

        # Extract notes
        extracted["notes"] = " ".join(user_messages)

        # Check if we have minimum required data
        extracted["complete"] = (
            extracted["pain_level"] is not None and
            len(extracted["pain_locations"]) > 0
        )

        return extracted

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get current status of check-in session.

        Args:
            session_id: Check-in session ID

        Returns:
            dict with session status and extracted data
        """
        history = self.chat_repo.get_session_history(session_id)
        extracted_data = self._extract_pain_data_from_history(history)

        return {
            "session_id": session_id,
            "message_count": len(history),
            "extracted_data": extracted_data,
            "completed": extracted_data["complete"]
        }
