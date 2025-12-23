#!/bin/bash
###############################################################################
# ENTERPRISE-GRADE WORKSPACE CLEANUP SCRIPT
# StudioCentos - Technical Debt Reduction Automation
# Version: 1.0
# Date: December 6, 2025
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Workspace root
WORKSPACE_ROOT="/home/autcir_gmail_com/studiocentos_ws"
cd "$WORKSPACE_ROOT"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  STUDIOCENTOS ENTERPRISE CLEANUP SCRIPT                    ║${NC}"
echo -e "${BLUE}║  Phase 1: Critical Issues Remediation                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Confirmation prompt
read -p "This will modify your workspace. Continue? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo -e "${RED}Cleanup cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}[✓] Starting cleanup process...${NC}"
echo ""

###############################################################################
# PHASE 1: BACKUP CURRENT STATE
###############################################################################
echo -e "${BLUE}[1/8] Creating backup...${NC}"
BACKUP_DIR="$WORKSPACE_ROOT/.cleanup_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup critical files
cp .gitignore "$BACKUP_DIR/.gitignore.backup" 2>/dev/null || echo "No .gitignore found"
cp apps/backend/pyproject.toml.poetry.backup "$BACKUP_DIR/" 2>/dev/null || true
cp docs/implementation_plan.md.resolved "$BACKUP_DIR/" 2>/dev/null || true
cp docs/marketing_hub_upgrade_plan.md.resolved "$BACKUP_DIR/" 2>/dev/null || true

echo -e "${GREEN}   Backup created at: $BACKUP_DIR${NC}"
echo ""

###############################################################################
# PHASE 2: UPDATE .gitignore
###############################################################################
echo -e "${BLUE}[2/8] Updating .gitignore...${NC}"

cat >> .gitignore << 'EOF'

# ==============================================================================
# ENTERPRISE CLEANUP - Added $(date +%Y-%m-%d)
# ==============================================================================

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.venv/
venv/
ENV/
env/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

# Build artifacts
dist/
dist-ssr/
*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local
.env.*.local
.env.production

# Logs
logs/
*.log

# Temporary files
*.tmp
*.temp
*.bak
*.backup
*.old

# Test coverage
coverage/
.coverage
htmlcov/
.pytest_cache/
.vitest/

EOF

echo -e "${GREEN}   .gitignore updated${NC}"
echo ""

###############################################################################
# PHASE 3: REMOVE __pycache__ DIRECTORIES
###############################################################################
echo -e "${BLUE}[3/8] Removing Python cache directories...${NC}"

PYCACHE_COUNT=$(find . -type d -name "__pycache__" | wc -l)
if [ "$PYCACHE_COUNT" -gt 0 ]; then
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    echo -e "${GREEN}   Removed $PYCACHE_COUNT __pycache__ directories${NC}"
else
    echo -e "${YELLOW}   No __pycache__ directories found${NC}"
fi
echo ""

###############################################################################
# PHASE 4: REMOVE .pyc FILES
###############################################################################
echo -e "${BLUE}[4/8] Removing compiled Python files...${NC}"

PYC_COUNT=$(find . -name "*.pyc" -o -name "*.pyo" | wc -l)
if [ "$PYC_COUNT" -gt 0 ]; then
    find . \( -name "*.pyc" -o -name "*.pyo" \) -delete
    echo -e "${GREEN}   Removed $PYC_COUNT .pyc/.pyo files${NC}"
else
    echo -e "${YELLOW}   No .pyc/.pyo files found${NC}"
fi
echo ""

###############################################################################
# PHASE 5: ARCHIVE RESOLVED DOCUMENTS
###############################################################################
echo -e "${BLUE}[5/8] Archiving resolved documentation...${NC}"

ARCHIVE_DIR="$WORKSPACE_ROOT/docs/archive/2025-Q4-cleanup"
mkdir -p "$ARCHIVE_DIR"

# Move resolved files
if [ -f "docs/implementation_plan.md.resolved" ]; then
    mv docs/implementation_plan.md.resolved "$ARCHIVE_DIR/"
    echo -e "${GREEN}   Archived: implementation_plan.md.resolved${NC}"
fi

if [ -f "docs/marketing_hub_upgrade_plan.md.resolved" ]; then
    mv docs/marketing_hub_upgrade_plan.md.resolved "$ARCHIVE_DIR/"
    echo -e "${GREEN}   Archived: marketing_hub_upgrade_plan.md.resolved${NC}"
fi

echo ""

###############################################################################
# PHASE 6: HANDLE BACKUP FILES
###############################################################################
echo -e "${BLUE}[6/8] Handling backup files...${NC}"

if [ -f "apps/backend/pyproject.toml.poetry.backup" ]; then
    echo -e "${YELLOW}   Found: pyproject.toml.poetry.backup${NC}"
    echo -e "${YELLOW}   Action: Kept (may be needed for reference)${NC}"
    # Optionally move to archive
    # mv apps/backend/pyproject.toml.poetry.backup "$ARCHIVE_DIR/"
fi

echo ""

###############################################################################
# PHASE 7: GIT CLEANUP (if in git repo)
###############################################################################
echo -e "${BLUE}[7/8] Git repository cleanup...${NC}"

if [ -d ".git" ]; then
    echo -e "${YELLOW}   Removing tracked build artifacts...${NC}"

    # Remove dist from git tracking
    if [ -d "apps/frontend/dist" ]; then
        git rm -r --cached apps/frontend/dist 2>/dev/null || true
        echo -e "${GREEN}   Removed apps/frontend/dist from git tracking${NC}"
    fi

    # Remove __pycache__ from git tracking
    git rm -r --cached **/__pycache__ 2>/dev/null || true

    echo -e "${GREEN}   Git cleanup completed${NC}"
    echo -e "${YELLOW}   Note: You need to commit these changes${NC}"
else
    echo -e "${YELLOW}   Not a git repository, skipping git cleanup${NC}"
fi

echo ""

###############################################################################
# PHASE 8: GENERATE CLEANUP REPORT
###############################################################################
echo -e "${BLUE}[8/8] Generating cleanup report...${NC}"

REPORT_FILE="$WORKSPACE_ROOT/docs/CLEANUP_REPORT_$(date +%Y%m%d_%H%M%S).md"

cat > "$REPORT_FILE" << EOF
# Cleanup Report - $(date +"%Y-%m-%d %H:%M:%S")

## Actions Performed

### 1. Backup Created
- Location: \`$BACKUP_DIR\`
- Files backed up: .gitignore, *.backup, *.resolved

### 2. .gitignore Updated
- Added comprehensive ignore patterns
- Includes: __pycache__, node_modules, dist/, .env*, logs/

### 3. Python Cache Removed
- __pycache__ directories: $PYCACHE_COUNT removed
- .pyc/.pyo files: $PYC_COUNT removed

### 4. Documentation Archived
- Resolved planning docs moved to: \`docs/archive/2025-Q4-cleanup/\`

### 5. Git Cleanup
- Removed dist/ from tracking
- Removed __pycache__ from tracking

## Disk Space Reclaimed
\`\`\`bash
# Run this to see savings:
du -sh $BACKUP_DIR
\`\`\`

## Next Steps

### Immediate (Do Today):
1. Review changes: \`git status\`
2. Test build process
3. Commit cleanup changes:
   \`\`\`bash
   git add .gitignore
   git commit -m "chore: enterprise cleanup - remove build artifacts and cache"
   \`\`\`

### This Week:
1. [ ] Remove unused npm dependencies (see main audit report)
2. [ ] Fix console.log statements in production code
3. [ ] Setup basic test framework

### This Month:
1. [ ] Refactor large files (>50KB)
2. [ ] Implement CI/CD pipeline
3. [ ] Achieve 30% test coverage

## Files to Review Manually

1. \`apps/backend/pyproject.toml.poetry.backup\` - Can this be deleted?
2. \`docs/features/*MARKETING_HUB*.md\` - Consolidate these docs

## Rollback Instructions

If something goes wrong:
\`\`\`bash
# Restore from backup
cp $BACKUP_DIR/* ./ -r

# Or use git
git reset --hard HEAD
git clean -fd
\`\`\`

## Metrics

- Cleanup Duration: \$(date -u -d "\${SECONDS} seconds" +"%M:%S") minutes
- Backup Size: \$(du -sh "$BACKUP_DIR" | cut -f1)
- Files Processed: $((PYCACHE_COUNT + PYC_COUNT))

---

**Cleanup Script Version:** 1.0
**Report Generated:** $(date +"%Y-%m-%d %H:%M:%S")
**Reference:** See ENTERPRISE_CODEBASE_AUDIT_REPORT.md for full analysis
EOF

echo -e "${GREEN}   Report generated: $REPORT_FILE${NC}"
echo ""

###############################################################################
# SUMMARY
###############################################################################
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  CLEANUP COMPLETE                                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓ Backup created:${NC} $BACKUP_DIR"
echo -e "${GREEN}✓ .gitignore updated${NC}"
echo -e "${GREEN}✓ Python cache removed:${NC} $PYCACHE_COUNT directories + $PYC_COUNT files"
echo -e "${GREEN}✓ Documentation archived${NC}"
echo -e "${GREEN}✓ Git cleanup performed${NC}"
echo -e "${GREEN}✓ Report generated:${NC} $REPORT_FILE"
echo ""
echo -e "${YELLOW}⚠ IMPORTANT NEXT STEPS:${NC}"
echo -e "  1. Review changes: ${BLUE}git status${NC}"
echo -e "  2. Test your build process"
echo -e "  3. Commit changes: ${BLUE}git add . && git commit -m 'chore: cleanup'${NC}"
echo -e "  4. Read full report: ${BLUE}docs/ENTERPRISE_CODEBASE_AUDIT_REPORT.md${NC}"
echo ""
echo -e "${GREEN}Thank you for keeping the codebase clean! 🚀${NC}"
echo ""
