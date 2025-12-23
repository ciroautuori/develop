#!/usr/bin/env python3
"""
Quick test dello SC AI custom model.
Usage: python scripts/quick_test_model.py
"""

import asyncio
from app.domain.marketing.content_creator import ContentCreatorAgent, SocialPostConfig, SocialPlatform, ContentTone
from app.core.config import settings

async def test_model():
    print("🧪 TEST STUDIOCENTOS AI CUSTOM MODEL\n")
    print(f"✅ USE_CUSTOM_MODEL: {settings.USE_CUSTOM_MODEL}")
    print(f"✅ MODEL NAME: {settings.HUGGINGFACE_MODEL_NAME}\n")

    agent = ContentCreatorAgent()

    # Test 1: Post LinkedIn
    print("=" * 60)
    print("📝 TEST 1: LinkedIn Post")
    print("=" * 60)

    config = SocialPostConfig(
        platform=SocialPlatform.LINKEDIN,
        message="Come l'AI può automatizzare la gestione clienti per studi professionali",
        post_type="tip_giorno",
        tone=ContentTone.PROFESSIONAL
    )

    result = await agent.generate_social_post(config)
    print(f"\n✨ OUTPUT:\n{result.content}\n")
    print(f"📊 Brand Compliance: {result.brand_compliance}")
    print(f"📏 Length: {len(result.content)} chars\n")

    # Test 2: Post Instagram
    print("=" * 60)
    print("📸 TEST 2: Instagram Post")
    print("=" * 60)

    config2 = SocialPostConfig(
        platform=SocialPlatform.INSTAGRAM,
        message="La tua azienda ha bisogno di un'AI che funziona davvero",
        post_type="lancio_prodotto",
        tone=ContentTone.FRIENDLY,
        include_emojis=True
    )

    result2 = await agent.generate_social_post(config2)
    print(f"\n✨ OUTPUT:\n{result2.content}\n")
    print(f"📊 Brand Compliance: {result2.brand_compliance}")
    print(f"📏 Length: {len(result2.content)} chars\n")

    print("=" * 60)
    print("✅ TEST COMPLETATI!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_model())
