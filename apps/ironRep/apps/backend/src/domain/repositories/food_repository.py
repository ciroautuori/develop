from abc import ABC, abstractmethod
from typing import List
from src.domain.entities.food import FoodItem

class IFoodRepository(ABC):
    @abstractmethod
    def add_favorite(self, user_id: str, fatsecret_id: str) -> None:
        pass

    @abstractmethod
    def get_user_favorites(self, user_id: str) -> List[str]:
        pass

    @abstractmethod
    def remove_favorite(self, user_id: str, fatsecret_id: str) -> None:
        pass
