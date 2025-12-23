
import asyncio
import os
import re
import shutil
import base64
import json
import time
import requests
import io
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Literal
from enum import Enum

# ============================================================================
# STANDALONE IMAGE BRANDING CLASS (Copied to avoid dependencies)
# ============================================================================

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL (Pillow) not installed. Branding will be disabled.")

# Brand Colors
BRAND_COLORS = {
    "primary": "#D4AF37",      # Gold
    "secondary": "#0A0A0A",    # Black
    "text_light": "#FAFAFA",
}

class LogoPosition(str, Enum):
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    TOP_CENTER = "top_center"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    BOTTOM_CENTER = "bottom_center"
    CENTER = "center"

class ImageBranding:
    def __init__(self, logo_path: Path):
        self.logo_path = logo_path
        self._logo = None
        if PIL_AVAILABLE and self.logo_path.exists():
            try:
                self._logo = Image.open(self.logo_path).convert("RGBA")
                print(f"✅ Loaded logo from {self.logo_path}")
            except Exception as e:
                print(f"❌ Failed to load logo: {e}")

    def apply_branding(self, image_bytes: bytes, platform: str = "default", logo_position=LogoPosition.BOTTOM_CENTER) -> bytes:
        if not PIL_AVAILABLE or not self._logo:
            return image_bytes

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

            # Simple branding: Add logo
            # Calculate logo size
            logo = self._logo.copy()
            size_ratio = 0.15
            logo_width = int(image.width * size_ratio)
            logo_ratio = logo.height / logo.width
            logo_height = int(logo_width * logo_ratio)
            logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

            # Position
            padding = int(image.width * 0.05)
            # Bottom Center
            x = (image.width - logo_width) // 2
            y = image.height - logo_height - padding

            # Transparency
            if logo.mode == 'RGBA':
                 # make it slightly transparent
                 logo.putalpha(Image.eval(logo.split()[3], lambda x: int(x * 0.9)))

            image.paste(logo, (x, y), logo)

            # Output
            output = io.BytesIO()
            image.convert("RGB").save(output, format="PNG", quality=95)
            output.seek(0)
            return output.getvalue()

        except Exception as e:
            print(f"❌ Branding failed: {e}")
            return image_bytes

# ============================================================================
# MAIN SCRIPT
# ============================================================================

# Configuration
PROMPTS_LIB_DIR = Path("/home/autcir_gmail_com/studiocentos_ws/prompts_library/03_launch_campaign_v2")
OUTPUT_DIR = Path("/home/autcir_gmail_com/studiocentos_ws/apps/ai_microservice/media/campaign_v2")
LOGO_PATH = Path("/home/autcir_gmail_com/studiocentos_ws/apps/ai_microservice/app/assets/brand/logo_white.png")

# API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")

async def main():
    print("🚀 Starting Launch Campaign V2 Generation (No Deps)...")

    branding = ImageBranding(LOGO_PATH)

    # Create output directory
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Process each kit
    files = sorted([f for f in PROMPTS_LIB_DIR.glob("*.md")])

    for file_path in files:
        await process_kit(file_path, branding)

    print("\n✨ Campaign Generation Complete!")
    print(f"📂 Output directory: {OUTPUT_DIR}")

async def process_kit(file_path: Path, branding: ImageBranding):
    kit_name = file_path.stem
    print(f"\n📦 Processing Kit: {kit_name}...")

    kit_dir = OUTPUT_DIR / kit_name
    kit_dir.mkdir(exist_ok=True)

    content = file_path.read_text()
    (kit_dir / "original_prompt.md").write_text(content)

    # Copy
    copy_section = extract_section(content, "COPY GENERATION")
    if copy_section:
        (kit_dir / "01_copy_text.txt").write_text(copy_section)

    # Image
    image_prompt = extract_section(content, "IMAGE GENERATION") or extract_section(content, "IMAGE PROMPT")
    if image_prompt and GOOGLE_API_KEY:
        clean_prompt = extract_code_block(image_prompt)
        print(f"  🎨 Generating: {clean_prompt[:50]}...")

        width, height = 1080, 1080
        if "Story" in image_prompt:
             width, height = 1080, 1920

        image_bytes = await generate_image_google(clean_prompt, width, height)
        if image_bytes:
            branded_bytes = branding.apply_branding(image_bytes)
            (kit_dir / "02_visual_generated.png").write_bytes(branded_bytes)
            print("  ✅ Image Saved")
        else:
            print("  ❌ Image Generation skipped/failed")

    # Video
    video_prompt = extract_section(content, "VIDEO GENERATION") or extract_section(content, "VIDEO PROMPT") or extract_section(content, "REEL SCRIPT")
    if video_prompt:
        (kit_dir / "03_video_script.md").write_text(video_prompt)

async def generate_image_google(prompt: str, width: int, height: int) -> Optional[bytes]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GOOGLE_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"Generate a high quality image of: {prompt}"}]}],
        "generationConfig": {"temperature": 1.0}
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"  API Error: {response.text}")
            return None

        data = response.json()
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                if "inlineData" in part:
                     return base64.b64decode(part["inlineData"]["data"])
        return None
    except Exception as e:
        print(f"  Gen Error: {e}")
        return None

def extract_section(content: str, section_name: str) -> Optional[str]:
    # Use re.escape for section_name but handle regex pattern
    # Simply looking for ## ... section ...
    lines = content.split('\n')
    in_section = False
    section_lines = []

    for line in lines:
        if line.startswith("##") and section_name.lower() in line.lower():
            in_section = True
            continue
        if in_section and line.startswith("##"):
            break
        if in_section:
            section_lines.append(line)

    return "\n".join(section_lines).strip() if section_lines else None

def extract_code_block(text: str) -> str:
    match = re.search(r"```(?:text)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text

if __name__ == "__main__":
    asyncio.run(main())
