# ISS - Innovazione Sociale Salernitana
# Docker Management Makefile

.PHONY: help setup build up down restart logs clean deploy backup health test

# Default target
help: ## Show this help message
	@echo "🏛️  ISS - Innovazione Sociale Salernitana"
	@echo "🐳 Docker Management Commands"
	@echo "=================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "📊 Quick Status:"
	@docker-compose ps 2>/dev/null || echo "Services not running"

# Development commands
setup: ## Initial setup for development
	@echo "🚀 Setting up ISS development environment..."
	@./scripts/docker-setup.sh

build: ## Build all Docker images
	@echo "🔨 Building Docker images..."
	@docker-compose build --parallel

up: ## Start all services
	@echo "▶️  Starting ISS services..."
	@docker-compose up -d
	@echo "✅ Services started. Check status with 'make status'"

down: ## Stop all services
	@echo "⏹️  Stopping ISS services..."
	@docker-compose down

restart: ## Restart all services
	@echo "🔄 Restarting ISS services..."
	@docker-compose restart

# Monitoring commands
logs: ## Show logs for all services
	@docker-compose logs -f

logs-backend: ## Show backend logs only
	@docker-compose logs -f backend

logs-frontend: ## Show frontend logs only
	@docker-compose logs -f frontend

logs-db: ## Show database logs only
	@docker-compose logs -f postgres

status: ## Show service status
	@echo "📊 ISS Services Status:"
	@docker-compose ps
	@echo ""
	@echo "🌐 Service URLs:"
	@echo "   Frontend:        http://localhost:3001"
	@echo "   Backend API:     http://localhost:8001"
	@echo "   API Docs:        http://localhost:8001/docs"
	@echo "   Redis Commander: http://localhost:8082"
	@echo "   MailHog (dev):   http://localhost:8026"

health: ## Check service health
	@echo "🏥 Checking service health..."
	@./scripts/docker-deploy.sh health

# Database commands
db-shell: ## Connect to PostgreSQL shell
	@docker-compose exec postgres psql -U postgres -d iss_wbs

db-backup: ## Create database backup
	@echo "💾 Creating database backup..."
	@mkdir -p backups
	@docker-compose exec -T postgres pg_dump -U postgres iss_wbs > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created in backups/ directory"

db-restore: ## Restore database from backup (usage: make db-restore FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then echo "❌ Please specify FILE=backup.sql"; exit 1; fi
	@echo "🔄 Restoring database from $(FILE)..."
	@docker-compose exec -T postgres psql -U postgres -d iss_wbs < $(FILE)
	@echo "✅ Database restored"

# Development tools
shell-backend: ## Access backend container shell
	@docker-compose exec backend bash

shell-frontend: ## Access frontend container shell
	@docker-compose exec frontend sh

shell-db: ## Access database container shell
	@docker-compose exec postgres bash

# Testing commands
test: ## Run all tests
	@echo "🧪 Running tests..."
	@docker-compose exec backend python -m pytest
	@echo "✅ Tests completed"

test-backend: ## Run backend tests only
	@docker-compose exec backend python -m pytest tests/

test-frontend: ## Run frontend tests only
	@docker-compose exec frontend npm test

# Production commands
deploy: ## Deploy to production
	@echo "🚀 Deploying to production..."
	@./scripts/docker-deploy.sh deploy

backup: ## Create full backup
	@echo "💾 Creating full backup..."
	@./scripts/docker-deploy.sh backup

rollback: ## Rollback to previous version (usage: make rollback BACKUP=backup_dir)
	@if [ -z "$(BACKUP)" ]; then echo "❌ Please specify BACKUP=backup_directory"; exit 1; fi
	@./scripts/docker-deploy.sh rollback $(BACKUP)

# Maintenance commands
clean: ## Clean up Docker resources
	@echo "🧹 Cleaning up Docker resources..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f
	@docker volume prune -f
	@echo "✅ Cleanup completed"

clean-all: ## Clean everything including images
	@echo "🧹 Deep cleaning Docker resources..."
	@docker-compose down -v --remove-orphans
	@docker system prune -af
	@docker volume prune -f
	@echo "✅ Deep cleanup completed"

update: ## Update all images and rebuild
	@echo "🔄 Updating ISS platform..."
	@docker-compose pull
	@docker-compose build --no-cache --parallel
	@docker-compose up -d
	@echo "✅ Update completed"

# Development helpers
dev-setup: ## Setup development environment with hot reload
	@echo "🛠️  Setting up development environment..."
	@cp .env.example .env
	@echo "ENVIRONMENT=development" >> .env
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "✅ Development environment ready"

prod-setup: ## Setup production environment
	@echo "🏭 Setting up production environment..."
	@cp .env.example .env
	@echo "ENVIRONMENT=production" >> .env
	@echo "⚠️  Please edit .env file with production values"
	@docker-compose --profile production up -d

# Monitoring
monitor: ## Show real-time resource usage
	@echo "📊 Real-time resource monitoring (Ctrl+C to exit):"
	@docker stats

# Quick actions
quick-restart-backend: ## Quick restart backend only
	@docker-compose restart backend

quick-restart-frontend: ## Quick restart frontend only
	@docker-compose restart frontend

quick-logs: ## Show last 50 lines of logs
	@docker-compose logs --tail=50

# Security
security-scan: ## Run security scan on images
	@echo "🔒 Running security scan..."
	@docker scout quickview 2>/dev/null || echo "Docker Scout not available"
	@echo "✅ Security scan completed"
