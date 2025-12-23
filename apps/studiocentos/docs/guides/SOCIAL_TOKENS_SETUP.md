# 🔐 Guida Configurazione Token Social Media

> **Guida completa** per configurare i token di accesso per Facebook, Instagram, LinkedIn e Twitter.

---

## 📋 Panoramica Token Richiesti

| Piattaforma | Tipo Token | Durata | Permessi Richiesti |
|-------------|------------|--------|-------------------|
| **Facebook** | Long-Lived Page Token | 90 giorni | `pages_manage_posts`, `pages_read_engagement` |
| **Instagram** | Long-Lived Token | 90 giorni | `instagram_basic`, `instagram_content_publish` |
| **LinkedIn** | OAuth 2.0 Token | 60 giorni | `w_member_social`, `r_liteprofile` |
| **Twitter/X** | OAuth 2.0 Bearer | Non scade | `tweet.read`, `tweet.write`, `users.read` |

---

## 1️⃣ FACEBOOK + INSTAGRAM (Meta)

Facebook e Instagram usano lo stesso token Meta. Un unico token può gestire entrambe le piattaforme.

### Step 1: Accedi a Meta for Developers

1. Vai su **https://developers.facebook.com/**
2. Accedi con il tuo account Facebook
3. Vai su **My Apps** → Seleziona la tua app (o creane una nuova)

### Step 2: Crea App (se non esiste)

Se non hai già un'app:

1. Clicca **Create App**
2. Seleziona **Business** come tipo
3. Nome app: `StudioCentOS`
4. Clicca **Create App**

### Step 3: Configura Prodotti

1. Nella dashboard app, vai su **Add Products**
2. Aggiungi:
   - ✅ **Facebook Login for Business**
   - ✅ **Instagram Graph API**

### Step 4: Genera Access Token

1. Vai su **https://developers.facebook.com/tools/explorer/**
2. Seleziona la tua App dal dropdown
3. Clicca **Generate Access Token**
4. Nella finestra di login, seleziona:
   - ✅ La tua **Pagina Facebook**
   - ✅ Il tuo **Account Instagram Business** collegato

### Step 5: Seleziona Permessi

Aggiungi questi permessi (clicca "Add a Permission"):

#### Per Facebook:
```
pages_show_list
pages_read_engagement
pages_manage_posts
pages_manage_metadata
```

#### Per Instagram:
```
instagram_basic
instagram_content_publish
instagram_manage_comments
instagram_manage_insights
```

### Step 6: Ottieni Page Access Token

1. Dopo aver generato il token, nel Graph API Explorer:
2. Esegui questa query:
```
GET /me/accounts?fields=name,access_token,id
```
3. Copia il `access_token` della tua pagina (NON il token utente!)

### Step 7: Converti in Long-Lived Token (90 giorni)

Esegui questo comando (sostituisci i valori):

```bash
curl -s "https://graph.facebook.com/v18.0/oauth/access_token?\
grant_type=fb_exchange_token&\
client_id=TUO_APP_ID&\
client_secret=TUO_APP_SECRET&\
fb_exchange_token=TOKEN_CORTO_QUI"
```

**Dove trovare i valori:**
- `TUO_APP_ID`: Dashboard App → Settings → Basic → App ID
- `TUO_APP_SECRET`: Dashboard App → Settings → Basic → App Secret
- `TOKEN_CORTO_QUI`: Il token generato nel Graph Explorer

### Step 8: Ottieni Instagram Account ID

Nel Graph API Explorer, esegui:
```
GET /me/accounts?fields=instagram_business_account{id,username}
```

Copia l'`id` dell'account Instagram.

### Step 9: Salva le Credenziali

Aggiorna il file `.env`:

```bash
# Meta / Facebook
META_APP_ID=832697706350252
META_APP_SECRET=8d1a6eddb0e4391bd2703cc5f651abd0
META_ACCESS_TOKEN=EAAL1VYrZBBqwBO...token_lungo...
FACEBOOK_PAGE_ID=162256733633265

# Instagram
INSTAGRAM_ACCOUNT_ID=17841462985991568
INSTAGRAM_ACCESS_TOKEN=EAAL1VYrZBBqwBO...stesso_token_meta...
```

---

## 2️⃣ LINKEDIN

### Step 1: Crea App LinkedIn

1. Vai su **https://www.linkedin.com/developers/apps**
2. Clicca **Create App**
3. Compila:
   - **App name**: StudioCentOS
   - **LinkedIn Page**: Seleziona la tua company page
   - **App logo**: Carica logo
4. Accetta i termini e clicca **Create app**

### Step 2: Configura Prodotti

1. Vai su tab **Products**
2. Richiedi accesso a:
   - ✅ **Share on LinkedIn** (per postare)
   - ✅ **Sign In with LinkedIn using OpenID Connect**

### Step 3: Configura OAuth 2.0

1. Vai su tab **Auth**
2. Aggiungi **Redirect URLs**:
```
https://studiocentos.com/api/v1/auth/linkedin/callback
http://localhost:8002/api/v1/auth/linkedin/callback
```
3. Copia:
   - **Client ID**
   - **Client Secret**

### Step 4: Genera Access Token

Usa questo URL per autorizzare (apri nel browser):

```
https://www.linkedin.com/oauth/v2/authorization?
response_type=code&
client_id=TUO_CLIENT_ID&
redirect_uri=https://studiocentos.com/api/v1/auth/linkedin/callback&
scope=openid%20profile%20w_member_social
```

Dopo l'autorizzazione, riceverai un `code`. Scambialo per un token:

```bash
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=IL_TUO_CODE" \
  -d "client_id=TUO_CLIENT_ID" \
  -d "client_secret=TUO_CLIENT_SECRET" \
  -d "redirect_uri=https://studiocentos.com/api/v1/auth/linkedin/callback"
```

### Step 5: Ottieni Person URN

```bash
curl -H "Authorization: Bearer TUO_ACCESS_TOKEN" \
  "https://api.linkedin.com/v2/userinfo"
```

Copia il `sub` (es: `urn:li:person:ABC123`)

### Step 6: Salva le Credenziali

```bash
# LinkedIn
LINKEDIN_CLIENT_ID=tuo_client_id
LINKEDIN_CLIENT_SECRET=tuo_client_secret
LINKEDIN_ACCESS_TOKEN=AQV...token...
LINKEDIN_PERSON_URN=urn:li:person:ABC123
```

---

## 3️⃣ TWITTER / X

Twitter usa OAuth 2.0 con PKCE per le nuove app.

### Step 1: Crea App Twitter

1. Vai su **https://developer.twitter.com/en/portal/dashboard**
2. Clicca **+ Create Project**
3. Nome progetto: `StudioCentOS`
4. Use case: **Making a bot**
5. Clicca **Create App** dentro il progetto

### Step 2: Configura App

1. Vai su **App Settings** → **User authentication settings**
2. Clicca **Set up**
3. Configura:
   - **App permissions**: Read and Write
   - **Type of App**: Web App
   - **Callback URI**:
     ```
     https://studiocentos.com/api/v1/auth/twitter/callback
     ```
   - **Website URL**: `https://studiocentos.com`

### Step 3: Ottieni Credenziali

1. Vai su tab **Keys and tokens**
2. Rigenera e copia:
   - **API Key** (Consumer Key)
   - **API Key Secret** (Consumer Secret)
   - **Bearer Token**

### Step 4: Genera Access Token (OAuth 2.0)

```bash
# Richiedi autorizzazione (apri nel browser)
https://twitter.com/i/oauth2/authorize?
response_type=code&
client_id=TUO_CLIENT_ID&
redirect_uri=https://studiocentos.com/api/v1/auth/twitter/callback&
scope=tweet.read%20tweet.write%20users.read%20offline.access&
state=state&
code_challenge=challenge&
code_challenge_method=plain
```

Dopo autorizzazione, scambia il code:

```bash
curl -X POST https://api.twitter.com/2/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "CLIENT_ID:CLIENT_SECRET" \
  -d "grant_type=authorization_code" \
  -d "code=IL_TUO_CODE" \
  -d "redirect_uri=https://studiocentos.com/api/v1/auth/twitter/callback" \
  -d "code_verifier=challenge"
```

### Step 5: Salva le Credenziali

```bash
# Twitter / X
TWITTER_API_KEY=tuo_api_key
TWITTER_API_SECRET=tuo_api_secret
TWITTER_BEARER_TOKEN=AAAAAAA...bearer...
TWITTER_ACCESS_TOKEN=1234567890-abc...
TWITTER_ACCESS_SECRET=xyz...
```

---

## 4️⃣ CONFIGURAZIONE FINALE

### File .env Completo

Dopo aver ottenuto tutti i token, il tuo `.env` dovrebbe contenere:

```bash
# ============================================
# SOCIAL MEDIA TOKENS
# ============================================

# Meta / Facebook
META_APP_ID=832697706350252
META_APP_SECRET=8d1a6eddb0e4391bd2703cc5f651abd0
META_ACCESS_TOKEN=EAAL1VYrZBBqwBO...
FACEBOOK_PAGE_ID=162256733633265

# Instagram (usa stesso token Meta)
INSTAGRAM_ACCOUNT_ID=17841462985991568
INSTAGRAM_ACCESS_TOKEN=EAAL1VYrZBBqwBO...

# LinkedIn
LINKEDIN_CLIENT_ID=abc123
LINKEDIN_CLIENT_SECRET=xyz789
LINKEDIN_ACCESS_TOKEN=AQV...
LINKEDIN_PERSON_URN=urn:li:person:ABC123

# Twitter / X
TWITTER_API_KEY=abc
TWITTER_API_SECRET=xyz
TWITTER_BEARER_TOKEN=AAAA...
TWITTER_ACCESS_TOKEN=12345-abc
TWITTER_ACCESS_SECRET=xyz
```

### Riavvia Backend

Dopo aver aggiornato `.env`:

```bash
cd /home/autcir_gmail_com/studiocentos_ws/config/docker
docker-compose -f docker-compose.production.yml restart backend
```

### Verifica Configurazione

Testa che i token funzionino:

```bash
docker exec studiocentos-backend python -c "
from app.domain.social.publisher_service import SocialPublisherService
import asyncio

async def test():
    service = SocialPublisherService()
    platforms = service.get_configured_platforms()
    print(f'✅ Piattaforme configurate: {platforms}')
    await service.close()

asyncio.run(test())
"
```

---

## 🔄 Rinnovo Token

### Meta (Facebook/Instagram)
- **Durata**: 90 giorni
- **Rinnovo**: Ripeti Step 4-7 prima della scadenza
- **Promemoria**: Imposta reminder 80 giorni dopo la generazione

### LinkedIn
- **Durata**: 60 giorni
- **Rinnovo**: Usa refresh_token (se disponibile) o ripeti autorizzazione
- **Promemoria**: Imposta reminder 50 giorni dopo

### Twitter
- **Durata**: Non scade (Bearer Token)
- **Rinnovo**: Solo se revocato o rigenerato manualmente

---

## ❓ Troubleshooting

### "Error validating access token"
- **Causa**: Token scaduto o utente ha fatto logout
- **Soluzione**: Rigenera il token seguendo questa guida

### "Invalid OAuth access token"
- **Causa**: Token non ha i permessi necessari
- **Soluzione**: Verifica di aver selezionato tutti i permessi richiesti

### "Page not found" su Facebook
- **Causa**: L'app non ha accesso alla pagina
- **Soluzione**: Durante la generazione token, seleziona la pagina corretta

### "Instagram account not linked"
- **Causa**: Account Instagram non è Business/Creator
- **Soluzione**: Converti in Business Account e collega alla Pagina Facebook

### LinkedIn "Unauthorized"
- **Causa**: Token non ha scope `w_member_social`
- **Soluzione**: Ripeti autorizzazione con scope corretto

---

## 📞 Supporto

Per problemi con le API social, consulta:
- **Meta**: https://developers.facebook.com/support/
- **LinkedIn**: https://www.linkedin.com/help/linkedin
- **Twitter**: https://developer.twitter.com/en/support

---

*Ultimo aggiornamento: Dicembre 2025*
