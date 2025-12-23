"""
Generate Workout Use Case

Generates adaptive workouts based on current pain state and phase.
"""
from typing import List
from datetime import datetime

from src.domain.entities.workout_session import WorkoutSession, WorkoutPhase, Exercise, PainImpact
from src.domain.repositories.workout_repository import IWorkoutRepository
from src.application.dtos.dtos import WorkoutDTO
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class GenerateWorkoutUseCase:
    """
    Use case for generating adaptive workouts.

    This uses exercise library, pain state, RAG knowledge base, and AI agent to create
    highly personalized workouts based on user profile and CrossFit knowledge.
    """

    def __init__(
        self,
        workout_repository: IWorkoutRepository,
        exercise_library,
        ai_agent,
        rag_service=None,  # Optional for backwards compatibility
        user_id: str = "default_user"
    ):

        self.workout_repository = workout_repository
        self.exercise_library = exercise_library
        self.ai_agent = ai_agent
        self.rag_service = rag_service
        self.user_id = user_id
        
        if not self.rag_service:
            logger.warning("RAG service not provided. Personalization will be limited.")

    async def generate_workout(
        self,
        current_pain: int,
        pain_locations: List[str],
        triggers: List[str],
        pain_analysis: dict,
        phase: WorkoutPhase = WorkoutPhase.PHASE_1_DECOMPRESSION
    ) -> WorkoutDTO:
        """
        Generate workout adapted to current pain state.

        Args:
            current_pain: Current pain level (0-10)
            pain_locations: List of pain locations
            triggers: Known pain triggers
            pain_analysis: Pain trend analysis
            phase: Current rehabilitation phase

        Returns:
            WorkoutDTO with adapted exercises
        """
        # Step 1: Determine workout adaptation strategy
        adaptation_strategy = self._determine_adaptation_strategy(current_pain)

        # Step 2: Get base exercises for phase
        base_exercises = self.exercise_library.get_exercises_for_phase(phase.value)

        # Step 3: Get RAG context for personalization
        rag_context = await self._get_rag_context(
            current_pain=current_pain,
            pain_locations=pain_locations,
            triggers=triggers,
            phase=phase
        )

        # Step 4: Filter out contraindicated exercises
        safe_exercises = self.exercise_library.filter_safe_exercises(
            base_exercises,
            pain_locations
        )

        # Step 5: Apply pain-based adaptations
        adapted_exercises = self._apply_adaptations(
            safe_exercises,
            adaptation_strategy,
            current_pain
        )

        # Step 6: Structure workout (warm-up, technical, conditioning, cool-down)
        structured_workout = self._structure_workout(
            adapted_exercises,
            phase
        )

        # Step 7: Create workout entity
        workout_session = WorkoutSession(
            session_id=self._generate_session_id(),
            user_id=self.user_id,
            date=datetime.now(),
            phase=phase,
            warm_up=structured_workout["warm_up"],
            technical_work=structured_workout["technical_work"],
            conditioning=structured_workout["conditioning"],
            cool_down=structured_workout["cool_down"],
            estimated_pain_impact=self._estimate_pain_impact(current_pain),
            contraindications=self._get_contraindications(pain_locations)
        )

        # Step 8: Save workout
        saved_workout = self.workout_repository.save(workout_session)

        # Step 9: Convert to DTO
        return self._entity_to_dto(saved_workout)

    def _determine_adaptation_strategy(self, pain_level: int) -> dict:
        """Determine how to adapt workout based on pain."""
        if pain_level >= 7:
            return {
                "type": "gentle_mobility_only",
                "intensity_reduction": 80,
                "focus": "decompression"
            }
        elif pain_level >= 5:
            return {
                "type": "moderate_reduction",
                "intensity_reduction": 50,
                "focus": "low_impact"
            }
        elif pain_level >= 3:
            return {
                "type": "mild_reduction",
                "intensity_reduction": 20,
                "focus": "proper_form"
            }
        else:
            return {
                "type": "normal",
                "intensity_reduction": 0,
                "focus": "progression"
            }

    async def _get_rag_context(
        self,
        current_pain: int,
        pain_locations: List[str],
        triggers: List[str],
        phase
    ) -> dict:
        """
        Get RAG context for personalized recommendations using knowledge base.

        Retrieves relevant medical and CrossFit knowledge based on:
        - Current pain level and locations
        - Rehabilitation phase
        - Known triggers

        Returns:
            dict with exercise_guidelines, phase_recommendations, safety_notes
        """
        if not self.rag_service:
            return {
                "exercise_guidelines": "",
                "phase_recommendations": "",
                "safety_notes": ""
            }

        try:
            # Build comprehensive query for RAG
            query_parts = [
                f"Pain level {current_pain}/10",
                f"Phase: {phase.value}",
                f"Pain locations: {', '.join(pain_locations)}" if pain_locations else "",
                f"Triggers: {', '.join(triggers)}" if triggers else "",
                "Safe exercises and modifications",
                "Contraindications",
                "CrossFit movement standards"
            ]
            query = " ".join(filter(None, query_parts))

            # Retrieve relevant context (top 8 chunks)
            results = self.rag_service.retrieve_context(query, k=8)

            if not results:
                return {
                    "exercise_guidelines": "",
                    "phase_recommendations": "",
                    "safety_notes": ""
                }

            # Organize results by category
            exercise_guidelines = []
            phase_recommendations = []
            safety_notes = []

            for result in results:
                content = result['content']
                metadata = result.get('metadata', {})

                # Categorize based on content and metadata
                if 'contraindication' in content.lower() or 'avoid' in content.lower():
                    safety_notes.append(content)
                elif 'phase' in content.lower() or 'progression' in content.lower():
                    phase_recommendations.append(content)
                else:
                    exercise_guidelines.append(content)

            return {
                "exercise_guidelines": "\n\n".join(exercise_guidelines[:3]),
                "phase_recommendations": "\n\n".join(phase_recommendations[:2]),
                "safety_notes": "\n\n".join(safety_notes[:3])
            }

        except Exception as e:
            logger.warning(f"Error retrieving RAG context: {e}")
            return {
                "exercise_guidelines": "",
                "phase_recommendations": "",
                "safety_notes": ""
            }

    def _apply_adaptations(
        self,
        exercises: List[dict],
        strategy: dict,
        pain_level: int
    ) -> List[dict]:
        """Apply adaptations to exercises based on strategy."""
        adapted = []

        for exercise in exercises:
            adapted_exercise = exercise.copy()

            # Reduce intensity based on strategy
            if strategy["intensity_reduction"] > 0:
                reduction = 1 - (strategy["intensity_reduction"] / 100)

                # Reduce sets or reps
                if "sets" in adapted_exercise:
                    adapted_exercise["sets"] = max(1, int(adapted_exercise["sets"] * reduction))

                # Add modification notes
                adapted_exercise["notes"] = f"Ridotto {strategy['intensity_reduction']}% per dolore {pain_level}/10"

            # Add coaching cues based on focus
            if strategy["focus"] == "decompression":
                adapted_exercise.setdefault("coaching_cues", []).append(
                    "Focus su decompressione e respirazione profonda"
                )

            adapted.append(adapted_exercise)

        return adapted

    def _structure_workout(self, exercises: List[dict], phase: WorkoutPhase) -> dict:
        """Structure exercises into workout sections."""
        # This is simplified - in production would use more sophisticated logic
        mobility_exercises = [ex for ex in exercises if ex.get("category") == "mobility"]
        strength_exercises = [ex for ex in exercises if ex.get("category") == "strength"]

        return {
            "warm_up": self._convert_to_exercise_entities(mobility_exercises[:3]),
            "technical_work": self._convert_to_exercise_entities(strength_exercises[:4]),
            "conditioning": self._convert_to_exercise_entities(strength_exercises[4:6]),
            "cool_down": self._convert_to_exercise_entities(mobility_exercises[3:5])
        }

    def _convert_to_exercise_entities(self, exercises: List[dict]) -> List[Exercise]:
        """Convert exercise dicts to Exercise value objects."""
        return [
            Exercise(
                name=ex.get("name", "Unknown"),
                sets=ex.get("sets", 2),
                reps=ex.get("reps", "10"),
                rest_seconds=ex.get("rest_seconds", 60),
                notes=ex.get("notes", ""),
                coaching_cues=ex.get("coaching_cues", []),
                video_url=ex.get("video_url") or f"https://www.youtube.com/results?search_query={ex.get('name', '').replace(' ', '+')}+exercise"
            )
            for ex in exercises
        ]

    def _estimate_pain_impact(self, current_pain: int) -> PainImpact:
        """Estimate expected pain impact of workout."""
        if current_pain >= 7:
            return PainImpact.VERY_LOW
        elif current_pain >= 5:
            return PainImpact.LOW
        elif current_pain >= 3:
            return PainImpact.MEDIUM_LOW
        else:
            return PainImpact.MEDIUM

    def _get_contraindications(self, pain_locations: List[str]) -> List[str]:
        """Get movement contraindications based on pain locations."""
        contraindications = []

        if "lombare" in pain_locations:
            contraindications.extend(["flessione_profonda", "torsione_carico"])

        if any("gluteo" in loc for loc in pain_locations):
            contraindications.append("estensione_anca_massima")

        if any("coscia" in loc for loc in pain_locations):
            contraindications.append("squat_profondo")

        return contraindications

    def _generate_session_id(self) -> str:
        """Generate session ID (e.g., W1D1 for Week 1 Day 1)."""
        # Simplified - would calculate based on user profile
        return f"W1D{datetime.now().day}"

    def _entity_to_dto(self, workout: WorkoutSession) -> WorkoutDTO:
        """Convert workout entity to DTO."""
        return WorkoutDTO(
            session_id=workout.session_id,
            date=workout.date.isoformat(),
            phase=workout.phase.value,
            warm_up=[ex.to_dict() for ex in workout.warm_up],
            technical_work=[ex.to_dict() for ex in workout.technical_work],
            conditioning=[ex.to_dict() for ex in workout.conditioning],
            cool_down=[ex.to_dict() for ex in workout.cool_down],
            estimated_pain_impact=workout.estimated_pain_impact.value,
            contraindications=workout.contraindications,
            total_exercises=workout.get_total_exercises(),
            estimated_duration_minutes=30 + (workout.get_total_exercises() * 3)
        )
