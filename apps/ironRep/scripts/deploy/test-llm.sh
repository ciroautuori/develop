#!/bin/bash
# 🔍 IronRep Test LLM Providers
# Usage: ./scripts/deploy/test-llm.sh

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🤖 IRONREP LLM PROVIDERS TEST                               ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# Load .env.prod
if [[ -f "config/docker/.env.prod" ]]; then
    source config/docker/.env.prod 2>/dev/null || true
fi

echo ""
echo "🔵 Testing GROQ..."
GROQ_KEY=$(echo "$GROQ_API_KEY" | cut -d',' -f1)
if [[ -n "$GROQ_KEY" ]]; then
    RESPONSE=$(curl -s -X POST "https://api.groq.com/openai/v1/chat/completions" \
        -H "Authorization: Bearer $GROQ_KEY" \
        -H "Content-Type: application/json" \
        -d '{"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":"Say OK"}],"max_tokens":5}' 2>/dev/null)

    if echo "$RESPONSE" | grep -q "choices"; then
        echo "  ✅ GROQ: Working!"
    else
        echo "  ❌ GROQ: Failed - $(echo $RESPONSE | head -c 100)"
    fi
else
    echo "  ⚠️ GROQ_API_KEY not set"
fi

echo ""
echo "🟣 Testing OpenRouter..."
if [[ -n "$OPENROUTER_API_KEY" ]]; then
    RESPONSE=$(curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
        -H "Authorization: Bearer $OPENROUTER_API_KEY" \
        -H "Content-Type: application/json" \
        -H "HTTP-Referer: https://ironrep.it" \
        -d '{"model":"meta-llama/llama-3.2-3b-instruct:free","messages":[{"role":"user","content":"Say OK"}],"max_tokens":5}' 2>/dev/null)

    if echo "$RESPONSE" | grep -q "choices"; then
        echo "  ✅ OpenRouter: Working!"
    else
        echo "  ❌ OpenRouter: Failed - $(echo $RESPONSE | head -c 100)"
    fi
else
    echo "  ⚠️ OPENROUTER_API_KEY not set"
fi

echo ""
echo "🟢 Testing Google Gemini..."
if [[ -n "$GOOGLE_API_KEY" ]]; then
    RESPONSE=$(curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$GOOGLE_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"contents":[{"parts":[{"text":"Say OK"}]}]}' 2>/dev/null)

    if echo "$RESPONSE" | grep -q "candidates"; then
        echo "  ✅ Gemini: Working!"
    elif echo "$RESPONSE" | grep -q "expired"; then
        echo "  ❌ Gemini: API key expired"
    else
        echo "  ❌ Gemini: Failed - $(echo $RESPONSE | head -c 100)"
    fi
else
    echo "  ⚠️ GOOGLE_API_KEY not set"
fi

echo ""
echo "✅ TEST COMPLETE"
