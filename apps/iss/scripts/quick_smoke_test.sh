#!/bin/bash

# 🧪 ISS QUICK SMOKE TEST - Test essenziali con dati reali
# Test rapido dei componenti critici

set -e

BASE_URL="http://localhost:8000"
API_URL="$BASE_URL/api/v1"

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

log_test() {
    local name="$1"
    local status="$2"
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ $name${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ $name${NC}"
        ((TESTS_FAILED++))
    fi
}

echo "🚀 ISS Quick Smoke Test"
echo "======================="

# 1. Health Check
echo "🏥 Testing Health..."
health_response=$(curl -s "$BASE_URL/health")
if echo "$health_response" | grep -q "healthy"; then
    log_test "Backend Health Check" "PASS"
else
    log_test "Backend Health Check" "FAIL"
fi

# 2. Bandi API
echo "📋 Testing Bandi API..."
bandi_response=$(curl -s "$API_URL/bandi/")
if echo "$bandi_response" | grep -q "items"; then
    log_test "Bandi List API" "PASS"
    
    # Count bandi
    bandi_count=$(echo "$bandi_response" | jq -r '.total // 0')
    echo "   📊 Found $bandi_count bandi in database"
else
    log_test "Bandi List API" "FAIL"
fi

# 3. Bandi Stats
echo "📊 Testing Bandi Stats..."
stats_response=$(curl -s "$API_URL/bandi/stats")
if echo "$stats_response" | grep -q "total_bandi"; then
    log_test "Bandi Stats API" "PASS"
    
    # Show stats
    total=$(echo "$stats_response" | jq -r '.total_bandi // 0')
    attivi=$(echo "$stats_response" | jq -r '.bandi_attivi // 0')
    echo "   📈 Total: $total, Active: $attivi"
else
    log_test "Bandi Stats API" "FAIL"
fi

# 4. Search Functionality
echo "🔍 Testing Search..."
search_response=$(curl -s "$API_URL/bandi/?query=test&limit=5")
if echo "$search_response" | grep -q "items"; then
    log_test "Bandi Search API" "PASS"
    
    search_count=$(echo "$search_response" | jq -r '.items | length')
    echo "   🔍 Search returned $search_count results"
else
    log_test "Bandi Search API" "FAIL"
fi

# 5. Filter by Source
echo "🏛️ Testing Filters..."
filter_response=$(curl -s "$API_URL/bandi/?fonte=comune_salerno")
if echo "$filter_response" | grep -q "items"; then
    log_test "Bandi Filter API" "PASS"
    
    filter_count=$(echo "$filter_response" | jq -r '.items | length')
    echo "   🏛️ Filter returned $filter_count results from Comune Salerno"
else
    log_test "Bandi Filter API" "FAIL"
fi

# 6. Performance Test
echo "⚡ Testing Performance..."
start_time=$(date +%s.%N)
for i in {1..5}; do
    curl -s "$API_URL/bandi/?limit=1" > /dev/null
done
end_time=$(date +%s.%N)
duration=$(echo "$end_time - $start_time" | bc)

if (( $(echo "$duration < 3.0" | bc -l) )); then
    log_test "Performance Test (5 requests)" "PASS"
    echo "   ⚡ Completed in ${duration}s"
else
    log_test "Performance Test (5 requests)" "FAIL"
    echo "   ⚠️ Too slow: ${duration}s"
fi

# 7. Test User Registration (if auth endpoints exist)
echo "👤 Testing User System..."
auth_health=$(curl -s "$API_URL/auth/health" 2>/dev/null)
if echo "$auth_health" | grep -q "healthy"; then
    log_test "Auth System Health" "PASS"
    
    # Test registration with unique email
    test_email="smoketest_$(date +%s)@example.com"
    register_data='{
      "email": "'$test_email'",
      "password": "SmokeTest2025!",
      "nome": "Test",
      "cognome": "Smoke",
      "role": "cittadino",
      "accessibility_needs": "none",
      "privacy_policy_accepted": true
    }'
    
    register_response=$(curl -s -X POST "$API_URL/auth/register" \
                        -H "Content-Type: application/json" \
                        -d "$register_data")
    
    if echo "$register_response" | grep -q "email"; then
        log_test "User Registration" "PASS"
        echo "   👤 Created test user: $test_email"
    else
        log_test "User Registration" "FAIL"
        echo "   ❌ Registration failed: $register_response"
    fi
else
    log_test "Auth System Health" "FAIL"
    echo "   ⚠️ Auth endpoints not available"
fi

# RISULTATI FINALI
echo ""
echo "======================="
echo "🎯 SMOKE TEST RESULTS"
echo "======================="
echo -e "✅ Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "❌ Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL CORE SYSTEMS WORKING!${NC}"
    echo ""
    echo "🚀 Sistema ISS è operativo e pronto per:"
    echo "   📋 Ricerca e filtro bandi"
    echo "   📊 Statistiche in tempo reale"
    echo "   👤 Registrazione utenti"
    echo "   ⚡ Performance ottimali"
    echo ""
    echo "🌐 Accesso: http://localhost:3000"
    echo "📚 API Docs: http://localhost:8000/docs"
    exit 0
else
    echo -e "${RED}⚠️ Some systems need attention${NC}"
    exit 1
fi
