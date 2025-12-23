"""
Agent Orchestrator Service

Coordinates the flow between agents: Wizard → Medical → Coach → Nutrition.
Manages constraints passing and decision logging.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


from src.domain.entities.workout_session import WorkoutPhase
from src.domain.entities.medical import MedicalReport, ClearanceLevel, ConstraintType
from src.domain.services.nutrition_calculator_service import NutritionCalculatorService


@dataclass
class OrchestrationDecision:
    """Log of an orchestration decision."""
    timestamp: datetime
    agent_from: str
    agent_to: str
    decision_type: str
    data_passed: Dict[str, Any]
    reasoning: str


class AgentOrchestrator:
    """
    Orchestrates the flow between agents.

    Pipeline:
    1. Wizard → collects user context → stores in RAG
    2. Medical → assesses pain/recovery → generates MedicalReport
    3. Coach → receives constraints → generates safe workout
    4. Nutrition → receives activity level → generates meal plan
    """

    def __init__(
        self,
        medical_agent=None,
        workout_coach=None,
        nutrition_agent=None,
        user_context_rag=None,
        db=None,
        coach_repo=None,
        nutrition_repo=None,
        medical_repo=None,
        exercise_library=None
    ):
        self.medical_agent = medical_agent
        self.workout_coach = workout_coach
        self.nutrition_agent = nutrition_agent
        self.user_context_rag = user_context_rag
        self.db = db  # Database session for saving plans

        # Repositories for saving generated plans to DB
        self.coach_repo = coach_repo
        self.nutrition_repo = nutrition_repo
        self.medical_repo = medical_repo
        self.exercise_library = exercise_library

        # Decision log
        self._decisions: List[OrchestrationDecision] = []

    def _log_decision(
        self,
        agent_from: str,
        agent_to: str,
        decision_type: str,
        data: Dict[str, Any],
        reasoning: str
    ):
        """Log an orchestration decision."""
        decision = OrchestrationDecision(
            timestamp=datetime.now(),
            agent_from=agent_from,
            agent_to=agent_to,
            decision_type=decision_type,
            data_passed=data,
            reasoning=reasoning
        )
        self._decisions.append(decision)
        logger.info(f"🔄 Orchestration: {agent_from} → {agent_to} | {decision_type}")

    def generate_medical_report(
        self,
        user_id: str,
        pain_assessments: List[Any],
        user_profile: Optional[Any] = None
    ) -> MedicalReport:
        """
        Generate a MedicalReport from pain data.

        This is called before workout generation to establish constraints.
        """
        report = MedicalReport(user_id=user_id)

        if not pain_assessments:
            # No pain data - assume cautious approach
            report.clearance_level = ClearanceLevel.YELLOW
            report.constraints = [ConstraintType.REDUCE_INTENSITY.value]
            report.notes = "Nessun dato dolore recente - approccio cautelativo"
            return report

        # Analyze recent pain
        recent = pain_assessments[0] if pain_assessments else None
        avg_pain = sum(a.pain_level for a in pain_assessments) / len(pain_assessments)

        report.current_pain_level = recent.pain_level if recent else 0
        report.pain_locations = recent.pain_locations if recent else []

        # Determine pain trend
        if len(pain_assessments) >= 3:
            recent_avg = sum(a.pain_level for a in pain_assessments[:len(pain_assessments)//2]) / (len(pain_assessments)//2)
            older_avg = sum(a.pain_level for a in pain_assessments[len(pain_assessments)//2:]) / (len(pain_assessments)//2)
            if recent_avg < older_avg - 0.5:
                report.pain_trend = "improving"
            elif recent_avg > older_avg + 0.5:
                report.pain_trend = "worsening"
            else:
                report.pain_trend = "stable"

        # Set clearance level based on pain
        if avg_pain >= 7 or report.current_pain_level >= 8:
            report.clearance_level = ClearanceLevel.RED
            report.notes = "Dolore troppo alto - riposo consigliato"
        elif avg_pain >= 4 or report.current_pain_level >= 5:
            report.clearance_level = ClearanceLevel.YELLOW
        else:
            report.clearance_level = ClearanceLevel.GREEN

        # Determine phase
        if avg_pain >= 6:
            report.phase = WorkoutPhase.PHASE_1_DECOMPRESSION
        elif avg_pain >= 4:
            report.phase = WorkoutPhase.PHASE_2_STABILIZATION
        elif avg_pain >= 2:
            report.phase = WorkoutPhase.PHASE_3_STRENGTHENING
        else:
            report.phase = WorkoutPhase.PHASE_4_RETURN_TO_SPORT

        # Generate constraints based on pain locations
        constraints = []
        for location in report.pain_locations:
            loc_lower = location.lower()
            if "lombare" in loc_lower or "schiena" in loc_lower or "lower back" in loc_lower:
                constraints.extend([
                    ConstraintType.NO_FLEXION_UNDER_LOAD.value,
                    ConstraintType.NO_HEAVY_DEADLIFTS.value,
                    ConstraintType.NO_SPINAL_LOADING.value
                ])
                report.avoid_movements.extend(["deadlift pesante", "good morning", "stacco da terra"])

            if "sciatica" in loc_lower or "gamba" in loc_lower or "gluteo" in loc_lower:
                constraints.append(ConstraintType.AVOID_HIGH_IMPACT.value)
                report.avoid_movements.extend(["box jump", "running", "burpees"])

            if "ginocchio" in loc_lower or "knee" in loc_lower:
                constraints.extend([
                    ConstraintType.NO_DEEP_SQUATS.value,
                    ConstraintType.KNEE_FLEXION_MAX_90.value
                ])
                report.avoid_movements.extend(["squat profondo", "pistol squat", "lunges profondi"])

            if "spalla" in loc_lower or "shoulder" in loc_lower:
                constraints.extend([
                    ConstraintType.NO_OVERHEAD_PRESSING.value,
                    ConstraintType.NO_KIPPING.value
                ])
                report.avoid_movements.extend(["overhead press", "kipping pull-up", "snatch"])

        report.constraints = list(set(constraints))
        report.avoid_movements = list(set(report.avoid_movements))

        # Set intensity limits
        if report.clearance_level == ClearanceLevel.RED:
            report.max_intensity_percent = 0
            report.max_session_duration_minutes = 0
        elif report.clearance_level == ClearanceLevel.YELLOW:
            report.max_intensity_percent = 60
            report.max_session_duration_minutes = 30
        else:
            report.max_intensity_percent = 85
            report.max_session_duration_minutes = 60

        # Set recommended focus based on phase
        phase_focus = {
            WorkoutPhase.PHASE_1_DECOMPRESSION: ["mobilità", "respirazione", "decompressione spinale"],
            WorkoutPhase.PHASE_2_STABILIZATION: ["core stability", "attivazione glutei", "controllo motorio"],
            WorkoutPhase.PHASE_3_STRENGTHENING: ["forza isometrica", "progressione carico", "pattern movimento"],
            WorkoutPhase.PHASE_4_RETURN_TO_SPORT: ["potenza", "sport-specifico", "condizionamento"]
        }
        report.recommended_focus = phase_focus.get(report.phase, [])

        self._log_decision(
            agent_from="medical",
            agent_to="coach",
            decision_type="medical_report",
            data=report.to_dict(),
            reasoning=f"Pain level {report.current_pain_level}/10, trend {report.pain_trend}"
        )

        return report

    async def orchestrate_workout_generation(
        self,
        user_id: str,
        pain_assessments: List[Any],
        training_days: int = 4
    ) -> Dict[str, Any]:
        """
        Full orchestration: Medical assessment → Workout generation.

        Returns workout plan with medical constraints applied.
        """
        # Step 1: Generate medical report
        medical_report = self.generate_medical_report(user_id, pain_assessments)

        # Step 2: Check if training is allowed
        if not medical_report.is_safe_for_training():
            return {
                "success": False,
                "reason": "medical_clearance_denied",
                "medical_report": medical_report.to_dict(),
                "message": "Il livello di dolore attuale non permette l'allenamento. Riposo consigliato."
            }

        # Step 3: Generate workout with constraints
        if self.workout_coach:
            workout_result = await self.workout_coach.generate_weekly_program(
                user_id=user_id,
                medical_clearance={
                    "pain_level": medical_report.current_pain_level,
                    "phase": medical_report.phase.value,
                    "contraindications": medical_report.constraints,
                    "max_intensity": medical_report.max_intensity_percent,
                    "avoid_movements": medical_report.avoid_movements
                },
                training_days=training_days
            )

            self._log_decision(
                agent_from="orchestrator",
                agent_to="coach",
                decision_type="workout_generation",
                data={"training_days": training_days, "constraints": medical_report.constraints},
                reasoning="Generating workout with medical constraints"
            )

            return {
                "success": True,
                "medical_report": medical_report.to_dict(),
                "workout": workout_result,
                "constraints_applied": medical_report.constraints
            }

        return {
            "success": False,
            "reason": "coach_not_available",
            "medical_report": medical_report.to_dict()
        }

    def validate_exercise_against_constraints(
        self,
        exercise: Dict[str, Any],
        constraints: List[str]
    ) -> Dict[str, Any]:
        """
        Validate if an exercise is safe given the constraints.

        Returns validation result with reasoning.
        """
        exercise_name = exercise.get("name", "").lower()
        exercise_contraindications = exercise.get("contraindications", [])

        violations = []

        # Check each constraint
        for constraint in constraints:
            if constraint == ConstraintType.NO_SPINAL_LOADING.value:
                if any(word in exercise_name for word in ["deadlift", "squat", "row", "stacco"]):
                    violations.append(f"'{exercise_name}' carica la colonna vertebrale")

            if constraint == ConstraintType.NO_HEAVY_DEADLIFTS.value:
                if "deadlift" in exercise_name or "stacco" in exercise_name:
                    violations.append(f"'{exercise_name}' è uno stacco pesante")

            if constraint == ConstraintType.NO_OVERHEAD_PRESSING.value:
                if any(word in exercise_name for word in ["press", "jerk", "push", "snatch"]):
                    if "overhead" in exercise_name or "military" in exercise_name:
                        violations.append(f"'{exercise_name}' è un movimento overhead")

            if constraint == ConstraintType.AVOID_HIGH_IMPACT.value:
                if any(word in exercise_name for word in ["jump", "run", "burpee", "box"]):
                    violations.append(f"'{exercise_name}' è ad alto impatto")

        is_safe = len(violations) == 0

        return {
            "exercise": exercise_name,
            "is_safe": is_safe,
            "violations": violations,
            "recommendation": "Esercizio approvato" if is_safe else f"Sostituire: {', '.join(violations)}"
        }

    def get_decision_log(self) -> List[Dict[str, Any]]:
        """Get log of all orchestration decisions."""
        return [
            {
                "timestamp": d.timestamp.isoformat(),
                "from": d.agent_from,
                "to": d.agent_to,
                "type": d.decision_type,
                "reasoning": d.reasoning
            }
            for d in self._decisions
        ]

    async def initialize_new_user(
        self,
        user_id: str,
        user_context: Dict[str, Any],
        agent_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initialize agents for a new user post-onboarding.

        Respects user's modular choices:
        - medical_mode: injury_recovery, wellness_tips, or disabled
        - coach_mode: crossfit, bodybuilding, powerlifting, running, etc.
        - nutrition_mode: full_diet_plan, recipes_only, tips_tracking, or disabled

        All agents remain available even if user chose minimal setup.

        Args:
            user_id: User identifier
            user_context: Collected data from wizard/onboarding
            agent_config: Modular agent configuration from wizard

        Returns:
            Dict with all generated initial plans based on user preferences
        """
        agent_config = agent_config or {}

        self._log_decision(
            agent_from="orchestrator",
            agent_to="all_agents",
            decision_type="user_initialization",
            data={"user_id": user_id, "agent_config": agent_config},
            reasoning=f"New user onboarding complete. Medical: {agent_config.get('medical_mode')}, "
                      f"Coach: {agent_config.get('coach_mode')}, Nutrition: {agent_config.get('nutrition_mode')}"
        )

        result = {
            "user_id": user_id,
            "success": True,
            "agent_config": agent_config,
            "medical_assessment": None,
            "initial_workout": None,
            "nutrition_plan": None,
            "agents_available": ["medical", "coach", "nutrition"],  # All always available
            "errors": []
        }

        # Extract pain data
        has_injury = agent_config.get("has_injury", False)
        medical_mode = agent_config.get("medical_mode", "wellness_tips")
        coach_mode = agent_config.get("coach_mode", "general_fitness")
        nutrition_mode = agent_config.get("nutrition_mode", "tips_tracking")
        sport_type = agent_config.get("sport_type")

        pain_level = user_context.get("pain_level", 0) if has_injury else 0
        pain_locations = user_context.get("pain_locations", []) if has_injury else []
        diagnosis = user_context.get("diagnosis", "") if has_injury else ""

        # ============ MEDICAL AGENT ============
        # Always generate some level of medical context
        medical_mode_value = medical_mode.value if hasattr(medical_mode, 'value') else str(medical_mode)

        try:
            if medical_mode_value == "injury_recovery" and has_injury:
                # Full medical assessment for injury recovery
                medical_report = self._generate_initial_medical_report(
                    user_id=user_id,
                    pain_level=pain_level,
                    pain_locations=pain_locations,
                    diagnosis=diagnosis,
                    user_context=user_context
                )
                result["medical_assessment"] = medical_report.to_dict()
                result["medical_assessment"]["mode"] = "injury_recovery"

                self._log_decision(
                    agent_from="medical",
                    agent_to="orchestrator",
                    decision_type="initial_assessment_injury",
                    data=medical_report.to_dict(),
                    reasoning=f"Injury recovery mode: Phase {medical_report.phase.value}, Pain {pain_level}/10"
                )
            elif medical_mode_value != "disabled":
                # Wellness mode - light assessment, tips available
                wellness_report = MedicalReport(user_id=user_id)
                wellness_report.clearance_level = ClearanceLevel.GREEN
                wellness_report.phase = WorkoutPhase.PHASE_4_RETURN_TO_SPORT
                wellness_report.current_pain_level = 0
                wellness_report.max_intensity_percent = 100
                wellness_report.max_session_duration_minutes = 90
                wellness_report.notes = "No active injuries. Available for wellness tips and prevention advice."
                wellness_report.recommended_focus = ["prevenzione", "mobilità", "recovery"]

                result["medical_assessment"] = wellness_report.to_dict()
                result["medical_assessment"]["mode"] = "wellness_tips"

                self._log_decision(
                    agent_from="medical",
                    agent_to="orchestrator",
                    decision_type="initial_assessment_wellness",
                    data=wellness_report.to_dict(),
                    reasoning="Wellness mode: No injuries, available for general health tips"
                )
        except Exception as e:
            logger.error(f"Medical assessment failed: {e}")
            result["errors"].append(f"Medical: {str(e)}")

        # ============ COACH AGENT ============
        # Generate workout based on sport type and medical clearance
        coach_mode_value = coach_mode.value if hasattr(coach_mode, 'value') else str(coach_mode)

        if result.get("medical_assessment") and self.workout_coach:
            medical_report = result["medical_assessment"]
            clearance = medical_report.get("clearance_level", "green")

            if clearance != "red":
                try:
                    training_days = user_context.get("training_days", 3)

                    # Customize workout based on sport type
                    workout = await self.workout_coach.generate_weekly_program(
                        user_id=user_id,
                        medical_clearance={
                            "pain_level": pain_level,
                            "phase": medical_report.get("phase"),
                            "contraindications": medical_report.get("constraints", []),
                            "max_intensity": medical_report.get("max_intensity_percent", 60),
                            "avoid_movements": medical_report.get("avoid_movements", [])
                        },
                        training_days=training_days,
                        sport_type=sport_type or coach_mode_value  # Pass sport type
                    )
                    result["initial_workout"] = workout
                    result["initial_workout"]["sport_type"] = sport_type or coach_mode_value

                    # 🔥 SAVE PLAN TO DATABASE
                    if self.coach_repo and workout:
                        try:
                            from datetime import datetime

                            week_num = workout.get("week_number", 1)
                            sessions = workout.get("sessions", [])

                            plan = self.coach_repo.create_coach_plan(
                                user_id=user_id,
                                week_number=week_num,
                                year=datetime.now().year,
                                name=f"{sport_type or coach_mode_value} Program - Week {week_num}",
                                focus=workout.get("focus", "General conditioning"),
                                sport_type=sport_type or coach_mode_value,
                                sessions=sessions,
                                medical_constraints=medical_report.get("constraints"),
                                max_intensity=medical_report.get("max_intensity_percent", 100)
                            )
                            logger.info(f"✅ Coach plan saved to DB for user {user_id} - ID: {plan.id}")
                        except Exception as save_error:
                            logger.error(f"Failed to save coach plan to DB: {save_error}")

                    self._log_decision(
                        agent_from="coach",
                        agent_to="orchestrator",
                        decision_type="initial_workout",
                        data={"training_days": training_days, "sport_type": sport_type or coach_mode_value},
                        reasoning=f"Generated {sport_type or coach_mode_value} workout program"
                    )
                except Exception as e:
                    logger.error(f"Workout generation failed: {e}")
                    result["errors"].append(f"Workout: {str(e)}")
            else:
                result["initial_workout"] = {
                    "status": "rest_required",
                    "message": "Riposo consigliato. Il coach genererà il programma quando il dolore diminuirà.",
                    "sport_type": sport_type or coach_mode_value
                }

        # ============ NUTRITION AGENT ============
        # Generate nutrition plan based on user's preference
        nutrition_mode_value = nutrition_mode.value if hasattr(nutrition_mode, 'value') else str(nutrition_mode)

        if nutrition_mode_value != "disabled" and self.nutrition_agent:
            try:
                if nutrition_mode_value == "full_diet_plan":
                    # Complete structured diet plan
                    nutrition_plan = await self.nutrition_agent.generate_weekly_plan({
                        "goal": user_context.get("nutrition_goal", "maintenance"),
                        "diet_type": user_context.get("diet_type", "balanced"),
                        "activity_level": user_context.get("activity_level", "moderate"),
                        "target_calories": user_context.get("target_calories"),
                        "injuries": diagnosis,
                        "sport_type": sport_type,
                        "plan_type": "full"
                    })
                    nutrition_plan["mode"] = "full_diet_plan"

                    # 🔥 SAVE NUTRITION PLAN TO DATABASE
                    if self.nutrition_repo and nutrition_plan:
                        try:
                            from src.domain.entities.nutrition import NutritionPlan, DietType, GoalType, MacroNutrients
                            from datetime import datetime

                            # Calculate target macros if not provided
                            target_calories = nutrition_plan.get("daily_calories", 2200)
                            protein_g = int(target_calories * 0.3 / 4)  # 30% from protein
                            carbs_g = int(target_calories * 0.4 / 4)    # 40% from carbs
                            fat_g = int(target_calories * 0.3 / 9)      # 30% from fat

                            goal_map = {
                                "weight_loss": GoalType.WEIGHT_LOSS,
                                "maintenance": GoalType.MAINTENANCE,
                                "muscle_gain": GoalType.MUSCLE_GAIN,
                                "deficit": GoalType.WEIGHT_LOSS,
                                "surplus": GoalType.MUSCLE_GAIN
                            }

                            diet_map = {
                                "balanced": DietType.BALANCED,
                                "keto": DietType.KETO,
                                "paleo": DietType.PALEO,
                                "vegan": DietType.VEGAN,
                                "vegetarian": DietType.VEGETARIAN,
                                "high_protein": DietType.HIGH_PROTEIN,
                                "mediterranean": DietType.MEDITERRANEAN
                            }

                            goal_str = user_context.get("nutrition_goal", "maintenance")
                            diet_str = user_context.get("diet_type", "balanced")

                            plan = NutritionPlan(
                                user_id=user_id,
                                goal=goal_map.get(goal_str, GoalType.MAINTENANCE),
                                diet_type=diet_map.get(diet_str, DietType.BALANCED),
                                target_macros=MacroNutrients(
                                    protein_g=protein_g,
                                    carbs_g=carbs_g,
                                    fat_g=fat_g,
                                    calories_kcal=target_calories
                                ),
                                weekly_schedule=nutrition_plan.get("weekly_schedule", {}),
                                created_at=datetime.now()
                            )
                            self.nutrition_repo.save_plan(plan)
                            logger.info(f"✅ Nutrition plan saved to DB for user {user_id}")
                        except Exception as save_error:
                            logger.error(f"Failed to save nutrition plan to DB: {save_error}")

                elif nutrition_mode_value == "recipes_only":
                    # Just recipes, no structured plan
                    nutrition_plan = await self.nutrition_agent.get_recipe_suggestions({
                        "diet_type": user_context.get("diet_type", "balanced"),
                        "goal": user_context.get("nutrition_goal", "maintenance"),
                        "count": 5
                    })
                    nutrition_plan = {
                        "mode": "recipes_only",
                        "recipes": nutrition_plan,
                        "message": "Ecco alcune ricette personalizzate. Chiedi sempre nuove idee!"
                    }

                else:  # tips_tracking
                    # Tips and tracking setup
                    nutrition_plan = {
                        "mode": "tips_tracking",
                        "tips": [
                            "Bevi almeno 2L di acqua al giorno",
                            "Mangia proteine ad ogni pasto",
                            "Verdure in ogni pasto principale",
                            "Carboidrati complessi prima dell'allenamento"
                        ],
                        "tracking_enabled": True,
                        "message": "Tracking pasti attivo. Registra i tuoi pasti per ricevere consigli personalizzati."
                    }

                result["nutrition_plan"] = nutrition_plan

                self._log_decision(
                    agent_from="nutrition",
                    agent_to="orchestrator",
                    decision_type="initial_nutrition",
                    data={"mode": nutrition_mode_value},
                    reasoning=f"Nutrition mode: {nutrition_mode_value}"
                )
            except Exception as e:
                logger.error(f"Nutrition plan failed: {e}")
                result["errors"].append(f"Nutrition: {str(e)}")
        else:
            result["nutrition_plan"] = {
                "mode": "disabled",
                "message": "Nutrizionista disabilitato. Puoi attivarlo quando vuoi dalle impostazioni."
            }

        result["success"] = len(result["errors"]) == 0

        # ============ SAVE PLANS TO DATABASE ============
        try:
            await self._save_initial_plans(
                user_id=user_id,
                user_context=user_context,
                agent_config=agent_config,
                medical_data=result.get("medical_assessment"),
                coach_data=result.get("initial_workout"),
                nutrition_data=result.get("nutrition_plan")
            )
            logger.info(f"Initial plans saved for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to save initial plans: {e}")
            result["errors"].append(f"Save plans: {str(e)}")

        return result

    async def _save_initial_plans(
        self,
        user_id: str,
        user_context: Dict[str, Any],
        agent_config: Dict[str, Any],
        medical_data: Optional[Dict] = None,
        coach_data: Optional[Dict] = None,
        nutrition_data: Optional[Dict] = None
    ):
        """Save generated plans to database."""
        if not self.db:
            logger.warning("No database session available for saving plans")
            return

        from src.infrastructure.persistence.repositories.weekly_plans_repository import (
            WeeklyPlansRepository,
            get_week_number
        )

        repo = WeeklyPlansRepository(self.db)
        week_num, year = get_week_number(datetime.now())

        # Save coach plan
        coach_plan_id = None
        if coach_data and coach_data.get("status") != "rest_required":
            try:
                training_days = user_context.get("training_days", 4)
                sessions = []
                days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

                for i, day in enumerate(days):
                    if i < training_days:
                        sessions.append({
                            "day": day,
                            "name": f"Session {i + 1}",
                            "type": coach_data.get("sport_type", "general"),
                            "duration": user_context.get("session_duration", 60),
                            "exercises": [],  # Would be filled by AI
                            "completed": False
                        })
                    else:
                        sessions.append({
                            "day": day,
                            "name": "Rest",
                            "type": "rest",
                            "completed": True
                        })

                coach_plan = repo.create_coach_plan(
                    user_id=user_id,
                    week_number=week_num,
                    year=year,
                    name=f"Week {week_num} Program",
                    focus=user_context.get("primary_goal", "general_fitness"),
                    sport_type=coach_data.get("sport_type", "general"),
                    sessions=sessions,
                    medical_constraints=medical_data.get("constraints") if medical_data else None,
                    max_intensity=medical_data.get("max_intensity_percent", 100) if medical_data else 100
                )
                coach_plan_id = coach_plan.id
            except Exception as e:
                logger.error(f"Failed to save coach plan: {e}")

        # Save medical protocol
        medical_plan_id = None
        if medical_data and medical_data.get("mode") == "injury_recovery":
            try:
                phase_str = medical_data.get("phase", WorkoutPhase.PHASE_1_DECOMPRESSION.value)
                # Extract phase number safely
                phase_num = 1
                if "Fase" in phase_str:
                    try:
                        phase_num = int(phase_str.split("Fase ")[1].split(":")[0])
                    except:
                        pass
                elif "phase_" in phase_str:
                    try:
                        phase_num = int(phase_str.split("_")[1])
                    except:
                        pass

                # Get exercises from library
                daily_exercises = []
                if self.exercise_library:
                    # Try exact match
                    try:
                        exercises = self.exercise_library.get_exercises_for_phase(phase_str)
                        # Filter for mobility/rehab
                        mobility = [ex for ex in exercises if ex.category == "mobility"]
                        # If empty, try finding any mobility
                        if not mobility:
                            all_ex = self.exercise_library.get_all_exercises()
                            mobility = [ex for ex in all_ex if ex.category == "mobility"]

                        # Take top 3 suitable
                        selected = mobility[:3]
                        daily_exercises = [{"name": ex.name, "duration": "2 min", "sets": ex.sets, "reps": ex.reps} for ex in selected]
                    except Exception as lib_err:
                        logger.warning(f"Error accessing exercise library: {lib_err}")

                # Fallback exercises if library failed or empty
                if not daily_exercises:
                    daily_exercises = [
                        {"name": "Respirazione diaframmatica", "duration": "3 min", "sets": 1, "reps": "10 respiri"},
                        {"name": "Cat-Cow", "duration": "2 min", "sets": 2, "reps": "10"},
                    ]

                protocol = repo.create_medical_protocol(
                    user_id=user_id,
                    week_number=week_num,
                    year=year,
                    phase=phase_str,
                    phase_number=phase_num,
                    daily_exercises=daily_exercises,
                    restrictions=medical_data.get("constraints", []),
                    starting_pain=user_context.get("pain_level", 0)
                )
                medical_plan_id = protocol.id
            except Exception as e:
                logger.error(f"Failed to save medical protocol: {e}")

        # Save nutrition plan
        nutrition_plan_id = None
        if nutrition_data and nutrition_data.get("mode") != "disabled":
            try:
                goal = user_context.get("nutrition_goal", "maintenance")
                base_calories = 2200 # Fallback default
                if "tdee" in user_context:
                    base_calories = int(user_context["tdee"])
                
                targets = NutritionCalculatorService.calculate_targets(goal, base_calories)
                
                plan = repo.create_nutrition_plan(
                    user_id=user_id,
                    week_number=week_num,
                    year=year,
                    goal=goal,
                    daily_calories=targets["daily_calories"],
                    daily_protein=targets["daily_protein"],
                    daily_carbs=targets["daily_carbs"],
                    daily_fat=targets["daily_fat"],
                    diet_type=user_context.get("diet_type"),
                    excluded_foods=user_context.get("allergies"),
                    preferred_foods=user_context.get("preferred_foods")
                )
                nutrition_plan_id = plan.id
            except Exception as e:
                logger.error(f"Failed to save nutrition plan: {e}")

        # Create unified weekly plan
        try:
            week_plan = repo.create_week_plan(
                user_id=user_id,
                week_number=week_num,
                year=year,
                coach_plan_id=coach_plan_id,
                medical_plan_id=medical_plan_id,
                nutrition_plan_id=nutrition_plan_id
            )

            # Update summaries
            repo.update_week_plan_summaries(
                plan_id=week_plan.id,
                coach_summary={
                    "sessions": user_context.get("training_days", 4),
                    "sport": agent_config.get("sport_type"),
                    "status": "active"
                } if coach_plan_id else None,
                medical_summary={
                    "phase": medical_data.get("phase") if medical_data else None,
                    "pain_level": user_context.get("pain_level", 0),
                    "status": "active"
                } if medical_plan_id else None,
                nutrition_summary={
                    "goal": user_context.get("nutrition_goal", "maintenance"),
                    "calories": calories if nutrition_plan_id else None,
                    "status": "active"
                } if nutrition_plan_id else None
            )

            logger.info(f"Created weekly plan {week_plan.id} for week {week_num}/{year}")
        except Exception as e:
            logger.error(f"Failed to create weekly plan: {e}")

    def _generate_initial_medical_report(
        self,
        user_id: str,
        pain_level: int,
        pain_locations: List[str],
        diagnosis: str,
        user_context: Dict[str, Any]
    ) -> MedicalReport:
        """
        Generate initial medical report for new user.

        Args:
            user_id: User identifier
            pain_level: Current pain level 0-10
            pain_locations: List of pain locations
            diagnosis: Medical diagnosis if any
            user_context: Full user context from onboarding

        Returns:
            MedicalReport with initial assessment
        """
        report = MedicalReport(user_id=user_id)
        report.current_pain_level = pain_level
        report.pain_locations = pain_locations
        report.notes = f"Initial assessment. Diagnosis: {diagnosis}" if diagnosis else "Initial assessment"

        # Determine clearance level
        if pain_level >= 7:
            report.clearance_level = ClearanceLevel.RED
            report.notes += " - High pain, rest recommended"
        elif pain_level >= 4:
            report.clearance_level = ClearanceLevel.YELLOW
        else:
            report.clearance_level = ClearanceLevel.GREEN

        # Determine phase
        if pain_level >= 6:
            report.phase = WorkoutPhase.PHASE_1_DECOMPRESSION
        elif pain_level >= 4:
            report.phase = WorkoutPhase.PHASE_2_STABILIZATION
        elif pain_level >= 2:
            report.phase = WorkoutPhase.PHASE_3_STRENGTHENING
        else:
            report.phase = WorkoutPhase.PHASE_4_RETURN_TO_SPORT

        # Generate constraints based on diagnosis and pain locations
        constraints = []
        avoid_movements = []

        diagnosis_lower = diagnosis.lower() if diagnosis else ""

        # Spine-related conditions
        if any(term in diagnosis_lower for term in ["sciatica", "ernia", "lombalgia", "disco", "stenosi"]):
            constraints.extend([
                ConstraintType.NO_FLEXION_UNDER_LOAD.value,
                ConstraintType.NO_HEAVY_DEADLIFTS.value,
                ConstraintType.NO_SPINAL_LOADING.value
            ])
            avoid_movements.extend(["deadlift", "good morning", "jefferson curl", "sit-up"])

        # Location-based constraints
        for location in pain_locations:
            loc_lower = location.lower()

            if any(term in loc_lower for term in ["lombare", "schiena", "back", "lower_back"]):
                constraints.append(ConstraintType.NO_SPINAL_LOADING.value)
                avoid_movements.extend(["heavy squat", "rowing"])

            if any(term in loc_lower for term in ["ginocchio", "knee"]):
                constraints.extend([
                    ConstraintType.NO_DEEP_SQUATS.value,
                    ConstraintType.KNEE_FLEXION_MAX_90.value
                ])
                avoid_movements.extend(["pistol squat", "deep lunge"])

            if any(term in loc_lower for term in ["spalla", "shoulder"]):
                constraints.extend([
                    ConstraintType.NO_OVERHEAD_PRESSING.value,
                    ConstraintType.NO_KIPPING.value
                ])
                avoid_movements.extend(["snatch", "overhead press", "kipping pull-up"])

            if any(term in loc_lower for term in ["anca", "hip"]):
                constraints.append(ConstraintType.LIMIT_ROM.value)
                avoid_movements.extend(["deep squat", "wide stance"])

        report.constraints = list(set(constraints))
        report.avoid_movements = list(set(avoid_movements))

        # Set intensity limits based on clearance
        if report.clearance_level == ClearanceLevel.RED:
            report.max_intensity_percent = 0
            report.max_session_duration_minutes = 0
        elif report.clearance_level == ClearanceLevel.YELLOW:
            report.max_intensity_percent = 60
            report.max_session_duration_minutes = 30
        else:
            report.max_intensity_percent = 85
            report.max_session_duration_minutes = 60

        # Set recommended focus based on phase
        phase_focus = {
            WorkoutPhase.PHASE_1_DECOMPRESSION: ["mobilità", "respirazione", "decompressione"],
            WorkoutPhase.PHASE_2_STABILIZATION: ["core stability", "attivazione", "controllo motorio"],
            WorkoutPhase.PHASE_3_STRENGTHENING: ["forza", "progressione carico", "pattern movimento"],
            WorkoutPhase.PHASE_4_RETURN_TO_SPORT: ["potenza", "sport-specifico", "condizionamento"]
        }
        report.recommended_focus = phase_focus.get(report.phase, [])

        return report
