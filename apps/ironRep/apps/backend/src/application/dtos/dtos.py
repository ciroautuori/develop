"""
Data Transfer Objects (DTOs)

Aggregates DTOs from specific modules for backward compatibility.
Refactored to split logic into separate files.
"""

from .user_dtos import UserDTO, OnboardingRequestDTO
from .workout_dtos import WorkoutDTO, KPIDTO, WeeklyReviewResponseDTO
from .medical_dtos import PainAssessmentDTO, DailyCheckInResponseDTO
from .chat_dtos import ChatMessageDTO, AskCoachResponseDTO
from .biometrics_dtos import BiometricEntryDTO, RecordBiometricRequestDTO
