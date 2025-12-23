"""
Dependency Injection Container

Manages dependencies and provides them to application layers.
"""
import os
from typing import Optional
from sqlalchemy.orm import Session

from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.config.settings import settings
from src.infrastructure.persistence.repositories.pain_repository_impl import PainRepositoryImpl
from src.infrastructure.persistence.repositories.workout_repository_impl import WorkoutRepositoryImpl
from src.infrastructure.persistence.repositories.kpi_repository_impl import KPIRepositoryImpl
from src.infrastructure.persistence.repositories.user_repository_impl import UserRepositoryImpl
from src.infrastructure.persistence.repositories.biometric_repository_impl import BiometricRepositoryImpl
from src.infrastructure.persistence.repositories.chat_repository_impl import ChatRepositoryImpl
from src.infrastructure.ai.llm_service import LLMService
from src.infrastructure.external.exercise_library import ExerciseLibrary
from src.infrastructure.ai.rag_service import get_rag_service
from src.infrastructure.ai.tools.agent_tools import create_agent_tools
from src.infrastructure.ai.agents.nutrition_agent import NutritionAgent
# from src.infrastructure.ai.tools.nutrition_tools import create_nutrition_tools  # Moved to smart_nutrition_tools
from src.infrastructure.persistence.repositories.nutrition_repository_impl import NutritionRepositoryImpl
from src.application.use_cases.ask_nutritionist import AskNutritionistUseCase
from src.application.use_cases.generate_diet import GenerateDietUseCase
from src.infrastructure.ai.agents.workout_coach import WorkoutCoachAgent
from src.infrastructure.ai.agents.medical_agent import MedicalAgent
from src.application.use_cases.checkin_conversational import CheckInConversationalUseCase
from src.application.use_cases.generate_workout import GenerateWorkoutUseCase
from src.application.use_cases.weekly_review import WeeklyReviewUseCase
from src.application.use_cases.ask_medical import AskMedicalUseCase
from src.application.use_cases.ask_workout_coach import AskWorkoutCoachUseCase
from src.application.use_cases.onboarding import OnboardingUseCase
from src.application.use_cases.record_biometric import RecordBiometricUseCase
from src.application.services.agent_orchestrator import AgentOrchestrator
from src.infrastructure.ai.agents.wizard_agent import WizardAgent
from src.infrastructure.ai.user_context_rag import get_user_context_rag


class DependencyContainer:
    """
    Dependency injection container.

    Manages creation and lifecycle of application dependencies.
    """

    def __init__(self):
        """Initialize container with defaults."""
        # Infrastructure
        self.llm_service = None
        self.exercise_library = None
        self.rag_service = None
        self._medical_agent = None
        self._workout_coach = None

        # Initialize services
        self._init_services()

    def _init_services(self):
        """Initialize infrastructure services."""
        # LLM Service
        self.llm_service = LLMService()

        # Exercise Library
        self.exercise_library = ExerciseLibrary()

        # RAG Service
        try:
            self.rag_service = get_rag_service()
            # Initialize knowledge base only in dev or when explicitly enabled.
            # In production we avoid auto-init to prevent accidental ingestion and unnecessary Chroma load.
            rag_auto_init_env = os.getenv("RAG_AUTO_INIT")
            rag_auto_init = (
                settings.debug
                if rag_auto_init_env is None
                else rag_auto_init_env.strip().lower() in {"1", "true", "yes", "on"}
            )

            if rag_auto_init:
                try:
                    self.rag_service.initialize_knowledge_base(settings.data_dir)
                except Exception as kb_err:
                    print(f"⚠️ Knowledge base initialization skipped: {kb_err}")
        except Exception as e:
            print(f"⚠️ RAG service not available: {e}")
            self.rag_service = None

    def get_pain_repository(self, db: Session):
        """Get pain repository instance."""
        return PainRepositoryImpl(db)

    def get_workout_repository(self, db: Session):
        """Get workout repository instance."""
        return WorkoutRepositoryImpl(db)

    def get_kpi_repository(self, db: Session):
        """Get KPI repository instance."""
        return KPIRepositoryImpl(db)

    def get_user_repository(self, db: Session):
        """Get user repository instance."""
        return UserRepositoryImpl(db)

    def get_biometric_repository(self, db: Session):
        """Get biometric repository instance."""
        return BiometricRepositoryImpl(db)

    def get_chat_repository(self, db: Session):
        """Get chat repository instance."""
        return ChatRepositoryImpl(db)

    def get_tools(self, db: Session, user_id: str):
        """Get LangChain tools for agents."""
        pain_repo = self.get_pain_repository(db)
        kpi_repo = self.get_kpi_repository(db)
        user_repo = self.get_user_repository(db)

        return create_agent_tools(
            pain_repository=pain_repo,
            kpi_repository=kpi_repo,
            user_repository=user_repo,
            exercise_library=self.exercise_library,
            user_id=user_id
        )

    def get_nutrition_repository(self, db: Session):
        return NutritionRepositoryImpl(db)

    def get_weekly_plans_repository(self, db: Session):
        """Get weekly plans repository for coach and nutrition plans."""
        from src.infrastructure.persistence.repositories.weekly_plans_repository import WeeklyPlansRepository
        return WeeklyPlansRepository(db)

    def get_nutrition_agent(self, db: Session, user_id: str = None):
        # Usa smart tools che integrano RAG locale + FatSecret API
        from src.infrastructure.ai.tools.smart_nutrition_tools import create_smart_nutrition_tools
        nutrition_repo = self.get_nutrition_repository(db)
        tools = create_smart_nutrition_tools(user_id, nutrition_repo)
        return NutritionAgent(self.llm_service, tools, nutrition_repo)

    def get_ask_nutritionist_usecase(self, db: Session, user_id: str, session_id: str = None):
        return AskNutritionistUseCase(
            self.get_nutrition_agent(db, user_id),
            self.get_nutrition_repository(db),
            self.get_chat_repository(db),
            user_id,
            session_id
        )

    def get_generate_diet_usecase(self, db: Session, user_id: str):
        return GenerateDietUseCase(
            self.get_nutrition_agent(db),
            self.get_nutrition_repository(db),
            user_id
        )

    def get_medical_agent(self, db: Session, user_id: str):
        """Get medical agent instance with Smart Medical Tools."""
        # Usa smart medical tools con RAG per protocolli e linee guida
        from src.infrastructure.ai.tools.smart_medical_tools import create_smart_medical_tools
        pain_repo = self.get_pain_repository(db)
        smart_tools = create_smart_medical_tools(pain_repo)

        user_repo = self.get_user_repository(db)
        biometric_repo = self.get_biometric_repository(db)

        return MedicalAgent(
            llm_service=self.llm_service,
            tools=smart_tools,
            user_repository=user_repo,
            pain_repository=pain_repo,
            biometric_repository=biometric_repo,
            rag_service=self.rag_service
        )

    def get_workout_coach(self, db: Session, user_id: str):
        """Get workout coach agent instance with Smart Workout Tools."""
        # Usa smart workout tools con RAG per esercizi e programmi
        from src.infrastructure.ai.tools.smart_workout_tools import create_smart_workout_tools
        smart_tools = create_smart_workout_tools()

        user_repo = self.get_user_repository(db)
        workout_repo = self.get_workout_repository(db)

        return WorkoutCoachAgent(
            llm_service=self.llm_service,
            tools=smart_tools,
            user_repository=user_repo,
            workout_repository=workout_repo,
            exercise_library=self.exercise_library,
            rag_service=self.rag_service
        )


    def get_checkin_conversational_usecase(self, db: Session, user_id: str):
        """Get conversational check-in use case (NEW - AI-driven with MedicalAgent)."""
        medical_agent = self.get_medical_agent(db, user_id)
        pain_repo = self.get_pain_repository(db)
        workout_repo = self.get_workout_repository(db)
        chat_repo = self.get_chat_repository(db)

        return CheckInConversationalUseCase(
            medical_agent=medical_agent,
            pain_repository=pain_repo,
            workout_repository=workout_repo,
            chat_repository=chat_repo,
            user_id=user_id
        )

    def get_generate_workout_usecase(self, db: Session, user_id: str):
        """Get generate workout use case."""
        workout_repo = self.get_workout_repository(db)
        workout_coach = self.get_workout_coach(db, user_id)

        return GenerateWorkoutUseCase(
            workout_repository=workout_repo,
            exercise_library=self.exercise_library,
            ai_agent=workout_coach,
            rag_service=self.rag_service,
            user_id=user_id
        )

    def get_weekly_review_usecase(self, db: Session, user_id: str):
        """Get weekly review use case."""
        pain_repo = self.get_pain_repository(db)
        workout_repo = self.get_workout_repository(db)
        kpi_repo = self.get_kpi_repository(db)
        workout_gen = self.get_generate_workout_usecase(db, user_id)

        return WeeklyReviewUseCase(
            pain_repository=pain_repo,
            workout_repository=workout_repo,
            kpi_repository=kpi_repo,
            workout_generator=workout_gen,
            user_id=user_id
        )

    def get_ask_medical_usecase(self, db: Session, user_id: str, session_id: str = None):
        """Get ask medical agent use case (NEW - medical questions only)."""
        pain_repo = self.get_pain_repository(db)
        kpi_repo = self.get_kpi_repository(db)
        chat_repo = self.get_chat_repository(db)
        medical_agent = self.get_medical_agent(db, user_id)

        return AskMedicalUseCase(
            pain_repository=pain_repo,
            kpi_repository=kpi_repo,
            chat_repository=chat_repo,
            medical_coach_agent=medical_agent,
            user_id=user_id,
            session_id=session_id
        )

    def get_ask_workout_coach_usecase(self, db: Session, user_id: str, session_id: str = None):
        """Get ask workout coach use case (NEW - training questions only)."""
        workout_repo = self.get_workout_repository(db)
        pain_repo = self.get_pain_repository(db)
        chat_repo = self.get_chat_repository(db)
        workout_coach = self.get_workout_coach(db, user_id)

        return AskWorkoutCoachUseCase(
            workout_repository=workout_repo,
            pain_repository=pain_repo,
            chat_repository=chat_repo,
            workout_coach_agent=workout_coach,
            user_id=user_id,
            session_id=session_id
        )

    def get_ask_coach_usecase(self, db: Session, user_id: str = "default_user", session_id: str = None):
        """Get ask coach use case (DEPRECATED - use get_ask_medical_usecase or get_ask_workout_coach_usecase)."""
        # Using MedicalAgent as fallback for generic coach
        pain_repo = self.get_pain_repository(db)
        kpi_repo = self.get_kpi_repository(db)
        chat_repo = self.get_chat_repository(db)
        medical_agent = self.get_medical_agent(db, user_id)

        return AskCoachUseCase(
            pain_repository=pain_repo,
            kpi_repository=kpi_repo,
            chat_repository=chat_repo,
            medical_coach_agent=medical_agent,
            user_id=user_id,
            session_id=session_id
        )

    def get_onboarding_usecase(self, db: Session):
        """Get onboarding use case."""
        user_repo = self.get_user_repository(db)
        return OnboardingUseCase(user_repository=user_repo)

    def get_agent_orchestrator(self, db: Session, user_id: str):
        """Get agent orchestrator for coordinating all agents."""
        medical_agent = self.get_medical_agent(db, user_id)
        workout_coach = self.get_workout_coach(db, user_id)
        nutrition_agent = self.get_nutrition_agent(db)

        try:
            user_context_rag = get_user_context_rag()
        except Exception:
            user_context_rag = None

        # Get repositories for saving generated plans to DB
        weekly_plans_repo = self.get_weekly_plans_repository(db)
        nutrition_repo = self.get_nutrition_repository(db)
        pain_repo = self.get_pain_repository(db)

        return AgentOrchestrator(
            medical_agent=medical_agent,
            workout_coach=workout_coach,
            nutrition_agent=nutrition_agent,
            user_context_rag=user_context_rag,
            db=db,  # Pass db for saving plans
            coach_repo=weekly_plans_repo,
            nutrition_repo=nutrition_repo,
            medical_repo=pain_repo,
            exercise_library=self.exercise_library
        )

    # Singleton WizardAgent per mantenere sessioni (con DB persistence)
    _wizard_agent: Optional[WizardAgent] = None

    def get_wizard_session_repository(self, db: Session):
        """Get wizard session repository for DB persistence."""
        from src.infrastructure.persistence.repositories.wizard_session_repository import WizardSessionRepository
        return WizardSessionRepository(db)

    def get_wizard_agent(self, db: Session, user_id: str = None):
        """Get wizard agent for conversational onboarding (SINGLETON with DB persistence)."""
        # Usa singleton per mantenere le sessioni
        if self._wizard_agent is None:
            try:
                user_context_rag = get_user_context_rag()
            except Exception as e:
                print(f"⚠️ User context RAG not available: {e}")
                user_context_rag = None

            self._wizard_agent = WizardAgent(
                llm_service=self.llm_service,
                user_context_rag=user_context_rag,
                user_repository=None,  # Set dynamically
                orchestrator=None,  # Set dynamically
                session_repository=None  # Set dynamically
            )

        # Aggiorna repository e orchestrator con la DB session corrente
        user_repo = self.get_user_repository(db)
        session_repo = self.get_wizard_session_repository(db)

        self._wizard_agent.user_repository = user_repo
        self._wizard_agent.session_repository = session_repo

        if user_id:
            self._wizard_agent.orchestrator = self.get_agent_orchestrator(db, user_id)

        return self._wizard_agent

    def get_record_biometric_usecase(self, db: Session):
        """Get record biometric use case."""
        biometric_repo = self.get_biometric_repository(db)
        user_repo = self.get_user_repository(db)
        return RecordBiometricUseCase(
            biometric_repository=biometric_repo,
            user_repository=user_repo
        )


# Global container instance
container = DependencyContainer()


# Helper functions for FastAPI dependency injection


def get_generate_workout_use_case(db: Session):
    """Get generate workout use case for dependency injection."""
    return container.get_generate_workout_usecase(db)


def get_weekly_review_use_case(db: Session):
    """Get weekly review use case for dependency injection."""
    return container.get_weekly_review_usecase(db)




def get_pain_repository(db: Session):
    """Get pain repository for dependency injection."""
    return container.get_pain_repository(db)


def get_workout_repository(db: Session):
    """Get workout repository for dependency injection."""
    return container.get_workout_repository(db)


def get_kpi_repository(db: Session):
    """Get KPI repository for dependency injection."""
    return container.get_kpi_repository(db)


def get_user_repository(db: Session):
    """Get user repository for dependency injection."""
    return container.get_user_repository(db)


def get_biometric_repository(db: Session):
    """Get biometric repository for dependency injection."""
    return container.get_biometric_repository(db)


def get_onboarding_use_case(db: Session):
    """Get onboarding use case for dependency injection."""
    return container.get_onboarding_usecase(db)


def get_record_biometric_use_case(db: Session):
    """Get record biometric use case for dependency injection."""
    return container.get_record_biometric_usecase(db)


def get_chat_repository(db: Session):
    """Get chat repository for dependency injection."""
    return container.get_chat_repository(db)


def get_wizard_agent(db: Session, user_id: str = None):
    """Get wizard agent for dependency injection."""
    return container.get_wizard_agent(db, user_id)


def get_agent_orchestrator(db: Session, user_id: str):
    """Get agent orchestrator for dependency injection."""
    return container.get_agent_orchestrator(db, user_id)


def get_container():
    """Get the dependency container."""
    return container
