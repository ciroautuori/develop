"""
Image Resize Service - Ridimensionamento automatico immagini per social media.

Dimensioni ottimali per ogni piattaforma:
- Facebook Post: 1200x630 (1.91:1)
- Instagram Square: 1080x1080 (1:1)
- Instagram Portrait: 1080x1350 (4:5)
- Instagram Story: 1080x1920 (9:16)
- LinkedIn: 1200x627 (1.91:1)
- Twitter/X: 1600x900 (16:9)
- TikTok: 1080x1920 (9:16)
- Pinterest: 1000x1500 (2:3)
- YouTube Thumbnail: 1280x720 (16:9)
"""

from io import BytesIO

import httpx
import structlog
from PIL import Image

logger = structlog.get_logger(__name__)


# Dimensioni social ottimali
SOCIAL_SIZES: dict[str, tuple[int, int]] = {
    "facebook": (1200, 630),
    "facebook_story": (1080, 1920),
    "instagram": (1080, 1080),
    "instagram_portrait": (1080, 1350),
    "instagram_story": (1080, 1920),
    "linkedin": (1200, 627),
    "twitter": (1600, 900),
    "tiktok": (1080, 1920),
    "pinterest": (1000, 1500),
    "youtube_thumbnail": (1280, 720),
    "threads": (1080, 1080),
    "google_business": (1200, 900),
}


class ImageResizeService:
    """Servizio per ridimensionare immagini per ogni social network."""

    @staticmethod
    def get_supported_platforms() -> list[str]:
        """Ritorna lista piattaforme supportate."""
        return list(SOCIAL_SIZES.keys())

    @staticmethod
    def get_size_for_platform(platform: str) -> tuple[int, int]:
        """Ottiene dimensioni per piattaforma."""
        return SOCIAL_SIZES.get(platform, (1080, 1080))

    async def resize_from_url(
        self,
        image_url: str,
        platform: str,
        output_format: str = "JPEG",
        quality: int = 90
    ) -> bytes:
        """
        Scarica immagine da URL e ridimensiona per piattaforma.

        Args:
            image_url: URL dell'immagine sorgente
            platform: Nome piattaforma (facebook, instagram, etc.)
            output_format: Formato output (JPEG, PNG, WEBP)
            quality: Qualità output (1-100)

        Returns:
            bytes dell'immagine ridimensionata
        """
        try:
            # Scarica immagine
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_data = response.content

            # Ridimensiona
            return self.resize_image(
                image_data=image_data,
                platform=platform,
                output_format=output_format,
                quality=quality
            )

        except Exception as e:
            logger.error("image_resize_from_url_error", url=image_url[:50], error=str(e))
            raise

    def resize_image(
        self,
        image_data: bytes,
        platform: str,
        output_format: str = "JPEG",
        quality: int = 90
    ) -> bytes:
        """
        Ridimensiona immagine per piattaforma specifica.

        Usa smart crop per mantenere il soggetto principale.
        """
        try:
            # Apri immagine
            img = Image.open(BytesIO(image_data))

            # Converti in RGB se necessario (per JPEG)
            if img.mode in ("RGBA", "P") and output_format.upper() == "JPEG":
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[3] if len(img.split()) > 3 else None)
                img = background
            elif img.mode != "RGB" and output_format.upper() == "JPEG":
                img = img.convert("RGB")

            # Ottieni dimensioni target
            target_width, target_height = SOCIAL_SIZES.get(platform, (1080, 1080))

            # Smart resize con crop centrale
            img = self._smart_crop_resize(img, target_width, target_height)

            # Salva in buffer
            buffer = BytesIO()
            img.save(
                buffer,
                format=output_format.upper(),
                quality=quality,
                optimize=True
            )

            logger.info(
                "image_resized",
                platform=platform,
                size=f"{target_width}x{target_height}",
                format=output_format
            )

            return buffer.getvalue()

        except Exception as e:
            logger.error("image_resize_error", platform=platform, error=str(e))
            raise

    def _smart_crop_resize(
        self,
        img: Image.Image,
        target_width: int,
        target_height: int
    ) -> Image.Image:
        """
        Ridimensiona con crop intelligente centrato.

        Mantiene l'aspect ratio e cropa le parti in eccesso.
        """
        original_width, original_height = img.size
        target_ratio = target_width / target_height
        original_ratio = original_width / original_height

        if original_ratio > target_ratio:
            # Immagine più larga: crop orizzontale
            new_width = int(original_height * target_ratio)
            left = (original_width - new_width) // 2
            img = img.crop((left, 0, left + new_width, original_height))
        elif original_ratio < target_ratio:
            # Immagine più alta: crop verticale
            new_height = int(original_width / target_ratio)
            top = (original_height - new_height) // 2
            img = img.crop((0, top, original_width, top + new_height))

        # Ridimensiona alla dimensione finale
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

        return img

    async def resize_for_all_platforms(
        self,
        image_url: str,
        platforms: list[str] = None
    ) -> dict[str, bytes]:
        """
        Ridimensiona immagine per multiple piattaforme.

        Args:
            image_url: URL immagine sorgente
            platforms: Lista piattaforme (default: tutte)

        Returns:
            Dict con platform -> bytes immagine
        """
        if platforms is None:
            platforms = ["facebook", "instagram", "instagram_story", "linkedin", "twitter"]

        # Scarica immagine una volta sola
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            image_data = response.content

        # Ridimensiona per ogni piattaforma
        results = {}
        for platform in platforms:
            try:
                results[platform] = self.resize_image(image_data, platform)
            except Exception as e:
                logger.error("resize_for_platform_error", platform=platform, error=str(e))
                results[platform] = None

        return results


# Singleton instance
image_resize_service = ImageResizeService()
