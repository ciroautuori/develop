
import sys
import os
from pathlib import Path
from PIL import Image

# Add parent to path for branding (or just duplicate class as it's small)
# Let's just duplicate to be safe and standalone
LOGO_PATH = Path("/home/autcir_gmail_com/studiocentos_ws/apps/ai_microservice/app/assets/brand/logo_white.png")

def apply_branding(input_path: str, output_path: str):
    print(f"Branding {input_path} -> {output_path}")

    try:
        image = Image.open(input_path).convert("RGBA")

        if not LOGO_PATH.exists():
            print(f"Error: Logo not found at {LOGO_PATH}")
            image.save(output_path)
            return

        logo = Image.open(LOGO_PATH).convert("RGBA")

        # Calculate logo size (15% width)
        size_ratio = 0.20 # A bit larger
        logo_width = int(image.width * size_ratio)
        logo_ratio = logo.height / logo.width
        logo_height = int(logo_width * logo_ratio)
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

        # Position: Bottom Center
        padding = int(image.height * 0.05)
        x = (image.width - logo_width) // 2
        y = image.height - logo_height - padding

        # Transparency (90%)
        # logo.putalpha(Image.eval(logo.split()[3], lambda x: int(x * 0.9)))

        image.paste(logo, (x, y), logo)
        image.convert("RGB").save(output_path)
        print("Done.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 brand_image.py <input> <output>")
        sys.exit(1)

    apply_branding(sys.argv[1], sys.argv[2])
