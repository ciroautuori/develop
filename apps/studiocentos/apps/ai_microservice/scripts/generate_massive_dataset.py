#!/usr/bin/env python3
"""
Massive Dataset Generator for StudioCentOS Content AI.

Generates high-quality, structured synthetic data for social media formats
that are missing from public datasets:
- Viral Reels/TikTok Scripts (Hook > Value > CTA)
- Instagram Stories Sequences
- LinkedIn Carousels
- Facebook Storytelling

Output: data/studiocentos_vertical_dataset.jsonl
"""

import json
import random
import os
from pathlib import Path
from typing import List, Dict

# ==============================================================================
# 🧠 BRAIN: TEMPLATES & PATTERNS
# ==============================================================================

SECTORS = [
    "Ristorazione", "Hospitality", "Studi Legali", "Commercialisti", "Tech Startup",
    "E-commerce", "Real Estate", "Fitness", "Beauty", "Consulenza"
]

TOPICS = {
    "Ristorazione": ["food cost", "sprechi", "recensioni", "delivery", "Instagram food", "menu engineering"],
    "Hospitality": ["booking dirette", "ota commissioni", "guest experience", "destagionalizzazione", "pricing"],
    "Studi Legali": ["automazione documenti", "clienti difficili", "gestione tempo", "marketing legale", "tariffe"],
    "Commercialisti": ["fatturazione elettronica", "scadenze fiscali", "consulenza vs data entry", "AI per studio"],
    "Tech Startup": ["fundraising", "mvp", "product market fit", "growth hacking", "remote work"],
    "General": ["produttività", "AI tools", "motivazione", "leadership", "vendita"]
}

# --- REELS / TIKTOK TEMPLATES ---
REEL_HOOKS = [
    "Scommetto che non sapevi questo su {topic}...",
    "L'errore numero 1 che vedo fare in {sector}...",
    "Come ho risparmiato 10k in {sector} usando l'AI...",
    "3 app gratuite per {topic} che devi scaricare ORA.",
    "Basta perdere tempo con {topic}! Fai così...",
    "Il segreto che i guru di {sector} non ti dicono.",
    "POV: Sei un {sector} e scopri l'automazione.",
    "Stop a {topic} manuale. Ecco il workflow automatico.",
]

REEL_STRUCTURES = [
    """[VIDEO: Primo piano, testo a comparsa veloce]
HOOK: {hook}

[VIDEO: Screen recording del tool / processo]
BODY: La maggior parte fa X. Sbagliato.
Devi fare Y.
Guarda questo risultato: +40% in 10 giorni.

[VIDEO: Speaker torna in camera]
CTA: Ho preparato una guida su questo. Commenta "GUIDA" e te la mando!""",

    """[VIDEO: Green screen con notizia di settore]
HOOK: {hook}

[VIDEO: Speaker indica grafico]
BODY: I dati parlano chiaro. Il trend è questo.
Se non ti adegui ora, tra 6 mesi sei fuori.

[VIDEO: Testo sovraimpresso: 3 STEP DA FARE]
1. Analizza i tuoi dati
2. Implementa questo tool
3. Misura il ROI

CTA: Salva il video per non perderlo!""",
]

# --- LINKEDIN CAROUSEL TEMPLATES ---
CAROUSEL_TITLES = [
    "La guida definitiva a {topic} (in 5 slide)",
    "7 tool AI per {sector} che sembrano illegali",
    "Come ho automatizzato {topic} in 24 ore",
    "Il framework 'StudioCentOS' per {topic}",
    "{topic}: Guida pratica per boomer",
]

# --- INSTAGRAM STORIES TEMPLATES ---
STORY_SEQUENCES = [
    [
        "Slide 1 [POLL]: Quanti di voi lottano con {topic} oggi? (Si/No)",
        "Slide 2 [VIDEO]: Anche io ci passavo. È frustrante perché...",
        "Slide 3 [TEXT]: Ecco la soluzione che ho trovato: [Nome Soluzione]",
        "Slide 4 [LINK]: Ho registrato un video di 2 min. Swipe up!"
    ],
    [
        "Slide 1 [QUIZ]: Sai quanto costa un errore in {topic}? (A: 100€, B: 1000€)",
        "Slide 2 [RESULT]: Risposta esatta: B! Ecco perché...",
        "Slide 3 [DM ME]: Chi vuole la checklist gratuita per evitarlo?",
        "Slide 4 [COUNTDOWN]: La mando solo per 24h!"
    ]
]


def generate_reels(count: int) -> List[Dict]:
    """Generate viral short-form video scripts."""
    print(f"   Generating {count} Reels/TikTok scripts...")
    data = []

    for _ in range(count):
        sector = random.choice(SECTORS)
        # Mix specific and general topics
        topic_list = TOPICS.get(sector, []) + TOPICS["General"]
        topic = random.choice(topic_list)

        hook_template = random.choice(REEL_HOOKS)
        hook = hook_template.format(topic=topic, sector=sector)

        structure = random.choice(REEL_STRUCTURES)
        content = structure.format(hook=hook)

        # Determine platform
        platform = random.choice(["tiktok", "instagram", "youtube_shorts"])

        data.append({
            "messages": [
                {"role": "system", "content": f"Sei un esperto di Viral Marketing per {sector}. Genera uno script per short video ({platform}) ad alto engagement."},
                {"role": "user", "content": f"Genera script video su: {topic}"},
                {"role": "assistant", "content": content}
            ],
            "post_type": "reel_script",
            "platform": platform,
            "sector": sector,
            "engagement_score": random.randint(85, 99)
        })
    return data


def generate_stories(count: int) -> List[Dict]:
    """Generate Instagram Story sequences."""
    print(f"   Generating {count} Story sequences...")
    data = []

    for _ in range(count):
        sector = random.choice(SECTORS)
        topic = random.choice(TOPICS.get(sector, []) + TOPICS["General"])
        sequence = random.choice(STORY_SEQUENCES)

        # Format sequence
        formatted_seq = "\n\n---\n\n".join([s.format(topic=topic) for s in sequence])

        data.append({
            "messages": [
                {"role": "system", "content": f"Sei un Social Media Manager per {sector}. Genera una sequenza di Instagram Stories per generare lead."},
                {"role": "user", "content": f"Crea sequenza storie su: {topic}"},
                {"role": "assistant", "content": formatted_seq}
            ],
            "post_type": "story_sequence",
            "platform": "instagram",
            "sector": sector,
            "engagement_score": random.randint(80, 95)
        })
    return data


def generate_carousels(count: int) -> List[Dict]:
    """Generate Carousel structures (LinkedIn/IG)."""
    print(f"   Generating {count} Carousels...")
    data = []

    for _ in range(count):
        sector = random.choice(SECTORS)
        topic = random.choice(TOPICS.get(sector, []) + TOPICS["General"])
        title = random.choice(CAROUSEL_TITLES).format(topic=topic, sector=sector)

        content = f"""SLIDE 1 (Copertina):
TITOLO: {title}
SUB: Scorri per imparare -->

SLIDE 2 (Problema):
Tutti pensano che {topic} sia difficile.
Ecco perché sbagliano.

SLIDE 3 (Soluzione):
La tecnica ABC:
1. Analizza
2. Bilancia
3. Chiudi

SLIDE 4 (Esempio):
Case study {sector}:
Prima: 0 risultati
Dopo: +50% crescita

SLIDE 5 (CTA):
Ti è stato utile?
[Salva] [Condividi] [Commenta]"""

        platform = random.choice(["linkedin", "instagram"])

        data.append({
            "messages": [
                {"role": "system", "content": f"Sei un Content Creator B2B per {sector}. Genera un carosello educativo."},
                {"role": "user", "content": f"Crea carosello su: {topic}"},
                {"role": "assistant", "content": content}
            ],
            "post_type": "carousel",
            "platform": platform,
            "sector": sector,
            "engagement_score": random.randint(88, 98)
        })
    return data


def generate_viral_posts(count: int) -> List[Dict]:
    """Generate Viral Text Posts (LinkedIn/FB)."""
    print(f"   Generating {count} Viral Posts...")
    data = []

    for _ in range(count):
        sector = random.choice(SECTORS)
        topic = random.choice(TOPICS.get(sector, []) + TOPICS["General"])

        content = f"""Ho licenziato il mio migliore cliente oggi.

Ecco perché (lezione per {sector}):

Mi chiedeva di fare {topic} gratis.
"Ti darà visibilità", diceva.

La visibilità non paga le bollette.
La qualità si paga.

Se sei un professionista in {sector}, ricorda:
Il tuo valore è quello che accetti.

Siete d'accordo? 👇

#business #{topic.replace(" ", "")} #mindset"""

        platform = random.choice(["linkedin", "facebook"])

        data.append({
            "messages": [
                {"role": "system", "content": f"Sei un Opinion Leader in {sector}. Scrivi un post controverso e virale."},
                {"role": "user", "content": f"Scrivi post su: {topic}"},
                {"role": "assistant", "content": content}
            ],
            "post_type": "viral_post",
            "platform": platform,
            "sector": sector,
            "engagement_score": random.randint(90, 99)
        })
    return data


def main():
    print("="*60)
    print("🚀 StudioCentOS Massive Dataset Generator")
    print("="*60)

    # Calculate targets
    reels_count = 150
    stories_count = 100
    carousels_count = 100
    viral_count = 150
    total = reels_count + stories_count + carousels_count + viral_count

    print(f"🎯 Target: {total} High-Quality Examples")

    dataset = []
    dataset.extend(generate_reels(reels_count))
    dataset.extend(generate_stories(stories_count))
    dataset.extend(generate_carousels(carousels_count))
    dataset.extend(generate_viral_posts(viral_count))

    # Output path
    output_file = Path(__file__).parent.parent / "data" / "studiocentos_vertical_dataset.jsonl"

    print(f"\n💾 Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✅ DONE! Generated {len(dataset)} examples.")


if __name__ == "__main__":
    main()
