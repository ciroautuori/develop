"""
Google Services - Unified OAuth & API Integration

Questo modulo consolida TUTTE le integrazioni Google in un'unica architettura:
- OAuth 2.0 flow unificato
- Token management centralizzato
- Scope management in un posto solo
- Support per: Login, Analytics, Business Profile, Calendar, Meet

ARCHITECTURAL DECISION (2025-05-29):
Prima di questo refactoring, c'erano 4 implementazioni separate:
1. domain/auth/google_oauth.py - Login Customer
2. domain/google/router.py - Admin connect
3. integrations/google_meet.py - Google Meet
4. services/calendar_service.py - Google Calendar

Ora tutto è consolidato qui per evitare:
- Duplicazione di codice
- Scope frammentati
- Token storage inconsistente
- Difficoltà di manutenzione
"""

from .scopes import GoogleScopes, GOOGLE_SCOPE_SETS
from .oauth_service import GoogleOAuthService, google_oauth_service
from .token_manager import GoogleTokenManager

__all__ = [
    "GoogleScopes",
    "GOOGLE_SCOPE_SETS",
    "GoogleOAuthService",
    "google_oauth_service",
    "GoogleTokenManager",
]
