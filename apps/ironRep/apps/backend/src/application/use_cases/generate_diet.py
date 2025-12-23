"""
Generate Diet Use Case
"""
class GenerateDietUseCase:
    def __init__(self, nutrition_agent, nutrition_repository, user_id: str = "default_user"):
        self.agent = nutrition_agent
        self.repo = nutrition_repository
        self.user_id = user_id

    async def execute(self, preferences: dict) -> dict:
        result = await self.agent.generate_weekly_plan(preferences)
        if result["success"]:
            # In real app, parse result["plan"] to NutritionPlan entity and save
            pass
        return result
