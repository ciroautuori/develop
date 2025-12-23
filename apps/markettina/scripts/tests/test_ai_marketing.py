#!/usr/bin/env python3
"""
Test script per gli endpoint AI Marketing con GROQ
Testa le funzionalità implementate negli agenti AI perfezionati
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001"  # AI Microservice
API_KEY = "markettina-ai-prod-key-2025-secure"  # Default dev key

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

async def test_content_generation():
    """Test content generation endpoints"""
    print("🎯 Testing Content Generation with GROQ...")

    test_cases = [
        {
            "type": "blog",
            "topic": "Sviluppo AI personalizzato per PMI italiane",
            "tone": "professionale"
        },
        {
            "type": "social",
            "topic": "Nuova app mobile React Native",
            "tone": "entusiasta",
            "platform": "linkedin"
        },
        {
            "type": "ad",
            "topic": "Consulenza gratuita sviluppo software",
            "tone": "persuasivo"
        },
        {
            "type": "video",
            "topic": "Come l'AI trasforma il business",
            "tone": "friendly"
        }
    ]

    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test {i}: {test_case['type']} content ---")

            try:
                async with session.post(
                    f"{BASE_URL}/api/v1/marketing/content/generate",
                    headers=HEADERS,
                    json=test_case
                ) as response:

                    print(f"Status: {response.status}")

                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Success!")
                        print(f"Provider: {data.get('provider', 'unknown')}")
                        print(f"Content length: {len(data.get('content', ''))} chars")
                        print(f"Content preview: {data.get('content', '')[:200]}...")
                    else:
                        error = await response.text()
                        print(f"❌ Failed: {error}")

            except Exception as e:
                print(f"❌ Error: {e}")

async def test_ai_microservice_health():
    """Test AI microservice health and availability"""
    print("🏥 Testing AI Microservice Health...")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/health") as response:
                print(f"Health status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ AI Microservice is healthy")
                    print(f"Details: {json.dumps(data, indent=2)}")
                else:
                    print(f"❌ Health check failed")
        except Exception as e:
            print(f"❌ Cannot reach AI Microservice: {e}")

async def test_groq_integration():
    """Test direct GROQ integration"""
    print("🚀 Testing GROQ Integration...")

    # Test GROQ client directly through support endpoint (uses GROQ)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/support/chat",
                headers=HEADERS,
                json={
                    "message": "Ciao, come funziona l'AI marketing di markettina?",
                    "context": "",
                    "provider": "groq"
                }
            ) as response:

                print(f"GROQ Chat Status: {response.status}")

                if response.status == 200:
                    data = await response.json()
                    print(f"✅ GROQ is working!")
                    print(f"Provider: {data.get('provider', 'unknown')}")
                    print(f"Response: {data.get('response', '')[:300]}...")
                    print(f"Processing time: {data.get('processing_time', 0)}ms")
                else:
                    error = await response.text()
                    print(f"❌ GROQ test failed: {error}")

        except Exception as e:
            print(f"❌ GROQ test error: {e}")

def print_results_summary():
    """Print test results summary"""
    print("\n" + "="*60)
    print("📊 AI MARKETING ENDPOINTS - TEST SUMMARY")
    print("="*60)
    print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Endpoints tested:")
    print(f"   • GET  /health - AI Microservice health")
    print(f"   • POST /api/v1/marketing/content/generate - Content generation")
    print(f"   • POST /api/v1/support/chat - GROQ integration test")
    print(f"\n💡 Next steps:")
    print(f"   1. Check Docker containers: docker-compose ps")
    print(f"   2. View logs: docker-compose logs ai_microservice")
    print(f"   3. Test social publishing after Meta tokens setup")

async def main():
    """Main test runner"""
    print("🤖 AI MARKETING ENDPOINTS TESTING")
    print("="*50)

    # Test sequence
    await test_ai_microservice_health()
    await test_groq_integration()
    await test_content_generation()

    # Summary
    print_results_summary()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
