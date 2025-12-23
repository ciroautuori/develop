"""
Image Branding System - MARKETTINA Brand Overlay

Applies brand elements to generated images:
- Logo overlay (corner position)
- Brand colors (#D4AF37 gold, #1a1a2e dark blue)
- Social media template formatting
- Watermark/footer

Author: MARKETTINA AI Team
Date: November 2025
"""

import io
import logging
from enum import Enum
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)

# Brand Colors - markettina REAL BRAND (NO BLU!)
BRAND_COLORS = {
    "primary": "#D4AF37",      # Gold - Lusso, Professionalità, Eccellenza
    "secondary": "#0A0A0A",    # Nero profondo - Background
    "accent": "#AA8C2C",       # Gold scuro
    "text_light": "#FAFAFA",   # Bianco - Testo chiaro
    "text_dark": "#171717",    # Quasi nero - Testo scuro
    "background": "#0A0A0A",   # Nero profondo
    "gold_light": "#F4E5B8",   # Gold chiaro
    "gold_50": "#FBF8EC",      # Gold molto chiaro
}

# Social Media Dimensions - AGGIORNATE NOVEMBRE 2025
SOCIAL_DIMENSIONS = {
    # Instagram
    "instagram": (1080, 1080),           # Square post (default)
    "instagram_square": (1080, 1080),    # Square post
    "instagram_vertical": (1080, 1350),  # Vertical post 4:5
    "instagram_landscape": (1080, 566),  # Landscape post
    "instagram_story": (1080, 1920),     # Stories/Reels 9:16
    "instagram_reels": (1080, 1920),     # Reels 9:16

    # Facebook
    "facebook": (1080, 1080),            # Square post (default)
    "facebook_square": (1080, 1080),     # Square post
    "facebook_vertical": (1080, 1350),   # Vertical post 4:5
    "facebook_landscape": (1080, 566),   # Landscape post
    "facebook_story": (1080, 1920),      # Stories 9:16

    # LinkedIn
    "linkedin": (1200, 627),             # Landscape post (default)
    "linkedin_landscape": (1200, 627),   # Landscape post
    "linkedin_square": (1200, 1200),     # Square post
    "linkedin_vertical": (720, 900),     # Vertical post (mobile only)

    # Twitter/X
    "twitter": (1280, 720),              # Landscape (default)
    "twitter_landscape": (1280, 720),    # Landscape 16:9
    "twitter_square": (720, 720),        # Square
    "twitter_vertical": (720, 1280),     # Vertical
    "x": (1280, 720),                    # Alias for Twitter

    # TikTok
    "tiktok": (1080, 1920),              # Vertical 9:16
    "tiktok_vertical": (1080, 1920),     # Vertical 9:16
    "tiktok_square": (640, 640),         # Square (ads)

    # Threads
    "threads": (1440, 1920),             # Vertical 3:4

    # Default
    "default": (1080, 1080),             # Square (works everywhere)
}


class LogoPosition(str, Enum):
    """Logo overlay position."""
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    TOP_CENTER = "top_center"  # Best for visibility
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"


class ImageBranding:
    """
    Handles brand overlay for generated images.

    Features:
    - Logo overlay with transparency
    - Social media template formatting
    - Brand color accents
    - Watermark/footer
    """

    def __init__(self):
        # Try multiple paths for Docker compatibility
        possible_paths = [
            Path(__file__).parent.parent.parent / "assets" / "brand",  # Development
            Path("/app/app/assets/brand"),  # Docker container
            Path("/app/assets/brand"),  # Alternative Docker path
        ]

        self.assets_dir = None
        for path in possible_paths:
            if path.exists():
                self.assets_dir = path
                break

        if not self.assets_dir:
            self.assets_dir = possible_paths[0]  # Default fallback
            logger.warning(f"Brand assets directory not found, tried: {possible_paths}")

        self.logo_path = self.assets_dir / "logo.png"
        self.logo_white_path = self.assets_dir / "logo_white.png"

        self._logo: Image.Image | None = None
        self._logo_white: Image.Image | None = None

        if PIL_AVAILABLE:
            self._load_assets()
            logger.info(f"ImageBranding initialized, assets_dir={self.assets_dir}, logo_loaded={self._logo is not None}")

    def _load_assets(self):
        """Load brand assets."""
        try:
            if self.logo_path.exists():
                self._logo = Image.open(self.logo_path).convert("RGBA")
                logger.info(f"Loaded logo: {self.logo_path}")

            if self.logo_white_path.exists():
                self._logo_white = Image.open(self.logo_white_path).convert("RGBA")
                logger.info(f"Loaded white logo: {self.logo_white_path}")
        except Exception as e:
            logger.warning(f"Failed to load brand assets: {e}")

    def apply_branding(
        self,
        image_bytes: bytes,
        platform: str = "default",
        logo_position: LogoPosition = LogoPosition.TOP_CENTER,  # Top center for better visibility
        logo_size_ratio: float = 0.18,  # Slightly larger
        add_footer: bool = True,
        footer_text: str = "MARKETTINA",
    ) -> bytes:
        """
        Apply brand elements to an image.

        Args:
            image_bytes: Original image bytes
            platform: Target platform (linkedin, facebook, instagram, etc.)
            logo_position: Where to place the logo
            logo_size_ratio: Logo size as ratio of image width
            add_footer: Whether to add brand footer
            footer_text: Text for footer

        Returns:
            Branded image bytes
        """
        if not PIL_AVAILABLE:
            logger.warning("PIL not available, returning original image")
            return image_bytes

        try:
            # Open image
            image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

            # Resize for platform if needed
            target_size = SOCIAL_DIMENSIONS.get(platform, SOCIAL_DIMENSIONS["default"])
            image = self._resize_and_crop(image, target_size)

            # Add logo overlay
            if self._logo_white:
                image = self._add_logo(image, logo_position, logo_size_ratio)

            # Add footer/watermark
            if add_footer:
                image = self._add_footer(image, footer_text)

            # Add subtle brand accent (gold border)
            image = self._add_brand_accent(image)

            # Convert back to bytes
            output = io.BytesIO()
            image.convert("RGB").save(output, format="PNG", quality=95)
            output.seek(0)

            logger.info(f"Applied branding for platform: {platform}")
            return output.getvalue()

        except Exception as e:
            logger.error(f"Failed to apply branding: {e}")
            return image_bytes

    def _resize_and_crop(
        self,
        image: Image.Image,
        target_size: tuple[int, int]
    ) -> Image.Image:
        """Resize and crop image to target size (center crop)."""
        target_ratio = target_size[0] / target_size[1]
        current_ratio = image.width / image.height

        if current_ratio > target_ratio:
            # Image is wider, crop width
            new_width = int(image.height * target_ratio)
            left = (image.width - new_width) // 2
            image = image.crop((left, 0, left + new_width, image.height))
        else:
            # Image is taller, crop height
            new_height = int(image.width / target_ratio)
            top = (image.height - new_height) // 2
            image = image.crop((0, top, image.width, top + new_height))

        return image.resize(target_size, Image.Resampling.LANCZOS)

    def _add_logo(
        self,
        image: Image.Image,
        position: LogoPosition,
        size_ratio: float
    ) -> Image.Image:
        """Add logo overlay to image."""
        logo = self._logo_white.copy()

        # Calculate logo size
        logo_width = int(image.width * size_ratio)
        logo_ratio = logo.height / logo.width
        logo_height = int(logo_width * logo_ratio)

        # Resize logo
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

        # Calculate position
        padding = int(image.width * 0.02)  # 2% padding

        if position == LogoPosition.TOP_LEFT:
            pos = (padding, padding)
        elif position == LogoPosition.TOP_RIGHT:
            pos = (image.width - logo_width - padding, padding)
        elif position == LogoPosition.TOP_CENTER:
            pos = ((image.width - logo_width) // 2, padding)  # Centered at top
        elif position == LogoPosition.BOTTOM_LEFT:
            pos = (padding, image.height - logo_height - padding - 40)  # Account for footer
        elif position == LogoPosition.BOTTOM_RIGHT:
            pos = (image.width - logo_width - padding, image.height - logo_height - padding - 40)
        else:  # CENTER
            pos = ((image.width - logo_width) // 2, (image.height - logo_height) // 2)

        # Create a semi-transparent version
        logo.putalpha(Image.eval(logo.split()[3], lambda x: int(x * 0.85)))

        # Paste logo
        image.paste(logo, pos, logo)

        return image

    def _add_footer(self, image: Image.Image, text: str) -> Image.Image:
        """Add brand footer to image - markettina GOLD & BLACK."""
        draw = ImageDraw.Draw(image)

        # Footer dimensions
        footer_height = 40
        footer_y = image.height - footer_height

        # Draw footer background (NERO markettina semi-transparent)
        footer_overlay = Image.new("RGBA", (image.width, footer_height), (10, 10, 10, 220))
        image.paste(footer_overlay, (0, footer_y), footer_overlay)

        # Draw gold accent line (ORO markettina)
        draw.line(
            [(0, footer_y), (image.width, footer_y)],
            fill=BRAND_COLORS["primary"],  # #D4AF37 Gold
            width=3
        )

        # Draw text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            font = ImageFont.load_default()

        # Center text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (image.width - text_width) // 2
        text_y = footer_y + (footer_height - 16) // 2

        draw.text((text_x, text_y), text, fill=BRAND_COLORS["primary"], font=font)

        return image

    def _add_brand_accent(self, image: Image.Image) -> Image.Image:
        """Add subtle brand accent (gold corner accents)."""
        draw = ImageDraw.Draw(image)
        accent_color = BRAND_COLORS["primary"]
        accent_length = int(image.width * 0.05)  # 5% of width
        accent_width = 3

        # Top-left corner
        draw.line([(0, 0), (accent_length, 0)], fill=accent_color, width=accent_width)
        draw.line([(0, 0), (0, accent_length)], fill=accent_color, width=accent_width)

        # Top-right corner
        draw.line([(image.width - accent_length, 0), (image.width, 0)], fill=accent_color, width=accent_width)
        draw.line([(image.width - 1, 0), (image.width - 1, accent_length)], fill=accent_color, width=accent_width)

        return image

    def create_social_template(
        self,
        platform: str,
        headline: str = "",
        subheadline: str = "",
        background_image: bytes | None = None,
    ) -> bytes:
        """
        Create a branded social media template.

        Args:
            platform: Target platform
            headline: Main text
            subheadline: Secondary text
            background_image: Optional background image

        Returns:
            Template image bytes
        """
        if not PIL_AVAILABLE:
            raise RuntimeError("PIL not available")

        size = SOCIAL_DIMENSIONS.get(platform, SOCIAL_DIMENSIONS["default"])

        # Create base image
        if background_image:
            image = Image.open(io.BytesIO(background_image)).convert("RGBA")
            image = self._resize_and_crop(image, size)

            # Add dark overlay for text readability
            overlay = Image.new("RGBA", size, (10, 10, 20, 150))
            image = Image.alpha_composite(image, overlay)
        else:
            # Gradient background
            image = self._create_gradient_background(size)

        draw = ImageDraw.Draw(image)

        # Add headline
        if headline:
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()

            # Center headline
            bbox = draw.textbbox((0, 0), headline, font=font_large)
            text_width = bbox[2] - bbox[0]
            text_x = (size[0] - text_width) // 2
            text_y = size[1] // 3

            # Draw shadow
            draw.text((text_x + 2, text_y + 2), headline, fill=(0, 0, 0, 128), font=font_large)
            draw.text((text_x, text_y), headline, fill=BRAND_COLORS["text_light"], font=font_large)

            # Subheadline
            if subheadline:
                bbox = draw.textbbox((0, 0), subheadline, font=font_small)
                text_width = bbox[2] - bbox[0]
                text_x = (size[0] - text_width) // 2
                text_y += 60

                draw.text((text_x, text_y), subheadline, fill=BRAND_COLORS["primary"], font=font_small)

        # Add logo
        if self._logo_white:
            image = self._add_logo(image, LogoPosition.BOTTOM_RIGHT, 0.12)

        # Add brand accents
        image = self._add_brand_accent(image)

        # Add footer
        image = self._add_footer(image, "MARKETTINA")

        # Convert to bytes
        output = io.BytesIO()
        image.convert("RGB").save(output, format="PNG", quality=95)
        output.seek(0)

        return output.getvalue()

    def _create_gradient_background(self, size: tuple[int, int]) -> Image.Image:
        """Create a branded gradient background."""
        image = Image.new("RGBA", size)
        draw = ImageDraw.Draw(image)

        # Vertical gradient from dark to darker (BLACK theme)
        for y in range(size[1]):
            ratio = y / size[1]
            r = int(10 * (1 - ratio * 0.3))
            g = int(10 * (1 - ratio * 0.3))
            b = int(10 * (1 - ratio * 0.2))
            draw.line([(0, y), (size[0], y)], fill=(r, g, b, 255))

        return image

    def create_business_dna_profile(
        self,
        company_name: str,
        tagline: str,
        website: str,
        fonts: list[str],
        colors: dict[str, str],
        brand_attributes: list[str],
        tone_of_voice: list[str],
        business_overview: str,
        logo_bytes: bytes | None = None,
        output_size: tuple[int, int] = (1920, 1080)
    ) -> bytes:
        """
        Create a BUSINESS DNA PROFILE visual like the example image.

        Generates a comprehensive brand identity board with:
        - Logo display (custom or default)
        - Color palette
        - Font showcase
        - Brand attributes tags
        - Tone of voice
        - Business overview
        - Professional dark theme with gold accents

        Args:
            company_name: Business name
            tagline: Company tagline
            website: Company website URL
            fonts: List of font names used in branding
            colors: Dict of color names and hex values (e.g., {"primary": "#D4AF37", "secondary": "#0A0A0A"})
            brand_attributes: List of brand characteristics (e.g., ["Professional", "Modern", "Innovative"])
            tone_of_voice: List of communication style descriptors (e.g., ["Confident", "Authentic"])
            business_overview: Brief company description
            logo_bytes: Optional custom logo image bytes (PNG/JPG)
            output_size: Image dimensions (default 1920x1080)

        Returns:
            Business DNA profile image bytes (PNG)
        """
        if not PIL_AVAILABLE:
            raise RuntimeError("PIL not available for Business DNA generation")

        # Load custom logo if provided, otherwise use default
        custom_logo = None
        if logo_bytes:
            try:
                custom_logo = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
                logger.info("Custom logo loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load custom logo: {e}, using default")

        # Create dark background
        image = Image.new("RGB", output_size, color=(32, 32, 32))  # Dark gray
        draw = ImageDraw.Draw(image)

        # Load fonts
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            font_heading = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font_title = ImageFont.load_default()
            font_heading = font_title
            font_body = font_title
            font_small = font_title

        # --- HEADER SECTION ---
        header_y = 60
        draw.text((60, header_y), company_name.upper(), fill=BRAND_COLORS["text_light"], font=font_title)
        draw.text((60, header_y + 60), website, fill=BRAND_COLORS["primary"], font=font_small)

        # Add "Your Business DNA" watermark
        watermark_x = output_size[0] - 400
        draw.text((watermark_x, 40), "Your Business DNA", fill=(128, 128, 128), font=font_small)
        draw.text((watermark_x, 60), "Here is a snapshot of your business DNA", fill=(96, 96, 96), font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12))
        draw.text((watermark_x, 78), "and how to build your social media campaigns.", fill=(96, 96, 96), font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12))

        # --- LOGO + FONTS SECTION (Left side, top) ---
        section_y = 180
        section_x = 60

        # Logo box - use custom logo if provided, otherwise default
        logo_to_use = custom_logo if custom_logo else self._logo
        logo_box_size = (350, 250)
        logo_box = Image.new("RGBA", logo_box_size, (45, 45, 50, 255))
        if logo_to_use:
            # Resize and center logo
            logo_resized = logo_to_use.copy()
            logo_resized.thumbnail((250, 200), Image.Resampling.LANCZOS)
            logo_x = (logo_box_size[0] - logo_resized.width) // 2
            logo_y = (logo_box_size[1] - logo_resized.height) // 2
            logo_box.paste(logo_resized, (logo_x, logo_y), logo_resized)
        image.paste(logo_box, (section_x, section_y), logo_box)

        # Fonts section
        fonts_y = section_y + logo_box_size[1] + 30
        draw.text((section_x, fonts_y), "Fonts", fill=BRAND_COLORS["text_light"], font=font_heading)
        for i, font_name in enumerate(fonts[:3]):  # Max 3 fonts
            draw.text((section_x, fonts_y + 50 + i * 35), "Aa", fill=BRAND_COLORS["primary"], font=font_title)
            draw.text((section_x + 80, fonts_y + 60 + i * 35), font_name, fill=BRAND_COLORS["text_light"], font=font_body)

        # --- IMAGES SECTION (Top right) ---
        images_x = section_x + 450
        draw.text((images_x, section_y - 40), "Images", fill=BRAND_COLORS["text_light"], font=font_heading)

        # Image placeholders (3 small squares)
        for i in range(3):
            img_x = images_x + i * 140
            img_box_size = (120, 120)
            img_placeholder = Image.new("RGB", img_box_size, (60, 60, 70))
            img_draw = ImageDraw.Draw(img_placeholder)

            # Add logo to placeholder
            if self._logo_white:
                logo_mini = self._logo_white.copy()
                logo_mini.thumbnail((80, 80), Image.Resampling.LANCZOS)
                logo_pos = ((img_box_size[0] - logo_mini.width) // 2, (img_box_size[1] - logo_mini.height) // 2)
                img_placeholder.paste(logo_mini, logo_pos, logo_mini)

            image.paste(img_placeholder, (img_x, section_y))

        # --- COLORS SECTION (Below images) ---
        colors_y = section_y + 180
        draw.text((images_x, colors_y), "Colors", fill=BRAND_COLORS["text_light"], font=font_heading)

        # Color swatches
        swatch_y = colors_y + 50
        swatch_size = 80
        for i, (color_name, color_hex) in enumerate(colors.items()):
            swatch_x = images_x + i * 120
            # Draw color swatch
            draw.rectangle(
                [(swatch_x, swatch_y), (swatch_x + swatch_size, swatch_y + swatch_size)],
                fill=color_hex
            )
            # Color name below
            draw.text((swatch_x, swatch_y + swatch_size + 10), color_hex, fill=BRAND_COLORS["text_light"], font=font_small)

        # --- TAGLINE SECTION (Below fonts) ---
        tagline_y = fonts_y + 150
        draw.text((section_x, tagline_y), "Tagline", fill=BRAND_COLORS["text_light"], font=font_heading)
        draw.text((section_x, tagline_y + 50), tagline, fill=BRAND_COLORS["primary"], font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", 20))

        # --- BRAND VOICES SECTION (Below colors) ---
        brand_voices_y = colors_y + 180
        draw.text((images_x, brand_voices_y), "Brand voices", fill=BRAND_COLORS["text_light"], font=font_heading)

        # Tags
        tag_y = brand_voices_y + 50
        tag_x = images_x
        for i, attribute in enumerate(brand_attributes[:5]):  # Max 5 attributes
            # Draw tag background
            tag_width = len(attribute) * 10 + 30
            draw.rounded_rectangle(
                [(tag_x, tag_y), (tag_x + tag_width, tag_y + 35)],
                radius=17,
                fill=(60, 60, 70)
            )
            draw.text((tag_x + 15, tag_y + 8), attribute, fill=BRAND_COLORS["text_light"], font=font_body)

            tag_x += tag_width + 15
            if tag_x > output_size[0] - 200:  # Wrap to next line
                tag_x = images_x
                tag_y += 50

        # --- BRAND ATTRIBUTES SECTION (Below tagline) ---
        attributes_y = tagline_y + 120
        draw.text((section_x, attributes_y), "Brand aesthetic", fill=BRAND_COLORS["text_light"], font=font_heading)

        # Tags
        tag_y = attributes_y + 50
        tag_x = section_x
        for attribute in tone_of_voice[:8]:  # Max 8 tone descriptors
            tag_width = len(attribute) * 9 + 25
            draw.rounded_rectangle(
                [(tag_x, tag_y), (tag_x + tag_width, tag_y + 32)],
                radius=16,
                fill=(60, 60, 70)
            )
            draw.text((tag_x + 12, tag_y + 7), attribute, fill=BRAND_COLORS["text_light"], font=font_body)

            tag_x += tag_width + 12
            if tag_x > section_x + 800:  # Wrap
                tag_x = section_x
                tag_y += 45

        # --- BUSINESS OVERVIEW SECTION (Bottom) ---
        overview_y = output_size[1] - 200
        draw.text((section_x, overview_y), "Business overview", fill=BRAND_COLORS["text_light"], font=font_heading)

        # Wrap text
        words = business_overview.split()
        lines = []
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            if draw.textbbox((0, 0), test_line, font=font_body)[2] < output_size[0] - 120:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))

        for i, line in enumerate(lines[:3]):  # Max 3 lines
            draw.text((section_x, overview_y + 50 + i * 30), line, fill=BRAND_COLORS["text_light"], font=font_body)

        # Convert to bytes
        output = io.BytesIO()
        image.save(output, format="PNG", quality=95)
        output.seek(0)

        logger.info(f"Business DNA profile created for {company_name}")
        return output.getvalue()


# Singleton instance
image_branding = ImageBranding()
