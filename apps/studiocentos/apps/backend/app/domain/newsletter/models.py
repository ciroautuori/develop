from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.infrastructure.database.session import Base

class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscribers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    source = Column(String, default="website") # e.g., 'landing_academy', 'footer'
    status = Column(String, default="active") # 'active', 'unsubscribed'
    created_at = Column(DateTime, default=datetime.utcnow)
