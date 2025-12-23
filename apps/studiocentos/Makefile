# ============================================================================
# STUDIOCENTOS - Makefile
# ============================================================================
# Comandi rapidi per gestire Docker Compose in sviluppo e produzione
# ============================================================================

.PHONY: help
.DEFAULT_GOAL := help

# Variabili
DOCKER_COMPOSE_DEV = docker compose -f docker-compose.yml
DOCKER_COMPOSE_PROD = docker compose -f docker-compose.production.yml
DOCKER_DIR = config/docker

# Colori per output
GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
RED    := \033[0;31m
NC     := \033[0m

# ============================================================================
# HELP
# ============================================================================

help: ## Mostra questo help
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║         STUDIOCENTOS - Comandi Make                       ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)📦 PRODUZIONE (Docker Completo):$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep "PROD" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)🔧 SVILUPPO (Servizi locali):$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep "DEV" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)🛠️  UTILITY:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -v "PROD\|DEV" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ============================================================================
# PRODUZIONE - Docker Compose Completo
# ============================================================================

prod-deploy: ## [PROD] Deploy completo produzione con SSL
	@echo "$(GREEN)🚀 Deploy produzione completo...$(NC)"
	@./scripts/deployment/deploy.sh

prod-build: ## [PROD] Build tutte le immagini Docker
	@echo "$(GREEN)📦 Build immagini produzione...$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) build

prod-build-backend: ## [PROD] Build solo backend
	@echo "$(GREEN)📦 Build backend...$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) build backend

prod-build-ai: ## [PROD] Build solo AI microservice
	@echo "$(GREEN)📦 Build AI microservice...$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) build ai_microservice

prod-build-frontend: ## [PROD] Build solo frontend
	@echo "$(GREEN)📦 Build frontend...$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) build frontend

prod-up: ## [PROD] Avvia tutti i servizi produzione
	@echo "$(GREEN)🚀 Avvio servizi produzione...$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) up -d
	@echo "$(GREEN)✅ Servizi avviati!$(NC)"
	@make prod-ps

prod-down: ## [PROD] Ferma tutti i servizi produzione
	@echo "$(YELLOW)🛑 Stop servizi produzione...$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) down
	@echo "$(GREEN)✅ Servizi fermati!$(NC)"

prod-restart: ## [PROD] Restart tutti i servizi produzione
	@echo "$(YELLOW)🔄 Restart servizi produzione...$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) restart
	@echo "$(GREEN)✅ Servizi riavviati!$(NC)"

prod-ps: ## [PROD] Status servizi produzione
	@echo "$(BLUE)📊 Status servizi produzione:$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) ps

prod-logs: ## [PROD] Logs tutti i servizi produzione
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) logs -f

prod-logs-backend: ## [PROD] Logs backend
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) logs -f backend

prod-logs-ai: ## [PROD] Logs AI microservice
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) logs -f ai_microservice

prod-logs-frontend: ## [PROD] Logs frontend
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) logs -f frontend

prod-logs-nginx: ## [PROD] Logs Nginx
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) logs -f nginx

prod-shell-backend: ## [PROD] Shell nel container backend
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) exec backend /bin/bash

prod-shell-ai: ## [PROD] Shell nel container AI
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) exec ai_microservice /bin/bash

prod-shell-db: ## [PROD] Shell PostgreSQL
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) exec postgres psql -U studiocentos -d studiocentos

prod-migrate: ## [PROD] Esegui migrations database
	@echo "$(GREEN)📊 Esecuzione migrations...$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) exec backend alembic upgrade head
	@echo "$(GREEN)✅ Migrations completate!$(NC)"

prod-ssl-renew: ## [PROD] Rinnova certificati SSL
	@echo "$(GREEN)🔐 Rinnovo certificati SSL...$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) exec certbot certbot renew
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) exec nginx nginx -s reload

prod-ssl-status: ## [PROD] Status certificati SSL
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) exec certbot certbot certificates

# ============================================================================
# SVILUPPO - Servizi infrastrutturali Docker + App locali
# ============================================================================

dev-up: ## [DEV] Avvia PostgreSQL + Redis
	@echo "$(GREEN)🚀 Avvio servizi sviluppo (PostgreSQL + Redis)...$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_DEV) up -d postgres redis
	@echo "$(GREEN)✅ Servizi avviati!$(NC)"
	@make dev-ps

dev-down: ## [DEV] Ferma servizi sviluppo
	@echo "$(YELLOW)🛑 Stop servizi sviluppo...$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_DEV) down
	@echo "$(GREEN)✅ Servizi fermati!$(NC)"

dev-restart: ## [DEV] Restart servizi sviluppo
	@echo "$(YELLOW)🔄 Restart servizi sviluppo...$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_DEV) restart
	@echo "$(GREEN)✅ Servizi riavviati!$(NC)"

dev-ps: ## [DEV] Status servizi sviluppo
	@echo "$(BLUE)📊 Status servizi sviluppo:$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_DEV) ps

dev-logs: ## [DEV] Logs servizi sviluppo
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_DEV) logs -f

dev-logs-db: ## [DEV] Logs PostgreSQL
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_DEV) logs -f postgres

dev-logs-redis: ## [DEV] Logs Redis
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_DEV) logs -f redis

dev-shell-db: ## [DEV] Shell PostgreSQL
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_DEV) exec postgres psql -U studiocentos -d studiocentos

dev-backend: ## [DEV] Avvia backend locale (porta 8002)
	@echo "$(GREEN)🚀 Avvio backend locale...$(NC)"
	@cd apps/backend && uv run uvicorn app.main:app --reload --port 8002

dev-ai: ## [DEV] Avvia AI microservice locale (porta 8001)
	@echo "$(GREEN)🚀 Avvio AI microservice locale...$(NC)"
	@cd apps/ai_microservice && uv run uvicorn app.main:app --reload --port 8001

dev-frontend: ## [DEV] Avvia frontend locale (porta 3000)
	@echo "$(GREEN)🚀 Avvio frontend locale...$(NC)"
	@cd apps/frontend && pnpm dev --port 3000

# ============================================================================
# UTILITY
# ============================================================================

clean: ## Pulisci containers, volumi e immagini
	@echo "$(RED)🧹 Pulizia completa Docker...$(NC)"
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) down -v --rmi all
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_DEV) down -v
	@docker system prune -af
	@echo "$(GREEN)✅ Pulizia completata!$(NC)"

clean-all: ## 🔥 PULIZIA TOTALE (Docker+Cache+Logs)
	@echo "$(RED)🧹 PULIZIA COMPLETA SISTEMA$(NC)"
	@echo "$(YELLOW)Questo pulirà: Docker, cache, logs, pacchetti orfani$(NC)"
	@read -p "Confermi? (yes/no): " confirm; \
	if [ "$$confirm" != "yes" ]; then \
		echo "$(YELLOW)❌ Operazione annullata$(NC)"; \
		exit 0; \
	fi; \
	echo ""; \
	BEFORE=$$(df -h / | tail -1 | awk '{print $$5}'); \
	echo "$(CYAN)📊 Disco PRIMA: $$BEFORE$(NC)"; \
	echo ""; \
	echo "$(CYAN)1️⃣  Docker system prune...$(NC)"; \
	docker system prune -af --volumes 2>/dev/null || true; \
	echo ""; \
	echo "$(CYAN)2️⃣  Cache UV/PIP...$(NC)"; \
	rm -rf ~/.cache/uv ~/.cache/pip 2>/dev/null || true; \
	echo ""; \
	echo "$(CYAN)3️⃣  PNPM store prune...$(NC)"; \
	pnpm store prune 2>/dev/null || true; \
	echo ""; \
	echo "$(CYAN)4️⃣  Pacman cache...$(NC)"; \
	sudo pacman -Sc --noconfirm 2>/dev/null || true; \
	echo ""; \
	echo "$(CYAN)5️⃣  Journal logs (2 weeks)...$(NC)"; \
	sudo journalctl --vacuum-time=2weeks 2>/dev/null || true; \
	echo ""; \
	echo "$(CYAN)6️⃣  Build artifacts...$(NC)"; \
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true; \
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true; \
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true; \
	find . -type d -name ".vite" -exec rm -rf {} + 2>/dev/null || true; \
	echo ""; \
	AFTER=$$(df -h / | tail -1 | awk '{print $$5}'); \
	AVAIL=$$(df -h / | tail -1 | awk '{print $$4}'); \
	echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"; \
	echo "$(GREEN)✅ PULIZIA COMPLETATA!$(NC)"; \
	echo "$(CYAN)📊 Disco PRIMA: $$BEFORE → DOPO: $$AFTER$(NC)"; \
	echo "$(CYAN)💾 Spazio disponibile: $$AVAIL$(NC)"; \
	echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"

stats: ## Statistiche Docker
	@echo "$(BLUE)📊 Statistiche Docker:$(NC)"
	@docker stats --no-stream

health: ## Health check servizi produzione
	@echo "$(BLUE)🏥 Health check servizi:$(NC)"
	@echo ""
	@echo "$(YELLOW)Backend:$(NC)"
	@curl -sf http://localhost:8002/health && echo "$(GREEN)✅ OK$(NC)" || echo "$(RED)❌ FAIL$(NC)"
	@echo ""
	@echo "$(YELLOW)AI Service:$(NC)"
	@curl -sf http://localhost:8001/health && echo "$(GREEN)✅ OK$(NC)" || echo "$(RED)❌ FAIL$(NC)"
	@echo ""
	@echo "$(YELLOW)Frontend:$(NC)"
	@curl -sf http://localhost:3000 && echo "$(GREEN)✅ OK$(NC)" || echo "$(RED)❌ FAIL$(NC)"
	@echo ""

backup-db: ## Backup database produzione
	@echo "$(GREEN)💾 Backup database...$(NC)"
	@mkdir -p backups
	@cd $(DOCKER_DIR) && $(DOCKER_COMPOSE_PROD) exec -T postgres \
		pg_dump -U studiocentos studiocentos | gzip > ../../backups/backup-$$(date +%Y%m%d-%H%M%S).sql.gz
	@echo "$(GREEN)✅ Backup salvato in backups/$(NC)"

env-example: ## Crea .env.production da example
	@echo "$(GREEN)📝 Creazione .env.production...$(NC)"
	@cp .env.production.example .env.production
	@echo "$(YELLOW)⚠️  Modifica .env.production con le tue credenziali!$(NC)"
	@echo ""
	@echo "Genera password con:"
	@echo "  openssl rand -base64 32  # PostgreSQL"
	@echo "  openssl rand -base64 32  # Redis"
	@echo "  openssl rand -hex 32     # JWT Secret"

install-deps: ## Installa dipendenze backend e frontend
	@echo "$(GREEN)📦 Installazione dipendenze...$(NC)"
	@echo "Backend (UV)..."
	@cd apps/backend && uv sync
	@echo "AI Microservice (UV)..."
	@cd apps/ai_microservice && uv sync
	@echo "Frontend (pnpm)..."
	@cd apps/frontend && pnpm install
	@echo "$(GREEN)✅ Dipendenze installate!$(NC)"

# ============================================================================
# QUICK COMMANDS (Alias)
# ============================================================================

up: prod-up ## Alias per prod-up
down: prod-down ## Alias per prod-down
build: prod-build ## Alias per prod-build
logs: prod-logs ## Alias per prod-logs
ps: prod-ps ## Alias per prod-ps
restart: prod-restart ## Alias per prod-restart
deploy: prod-deploy ## Alias per prod-deploy
