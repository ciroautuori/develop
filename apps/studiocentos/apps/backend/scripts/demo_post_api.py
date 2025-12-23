"""
DEMO COMPLETA - Calendario Editoriale via API REST
Crea post schedulato per FB + Instagram tramite API
"""

import asyncio
import httpx
from datetime import datetime, timedelta
import json


async def create_scheduled_post_via_api():
    """Crea post schedulato tramite API REST."""
    print("=" * 80)
    print("🚀 DEMO CALENDARIO EDITORIALE - Posting Automatico FB + Instagram")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Prepara immagine (Unsplash pubblica e sicura)
    image_url = "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1080&h=1080&fit=crop"

    print(f"\n🎨 Immagine preparata:")
    print(f"   {image_url}")

    # Contenuto del post
    content = """🚀 L'AI sta trasformando il modo di fare business!

Con StudioCentOS, porta l'innovazione nella tua azienda: sviluppo software su misura, integrazione AI e molto altro.

Inizia oggi la tua trasformazione digitale! 💡
Info: studiocentos.it"""

    print(f"\n📝 Contenuto:")
    print(f"   {content[:100]}...")

    # Calcola orario pubblicazione (tra 3 minuti)
    publish_in_minutes = 3
    scheduled_at = datetime.now() + timedelta(minutes=publish_in_minutes)

    # Prepara payload
    payload = {
        "content": content,
        "title": "Demo Post AI - StudioCentOS",
        "hashtags": ["#AI", "#Innovation", "#TechItalia"],
        "media_urls": [image_url],
        "media_type": "image",
        "platforms": ["facebook", "instagram"],
        "scheduled_at": scheduled_at.isoformat() + "Z",
        "ai_generated": True,
        "ai_model": "demo"
    }

    print(f"\n📅 Schedulazione:")
    print(f"   Piattaforme: Facebook + Instagram")
    print(f"   Pubblicazione: {scheduled_at.strftime('%H:%M:%S')} (tra {publish_in_minutes} min)")

    # Chiama API
    print(f"\n🔄 Chiamando API...")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "http://localhost:8000/api/v1/marketing/calendar/posts",
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                post_id = data.get('id')

                print(f"\n✅ POST CREATO CON SUCCESSO!")
                print(f"   Post ID: {post_id}")
                print(f"   Status: {data.get('status')}")
                print(f"   Scheduled: {data.get('scheduled_at')}")

                print("\n" + "=" * 80)
                print("📊 RIEPILOGO FINALE")
                print("=" * 80)
                print(f"✅ Post ID: {post_id}")
                print(f"✅ Immagine AI: Preparata")
                print(f"✅ Piattaforme: Facebook + Instagram")
                print(f"✅ Pubblicazione automatica tra: {publish_in_minutes} minuti")
                print(f"✅ Orario: {scheduled_at.strftime('%H:%M:%S')}")
                print("=" * 80)

                print(f"\n⏰ ATTENDERE {publish_in_minutes} MINUTI...")
                print(f"   Il sistema pubblicherà AUTOMATICAMENTE su:")
                print(f"   📘 Facebook: https://www.facebook.com/Studiocentos")
                print(f"   📸 Instagram: https://www.instagram.com/studiocentos")
                print(f"\n🎯 Controlla entrambe le pagine alle {scheduled_at.strftime('%H:%M')}!")
                print("=" * 80)

                return True

            else:
                print(f"\n❌ Errore API: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except Exception as e:
        print(f"\n❌ Errore: {str(e)}")
        return False


if __name__ == "__main__":
    import sys
    success = asyncio.run(create_scheduled_post_via_api())
    sys.exit(0 if success else 1)
