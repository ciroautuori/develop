#!/bin/bash
#
# 🧪 IronRep Complete E2E Test Runner
# ====================================
# Esegue TUTTI i test E2E in sequenza
#
# Usage:
#   ./scripts/tests/run_all_e2e.sh           # Run all tests
#   ./scripts/tests/run_all_e2e.sh --api     # Only API tests
#   ./scripts/tests/run_all_e2e.sh --browser # Only browser tests
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
E2E_DIR="$SCRIPT_DIR/e2e"
REPORT_DIR="$SCRIPT_DIR/test-reports"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          🧪 IRONREP COMPLETE E2E TEST SUITE                  ║"
echo "║          $(date '+%Y-%m-%d %H:%M:%S')                                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Create report directory
mkdir -p "$REPORT_DIR"

# Track results
API_PASSED=0
BROWSER_PASSED=0
TOTAL_FAILED=0

# =============================================================================
# API TESTS
# =============================================================================
run_api_tests() {
    echo -e "\n${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}📡 PHASE 1: API TESTS (test_full_system.py)${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}\n"

    if python3 "$E2E_DIR/test_full_system.py"; then
        API_PASSED=1
        echo -e "\n${GREEN}✅ API Tests PASSED${NC}"
    else
        TOTAL_FAILED=$((TOTAL_FAILED + 1))
        echo -e "\n${RED}❌ API Tests FAILED${NC}"
    fi
}

# =============================================================================
# BROWSER TESTS (requires playwright)
# =============================================================================
run_browser_tests() {
    echo -e "\n${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}🌐 PHASE 2: BROWSER TESTS (test_browser_real_user.py)${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}\n"

    # Check if playwright is installed
    if ! python3 -c "import playwright" 2>/dev/null; then
        echo -e "${YELLOW}⚠️ Playwright not installed. Installing...${NC}"
        pip install playwright
        playwright install chromium
    fi

    if python3 "$E2E_DIR/test_browser_real_user.py"; then
        BROWSER_PASSED=1
        echo -e "\n${GREEN}✅ Browser Tests PASSED${NC}"
    else
        TOTAL_FAILED=$((TOTAL_FAILED + 1))
        echo -e "\n${RED}❌ Browser Tests FAILED${NC}"
    fi
}

# =============================================================================
# WIZARD TESTS
# =============================================================================
run_wizard_tests() {
    echo -e "\n${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}🧙 PHASE 3: WIZARD FLOW TESTS${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}\n"

    if python3 "$E2E_DIR/test_wizard_flow.py"; then
        echo -e "\n${GREEN}✅ Wizard Tests PASSED${NC}"
    else
        TOTAL_FAILED=$((TOTAL_FAILED + 1))
        echo -e "\n${RED}❌ Wizard Tests FAILED${NC}"
    fi
}

# =============================================================================
# MAIN
# =============================================================================

case "${1:-all}" in
    --api)
        run_api_tests
        ;;
    --browser)
        run_browser_tests
        ;;
    --wizard)
        run_wizard_tests
        ;;
    all|*)
        run_api_tests
        run_browser_tests
        run_wizard_tests
        ;;
esac

# =============================================================================
# SUMMARY
# =============================================================================
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📊 FINAL SUMMARY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

if [ $TOTAL_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ ALL TESTS PASSED!${NC}\n"
    exit 0
else
    echo -e "\n${RED}❌ $TOTAL_FAILED test suite(s) FAILED${NC}"
    echo -e "${YELLOW}📄 Check reports in: $REPORT_DIR${NC}\n"
    exit 1
fi
