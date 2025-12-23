# 🔑 GUIDA CONFIGURAZIONE API KEYS - StudioCentOS

**Data**: 10 Dicembre 2025
**Versione**: 1.0
**Scopo**: Configurare tutte le API mancanti per il sistema Marketing AI

---

## 📋 INDICE

1. [Veo 3.1 - Google Video AI](#1-veo-31---google-video-ai)
2. [Apollo.io - Lead Intelligence](#2-apolloio---lead-intelligence)
3. [SendGrid - Email Marketing](#3-sendgrid---email-marketing)
4. [Twitter/X API](#4-twitterx-api)
5. [LinkedIn Marketing API](#5-linkedin-marketing-api)
6. [Threads API](#6-threads-api)
7. [Configurazione Finale](#7-configurazione-finale)

---

## 1. VEO 3.1 - Google Video AI

### Cos'è
Veo 3.1 è il modello di generazione video di Google, parte di Vertex AI. Genera video professionali da prompt testuali.

### Prerequisiti
- Account Google Cloud con fatturazione attiva
- Progetto Google Cloud esistente

### Passaggi

#### 1.1 Accedi a Google Cloud Console
```
https://console.cloud.google.com/
```

#### 1.2 Abilita Vertex AI API
1. Vai a **APIs & Services** → **Library**
2. Cerca "Vertex AI API"
3. Clicca **Enable**

#### 1.3 Abilita Imagen/Veo API
1. Cerca "Imagen API" o "Generative AI on Vertex AI"
2. Clicca **Enable**

#### 1.4 Crea Service Account
1. Vai a **IAM & Admin** → **Service Accounts**
2. Clicca **Create Service Account**
3. Nome: `studiocentos-ai-service`
4. Ruoli da assegnare:
   - `Vertex AI User`
   - `Vertex AI Service Agent`
   - `Storage Object Viewer` (per output video)

#### 1.5 Genera JSON Key
1. Clicca sul service account creato
2. Tab **Keys** → **Add Key** → **Create new key**
3. Seleziona **JSON**
4. Salva il file come `google-credentials.json`

#### 1.6 Richiedi Accesso Veo (se necessario)
Veo 3.1 potrebbe richiedere accesso allowlist:
1. Vai a: https://cloud.google.com/vertex-ai/generative-ai/docs/image/generate-videos
2. Compila il form di richiesta accesso
3. Attendi approvazione (1-5 giorni lavorativi)

### Variabili da Aggiungere
```bash
# In .env.production
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-credentials.json
# Oppure inline:
GOOGLE_CREDENTIALS_JSON='{"type":"service_account","project_id":"...","private_key":"..."}'
```

### Costo Stimato
- Veo 3.1: ~$0.05-0.10 per secondo di video generato
- Video 5s: ~$0.25-0.50

---

## 2. APOLLO.IO - Lead Intelligence

### Cos'è
Apollo.io è una piattaforma di sales intelligence per trovare contatti B2B, email aziendali e informazioni su decision makers.

### Passaggi

#### 2.1 Registrazione
```
https://www.apollo.io/
```
1. Clicca **Sign Up Free**
2. Registrati con email aziendale (preferibile @studiocentos.it)

#### 2.2 Scegli Piano
| Piano | Crediti/mese | Costo |
|-------|--------------|-------|
| Free | 50 email lookups | $0 |
| Basic | 900 credits | $49/mese |
| Professional | 3,000 credits | $79/mese |
| Organization | Unlimited | $119/mese |

**Consiglio**: Inizia con **Free** per testare, poi passa a **Basic**.

#### 2.3 Genera API Key
1. Login su Apollo.io
2. Vai a **Settings** (icona ingranaggio)
3. **Integrations** → **API**
4. Clicca **Generate API Key**
5. Copia la chiave (inizia con `api_...`)

### Variabili da Aggiungere
```bash
# In .env.production
APOLLO_API_KEY=api_xxxxxxxxxxxxxxxxxxxxxxxx
```

### Funzionalità Attivate
Con Apollo.io attivo, il sistema potrà:
- ✅ Cercare contatti per industria/location/ruolo
- ✅ Trovare email verificate di decision makers
- ✅ Arricchire dati aziendali (fatturato, dipendenti, tecnologie)
- ✅ Creare liste di prospect automatiche

---

## 3. SENDGRID - Email Marketing

### Cos'è
SendGrid (Twilio) è una piattaforma per email transazionali e marketing con alta deliverability.

### Passaggi

#### 3.1 Registrazione
```
https://sendgrid.com/
```
1. Clicca **Start for Free**
2. Registrati con email

#### 3.2 Scegli Piano
| Piano | Email/mese | Costo |
|-------|------------|-------|
| Free | 100/giorno | $0 |
| Essentials | 50,000 | $19.95/mese |
| Pro | 100,000 | $89.95/mese |

**Consiglio**: **Free** per iniziare (3,000 email/mese).

#### 3.3 Verifica Dominio (IMPORTANTE!)
1. Vai a **Settings** → **Sender Authentication**
2. **Authenticate Your Domain**
3. Aggiungi: `studiocentos.it`
4. Copia i record DNS forniti:
   ```
   CNAME: em1234.studiocentos.it → sendgrid.net
   CNAME: s1._domainkey.studiocentos.it → s1.domainkey.xxx.sendgrid.net
   CNAME: s2._domainkey.studiocentos.it → s2.domainkey.xxx.sendgrid.net
   ```
5. Aggiungi questi record nel pannello DNS di Register.it
6. Torna su SendGrid e clicca **Verify**

#### 3.4 Genera API Key
1. **Settings** → **API Keys**
2. Clicca **Create API Key**
3. Nome: `StudioCentOS Production`
4. Permessi: **Full Access** (o seleziona: Mail Send, Marketing)
5. Copia la chiave (inizia con `SG.`)

### Variabili da Aggiungere
```bash
# In .env.production
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=info@studiocentos.it
SENDGRID_FROM_NAME=StudioCentOS
```

### Funzionalità Attivate
- ✅ Email transazionali (conferme, notifiche)
- ✅ Campagne email marketing
- ✅ Template email professionali
- ✅ Analytics aperture/click
- ✅ A/B testing subject lines
- ✅ Gestione liste contatti

---

## 4. TWITTER/X API

### Cos'è
API ufficiale di Twitter/X per pubblicare tweet, leggere analytics e gestire il profilo.

### Passaggi

#### 4.1 Accedi al Developer Portal
```
https://developer.twitter.com/
```

#### 4.2 Crea App
1. Clicca **Create Project**
2. Nome progetto: `StudioCentOS Marketing`
3. Use case: **Making a bot** o **Managing ads**
4. Crea App dentro il progetto

#### 4.3 Scegli Piano API
| Piano | Tweets/mese | Costo |
|-------|-------------|-------|
| Free | 1,500 (solo lettura) | $0 |
| Basic | 50,000 | $100/mese |
| Pro | 1,000,000 | $5,000/mese |

**Consiglio**: **Basic** è sufficiente per posting automatico.

#### 4.4 Genera Credenziali
1. Nella tua App, vai a **Keys and Tokens**
2. Genera:
   - **API Key** (Consumer Key)
   - **API Key Secret** (Consumer Secret)
   - **Access Token**
   - **Access Token Secret**
   - **Bearer Token**

#### 4.5 Configura Permessi
1. **App Settings** → **User authentication settings**
2. Abilita **OAuth 1.0a**
3. Permessi: **Read and Write**
4. Callback URL: `https://studiocentos.it/api/v1/social/twitter/callback`

### Variabili da Aggiungere
```bash
# In .env.production
TWITTER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_ACCESS_TOKEN=xxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_ACCESS_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 5. LINKEDIN MARKETING API

### Cos'è
API LinkedIn per pubblicare post, gestire Company Page e accedere ad analytics.

### Passaggi

#### 5.1 Crea LinkedIn App
```
https://www.linkedin.com/developers/apps
```
1. Clicca **Create App**
2. Nome: `StudioCentOS Marketing`
3. Company Page: Seleziona la pagina StudioCentOS
4. Logo: Carica logo aziendale

#### 5.2 Richiedi Prodotti API
Nella tab **Products**, richiedi:
- ✅ **Share on LinkedIn** (posting)
- ✅ **Sign In with LinkedIn using OpenID Connect**
- ✅ **Marketing Developer Platform** (per Company Page)

⚠️ **Marketing Developer Platform** richiede approvazione (1-2 settimane).

#### 5.3 Genera Credenziali
1. Tab **Auth**
2. Copia:
   - **Client ID**
   - **Client Secret**

#### 5.4 Genera Access Token
Per generare un token duraturo:
1. Vai a: https://www.linkedin.com/developers/tools/oauth
2. Seleziona la tua app
3. Scopes richiesti:
   - `w_member_social` (post come utente)
   - `w_organization_social` (post come Company Page)
   - `r_organization_social`
4. Genera token e copia

### Variabili da Aggiungere
```bash
# In .env.production
LINKEDIN_CLIENT_ID=xxxxxxxxxxxxxx
LINKEDIN_CLIENT_SECRET=xxxxxxxxxxxxxxxx
LINKEDIN_ACCESS_TOKEN=AQVxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LINKEDIN_ORGANIZATION_ID=xxxxxxxx  # Company Page ID
```

#### Come trovare Organization ID
1. Vai sulla tua Company Page LinkedIn
2. Clicca **Admin tools** → **View as member**
3. L'URL sarà: `linkedin.com/company/12345678`
4. `12345678` è il tuo Organization ID

---

## 6. THREADS API

### Cos'è
API di Threads (Meta) per pubblicare post sulla piattaforma Threads.

### Prerequisiti
- Hai già configurato META_APP_ID e META_APP_SECRET
- L'app Meta deve avere i permessi Threads

### Passaggi

#### 6.1 Abilita Threads sulla App Meta
1. Vai a: https://developers.facebook.com/apps/1379102196930807/
2. **Add Products** → Cerca "Threads"
3. Clicca **Set Up**

#### 6.2 Configura Permessi
1. **App Review** → **Permissions and Features**
2. Richiedi:
   - `threads_basic`
   - `threads_content_publish`
   - `threads_manage_insights`
   - `threads_manage_replies`

#### 6.3 Genera Access Token
1. Vai a Graph API Explorer: https://developers.facebook.com/tools/explorer/
2. Seleziona la tua app
3. Aggiungi permessi:
   - `threads_basic`
   - `threads_content_publish`
4. Clicca **Generate Access Token**
5. Copia il token

#### 6.4 Ottieni Threads User ID
```bash
curl -X GET "https://graph.threads.net/v1.0/me?access_token=YOUR_TOKEN"
```
La risposta conterrà il tuo `id`.

### Variabili da Aggiungere
```bash
# In .env.production
THREADS_APP_ID=1379102196930807  # Stesso di META_APP_ID
THREADS_APP_SECRET=30c0af296ee8c2c91cd59214219ff177  # Stesso di META
THREADS_ACCESS_TOKEN=THQWxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
THREADS_USER_ID=xxxxxxxxxxxxxxxxxx
```

---

## 7. CONFIGURAZIONE FINALE

### 7.1 Aggiorna .env.production

Aggiungi tutte le variabili al file:
```bash
nano /home/autcir_gmail_com/studiocentos_ws/config/docker/.env.production
```

Aggiungi in fondo:
```bash
# ============================================================================
# API AGGIUNTIVE - Marketing AI Complete
# ============================================================================

# Veo 3.1 / Google Cloud (Video Generation)
GOOGLE_CLOUD_PROJECT=studiocentos-ai
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/google-credentials.json

# Apollo.io (Lead Intelligence)
APOLLO_API_KEY=api_xxxxxxxxxxxxxxxxxxxxxxxx

# SendGrid (Email Marketing)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=info@studiocentos.it
SENDGRID_FROM_NAME=StudioCentOS

# Twitter/X
TWITTER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_ACCESS_TOKEN=xxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_ACCESS_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# LinkedIn
LINKEDIN_CLIENT_ID=xxxxxxxxxxxxxx
LINKEDIN_CLIENT_SECRET=xxxxxxxxxxxxxxxx
LINKEDIN_ACCESS_TOKEN=AQVxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LINKEDIN_ORGANIZATION_ID=xxxxxxxx

# Threads
THREADS_ACCESS_TOKEN=THQWxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
THREADS_USER_ID=xxxxxxxxxxxxxxxxxx
```

### 7.2 Rebuild Docker
```bash
cd /home/autcir_gmail_com/studiocentos_ws/config/docker
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml build --no-cache ai_microservice
docker compose -f docker-compose.production.yml up -d
```

### 7.3 Verifica
```bash
# Health check
curl -s http://localhost:8001/health | jq .

# Test con nuove API
curl -s http://localhost:8001/api/v1/marketing/leads/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-api-key-change-in-production" \
  -d '{"industry":"tech","location":"Milano","size":"medium"}' | jq .
```

---

## 📊 RIEPILOGO COSTI MENSILI STIMATI

| Servizio | Piano | Costo/mese |
|----------|-------|------------|
| **Veo 3.1** | Pay-per-use | ~$10-50 (uso moderato) |
| **Apollo.io** | Basic | $49 |
| **SendGrid** | Free/Essentials | $0-19.95 |
| **Twitter/X** | Basic | $100 |
| **LinkedIn** | Free | $0 |
| **Threads** | Free | $0 |
| **TOTALE** | | **$159-219/mese** |

### Alternative Gratuite
- **Video**: Usa HeyGen (già configurato) invece di Veo
- **Leads**: ML fallback funziona (già attivo)
- **Email**: SMTP Register.it (già configurato)
- **Twitter**: Posting manuale

---

## ✅ CHECKLIST FINALE

Dopo aver completato la guida, forniscimi:

```
□ APOLLO_API_KEY=api_...
□ SENDGRID_API_KEY=SG....
□ TWITTER_API_KEY=...
□ TWITTER_API_SECRET=...
□ TWITTER_ACCESS_TOKEN=...
□ TWITTER_ACCESS_SECRET=...
□ TWITTER_BEARER_TOKEN=...
□ LINKEDIN_CLIENT_ID=...
□ LINKEDIN_CLIENT_SECRET=...
□ LINKEDIN_ACCESS_TOKEN=...
□ LINKEDIN_ORGANIZATION_ID=...
□ THREADS_ACCESS_TOKEN=...
□ THREADS_USER_ID=...
□ GOOGLE_CLOUD_PROJECT=... (per Veo, opzionale)
```

Quando me li fornirai, li inserirò nel sistema e farò il rebuild! 🚀

---

**Autore**: AI Agent
**Ultimo Aggiornamento**: 10 Dicembre 2025
