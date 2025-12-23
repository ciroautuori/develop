"""
Google OAuth Scopes - SINGLE SOURCE OF TRUTH

TUTTI gli scope Google sono definiti QUI e solo qui.
Non duplicare scope in altri file.

Docs:
- https://developers.google.com/identity/protocols/oauth2/scopes
- https://developers.google.com/analytics/devguides/config/admin/v1
- https://developers.google.com/my-business/reference/rest
- https://developers.google.com/calendar/api/auth
"""

from enum import Enum


class GoogleScopes(str, Enum):
    """
    Tutti gli scope Google API disponibili.

    IMPORTANTE: Usare questi enum invece di stringhe hardcoded.
    """

    # =========================================================================
    # IDENTITY & PROFILE (OpenID Connect)
    # =========================================================================
    OPENID = "openid"
    EMAIL = "email"
    PROFILE = "profile"

    # Full URLs (alcuni provider li richiedono così)
    USERINFO_EMAIL = "https://www.googleapis.com/auth/userinfo.email"
    USERINFO_PROFILE = "https://www.googleapis.com/auth/userinfo.profile"

    # =========================================================================
    # GOOGLE ANALYTICS 4 (GA4)
    # =========================================================================
    ANALYTICS_READONLY = "https://www.googleapis.com/auth/analytics.readonly"
    ANALYTICS_EDIT = "https://www.googleapis.com/auth/analytics.edit"
    ANALYTICS_MANAGE_USERS = "https://www.googleapis.com/auth/analytics.manage.users"

    # =========================================================================
    # GOOGLE BUSINESS PROFILE (ex Google My Business)
    # =========================================================================
    BUSINESS_MANAGE = "https://www.googleapis.com/auth/business.manage"

    # =========================================================================
    # GOOGLE CALENDAR
    # =========================================================================
    CALENDAR = "https://www.googleapis.com/auth/calendar"
    CALENDAR_EVENTS = "https://www.googleapis.com/auth/calendar.events"
    CALENDAR_READONLY = "https://www.googleapis.com/auth/calendar.readonly"
    CALENDAR_SETTINGS_READONLY = "https://www.googleapis.com/auth/calendar.settings.readonly"

    # =========================================================================
    # GOOGLE SEARCH CONSOLE
    # =========================================================================
    WEBMASTERS_READONLY = "https://www.googleapis.com/auth/webmasters.readonly"
    WEBMASTERS = "https://www.googleapis.com/auth/webmasters"

    # =========================================================================
    # GOOGLE DRIVE (per upload media e documenti)
    # =========================================================================
    DRIVE = "https://www.googleapis.com/auth/drive"
    DRIVE_FILE = "https://www.googleapis.com/auth/drive.file"
    DRIVE_READONLY = "https://www.googleapis.com/auth/drive.readonly"
    DOCS = "https://www.googleapis.com/auth/documents"
    DOCS_READONLY = "https://www.googleapis.com/auth/documents.readonly"

    # =========================================================================
    # GMAIL (per notifiche/inviti)
    # =========================================================================
    GMAIL_SEND = "https://www.googleapis.com/auth/gmail.send"
    GMAIL_READONLY = "https://www.googleapis.com/auth/gmail.readonly"
    GMAIL_COMPOSE = "https://www.googleapis.com/auth/gmail.compose"


# =============================================================================
# SCOPE SETS - Raggruppamenti predefiniti per casi d'uso comuni
# =============================================================================

GOOGLE_SCOPE_SETS = {
    # Login base (solo autenticazione)
    "login": [
        GoogleScopes.OPENID.value,
        GoogleScopes.EMAIL.value,
        GoogleScopes.PROFILE.value,
    ],

    # Customer OAuth (login + basic profile)
    "customer": [
        GoogleScopes.OPENID.value,
        GoogleScopes.EMAIL.value,
        GoogleScopes.PROFILE.value,
    ],

    # Admin full integration (Analytics + Business + Calendar + Gmail + Drive)
    "admin_full": [
        GoogleScopes.OPENID.value,
        GoogleScopes.EMAIL.value,
        GoogleScopes.PROFILE.value,
        GoogleScopes.ANALYTICS_READONLY.value,
        GoogleScopes.BUSINESS_MANAGE.value,
        GoogleScopes.CALENDAR_EVENTS.value,
        GoogleScopes.GMAIL_SEND.value,
        GoogleScopes.DRIVE.value,
        GoogleScopes.DOCS.value,
    ],

    # Solo Analytics
    "analytics": [
        GoogleScopes.OPENID.value,
        GoogleScopes.EMAIL.value,
        GoogleScopes.ANALYTICS_READONLY.value,
    ],

    # Solo Business Profile
    "business": [
        GoogleScopes.OPENID.value,
        GoogleScopes.EMAIL.value,
        GoogleScopes.BUSINESS_MANAGE.value,
    ],

    # Solo Calendar (per booking e meetings)
    "calendar": [
        GoogleScopes.OPENID.value,
        GoogleScopes.EMAIL.value,
        GoogleScopes.CALENDAR.value,
        GoogleScopes.CALENDAR_EVENTS.value,
    ],

    # Calendar readonly (per visualizzare disponibilità)
    "calendar_readonly": [
        GoogleScopes.OPENID.value,
        GoogleScopes.EMAIL.value,
        GoogleScopes.CALENDAR_READONLY.value,
    ],

    # Search Console
    "search_console": [
        GoogleScopes.OPENID.value,
        GoogleScopes.EMAIL.value,
        GoogleScopes.WEBMASTERS_READONLY.value,
    ],

    # Backoffice completo (TUTTI i servizi)
    "backoffice_full": [
        GoogleScopes.OPENID.value,
        GoogleScopes.EMAIL.value,
        GoogleScopes.PROFILE.value,
        GoogleScopes.ANALYTICS_READONLY.value,
        GoogleScopes.BUSINESS_MANAGE.value,
        GoogleScopes.CALENDAR_EVENTS.value,
        GoogleScopes.WEBMASTERS_READONLY.value,
        GoogleScopes.GMAIL_SEND.value,
        GoogleScopes.DRIVE.value,
        GoogleScopes.DOCS.value,
    ],

    # Gmail + Docs (per preventivi ed email)
    "documents": [
        GoogleScopes.OPENID.value,
        GoogleScopes.EMAIL.value,
        GoogleScopes.GMAIL_SEND.value,
        GoogleScopes.GMAIL_READONLY.value,
        GoogleScopes.GMAIL_COMPOSE.value,
        GoogleScopes.DRIVE.value,
        GoogleScopes.DOCS.value,
    ],
}


def get_scopes_for_use_case(use_case: str) -> list[str]:
    """
    Ottieni lista di scope per un caso d'uso specifico.

    Args:
        use_case: Nome del caso d'uso (chiave di GOOGLE_SCOPE_SETS)

    Returns:
        Lista di scope strings

    Raises:
        ValueError: Se il caso d'uso non esiste

    Example:
        >>> scopes = get_scopes_for_use_case("admin_full")
        >>> print(scopes)
        ['openid', 'email', 'profile', 'https://www.googleapis.com/auth/analytics.readonly', ...]
    """
    if use_case not in GOOGLE_SCOPE_SETS:
        available = ", ".join(GOOGLE_SCOPE_SETS.keys())
        raise ValueError(f"Unknown use case '{use_case}'. Available: {available}")

    return GOOGLE_SCOPE_SETS[use_case]


def check_scope_coverage(granted_scopes: str, required_use_case: str) -> dict:
    """
    Verifica se gli scope concessi coprono un caso d'uso.

    Args:
        granted_scopes: Stringa di scope separati da spazio (come ritornati da Google)
        required_use_case: Caso d'uso da verificare

    Returns:
        dict con: covered (bool), missing (list), granted (list)
    """
    granted_list = granted_scopes.split() if granted_scopes else []
    required_list = get_scopes_for_use_case(required_use_case)

    missing = [s for s in required_list if s not in granted_list]

    return {
        "covered": len(missing) == 0,
        "missing": missing,
        "granted": granted_list,
        "required": required_list,
    }
