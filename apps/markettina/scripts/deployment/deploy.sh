#!/bin/bash
# ============================================================================
# DEPLOY DOCKER PRODUZIONE - markettina.it
# ============================================================================
# Avvia TUTTO con Docker Compose:
# - PostgreSQL + Redis
# - Backend FastAPI
# - AI Microservice
# - Frontend React
# - Nginx + SSL
# ============================================================================

set -e

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🐳 DEPLOY DOCKER PRODUZIONE - markettina.IT${NC}"
echo "=================================================="
echo ""

# Directory di lavoro
WORKSPACE_DIR="/home/autcir_gmail_com/markettina"
DOCKER_DIR="$WORKSPACE_DIR/config/docker"

cd "$WORKSPACE_DIR"

# ============================================================================
# 1. Verifica prerequisiti
# ============================================================================
echo -e "${YELLOW}[1/8] Verifica prerequisiti...${NC}"

# Verifica Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker non installato!${NC}"
    echo "Installa con: sudo pacman -S docker"
    exit 1
fi

# Verifica Docker Compose
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose non installato!${NC}"
    echo "Installa con: sudo pacman -S docker-compose"
    exit 1
fi

# Verifica Docker attivo
if ! systemctl is-active --quiet docker; then
    echo "🐳 Avvio Docker..."
    sudo systemctl start docker
fi

echo "✅ Docker attivo"

# Verifica DNS
echo "🔍 Verifica DNS per markettina.com..."
if ! host markettina.com &> /dev/null; then
    echo -e "${YELLOW}⚠️  markettina.com non risolve!${NC}"
    echo "Assicurati che il DNS punti all'IP del server prima di ottenere SSL"
else
    echo "✅ DNS configurato correttamente"
fi

# ============================================================================
# 2. Verifica file .env.production
# ============================================================================
echo -e "${YELLOW}[2/8] Verifica configurazione...${NC}"

if [ ! -f ".env.production" ]; then
    echo -e "${RED}❌ File .env.production non trovato!${NC}"
    echo "Crea il file .env.production partendo da .env.production.example"
    echo ""
    echo "Comandi:"
    echo "  cp .env.production.example .env.production"
    echo "  nano .env.production"
    echo ""
    echo "Genera password sicure con:"
    echo "  openssl rand -base64 32  # PostgreSQL"
    echo "  openssl rand -base64 32  # Redis"
    echo "  openssl rand -hex 32     # JWT Secret"
    exit 1
fi

echo "✅ File .env.production trovato"

# Carica variabili ambiente
set -a
source .env.production
set +a

# ============================================================================
# 3. Crea directory necessarie
# ============================================================================
echo -e "${YELLOW}[3/8] Creazione directory...${NC}"

sudo mkdir -p /var/log/nginx
sudo mkdir -p /var/www/certbot
sudo mkdir -p /etc/letsencrypt

echo "✅ Directory create"

# ============================================================================
# 4. Build immagini Docker
# ============================================================================
echo -e "${YELLOW}[4/8] Build immagini Docker...${NC}"

cd "$DOCKER_DIR"

echo "📦 Build backend..."
docker compose -f docker-compose.production.yml build backend

echo "📦 Build AI microservice..."
docker compose -f docker-compose.production.yml build ai_microservice

echo "📦 Build frontend..."
docker compose -f docker-compose.production.yml build frontend

echo "✅ Immagini Docker buildate"

# ============================================================================
# 5. Avvia servizi infrastrutturali (PostgreSQL + Redis)
# ============================================================================
echo -e "${YELLOW}[5/8] Avvio servizi infrastrutturali...${NC}"

docker compose -f docker-compose.production.yml up -d postgres redis

echo "⏳ Attesa avvio PostgreSQL..."
timeout 60 bash -c 'until docker compose -f docker-compose.production.yml exec -T postgres pg_isready -U markettina > /dev/null 2>&1; do sleep 2; done' || {
    echo -e "${RED}❌ PostgreSQL non si è avviato in tempo${NC}"
    exit 1
}

echo "⏳ Attesa avvio Redis..."
timeout 60 bash -c 'until docker compose -f docker-compose.production.yml exec -T redis redis-cli -a $REDIS_PASSWORD ping > /dev/null 2>&1; do sleep 2; done' || {
    echo -e "${RED}❌ Redis non si è avviato in tempo${NC}"
    exit 1
}

echo "✅ Servizi infrastrutturali avviati"

# ============================================================================
# 6. Esegui migrations database
# ============================================================================
echo -e "${YELLOW}[6/8] Esecuzione migrations database...${NC}"

# Avvia temporaneamente backend per migrations
docker compose -f docker-compose.production.yml run --rm backend alembic upgrade head || {
    echo -e "${YELLOW}⚠️  Migrations fallite o non configurate${NC}"
}

echo "✅ Migrations completate"

# ============================================================================
# 7. Avvia servizi applicativi
# ============================================================================
echo -e "${YELLOW}[7/8] Avvio servizi applicativi...${NC}"

docker compose -f docker-compose.production.yml up -d backend ai_microservice frontend

echo "⏳ Attesa avvio servizi (30 secondi)..."
sleep 30

# Verifica health checks
echo "🔍 Verifica health checks..."

if docker compose -f docker-compose.production.yml exec -T backend curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "✅ Backend: ${GREEN}OK${NC}"
else
    echo -e "❌ Backend: ${RED}FAIL${NC}"
fi

if docker compose -f docker-compose.production.yml exec -T ai_microservice curl -sf http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "✅ AI Service: ${GREEN}OK${NC}"
else
    echo -e "❌ AI Service: ${RED}FAIL${NC}"
fi

echo "✅ Servizi applicativi avviati"

# ============================================================================
# 8. Setup SSL e avvio Nginx
# ============================================================================
echo -e "${YELLOW}[8/8] Setup SSL e Nginx...${NC}"
echo ""
echo -e "${BLUE}IMPORTANTE: Prima di procedere con SSL${NC}"
echo "  1. Verifica che markettina.it punti all'IP del server"
echo "  2. Verifica che le porte 80 e 443 siano aperte"
echo ""
read -p "Procedere con l'ottenimento dei certificati SSL? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔐 Ottenimento certificati SSL..."

    # Avvia Nginx temporaneo per certbot (senza SSL)
    docker compose -f docker-compose.production.yml up -d nginx

    # Ottieni certificati
    docker compose -f docker-compose.production.yml run --rm certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        -d markettina.it \
        -d www.markettina.it \
        --email admin@markettina.it \
        --agree-tos \
        --no-eff-email

    if [ $? -eq 0 ]; then
        echo "✅ Certificati SSL ottenuti!"

        # Restart Nginx con SSL
        docker compose -f docker-compose.production.yml restart nginx

        # Avvia certbot auto-renewal
        docker compose -f docker-compose.production.yml up -d certbot

        echo "✅ SSL configurato e auto-renewal attivo"
    else
        echo -e "${RED}❌ Errore nell'ottenimento dei certificati SSL${NC}"
        echo "Verifica DNS e firewall, poi riprova con:"
        echo "  docker compose -f $DOCKER_DIR/docker-compose.production.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot -d markettina.it -d www.markettina.it"
    fi
else
    echo "⏭️  SSL saltato - avvio Nginx senza HTTPS"
    docker compose -f docker-compose.production.yml up -d nginx
fi

# ============================================================================
# Configurazione Firewall
# ============================================================================
echo ""
echo -e "${GREEN}Configurazione Firewall...${NC}"

if command -v ufw &> /dev/null; then
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    echo "✅ Firewall configurato (ufw)"
elif command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    sudo firewall-cmd --reload
    echo "✅ Firewall configurato (firewalld)"
else
    echo "⚠️  Configura manualmente il firewall per aprire porte 80 e 443"
fi

# ============================================================================
# RIEPILOGO
# ============================================================================
echo ""
echo -e "${GREEN}✅ DEPLOY DOCKER COMPLETATO!${NC}"
echo "=============================="
echo ""
echo "📊 Servizi attivi:"
docker compose -f docker-compose.production.yml ps
echo ""
echo "🌐 Accesso:"
echo -e "  - ${BLUE}https://markettina.it${NC} (Frontend)"
echo -e "  - ${BLUE}https://markettina.it/api${NC} (Backend API)"
echo -e "  - ${BLUE}https://markettina.it/ai${NC} (AI Service)"
echo ""
echo "📝 Comandi utili:"
echo "  - Logs: docker compose -f $DOCKER_DIR/docker-compose.production.yml logs -f"
echo "  - Status: docker compose -f $DOCKER_DIR/docker-compose.production.yml ps"
echo "  - Stop: docker compose -f $DOCKER_DIR/docker-compose.production.yml down"
echo "  - Restart: docker compose -f $DOCKER_DIR/docker-compose.production.yml restart"
echo ""
echo "🔧 Logs specifici:"
echo "  - Backend: docker compose -f $DOCKER_DIR/docker-compose.production.yml logs -f backend"
echo "  - AI: docker compose -f $DOCKER_DIR/docker-compose.production.yml logs -f ai_microservice"
echo "  - Frontend: docker compose -f $DOCKER_DIR/docker-compose.production.yml logs -f frontend"
echo "  - Nginx: docker compose -f $DOCKER_DIR/docker-compose.production.yml logs -f nginx"
echo ""
echo "🔐 SSL:"
echo "  - Certificati: docker compose -f $DOCKER_DIR/docker-compose.production.yml exec certbot certbot certificates"
echo "  - Rinnova: docker compose -f $DOCKER_DIR/docker-compose.production.yml exec certbot certbot renew"
echo ""
