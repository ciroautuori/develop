# 📧 Gmail API Setup - Guida Completa

## ✅ Modifiche Applicate al Codice

### **1. Scope Gmail Aggiunti**

**File modificati:**
- `apps/backend/app/core/google/scopes.py`
- `apps/backend/app/domain/auth/admin_service.py`

**Scope aggiunti:**
```python
GoogleScopes.GMAIL_READONLY  # Leggi email, profilo, labels
GoogleScopes.GMAIL_COMPOSE   # Crea bozze
```

**Aggiornati in:**
- `admin_full` scope set
- `backoffice_full` scope set
- `documents` scope set

---

## 🔧 STEP DA FARE SU GOOGLE CLOUD CONSOLE

### **STEP 1: Abilita Gmail API**

1. Vai su: https://console.cloud.google.com/apis/dashboard?project=civil-hologram-302513
2. Click **"+ ENABLE APIS AND SERVICES"**
3. Cerca **"Gmail API"**
4. Click **"ENABLE"**

✅ **Gmail API deve essere abilitata**

---

### **STEP 2: Aggiungi Scope OAuth**

1. Vai su: https://console.cloud.google.com/apis/credentials/consent?project=civil-hologram-302513
2. Sezione **"OAuth consent screen"**
3. Click **"EDIT APP"**
4. Vai a **"Scopes"** → Click **"ADD OR REMOVE SCOPES"**
5. **Aggiungi questi scope:**

```
https://www.googleapis.com/auth/gmail.send          ✅ (già presente)
https://www.googleapis.com/auth/gmail.readonly      ⚠️ DA AGGIUNGERE
https://www.googleapis.com/auth/gmail.compose       ⚠️ DA AGGIUNGERE
```

6. Click **"UPDATE"** e poi **"SAVE AND CONTINUE"**

---

### **STEP 3: Verifica Authorized Redirect URIs**

1. Vai su: https://console.cloud.google.com/apis/credentials?project=civil-hologram-302513
2. Click sul Client ID: `157170586454-so737s1k0bag7imtar3biskfhv2h0pau`
3. Sezione **"Authorized redirect URIs"**
4. Verifica che ci sia:

```
https://studiocentos.it/api/v1/admin/auth/google/callback
https://www.studiocentos.it/api/v1/admin/auth/google/callback
```

---

### **STEP 4: Testa gli Scope**

Dopo aver abilitato Gmail API e aggiunto gli scope:

1. **Logout** dall'admin dashboard
2. **Login di nuovo** con Google OAuth (studiocentos089@gmail.com)
3. Google ti chiederà di **autorizzare i nuovi permessi Gmail**
4. Accetta i permessi

---

## 🧪 Test API Gmail

Dopo il re-login, verifica che funzioni:

```bash
# 1. Recupera il token dal database
GOOGLE_TOKEN=$(docker exec studiocentos-db psql -U studiocentos -d studiocentos -t -A -c \
  "SELECT access_token FROM admin_google_settings ags JOIN admin_users a ON ags.admin_id = a.id WHERE a.email = 'studiocentos089@gmail.com';")

# 2. Test Gmail Profile (prima falliva)
curl -s "https://gmail.googleapis.com/gmail/v1/users/me/profile" \
  -H "Authorization: Bearer $GOOGLE_TOKEN" | jq .

# Output atteso:
{
  "emailAddress": "studiocentos089@gmail.com",
  "messagesTotal": 123,
  "threadsTotal": 45,
  "historyId": "..."
}

# 3. Test Gmail Labels
curl -s "https://gmail.googleapis.com/gmail/v1/users/me/labels" \
  -H "Authorization: Bearer $GOOGLE_TOKEN" | jq '.labels[0:3]'

# 4. Test Gmail Messages List
curl -s "https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=5" \
  -H "Authorization: Bearer $GOOGLE_TOKEN" | jq .
```

---

## 📋 Scope Gmail - Differenze

| Scope | Permessi | Quando usarlo |
|-------|----------|---------------|
| `gmail.send` | ✅ Solo invio email | Notifiche automatiche |
| `gmail.compose` | ✅ Creare bozze e inviare | Preventivi e proposte |
| `gmail.readonly` | ✅ Leggere email, profilo, labels | Dashboard analytics email |
| `gmail.modify` | ✅ Leggere + modificare + archiviare | Gestione completa inbox |
| `https://mail.google.com/` | 🔴 Accesso completo Gmail | ⚠️ Troppo permissivo |

**Configurazione attuale:**
- ✅ `gmail.send` (invio)
- ✅ `gmail.readonly` (lettura)
- ✅ `gmail.compose` (bozze)

---

## 🔐 Verifica Scope Salvati nel Database

```sql
SELECT
    a.email,
    ags.scopes
FROM admin_google_settings ags
JOIN admin_users a ON ags.admin_id = a.id
WHERE a.email = 'studiocentos089@gmail.com';
```

**Scope attesi dopo re-login:**
```
openid
email
profile
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.readonly ← NUOVO
https://www.googleapis.com/auth/gmail.compose  ← NUOVO
https://www.googleapis.com/auth/drive
https://www.googleapis.com/auth/analytics.readonly
https://www.googleapis.com/auth/business.manage
https://www.googleapis.com/auth/documents
https://www.googleapis.com/auth/calendar.events
```

---

## ⚠️ Troubleshooting

### **Errore: "Insufficient Permission"**

**Causa:** Gmail API non abilitata su Google Cloud Console
**Soluzione:** STEP 1 - Abilita Gmail API

### **Errore: "Access blocked: This app's request is invalid"**

**Causa:** Scope non autorizzati nell'OAuth consent screen
**Soluzione:** STEP 2 - Aggiungi scope Gmail

### **Errore: 401 "Invalid Credentials"**

**Causa:** Token non ha i nuovi scope
**Soluzione:** Logout → Login di nuovo per ottenere nuovi permessi

### **Gmail API risponde ma senza dati**

**Causa:** Scope `gmail.send` consente solo invio, non lettura
**Soluzione:** Verifica scope nel database (query sopra)

---

## 🎯 Checklist Completa

- [ ] **Gmail API abilitata** su Google Cloud Console
- [ ] **Scope `gmail.readonly`** aggiunto all'OAuth consent screen
- [ ] **Scope `gmail.compose`** aggiunto all'OAuth consent screen
- [ ] **Codice backend** aggiornato (✅ fatto)
- [ ] **Backend riavviato** (✅ fatto)
- [ ] **Logout** dall'admin dashboard
- [ ] **Login di nuovo** con Google OAuth
- [ ] **Accettato** nuovi permessi Gmail
- [ ] **Test API Gmail** funzionanti

---

## 📞 API Gmail Disponibili Dopo Setup

### **1. Profilo Gmail**
```bash
GET https://gmail.googleapis.com/gmail/v1/users/me/profile
```

### **2. Lista Labels**
```bash
GET https://gmail.googleapis.com/gmail/v1/users/me/labels
```

### **3. Lista Messaggi**
```bash
GET https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=10
```

### **4. Leggi Messaggio**
```bash
GET https://gmail.googleapis.com/gmail/v1/users/me/messages/{messageId}
```

### **5. Invia Email**
```bash
POST https://gmail.googleapis.com/gmail/v1/users/me/messages/send
```

### **6. Crea Bozza**
```bash
POST https://gmail.googleapis.com/gmail/v1/users/me/drafts
```

---

## 🚀 Prossimi Passi

1. **Vai su Google Cloud Console** e completa STEP 1 e 2
2. **Fai logout** dal dashboard admin
3. **Login di nuovo** con Google OAuth
4. **Testa le API Gmail** con i comandi sopra

✅ **Dopo questi step, Gmail API sarà completamente funzionante!**
