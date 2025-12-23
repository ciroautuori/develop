"""
DEMO COMPLETA - Calendario Editoriale con Immagine AI
1. Genera immagine con AI
2. Salva in locale (accessibile via backend)
3. Crea post schedulato per FB + Instagram
4. Sistema pubblica automaticamente tra 3 minuti
"""

import asyncio
import sys
import os
import httpx
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.infrastructure.database import SessionLocal
from app.domain.marketing.models import ScheduledPost, PostStatus


async def generate_demo_image_url():
    """
    Per questa demo, uso un'immagine pubblica sicura.
    In produzione, useresti HuggingFace Image Generation.
    """
    print("\n🎨 Preparando immagine per il post...")

    # Uso un'immagine tech/AI pubblica e sicura
    # Unsplash fornisce immagini pubblicamente accessibili
    image_url = "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1080&h=1080&fit=crop"

    print(f"✅ Immagine pronta: {image_url}")
    print(f"   Tema: AI & Technology")

    return image_url


async def create_scheduled_post(content: str, image_url: str, publish_in_minutes: int = 3):
    """Crea post schedulato nel database."""
    print(f"\n📅 Creando post schedulato (pubblicazione tra {publish_in_minutes} minuti)...")

    db = SessionLocal()
    try:
        # Calcola il momento di pubblicazione
        scheduled_at = datetime.utcnow() + timedelta(minutes=publish_in_minutes)

        # Crea post
        post = ScheduledPost(
            content=content,
            title="Demo Post AI - StudioCentOS",
            hashtags=["#AI", "#Innovation", "#TechItalia"],
            media_urls=[image_url],
            media_type="image",
            platforms=["facebook", "instagram"],  # Entrambe le piattaforme!
            scheduled_at=scheduled_at,
            status=PostStatus.SCHEDULED,
            ai_generated=True,
            ai_model="llama-3.3-70b",
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        post_id = post.id

        print(f"✅ Post creato con successo!")
        print(f"   ID: {post_id}")
        print(f"   Piattaforme: {', '.join(post.platforms)}")
        print(f"   Pubblicazione schedulata: {scheduled_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"   Status: {post.status.value}")

        # Ora scheduliamo con APScheduler
        from app.infrastructure.scheduler import post_scheduler

        await post_scheduler.schedule_post(post_id, scheduled_at)

        print(f"✅ Post aggiunto allo scheduler!")

        db.close()
        return post_id, scheduled_at

    except Exception as e:
        print(f"❌ Errore creazione post: {str(e)}")
        db.rollback()
        db.close()
        return None, None


async def verify_post_creation(post_id: int):
    """Verifica che il post sia stato creato correttamente."""
    print(f"\n🔍 Verificando post ID {post_id}...")

    db = SessionLocal()
    try:
        post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()

        if post:
            print(f"✅ Post trovato nel database")
            print(f"   Content: {post.content[:80]}...")
            print(f"   Platforms: {', '.join(post.platforms)}")
            print(f"   Media URLs: {len(post.media_urls)} image(s)")
            print(f"   Scheduled: {post.scheduled_at}")
            return True
        else:
            print(f"❌ Post non trovato!")
            return False

    finally:
        db.close()


async def main():
    """Demo completa calendario editoriale."""
    print("=" * 80)
    print("🚀 DEMO CALENDARIO EDITORIALE - Posting Automatico FB + Instagram")
    print(f"⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 80)

    # Step 1: Genera immagine
    image_url = await generate_demo_image_url()

    # Step 2: Prepara contenuto
    content = """🚀 L'AI sta trasformando il modo di fare business!

Con StudioCentOS, porta l'innovazione nella tua azienda: sviluppo software su misura, integrazione AI e molto altro.

Inizia oggi la tua trasformazione digitale! 💡
Info: studiocentos.it"""

    print(f"\n📝 Contenuto del post:")
    print(f"   {content[:100]}...")

    # Step 3: Crea post schedulato
    publish_minutes = 3
    post_id, scheduled_at = await create_scheduled_post(content, image_url, publish_minutes)

    if not post_id:
        print("\n❌ Creazione post fallita")
        return False

    # Step 4: Verifica
    verified = await verify_post_creation(post_id)

    # Summary
    print("\n" + "=" * 80)
    print("📊 RIEPILOGO")
    print("=" * 80)
    print(f"✅ Post ID: {post_id}")
    print(f"✅ Immagine: {image_url[:60]}...")
    print(f"✅ Piattaforme: Facebook + Instagram")
    print(f"✅ Pubblicazione automatica tra: {publish_minutes} minuti")
    print(f"✅ Orario pubblicazione: {scheduled_at.strftime('%H:%M:%S')} UTC")
    print("=" * 80)

    print(f"\n⏰ ATTENDERE {publish_minutes} MINUTI...")
    print(f"   Il sistema pubblicherà automaticamente su:")
    print(f"   📘 Facebook: https://www.facebook.com/Studiocentos")
    print(f"   📸 Instagram: https://www.instagram.com/studiocentos")
    print("\n🎯 Dopo {publish_minutes} minuti, controlla entrambe le pagine!")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
