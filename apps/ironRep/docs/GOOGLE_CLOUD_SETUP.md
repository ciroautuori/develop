# 🔧 Guida Setup Google Cloud per IronRep

Configurazione completa per abilitare Google Fit, Calendar e YouTube APIs.

---

## 1️⃣ Crea Progetto Google Cloud

1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Clicca **"Select a project"** → **"New Project"**
3. Nome progetto: `ironrep-production`
4. Clicca **"Create"**

---

## 2️⃣ Abilita le API

Nel menu laterale vai su **APIs & Services** → **Library**

Cerca e abilita ognuna:

| API | Cerca | Azione |
|-----|-------|--------|
| **Fitness API** | "Fitness API" | Enable |
| **Google Calendar API** | "Calendar API" | Enable |
| **YouTube Data API v3** | "YouTube Data API" | Enable |
| **People API** | "People API" | Enable (per user info) |

---

## 3️⃣ Configura OAuth Consent Screen

**APIs & Services** → **OAuth consent screen**

### Step 1: User Type
- Seleziona **External** (o Internal se hai Google Workspace)
- Clicca **"Create"**

### Step 2: App Info
```
App name: IronRep
User support email: tua-email@gmail.com
App logo: (carica logo IronRep)
```

### Step 3: App Domain
```
Application home page: https://ironrep.it
Privacy policy: https://ironrep.it/privacy
Terms of service: https://ironrep.it/terms
```

### Step 4: Developer Contact
```
Email: tua-email@gmail.com
```

### Step 5: Scopes
Clicca **"Add or Remove Scopes"** e aggiungi:

```
• https://www.googleapis.com/auth/fitness.activity.read
• https://www.googleapis.com/auth/fitness.body.read
• https://www.googleapis.com/auth/fitness.heart_rate.read
• https://www.googleapis.com/auth/fitness.sleep.read
• https://www.googleapis.com/auth/calendar.events
• https://www.googleapis.com/auth/youtube.readonly
• https://www.googleapis.com/auth/userinfo.email
• https://www.googleapis.com/auth/userinfo.profile
```

### Step 6: Test Users
Aggiungi i tuoi indirizzi email per testing.

---

## 4️⃣ Crea Credenziali OAuth

**APIs & Services** → **Credentials** → **Create Credentials** → **OAuth client ID**

### Application type
`Web application`

### Name
`IronRep Web Client`

### Authorized JavaScript origins
```
http://localhost:5173
http://localhost:8000
https://ironrep.it
```

### Authorized redirect URIs
```
http://localhost:8000/api/google/auth/callback
https://ironrep.it/api/google/auth/callback
```

Clicca **"Create"** e **scarica il JSON** con le credenziali.

---

## 5️⃣ Crea API Key per YouTube

**Credentials** → **Create Credentials** → **API Key**

1. Copia la chiave generata
2. Clicca **"Edit API key"**
3. Nome: `IronRep YouTube Key`
4. **API restrictions**: Seleziona "YouTube Data API v3"
5. **Application restrictions**: HTTP referrers
   - `http://localhost:*`
   - `https://ironrep.it/*`

---

## 6️⃣ Configura Environment Variables

Aggiungi a `apps/backend/.env`:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=123456789-xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxx
GOOGLE_REDIRECT_URI=http://localhost:8000/api/google/auth/callback

# YouTube API Key
YOUTUBE_API_KEY=AIzaSyXXXXXXXXXXXXXXXX
```

---

## 7️⃣ Verifica Configurazione

```bash
# Backend
cd apps/backend
uv run python -c "
from src.infrastructure.external.google_oauth_service import google_oauth_service
url = google_oauth_service.get_authorization_url()
print(f'✅ OAuth URL: {url[:50]}...')
"
```

---

## ⚠️ Produzione: Pubblica App

Per uscire da "Testing" mode:

1. **OAuth consent screen** → **"Publish App"**
2. Compila questionario Google
3. Attendi review (1-4 settimane)

> **Nota**: In modalità testing, solo gli utenti aggiunti come "Test users" possono usare l'OAuth.

---

## 🔗 Link Utili

- [Google Cloud Console](https://console.cloud.google.com/)
- [Fitness API Docs](https://developers.google.com/fit)
- [Calendar API Docs](https://developers.google.com/calendar)
- [YouTube API Docs](https://developers.google.com/youtube/v3)
