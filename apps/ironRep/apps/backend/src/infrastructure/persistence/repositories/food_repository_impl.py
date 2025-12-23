from __future__ import annotations

import uuid
from typing import List

from sqlalchemy.orm import Session

from src.domain.repositories.food_repository import IFoodRepository
from src.infrastructure.persistence.food_models import UserFavoriteFoodModel


class FoodRepositoryImpl(IFoodRepository):
    def __init__(self, db: Session):
        self.db = db

    def add_favorite(self, user_id: str, fatsecret_id: str) -> None:
        existing = (
            self.db.query(UserFavoriteFoodModel)
            .filter(
                UserFavoriteFoodModel.user_id == user_id,
                UserFavoriteFoodModel.fatsecret_id == fatsecret_id,
            )
            .first()
        )

        if existing:
            return

        fav = UserFavoriteFoodModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            fatsecret_id=fatsecret_id,
        )
        self.db.add(fav)
        self.db.commit()

    def get_user_favorites(self, user_id: str) -> List[str]:
        favorites = (
            self.db.query(UserFavoriteFoodModel)
            .filter(UserFavoriteFoodModel.user_id == user_id)
            .all()
        )
        return [str(f.fatsecret_id) for f in favorites if f.fatsecret_id]

    def remove_favorite(self, user_id: str, fatsecret_id: str) -> None:
        existing = (
            self.db.query(UserFavoriteFoodModel)
            .filter(
                UserFavoriteFoodModel.user_id == user_id,
                UserFavoriteFoodModel.fatsecret_id == fatsecret_id,
            )
            .first()
        )

        if not existing:
            return

        self.db.delete(existing)
        self.db.commit()
