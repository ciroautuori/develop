.PHONY: help update backup maintenance clean-all clean-caches clean-docker status
.DEFAULT_GOAL := help

# ============================================================================
# 🎯 ARCH LINUX DAILY MAKEFILE - Personal Workstation
# ============================================================================
# Posizione: ~/Makefile
# Uso: make [comando] oppure con alias: m [comando]
# ============================================================================

# Colors
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
BOLD := \033[1m
NC := \033[0m

# Paths
BACKUP_SCRIPT := /home/ciroautuori/Scrivania/cv-lab/scripts/backup-remote-encrypted.sh
MAINTENANCE_SCRIPT := /home/ciroautuori/Scrivania/cv-lab/scripts/system-maintenance.sh

# ============================================================================
# 📚 HELP
# ============================================================================

help:
	@echo ""
	@echo "╔═══════════════════════════════════════════════════════════════════╗"
	@echo "║      🐧 ARCH LINUX DAILY MAKEFILE - Workstation Commands         ║"
	@echo "╚═══════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo -e "$(BOLD)⬆️  AGGIORNAMENTI$(NC)"
	@echo -e "  $(GREEN)make update$(NC)       - Scarica aggiornamenti AUR (senza installare)"
	@echo -e "  $(GREEN)make upgrade$(NC)      - ⚠️  INSTALLA aggiornamenti (yay -Syu)"
	@echo ""
	@echo -e "$(BOLD)🧹 PULIZIA$(NC)"
	@echo -e "  $(GREEN)make clean-all$(NC)    - Pulizia COMPLETA (Cache, Cestino, Docker, Pacman)"
	@echo -e "  $(GREEN)make clean-caches$(NC) - Solo cache applicazioni e cestino"
	@echo -e "  $(GREEN)make clean-docker$(NC) - Solo Docker prune"
	@echo -e "  $(GREEN)make maintenance$(NC)  - Script manutenzione automatica"
	@echo ""
	@echo -e "$(BOLD)💾 BACKUP$(NC)"
	@echo -e "  $(GREEN)make backup$(NC)       - Backup DB Produzione (Criptato su disco esterno)"
	@echo ""
	@echo -e "$(BOLD)📊 INFO$(NC)"
	@echo -e "  $(GREEN)make status$(NC)       - Stato sistema (Disco, RAM, Servizi)"
	@echo ""

# ============================================================================
# ⬆️  AGGIORNAMENTI
# ============================================================================

update:
	@echo -e "$(GREEN)$(BOLD)⬆️  DOWNLOAD AGGIORNAMENTI (senza installazione)$(NC)"
	@echo -e "$(CYAN)Sincronizzazione database e download pacchetti...$(NC)"
	@yay -Syu --noconfirm
	@echo -e "$(GREEN)✅ Update completato!$(NC)"

# ============================================================================
# 🧹 PULIZIA
# ============================================================================

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

maintenance:
	@echo -e "$(GREEN)🧹 Esecuzione Script Manutenzione...$(NC)"
	@if [ -f "$(MAINTENANCE_SCRIPT)" ]; then \
		bash $(MAINTENANCE_SCRIPT); \
	else \
		echo -e "$(RED)❌ Script non trovato: $(MAINTENANCE_SCRIPT)$(NC)"; \
	fi

# ============================================================================
# 💾 BACKUP
# ============================================================================

backup:
	@echo -e "$(GREEN)💾 Avvio Backup DB Produzione...$(NC)"
	@if [ -f "$(BACKUP_SCRIPT)" ]; then \
		bash $(BACKUP_SCRIPT); \
	else \
		echo -e "$(RED)❌ Script non trovato: $(BACKUP_SCRIPT)$(NC)"; \
	fi

# ============================================================================
# 📊 INFO SISTEMA
# ============================================================================

status:
	@echo -e "$(BOLD)📊 STATO SISTEMA$(NC)"
	@echo ""
	@echo -e "$(CYAN)💾 Spazio Disco:$(NC)"
	@df -h / /home /run/media/ciroautuori/DOCKER 2>/dev/null | grep -v tmpfs || df -h / /home
	@echo ""
	@echo -e "$(CYAN)🧠 Memoria:$(NC)"
	@free -h | head -2
	@echo ""
	@echo -e "$(CYAN)🐳 Docker:$(NC)"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "   Docker non attivo"
	@echo ""
	@echo -e "$(CYAN)📦 Pacchetti da aggiornare:$(NC)"
	@checkupdates 2>/dev/null | wc -l || echo "   0"

# ============================================================================
# 🚀 GIT SUBTREE - Push to App Repos
# ============================================================================

push-all: push-develop push-iss push-studiocentos push-markettina push-ironrep
	@echo -e "$(GREEN)✅ Tutti i push completati!$(NC)"

push-develop:
	@echo -e "$(CYAN)📤 Push develop...$(NC)"
	@git add . && git commit -m "Auto-sync: $$(date +%Y-%m-%d)" 2>/dev/null || true
	@git push origin main
	@echo -e "$(GREEN)✅ develop → origin$(NC)"

push-iss:
	@echo -e "$(CYAN)📤 Push ISS...$(NC)"
	@git subtree push --prefix=apps/iss iss-repo main
	@echo -e "$(GREEN)✅ apps/iss → iss_ws.git$(NC)"

push-studiocentos:
	@echo -e "$(CYAN)📤 Push StudioCentos...$(NC)"
	@git subtree push --prefix=apps/studiocentos studiocentos-repo main
	@echo -e "$(GREEN)✅ apps/studiocentos → studiocentos_ws.git$(NC)"

push-markettina:
	@echo -e "$(CYAN)📤 Push Markettina...$(NC)"
	@git subtree push --prefix=apps/markettina markettina-repo main
	@echo -e "$(GREEN)✅ apps/markettina → markettina.git$(NC)"

push-ironrep:
	@echo -e "$(CYAN)📤 Push IronRep...$(NC)"
	@git subtree push --prefix=apps/ironRep ironrep-repo main
	@echo -e "$(GREEN)✅ apps/ironRep → ironrep.git$(NC)"

