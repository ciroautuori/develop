#!/bin/bash
# ============================================================================
# STUDIOCENTOS - Quick Start con Docker
# ============================================================================

set -e  # Exit on error

echo "🐳 STUDIOCENTOS - Setup Completo con Docker"
echo "=============================================="
echo ""

# Colori
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Verifica Docker
echo -e "${BLUE}Step 1/6: Verifica Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker non installato!${NC}"
    echo "Installa Docker: sudo pacman -S docker docker-compose"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon non avviato!${NC}"
    echo "Avvia Docker: sudo systemctl start docker"
    exit 1
fi

echo -e "${GREEN}✅ Docker OK${NC}"
echo ""

# Step 2: Setup Environment Variables
echo -e "${BLUE}Step 2/6: Setup Environment Variables...${NC}"
cd /home/ciroautuori/studiocentos/config/docker

if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  File .env non trovato, uso quello esistente${NC}"
fi

echo -e "${GREEN}✅ Environment OK${NC}"
echo ""

# Step 3: Build Docker Images
echo -e "${BLUE}Step 3/6: Build Docker Images...${NC}"
echo "Questo può richiedere 5-10 minuti..."
make build

echo -e "${GREEN}✅ Build completato${NC}"
echo ""

# Step 4: Avvia Stack Completo
echo -e "${BLUE}Step 4/6: Avvia Stack Completo...${NC}"
make up

echo -e "${GREEN}✅ Stack avviato${NC}"
echo ""

# Step 5: Attendi che i servizi siano pronti
echo -e "${BLUE}Step 5/6: Attendi servizi pronti...${NC}"
echo "Attendo 30 secondi per l'avvio completo..."
sleep 30

# Step 6: Esegui Migration e Seed
echo -e "${BLUE}Step 6/6: Migration e Seed Database...${NC}"

# Migration
echo "Eseguo migration..."
docker compose -f docker-compose.yml exec -T backend alembic upgrade head

# Seed
echo "Eseguo seed..."
docker compose -f docker-compose.yml exec -T backend python scripts/seed_portfolio.py

echo -e "${GREEN}✅ Migration e Seed completati${NC}"
echo ""

# Test Data Flow
echo -e "${BLUE}Test Data Flow...${NC}"
docker compose -f docker-compose.yml exec -T backend python scripts/test_data_flow.py

echo ""
echo "=============================================="
echo -e "${GREEN}🎉 SETUP COMPLETATO!${NC}"
echo "=============================================="
echo ""
echo "📊 Servizi disponibili:"
echo ""
echo "  🌐 Frontend:        http://localhost:3000"
echo "  🔧 Backend API:     http://localhost:8000"
echo "  📚 API Docs:        http://localhost:8000/docs"
echo "  🤖 AI Service:      http://localhost:8001"
echo "  🗄️  PostgreSQL:      localhost:5432"
echo "  💾 Redis:           localhost:6379"
echo "  🔀 Traefik:         http://localhost:8080"
echo ""
echo "🛠️  Comandi utili:"
echo ""
echo "  make logs          # Visualizza logs"
echo "  make ps            # Status containers"
echo "  make health        # Health check"
echo "  make down          # Stop tutto"
echo "  make restart       # Restart tutto"
echo ""
echo "📖 Documentazione completa:"
echo "  cat SETUP_AND_DEPLOYMENT_GUIDE.md"
echo ""
