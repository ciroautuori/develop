#!/bin/bash
# 🧪 IronRep Test All Agents
# Usage: ./scripts/deploy/test-agents.sh

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🧪 IRONREP AI AGENTS TEST                                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"

BASE="http://localhost:8000/api"

# Check backend health
echo ""
echo "📡 Checking backend health..."
if ! curl -sf http://localhost:8000/health > /dev/null; then
    echo "❌ Backend not running! Run: make rebuild-backend"
    exit 1
fi
echo "✅ Backend healthy"

# Test endpoints
echo ""
echo "📦 Testing API endpoints..."

echo -n "  - Exercises: "
if curl -sf "$BASE/exercises/" > /dev/null; then
    COUNT=$(curl -s "$BASE/exercises/" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
    echo "✅ $COUNT found"
else
    echo "❌ Failed"
fi

echo -n "  - Foods (FatSecret): "
FOOD=$(curl -s "$BASE/foods/search?q=pollo&limit=1")
if [[ $? -eq 0 && "$FOOD" != "[]" ]]; then
    NAME=$(echo "$FOOD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0].get('name','?'))" 2>/dev/null)
    echo "✅ Found: $NAME"
else
    echo "❌ Failed"
fi

echo -n "  - Auth (login): "
if curl -sf -X POST "$BASE/auth/login" -d "username=test@test.com&password=wrong" > /dev/null 2>&1; then
    echo "✅ Endpoint works"
elif [[ $? -eq 22 ]]; then
    echo "✅ Endpoint works (401 expected)"
else
    echo "❌ Failed"
fi

echo ""
echo "🤖 Testing AI Agents (requires auth)..."
echo "   NOTE: Create a test user first to test agents with authentication"

echo ""
echo "✅ TEST COMPLETE!"
