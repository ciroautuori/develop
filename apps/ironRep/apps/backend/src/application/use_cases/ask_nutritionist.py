"""
Ask Nutritionist Use Case
"""
from datetime import datetime
from typing import Optional

class AskNutritionistUseCase:
    def __init__(
        self,
        nutrition_agent,
        nutrition_repository,
        chat_repository,
        user_id: str,
        session_id: str = None
    ):
        self.agent = nutrition_agent
        self.nutrition_repo = nutrition_repository
        self.chat_repo = chat_repository
        self.user_id = user_id
        self.session_id = session_id or chat_repository.create_new_session(user_id, session_type="nutrition")

    async def execute(self, question: str) -> dict:
        # Save user message
        self.chat_repo.save_message(self.user_id, self.session_id, "user", question, {"timestamp": datetime.now().isoformat()})

        # Get current plan context
        plan = self.nutrition_repo.get_current_plan(self.user_id)
        context = {"current_plan": plan.goal.value if plan else "Nessuno"}

        # Ask agent
        response = await self.agent.answer_question(question, context)

        # Save answer
        self.chat_repo.save_message(self.user_id, self.session_id, "assistant", response["answer"], {"timestamp": datetime.now().isoformat()})

        return {
            "answer": response["answer"],
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        }

    def get_session_id(self) -> str:
        return self.session_id
