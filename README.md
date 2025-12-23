# 🌟 **ISS - Innovazione Sociale Salernitana APS-ETS**

> **🎯 Trasformare Salerno nel hub regionale per l'accesso democratico ai bandi di finanziamento per il terzo settore**

[![Tests](https://img.shields.io/badge/tests-61%2F61%20passing-brightgreen.svg)](https://github.com/iss-salerno/iss)
[![API Status](https://img.shields.io/badge/API-fully%20operational-blue.svg)](https://api.iss-salerno.it/docs)
[![Database](https://img.shields.io/badge/database-PostgreSQL%20100%25%20connected-success.svg)](https://github.com/iss-salerno/iss)

---

## 🚀 **VISION & MISSION**

**ISS** è una piattaforma digitale rivoluzionaria che **democratizza l'accesso ai bandi di finanziamento** per centinaia di APS (Associazioni di Promozione Sociale) e organizzazioni del terzo settore della Campania.

### **💡 KILLER FEATURE: Sistema Bandi Automatizzato**
- **🤖 Monitoraggio 24/7** di fonti ufficiali (Comune, Regione, CSV, Fondazioni)
- **🔍 Ricerca intelligente** con filtri avanzati e keywords
- **📱 Notifiche real-time** via email e Telegram
- **📊 Analytics avanzati** su trends e opportunità
- **🎯 Personalizzazione** per ogni tipologia di organizzazione

### **📈 IMPATTO ATTESO**
- **500+ APS** potenzialmente servite nella provincia
- **Aumento del 300%** nell'accesso ai finanziamenti
- **Riduzione del 80%** del tempo di ricerca bandi
- **Democratizzazione** dell'accesso alle opportunità

---

## 🎯 Caratteristiche Principali

### 🌐 Backend API Completo
- **FastAPI** con SQLAlchemy + PostgreSQL
- **Autenticazione JWT** per admin
- **Rate limiting** con Redis
- **Sistema CRUD** completo per progetti, eventi, news, volontari
- **Stripe integration** per donazioni
- **Prometheus metrics** e monitoring

### 🤖 Sistema Bandi Automatico ⭐
- **Monitoraggio 24/7** di siti istituzionali
- **Scraping intelligente** multi-fonte (Comune Salerno, Regione Campania, CSV, etc.)
- **Filtraggio per keywords** (alfabetizzazione digitale, inclusione sociale)
- **Notifiche email/Telegram** automatiche
- **API pubblica** per integrazione frontend
- **Dashboard admin** per configurazione completa
- **Scheduling configurabile** con APScheduler

## 🏗️ Architettura

```
iss/
├── apps/
│   └── backend/           # FastAPI Backend + Sistema Bandi
│       ├── app/
│       │   ├── api/       # Endpoints REST
│       │   ├── models/    # Database models (inclusi bandi)
│       │   ├── services/  # Bandi monitoring + Scheduler
│       │   ├── crud/      # Database operations
│       │   └── schemas/   # Pydantic schemas
│       ├── docs/          # Documentazione
│       └── scripts/       # Utility e setup
├── iss-bot/              # Bot originale (ora integrato)
├── logo/                 # Assets grafici
└── scripts/              # Script Docker e test
```

## 🚀 Quick Start

### 1. Clona e Avvia
```bash
git clone <repository>
cd iss

# Avvia tutto con Docker
chmod +x scripts/start.sh
./scripts/start.sh
```

### 2. Test del Sistema
```bash
chmod +x scripts/test_bandi_system.sh
./scripts/test_bandi_system.sh
```

## 📊 Servizi Disponibili

| Servizio | URL | Descrizione |
|----------|-----|-------------|
| 🌐 **Backend API** | http://localhost:8000 | API principale |
| 📖 **Swagger Docs** | http://localhost:8000/docs | Documentazione interattiva |
| ❤️ **Health Check** | http://localhost:8000/health | Status sistema |
| 🗄️ **PgAdmin** | http://localhost:5050 | Gestione database |
| 🔴 **Redis Commander** | http://localhost:8081 | Gestione Redis |
| 📧 **MailHog** | http://localhost:8025 | Test email (dev) |

## 🎯 API Endpoints Principali

### Bandi System (Pubblico)
```bash
GET  /api/v1/bandi/                    # Lista bandi con filtri
GET  /api/v1/bandi/stats               # Statistiche dashboard
GET  /api/v1/bandi/recent              # Bandi più recenti
GET  /api/v1/bandi/{id}                # Dettaglio bando
```

### Gestione Bandi (Admin)
```bash
GET  /api/v1/admin/bandi-config/       # Configurazioni monitoraggio
POST /api/v1/admin/bandi-config/       # Crea configurazione  
PUT  /api/v1/admin/bandi-config/{id}   # Aggiorna configurazione
POST /api/v1/admin/bandi-config/{id}/run # Trigger manuale
GET  /api/v1/admin/bandi-config/status   # Stato sistema
```

### CMS (Admin)
```bash
GET /api/v1/projects/                  # Progetti ISS
GET /api/v1/events/                    # Eventi
GET /api/v1/news/                      # News  
GET /api/v1/volunteer-applications/    # Candidature volontari
```

## ⚙️ Configurazione Sistema Bandi

### 1. Accesso Admin
```bash
# Crea utente admin (one-time)
docker-compose exec backend python -c "
from app.crud.admin import create_admin_user
admin = create_admin_user('admin@iss.it', 'password123')
print(f'Admin created: {admin.email}')
"

# Login per ottenere token
curl -X POST "http://localhost:8000/api/v1/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@iss.it", "password": "password123"}'
```

### 2. Configurazione Email
```bash
# Aggiorna configurazione di default
curl -X PUT "http://localhost:8000/api/v1/admin/bandi-config/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email_username": "tua-email@gmail.com",
    "email_password": "tua-app-password",
    "email_recipient": "notifiche@iss.it"
  }'
```

### 3. Test Monitoraggio
```bash
# Trigger manuale per test
curl -X POST "http://localhost:8000/api/v1/admin/bandi-config/1/run" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 Sviluppo

### Struttura Database
- **bandi**: Bandi trovati dal monitoraggio
- **bando_configs**: Configurazioni di monitoraggio  
- **bando_logs**: Log delle esecuzioni
- **projects**, **events**, **news**: Contenuti CMS
- **admin_users**: Utenti amministratori

### Servizi Principali
- **BandoMonitorService**: Scraping automatico
- **SchedulerService**: Gestione job programmati
- **Rate limiting**: Protezione API
- **Caching**: Performance con Redis

### Comandi Utili
```bash
# Logs
docker-compose logs backend
docker-compose logs postgres

# Shell nel container
docker-compose exec backend bash

# Migrazioni database
docker-compose exec backend alembic upgrade head

# Stop sistema
docker-compose down
```

## 📚 Documentazione

### **👥 Per Team Frontend**
- 📖 **[Guida Completa Frontend](docs/FRONTEND_GUIDE.md)** - Vision, strategia, UX/UI guidelines
- 🔌 **[API Reference](docs/API_REFERENCE.md)** - Endpoints completi, esempi, testing
- 🎨 **Design System** - Componenti, palette colori, responsive design

### **🔧 Per Sviluppatori Backend**
- 📖 **[Sistema Bandi - Guida Completa](./apps/backend/docs/BANDI_SYSTEM.md)**
- 🔧 **[Setup Bandi](./apps/backend/scripts/setup_bando_system.py)**
- 📊 **[API Docs Interactive](http://localhost:8000/docs)** (dopo l'avvio)
- 🧪 **Testing**: 61/61 test al 100% ✅

## 🛡️ Sicurezza

- **JWT Authentication** per endpoints admin
- **Rate limiting** su tutte le API
- **Input validation** con Pydantic
- **CORS** configurato per frontend
- **Password hashing** con bcrypt
- **SQL injection protection**

## 📞 Supporto

Per problemi tecnici:
1. Controlla i log: `docker-compose logs backend`
2. Verifica health: http://localhost:8000/health  
3. Test sistema: `./scripts/test_bandi_system.sh`
4. Documentazione: `./apps/backend/docs/BANDI_SYSTEM.md`

---

## 🌟 **IMPATTO SOCIALE**

> **💡 Ogni bando trovato facilmente attraverso ISS significa un progetto sociale finanziato, una comunità aiutata, un futuro migliore per il territorio campano.**

**ISS non è solo una piattaforma tecnologica, ma uno strumento di democrazia digitale che permette a tutte le APS, grandi e piccole, di accedere equamente alle opportunità di finanziamento.**

### **🎯 PRIORITÀ PER IL TEAM FRONTEND**

Il sistema bandi è il **core business** della piattaforma. L'implementazione frontend deve essere:
- **User-centric**: Ogni APS deve trovare facilmente i bandi pertinenti
- **Performante**: Ricerche rapide e risultati immediati  
- **Accessibile**: Design inclusivo per tutte le età e competenze digitali
- **Mobile-first**: Molte APS operano principalmente da mobile

---

**🚀 Rendiamo Salerno la capitale dell'innovazione sociale digitale!**

[![Follow](https://img.shields.io/badge/Follow-@ISSSalerno-blue.svg)](https://twitter.com/ISSSalerno)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-ISS%20Salerno-blue.svg)](https://linkedin.com/company/iss-salerno)
