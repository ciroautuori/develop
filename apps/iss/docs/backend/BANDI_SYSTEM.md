# 🎯 Sistema Bandi ISS - Integrazione Backend

Il sistema di monitoraggio bandi è stato completamente integrato nel backend FastAPI dell'ISS. Questo documento descrive l'architettura, l'utilizzo e la configurazione del sistema.

## 🏗️ Architettura del Sistema

### Database Models

#### `Bando` - Tabella principale dei bandi
```python
- id: ID univoco
- title: Titolo del bando
- ente: Ente/organizzazione
- scadenza: Data di scadenza parsed
- scadenza_raw: Testo originale scadenza  
- link: URL del bando
- descrizione: Descrizione completa
- fonte: Enum fonte (comune_salerno, regione_campania, etc.)
- status: Enum status (attivo, scaduto, archiviato)
- hash_identifier: MD5 hash per deduplicazione
- keyword_match: Parole chiave che hanno fatto match
- notificato_email/telegram: Flag notifiche
```

#### `BandoConfig` - Configurazioni di monitoraggio
```python
- name: Nome configurazione
- email_*: Configurazioni email SMTP
- telegram_*: Configurazioni bot Telegram
- keywords: Array JSON parole chiave
- schedule_*: Impostazioni scheduling
- fonte_enabled: JSON fonti da monitorare
```

#### `BandoLog` - Log delle esecuzioni
```python
- config_id: FK a BandoConfig
- started_at/completed_at: Timestamps
- bandi_found/bandi_new: Statistiche
- status: running/completed/failed
- sources_processed: JSON risultati per fonte
```

## 🔌 API Endpoints

### Endpoints Pubblici (`/api/v1/bandi/`)

#### `GET /api/v1/bandi/`
Lista paginata di bandi con filtri
```bash
curl "http://localhost:8000/api/v1/bandi/?query=digitale&fonte=comune_salerno&limit=10"
```

#### `GET /api/v1/bandi/stats`
Statistiche sui bandi
```json
{
  "total_bandi": 150,
  "bandi_attivi": 45,
  "bandi_scaduti": 105,
  "bandi_per_fonte": {...},
  "ultimi_trovati": 12,
  "media_giornaliera": 2.3
}
```

#### `GET /api/v1/bandi/recent`
Bandi più recenti
```bash
curl "http://localhost:8000/api/v1/bandi/recent?limit=5"
```

### Endpoints Admin (`/api/v1/admin/bandi-config/`)

#### `GET /api/v1/admin/bandi-config/`
Lista configurazioni (richiede autenticazione admin)

#### `POST /api/v1/admin/bandi-config/`
Crea nuova configurazione
```json
{
  "name": "Config Speciale",
  "email_enabled": true,
  "email_username": "admin@iss.it",
  "email_recipient": "notifiche@iss.it",
  "keywords": ["digitale", "inclusione"],
  "schedule_interval_hours": 12,
  "fonte_enabled": {
    "comune_salerno": true,
    "regione_campania": true
  }
}
```

#### `POST /api/v1/admin/bandi-config/{id}/run`
Trigger manuale monitoraggio
```bash
curl -X POST "http://localhost:8000/api/v1/admin/bandi-config/1/run" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### `GET /api/v1/admin/bandi-config/status`
Stato generale del sistema
```json
{
  "is_running": false,
  "active_configs": 2,
  "last_successful_run": "2025-09-23T10:30:00Z",
  "total_bandi_found": 150,
  "errors_last_24h": 0
}
```

## 🚀 Setup e Installazione

### 1. Installazione Dipendenze
```bash
cd /home/ciroautuori/Scrivania/iss/backend
pip install -r requirements.txt
```

### 2. Migrazioni Database
```bash
alembic upgrade head
```
Questo esegue la migrazione `003_add_bando_monitoring_system.py` che crea tutte le tabelle necessarie.

### 3. Setup Automatico
```bash
python scripts/setup_bando_system.py
```
Questo script:
- Verifica la connessione database
- Crea una configurazione di default "ISS Default"
- Valida le dipendenze
- Mostra le istruzioni di configurazione

### 4. Configurazione Email
Aggiorna la configurazione creata:
```bash
curl -X PUT "http://localhost:8000/api/v1/admin/bandi-config/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "email_username": "tua-email@gmail.com",
    "email_password": "tua-app-password",
    "email_recipient": "destinatario@iss.it"
  }'
```

## ⚙️ Scheduling Automatico

Il sistema utilizza **APScheduler** per il monitoraggio automatico:

### Scheduler Jobs
- **bandi_monitor_check**: Controlla ogni 5 minuti le configurazioni da eseguire
- **bandi_cleanup**: Pulizia automatica giornaliera alle 02:00

### Configurazione Schedule
Ogni `BandoConfig` ha:
- `schedule_enabled`: Abilita/disabilita scheduling
- `schedule_interval_hours`: Intervallo in ore (default: 24)
- `next_run`: Prossima esecuzione calcolata automaticamente

## 🔧 Servizi Principali

### BandoMonitorService
```python
from app.services.bando_monitor import bando_monitor_service

async with bando_monitor_service as monitor:
    result = await monitor.run_monitoring(db, config)
```

Funzionalità:
- Scraping asincrono multi-fonte
- Parsing intelligente delle date
- Deduplicazione automatica con hash MD5
- Gestione errori e retry
- Logging strutturato

### SchedulerService
```python
from app.services.scheduler import scheduler_service

# Avvio automatico in main.py
await scheduler_service.start()
```

## 📊 Monitoring e Logs

### Logs Strutturati
Ogni esecuzione genera log dettagliati:
```json
{
  "config_id": 1,
  "started_at": "2025-09-23T09:00:00Z",
  "completed_at": "2025-09-23T09:05:00Z", 
  "bandi_found": 8,
  "bandi_new": 3,
  "errors_count": 0,
  "status": "completed",
  "sources_processed": {
    "comune_salerno": {"found": 5, "status": "success"},
    "regione_campania": {"found": 3, "status": "success"}
  }
}
```

### Metriche Prometheus
Il sistema espone metriche su `/metrics`:
- Numero bandi trovati
- Tempo di esecuzione scraping
- Errori per fonte
- Configurazioni attive

## 🛡️ Security e Performance

### Sicurezza
- **Rate limiting** su tutti gli endpoint
- **Autenticazione JWT** per endpoints admin
- **Input validation** con Pydantic
- **SQL injection protection** con SQLAlchemy
- **Password encryption** (TODO in produzione)

### Performance
- **Caching Redis** per endpoints pubblici (TTL 5-10 min)
- **Connection pooling** PostgreSQL
- **Async/await** per scraping parallelo
- **Background tasks** per operazioni lunghe
- **Database indexes** su campi critici

## 🔄 Integrazione Frontend/Backoffice

### Endpoints per Frontend Pubblico
```javascript
// Lista bandi pubblici
fetch('/api/v1/bandi/?query=digitale')

// Statistiche per dashboard
fetch('/api/v1/bandi/stats')

// Bandi recenti per homepage
fetch('/api/v1/bandi/recent?limit=5')
```

### Endpoints per Backoffice Admin
```javascript
// Dashboard amministrativo
fetch('/api/v1/admin/bandi-config/status', {
  headers: { 'Authorization': 'Bearer ' + token }
})

// Gestione configurazioni
fetch('/api/v1/admin/bandi-config/', {
  method: 'POST',
  headers: { 
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(newConfig)
})

// Trigger manuale
fetch('/api/v1/admin/bandi-config/1/run', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer ' + token }
})
```

## 🎯 Prossimi Sviluppi

1. **Crittografia password** in produzione
2. **Notifiche push** per frontend
3. **Machine learning** per classificazione automatica bandi
4. **Export avanzato** (PDF, Excel)
5. **API webhooks** per integrazioni esterne
6. **Dashboard analytics** avanzata

---

## 📞 Troubleshooting

### Problemi Comuni

**Scheduler non si avvia**
```bash
# Verifica Redis
redis-cli ping

# Controlla logs
tail -f logs/app.log | grep scheduler
```

**Database connection error**
```bash
# Verifica PostgreSQL
pg_isready -h localhost -p 5432

# Test connessione
python -c "from app.database.database import async_session_maker; import asyncio; asyncio.run(async_session_maker().__anext__())"
```

**Scraping fallisce**
```bash
# Test manuale
python -c "
import asyncio
from app.services.bando_monitor import bando_monitor_service
async def test():
    async with bando_monitor_service as m:
        print('Service OK')
asyncio.run(test())
"
```

---

*Sistema sviluppato per Innovazione Sociale Salernitana (ISS) - Settembre 2025*
