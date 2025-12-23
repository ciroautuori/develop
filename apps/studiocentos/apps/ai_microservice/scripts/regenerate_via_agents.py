#!/usr/bin/env python3
"""
Regenerate problematic campaign images using AI Microservice Agents.
This script calls the AI microservice API endpoints to use the actual ImageGeneratorAgent.
"""

import requests
import json
from pathlib import Path
from PIL import Image
import io

MICROSERVICE_URL = "http://localhost:8002"
LOGO_PATH = Path("/home/autcir_gmail_com/studiocentos_ws/apps/ai_microservice/app/assets/brand/logo_white.png")
OUTPUT_DIR = Path("/home/autcir_gmail_com/studiocentos_ws/apps/ai_microservice/media/campaign_v2")

# Improved prompts for the 4 problematic images
IMPROVED_PROMPTS = {
    "01_announcement_kit": {
        "prompt": """Create a bold social media graphic for Instagram post.
CRITICAL: The image MUST contain large, prominent text that says "SIAMO TORNATI" in the center.
Typography: Inter Bold font style, huge letters, center-aligned.
Text color: White or Gold (#D4AF37) with strong contrast.
Background: Deep matte black (#0A0A0A) with subtle golden wireframe geometric patterns in corners only.
Lighting: Cinematic rim lighting making the text pop and glow.
Style: Minimalist, high-tech, premium. Apple product launch aesthetic.
Format: Square 1080x1080.
NEGATIVE: NO other text, no cluttered elements, no rainbow colors, no cartoon style.
REQUIREMENT: The text "SIAMO TORNATI" must be clearly readable and the main focus.""",
        "width": 1080,
        "height": 1080
    },
    
    "03_case_study_kit": {
        "prompt": """Create a business infographic showing 4 data metrics clearly.
CRITICAL: Must show these exact numbers prominently:
- "+650% ROI" in large text with green/gold color
- "89h Saved" in large text with blue/gold color  
- "+42% Satisfaction" in large text
- "78% Automated" in large text

Layout: 4 separate boxes/cards floating in space, each with ONE metric.
Typography: Numbers should be HUGE (like 72pt+), very bold and readable.
Background: Dark (#0A0A0A) with subtle glassmorphism effect.
Style: Modern business dashboard, clean infographic design.
Colors: Gold (#D4AF37) primary, with green and cyan accents for variety.
Format: Square 1080x1080.
NEGATIVE: No abstract shapes without numbers, no unreadable text, no cluttered designs.
REQUIREMENT: All 4 numbers must be crystal clear and immediately readable.""",
        "width": 1080,
        "height": 1080
    },
    
    "06_myth_busting_kit": {
        "prompt": """Create a high-contrast YouTube-style thumbnail for myth busting.
CRITICAL: Must show prominent text:
- Left side: "MITO" or "MYTH" in RED neon style, large bold letters
- Right side: "REALTÀ" or "REALITY" in GOLD (#D4AF37), large elegant letters

Layout: Split screen or versus layout.
Typography: Very bold, large text (like 96pt), maximum readability.
Background: Dark tech abstract background with energy/pulsing effect.
Visual effects: Red text should have neon glow, Gold text should have premium shine.
Style: YouTube thumbnail aesthetic - high contrast, eye-catching, bold.
Format: Square 1080x1080.
NEGATIVE: No small text, no low contrast, no subtle designs.
REQUIREMENT: Both "MYTH" and "REALITY" text must be immediately visible and readable.""",
        "width": 1080,
        "height": 1080
    },
    
    "10_final_cta_kit": {
        "prompt": """Create a business decision concept illustration - professional and realistic.
Subject: A realistic business crossroads or fork in the road.
Left path: Grey, foggy, representing status quo/stagnation. Show office desk with paperwork piling up.
Right path: Illuminated by warm golden light (#D4AF37), representing AI transformation. Show modern clean workspace with digital screens showing positive metrics.

Style: Professional photography style, NOT fantasy art. Corporate business imagery.
Mood: Serious business decision, concrete and realistic.
Lighting: Natural office lighting on left, premium warm golden light on right.
Format: Square 1080x1080.
NEGATIVE: No fantasy cities, no sci-fi elements, no cartoon, no video game aesthetics.
REQUIREMENT: Must look like a real business scenario, not concept art.""",
        "width": 1080,
        "height": 1080
    }
}

def apply_logo(image_bytes: bytes) -> bytes:
    """Apply logo branding to image bytes."""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    
    if not LOGO_PATH.exists():
        print(f"  ⚠️ Logo not found")
        output = io.BytesIO()
        image.convert("RGB").save(output, format="PNG")
        output.seek(0)
        return output.getvalue()
    
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
    
    output = io.BytesIO()
    image.convert("RGB").save(output, format="PNG", quality=95)
    output.seek(0)
    return output.getvalue()

def generate_via_agent(kit_name: str, config: dict):
    """Call the AI Microservice ImageGeneratorAgent API."""
    print(f"\n📦 {kit_name}")
    print(f"  🤖 Calling ImageGeneratorAgent...")
    
    # Call the marketing image generation endpoint
    endpoint = f"{MICROSERVICE_URL}/api/v1/marketing/image/generate"
    
    payload = {
        "prompt": config["prompt"],
        "style": "professional",
        "width": config["width"],
        "height": config["height"],
        "apply_branding": False  # We'll apply manually to have more control
    }
    
    try:
        response = requests.post(endpoint, json=payload, timeout=60)
        
        if response.status_code != 200:
            print(f"  ❌ API Error: {response.status_code}")
            print(f"     {response.text[:200]}")
            return False
        
        result = response.json()
        
        # Download the generated image
        image_url = result.get("image_url", "")
        
        if image_url.startswith("http"):
            img_response = requests.get(image_url)
            image_bytes = img_response.content
        else:
            # It's a local file path
            local_path = image_url.replace("http://localhost:8002/", "")
            with open(local_path, "rb") as f:
                image_bytes = f.read()
        
        # Apply branding
        print(f"  🎨 Applying logo...")
        branded_bytes = apply_logo(image_bytes)
        
        # Save
        output_path = OUTPUT_DIR / kit_name / "02_visual_generated.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(branded_bytes)
        
        print(f"  ✅ Regenerated and saved!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("🚀 Regenerating Campaign Images via AI Microservice Agents\n")
    print("Using ImageGeneratorAgent API endpoints...\n")
    
    # Check if service is running
    try:
        health = requests.get(f"{MICROSERVICE_URL}/health", timeout=2)
        print(f"✅ Microservice is running\n")
    except:
        print(f"❌ ERROR: AI Microservice not running at {MICROSERVICE_URL}")
        print(f"Please start the service first with: cd apps/ai_microservice && uvicorn app.main:app --port 8002")
        return
    
    success_count = 0
    for kit_name, config in IMPROVED_PROMPTS.items():
        if generate_via_agent(kit_name, config):
            success_count += 1
    
    print(f"\n✨ Regeneration complete: {success_count}/{len(IMPROVED_PROMPTS)} successful")

if __name__ == "__main__":
    main()
