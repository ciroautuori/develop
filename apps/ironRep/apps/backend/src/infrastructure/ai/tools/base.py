from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class IronRepBaseTool(ABC):
    """Base interface for AI Tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for the agent."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does."""
        pass

    @abstractmethod
    async def execute(self, query: str) -> Dict[str, Any]:
        """Execute the tool action."""
        pass
