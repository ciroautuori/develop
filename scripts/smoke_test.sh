#!/bin/bash

# 🧪 ISS SMOKE TEST - Test completo sistema con dati reali
# Testa tutti gli endpoint critici con curl e dati reali

# set -e  # Exit on any error (DISABLED FOR DEBUG)

# Configurazione
BASE_URL="http://localhost:8001"
API_URL="$BASE_URL/api/v1"

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contatori
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Funzioni utility
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local headers="$5"
    local expected_status="$6"

    ((TESTS_TOTAL++))

    log_info "Testing: $name"

    if [ -z "$data" ]; then
        if [[ "$endpoint" == "/health" || "$endpoint" == "/auth/health" ]]; then
            # Health checks are often on base URL or specific auth path
            response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint" $headers)
        else
            response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" $headers)
        fi
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
                   -H "Content-Type: application/json" \
                   $headers \
                   -d "$data")
    fi

    # Estrai status code (ultima riga)
    status_code=$(echo "$response" | tail -n1)
    # Estrai body (tutto tranne ultima riga)
    body=$(echo "$response" | head -n -1)

    if [ "$status_code" = "$expected_status" ]; then
        log_success "$name - Status: $status_code"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        log_error "$name - Expected: $expected_status, Got: $status_code"
        echo "Response: $body"
    fi

    echo "----------------------------------------"
}

# Variabili globali per token
ADMIN_TOKEN=""
APS_TOKEN=""
CITIZEN_TOKEN=""

echo "🚀 Starting ISS Smoke Test Suite"
echo "========================================"

# 1. HEALTH CHECKS
log_info "🏥 HEALTH CHECKS"

test_endpoint "Backend Health" "GET" "/health" "" "" "200"
test_endpoint "Auth Health" "GET" "/auth/health" "" "" "200"

# 2. SISTEMA BANDI (PUBBLICO)
log_info "📋 SISTEMA BANDI - ENDPOINTS PUBBLICI"

test_endpoint "Bandi List" "GET" "/bandi/" "" "" "200"
test_endpoint "Bandi Stats" "GET" "/bandi/stats" "" "" "200"
test_endpoint "Bandi Search" "GET" "/bandi/?query=test&limit=5" "" "" "200"
test_endpoint "Bandi Filter by Source" "GET" "/bandi/?fonte=comune_salerno" "" "" "200"

# 3. REGISTRAZIONE UTENTE
log_info "👤 REGISTRAZIONE NUOVO UTENTE"

# Genera email unica per test
TEST_EMAIL="smoketest_$(date +%s)@example.com"

REGISTER_DATA='{
  "email": "'$TEST_EMAIL'",
  "password": "SmokeTest2025!",
  "nome": "Test",
  "cognome": "Smoke",
  "role": "cittadino",
  "accessibility_needs": "none",
  "privacy_policy_accepted": true,
  "newsletter_subscription": true
}'

test_endpoint "User Registration" "POST" "/auth/register" "$REGISTER_DATA" "" "200"

# 4. LOGIN UTENTI TEST
log_info "🔐 LOGIN UTENTI DI TEST"

# Login Admin
ADMIN_LOGIN='{
  "email": "admin@iss.salerno.it",
  "password": "AdminISS2025!"
}'

admin_response=$(curl -s -X POST "$API_URL/auth/login" \
                 -H "Content-Type: application/json" \
                 -d "$ADMIN_LOGIN")

if echo "$admin_response" | jq -e '.access_token' > /dev/null 2>&1; then
    ADMIN_TOKEN=$(echo "$admin_response" | jq -r '.access_token')
    log_success "Admin Login - Token obtained"
    ((TESTS_PASSED++))
else
    log_error "Admin Login Failed"
    echo "Response: $admin_response"
    ((TESTS_FAILED++))
fi
((TESTS_TOTAL++))

# Login APS Responsabile
APS_LOGIN='{
  "email": "responsabile@aps-esempio.it",
  "password": "ApsResp2025!"
}'

aps_response=$(curl -s -X POST "$API_URL/auth/login" \
               -H "Content-Type: application/json" \
               -d "$APS_LOGIN")

if echo "$aps_response" | jq -e '.access_token' > /dev/null 2>&1; then
    APS_TOKEN=$(echo "$aps_response" | jq -r '.access_token')
    log_success "APS Login - Token obtained"
    ((TESTS_PASSED++))
else
    log_error "APS Login Failed"
    echo "Response: $aps_response"
    ((TESTS_FAILED++))
fi
((TESTS_TOTAL++))

# Login Cittadino
CITIZEN_LOGIN='{
  "email": "cittadino@example.com",
  "password": "Cittadino2025!"
}'

citizen_response=$(curl -s -X POST "$API_URL/auth/login" \
                   -H "Content-Type: application/json" \
                   -d "$CITIZEN_LOGIN")

if echo "$citizen_response" | jq -e '.access_token' > /dev/null 2>&1; then
    CITIZEN_TOKEN=$(echo "$citizen_response" | jq -r '.access_token')
    log_success "Citizen Login - Token obtained"
    ((TESTS_PASSED++))
else
    log_error "Citizen Login Failed"
    echo "Response: $citizen_response"
    ((TESTS_FAILED++))
fi
((TESTS_TOTAL++))

# 5. ENDPOINTS AUTENTICATI - PROFILO UTENTE
log_info "👤 PROFILO UTENTE AUTENTICATO"

if [ -n "$ADMIN_TOKEN" ]; then
    test_endpoint "Admin Profile" "GET" "/auth/me" "" "-H \"Authorization: Bearer $ADMIN_TOKEN\"" "200"
    test_endpoint "Admin Full Profile" "GET" "/users/me" "" "-H \"Authorization: Bearer $ADMIN_TOKEN\"" "200"
fi

if [ -n "$APS_TOKEN" ]; then
    test_endpoint "APS Profile" "GET" "/auth/me" "" "-H \"Authorization: Bearer $APS_TOKEN\"" "200"
    test_endpoint "APS Preferences" "GET" "/users/me/preferences" "" "-H \"Authorization: Bearer $APS_TOKEN\"" "200"
fi

if [ -n "$CITIZEN_TOKEN" ]; then
    test_endpoint "Citizen Profile" "GET" "/auth/me" "" "-H \"Authorization: Bearer $CITIZEN_TOKEN\"" "200"
    test_endpoint "Citizen Activity" "GET" "/users/me/activity" "" "-H \"Authorization: Bearer $CITIZEN_TOKEN\"" "200"
fi

# 6. ADMIN ENDPOINTS
log_info "⚙️  ADMIN ENDPOINTS"

if [ -n "$ADMIN_TOKEN" ]; then
    test_endpoint "Users List" "GET" "/users/?limit=10" "" "-H \"Authorization: Bearer $ADMIN_TOKEN\"" "200"
    test_endpoint "User Statistics" "GET" "/users/stats" "" "-H \"Authorization: Bearer $ADMIN_TOKEN\"" "200"
    test_endpoint "APS Organizations" "GET" "/users/aps/organizations" "" "-H \"Authorization: Bearer $ADMIN_TOKEN\"" "200"
    test_endpoint "Accessibility Users" "GET" "/users/accessibility/users" "" "-H \"Authorization: Bearer $ADMIN_TOKEN\"" "200"
    test_endpoint "Accessibility Stats" "GET" "/users/accessibility/stats" "" "-H \"Authorization: Bearer $ADMIN_TOKEN\"" "200"
fi

# 7. UPDATE PROFILO
log_info "✏️  UPDATE PROFILO UTENTE"

if [ -n "$CITIZEN_TOKEN" ]; then
    UPDATE_PROFILE='{
      "bio": "Profilo aggiornato durante smoke test",
      "telefono": "+39 089 999999"
    }'

    test_endpoint "Update Profile" "PUT" "/users/me" "$UPDATE_PROFILE" "-H \"Authorization: Bearer $CITIZEN_TOKEN\"" "200"
fi

# 8. PREFERENZE UTENTE
log_info "⚙️  PREFERENZE UTENTE"

if [ -n "$CITIZEN_TOKEN" ]; then
    UPDATE_PREFS='{
      "theme": "dark",
      "font_size": "large",
      "notify_new_bandi": true,
      "alert_frequency": "weekly"
    }'

    test_endpoint "Update Preferences" "PUT" "/users/me/preferences" "$UPDATE_PREFS" "-H \"Authorization: Bearer $CITIZEN_TOKEN\"" "200"
fi

# 9. BANDI CON AUTENTICAZIONE
log_info "📋 BANDI CON UTENTE AUTENTICATO"

if [ -n "$APS_TOKEN" ]; then
    test_endpoint "Bandi as APS User" "GET" "/bandi/?limit=5" "" "-H \"Authorization: Bearer $APS_TOKEN\"" "200"
fi

# 10. CAMBIO PASSWORD
log_info "🔑 CAMBIO PASSWORD"

if [ -n "$CITIZEN_TOKEN" ]; then
    CHANGE_PASSWORD='{
      "current_password": "Cittadino2025!",
      "new_password": "NuovaPassword2025!"
    }'

    test_endpoint "Change Password" "POST" "/users/me/change-password" "$CHANGE_PASSWORD" "-H \"Authorization: Bearer $CITIZEN_TOKEN\"" "200"

    # Test login con nuova password
    NEW_LOGIN='{
      "email": "cittadino@example.com",
      "password": "NuovaPassword2025!"
    }'

    test_endpoint "Login with New Password" "POST" "/auth/login" "$NEW_LOGIN" "" "200"
fi

# 11. LOGOUT
log_info "🚪 LOGOUT"

if [ -n "$CITIZEN_TOKEN" ]; then
    test_endpoint "User Logout" "POST" "/auth/logout" "" "-H \"Authorization: Bearer $CITIZEN_TOKEN\"" "200"
fi

# 12. PERFORMANCE TEST
log_info "⚡ PERFORMANCE TEST"

log_info "Testing concurrent requests..."
start_time=$(date +%s.%N)

# 10 richieste concorrenti
for i in {1..10}; do
    curl -s "$API_URL/bandi/?limit=1" > /dev/null &
done
wait

end_time=$(date +%s.%N)
# Usa python per il calcolo floating point se bc non c'è
duration=$(python3 -c "print($end_time - $start_time)")

if (( $(python3 -c "print(1 if $duration < 5.0 else 0)") )); then
    log_success "Performance Test - 10 concurrent requests in ${duration}s"
    ((TESTS_PASSED++))
else
    log_error "Performance Test - Too slow: ${duration}s"
    ((TESTS_FAILED++))
fi
((TESTS_TOTAL++))

# 13. ACCESSIBILITY TEST
log_info "♿ ACCESSIBILITY TEST"

# Login utente con screen reader
ACCESS_LOGIN='{
  "email": "accessibile@example.com",
  "password": "Access2025!"
}'

access_response=$(curl -s -X POST "$API_URL/auth/login" \
                  -H "Content-Type: application/json" \
                  -d "$ACCESS_LOGIN")

if echo "$access_response" | jq -e '.access_token' > /dev/null 2>&1; then
    ACCESS_TOKEN=$(echo "$access_response" | jq -r '.access_token')

    # Verifica che il profilo mostri esigenze di accessibilità
    profile_response=$(curl -s -X GET "$API_URL/auth/me" \
                       -H "Authorization: Bearer $ACCESS_TOKEN")

    if echo "$profile_response" | jq -e '.accessibility_needs' | grep -q "screen_reader"; then
        log_success "Accessibility User Profile - Screen reader needs detected"
        ((TESTS_PASSED++))
    else
        log_error "Accessibility User Profile - Screen reader needs not detected"
        ((TESTS_FAILED++))
    fi
else
    log_error "Accessibility User Login Failed"
    ((TESTS_FAILED++))
fi
((TESTS_TOTAL++))

# RIEPILOGO FINALE
echo ""
echo "========================================"
echo "🎯 SMOKE TEST RESULTS"
echo "========================================"
echo -e "📊 Total Tests: ${BLUE}$TESTS_TOTAL${NC}"
echo -e "✅ Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "❌ Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Sistema ISS is ready for production!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Check the output above.${NC}"
    exit 1
fi
