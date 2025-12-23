"""WhatsApp Cloud API Integration Domain."""

from .router import router
from .service import WhatsAppService

__all__ = ["WhatsAppService", "router"]
