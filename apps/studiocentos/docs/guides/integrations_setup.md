# 🔌 Guida Setup Integrazioni Esterne

Questa guida copre la configurazione delle integrazioni esterne per StudioCentOS: **Google Calendar** e **Social Media (Meta/Threads)**.

---

## 📅 1. Google Calendar Integration

Per sincronizzare gli appuntamenti del backoffice con Google Calendar.

**Account Google**: `studiocentos089@gmail.com`

### Step 1: Google Cloud Console
1. Vai su [Google Cloud Console](https://console.cloud.google.com/projectcreate).
2. Crea un progetto "StudioCentOS".
3. Abilita **Google Calendar API** dalla Library.

### Step 2: OAuth Consent Screen
1. Vai su **APIs & Services > OAuth consent screen**.
2. Tipo: **External**.
3. App Name: `StudioCentOS Backoffice`.
4. Email: `studiocentos089@gmail.com`.
5. Aggiungi Test Users: `studiocentos089@gmail.com`, `info@studiocentos.it`.

### Step 3: Credentials
1. Vai su **Credentials > Create Credentials > OAuth client ID**.
2. Tipo: **Web application**.
3. **Authorized JavaScript origins**:
   - `https://studiocentos.it`
   - `http://localhost:8002`
4. **Authorized redirect URIs**:
   - `https://studiocentos.it/api/v1/auth/google/callback`
   - `http://localhost:8002/api/v1/auth/google/callback`
5. Copia **Client ID** e **Client Secret**.

### Step 4: Configurazione Backend
Aggiungi al file `.env.production`:
```bash
GOOGLE_CLIENT_ID="il_tuo_client_id"
GOOGLE_CLIENT_SECRET="il_tuo_secret"
```

---

## 📱 2. Social Media Integration (Meta & Threads)

Per la pubblicazione automatica dei contenuti generati dall'AI.

### Credenziali App
**Meta/Facebook App**: ID `832697706350252`
**Threads App**: ID `1142047478046537`

### Step 1: Access Token Meta/Facebook
1. Vai su [Graph API Explorer](https://developers.facebook.com/tools/explorer/).
2. Seleziona App: `StudioCentOS-Marketing`.
3. Richiedi permessi: `pages_manage_posts`, `pages_read_engagement`, `publish_to_groups`.
4. Genera Token.
5. Scambia per **Long-lived Token** (60 giorni):
   ```bash
   curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=832697706350252&client_secret=...&fb_exchange_token=SHORT_TOKEN"
   ```

### Step 2: Access Token Threads
1. Segui la [guida ufficiale Threads](https://developers.facebook.com/docs/threads/get-started).
2. Ottieni User ID e Token.
3. Scambia per Long-lived Token.

### Step 3: Configurazione Backend
Aggiungi al file `.env.production`:

```bash
# Meta/Facebook
META_APP_ID=832697706350252
META_APP_SECRET=8d1a6eddb0e4391bd2703cc5f651abd0
META_ACCESS_TOKEN=...
FACEBOOK_PAGE_ID=...

# Threads
THREADS_APP_ID=1142047478046537
THREADS_APP_SECRET=b20c55e8e7a2338cba0fe0eefc6583e5
THREADS_ACCESS_TOKEN=...
THREADS_USER_ID=...
```

### Step 4: Testing
Endpoint: `POST /api/v1/copilot/marketing/publish`
```json
{
  "content": "Test post from AI!",
  "platforms": ["threads", "facebook"]
}
```

---

## 🔐 Security Notes
- **Token Rotation**: I token Meta/Threads scadono ogni 60 giorni. Imposta un reminder.
- **HTTPS**: Obbligatorio per le callback OAuth e API Social in produzione.
- **Environment**: Mai committare le chiavi segrete nel repository.
