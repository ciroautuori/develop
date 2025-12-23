#!/bin/bash
# ============================================================================
# STUDIOCENTOS - INSTALLAZIONE COMPLETA AUTOMATICA
# ============================================================================

set -e

echo "🚀 STUDIOCENTOS - INSTALLAZIONE COMPLETA"
echo "=========================================="
echo ""

# Colori
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ============================================================================
# STEP 1: INSTALLA DIPENDENZE SISTEMA
# ============================================================================
echo -e "${BLUE}STEP 1/7: Installazione dipendenze sistema...${NC}"
echo ""

echo "Installazione: Docker, Docker Compose, Make, PostgreSQL, Redis..."

# Aggiorna repository
sudo apt update

# Installa dipendenze base
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Installa Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Installa altre dipendenze
sudo apt install -y make postgresql postgresql-contrib redis-server

echo -e "${GREEN}✅ Dipendenze sistema installate${NC}"
echo ""

# ============================================================================
# STEP 2: CONFIGURA DOCKER
# ============================================================================
echo -e "${BLUE}STEP 2/7: Configurazione Docker...${NC}"
echo ""

# Avvia Docker daemon
sudo systemctl start docker
sudo systemctl enable docker

# Aggiungi utente al gruppo docker
sudo usermod -aG docker $USER

echo -e "${GREEN}✅ Docker configurato${NC}"
echo -e "${YELLOW}⚠️  IMPORTANTE: Esegui 'newgrp docker' o riavvia la sessione${NC}"
echo ""

# ============================================================================
# STEP 3: INSTALLA UV (Python Package Manager)
# ============================================================================
echo -e "${BLUE}STEP 3/7: Installazione UV...${NC}"
echo ""

curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

echo -e "${GREEN}✅ UV installato${NC}"
echo ""

# ============================================================================
# STEP 4: INSTALLA PNPM (Node Package Manager)
# ============================================================================
echo -e "${BLUE}STEP 4/7: Installazione pnpm...${NC}"
echo ""

# Installa Node.js se non presente
if ! command -v node &> /dev/null; then
    sudo pacman -S --noconfirm nodejs npm
fi

# Installa pnpm
npm install -g pnpm

echo -e "${GREEN}✅ pnpm installato${NC}"
echo ""

# ============================================================================
# STEP 5: SETUP POSTGRESQL
# ============================================================================
echo -e "${BLUE}STEP 5/7: Setup PostgreSQL...${NC}"
echo ""

# Inizializza database
sudo -u postgres initdb -D /var/lib/postgres/data 2>/dev/null || true

# Avvia PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Crea utente e database
sudo -u postgres psql -c "DROP DATABASE IF EXISTS studiocentos;" 2>/dev/null || true
sudo -u postgres psql -c "DROP USER IF EXISTS studiocentos;" 2>/dev/null || true
sudo -u postgres psql << EOF
CREATE USER studiocentos WITH PASSWORD 'studiocentos2025';
CREATE DATABASE studiocentos OWNER studiocentos;
GRANT ALL PRIVILEGES ON DATABASE studiocentos TO studiocentos;
ALTER USER studiocentos CREATEDB;
EOF

echo -e "${GREEN}✅ PostgreSQL configurato${NC}"
echo ""

# ============================================================================
# STEP 6: SETUP REDIS
# ============================================================================
echo -e "${BLUE}STEP 6/7: Setup Redis...${NC}"
echo ""

sudo systemctl start redis
sudo systemctl enable redis

echo -e "${GREEN}✅ Redis configurato${NC}"
echo ""

# ============================================================================
# STEP 7: BUILD DOCKER IMAGES
# ============================================================================
echo -e "${BLUE}STEP 7/7: Build Docker Images...${NC}"
echo ""

cd /home/ciroautuori/studiocentos/config/docker

# Build images
echo "Building backend..."
docker compose -f docker-compose.yml build backend

echo "Building frontend..."
docker compose -f docker-compose.yml build frontend

echo "Building ai_microservice..."
docker compose -f docker-compose.yml build ai_microservice

echo -e "${GREEN}✅ Docker images buildate${NC}"
echo ""

# ============================================================================
# RIEPILOGO
# ============================================================================
echo "=========================================="
echo -e "${GREEN}🎉 INSTALLAZIONE COMPLETATA!${NC}"
echo "=========================================="
echo ""
echo "📦 Installato:"
echo "  ✅ Docker + Docker Compose"
echo "  ✅ Make"
echo "  ✅ PostgreSQL 16"
echo "  ✅ Redis 7"
echo "  ✅ UV (Python package manager)"
echo "  ✅ pnpm (Node package manager)"
echo "  ✅ Docker images (backend, frontend, ai)"
echo ""
echo "🔄 Prossimi step:"
echo ""
echo "  1. Riavvia sessione o esegui: newgrp docker"
echo "  2. Avvia stack: cd config/docker && make up"
echo "  3. Migration: make shell-backend"
echo "     Dentro container: alembic upgrade head"
echo "  4. Seed: python scripts/seed_portfolio.py"
echo "  5. Test: python scripts/test_data_flow.py"
echo ""
echo "📚 Oppure usa lo script automatico:"
echo "  ./QUICK_START_DOCKER.sh"
echo ""
echo "🌐 Servizi disponibili dopo 'make up':"
echo "  - Frontend:     http://localhost:3000"
echo "  - Backend API:  http://localhost:8000"
echo "  - AI Service:   http://localhost:8001"
echo "  - API Docs:     http://localhost:8000/docs"
echo ""
