#!/bin/bash
# ================================
# IronRep Production Deployment Script
# ================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$PROJECT_ROOT/config/docker"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}   IronRep Production Deploy    ${NC}"
echo -e "${BLUE}================================${NC}"

# Check .env.prod exists
if [ ! -f "$DOCKER_DIR/.env.prod" ]; then
    echo -e "${RED}❌ .env.prod not found!${NC}"
    echo "Copy .env.example to .env.prod and configure it:"
    echo "  cp $DOCKER_DIR/.env.example $DOCKER_DIR/.env.prod"
    exit 1
fi

echo -e "${GREEN}✅ .env.prod found${NC}"

# Navigate to docker directory
cd "$DOCKER_DIR"

# Parse command
case "${1:-deploy}" in
    deploy)
        echo -e "\n${YELLOW}🚀 Starting production deployment...${NC}\n"

        # Pull latest images
        echo -e "${BLUE}📦 Building images...${NC}"
        docker-compose -f docker-compose.prod.yml build

        # Start services
        echo -e "${BLUE}🔄 Starting services...${NC}"
        docker-compose -f docker-compose.prod.yml up -d

        # Wait for health checks
        echo -e "${BLUE}⏳ Waiting for services to be healthy...${NC}"
        sleep 10

        # Run migrations
        echo -e "${BLUE}📊 Running database migrations...${NC}"
        docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head || true

        # Setup SSL certificates (if needed)
        echo -e "${BLUE}🔒 Checking SSL certificates...${NC}"
        if ! docker-compose -f docker-compose.prod.yml exec -T frontend test -f /etc/letsencrypt/live/ironrep.it/fullchain.pem; then
            echo -e "${YELLOW}⚠️  SSL certificates not found. Run: ./scripts/deploy.sh ssl${NC}"
        fi

        # Show status
        echo -e "\n${GREEN}✅ Deployment complete!${NC}\n"
        docker-compose -f docker-compose.prod.yml ps
        ;;

    stop)
        echo -e "${YELLOW}⏹️  Stopping services...${NC}"
        docker-compose -f docker-compose.prod.yml down
        echo -e "${GREEN}✅ Services stopped${NC}"
        ;;

    restart)
        echo -e "${YELLOW}🔄 Restarting services...${NC}"
        docker-compose -f docker-compose.prod.yml restart
        echo -e "${GREEN}✅ Services restarted${NC}"
        ;;

    logs)
        docker-compose -f docker-compose.prod.yml logs -f ${2:-}
        ;;

    status)
        docker-compose -f docker-compose.prod.yml ps
        ;;

    migrate)
        echo -e "${BLUE}📊 Running migrations...${NC}"
        docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
        ;;

    ssl)
        echo -e "${BLUE}🔒 Setting up SSL certificates...${NC}"
        docker-compose -f docker-compose.prod.yml run --rm certbot
        echo -e "${GREEN}✅ SSL certificates obtained${NC}"
        echo -e "${YELLOW}Restarting frontend to apply SSL...${NC}"
        docker-compose -f docker-compose.prod.yml restart frontend
        ;;

    clean)
        echo -e "${RED}⚠️  Cleaning all data (volumes)...${NC}"
        read -p "Are you sure? (y/N) " confirm
        if [ "$confirm" = "y" ]; then
            docker-compose -f docker-compose.prod.yml down -v
            echo -e "${GREEN}✅ Cleaned${NC}"
        fi
        ;;

    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status|migrate|ssl|clean}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Build and start all services"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - View logs (optional: service name)"
        echo "  status   - Show service status"
        echo "  migrate  - Run database migrations"
        echo "  ssl      - Setup SSL certificates"
        echo "  clean    - Remove all containers and volumes"
        exit 1
        ;;
esac
