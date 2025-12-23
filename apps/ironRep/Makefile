.PHONY: help deploy build test clean clean-all

# ============================================================================
# 🎯 CV-LAB MAKEFILE v9.0 - ENTERPRISE GRADE (LOCAL/PROD)
# ============================================================================
# Separazione completa LOCAL vs PRODUCTION
# Updated: 2025-12-14
# ============================================================================

.DEFAULT_GOAL := help

# Colors
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
BOLD := \033[1m
NC := \033[0m

# Paths
PROJECT_ROOT := $(shell pwd)
APPS_DIR := $(PROJECT_ROOT)/apps
CONFIG_DIR := $(PROJECT_ROOT)/config
SCRIPTS_DIR := $(PROJECT_ROOT)/scripts

# Docker LOCAL
COMPOSE_LOCAL := $(CONFIG_DIR)/docker/docker-compose.local-prod.yml
LOCAL_FRONTEND_URL := http://localhost:3000
LOCAL_BACKEND_URL := http://localhost:8000

# Docker PRODUCTION
STACK_NAME := cv-lab-prod
COMPOSE_PROD := $(CONFIG_DIR)/docker/docker-compose.prod.yml
PROD_FRONTEND_URL := https://cv-lab.pro
PROD_BACKEND_URL := https://cv-lab.pro/api/v1

# ============================================================================
# 📚 HELP
# ============================================================================

help:
	@echo ""
	@echo "╔═══════════════════════════════════════════════════════════════════╗"
	@echo "║         🚀 CV-LAB MAKEFILE v9.0 - ENTERPRISE (LOCAL/PROD)         ║"
	@echo "╚═══════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo -e "$(GREEN)$(BOLD)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(GREEN)$(BOLD)  🏠 LOCAL ENVIRONMENT (docker-compose.local-prod.yml)$(NC)"
	@echo -e "$(GREEN)$(BOLD)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo -e "$(CYAN)$(BOLD)� CONTAINER:$(NC)"
	@echo -e "  $(GREEN)make up-local$(NC)              - 🚀 Avvia ambiente locale (TUTTO)"
	@echo -e "  $(GREEN)make up-backend-only$(NC)       - 🚀 Avvia solo Backend (Frontend locale)"
	@echo -e "  make down-local              - 🛑 Ferma ambiente locale"
	@echo -e "  make restart-local           - 🔄 Restart ambiente locale"
	@echo -e "  make ps-local                - 📊 Status container"
	@echo -e "  make logs-local              - 📋 Logs tutti i servizi"
	@echo -e "  make logs-local-backend      - 📋 Logs backend"
	@echo -e "  make logs-local-frontend     - 📋 Logs frontend"
	@echo ""
	@echo -e "$(CYAN)$(BOLD)🗄️  DATABASE LOCAL:$(NC)"
	@echo -e "  make db-backup-local         - 💾 Backup database"
	@echo -e "  make db-seed-local           - 🌱 Seed dati"
	@echo -e "  make cleanup-test-users-local- 🧹 Cleanup utenti test"
	@echo ""
	@echo -e "$(CYAN)$(BOLD)� DEV (senza Docker):$(NC)"
	@echo -e "  make dev-backend             - Avvia backend (uvicorn)"
	@echo -e "  make dev-frontend            - Avvia frontend (vite)"
	@echo ""
	@echo -e "$(RED)$(BOLD)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(RED)$(BOLD)  🌐 PRODUCTION (Docker Swarm - cv-lab.pro)$(NC)"
	@echo -e "$(RED)$(BOLD)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo -e "$(CYAN)$(BOLD)🚀 DEPLOY:$(NC)"
	@echo -e "  $(YELLOW)make deploy$(NC)                - Deploy completo (preferisci git push)"
	@echo -e "  make deploy-backend          - Deploy solo backend"
	@echo -e "  make deploy-frontend         - Deploy solo frontend"
	@echo -e "  make deploy-quick            - Quick deploy (no rebuild)"
	@echo ""
	@echo -e "$(CYAN)$(BOLD)📊 MONITORING PROD:$(NC)"
	@echo -e "  make services                - Status servizi Swarm"
	@echo -e "  make logs                    - Logs PROD"
	@echo -e "  make logs-backend            - Logs backend PROD"
	@echo -e "  make logs-frontend           - Logs frontend PROD"
	@echo -e "  make health                  - Health check PROD"
	@echo ""
	@echo -e "$(CYAN)$(BOLD)🗄️  DATABASE PROD:$(NC)"
	@echo -e "  make db-backup               - 💾 Backup database PROD"
	@echo -e "  make db-seed                 - 🌱 Seed dati PROD"
	@echo -e "  $(YELLOW)make cleanup-test-users$(NC)      - 🧹 Cleanup utenti test PROD"
	@echo -e "  $(YELLOW)make delete-test-user EMAIL=x$(NC)- 🗑️  Elimina utente PROD"
	@echo -e "  $(RED)make db-reset-users$(NC)          - ⚠️  RESET utenti PROD"
	@echo ""
	@echo -e "$(CYAN)$(BOLD)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(CYAN)$(BOLD)  🧪 TEST & 🧹 CLEANUP$(NC)"
	@echo -e "$(CYAN)$(BOLD)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo -e "$(CYAN)$(BOLD)🧪 TEST:$(NC)"
	@echo -e "  make test                    - Run tutti i test"
	@echo -e "  make test-backend            - Test backend"
	@echo -e "  make test-frontend           - Test frontend"
	@echo -e "  make lint                    - Lint codice"
	@echo -e "  make format                  - Format codice"
	@echo ""
	@echo -e "$(CYAN)$(BOLD)🧹 CLEANUP:$(NC)"
	@echo -e "  make clean                   - Pulisci artifacts"
	@echo -e "  make clean-docker            - Pulisci cache Docker"
	@echo -e "  $(RED)make clean-all$(NC)               - 🔥 PULIZIA TOTALE"
	@echo ""

# ============================================================================
# 🏠 LOCAL ENVIRONMENT (docker-compose.local-prod.yml)
# ============================================================================

up-local:
	@echo -e "$(GREEN)🚀 Avvio ambiente LOCAL...$(NC)"
	@docker compose -f $(COMPOSE_LOCAL) up -d
	@echo -e "$(GREEN)✅ Ambiente LOCAL avviato!$(NC)"
	@echo -e "$(CYAN)   Frontend: $(LOCAL_FRONTEND_URL)$(NC)"
	@echo -e "$(CYAN)   Backend:  $(LOCAL_BACKEND_URL)$(NC)"
	@echo -e "$(CYAN)   API Docs: $(LOCAL_BACKEND_URL)/docs$(NC)"

up-backend-only:
	@echo -e "$(GREEN)🚀 Avvio ambiente LOCAL (SOLO BACKEND)...$(NC)"
	@docker compose -f $(COMPOSE_LOCAL) up -d backend postgres redis nginx ai-service prometheus grafana alertmanager
	@echo -e "$(GREEN)✅ Backend LOCAL avviato!$(NC)"
	@echo -e "$(YELLOW)⚠️  Frontend Docker NON avviato (usa 'make dev-frontend' per locale)$(NC)"
	@echo -e "$(CYAN)   Backend:  $(LOCAL_BACKEND_URL)$(NC)"
	@echo -e "$(CYAN)   API Docs: $(LOCAL_BACKEND_URL)/docs$(NC)"

down-local:
	@echo -e "$(YELLOW)🚫 Stop ambiente LOCAL...$(NC)"
	@docker compose -f $(COMPOSE_LOCAL) down
	@echo -e "$(GREEN)✅ Ambiente LOCAL fermato!$(NC)"

restart-local:
	@echo -e "$(CYAN)🔄 Restart ambiente LOCAL...$(NC)"
	@docker compose -f $(COMPOSE_LOCAL) restart

ps-local:
	@docker compose -f $(COMPOSE_LOCAL) ps

logs-local:
	@docker compose -f $(COMPOSE_LOCAL) logs -f

logs-local-backend:
	@docker compose -f $(COMPOSE_LOCAL) logs -f backend

logs-local-frontend:
	@docker compose -f $(COMPOSE_LOCAL) logs -f frontend

build-local:
	@echo -e "$(CYAN)🔨 Build immagini LOCAL...$(NC)"
	@docker compose -f $(COMPOSE_LOCAL) build

rebuild-local:
	@echo -e "$(CYAN)🔨 Rebuild e restart LOCAL...$(NC)"
	@docker compose -f $(COMPOSE_LOCAL) up -d --build

health-local:
	@echo -e "$(CYAN)� Health Check LOCAL...$(NC)"
	@curl -sf $(LOCAL_BACKEND_URL)/health 2>/dev/null && echo " ✅ Backend OK" || echo " ❌ Backend DOWN"
	@curl -sf -o /dev/null $(LOCAL_FRONTEND_URL) 2>/dev/null && echo " ✅ Frontend OK" || echo " ❌ Frontend DOWN"

# ============================================================================
# 🗄️  DATABASE - LOCAL
# ============================================================================

db-backup-local:
	@echo -e "$(CYAN)💾 [LOCAL] Backup database...$(NC)"
	@bash $(SCRIPTS_DIR)/database/local/backup.sh

db-seed-local:
	@echo -e "$(CYAN)🌱 [LOCAL] Seeding database...$(NC)"
	@docker exec -i cv-lab-postgres psql -U cv_lab_local_user -d cv_lab_local < $(SCRIPTS_DIR)/deployment/database/seed-production-CLEAN.sql

cleanup-test-users-local:
	@echo -e "$(CYAN)🧹 [LOCAL] Cleanup utenti test...$(NC)"
	@bash $(SCRIPTS_DIR)/database/local/cleanup-test-users.sh

# ============================================================================
#  DEV (senza Docker)
# ============================================================================

dev-frontend:
	@echo -e "$(CYAN)🚀 Avvio FRONTEND in locale...$(NC)"
	@cd $(APPS_DIR)/frontend && pnpm dev

dev-backend:
	@echo -e "$(CYAN)🚀 Avvio BACKEND in locale...$(NC)"
	@cd $(APPS_DIR)/backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ============================================================================
# 🌐 PRODUCTION - DEPLOY (Docker Swarm)
# ============================================================================

deploy:
	@echo -e "$(RED)🚀 [PROD] Deploy COMPLETO...$(NC)"
	@echo -e "$(YELLOW)⚠️  Preferisci git push per auto-deploy via GitHub Actions$(NC)"
	@docker stack deploy -c $(COMPOSE_PROD) $(STACK_NAME)

deploy-quick:
	@echo -e "$(CYAN)⚡ [PROD] Quick Deploy (no rebuild)...$(NC)"
	@docker stack deploy -c $(COMPOSE_PROD) $(STACK_NAME)

# ============================================================================
# 🌐 PRODUCTION - MONITORING
# ============================================================================

services:
	@echo -e "$(CYAN)� [PROD] Status servizi Swarm...$(NC)"
	@docker stack services $(STACK_NAME) --format "table {{.Name}}\t{{.Replicas}}\t{{.Image}}"

logs:
	@docker service logs $(STACK_NAME)_backend --tail 30
	@docker service logs $(STACK_NAME)_frontend --tail 30

logs-backend:
	@docker service logs $(STACK_NAME)_backend --tail 50 -f

logs-frontend:
	@docker service logs $(STACK_NAME)_frontend --tail 50 -f

health:
	@echo -e "$(CYAN)🏥 [PROD] Health Check...$(NC)"
	@curl -sf $(PROD_BACKEND_URL)/health | head -c 100 && echo ""
	@curl -sf -o /dev/null -w "Frontend: HTTP %{http_code}\n" $(PROD_FRONTEND_URL)

# ============================================================================
# 🗄️  DATABASE - PRODUCTION
# ============================================================================

db-backup:
	@echo -e "$(RED)💾 [PROD] Backup database...$(NC)"
	@bash $(SCRIPTS_DIR)/database/prod/backup.sh

db-seed:
	@echo -e "$(RED)🌱 [PROD] Seeding database...$(NC)"
	@POSTGRES_CONTAINER=$$(docker ps --filter "name=cv-lab-prod_postgres" --format "{{.Names}}" | head -1); \
	docker exec -i "$$POSTGRES_CONTAINER" psql -U cv_lab_prod_user -d cv_lab_prod < $(SCRIPTS_DIR)/deployment/database/seed-production-CLEAN.sql

cleanup-test-users:
	@echo -e "$(RED)🧹 [PROD] Cleanup utenti test...$(NC)"
	@bash $(SCRIPTS_DIR)/database/prod/cleanup-test-users.sh

delete-test-user:
	@echo -e "$(RED)🗑️  [PROD] Elimina utente test...$(NC)"
	@if [ -z "$(EMAIL)" ]; then \
		echo -e "$(RED)❌ Usage: make delete-test-user EMAIL=user@example.com$(NC)"; \
		exit 1; \
	fi
	@bash $(SCRIPTS_DIR)/database/delete-test-user.sh "$(EMAIL)"

# ============================================================================
# 🧪 TEST
# ============================================================================

test: test-backend test-frontend
	@echo -e "$(GREEN)✅ All tests completed!$(NC)"

test-backend:
	@echo -e "$(CYAN)🧪 Backend tests...$(NC)"
	@cd $(APPS_DIR)/backend && uv run pytest --cov=app -q

test-frontend:
	@echo -e "$(CYAN)🧪 Frontend tests...$(NC)"
	@cd $(APPS_DIR)/frontend && pnpm test:coverage

db-reset-users:
	@echo -e "$(RED)⚠️  ATTENZIONE: Elimina TUTTI gli utenti tranne admin su PRODUZIONE!$(NC)"
	@read -p "Confermi? (yes/no): " confirm; \
	if [ "$$confirm" != "yes" ]; then \
		echo -e "$(YELLOW)❌ Operazione annullata$(NC)"; \
		exit 0; \
	fi; \
	echo -e "$(CYAN)🗑️  Connessione a PRODUZIONE (cv-lab)...$(NC)"; \
	ssh cv-lab 'docker exec $$(docker ps -q -f name=cv-lab-prod_postgres) psql -U cv_lab_prod_user -d cv_lab_prod -c " \
		UPDATE tester_invitations SET accepted_by_id = NULL WHERE accepted_by_id IN (SELECT id FROM users WHERE role != '"'"'ADMIN'"'"'); \
		UPDATE tester_invitations SET invited_by_id = NULL WHERE invited_by_id IN (SELECT id FROM users WHERE role != '"'"'ADMIN'"'"'); \
		DELETE FROM tester_invitations WHERE email IN (SELECT email FROM users WHERE role != '"'"'ADMIN'"'"'); \
		DELETE FROM refresh_tokens WHERE user_id IN (SELECT id FROM users WHERE role != '"'"'ADMIN'"'"'); \
		DELETE FROM portfolio_profiles WHERE user_id IN (SELECT id FROM users WHERE role != '"'"'ADMIN'"'"'); \
		DELETE FROM portfolio_experiences WHERE user_id IN (SELECT id FROM users WHERE role != '"'"'ADMIN'"'"'); \
		DELETE FROM portfolio_education WHERE user_id IN (SELECT id FROM users WHERE role != '"'"'ADMIN'"'"'); \
		DELETE FROM portfolio_skills WHERE user_id IN (SELECT id FROM users WHERE role != '"'"'ADMIN'"'"'); \
		DELETE FROM portfolio_languages WHERE user_id IN (SELECT id FROM users WHERE role != '"'"'ADMIN'"'"'); \
		DELETE FROM portfolio_projects WHERE user_id IN (SELECT id FROM users WHERE role != '"'"'ADMIN'"'"'); \
		DELETE FROM portfolio_settings WHERE user_id IN (SELECT id FROM users WHERE role != '"'"'ADMIN'"'"'); \
		DELETE FROM subscriptions WHERE user_id IN (SELECT id FROM users WHERE role != '"'"'ADMIN'"'"'); \
		DELETE FROM users WHERE role != '"'"'ADMIN'"'"'; \
		SELECT id, email, role FROM users; \
	"'; \
	echo -e "$(GREEN)✅ Tutti gli utenti (tranne admin) eliminati da PRODUZIONE!$(NC)"

# ============================================================================
# 🧹 CLEANUP
# ============================================================================

clean:
	@echo -e "$(CYAN)🧹 Cleaning build artifacts...$(NC)"
	@rm -rf $(APPS_DIR)/frontend/dist $(APPS_DIR)/frontend/node_modules/.vite
	@echo -e "$(GREEN)✅ Clean!$(NC)"

clean-docker:
	@echo -e "$(CYAN)🧹 Docker cleanup...$(NC)"
	@docker container prune -f
	@docker image prune -af
	@docker builder prune -af
	@echo -e "$(GREEN)✅ Docker clean!$(NC)"

clean-all:
	@echo -e "$(RED)🧹 PULIZIA COMPLETA SISTEMA$(NC)"
	@echo -e "$(YELLOW)Questo pulirà: Docker, cache, logs, pacchetti orfani$(NC)"
	@read -p "Confermi? (yes/no): " confirm; \
	if [ "$$confirm" != "yes" ]; then \
		echo -e "$(YELLOW)❌ Operazione annullata$(NC)"; \
		exit 0; \
	fi; \
	echo ""; \
	BEFORE=$$(df -h / | tail -1 | awk '{print $$5}'); \
	echo -e "$(CYAN)📊 Disco PRIMA: $$BEFORE$(NC)"; \
	echo ""; \
	echo -e "$(CYAN)1️⃣  Docker system prune...$(NC)"; \
	docker system prune -af --volumes 2>/dev/null || true; \
	echo ""; \
	echo -e "$(CYAN)2️⃣  Cache UV/PIP...$(NC)"; \
	rm -rf ~/.cache/uv ~/.cache/pip 2>/dev/null || true; \
	echo ""; \
	echo -e "$(CYAN)3️⃣  Cache Cypress/Puppeteer...$(NC)"; \
	rm -rf ~/.cache/Cypress ~/.cache/puppeteer 2>/dev/null || true; \
	echo ""; \
	echo -e "$(CYAN)4️⃣  Trash...$(NC)"; \
	rm -rf ~/.local/share/Trash/files/* 2>/dev/null || true; \
	echo ""; \
	echo -e "$(CYAN)5️⃣  PNPM store prune...$(NC)"; \
	pnpm store prune 2>/dev/null || true; \
	echo ""; \
	echo -e "$(CYAN)6️⃣  Pacman cache...$(NC)"; \
	sudo pacman -Sc --noconfirm 2>/dev/null || true; \
	echo ""; \
	echo -e "$(CYAN)7️⃣  Journal logs (2 weeks)...$(NC)"; \
	sudo journalctl --vacuum-time=2weeks 2>/dev/null || true; \
	echo ""; \
	echo -e "$(CYAN)8️⃣  Build artifacts...$(NC)"; \
	find $(PROJECT_ROOT) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true; \
	find $(PROJECT_ROOT) -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true; \
	find $(PROJECT_ROOT) -type d -name "node_modules/.cache" -exec rm -rf {} + 2>/dev/null || true; \
	echo ""; \
	echo -e "$(CYAN)9️⃣  Cache IDE (Codeium, VSCode, Windsurf, Antigravity)...$(NC)"; \
	rm -rf ~/.codeium/windsurf/implicit 2>/dev/null || true; \
	rm -rf ~/.codeium/windsurf/cascade 2>/dev/null || true; \
	rm -rf ~/.codeium/windsurf/cache 2>/dev/null || true; \
	rm -rf ~/.vscode-server/cli 2>/dev/null || true; \
	rm -rf ~/.vscode-server/data/CachedExtensionVSIXs 2>/dev/null || true; \
	rm -rf ~/.vscode-server/data/logs 2>/dev/null || true; \
	rm -rf ~/.windsurf-server/data/CachedExtensionVSIXs 2>/dev/null || true; \
	rm -rf ~/.windsurf-server/data/logs 2>/dev/null || true; \
	rm -rf ~/.antigravity-server/bin 2>/dev/null || true; \
	rm -rf ~/.antigravity-server/data/logs 2>/dev/null || true; \
	rm -rf ~/.npm/_cacache ~/.npm/_npx ~/.npm/_logs 2>/dev/null || true; \
	rm -rf ~/.cache/typescript 2>/dev/null || true; \
	rm -rf ~/.cache/go-build 2>/dev/null || true; \
	rm -rf ~/.cache/node-gyp 2>/dev/null || true; \
	rm -rf ~/.cache/ms-playwright-go 2>/dev/null || true; \
	npm cache clean --force 2>/dev/null || true; \
	echo ""; \
	echo -e "$(CYAN)🔟  Gemini/AI cache e recordings...$(NC)"; \
	rm -rf ~/.gemini/antigravity/browser_recordings 2>/dev/null || true; \
	rm -rf ~/.gemini/antigravity/implicit 2>/dev/null || true; \
	rm -rf ~/.gemini/cache 2>/dev/null || true; \
	echo ""; \
	AFTER=$$(df -h / | tail -1 | awk '{print $$5}'); \
	AVAIL=$$(df -h / | tail -1 | awk '{print $$4}'); \
	echo -e "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"; \
	echo -e "$(GREEN)✅ PULIZIA COMPLETATA!$(NC)"; \
	echo -e "$(CYAN)📊 Disco PRIMA: $$BEFORE → DOPO: $$AFTER$(NC)"; \
	echo -e "$(CYAN)💾 Spazio disponibile: $$AVAIL$(NC)"; \
	echo -e "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"

clean-workflows:
	@echo -e "$(CYAN)🗑️  Pulizia GitHub Actions workflow runs...$(NC)"
	@bash $(SCRIPTS_DIR)/cleanup/clean-workflows.sh
	@echo -e "$(GREEN)✅ Workflow runs puliti!$(NC)"

lint:
	@cd $(APPS_DIR)/frontend && pnpm lint
	@cd $(APPS_DIR)/backend && uv run ruff check .

format:
	@cd $(APPS_DIR)/frontend && pnpm format
	@cd $(APPS_DIR)/backend && uv run ruff format .

# ============================================================================
# 🎯 SHORTCUTS
# ============================================================================

.PHONY: up down ps d b t l
up: up-local
down: down-local
ps: ps-local
l: logs-local
d: deploy
t: test

# ============================================================================
# 🏋️ IRONREP - DOCKER PRODUCTION (config/docker/docker-compose.prod.yml)
# ============================================================================

IRONREP_COMPOSE := $(CONFIG_DIR)/docker/docker-compose.prod.yml
IRONREP_BACKEND_URL := http://localhost:8000
IRONREP_FRONTEND_URL := http://localhost:80

# 🚀 DEPLOY & BUILD
rebuild-backend:
	@echo -e "$(CYAN)🔨 Rebuild Backend Docker...$(NC)"
	@bash $(SCRIPTS_DIR)/deploy/rebuild-backend.sh

rebuild-frontend:
	@echo -e "$(CYAN)🔨 Rebuild Frontend Docker...$(NC)"
	@docker build \
		-f $(CONFIG_DIR)/docker/dockerfiles/frontend.Dockerfile \
		-t ironrep-frontend:latest \
		--build-arg VITE_API_URL= \
		--build-arg VITE_API_BASE_URL=http://backend:8000 \
		--build-arg NODE_ENV=production \
		$(APPS_DIR)/frontend
	@cd $(CONFIG_DIR)/docker && docker-compose -f docker-compose.prod.yml up -d frontend

up-ironrep:
	@echo -e "$(GREEN)🚀 Avvio IronRep PRODUCTION...$(NC)"
	@cd $(CONFIG_DIR)/docker && docker-compose -f docker-compose.prod.yml up -d
	@echo -e "$(GREEN)✅ IronRep avviato!$(NC)"

down-ironrep:
	@echo -e "$(YELLOW)🛑 Stop IronRep...$(NC)"
	@cd $(CONFIG_DIR)/docker && docker-compose -f docker-compose.prod.yml down

ps-ironrep:
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep ironrep

logs-ironrep:
	@cd $(CONFIG_DIR)/docker && docker-compose -f docker-compose.prod.yml logs -f backend

health-ironrep:
	@echo -e "$(CYAN)🏥 IronRep Health Check...$(NC)"
	@curl -sf $(IRONREP_BACKEND_URL)/health 2>/dev/null && echo " ✅" || echo " ❌ Backend DOWN"

# 🤖 AI & LLM
test-llm:
	@echo -e "$(CYAN)🤖 Test LLM Providers...$(NC)"
	@bash $(SCRIPTS_DIR)/deploy/test-llm.sh

test-agents:
	@echo -e "$(CYAN)🧪 Test AI Agents...$(NC)"
	@bash $(SCRIPTS_DIR)/deploy/test-agents.sh

# 🧪 E2E TESTS
test-e2e:
	@echo -e "$(CYAN)🧪 Running E2E Tests...$(NC)"
	@python3 $(SCRIPTS_DIR)/tests/e2e/test_full_system.py

# 📊 QUICK SHORTCUTS
rb: rebuild-backend
tf: test-frontend
te: test-e2e
tl: test-llm
ta: test-agents
hi: health-ironrep
li: logs-ironrep
