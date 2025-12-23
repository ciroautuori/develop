from enum import Enum

class Sex(Enum):
    """User sex."""
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"

class ActivityLevel(Enum):
    """User's physical activity level."""
    SEDENTARY = "sedentario"
    LIGHTLY_ACTIVE = "leggermente_attivo"
    MODERATELY_ACTIVE = "moderatamente_attivo"
    VERY_ACTIVE = "molto_attivo"
    ATHLETE = "atleta"
