#!/usr/bin/env python3
"""Apply branding to regenerated images and move them to campaign folders."""

import shutil
from pathlib import Path
from PIL import Image
import io

BRAIN_DIR = Path("/home/autcir_gmail_com/.gemini/antigravity/brain/4fea3494-9b97-4e13-96bb-f7478088fe63")
CAMPAIGN_DIR = Path("/home/autcir_gmail_com/studiocentos_ws/apps/ai_microservice/media/campaign_v2")
LOGO_PATH = Path("/home/autcir_gmail_com/studiocentos_ws/apps/ai_microservice/app/assets/brand/logo_white.png")

# Mapping of source images to destination kits
IMAGE_MAP = {
    "announcement_kit_v2": "01_announcement_kit",
    "case_study_infographic_v2": "03_case_study_kit",
    "myth_busting_v2_retry": "06_myth_busting_kit",
    "final_cta_realistic_v2": "10_final_cta_kit",
}

def apply_logo(input_path: Path, output_path: Path):
    """Apply logo branding."""
    print(f"  🎨 Branding: {input_path.name}")
    
    image = Image.open(input_path).convert("RGBA")
    
    if not LOGO_PATH.exists():
        print(f"  ⚠️ Logo not found")
        image.convert("RGB").save(output_path)
        return
    
    logo = Image.open(LOGO_PATH).convert("RGBA")
    
    size_ratio = 0.20
    logo_width = int(image.width * size_ratio)
    logo_ratio = logo.height / logo.width
    logo_height = int(logo_width * logo_ratio)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
    
    padding = int(image.height * 0.05)
    x = (image.width - logo_width) // 2
    y = image.height - logo_height - padding
    
    image.paste(logo, (x, y), logo)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output_path, quality=95)
    print(f"  ✅ Saved to: {output_path.relative_to(CAMPAIGN_DIR.parent)}")

def main():
    print("🚀 Applying Branding to Regenerated Images\n")
    
    for image_prefix, kit_name in IMAGE_MAP.items():
        image_files = list(BRAIN_DIR.glob(f"{image_prefix}_*.png"))
        
        if not image_files:
            print(f"⚠️ No image found for pattern: {image_prefix}")
            continue
        
        input_image = image_files[0]
        output_file = CAMPAIGN_DIR / kit_name / "02_visual_generated.png"
        
        print(f"📦 {kit_name}")
        apply_logo(input_image, output_file)
        print()
    
    print("✨ Branding complete!")

if __name__ == "__main__":
    main()
