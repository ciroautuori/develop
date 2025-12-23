# 🐳 ISS Docker Infrastructure

## Innovazione Sociale Salernitana - Production Ready

Infrastruttura Docker completamente ottimizzata per la piattaforma ISS con configurazioni enterprise-ready per sviluppo e produzione.

## 🚀 Quick Start

### Prerequisiti
- Docker 20.10+
- Docker Compose 2.0+
- Make (opzionale, per comandi semplificati)

### Setup Rapido
```bash
# Clone e setup
git clone <repository-url>
cd iss

# Setup automatico
make setup
# oppure
./scripts/docker-setup.sh

# Avvia servizi
make up
```

## 📋 Servizi Disponibili

| Servizio | Porta | Descrizione |
|----------|-------|-------------|
| **Frontend** | 3001 | React + Vite + Nginx |
| **Backend** | 8001 | FastAPI + Python |
| **PostgreSQL** | 5433 | Database principale |
| **Redis** | 6380 | Cache e sessioni |
| **Redis Commander** | 8082 | Gestione Redis |
| **MailHog** | 8026 | Email testing (dev) |
| **Nginx Proxy** | 80/443 | Reverse proxy (prod) |

## 🛠️ Comandi Make

### Sviluppo
```bash
make help           # Mostra tutti i comandi
make setup          # Setup iniziale
make up             # Avvia servizi
make down           # Ferma servizi
make restart        # Riavvia servizi
make logs           # Mostra logs
make status         # Status servizi
```

### Database
```bash
make db-shell       # Connetti a PostgreSQL
make db-backup      # Backup database
make db-restore FILE=backup.sql  # Ripristina backup
```

### Testing
```bash
make test           # Tutti i test
make test-backend   # Test backend
make test-frontend  # Test frontend
make health         # Health check
```

### Produzione
```bash
make deploy         # Deploy produzione
make backup         # Backup completo
make rollback BACKUP=dir  # Rollback
```

### Manutenzione
```bash
make clean          # Pulizia Docker
make clean-all      # Pulizia completa
make update         # Aggiorna tutto
make monitor        # Monitoraggio risorse
```

## 🔧 Configurazione

### File di Configurazione

```
config/
├── postgres/
│   ├── postgresql.conf    # Ottimizzazioni PostgreSQL
│   └── init.sql          # Script inizializzazione
├── redis/
│   └── redis.conf        # Configurazione Redis
├── nginx/
│   └── nginx.conf        # Reverse proxy
└── backend/
    └── logging.conf      # Logging backend
```

### Variabili Ambiente

Copia `.env.example` in `.env` e personalizza:

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false

# Database
POSTGRES_PASSWORD=your-secure-password

# Sicurezza
SECRET_KEY=your-32-char-secret-key

# Email
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Porte (opzionale)
FRONTEND_PORT=3001
BACKEND_PORT=8001
```

## 🏗️ Architettura

### Multi-Stage Build
- **Frontend**: Node.js build → Nginx production
- **Backend**: Python venv → Slim runtime
- **Ottimizzazioni**: Layer caching, multi-arch support

### Network Architecture
```
Internet → Nginx Proxy → Frontend/Backend
                      ↓
              PostgreSQL + Redis
```

### Volume Management
```
data/
├── postgres/     # Database persistente
├── redis/        # Cache Redis
├── uploads/      # File caricati
├── logs/         # Log applicazioni
└── nginx-logs/   # Log proxy
```

## 🔒 Sicurezza

### Implementate
- ✅ Non-root users nei container
- ✅ Security headers Nginx
- ✅ Rate limiting API
- ✅ Network isolation
- ✅ Secrets management
- ✅ Health checks

### Best Practices
- Passwords sicure in `.env`
- SSL/TLS in produzione
- Backup regolari
- Monitoring attivo
- Log centralizati

## 📊 Monitoring

### Health Checks
```bash
# Controllo automatico
make health

# Controllo manuale
curl http://localhost:8001/health
curl http://localhost:3001/health
```

### Logs
```bash
# Tutti i servizi
make logs

# Servizio specifico
make logs-backend
make logs-frontend
make logs-db

# Ultimi 50 log
make quick-logs
```

### Metriche
```bash
# Risorse in tempo reale
make monitor

# Status servizi
make status
```

## 🚀 Deployment

### Sviluppo
```bash
# Setup development
make dev-setup

# Con hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Produzione
```bash
# Setup produzione
make prod-setup

# Deploy completo
make deploy

# Con proxy Nginx
docker-compose --profile production up -d
```

### CI/CD Pipeline
```yaml
# Esempio GitHub Actions
- name: Deploy ISS
  run: |
    make backup
    make deploy
    make health
```

## 🔄 Backup & Recovery

### Backup Automatico
```bash
# Backup completo
make backup

# Solo database
make db-backup
```

### Recovery
```bash
# Rollback completo
make rollback BACKUP=backups/20240924_143000

# Solo database
make db-restore FILE=backup.sql
```

## 🐛 Troubleshooting

### Problemi Comuni

**Servizi non si avviano**
```bash
# Controlla logs
make logs

# Verifica configurazione
docker-compose config

# Ricostruisci immagini
make build
```

**Database connection error**
```bash
# Verifica PostgreSQL
make db-shell

# Controlla health
docker-compose exec postgres pg_isready -U postgres
```

**Frontend non carica**
```bash
# Verifica build
docker-compose logs frontend

# Ricostruisci frontend
docker-compose build --no-cache frontend
```

### Debug Mode
```bash
# Abilita debug
echo "DEBUG=true" >> .env
make restart

# Accedi ai container
make shell-backend
make shell-frontend
```

## 📈 Performance

### Ottimizzazioni Implementate
- Multi-stage builds per immagini leggere
- Layer caching per build veloci
- Resource limits per stabilità
- Connection pooling database
- Redis caching strategico
- Nginx compression e caching

### Tuning Produzione
```bash
# Aumenta worker backend
WORKERS=8 make up

# Ottimizza PostgreSQL
# Modifica config/postgres/postgresql.conf

# Monitoring risorse
make monitor
```

## 🤝 Contribuire

1. Fork del repository
2. Crea feature branch
3. Test con `make test`
4. Commit e push
5. Crea Pull Request

## 📞 Supporto

- **Issues**: GitHub Issues
- **Docs**: `/docs` directory
- **Email**: tech@iss-aps.it

---

**🏛️ ISS - Innovazione Sociale Salernitana APS-ETS**  
*Piattaforma tecnologica per l'innovazione sociale in Campania*
