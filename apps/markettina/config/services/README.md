# 🔧 SERVICES - Infrastructure Services Hub

**Hub centrale per i servizi infrastrutturali Docker**

## 📁 Struttura

```
config/services/
├── postgres/          # Database PostgreSQL
│   ├── service.yml   # Service definition
│   └── init.sql      # Init script
├── redis/            # Cache & Sessions
│   ├── service.yml
│   └── redis.conf
├── traefik/          # Reverse Proxy
│   ├── service.yml
│   ├── traefik.yml
│   └── dynamic.yml
├── prometheus/       # Metrics
│   ├── service.yml
│   ├── prometheus.yml
│   └── alerts.yml
├── grafana/          # Dashboards
│   ├── service.yml
│   └── datasources.yml
└── nginx/            # Web Server (se necessario)
    ├── service.yml
    └── nginx.conf
```

## 🎯 Filosofia

**SOLO servizi infrastrutturali qui!**

✅ **Vanno qui**:
- PostgreSQL
- Redis
- Traefik
- Prometheus
- Grafana
- Nginx
- Exporters (node, postgres, redis)

❌ **NON vanno qui** (restano in docker-compose.yml):
- Backend (FastAPI)
- Frontend (React)
- AI Microservice
- Applicazioni custom

## 🚀 Utilizzo

### Import nei docker-compose

```yaml
# docker-compose.yml
services:
  # Import servizi infrastrutturali
  postgres:
    extends:
      file: ../services/postgres/service.yml
      service: postgres
  
  redis:
    extends:
      file: ../services/redis/service.yml
      service: redis
  
  # ... servizi applicativi qui
  backend:
    build: ...
    # ...
```

### Start singolo servizio

```bash
# Solo PostgreSQL
docker compose -f config/services/postgres/service.yml up -d

# Solo Redis
docker compose -f config/services/redis/service.yml up -d
```

## 📊 Servizi Disponibili

### 1. PostgreSQL
- **Porta**: 5432
- **User**: markettina
- **DB**: markettina
- **Features**: Extensions, schemas, audit

### 2. Redis
- **Porta**: 6379
- **Password**: Da .env
- **Features**: Persistence, LRU, AOF

### 3. Traefik
- **Porta**: 80, 443, 8080
- **Dashboard**: http://traefik.localhost:8080
- **Features**: SSL, Load balancing, Metrics

### 4. Prometheus
- **Porta**: 9090
- **URL**: http://prometheus.localhost
- **Targets**: Backend, AI, Traefik, DBs

### 5. Grafana
- **Porta**: 3001
- **URL**: http://grafana.localhost
- **User**: admin / admin

## 🔐 Configurazione

Tutte le password e secrets vanno in:
```
config/docker/.env
```

## 📝 Best Practices

1. **Un servizio = Una cartella**
2. **service.yml** = Definizione Docker Compose
3. **Config files** = Configurazioni specifiche
4. **NO duplicazione** con docker-compose.yml
5. **Extends** per riutilizzo

## 🎨 Aggiungere Nuovo Servizio

```bash
# 1. Crea cartella
mkdir -p config/services/myservice

# 2. Crea service.yml
cat > config/services/myservice/service.yml << 'EOF'
myservice:
  image: myservice:latest
  container_name: markettina-myservice
  # ...
EOF

# 3. Import in docker-compose.yml
# services:
#   myservice:
#     extends:
#       file: ../services/myservice/service.yml
#       service: myservice
```

---

**Made with ❤️ by markettina Team**
