# Google Cloud Setup Guide - StudioCentOS

> **Guida completa** per configurare tutte le API Google necessarie.

## 🎯 API Richieste

| API | Scopo | Obbligatoria |
|-----|-------|--------------|
| **OAuth 2.0** | Login, Analytics, Business, Calendar | ✅ SÌ |
| **Places API (New)** | Lead Finder | ✅ SÌ |
| **PageSpeed Insights** | SEO Tools | ⚠️ Opzionale |
| **Generative Language** | AI (Gemini) | ⚠️ Opzionale |

---

## 1️⃣ Creare Progetto Google Cloud

1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Crea nuovo progetto: **StudioCentOS**
3. Seleziona il progetto creato

---

## 2️⃣ Abilitare le API

Vai su **APIs & Services → Library** e abilita:

### Obbligatorie
- [x] **Google+ API** (deprecata ma necessaria per OAuth)
- [x] **People API** (per user info)
- [x] **Places API (New)** - [Link diretto](https://console.cloud.google.com/apis/library/places-backend.googleapis.com)

### Per Analytics/Business (se usate)
- [x] **Google Analytics Data API**
- [x] **Google My Business API**
- [x] **Google Calendar API**

### Opzionali
- [ ] **PageSpeed Insights API**
- [ ] **Generative Language API** (Gemini)

---

## 3️⃣ Creare Credenziali OAuth 2.0

1. Vai su **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth client ID**
3. Tipo: **Web application**
4. Nome: **StudioCentOS Web**

### ⚠️ IMPORTANTE: Authorized redirect URIs

Devi aggiungere **ENTRAMBI** questi URI:

```
https://studiocentos.it/api/v1/auth/google/callback
https://studiocentos.it/api/v1/admin/google/callback
```

Per development aggiungi anche:
```
http://localhost:8000/api/v1/auth/google/callback
http://localhost:8000/api/v1/admin/google/callback
```

5. Salva e copia:
   - **Client ID**: `xxx.apps.googleusercontent.com`
   - **Client Secret**: `GOCSPX-xxx`

---

## 4️⃣ Creare API Key

1. **APIs & Services → Credentials**
2. **Create Credentials → API Key**
3. Rinomina: **StudioCentOS API Key**
4. Click **Edit** per limitare:

### Restrizioni Consigliate

**Application restrictions:**
- HTTP referrers (websites)
- Aggiungi: `studiocentos.it/*`, `*.studiocentos.it/*`

**API restrictions:**
- Restrict key
- Seleziona: Places API (New), PageSpeed Insights API

5. Copia l'API Key

---

## 5️⃣ Configurare OAuth Consent Screen

1. **APIs & Services → OAuth consent screen**
2. User Type: **External**
3. Compila:
   - **App name**: StudioCentOS
   - **User support email**: tua email
   - **Developer contact**: tua email

### Scopes Richiesti

Aggiungi questi scopes:

```
openid
https://www.googleapis.com/auth/userinfo.email
https://www.googleapis.com/auth/userinfo.profile
https://www.googleapis.com/auth/analytics.readonly
https://www.googleapis.com/auth/business.manage
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/calendar.events
```

4. **Publish App** (per produzione)

---

## 6️⃣ Configurare .env

Aggiorna il file `.env` o `.env.production`:

```env
# OAuth 2.0
GOOGLE_CLIENT_ID=780906650552-xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxx

# API Keys
GOOGLE_API_KEY=AIzaSyXXX
GOOGLE_PLACES_API_KEY=AIzaSyXXX

# URLs
BASE_URL=https://studiocentos.it
BACKEND_URL=https://studiocentos.it

# Analytics (opzionale)
GA4_PROPERTY_ID=properties/123456789

# Gemini AI (opzionale)
GOOGLE_AI_API_KEY=AIzaSyXXX
```

---

## 7️⃣ Verifica Configurazione

Esegui il test:

```bash
cd /home/autcir_gmail_com/studiocentos_ws
python scripts/tests/test_google_apis.py
```

---

## 🐛 Troubleshooting

### Errore: `redirect_uri_mismatch`
- Verifica che ENTRAMBI i redirect URI siano registrati nella Cloud Console
- Verifica che non ci siano spazi o caratteri extra

### Errore: `access_denied`
- L'app non è pubblicata (OAuth Consent Screen)
- L'utente non ha i permessi necessari

### Errore: `invalid_grant`
- Il token è scaduto
- L'utente deve ri-autenticarsi

### Errore: `403 Forbidden` su Places API
- Verifica che Places API (New) sia abilitata
- Verifica che il billing sia attivo
- Verifica le quote API

### Errore CORS `play.google.com/log`
- Questo è un warning delle librerie Google client-side
- **Ignorabile** - non influisce sul funzionamento

---

## 📊 Costi API

| API | Costo |
|-----|-------|
| OAuth | Gratuito |
| Places API | $17/1000 richieste (primi $200/mese gratis) |
| PageSpeed | Gratuito |
| Gemini | Gratuito (tier free) |
| Analytics | Gratuito |

---

## ✅ Checklist Finale

- [ ] Progetto creato su Google Cloud
- [ ] APIs abilitate (OAuth, Places, etc.)
- [ ] OAuth Client ID creato
- [ ] **Entrambi** i redirect URI registrati
- [ ] API Key creata e limitata
- [ ] OAuth Consent Screen configurato
- [ ] Scopes aggiunti
- [ ] .env aggiornato
- [ ] Test passato
