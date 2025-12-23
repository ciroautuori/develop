"""
Workout Template Service

Provides default workout templates and fallback exercises.
"""
from typing import List, Dict, Optional

class WorkoutTemplateService:
    """Service for retrieving default workout templates."""

    @staticmethod
    def get_default_exercises(session_index: int, focus: Optional[str] = None) -> List[Dict]:
        """
        Get default exercises based on session index and focus.
        Provides sensible fallback when AI generation fails.
        """
        # Standard templates (Split: Lower, Upper Push, Upper Pull, Full Body)
        templates = {
            0: [  # Day 1 - Lower body
                {"name": "Back Squat", "sets": 4, "reps": "8", "rest_seconds": 120, "notes": "Focus on depth", "coaching_cues": ["Chest up", "Knees out"], "completed": False},
                {"name": "Romanian Deadlift", "sets": 3, "reps": "10", "rest_seconds": 90, "notes": "", "coaching_cues": ["Hinge at hips", "Keep bar close"], "completed": False},
                {"name": "Walking Lunges", "sets": 3, "reps": "12/leg", "rest_seconds": 60, "notes": "", "coaching_cues": ["Upright torso"], "completed": False},
                {"name": "Leg Press", "sets": 3, "reps": "12", "rest_seconds": 60, "notes": "", "coaching_cues": [], "completed": False},
            ],
            1: [  # Day 2 - Upper body push
                {"name": "Bench Press", "sets": 4, "reps": "8", "rest_seconds": 120, "notes": "", "coaching_cues": ["Arch back", "Leg drive"], "completed": False},
                {"name": "Overhead Press", "sets": 3, "reps": "10", "rest_seconds": 90, "notes": "", "coaching_cues": ["Core tight"], "completed": False},
                {"name": "Incline Dumbbell Press", "sets": 3, "reps": "12", "rest_seconds": 60, "notes": "", "coaching_cues": [], "completed": False},
                {"name": "Tricep Dips", "sets": 3, "reps": "12", "rest_seconds": 60, "notes": "", "coaching_cues": [], "completed": False},
            ],
            2: [  # Day 3 - Upper body pull
                {"name": "Pull-ups", "sets": 4, "reps": "8", "rest_seconds": 120, "notes": "Use band if needed", "coaching_cues": ["Full ROM"], "completed": False},
                {"name": "Barbell Row", "sets": 3, "reps": "10", "rest_seconds": 90, "notes": "", "coaching_cues": ["Elbows back"], "completed": False},
                {"name": "Face Pulls", "sets": 3, "reps": "15", "rest_seconds": 60, "notes": "", "coaching_cues": [], "completed": False},
                {"name": "Bicep Curls", "sets": 3, "reps": "12", "rest_seconds": 60, "notes": "", "coaching_cues": [], "completed": False},
            ],
            3: [  # Day 4 - Full body/conditioning
                {"name": "Deadlift", "sets": 4, "reps": "5", "rest_seconds": 180, "notes": "Heavy", "coaching_cues": ["Brace core", "Push floor away"], "completed": False},
                {"name": "Push-ups", "sets": 3, "reps": "15", "rest_seconds": 60, "notes": "", "coaching_cues": [], "completed": False},
                {"name": "Kettlebell Swings", "sets": 3, "reps": "15", "rest_seconds": 60, "notes": "", "coaching_cues": ["Hip hinge"], "completed": False},
                {"name": "Plank", "sets": 3, "reps": "45s", "rest_seconds": 45, "notes": "", "coaching_cues": [], "completed": False},
            ],
        }

        # CrossFit specific override
        if focus and "crossfit" in focus.lower():
            templates = {
                0: [
                    {"name": "Back Squat", "sets": 5, "reps": "5", "rest_seconds": 180, "notes": "Build to heavy", "coaching_cues": [], "completed": False},
                    {"name": "AMRAP 12min: 10 Thrusters, 15 Box Jumps", "sets": 1, "reps": "AMRAP", "rest_seconds": 0, "notes": "RX: 43/30kg", "coaching_cues": [], "completed": False},
                ],
                1: [
                    {"name": "Power Clean", "sets": 5, "reps": "3", "rest_seconds": 120, "notes": "Technique focus", "coaching_cues": [], "completed": False},
                    {"name": "For Time: 21-15-9 Pull-ups, Push-ups, Air Squats", "sets": 1, "reps": "For Time", "rest_seconds": 0, "notes": "", "coaching_cues": [], "completed": False},
                ],
                2: [
                    {"name": "Deadlift", "sets": 5, "reps": "3", "rest_seconds": 180, "notes": "Heavy singles", "coaching_cues": [], "completed": False},
                    {"name": "EMOM 10min: 5 Burpees", "sets": 1, "reps": "EMOM", "rest_seconds": 0, "notes": "", "coaching_cues": [], "completed": False},
                ],
                3: [
                    {"name": "Overhead Squat", "sets": 5, "reps": "5", "rest_seconds": 120, "notes": "Mobility work first", "coaching_cues": [], "completed": False},
                    {"name": "3 Rounds: 400m Run, 15 KB Swings, 10 Pull-ups", "sets": 1, "reps": "3 Rounds", "rest_seconds": 0, "notes": "", "coaching_cues": [], "completed": False},
                ],
            }

        return templates.get(session_index % 4, templates[0])
