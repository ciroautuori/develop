#!/bin/bash
# ============================================================================
# AVVIO SERVIZI PRODUZIONE - markettina
# ============================================================================
# Avvia tutti i servizi in produzione:
# - PostgreSQL + Redis (Docker)
# - Backend FastAPI (porta 8002)
# - AI Microservice (porta 8001)
# - Frontend React (porta 3000)
# ============================================================================

set -e

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🚀 AVVIO SERVIZI PRODUZIONE - markettina${NC}"
echo "=============================================="
echo ""

# Directory di lavoro
WORKSPACE_DIR="/home/autcir_gmail_com/markettina_ws"
cd "$WORKSPACE_DIR"

# ============================================================================
# 1. Verifica file .env.production
# ============================================================================
echo -e "${YELLOW}[1/6] Verifica configurazione...${NC}"

if [ ! -f ".env.production" ]; then
    echo -e "${RED}❌ File .env.production non trovato!${NC}"
    echo "Crea il file .env.production partendo da .env.production.example"
    echo "Comando: cp .env.production.example .env.production"
    echo "Poi modifica i valori con le credenziali reali"
    exit 1
fi

echo "✅ File .env.production trovato"

# Carica variabili ambiente
set -a
source .env.production
set +a

# ============================================================================
# 2. Avvio servizi Docker (PostgreSQL + Redis)
# ============================================================================
echo -e "${YELLOW}[2/6] Avvio servizi Docker...${NC}"

cd config/docker

# Verifica se Docker è attivo
if ! systemctl is-active --quiet docker; then
    echo "🐳 Avvio Docker..."
    sudo systemctl start docker
fi

# Avvia PostgreSQL e Redis
docker compose up -d postgres redis

# Attendi che i servizi siano pronti
echo "⏳ Attesa avvio PostgreSQL..."
timeout 30 bash -c 'until docker compose exec -T postgres pg_isready -U markettina > /dev/null 2>&1; do sleep 1; done' || {
    echo -e "${RED}❌ PostgreSQL non si è avviato in tempo${NC}"
    exit 1
}

echo "⏳ Attesa avvio Redis..."
timeout 30 bash -c 'until docker compose exec -T redis redis-cli -a $REDIS_PASSWORD ping > /dev/null 2>&1; do sleep 1; done' || {
    echo -e "${RED}❌ Redis non si è avviato in tempo${NC}"
    exit 1
}

echo "✅ Servizi Docker avviati (PostgreSQL, Redis)"

cd "$WORKSPACE_DIR"

# ============================================================================
# 3. Esegui migrations database
# ============================================================================
echo -e "${YELLOW}[3/6] Esecuzione migrations database...${NC}"

cd apps/backend

# Verifica se alembic è configurato
if [ -f "alembic.ini" ]; then
    echo "📊 Esecuzione migrations Alembic..."
    uv run alembic upgrade head
    echo "✅ Migrations completate"
else
    echo "⚠️  Alembic non configurato, skip migrations"
fi

cd "$WORKSPACE_DIR"

# ============================================================================
# 4. Avvio Backend (FastAPI - porta 8002)
# ============================================================================
echo -e "${YELLOW}[4/6] Avvio Backend FastAPI...${NC}"

cd apps/backend

# Kill processo esistente se presente
if lsof -ti:8002 > /dev/null 2>&1; then
    echo "⚠️  Processo già in ascolto su porta 8002, termino..."
    kill -9 $(lsof -ti:8002) 2>/dev/null || true
    sleep 2
fi

# Avvia backend in background
echo "🚀 Avvio backend su porta 8002..."
nohup uv run uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8002 \
    --workers 4 \
    --log-level info \
    > /var/log/markettina-backend.log 2>&1 &

BACKEND_PID=$!
echo "✅ Backend avviato (PID: $BACKEND_PID)"

cd "$WORKSPACE_DIR"

# ============================================================================
# 5. Avvio AI Microservice (porta 8001)
# ============================================================================
echo -e "${YELLOW}[5/6] Avvio AI Microservice...${NC}"

cd apps/ai_microservice

# Kill processo esistente se presente
if lsof -ti:8001 > /dev/null 2>&1; then
    echo "⚠️  Processo già in ascolto su porta 8001, termino..."
    kill -9 $(lsof -ti:8001) 2>/dev/null || true
    sleep 2
fi

# Avvia AI service in background
echo "🚀 Avvio AI service su porta 8001..."
nohup uv run uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8001 \
    --workers 2 \
    --log-level info \
    > /var/log/markettina-ai.log 2>&1 &

AI_PID=$!
echo "✅ AI Microservice avviato (PID: $AI_PID)"

cd "$WORKSPACE_DIR"

# ============================================================================
# 6. Avvio Frontend (React - porta 3000)
# ============================================================================
echo -e "${YELLOW}[6/6] Avvio Frontend React...${NC}"

cd apps/frontend

# Kill processo esistente se presente
if lsof -ti:3000 > /dev/null 2>&1; then
    echo "⚠️  Processo già in ascolto su porta 3000, termino..."
    kill -9 $(lsof -ti:3000) 2>/dev/null || true
    sleep 2
fi

# Build frontend per produzione
echo "📦 Build frontend produzione..."
pnpm build

# Avvia frontend con preview (o usa nginx per servire dist/)
echo "🚀 Avvio frontend su porta 3000..."
nohup pnpm preview --host 0.0.0.0 --port 3000 \
    > /var/log/markettina-frontend.log 2>&1 &

FRONTEND_PID=$!
echo "✅ Frontend avviato (PID: $FRONTEND_PID)"

cd "$WORKSPACE_DIR"

# ============================================================================
# Attesa avvio servizi
# ============================================================================
echo ""
echo "⏳ Attesa avvio servizi (5 secondi)..."
sleep 5

# ============================================================================
# Verifica health check
# ============================================================================
echo ""
echo -e "${YELLOW}🔍 Verifica health check...${NC}"

# Backend
if curl -sf http://localhost:8002/health > /dev/null 2>&1; then
    echo -e "✅ Backend: ${GREEN}OK${NC} (http://localhost:8002)"
else
    echo -e "❌ Backend: ${RED}FAIL${NC} (http://localhost:8002)"
fi

# AI Service
if curl -sf http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "✅ AI Service: ${GREEN}OK${NC} (http://localhost:8001)"
else
    echo -e "❌ AI Service: ${RED}FAIL${NC} (http://localhost:8001)"
fi

# Frontend
if curl -sf http://localhost:3000 > /dev/null 2>&1; then
    echo -e "✅ Frontend: ${GREEN}OK${NC} (http://localhost:3000)"
else
    echo -e "❌ Frontend: ${RED}FAIL${NC} (http://localhost:3000)"
fi

# ============================================================================
# RIEPILOGO
# ============================================================================
echo ""
echo -e "${GREEN}✅ TUTTI I SERVIZI AVVIATI!${NC}"
echo "============================"
echo ""
echo "📊 Servizi attivi:"
echo "  - PostgreSQL: localhost:5433 (Docker)"
echo "  - Redis: localhost:6380 (Docker)"
echo "  - Backend API: localhost:8002 (PID: $BACKEND_PID)"
echo "  - AI Service: localhost:8001 (PID: $AI_PID)"
echo "  - Frontend: localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo "🌐 Accesso pubblico (via Nginx):"
echo -e "  - ${BLUE}https://markettina.it${NC}"
echo -e "  - ${BLUE}https://markettina.it/api${NC} (Backend)"
echo -e "  - ${BLUE}https://markettina.it/ai${NC} (AI Service)"
echo ""
echo "📝 Logs:"
echo "  - Backend: tail -f /var/log/markettina-backend.log"
echo "  - AI Service: tail -f /var/log/markettina-ai.log"
echo "  - Frontend: tail -f /var/log/markettina-frontend.log"
echo "  - Nginx: sudo tail -f /var/log/nginx/markettina-access.log"
echo ""
echo "🛑 Stop servizi:"
echo "  - ./scripts/stop_production.sh"
echo ""
echo "📊 Monitora processi:"
echo "  - ps aux | grep uvicorn"
echo "  - ps aux | grep node"
echo "  - docker compose -f config/docker/docker-compose.yml ps"
echo ""
