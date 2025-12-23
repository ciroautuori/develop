from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime
from .database import Base

class UserFavoriteFoodModel(Base):
    __tablename__ = "user_favorite_foods"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    fatsecret_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (UniqueConstraint('user_id', 'fatsecret_id', name='unique_user_food'),)
