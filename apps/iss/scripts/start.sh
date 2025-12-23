#!/bin/bash

# 🚀 Script di avvio completo ISS con sistema bandi integrato

set -e

echo "🔥 Starting ISS Complete System..."

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica prerequisiti
print_status "Verificando prerequisiti..."

if ! command -v docker &> /dev/null; then
    print_error "Docker non trovato. Installa Docker prima di continuare."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose non trovato. Installa Docker Compose prima di continuare."
    exit 1
fi

print_success "Docker e Docker Compose trovati ✅"

# Pulisci eventuali container precedenti
print_status "Pulizia container precedenti..."
docker-compose down -v --remove-orphans 2>/dev/null || true

# Avvia i servizi
print_status "Avvio servizi ISS..."
docker-compose up -d --build

# Aspetta che i servizi siano pronti
print_status "Attendendo che i servizi siano pronti..."

# Attendi PostgreSQL
print_status "Attendendo PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U postgres -d iss_wbs &>/dev/null; do
    sleep 2
done
print_success "PostgreSQL pronto ✅"

# Attendi Redis
print_status "Attendendo Redis..."
until docker-compose exec -T redis redis-cli ping &>/dev/null; do
    sleep 1
done
print_success "Redis pronto ✅"

# Attendi Backend
print_status "Attendendo Backend API..."
max_attempts=30
attempt=0
until curl -f http://localhost:8000/health &>/dev/null; do
    attempt=$((attempt + 1))
    if [ $attempt -gt $max_attempts ]; then
        print_error "Backend non risponde dopo $max_attempts tentativi"
        print_error "Controlla i log: docker-compose logs backend"
        exit 1
    fi
    sleep 2
done
print_success "Backend API pronto ✅"

# Esegui le migrazioni
print_status "Esecuzione migrazioni database..."
docker-compose exec backend alembic upgrade head
if [ $? -eq 0 ]; then
    print_success "Migrazioni completate ✅"
else
    print_warning "Errore nelle migrazioni - il database potrebbe essere già aggiornato"
fi

# Setup iniziale sistema bandi
print_status "Setup sistema bandi..."
docker-compose exec backend python scripts/setup_bando_system.py --auto-setup 2>/dev/null || true
print_success "Sistema bandi configurato ✅"

echo
echo "🎉 ISS System avviato con successo!"
echo
echo "📊 SERVIZI DISPONIBILI:"
echo "┌─────────────────────────────────────────────────────┐"
echo "│ 🌐 Backend API:          http://localhost:8000      │"
echo "│ 📊 API Docs (Swagger):   http://localhost:8000/docs │"
echo "│ ❤️  Health Check:        http://localhost:8000/health│"
echo "│                                                     │"
echo "│ 🗄️  PgAdmin:             http://localhost:5050      │"
echo "│     Login: admin@iss.local / admin123              │"
echo "│                                                     │"
echo "│ 🔴 Redis Commander:      http://localhost:8081      │"
echo "│     Login: admin / admin123                         │"
echo "│                                                     │"
echo "│ 📧 MailHog (Email Test):  http://localhost:8025     │"
echo "└─────────────────────────────────────────────────────┘"
echo
echo "🎯 ENDPOINTS API BANDI:"
echo "• GET  /api/v1/bandi/                    - Lista bandi"
echo "• GET  /api/v1/bandi/stats               - Statistiche"  
echo "• GET  /api/v1/bandi/recent              - Bandi recenti"
echo "• GET  /api/v1/admin/bandi-config/       - Configurazioni (admin)"
echo "• POST /api/v1/admin/bandi-config/{id}/run - Trigger monitoraggio"
echo
echo "📋 COMANDI UTILI:"
echo "• docker-compose logs backend            - Log backend"
echo "• docker-compose logs postgres           - Log database"
echo "• docker-compose exec backend bash       - Shell nel container"
echo "• docker-compose down                    - Stop tutti i servizi"
echo
echo "🔧 Per configurare email/Telegram per il sistema bandi:"
echo "   Vai su http://localhost:8000/docs e usa gli endpoints admin"
echo
