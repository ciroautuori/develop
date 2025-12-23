"""
Exercise Library

Manages exercise database loading and filtering.
"""
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ExerciseData:
    """Exercise data structure."""
    id: str
    name: str
    phases: List[str]
    category: str
    contraindications: List[str]
    coaching_cues: List[str]
    sets: int = 2
    reps: str = "10"
    rest_seconds: int = 60
    video_url: Optional[str] = None
    difficulty: str = "beginner"
    equipment: List[str] = None
    movement_pattern: Optional[str] = None
    progressions: List[str] = None
    regressions: List[str] = None
    sciatica_risk: Optional[str] = None
    modifications: List[str] = None

    def __post_init__(self):
        if self.equipment is None:
            self.equipment = []
        if self.progressions is None:
            self.progressions = []
        if self.regressions is None:
            self.regressions = []
        if self.modifications is None:
            self.modifications = []


class ExerciseLibrary:
    """
    Exercise library manager.

    Loads exercises from JSON and provides filtering/querying.
    """

    def __init__(self, exercises_file: str = "data/exercises.json"):
        self.exercises_file = exercises_file
        self.exercises: List[ExerciseData] = []
        self.load_exercises()

    def load_exercises(self):
        """Load exercises from JSON file."""
        if not os.path.exists(self.exercises_file):
            print(f"⚠️  Exercise file not found: {self.exercises_file}")
            self._create_default_exercises()
            return

        try:
            with open(self.exercises_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.exercises = [
                ExerciseData(**ex) for ex in data.get("exercises", [])
            ]

            print(f"✅ Loaded {len(self.exercises)} exercises")

        except Exception as e:
            print(f"❌ Error loading exercises: {e}")
            self._create_default_exercises()

    def get_exercises_for_phase(self, phase: str) -> List[Dict]:
        """Get exercises suitable for a rehabilitation phase."""
        filtered = [
            ex for ex in self.exercises
            if phase in ex.phase
        ]

        return [self._exercise_to_dict(ex) for ex in filtered]

    def get_safe_exercises(
        self,
        pain_locations: List[str],
        phase: Optional[str] = None
    ) -> List[Dict]:
        """
        Get exercises safe for given pain locations.

        Filters out exercises with contraindications matching pain locations.
        """
        safe = []

        for ex in self.exercises:
            # Check if any contraindication matches pain location
            is_safe = True
            for contraindication in ex.contraindications:
                for location in pain_locations:
                    if location.lower() in contraindication.lower():
                        is_safe = False
                        break

            # Check phase if specified
            if phase and phase not in ex.phases:
                is_safe = False

            if is_safe:
                safe.append(ex)

        return [self._exercise_to_dict(ex) for ex in safe]

    def filter_safe_exercises(
        self,
        exercises: List[Dict],
        pain_locations: List[str]
    ) -> List[Dict]:
        """Filter exercise list removing contraindicated ones."""
        safe = []

        for ex_dict in exercises:
            is_safe = True
            contraindications = ex_dict.get("contraindications", [])

            for contraindication in contraindications:
                for location in pain_locations:
                    if location.lower() in contraindication.lower():
                        is_safe = False
                        break

            if is_safe:
                safe.append(ex_dict)

        return safe

    def get_by_category(self, category: str) -> List[Dict]:
        """Get exercises by category."""
        filtered = [
            ex for ex in self.exercises
            if ex.category.lower() == category.lower()
        ]

        return [self._exercise_to_dict(ex) for ex in filtered]

    def get_by_id(self, exercise_id: str) -> Optional[Dict]:
        """Get specific exercise by ID."""
        for ex in self.exercises:
            if ex.id == exercise_id:
                return self._exercise_to_dict(ex)
        return None

    def _exercise_to_dict(self, ex: ExerciseData) -> Dict:
        """Convert ExerciseData to dict."""
        return {
            "id": ex.id,
            "name": ex.name,
            "phases": ex.phases,
            "category": ex.category,
            "contraindications": ex.contraindications,
            "coaching_cues": ex.coaching_cues,
            "sets": ex.sets,
            "reps": ex.reps,
            "rest_seconds": ex.rest_seconds,
            "video_url": ex.video_url,
            "difficulty": ex.difficulty,
            "equipment": ex.equipment
        }

    def _create_default_exercises(self):
        """Create default exercise set if file doesn't exist."""
        default_exercises = [
            ExerciseData(
                id="cat_cow",
                name="Cat-Cow Stretch",
                phases=["Fase 1: Decompressione"],
                category="mobility",
                contraindications=[],
                coaching_cues=[
                    "Mantieni colonna neutra",
                    "Respira profondamente",
                    "Movimento lento e controllato"
                ],
                sets=3,
                reps="10",
                rest_seconds=30
            ),
            ExerciseData(
                id="bird_dog",
                name="Bird Dog",
                phases=["Fase 1: Decompressione", "Fase 2: Stabilizzazione"],
                category="stability",
                contraindications=["estensione_lombare_eccessiva"],
                coaching_cues=[
                    "Core attivo",
                    "Movimento opposto braccio-gamba",
                    "Mantieni schiena piatta"
                ],
                sets=3,
                reps="8 per lato",
                rest_seconds=45
            ),
            ExerciseData(
                id="glute_bridge",
                name="Glute Bridge",
                phases=["Fase 2: Stabilizzazione"],
                category="strength",
                contraindications=[],
                coaching_cues=[
                    "Spingi attraverso i talloni",
                    "Glutei contratti in alto",
                    "Evita iperestensione lombare"
                ],
                sets=3,
                reps="12",
                rest_seconds=60
            ),
            ExerciseData(
                id="dead_bug",
                name="Dead Bug",
                phases=["Fase 1: Decompressione", "Fase 2: Stabilizzazione"],
                category="stability",
                contraindications=[],
                coaching_cues=[
                    "Lombare schiacciata a terra",
                    "Respirazione controllata",
                    "Movimento alternato"
                ],
                sets=3,
                reps="10 per lato",
                rest_seconds=45
            )
        ]

        self.exercises = default_exercises
        print(f"✅ Created {len(default_exercises)} default exercises")
