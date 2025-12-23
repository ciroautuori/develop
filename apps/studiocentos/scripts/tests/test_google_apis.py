#!/usr/bin/env python3
"""
Test Google APIs Configuration
Verifica che tutte le API Google siano configurate correttamente.

Usage:
    python scripts/tests/test_google_apis.py
"""

import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "apps" / "backend"
sys.path.insert(0, str(backend_path))

import httpx
from dotenv import load_dotenv

# Load environment
load_dotenv(backend_path / ".env")


class GoogleAPITester:
    """Test all Google API configurations."""

    def __init__(self):
        self.results = {}
        self.errors = []

    def check_env_var(self, name: str, required: bool = True) -> str:
        """Check if environment variable is set."""
        value = os.getenv(name, "")
        if not value and required:
            self.errors.append(f"❌ {name} non configurato")
            return ""
        elif not value:
            print(f"⚠️  {name} non configurato (opzionale)")
            return ""
        else:
            # Mask the value
            masked = value[:10] + "..." if len(value) > 10 else "***"
            print(f"✅ {name} = {masked}")
            return value

    async def test_oauth_credentials(self) -> bool:
        """Test OAuth credentials validity."""
        print("\n📋 Test OAuth Credentials")
        print("-" * 40)

        client_id = self.check_env_var("GOOGLE_CLIENT_ID")
        client_secret = self.check_env_var("GOOGLE_CLIENT_SECRET")
        redirect_uri = self.check_env_var("GOOGLE_REDIRECT_URI", required=False)

        if not client_id or not client_secret:
            print("❌ OAuth non configurato - Login Google non funzionerà")
            return False

        # Check if client_id format is valid
        if ".apps.googleusercontent.com" not in client_id:
            self.errors.append("❌ GOOGLE_CLIENT_ID formato non valido (deve contenere .apps.googleusercontent.com)")
            return False

        print("✅ OAuth credentials presenti")
        return True

    async def test_places_api(self) -> bool:
        """Test Google Places API."""
        print("\n📍 Test Google Places API (Lead Finder)")
        print("-" * 40)

        api_key = self.check_env_var("GOOGLE_PLACES_API_KEY", required=False)
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY", "")
            if api_key:
                print("ℹ️  Usando GOOGLE_API_KEY come fallback")

        if not api_key:
            print("❌ Places API non configurato - Lead Finder non funzionerà")
            return False

        # Test API call
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = "https://places.googleapis.com/v1/places:searchNearby"
                headers = {
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": api_key,
                    "X-Goog-FieldMask": "places.displayName"
                }
                payload = {
                    "includedTypes": ["restaurant"],
                    "maxResultCount": 1,
                    "locationRestriction": {
                        "circle": {
                            "center": {"latitude": 40.6824, "longitude": 14.7681},
                            "radius": 1000.0
                        }
                    }
                }

                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    places_count = len(data.get("places", []))
                    print(f"✅ Places API funzionante - trovati {places_count} risultati test")
                    return True
                elif response.status_code == 403:
                    self.errors.append("❌ Places API: Accesso negato - verifica billing/quota")
                    return False
                elif response.status_code == 400:
                    error_msg = response.json().get("error", {}).get("message", "Unknown error")
                    if "API key" in error_msg:
                        self.errors.append("❌ Places API: API key non valida")
                    else:
                        self.errors.append(f"❌ Places API: {error_msg}")
                    return False
                else:
                    self.errors.append(f"❌ Places API: HTTP {response.status_code}")
                    return False

        except Exception as e:
            self.errors.append(f"❌ Places API: {str(e)}")
            return False

    async def test_pagespeed_api(self) -> bool:
        """Test PageSpeed Insights API."""
        print("\n🚀 Test PageSpeed Insights API (SEO)")
        print("-" * 40)

        api_key = self.check_env_var("GOOGLE_API_KEY", required=False)

        if not api_key:
            print("⚠️  PageSpeed API non configurato - SEO tools limitati")
            return False

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
                params = {
                    "url": "https://google.com",
                    "key": api_key,
                    "category": "performance"
                }

                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    score = data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score", 0)
                    print(f"✅ PageSpeed API funzionante - score test: {int(score * 100)}%")
                    return True
                elif response.status_code == 403:
                    self.errors.append("❌ PageSpeed API: Accesso negato")
                    return False
                else:
                    self.errors.append(f"❌ PageSpeed API: HTTP {response.status_code}")
                    return False

        except Exception as e:
            self.errors.append(f"❌ PageSpeed API: {str(e)}")
            return False

    async def test_gemini_api(self) -> bool:
        """Test Google Gemini AI API."""
        print("\n🤖 Test Google Gemini API (AI)")
        print("-" * 40)

        api_key = self.check_env_var("GOOGLE_AI_API_KEY", required=False)
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY", "")
            if api_key:
                print("ℹ️  Usando GOOGLE_API_KEY come fallback")

        if not api_key:
            print("⚠️  Gemini API non configurato - AI generation limitata")
            return False

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

                response = await client.get(url)

                if response.status_code == 200:
                    data = response.json()
                    models = data.get("models", [])
                    print(f"✅ Gemini API funzionante - {len(models)} modelli disponibili")
                    return True
                elif response.status_code == 403:
                    self.errors.append("❌ Gemini API: Accesso negato")
                    return False
                else:
                    self.errors.append(f"❌ Gemini API: HTTP {response.status_code}")
                    return False

        except Exception as e:
            self.errors.append(f"❌ Gemini API: {str(e)}")
            return False

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 50)
        print("📊 RIEPILOGO TEST GOOGLE APIS")
        print("=" * 50)

        for service, status in self.results.items():
            icon = "✅" if status else "❌"
            print(f"{icon} {service}")

        if self.errors:
            print("\n⚠️  ERRORI RILEVATI:")
            for error in self.errors:
                print(f"   {error}")

        # Count
        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)

        print(f"\n📈 Risultato: {passed}/{total} test passati")

        if passed < total:
            print("\n🔧 AZIONI RICHIESTE:")
            print("1. Vai su https://console.cloud.google.com/apis/credentials")
            print("2. Crea le credenziali mancanti")
            print("3. Abilita le API necessarie in Library")
            print("4. Aggiorna il file .env")

    async def run_all_tests(self):
        """Run all API tests."""
        print("🔍 GOOGLE APIS CONFIGURATION TEST")
        print("=" * 50)

        self.results["OAuth Credentials"] = await self.test_oauth_credentials()
        self.results["Places API (Lead Finder)"] = await self.test_places_api()
        self.results["PageSpeed API (SEO)"] = await self.test_pagespeed_api()
        self.results["Gemini API (AI)"] = await self.test_gemini_api()

        self.print_summary()

        return all(self.results.values())


async def main():
    tester = GoogleAPITester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
