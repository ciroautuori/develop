"""
Demo Instagram Post - Con Immagine Generata
Pubblica post completo su Instagram con AI
"""

import asyncio
import sys
import os
import httpx
import base64
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings


async def create_demo_image():
    """Crea immagine placeholder per il post."""
    print("\n🎨 Preparando immagine per Instagram...")

    # Per semplicità, uso un'immagine placeholder online
    # In produzione, useresti HuggingFace o generate_image
    image_url = "https://picsum.photos/1080/1080"  # Immagine casuale quadrata

    print(f"✅ Immagine pronta: {image_url}")
    return image_url


async def publish_instagram_photo(caption: str, image_url: str):
    """Pubblica foto su Instagram usando Container  API."""
    print("\n📸 Pubblicando su Instagram...")

    if not settings.INSTAGRAM_ACCESS_TOKEN or not settings.INSTAGRAM_ACCOUNT_ID:
        print("❌ Credenziali Instagram mancanti")
        return False

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Create media container
            print("   Step 1: Creando media container...")
            container_response = await client.post(
                f"https://graph.facebook.com/v18.0/{settings.INSTAGRAM_ACCOUNT_ID}/media",
                params={
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": settings.INSTAGRAM_ACCESS_TOKEN
                }
            )

            if container_response.status_code != 200:
                print(f"❌ Errore creazione container: {container_response.status_code}")
                print(f"   Response: {container_response.text}")
                return False

            container_data = container_response.json()
            creation_id = container_data.get('id')
            print(f"   ✅ Container creato: {creation_id}")

            # Step 2: Publish the container
            print("   Step 2: Pubblicando media...")
            await asyncio.sleep(2)  # Wait for Instagram to process

            publish_response = await client.post(
                f"https://graph.facebook.com/v18.0/{settings.INSTAGRAM_ACCOUNT_ID}/media_publish",
                params={
                    "creation_id": creation_id,
                    "access_token": settings.INSTAGRAM_ACCESS_TOKEN
                }
            )

            if publish_response.status_code == 200:
                publish_data = publish_response.json()
                media_id = publish_data.get('id')
                print(f"✅ Post pubblicato su Instagram!")
                print(f"   Media ID: {media_id}")
                print(f"   Visibile su: https://www.instagram.com/@studiocentos")
                return True
            else:
                print(f"❌ Errore pubblicazione: {publish_response.status_code}")
                print(f"   Response: {publish_response.text}")
                return False

    except Exception as e:
        print(f"❌ Errore Instagram: {str(e)}")
        return False


async def main():
    """Demo completa Instagram con immagine."""
    print("=" * 70)
    print("📸 DEMO INSTAGRAM - Post con Immagine")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Caption generata
    caption = """🚀 Innovazione e tecnologia al servizio del tuo business!

StudioCentOS trasforma idee in soluzioni digitali concrete.
Scopri il futuro della tua azienda con noi.

#AI #Innovation #TechItalia #StudioCentOS #DigitalTransformation"""

    print(f"\n📝 Caption:")
    print(f"   {caption[:100]}...")

    # Genera/Prepara immagine
    image_url = await create_demo_image()

    # Pubblica
    success = await publish_instagram_photo(caption, image_url)

    # Summary
    print("\n" + "=" * 70)
    print("📊 RISULTATO")
    print("=" * 70)
    print(f"{'✅' if success else '❌'} Instagram: {'POST PUBBLICATO!' if success else 'ERRORE'}")

    if success:
        print("\n🎉 VAI SU INSTAGRAM E VERIFICA IL POST!")
        print("   Account: @studiocentos")
        print("   Il post dovrebbe essere visibile nel feed")

    print("=" * 70)

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
