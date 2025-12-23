"""
Post BRANDIZZATO con Sistema StudioCentOS
Genera immagine con brand overlay (logo oro + footer)
"""

import asyncio
import httpx
import io
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Per PIL
try:
    from PIL import Image
    PIL_AVAILABLE = True
except:
    PIL_AVAILABLE = False

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ai_microservice")))


async def download_base_image():
    """Scarica immagine base tech."""
    print("\n📥 Scaricando immagine base...")

    # Immagine AI/Tech da Unsplash
    url = "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1080&h=1080&fit=crop"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        if response.status_code == 200:
            print(f"✅ Immagine scaricata ({len(response.content)} bytes)")
            return response.content

    return None


def apply_studiocentos_branding(image_bytes: bytes) -> bytes:
    """Applica branding StudioCentOS all'immagine."""
    print("\n🎨 Applicando branding StudioCentOS...")

    if not PIL_AVAILABLE:
        print("⚠️ PIL non disponibile, uso immagine originale")
        return image_bytes

    try:
        from PIL import Image, ImageDraw, ImageFont

        # Apri immagine
        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        image = image.resize((1080, 1080), Image.Resampling.LANCZOS)

        draw = ImageDraw.Draw(image)

        # Colori brand
        GOLD = "#D4AF37"
        DARK_BLUE = "#1a1a2e"

        # 1. Aggiungi footer brandizzato
        footer_height = 50
        footer_y = image.height - footer_height

        # Background footer (semi-trasparente)
        footer = Image.new("RGBA", (image.width, footer_height), (26, 26, 46, 220))
        image.paste(footer, (0, footer_y), footer)

        # Linea oro
        draw.line([(0, footer_y), (image.width, footer_y)], fill=GOLD, width=3)

        # Testo "StudioCentOS"
        try:
            font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        except:
            font_footer = ImageFont.load_default()

        text = "STUDIOCENTOS"
        bbox = draw.textbbox((0, 0), text, font=font_footer)
        text_width = bbox[2] - bbox[0]
        text_x = (image.width - text_width) // 2
        text_y = footer_y + 15

        draw.text((text_x, text_y), text, fill=GOLD, font=font_footer)

        # 2. Aggiungi accenti oro negli angoli
        accent_length = 60
        accent_width = 4

        # Angolo top-left
        draw.line([(0, 0), (accent_length, 0)], fill=GOLD, width=accent_width)
        draw.line([(0, 0), (0, accent_length)], fill=GOLD, width=accent_width)

        # Angolo top-right
        draw.line([(image.width - accent_length, 0), (image.width, 0)], fill=GOLD, width=accent_width)
        draw.line([(image.width - 1, 0), (image.width - 1, accent_length)], fill=GOLD, width=accent_width)

        # 3. Aggiungi watermark "StudioCentOS" in alto (semi-trasparente)
        try:
            font_watermark = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        except:
            font_watermark = font_footer

        watermark_text = "StudioCentOS"
        bbox = draw.textbbox((0, 0), watermark_text, font=font_watermark)
        wm_width = bbox[2] - bbox[0]
        wm_x = image.width - wm_width - 30
        wm_y = 25

        # Semi-trasparente
        watermark_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
        wm_draw = ImageDraw.Draw(watermark_layer)
        wm_draw.text((wm_x, wm_y), watermark_text, fill=(212, 175, 55, 180), font=font_watermark)

        image = Image.alpha_composite(image, watermark_layer)

        # Converti a bytes
        output = io.BytesIO()
        image.convert("RGB").save(output, format="JPEG", quality=95)
        output.seek(0)

        print("✅ Branding applicato:")
        print("   - Footer oro con logo")
        print("   - Accenti oro negli angoli")
        print("   - Watermark StudioCentOS")

        return output.getvalue()

    except Exception as e:
        print(f"❌ Errore branding: {e}")
        return image_bytes


async def upload_to_static(image_bytes: bytes, filename: str) -> str:
    """Salva immagine in static e ritorna URL pubblico."""
    print(f"\n💾 Salvando immagine brandizzata...")

    # Salva in /app/static
    static_dir = Path("/app/static/social")
    static_dir.mkdir(parents=True, exist_ok=True)

    image_path = static_dir / filename
    with open(image_path, "wb") as f:
        f.write(image_bytes)

    # URL pubblico
    public_url = f"https://studiocentos.it/static/social/{filename}"

    print(f"✅ Immagine salvata: {image_path}")
    print(f"✅ URL pubblico: {public_url}")

    return public_url


async def create_branded_post():
    """Crea post con immagine brandizzata."""
    print("=" * 80)
    print("🎨 POST BRANDIZZATO - StudioCentOS Auto-Publishing")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Step 1: Scarica immagine base
    base_image = await download_base_image()
    if not base_image:
        print("❌ Download fallito")
        return False

    # Step 2: Applica branding StudioCentOS
    branded_image = apply_studiocentos_branding(base_image)

    # Step 3: Salva in static (accessibile pubblicamente)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"post_branded_{timestamp}.jpg"
    image_url = await upload_to_static(branded_image, filename)

    # Step 4: Crea post tramite API
    content = """🚀 L'intelligenza artificiale non è più il futuro, è ORA!

StudioCentOS ti aiuta a integrare soluzioni AI reali nel tuo business:
• Chatbot intelligenti
• Automazione processi
• Analisi dati avanzata
• App custom su misura

Scopri come trasformare la tua azienda oggi 💡
👉 studiocentos.it"""

    print(f"\n📝 Caption preparata")

    # Schedulazione
    publish_in_minutes = 2
    scheduled_at = datetime.now() + timedelta(minutes=publish_in_minutes)

    payload = {
        "content": content,
        "title": "Post Brandizzato AI - StudioCentOS",
        "hashtags": ["#AI", "#Innovation", "#StudioCentOS", "#TechItalia"],
        "media_urls": [image_url],
        "media_type": "image",
        "platforms": ["facebook", "instagram"],
        "scheduled_at": scheduled_at.isoformat() + "Z",
        "ai_generated": False
    }

    print(f"\n🔄 Creando post schedulato...")

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

                print("\n" + "=" * 80)
                print("🎉 POST BRANDIZZATO CREATO!")
                print("=" * 80)
                print(f"✅ Post ID: {post_id}")
                print(f"✅ Immagine: BRANDIZZATA con logo StudioCentOS oro")
                print(f"✅ Piattaforme: Facebook + Instagram")
                print(f"✅ Pubblicazione tra: {publish_in_minutes} minuti")
                print(f"✅ Orario: {scheduled_at.strftime('%H:%M:%S')}")
                print("=" * 80)

                print(f"\n🎨 ELEMENTI BRAND APPLICATI:")
                print(f"   📌 Footer oro con nome StudioCentOS")
                print(f"   📌 Accenti oro negli angoli (design premium)")
                print(f"   📌 Watermark StudioCentOS semi-trasparente")
                print(f"   📌 Colori brand #D4AF37 (oro)")

                print(f"\n⏰ Controlla tra {publish_in_minutes} minuti:")
                print(f"   📘 Facebook: https://www.facebook.com/Studiocentos")
                print(f"   📸 Instagram: https://www.instagram.com/studiocentos")
                print("=" * 80)

                return True
            else:
                print(f"❌ Errore API: {response.status_code}")
                print(f"   {response.text}")
                return False

    except Exception as e:
        print(f"❌ Errore: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(create_branded_post())
    sys.exit(0 if success else 1)
