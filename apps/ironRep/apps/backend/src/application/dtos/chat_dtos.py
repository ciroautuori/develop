from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChatMessageDTO(BaseModel):
    """DTO for chat messages."""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str
    timestamp: Optional[datetime] = None


class AskCoachResponseDTO(BaseModel):
    """Response DTO for coach chatbot."""
    answer: str
    suggested_actions: List[str] = []
    relevant_exercises: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.now)
