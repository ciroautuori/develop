from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime
from sqlalchemy.sql import func
from app.database.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    excerpt = Column(String(300), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
