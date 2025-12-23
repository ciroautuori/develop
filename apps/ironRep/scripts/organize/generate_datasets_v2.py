#!/usr/bin/env python3
"""
Dataset Generator using OpenRouter API (Google Gemini/DeepSeek)
Generates comprehensive datasets for IronRep:
1. Movement Standards for ALL injuries (8 types)
2. Fitness Recipes with complete macros
3. Nutrition guidelines for athletes
4. Rehab protocols
"""

import json
import os
import time
import requests
from pathlib import Path

# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyBd2PX97FoHO-lnnROTCFr6MCxqsCzam-o")

# Output paths
DATA_DIR = Path(__file__).parent.parent / "apps/backend/data"
KB_DIR = DATA_DIR / "knowledge_base"
FINAL_DIR = DATA_DIR / "final"

# Ensure directories exist
KB_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)


def generate_with_openrouter(prompt: str, model: str = "google/gemini-2.0-flash-001") -> str:
    """Generate content using OpenRouter API."""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "Sei un esperto di fitness, nutrizione sportiva e medicina dello sport. Genera contenuti dettagliati, scientificamente accurati e pratici. Rispondi sempre in italiano."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 8000
        }
    )

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

    return response.json()["choices"][0]["message"]["content"]


def generate_movement_standards():
    """Generate complete movement standards for ALL 8 injuries."""

    movements = [
        ("SQUAT", "Air Squat, Front Squat, Back Squat, Overhead Squat"),
        ("DEADLIFT", "Conventional, Sumo, Romanian, Trap Bar"),
        ("PRESS", "Shoulder Press, Push Press, Push Jerk, Bench Press"),
        ("OLYMPIC_LIFTS", "Clean, Snatch, Clean & Jerk"),
        ("PULL_UPS", "Strict, Kipping, Chest-to-Bar, Muscle-Up"),
        ("BOX_JUMPS", "Box Jump, Step-Up, Burpee Box Jump"),
        ("RUNNING", "Sprint, Jog, Shuttle Run"),
        ("ROWING", "Row Machine, Single Arm Row, Barbell Row"),
        ("CORE", "Sit-ups, Toes-to-Bar, GHD, Plank"),
        ("LUNGES", "Walking Lunge, Reverse Lunge, Bulgarian Split Squat"),
        ("KETTLEBELL", "Swing, Goblet Squat, Turkish Get-Up")
    ]

    print("🏋️ Generating Movement Standards for ALL injuries...")

    full_content = """# CrossFit Movement Standards - Complete Multi-Injury Adaptations

> Guida completa agli adattamenti dei movimenti CrossFit per TUTTI gli infortuni sportivi comuni.
>
> ## Infortuni Coperti:
> 1. **SCIATICA** - Sciatalgia, ernia discale, radicolopatia
> 2. **PUBALGIA** - Sports hernia, dolore inguinale
> 3. **SHOULDER_IMPINGEMENT** - Conflitto subacromiale
> 4. **PATELLAR_TENDINITIS** - Ginocchio del saltatore
> 5. **HIP_FAI** - Impingement femoro-acetabolare
> 6. **ANKLE_SPRAIN** - Distorsione caviglia
> 7. **LUMBAR_STRAIN** - Lombalgia muscolare
> 8. **CERVICAL_PAIN** - Cervicalgia, tensione cervicale

---

## SCALA DOLORE (0-10)
| Livello | Descrizione | Approccio |
|---------|-------------|-----------|
| 0-3 | Minimo/assente | Progressione normale con monitoraggio |
| 3-5 | Moderato | Modifiche moderate, evitare aggravanti |
| 5-7 | Significativo | Modifiche importanti, focus rehab |
| 7-10 | Severo | STOP o solo isometrici/mobilità |

---

"""

    for movement_name, movement_desc in movements:
        print(f"  ⚡ Generating {movement_name}...")

        prompt = f"""Genera una sezione DETTAGLIATA per il movimento "{movement_name}" ({movement_desc}) con adattamenti per TUTTI questi 8 infortuni:

1. SCIATICA (sciatalgia, ernia discale)
2. PUBALGIA (sports hernia, adduttori)
3. SHOULDER_IMPINGEMENT (conflitto subacromiale)
4. PATELLAR_TENDINITIS (ginocchio saltatore)
5. HIP_FAI (impingement femoro-acetabolare)
6. ANKLE_SPRAIN (distorsione caviglia)
7. LUMBAR_STRAIN (lombalgia muscolare)
8. CERVICAL_PAIN (cervicalgia)

Per OGNI infortunio crea una tabella con:
| Dolore | Adattamento |
|--------|-------------|
| 7-10 | cosa fare in fase acuta |
| 5-7 | modifiche importanti |
| 3-5 | modifiche leggere |
| 0-3 | progressione normale |

Poi aggiungi:
- **Evitare**: cosa NON fare
- **Alternative**: movimenti sostitutivi sicuri
- **Note**: consigli per progressione

Formato Markdown. Sii specifico, pratico e basato su evidenze."""

        try:
            section = generate_with_openrouter(prompt)
            full_content += f"\n## {movement_name} ({movement_desc})\n\n{section}\n\n---\n"
            time.sleep(1)  # Rate limiting
        except Exception as e:
            print(f"    ❌ Error: {e}")
            # Fallback content
            full_content += f"\n## {movement_name} ({movement_desc})\n\n*Contenuto da generare*\n\n---\n"

    # Save
    output_path = KB_DIR / "movement_standards_complete.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)

    print(f"✅ Saved to {output_path}")
    return output_path


def generate_fitness_recipes():
    """Generate comprehensive fitness recipes dataset."""

    categories = [
        ("COLAZIONE_PROTEICA", "Colazioni ad alto contenuto proteico per atleti", 8),
        ("PRANZO_BILANCIATO", "Pranzi bilanciati pre/post workout", 8),
        ("CENA_RECOVERY", "Cene per recupero muscolare", 8),
        ("SNACK_PROTEICI", "Snack veloci ad alto contenuto proteico", 6),
        ("SMOOTHIE_ENERGIA", "Frullati energetici e proteici", 6),
        ("MEAL_PREP", "Ricette per meal prep settimanale", 6),
        ("VEGETARIANO", "Opzioni vegetariane ad alto contenuto proteico", 6),
        ("LOW_CARB", "Ricette low carb per definizione", 6),
        ("BULK", "Ricette ipercaloriche per massa", 6),
        ("QUICK_MEALS", "Pasti veloci < 15 minuti", 6)
    ]

    print("\n🍳 Generating Fitness Recipes Dataset...")

    all_recipes = []

    for cat_id, cat_desc, num_recipes in categories:
        print(f"  🥗 Generating {cat_id} ({num_recipes} recipes)...")

        prompt = f"""Genera esattamente {num_recipes} ricette fitness per la categoria "{cat_desc}".

Per OGNI ricetta fornisci SOLO un JSON valido (senza markdown code blocks):
[
  {{
    "id": "{cat_id.lower()}_1",
    "name": "Nome Ricetta Italiano",
    "category": "{cat_id}",
    "description": "Descrizione breve della ricetta",
    "prep_time_min": 10,
    "cook_time_min": 15,
    "servings": 2,
    "difficulty": "easy",
    "ingredients": [
      {{"name": "pollo", "quantity": 200, "unit": "g"}},
      {{"name": "riso", "quantity": 100, "unit": "g"}}
    ],
    "instructions": ["Cuoci il pollo", "Aggiungi il riso"],
    "nutrition_per_serving": {{
      "calories": 450,
      "protein_g": 35,
      "carbs_g": 40,
      "fat_g": 12,
      "fiber_g": 3
    }},
    "tags": ["high-protein", "post-workout"],
    "suitable_for": ["bulking", "maintenance"],
    "meal_timing": ["post-workout", "lunch"]
  }}
]

IMPORTANTE: Rispondi SOLO con l'array JSON, niente altro testo."""

        try:
            result = generate_with_openrouter(prompt)
            # Clean result - remove markdown code blocks if present
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            result = result.strip()

            # Extract JSON
            json_start = result.find('[')
            json_end = result.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                recipes = json.loads(result[json_start:json_end])
                # Add unique IDs
                for i, recipe in enumerate(recipes):
                    recipe['id'] = f"{cat_id.lower()}_{i+1}"
                all_recipes.extend(recipes)
                print(f"    ✅ Added {len(recipes)} recipes")
            time.sleep(1)
        except Exception as e:
            print(f"    ❌ Error: {e}")

    # Save
    output_path = FINAL_DIR / "fitness_recipes.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_recipes, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(all_recipes)} recipes to {output_path}")
    return output_path


def generate_nutrition_guidelines():
    """Generate comprehensive nutrition guidelines for athletes."""

    print("\n📊 Generating Nutrition Guidelines...")

    prompt = """Genera una guida COMPLETA alla nutrizione per atleti CrossFit/Fitness in formato Markdown.

Includi sezioni dettagliate su:

1. **MACRONUTRIENTI PER OBIETTIVO**
   - Bulk/Massa: grammi per kg, timing, surplus calorico
   - Cut/Definizione: grammi per kg, timing, deficit calorico
   - Mantenimento: rapporti ideali
   - Recomp: strategie cicliche

2. **TIMING NUTRIZIONALE**
   Tabelle con cosa mangiare:
   - 2-3h prima allenamento
   - 30-60min prima
   - Durante (se >1h)
   - Entro 30min dopo
   - 1-2h dopo

3. **TOP 20 ALIMENTI PER ATLETI**
   Tabella con: Alimento | Proteine/100g | Carboidrati | Grassi | Note

4. **IDRATAZIONE**
   - Formula per calcolo fabbisogno
   - Durante allenamento
   - Elettroliti quando servono

5. **INTEGRAZIONE EVIDENCE-BASED**
   Tabella: Integratore | Dosaggio | Timing | Efficacia (1-5) | Note

6. **ESEMPIO GIORNATA TIPO**
   - Giornata BULK (3200 kcal)
   - Giornata CUT (2000 kcal)
   - Giornata RIPOSO vs ALLENAMENTO

7. **ERRORI COMUNI DA EVITARE**
   Lista dei 10 errori più frequenti

Tutto in italiano, formato Markdown con tabelle."""

    try:
        content = generate_with_openrouter(prompt)

        output_path = KB_DIR / "nutrition_guidelines_complete.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Guida Completa alla Nutrizione per Atleti\n\n")
            f.write(content)

        print(f"✅ Saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def generate_injury_rehab_protocols():
    """Generate rehabilitation protocols for each injury type."""

    injuries = [
        ("SCIATICA", "Sciatalgia, ernia discale, radicolopatia lombare"),
        ("PUBALGIA", "Sports hernia, dolore inguinale, tendinopatia adduttori"),
        ("SHOULDER_IMPINGEMENT", "Conflitto subacromiale, tendinite cuffia rotatori"),
        ("PATELLAR_TENDINITIS", "Ginocchio del saltatore, tendinite rotulea"),
        ("HIP_FAI", "Impingement femoro-acetabolare, conflitto anca"),
        ("ANKLE_SPRAIN", "Distorsione caviglia, instabilità legamentosa"),
        ("LUMBAR_STRAIN", "Lombalgia muscolare, contrattura lombare"),
        ("CERVICAL_PAIN", "Cervicalgia, tensione cervicale, torcicollo")
    ]

    print("\n🏥 Generating Rehab Protocols...")

    all_protocols = []

    for injury_id, injury_desc in injuries:
        print(f"  💊 Generating {injury_id}...")

        prompt = f"""Genera un protocollo di RIABILITAZIONE per {injury_desc}.

Rispondi SOLO con JSON valido (senza markdown):
{{
  "injury_id": "{injury_id}",
  "injury_name": "{injury_desc.split(',')[0]}",
  "description": "Descrizione patologia",
  "common_causes": ["causa1", "causa2", "causa3"],
  "symptoms": ["sintomo1", "sintomo2", "sintomo3"],
  "red_flags": ["quando andare dal medico urgente"],
  "recovery_time_weeks": "4-8",
  "phases": [
    {{
      "phase": 1,
      "name": "Fase Acuta",
      "duration": "giorni 1-7",
      "goals": ["ridurre dolore", "proteggere"],
      "exercises": [
        {{"name": "Esercizio 1", "sets": 3, "reps": "10-15", "frequency": "2x/giorno"}}
      ],
      "avoid": ["movimenti da evitare"],
      "ice_heat": "ghiaccio 15min 3x/giorno"
    }},
    {{
      "phase": 2,
      "name": "Fase Subacuta",
      "duration": "settimane 2-3",
      "goals": ["recuperare mobilità"],
      "exercises": [...],
      "avoid": [...]
    }},
    {{
      "phase": 3,
      "name": "Fase Rinforzo",
      "duration": "settimane 4-6",
      "goals": ["recuperare forza"],
      "exercises": [...],
      "progression_criteria": ["criteri per avanzare"]
    }},
    {{
      "phase": 4,
      "name": "Ritorno Sport",
      "duration": "settimane 6+",
      "goals": ["ritorno attività completa"],
      "exercises": [...],
      "return_criteria": ["criteri per tornare allo sport"]
    }}
  ],
  "prevention_tips": ["come prevenire recidive"],
  "when_to_see_doctor": ["situazioni che richiedono visita medica"]
}}"""

        try:
            result = generate_with_openrouter(prompt)
            # Clean result
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            result = result.strip()

            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                protocol = json.loads(result[json_start:json_end])
                all_protocols.append(protocol)
                print(f"    ✅ Added protocol for {injury_id}")
            time.sleep(1)
        except Exception as e:
            print(f"    ❌ Error: {e}")

    # Save
    output_path = FINAL_DIR / "rehab_protocols.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_protocols, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(all_protocols)} protocols to {output_path}")
    return output_path


def main():
    print("=" * 60)
    print("🚀 IronRep Dataset Generator v2 (OpenRouter)")
    print("=" * 60)

    print(f"\n📁 Output directories:")
    print(f"   Knowledge Base: {KB_DIR}")
    print(f"   Final Data: {FINAL_DIR}")

    # Test API first
    print("\n🔑 Testing OpenRouter API...")
    try:
        test = generate_with_openrouter("Rispondi solo 'OK' se funziona.")
        print(f"   ✅ API working: {test[:50]}...")
    except Exception as e:
        print(f"   ❌ API Error: {e}")
        return

    # Generate all datasets
    generate_movement_standards()
    generate_fitness_recipes()
    generate_nutrition_guidelines()
    generate_injury_rehab_protocols()

    print("\n" + "=" * 60)
    print("✅ All datasets generated successfully!")
    print("=" * 60)

    # Summary
    print("\n📊 Generated files:")
    for f in KB_DIR.glob("*"):
        size = f.stat().st_size / 1024
        print(f"   {f.name}: {size:.1f} KB")
    for f in FINAL_DIR.glob("*.json"):
        size = f.stat().st_size / 1024
        print(f"   {f.name}: {size:.1f} KB")


if __name__ == "__main__":
    main()
