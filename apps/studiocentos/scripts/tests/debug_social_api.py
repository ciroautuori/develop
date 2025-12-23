#!/usr/bin/env python3
"""
DEBUG SOCIAL API - Verifica cosa funziona e cosa no
Esegui con: docker exec studiocentos-backend python /app/debug_social_api.py
"""
import asyncio
import os
import sys

# Aggiungi path per imports
sys.path.insert(0, '/app')

async def main():
    print("=" * 60)
    print("🔍 DEBUG SOCIAL API - VERIFICA CONFIGURAZIONE")
    print("=" * 60)

    # 1. Verifica variabili d'ambiente
    print("\n📋 VARIABILI D'AMBIENTE:")
    env_vars = {
        "META_ACCESS_TOKEN": os.getenv("META_ACCESS_TOKEN", ""),
        "META_APP_ID": os.getenv("META_APP_ID", ""),
        "META_APP_SECRET": os.getenv("META_APP_SECRET", ""),
        "FACEBOOK_PAGE_ID": os.getenv("FACEBOOK_PAGE_ID", ""),
        "INSTAGRAM_ACCOUNT_ID": os.getenv("INSTAGRAM_ACCOUNT_ID", ""),
        "INSTAGRAM_ACCESS_TOKEN": os.getenv("INSTAGRAM_ACCESS_TOKEN", ""),
        "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY", ""),
        "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET", ""),
        "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN", ""),
        "TWITTER_ACCESS_SECRET": os.getenv("TWITTER_ACCESS_SECRET", ""),
        "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN", ""),
        "LINKEDIN_ACCESS_TOKEN": os.getenv("LINKEDIN_ACCESS_TOKEN", ""),
    }

    for key, value in env_vars.items():
        if value:
            # Mostra solo primi 10 caratteri per sicurezza
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"  ✅ {key}: {masked}")
        else:
            print(f"  ❌ {key}: NON CONFIGURATO")

    # 2. Test chiamate API reali
    print("\n🌐 TEST CHIAMATE API:")

    try:
        from app.integrations.social_media import SocialMediaIntegration
        integration = SocialMediaIntegration()

        # Facebook
        print("\n  📘 FACEBOOK:")
        try:
            fb_result = await integration.get_account_stats('facebook')
            print(f"     Risultato: {fb_result}")
            if not fb_result:
                print("     ⚠️ Risultato vuoto - token mancante o invalido")
        except Exception as e:
            print(f"     ❌ Errore: {e}")

        # Instagram
        print("\n  📸 INSTAGRAM:")
        try:
            ig_result = await integration.get_account_stats('instagram')
            print(f"     Risultato: {ig_result}")
            if not ig_result:
                print("     ⚠️ Risultato vuoto - token mancante o invalido")
        except Exception as e:
            print(f"     ❌ Errore: {e}")

        # Twitter
        print("\n  🐦 TWITTER:")
        try:
            tw_result = await integration.get_account_stats('twitter')
            print(f"     Risultato: {tw_result}")
            if not tw_result:
                print("     ⚠️ Risultato vuoto - token mancante o invalido")
        except Exception as e:
            print(f"     ❌ Errore: {e}")

        # LinkedIn
        print("\n  💼 LINKEDIN:")
        try:
            li_result = await integration.get_account_stats('linkedin')
            print(f"     Risultato: {li_result}")
            if not li_result:
                print("     ⚠️ Risultato vuoto - non implementato o token mancante")
        except Exception as e:
            print(f"     ❌ Errore: {e}")

    except ImportError as e:
        print(f"  ❌ Errore import: {e}")
    except Exception as e:
        print(f"  ❌ Errore generale: {e}")

    # 3. Test diretto API Facebook/Instagram (se token presente)
    if env_vars["META_ACCESS_TOKEN"] and env_vars["FACEBOOK_PAGE_ID"]:
        print("\n🔥 TEST DIRETTO API META (Facebook Graph API):")
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://graph.facebook.com/v18.0/{env_vars['FACEBOOK_PAGE_ID']}"
                params = {
                    'fields': 'followers_count,fan_count,name',
                    'access_token': env_vars['META_ACCESS_TOKEN'],
                }
                async with session.get(url, params=params) as response:
                    status = response.status
                    text = await response.text()
                    print(f"     Status: {status}")
                    print(f"     Response: {text[:500]}")
        except Exception as e:
            print(f"     ❌ Errore: {e}")

    if env_vars["META_ACCESS_TOKEN"] and env_vars["INSTAGRAM_ACCOUNT_ID"]:
        print("\n🔥 TEST DIRETTO API META (Instagram):")
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://graph.facebook.com/v18.0/{env_vars['INSTAGRAM_ACCOUNT_ID']}"
                params = {
                    'fields': 'followers_count,media_count,username',
                    'access_token': env_vars['META_ACCESS_TOKEN'],
                }
                async with session.get(url, params=params) as response:
                    status = response.status
                    text = await response.text()
                    print(f"     Status: {status}")
                    print(f"     Response: {text[:500]}")
        except Exception as e:
            print(f"     ❌ Errore: {e}")

    print("\n" + "=" * 60)
    print("📊 DIAGNOSI COMPLETATA")
    print("=" * 60)
    print("""
Se vedi ❌ NON CONFIGURATO per i token, devi:
1. Configurare le variabili nel file .env
2. Riavviare i container Docker

Se vedi errori API (401, 403), i token sono:
- Scaduti (Meta token scadono dopo 60 giorni)
- Permessi insufficienti
- Account ID sbagliato
""")

if __name__ == "__main__":
    asyncio.run(main())
