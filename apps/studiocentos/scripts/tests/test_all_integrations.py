"""
Test Script - Verifica Completa Tutte le Integrazioni
Testa: Google, Meta/Facebook, Instagram, Calendario Editoriale
"""

import asyncio
import sys
import os
import httpx
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings


async def test_meta_facebook():
    """Test Meta/Facebook API connectivity."""
    print("\n📘 Testing Facebook/Meta Integration...")

    if not settings.META_ACCESS_TOKEN:
        print("❌ META_ACCESS_TOKEN not configured")
        return False

    try:
        async with httpx.AsyncClient() as client:
            # Test Page access
            response = await client.get(
                f"https://graph.facebook.com/v18.0/{settings.FACEBOOK_PAGE_ID}",
                params={
                    "fields": "name,fan_count,about",
                    "access_token": settings.META_ACCESS_TOKEN
                },
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Facebook Page Connected: {data.get('name')}")
                print(f"   Fan Count: {data.get('fan_count', 'N/A')}")
                return True
            else:
                print(f"❌ Facebook API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Facebook Connection Error: {str(e)}")
        return False


async def test_instagram():
    """Test Instagram Business API connectivity."""
    print("\n📸 Testing Instagram Integration...")

    if not settings.INSTAGRAM_ACCESS_TOKEN:
        print("❌ INSTAGRAM_ACCESS_TOKEN not configured")
        return False

    try:
        async with httpx.AsyncClient() as client:
            # Test IG account access
            response = await client.get(
                f"https://graph.facebook.com/v18.0/{settings.INSTAGRAM_ACCOUNT_ID}",
                params={
                    "fields": "username,followers_count,media_count",
                    "access_token": settings.INSTAGRAM_ACCESS_TOKEN
                },
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Instagram Connected: @{data.get('username')}")
                print(f"   Followers: {data.get('followers_count', 'N/A')}")
                print(f"   Media Count: {data.get('media_count', 'N/A')}")
                return True
            else:
                print(f"❌ Instagram API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Instagram Connection Error: {str(e)}")
        return False


async def test_google_analytics():
    """Test Google Analytics connectivity."""
    print("\n📊 Testing Google Analytics...")

    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.domain.auth.oauth_tokens import OAuthTokenService, OAuthProvider

        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        admin_id = 1
        token = OAuthTokenService.get_valid_token(db, admin_id, OAuthProvider.GOOGLE)

        if not token:
            print("❌ No valid Google Token found")
            return False

        print("✅ Google OAuth Token: Valid")

        # Try to fetch accounts
        from app.domain.google.analytics_service import GoogleAnalyticsService

        ga_service = GoogleAnalyticsService(access_token=token)
        accounts = await ga_service.list_accounts()

        print(f"✅ Google Analytics Connected: {len(accounts)} accounts found")
        if accounts:
            print(f"   First Account: {accounts[0].get('displayName')}")

        db.close()
        return True

    except Exception as e:
        print(f"❌ Google Analytics Error: {str(e)}")
        return False


async def test_backend_api():
    """Test Backend API availability."""
    print("\n🔧 Testing Backend API...")

    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            response = await client.get(
                "http://localhost:8002/health",
                timeout=5.0
            )

            if response.status_code == 200:
                print("✅ Backend API: Healthy")
                return True
            else:
                print(f"⚠️ Backend API: Status {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Backend API Error: {str(e)}")
        return False


async def test_ai_microservice():
    """Test AI Microservice availability."""
    print("\n🤖 Testing AI Microservice...")

    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            response = await client.get(
                "http://localhost:8001/health",
                timeout=5.0
            )

            if response.status_code == 200:
                print("✅ AI Microservice: Healthy")
                return True
            else:
                print(f"⚠️ AI Microservice: Status {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ AI Microservice Error: {str(e)}")
        return False


async def main():
    """Run all integration tests."""
    print("=" * 60)
    print("🧪 STUDIOCENTOS - Integration Test Suite")
    print(f"⏰ Started: {datetime.now().isoformat()}")
    print("=" * 60)

    results = {}

    # Test Backend
    results['backend'] = await test_backend_api()

    # Test AI Microservice
    results['ai_service'] = await test_ai_microservice()

    # Test Google Analytics
    results['google_analytics'] = await test_google_analytics()

    # Test Facebook
    results['facebook'] = await test_meta_facebook()

    # Test Instagram
    results['instagram'] = await test_instagram()

    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for service, status in results.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {service.upper()}: {'PASS' if status else 'FAIL'}")

    print("=" * 60)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📊 Success Rate: {(passed/total*100):.1f}%")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
