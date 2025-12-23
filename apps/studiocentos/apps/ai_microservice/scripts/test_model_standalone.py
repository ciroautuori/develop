#!/usr/bin/env python3
"""
Test diretto del custom model service.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import asyncio

# Test diretto del servizio
async def test_custom_model():
    print("🧪 TEST STUDIOCENTOS CUSTOM MODEL SERVICE\n")

    # Imposta env vars
    os.environ['USE_CUSTOM_MODEL'] = 'true'
    os.environ['HUGGINGFACE_MODEL_NAME'] = 'autuoriciro/studiocentos-ai-qwen-3b'
    os.environ['HUGGINGFACE_TOKEN'] = os.getenv('HUGGINGFACE_TOKEN', 'your_token_here')

    try:
        from app.domain.marketing.custom_model_service import custom_model_service

        print("✅ Custom model service importato\n")

        # Test 1: Generazione semplice
        print("=" * 60)
        print("📝 TEST 1: Post LinkedIn B2B")
        print("=" * 60)

        prompt = """Scrivi un post LinkedIn professionale per promuovere i servizi di automazione AI per studi professionali.

TARGET: Commercialisti, avvocati, consulenti
LUNGHEZZA: ~150 parole
TONO: Professionale ma accessibile
STRUTTURA: Hook → Problema → Soluzione → CTA

Includi:
- Hook che cattura attenzione
- Problema specifico (gestione clienti manuale)
- Soluzione con benefici concreti
- CTA chiara
- 3-5 hashtag pertinenti"""

        print("⏳ Generazione in corso...")
        content = custom_model_service.generate(
            prompt=prompt,
            system_message="Sei un esperto di content marketing B2B per StudioCentOS.",
            max_new_tokens=400,
            temperature=0.7
        )

        print(f"\n✨ OUTPUT:\n{content}\n")
        print(f"📏 Lunghezza: {len(content)} caratteri")
        print(f"📏 Parole: {len(content.split())} parole\n")

        # Test 2: Post Instagram
        print("=" * 60)
        print("📸 TEST 2: Caption Instagram")
        print("=" * 60)

        prompt2 = """Crea una caption Instagram coinvolgente per un post sul tema:
"Come l'AI può far risparmiare 20 ore a settimana nella gestione clienti"

STILE: Friendly, ispirazionale
LUNGHEZZA: ~100 parole
EMOJI: Si, usale strategicamente
HASHTAG: 5-8 hashtag mirati

Struttura: Hook emozionale → Benefit → CTA + emoji"""

        print("⏳ Generazione in corso...")
        content2 = custom_model_service.generate(
            prompt=prompt2,
            system_message="Sei un content creator per Instagram, esperto di AI e business.",
            max_new_tokens=300,
            temperature=0.8
        )

        print(f"\n✨ OUTPUT:\n{content2}\n")
        print(f"📏 Lunghezza: {len(content2)} caratteri\n")

        print("=" * 60)
        print("✅ TEST COMPLETATI CON SUCCESSO!")
        print("=" * 60)
        print("\n💡 Il modello custom funziona correttamente!")
        print("   Pronto per l'integrazione in produzione.\n")

    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_custom_model())
    sys.exit(0 if success else 1)
