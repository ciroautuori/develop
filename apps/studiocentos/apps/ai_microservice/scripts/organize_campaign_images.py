#!/usr/bin/env python3
import shutil
from pathlib import Path
from PIL import Image

BRAIN_DIR = Path("/home/autcir_gmail_com/.gemini/antigravity/brain/4fea3494-9b97-4e13-96bb-f7478088fe63")
CAMPAIGN_DIR = Path("/home/autcir_gmail_com/studiocentos_ws/apps/ai_microservice/media/campaign_v2")
LOGO_PATH = Path("/home/autcir_gmail_com/studiocentos_ws/apps/ai_microservice/app/assets/brand/logo_white.png")

# Mapping of image files to kit folders
IMAGE_MAP = {
    "announcement_kit_visual": "01_announcement_kit",
    "problem_agitation_visual": "02_problem_agitation_kit",
    "case_study_visual": "03_case_study_kit",
    "educational_kit_visual": "04_educational_kit",
    "behind_scenes_visual": "05_behind_scenes_kit",
    "myth_busting_visual": "06_myth_busting_kit",
    "testimonial_visual": "07_testimonial_kit",
    "tutorial_visual": "08_tutorial_kit",
    "comparison_visual": "09_comparison_kit",
    "final_cta_visual": "10_final_cta_kit",
    "stories_background_visual": "11_stories_strategy",
}

def apply_logo(input_path: Path, output_path: Path):
    """Apply logo branding to image."""
    print(f"  🎨 Branding: {input_path.name}")
    
    image = Image.open(input_path).convert("RGBA")
    
    if not LOGO_PATH.exists():
        print(f"  ⚠️ Logo not found, saving without branding")
        image.convert("RGB").save(output_path)
        return
    
    logo = Image.open(LOGO_PATH).convert("RGBA")
    
    # Logo size (20% of width)
    size_ratio = 0.20
    logo_width = int(image.width * size_ratio)
    logo_ratio = logo.height / logo.width
    logo_height = int(logo_width * logo_ratio)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
    
    # Position: Bottom Center
    padding = int(image.height * 0.05)
    x = (image.width - logo_width) // 2
    y = image.height - logo_height - padding
    
    # Paste logo
    image.paste(logo, (x, y), logo)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    image.convert("RGB").save(output_path, quality=95)
    print(f"  ✅ Saved: {output_path.name}")

def main():
    print("🚀 Organizing and Branding Campaign Images\n")
    
    for image_prefix, kit_name in IMAGE_MAP.items():
        # Find the image file
        image_files = list(BRAIN_DIR.glob(f"{image_prefix}_*.png"))
        
        if not image_files:
            print(f"⚠️ No image found for {kit_name}")
            continue
        
        input_image = image_files[0]
        output_dir = CAMPAIGN_DIR / kit_name
        output_file = output_dir / "02_visual_generated.png"
        
        print(f"📦 {kit_name}")
        apply_logo(input_image, output_file)
        print()
    
    print("✨ All images organized and branded!")

if __name__ == "__main__":
    main()
