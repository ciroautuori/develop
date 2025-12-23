# 📋 TO-DO LIST PRIORITARIO - Dicembre 2025

> Creato: 6 Dicembre 2025
> Obiettivo: Risolvere token social, eliminare WhatsApp, configurare Threads, potenziare SEO

---

## 🔴 PRIORITÀ 1 - TOKEN FACEBOOK/INSTAGRAM SCADONO

### ❌ PROBLEMA
I token Meta (Facebook/Instagram) scadono ogni giorno perché:
1. **Short-lived token** (1 ora) - Generato da Graph API Explorer
2. **Long-lived token** (60 giorni) - Da convertire manualmente
3. **Nessun refresh automatico** - Il sistema non rinnova i token

### ✅ SOLUZIONE
1. **Convertire a Long-Lived Token** (dura 60 giorni):
   ```bash
   GET /oauth/access_token?
     grant_type=fb_exchange_token&
     client_id={app-id}&
     client_secret={app-secret}&
     fb_exchange_token={short-lived-token}
   ```

2. **Implementare Token Refresh Automatico**:
   - Cron job che controlla expiry ogni 24h
   - Refresh automatico 7 giorni prima della scadenza
   - Notifica email quando token sta per scadere

3. **Setup OAuth Flow Completo** (raccomandato):
   - Implementare login OAuth nel Marketing Hub
   - Salvare token in database con expiry date
   - Refresh automatico via Meta Graph API

### 📁 FILE DA MODIFICARE
- `apps/backend/app/integrations/social_media.py` - Aggiungere token refresh
- `apps/backend/app/domain/social/token_refresh_service.py` - NUOVO: Servizio refresh token
- `apps/backend/app/core/config.py` - Aggiungere META_TOKEN_EXPIRES_AT
- `.env.production` - Aggiornare con nuovo long-lived token

### ⏱️ TEMPO STIMATO: 2-3 ore

---

## 🟠 PRIORITÀ 2 - RIMUOVERE WHATSAPP

### ❌ STATO ATTUALE
WhatsApp Business API è configurato ma **non utilizzato** (usiamo l'app mobile).
Occupa risorse e complica la configurazione.

### ✅ AZIONE
Rimuovere completamente WhatsApp dal backend:

### 📁 FILE DA MODIFICARE
- [x] `apps/backend/app/main.py` - Rimuovere import e router WhatsApp (righe 287-289)
- [ ] `apps/backend/app/domain/whatsapp/` - Eliminare intera cartella
- [ ] `apps/backend/app/core/config.py` - Rimuovere config WhatsApp (righe 235-240)
- [ ] `.env.production` - Rimuovere variabili WHATSAPP_*

### ⏱️ TEMPO STIMATO: 30 minuti

---

## 🟡 PRIORITÀ 3 - CONFIGURARE THREADS

### ✅ STATO ATTUALE
Threads è **già implementato** nel codice:
- `apps/backend/app/integrations/social_media.py` - publish_threads() esiste
- `apps/backend/app/core/config.py` - THREADS_* config esiste

### ❌ MANCA
1. Token di accesso Threads
2. User ID Threads
3. Test pubblicazione

### ✅ AZIONE
1. **Ottenere Token Threads**:
   - Vai su https://developers.facebook.com
   - Seleziona l'app StudioCentOS
   - Products → Threads → Aggiungi
   - Genera token con permessi: `threads_basic`, `threads_content_publish`

2. **Aggiornare .env.production**:
   ```env
   THREADS_APP_ID=<tuo-app-id>
   THREADS_APP_SECRET=<tuo-app-secret>
   THREADS_ACCESS_TOKEN=<token-generato>
   THREADS_USER_ID=<tuo-user-id>
   ```

3. **Aggiungere Threads al ContentStudio** (frontend)

### 📁 FILE DA MODIFICARE
- `.env.production` - Aggiungere credenziali Threads
- `apps/frontend/.../ContentStudio.tsx` - Aggiungere Threads come piattaforma

### ⏱️ TEMPO STIMATO: 1 ora

---

## 🟢 PRIORITÀ 4 - POTENZIARE SEO

### ❌ PROBLEMA ATTUALE
Appariamo solo per "Software House Salerno" ma NON per:
- "Intelligenza Artificiale Salerno"
- "AI Salerno"
- "Sviluppo AI Campania"
- "Automazione AI Salerno"
- "Machine Learning Salerno"

### ✅ ANALISI ATTUALE
**index.html** ha già:
- ✅ Meta description con "AI"
- ✅ Keywords con "sviluppo ai salerno"
- ✅ Schema.org LocalBusiness
- ✅ Geo tags Salerno

**MANCA**:
1. ❌ Pagina dedicata "Servizi AI" (contenuto unico per ranking)
2. ❌ Keywords più aggressive per AI
3. ❌ Blog/articoli su AI (contenuto fresco)
4. ❌ Backlinks da siti AI
5. ❌ Google Business Profile ottimizzato per AI
6. ❌ Sitemap con pagine AI

### ✅ AZIONI SEO

#### 4.1 - MIGLIORARE META TAGS (IMMEDIATO)
```html
<meta name="keywords" content="
  intelligenza artificiale salerno,
  ai salerno,
  sviluppo ai campania,
  machine learning salerno,
  automazione intelligente salerno,
  chatbot ai salerno,
  software ai italia,
  consulenza ai salerno,
  sviluppo software ai,
  integrazione ai aziendale,
  software house salerno,
  sviluppo web salerno,
  ...
" />
```

#### 4.2 - AGGIORNARE SCHEMA.ORG
Aggiungere più serviceType AI-focused:
```json
"serviceType": [
  "Intelligenza Artificiale",
  "Machine Learning",
  "Sviluppo Chatbot AI",
  "Automazione Processi AI",
  "Integrazione AI Aziendale",
  "Sviluppo Web",
  "App Mobile",
  ...
]
```

#### 4.3 - CREARE PAGINA SERVIZI AI (NUOVO)
Creare `/servizi/intelligenza-artificiale` con:
- H1: "Intelligenza Artificiale a Salerno"
- Contenuto unico 1000+ parole
- Case studies
- FAQ strutturate (Schema.org)

#### 4.4 - AGGIORNARE SITEMAP
Aggiungere:
```xml
<url>
  <loc>https://studiocentos.it/servizi/intelligenza-artificiale</loc>
  <priority>0.9</priority>
</url>
<url>
  <loc>https://studiocentos.it/servizi/sviluppo-chatbot</loc>
  <priority>0.8</priority>
</url>
```

#### 4.5 - GOOGLE BUSINESS PROFILE
- Aggiungere categoria "Intelligenza Artificiale"
- Aggiungere servizi AI nel profilo
- Post settimanali su AI

### 📁 FILE DA MODIFICARE
- `apps/frontend/index.html` - Meta tags potenziati
- `apps/frontend/public/sitemap.xml` - Nuove pagine
- `apps/frontend/src/pages/ServicesAI.tsx` - NUOVO: Pagina servizi AI

### ⏱️ TEMPO STIMATO: 4-6 ore (contenuto + sviluppo)

---

## 📊 RIEPILOGO

| Priorità | Task | Tempo | Impatto |
|----------|------|-------|---------|
| 🔴 1 | Token Refresh Facebook/Instagram | 2-3h | CRITICO |
| 🟠 2 | Rimuovere WhatsApp | 30min | Pulizia |
| 🟡 3 | Configurare Threads | 1h | Espansione |
| 🟢 4 | Potenziare SEO AI | 4-6h | Visibilità |

---

## 🚀 STATO IMPLEMENTAZIONE

### ✅ COMPLETATO (6 Dicembre 2025)

1. ✅ **WhatsApp RIMOSSO** - Router disabilitato in main.py
2. ✅ **SEO POTENZIATA** - Meta tags, keywords, Schema.org per TUTTI i servizi
3. ✅ **Sitemap AGGIORNATA** - 10+ pagine servizi indicizzate
4. ✅ **Threads AGGIUNTO** - Piattaforma nel ContentStudio
5. ✅ **Token Service CREATO** - Sistema verifica/refresh token Meta
6. ✅ **Endpoint Token AGGIUNTI**:
   - `GET /api/v1/social/token/status` - Verifica stato token
   - `GET /api/v1/social/token/refresh-instructions` - Istruzioni refresh
   - `POST /api/v1/social/token/convert-to-long-lived` - Converti token

### ⚠️ AZIONE MANUALE RICHIESTA

**RINNOVO TOKEN META (Facebook/Instagram)**:

1. Vai su: https://developers.facebook.com/tools/explorer/
2. Genera nuovo token con permessi:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `instagram_basic`
   - `instagram_content_publish`
3. Usa endpoint `/api/v1/social/token/convert-to-long-lived` per convertire
4. Aggiorna `META_ACCESS_TOKEN` in `.env.production`
5. Restart backend: `docker compose restart backend`

---

## 📊 KEYWORD SEO IMPLEMENTATE

### Servizi Primari (Priority 0.95)
- sviluppo siti web salerno
- app mobile salerno
- e-commerce salerno
- intelligenza artificiale salerno

### Servizi Secondari (Priority 0.90)
- chatbot salerno
- dashboard analytics salerno
- automazione marketing salerno

### Servizi Terzi (Priority 0.85)
- web design salerno
- consulenza it salerno
- software gestionali salerno

---

## 🎯 OTTIMIZZAZIONI FUTURE

1. [ ] Creare pagine dedicate per ogni servizio (non solo anchor #)
2. [ ] Blog con articoli SEO-friendly
3. [ ] Case studies dettagliati per ogni servizio
4. [ ] Google Business Profile ottimizzato
5. [ ] Backlinks da directory locali Salerno/Campania
6. [ ] Recensioni Google (Social Proof)

---

*Documento aggiornato: 6 Dicembre 2025 - Cascade AI*
