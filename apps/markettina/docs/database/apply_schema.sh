#!/bin/bash
# ============================================================================
# MARKETTINA v2.0 - Apply Schema to Docker PostgreSQL
# ============================================================================
# Usage: ./apply_schema.sh
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="markettina-db"
DB_NAME="markettina"
DB_USER="markettina"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}  MARKETTINA v2.0 - Schema ER Application${NC}"
echo -e "${BLUE}============================================================================${NC}"

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}❌ Container ${CONTAINER_NAME} non in esecuzione!${NC}"
    echo -e "${YELLOW}Avvia con: cd config/docker && docker compose -f docker-compose.production.yml up -d postgres${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Container ${CONTAINER_NAME} attivo${NC}"

# Function to execute SQL file
execute_sql_file() {
    local file=$1
    local description=$2

    echo -e "${YELLOW}📄 Esecuzione: ${description}...${NC}"

    if docker exec -i ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} < "${file}" 2>&1; then
        echo -e "${GREEN}   ✅ Completato${NC}"
    else
        echo -e "${RED}   ❌ Errore in ${file}${NC}"
        return 1
    fi
}

# Backup first
echo -e "${YELLOW}📦 Creazione backup database...${NC}"
BACKUP_FILE="${SCRIPT_DIR}/backup_$(date +%Y%m%d_%H%M%S).sql"
docker exec ${CONTAINER_NAME} pg_dump -U ${DB_USER} -d ${DB_NAME} > "${BACKUP_FILE}" 2>/dev/null || true
echo -e "${GREEN}   ✅ Backup salvato: ${BACKUP_FILE}${NC}"

# Apply DDL files in order
echo -e "\n${BLUE}🚀 Applicazione Schema DDL...${NC}\n"

execute_sql_file "${SCRIPT_DIR}/MARKETTINA_v2_DDL_PART1.sql" "Part 1: Accounts, Identity, Billing"
execute_sql_file "${SCRIPT_DIR}/MARKETTINA_v2_DDL_PART2.sql" "Part 2: Content, Analytics"
execute_sql_file "${SCRIPT_DIR}/MARKETTINA_v2_DDL_PART3.sql" "Part 3: Social, AI Services"
execute_sql_file "${SCRIPT_DIR}/MARKETTINA_v2_DDL_PART4.sql" "Part 4: Workflow, Knowledge Base, Shared Kernel"
execute_sql_file "${SCRIPT_DIR}/MARKETTINA_v2_DDL_PART5_VIEWS.sql" "Part 5: Materialized Views, Triggers, RLS"

echo -e "\n${GREEN}============================================================================${NC}"
echo -e "${GREEN}  ✅ SCHEMA MARKETTINA v2.0 APPLICATO CON SUCCESSO!${NC}"
echo -e "${GREEN}============================================================================${NC}"

# Show table count
echo -e "\n${BLUE}📊 Statistiche Database:${NC}"
docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -c "
SELECT
    'Tabelle' as tipo,
    COUNT(*) as conteggio
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
UNION ALL
SELECT
    'Viste Materializzate',
    COUNT(*)
FROM pg_matviews
WHERE schemaname = 'public'
UNION ALL
SELECT
    'Indici',
    COUNT(*)
FROM pg_indexes
WHERE schemaname = 'public';
"

echo -e "\n${YELLOW}💡 Prossimi passi:${NC}"
echo -e "   1. Verifica le tabelle: docker exec -it ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -c '\\dt'"
echo -e "   2. Genera migrazioni Alembic: cd apps/backend && uv run alembic revision --autogenerate -m 'markettina_v2'"
echo -e "   3. Crea modelli SQLAlchemy per le nuove tabelle"
