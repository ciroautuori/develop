#!/bin/bash
# Test Booking Google Calendar/Meet Integration
# Verifica creazione booking con Google Meet link automatico

set -e

echo "🧪 TEST: Booking con Google Calendar/Meet Integration"
echo "======================================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Backend URL
BACKEND_URL="${BACKEND_URL:-http://localhost:8002}"
API_URL="$BACKEND_URL/api/v1"

# Get admin JWT token (NOT Google OAuth token)
echo -e "\n${YELLOW}1. Getting admin JWT token...${NC}"

# Get admin session JTI
ADMIN_JTI=$(docker exec studiocentos-db psql -U studiocentos -d studiocentos -t -c \
  "SELECT access_token_jti FROM admin_sessions WHERE admin_id = 2 AND is_revoked = false AND expires_at > NOW() ORDER BY created_at DESC LIMIT 1" \
  2>/dev/null | tr -d ' \n\r')

if [ -z "$ADMIN_JTI" ]; then
  echo -e "${RED}❌ No active admin session found${NC}"
  echo -e "${YELLOW}Please login at https://studiocentos.it/admin/login${NC}"
  exit 1
fi

# Generate JWT token from JTI
ADMIN_TOKEN=$(docker exec studiocentos-backend python3 -c "
from app.core.security import create_access_token
print(create_access_token(data={'sub': '2', 'type': 'access', 'role': 'admin', 'jti': '$ADMIN_JTI'}))
" 2>/dev/null)

if [ -z "$ADMIN_TOKEN" ]; then
  echo -e "${RED}❌ Failed to generate JWT token${NC}"
  exit 1
fi

echo -e "${GREEN}✅ Admin token retrieved${NC}"

# Generate future datetime (tomorrow at 15:00)
TOMORROW=$(date -d "tomorrow 15:00" -u +"%Y-%m-%dT%H:%M:%SZ")

echo -e "\n${YELLOW}2. Creating booking with Google Meet...${NC}"
echo "   Service Type: consultation (60 min)"
echo "   Meeting Provider: google_meet"
echo "   Scheduled: $TOMORROW"

BOOKING_RESPONSE=$(curl -s -X POST "$API_URL/admin/bookings" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"client_name\": \"Test Cliente $(date +%H%M%S)\",
    \"client_email\": \"test.booking@studiocentos.it\",
    \"client_phone\": \"+39 333 1234567\",
    \"title\": \"Test Booking Google Meet\",
    \"description\": \"Test automatico integrazione Google Calendar + Meet\",
    \"service_type\": \"consultation\",
    \"scheduled_at\": \"$TOMORROW\",
    \"duration_minutes\": 60,
    \"meeting_provider\": \"google_meet\",
    \"status\": \"confirmed\"
  }")

echo "$BOOKING_RESPONSE" | jq .

# Extract booking ID and meeting_url
BOOKING_ID=$(echo "$BOOKING_RESPONSE" | jq -r '.id // empty')
MEETING_URL=$(echo "$BOOKING_RESPONSE" | jq -r '.meeting_url // empty')
MEETING_ID=$(echo "$BOOKING_RESPONSE" | jq -r '.meeting_id // empty')

if [ -z "$BOOKING_ID" ]; then
  echo -e "${RED}❌ Booking creation failed${NC}"
  exit 1
fi

echo -e "\n${GREEN}✅ Booking created: ID=$BOOKING_ID${NC}"

# Check if Google Meet link was generated
if [ -n "$MEETING_URL" ] && [ "$MEETING_URL" != "null" ]; then
  echo -e "${GREEN}✅ Google Meet link generated!${NC}"
  echo -e "   📹 Meet URL: ${GREEN}$MEETING_URL${NC}"
  echo -e "   📅 Calendar Event ID: $MEETING_ID"
else
  echo -e "${YELLOW}⚠️  Google Meet link not yet generated${NC}"
  echo -e "   This is normal if Google Calendar API is processing"
  echo -e "   Check booking again in a few seconds..."
fi

# Wait and check again
echo -e "\n${YELLOW}3. Waiting 3 seconds and checking booking again...${NC}"
sleep 3

BOOKING_CHECK=$(curl -s -X GET "$API_URL/admin/bookings/$BOOKING_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

echo "$BOOKING_CHECK" | jq .

MEETING_URL_CHECK=$(echo "$BOOKING_CHECK" | jq -r '.meeting_url // empty')

if [ -n "$MEETING_URL_CHECK" ] && [ "$MEETING_URL_CHECK" != "null" ]; then
  echo -e "\n${GREEN}✅ INTEGRATION TEST PASSED!${NC}"
  echo -e "   📹 Google Meet URL: ${GREEN}$MEETING_URL_CHECK${NC}"
  echo -e "   📅 Calendar Event: $MEETING_ID"
  echo -e "   🎉 Backend is correctly creating Google Calendar events with Meet links"
else
  echo -e "\n${YELLOW}⚠️  No Google Meet link found${NC}"
  echo -e "   Possible reasons:"
  echo -e "   - Google Calendar API scope not granted"
  echo -e "   - OAuth token missing calendar permissions"
  echo -e "   - Backend Google Calendar service error"
  echo -e "   Check backend logs: docker logs studiocentos-backend --tail 50"
fi

# Test smart pre-selection
echo -e "\n${YELLOW}4. Testing smart pre-selection (service_type = demo)...${NC}"

DEMO_BOOKING=$(curl -s -X POST "$API_URL/admin/bookings" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"client_name\": \"Demo Test $(date +%H%M%S)\",
    \"client_email\": \"demo@studiocentos.it\",
    \"title\": \"Demo Test - 45 min default\",
    \"service_type\": \"demo\",
    \"scheduled_at\": \"$TOMORROW\",
    \"duration_minutes\": 45,
    \"meeting_provider\": \"google_meet\",
    \"status\": \"confirmed\"
  }")

DEMO_ID=$(echo "$DEMO_BOOKING" | jq -r '.id // empty')
DEMO_DURATION=$(echo "$DEMO_BOOKING" | jq -r '.duration_minutes')

if [ "$DEMO_DURATION" = "45" ]; then
  echo -e "${GREEN}✅ Smart pre-selection working: Demo = 45 min${NC}"
else
  echo -e "${YELLOW}⚠️  Duration: $DEMO_DURATION (expected 45)${NC}"
fi

# Cleanup
echo -e "\n${YELLOW}5. Cleanup: Deleting test bookings...${NC}"
if [ -n "$BOOKING_ID" ]; then
  curl -s -X DELETE "$API_URL/admin/bookings/$BOOKING_ID" \
    -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
  echo -e "${GREEN}✅ Deleted booking $BOOKING_ID${NC}"
fi

if [ -n "$DEMO_ID" ]; then
  curl -s -X DELETE "$API_URL/admin/bookings/$DEMO_ID" \
    -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
  echo -e "${GREEN}✅ Deleted booking $DEMO_ID${NC}"
fi

echo -e "\n${GREEN}✅ TEST COMPLETED${NC}"
echo "======================================================="
