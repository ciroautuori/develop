#!/usr/bin/env python3
"""
Test script per il modello StudioCentOS AI custom.

Genera contenuti di esempio per ogni tipo di post e valida la qualità.
"""

import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Configurazione
MODEL_NAME = "autuoriciro/studiocentos-ai-qwen-3b"
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "your_token_here")

# Test prompts per ogni tipo di contenuto
TEST_PROMPTS = {
    "reel_script": [
        "Genera uno script per un Reel su come trovare clienti B2B su LinkedIn in 30 secondi",
        "Crea uno script TikTok virale per promuovere un servizio di AI per ristoranti",
    ],
    "story_sequence": [
        "Genera una sequenza di 4 storie Instagram per lanciare un nuovo servizio di branding",
        "Crea una sequenza Stories per promuovere un workshop gratuito sul marketing digitale",
    ],
    "carousel": [
        "Genera un carousel LinkedIn di 7 slide su 'Come usare l'AI nel tuo business'",
        "Crea un carousel Instagram educativo su 'Errori comuni nel social media marketing'",
    ],
    "linkedin_post": [
        "Scrivi un post LinkedIn B2B su come l'automazione può far risparmiare tempo agli studi professionali",
        "Genera un post controverso su LinkedIn sul futuro del marketing tradizionale vs digitale",
    ],
    "facebook_post": [
        "Crea un post Facebook storytelling per una pizzeria che ha aumentato il fatturato con l'AI",
        "Scrivi un post community per Facebook su come coinvolgere i clienti online",
    ],
}


def load_model():
    """Carica il modello custom da HuggingFace."""
    print(f"🔄 Caricamento modello: {MODEL_NAME}...")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        token=HF_TOKEN,
        trust_remote_code=True
    )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        token=HF_TOKEN,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("✅ Modello caricato!\n")
    return model, tokenizer


def generate_content(model, tokenizer, prompt, max_new_tokens=512, temperature=0.7):
    """Genera contenuto usando il modello."""
    # Format come durante il training
    formatted_prompt = f"<|im_start|>system\nSei un esperto di content creation e social media strategy per StudioCentOS.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Estrai solo la parte assistant
    if "<|im_start|>assistant" in response:
        response = response.split("<|im_start|>assistant")[-1].strip()
    if "<|im_end|>" in response:
        response = response.split("<|im_end|>")[0].strip()

    return response


def test_content_type(model, tokenizer, content_type, prompts):
    """Testa un tipo specifico di contenuto."""
    print("=" * 80)
    print(f"🎯 TEST: {content_type.upper().replace('_', ' ')}")
    print("=" * 80)

    results = []

    for i, prompt in enumerate(prompts, 1):
        print(f"\n📝 Prompt {i}: {prompt}")
        print("-" * 80)

        content = generate_content(model, tokenizer, prompt)

        print(f"✨ Output:\n{content}\n")

        results.append({
            "prompt": prompt,
            "output": content,
            "length": len(content),
        })

    return results


def main():
    """Esegue tutti i test."""
    print("\n" + "=" * 80)
    print("🧪 TEST STUDIOCENTOS AI CUSTOM MODEL")
    print("=" * 80 + "\n")

    # Carica modello
    model, tokenizer = load_model()

    # Esegui test per ogni tipo
    all_results = {}

    for content_type, prompts in TEST_PROMPTS.items():
        results = test_content_type(model, tokenizer, content_type, prompts)
        all_results[content_type] = results

    # Riepilogo
    print("\n" + "=" * 80)
    print("📊 RIEPILOGO TEST")
    print("=" * 80 + "\n")

    for content_type, results in all_results.items():
        print(f"\n{content_type.upper().replace('_', ' ')}:")
        for i, result in enumerate(results, 1):
            print(f"  Test {i}:")
            print(f"    - Lunghezza output: {result['length']} caratteri")
            print(f"    - Prompt: {result['prompt'][:60]}...")

    print("\n" + "=" * 80)
    print("✅ TEST COMPLETATI!")
    print("=" * 80)
    print("\n💡 Prossimi passi:")
    print("   1. Rivedi la qualità degli output")
    print("   2. Confronta con output Gemini (se disponibili)")
    print("   3. Decidi se procedere con l'integrazione completa\n")


if __name__ == "__main__":
    main()
