#!/bin/bash
# ============================================================================
# STOP SERVIZI PRODUZIONE - markettina
# ============================================================================

set -e

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🛑 STOP SERVIZI PRODUZIONE - markettina${NC}"
echo "============================================"
echo ""

# ============================================================================
# 1. Stop Frontend (porta 3000)
# ============================================================================
echo -e "${YELLOW}[1/4] Stop Frontend...${NC}"

if lsof -ti:3000 > /dev/null 2>&1; then
    echo "🛑 Termino processo su porta 3000..."
    kill -15 $(lsof -ti:3000) 2>/dev/null || true
    sleep 2
    
    # Force kill se ancora attivo
    if lsof -ti:3000 > /dev/null 2>&1; then
        kill -9 $(lsof -ti:3000) 2>/dev/null || true
    fi
    
    echo "✅ Frontend terminato"
else
    echo "ℹ️  Nessun processo su porta 3000"
fi

# ============================================================================
# 2. Stop AI Microservice (porta 8001)
# ============================================================================
echo -e "${YELLOW}[2/4] Stop AI Microservice...${NC}"

if lsof -ti:8001 > /dev/null 2>&1; then
    echo "🛑 Termino processo su porta 8001..."
    kill -15 $(lsof -ti:8001) 2>/dev/null || true
    sleep 2
    
    # Force kill se ancora attivo
    if lsof -ti:8001 > /dev/null 2>&1; then
        kill -9 $(lsof -ti:8001) 2>/dev/null || true
    fi
    
    echo "✅ AI Microservice terminato"
else
    echo "ℹ️  Nessun processo su porta 8001"
fi

# ============================================================================
# 3. Stop Backend (porta 8002)
# ============================================================================
echo -e "${YELLOW}[3/4] Stop Backend...${NC}"

if lsof -ti:8002 > /dev/null 2>&1; then
    echo "🛑 Termino processo su porta 8002..."
    kill -15 $(lsof -ti:8002) 2>/dev/null || true
    sleep 2
    
    # Force kill se ancora attivo
    if lsof -ti:8002 > /dev/null 2>&1; then
        kill -9 $(lsof -ti:8002) 2>/dev/null || true
    fi
    
    echo "✅ Backend terminato"
else
    echo "ℹ️  Nessun processo su porta 8002"
fi

# ============================================================================
# 4. Stop servizi Docker (opzionale)
# ============================================================================
echo -e "${YELLOW}[4/4] Stop servizi Docker...${NC}"

read -p "Vuoi fermare anche PostgreSQL e Redis? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd /home/autcir_gmail_com/markettina_ws/config/docker
    docker compose stop postgres redis
    echo "✅ Servizi Docker fermati"
else
    echo "ℹ️  Servizi Docker lasciati attivi"
fi

# ============================================================================
# RIEPILOGO
# ============================================================================
echo ""
echo -e "${GREEN}✅ SERVIZI FERMATI!${NC}"
echo "==================="
echo ""
echo "📊 Verifica processi rimasti:"
echo "  - ps aux | grep uvicorn"
echo "  - ps aux | grep node"
echo "  - docker compose -f /home/autcir_gmail_com/markettina_ws/config/docker/docker-compose.yml ps"
echo ""
echo "🚀 Riavvia con:"
echo "  - ./scripts/start_production.sh"
echo ""
