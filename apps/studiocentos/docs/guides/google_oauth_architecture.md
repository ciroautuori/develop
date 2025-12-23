# Google OAuth Architecture - Unified Service

> **Data Refactoring**: 2025-05-29
> **Problema Risolto**: Debito tecnico con 4 implementazioni OAuth separate

## 🎯 Problema Originale

Il progetto aveva **4 implementazioni OAuth Google separate**:

| File | Scopo | Scope |
|------|-------|-------|
| `domain/auth/google_oauth.py` | Login Customer | `openid email profile` |
| `domain/google/router.py` | Admin connect | Analytics, Business, Calendar |
| `integrations/google_meet.py` | Google Meet | Calendar only |
| `services/calendar_service.py` | Google Calendar | Calendar only |

### Conseguenze

1. **Scope frammentati** - ogni file richiedeva scope diversi
2. **Token non condivisi** - impossibile accedere a tutti i servizi
3. **Duplicazione codice** - 4 implementazioni del flow OAuth
4. **Manutenzione difficile** - bug fix in un posto, non negli altri

## ✅ Soluzione: Servizio Unificato

Tutto consolidato in `app/core/google/`:

```
app/core/google/
├── __init__.py          # Export pubblici
├── scopes.py            # TUTTI gli scope in un posto solo
├── oauth_service.py     # Servizio OAuth unificato
└── token_manager.py     # Gestione token centralizzata
```

## 📦 Scope Sets Disponibili

Definiti in `scopes.py`:

```python
from app.core.google import GOOGLE_SCOPE_SETS

# Scope disponibili:
- "login"           # Solo autenticazione base
- "customer"        # Login Customer (openid, email, profile)
- "admin_full"      # Analytics + Business + Calendar
- "analytics"       # Solo Google Analytics
- "business"        # Solo Business Profile
- "calendar"        # Google Calendar full
- "calendar_readonly"
- "search_console"  # Search Console
- "backoffice_full" # TUTTI i servizi
```

## 🔧 Come Usare

### Login Customer

```python
from app.core.google import google_oauth_service

# Genera URL autorizzazione
auth_url = google_oauth_service.get_auth_url(
    redirect_uri="http://example.com/callback",
    use_case="customer",
    state="csrf_token"
)

# Scambia code per token
token = await google_oauth_service.exchange_code(
    code=auth_code,
    redirect_uri="http://example.com/callback"
)

# Ottieni info utente
user_info = await google_oauth_service.get_user_info(token.access_token)
```

### Admin Full Integration

```python
from app.core.google import google_oauth_service

# Per admin usa "admin_full" per avere tutti gli scope
auth_url = google_oauth_service.get_auth_url(
    redirect_uri="http://example.com/admin/callback",
    use_case="admin_full",  # Analytics + Business + Calendar
    state=google_oauth_service.generate_csrf_state(extra_data=str(admin_id))
)
```

### Token Refresh

```python
from app.core.google import GoogleTokenManager

manager = GoogleTokenManager(db)

# Ottieni token valido (auto-refresh se scaduto)
token = await manager.get_valid_token(admin_id=admin.id)

# Oppure per customer
token = await manager.get_valid_token(user_id=user.id)
```

## ⚠️ Migrazione Necessaria

Se l'utente ha già un token con scope limitati, deve ri-autenticarsi per ottenere tutti gli scope.

### Verifica Scope

```python
from app.core.google.scopes import check_scope_coverage

result = check_scope_coverage(
    granted_scopes="openid email profile",
    required_use_case="admin_full"
)

if not result["covered"]:
    print(f"Scope mancanti: {result['missing']}")
    # Richiedi nuova autorizzazione con scope completi
```

## 🔐 Sicurezza

1. **CSRF Protection** - State token generato automaticamente
2. **Token Storage** - In database, mai in cookie/localStorage
3. **Auto Refresh** - Token refreshati 5 minuti prima della scadenza
4. **Scope Validation** - Verifica scope prima di chiamare API

## 📝 File Obsoleti (DA NON USARE)

I seguenti file sono stati deprecati ma mantenuti per compatibilità:

- `integrations/google_meet.py` → Usa `GoogleCalendarService` da `core/google`
- `services/calendar_service.py` → Idem

## 🐛 Debug CORS

L'errore `play.google.com/log` è causato da librerie Google client-side, non dal backend.
Non è risolvibile lato server - ignorare nel browser console.
