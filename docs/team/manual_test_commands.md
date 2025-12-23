# 🧪 **ISS MANUAL SMOKE TEST - COMANDI CURL**

> **Test manuali con curl per verificare tutti i sistemi ISS con dati reali**

## 🏥 **1. HEALTH CHECKS**

```bash
# Backend Health
curl -s http://localhost:8000/health | jq .

# Expected: {"status": "healthy", "timestamp": ..., "environment": "development"}
```

## 📋 **2. SISTEMA BANDI - ENDPOINTS PUBBLICI**

```bash
# Lista tutti i bandi
curl -s http://localhost:8000/api/v1/bandi/ | jq .

# Statistiche bandi
curl -s http://localhost:8000/api/v1/bandi/stats | jq .

# Ricerca bandi
curl -s "http://localhost:8000/api/v1/bandi/?query=test&limit=5" | jq .

# Filtro per fonte
curl -s "http://localhost:8000/api/v1/bandi/?fonte=comune_salerno" | jq .

# Filtro per importo
curl -s "http://localhost:8000/api/v1/bandi/?importo_min=1000&importo_max=50000" | jq .

# Ordinamento
curl -s "http://localhost:8000/api/v1/bandi/?sort=scadenza&limit=10" | jq .
```

## 👤 **3. SISTEMA USERS - REGISTRAZIONE**

```bash
# Health check auth
curl -s http://localhost:8000/api/v1/auth/health | jq .

# Registrazione nuovo cittadino
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_'$(date +%s)'@example.com",
    "password": "TestUser2025!",
    "nome": "Mario",
    "cognome": "Rossi",
    "role": "cittadino",
    "accessibility_needs": "none",
    "privacy_policy_accepted": true,
    "newsletter_subscription": true
  }' | jq .

# Registrazione APS
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "aps_test_'$(date +%s)'@example.com",
    "password": "ApsTest2025!",
    "nome": "Giulia",
    "cognome": "Verdi",
    "role": "aps_responsabile",
    "aps_nome_organizzazione": "APS Test Smoke",
    "aps_citta": "Salerno",
    "aps_settore_attivita": "Test e sviluppo",
    "accessibility_needs": "none",
    "privacy_policy_accepted": true
  }' | jq .

# Registrazione utente con accessibilità
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "access_test_'$(date +%s)'@example.com",
    "password": "AccessTest2025!",
    "nome": "Anna",
    "cognome": "Blu",
    "role": "cittadino",
    "accessibility_needs": "screen_reader",
    "privacy_policy_accepted": true
  }' | jq .
```

## 🔐 **4. LOGIN E AUTENTICAZIONE**

```bash
# Login Admin (se utenti test esistono)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@iss.salerno.it",
    "password": "AdminISS2025!"
  }' | jq .

# Salva il token per i test successivi
ADMIN_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." # Sostituisci con token reale

# Login APS Responsabile
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "responsabile@aps-esempio.it",
    "password": "ApsResp2025!"
  }' | jq .

# Login Cittadino
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "cittadino@example.com",
    "password": "Cittadino2025!"
  }' | jq .

# Login utente con accessibilità
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "accessibile@example.com",
    "password": "Access2025!"
  }' | jq .
```

## 👤 **5. PROFILO UTENTE AUTENTICATO**

```bash
# Sostituisci TOKEN con il token ottenuto dal login
TOKEN="your_jwt_token_here"

# Profilo utente corrente
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/auth/me | jq .

# Profilo completo
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/users/me | jq .

# Preferenze utente
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/users/me/preferences | jq .

# Attività utente
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/users/me/activity | jq .
```

## ✏️ **6. AGGIORNAMENTO PROFILO**

```bash
# Aggiorna profilo
curl -X PUT http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Profilo aggiornato durante smoke test",
    "telefono": "+39 089 123456"
  }' | jq .

# Aggiorna preferenze
curl -X PUT http://localhost:8000/api/v1/users/me/preferences \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "dark",
    "font_size": "large",
    "notify_new_bandi": true,
    "alert_frequency": "weekly"
  }' | jq .

# Cambio password
curl -X POST http://localhost:8000/api/v1/users/me/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPassword2025!",
    "new_password": "NewPassword2025!"
  }' | jq .
```

## ⚙️ **7. ADMIN ENDPOINTS (Solo con token admin)**

```bash
# Lista utenti
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/users/?limit=10" | jq .

# Statistiche utenti
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/v1/users/stats | jq .

# Organizzazioni APS
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/v1/users/aps/organizations | jq .

# Statistiche APS
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/v1/users/aps/stats | jq .

# Utenti con esigenze accessibilità
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/v1/users/accessibility/users | jq .

# Statistiche accessibilità
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/v1/users/accessibility/stats | jq .

# Dettagli utente specifico
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/v1/users/1 | jq .

# Cambia ruolo utente
curl -X POST http://localhost:8000/api/v1/users/2/change-role \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '"aps_operatore"' | jq .

# Cambia status utente
curl -X POST http://localhost:8000/api/v1/users/2/change-status \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '"suspended"' | jq .
```

## ⚡ **8. PERFORMANCE TESTS**

```bash
# Test concorrenza (5 richieste simultanee)
for i in {1..5}; do
  curl -s http://localhost:8000/api/v1/bandi/?limit=1 > /dev/null &
done
wait
echo "✅ Concurrent requests completed"

# Test con dataset grande
time curl -s "http://localhost:8000/api/v1/bandi/?limit=100" | jq '.items | length'

# Test ricerca complessa
time curl -s "http://localhost:8000/api/v1/bandi/?query=inclusione&fonte=regione_campania&limit=50" | jq .
```

## 🚪 **9. LOGOUT**

```bash
# Logout utente
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN" | jq .
```

## 🎯 **10. TEST COMPLETO WORKFLOW**

```bash
#!/bin/bash
# Script completo per testare workflow utente

echo "🚀 Testing complete user workflow..."

# 1. Registrazione
echo "👤 Registering new user..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "workflow_test_'$(date +%s)'@example.com",
    "password": "WorkflowTest2025!",
    "nome": "Test",
    "cognome": "Workflow",
    "role": "cittadino",
    "accessibility_needs": "none",
    "privacy_policy_accepted": true
  }')

echo "$REGISTER_RESPONSE" | jq .

# 2. Login
echo "🔐 Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "workflow_test_'$(date +%s)'@example.com",
    "password": "WorkflowTest2025!"
  }')

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
echo "Token obtained: ${TOKEN:0:20}..."

# 3. Visualizza profilo
echo "👤 Getting profile..."
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/auth/me | jq .

# 4. Cerca bandi
echo "📋 Searching bandi..."
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/bandi/?query=formazione&limit=5" | jq .

# 5. Aggiorna preferenze
echo "⚙️ Updating preferences..."
curl -s -X PUT http://localhost:8000/api/v1/users/me/preferences \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notify_new_bandi": true,
    "alert_frequency": "daily"
  }' | jq .

# 6. Logout
echo "🚪 Logging out..."
curl -s -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN" | jq .

echo "✅ Workflow test completed!"
```

## 📊 **EXPECTED RESULTS**

### **✅ Success Indicators:**
- Health checks return `{"status": "healthy"}`
- Bandi API returns `{"items": [...], "total": N}`
- Registration returns user object with `id`
- Login returns `{"access_token": "...", "user": {...}}`
- Profile endpoints return user data
- Admin endpoints return lists/stats (with admin token)

### **❌ Error Indicators:**
- 500 Internal Server Error
- 401 Unauthorized (without token)
- 403 Forbidden (wrong permissions)
- 404 Not Found (invalid endpoints)
- Validation errors on malformed data

### **⚡ Performance Targets:**
- Health check: <100ms
- Bandi list: <500ms
- Search queries: <1s
- User operations: <300ms
- Admin queries: <1s

---

**🎯 Usa questi comandi per testare manualmente tutti i sistemi ISS con dati reali!**
