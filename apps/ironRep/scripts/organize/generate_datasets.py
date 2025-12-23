#!/usr/bin/env python3
"""
Dataset Generator using GROQ API
Generates comprehensive datasets for IronRep:
1. Movement Standards for ALL injuries (8 types)
2. Fitness Recipes with complete macros
3. Nutrition guidelines for athletes
"""

import json
import os
import time
from pathlib import Path

# Try to import groq
try:
    from groq import Groq
except ImportError:
    print("Installing groq package...")
    os.system("pip install groq")
    from groq import Groq

# API Keys - prova varie fonti
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "gsk_your_key_here"

# Output paths
DATA_DIR = Path(__file__).parent.parent / "apps/backend/data"
KB_DIR = DATA_DIR / "knowledge_base"
FINAL_DIR = DATA_DIR / "final"

# Ensure directories exist
KB_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)


def generate_with_groq(prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
    """Generate content using GROQ API."""
    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Sei un esperto di fitness, nutrizione sportiva e medicina dello sport. Genera contenuti dettagliati, scientificamente accurati e pratici."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=8000
    )

    return response.choices[0].message.content


def generate_movement_standards():
    """Generate complete movement standards for ALL 8 injuries."""

    injuries = [
        "SCIATICA",
        "PUBALGIA",
        "SHOULDER_IMPINGEMENT",
        "PATELLAR_TENDINITIS",
        "HIP_FAI",
        "ANKLE_SPRAIN",
        "LUMBAR_STRAIN",
        "CERVICAL_PAIN"
    ]

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

## SCALA DOLORE
- **0-3**: Dolore minimo/assente → Progressione normale con monitoraggio
- **3-5**: Dolore moderato → Modifiche moderate, evitare aggravanti
- **5-7**: Dolore significativo → Modifiche importanti, focus su rehab
- **7-10**: Dolore severo → STOP o solo isometrici/mobilità

---

"""

    for movement_name, movement_desc in movements:
        print(f"  ⚡ Generating {movement_name}...")

        prompt = f"""Genera una sezione DETTAGLIATA per il movimento "{movement_name}" ({movement_desc}) con adattamenti per TUTTI questi 8 infortuni:

1. SCIATICA (sciatalgia, ernia discale)
2. PUBALGIA (sports hernia)
3. SHOULDER_IMPINGEMENT (conflitto subacromiale)
4. PATELLAR_TENDINITIS (ginocchio saltatore)
5. HIP_FAI (impingement femoro-acetabolare)
6. ANKLE_SPRAIN (distorsione caviglia)
7. LUMBAR_STRAIN (lombalgia muscolare)
8. CERVICAL_PAIN (cervicalgia)

Per OGNI infortunio includi:
- Tabella con livelli dolore (0-3, 3-5, 5-7, 7-10) e adattamento specifico
- Cosa EVITARE assolutamente
- Alternative sicure
- Note per progressione

Formato Markdown con tabelle. Sii specifico e pratico. In italiano."""

        try:
            section = generate_with_groq(prompt)
            full_content += f"\n## {movement_name} ({movement_desc})\n\n{section}\n\n---\n"
            time.sleep(2)  # Rate limiting
        except Exception as e:
            print(f"    ❌ Error: {e}")
            full_content += f"\n## {movement_name}\n\n*Sezione da completare*\n\n---\n"

    # Save
    output_path = KB_DIR / "movement_standards_complete.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)

    print(f"✅ Saved to {output_path}")
    return output_path


def generate_fitness_recipes():
    """Generate comprehensive fitness recipes dataset."""

    categories = [
        ("COLAZIONE_PROTEICA", "Colazioni ad alto contenuto proteico per atleti", 15),
        ("PRANZO_BILANCIATO", "Pranzi bilanciati pre/post workout", 15),
        ("CENA_RECOVERY", "Cene per recupero muscolare", 15),
        ("SNACK_PROTEICI", "Snack veloci ad alto contenuto proteico", 10),
        ("SMOOTHIE_ENERGIA", "Frullati energetici e proteici", 10),
        ("MEAL_PREP", "Ricette per meal prep settimanale", 10),
        ("VEGETARIANO", "Opzioni vegetariane ad alto contenuto proteico", 10),
        ("LOW_CARB", "Ricette low carb per definizione", 10),
        ("BULK", "Ricette ipercaloriche per massa", 10),
        ("QUICK_MEALS", "Pasti veloci < 15 minuti", 10)
    ]

    print("\n🍳 Generating Fitness Recipes Dataset...")

    all_recipes = []

    for cat_id, cat_desc, num_recipes in categories:
        print(f"  🥗 Generating {cat_id} ({num_recipes} recipes)...")

        prompt = f"""Genera esattamente {num_recipes} ricette fitness per la categoria "{cat_desc}".

Per OGNI ricetta fornisci in formato JSON:
{{
  "id": "unique_id",
  "name": "Nome Ricetta",
  "category": "{cat_id}",
  "description": "Descrizione breve",
  "prep_time_min": 10,
  "cook_time_min": 15,
  "servings": 2,
  "difficulty": "easy|medium|hard",
  "ingredients": [
    {{"name": "ingrediente", "quantity": 100, "unit": "g"}}
  ],
  "instructions": ["Step 1", "Step 2"],
  "nutrition_per_serving": {{
    "calories": 350,
    "protein_g": 30,
    "carbs_g": 25,
    "fat_g": 12,
    "fiber_g": 5,
    "sugar_g": 3
  }},
  "tags": ["high-protein", "post-workout"],
  "suitable_for": ["bulking", "cutting", "maintenance"],
  "meal_timing": ["pre-workout", "post-workout", "anytime"]
}}

Rispondi SOLO con array JSON valido, nessun testo aggiuntivo."""

        try:
            result = generate_with_groq(prompt)
            # Extract JSON from response
            json_start = result.find('[')
            json_end = result.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                recipes = json.loads(result[json_start:json_end])
                all_recipes.extend(recipes)
                print(f"    ✅ Added {len(recipes)} recipes")
            time.sleep(2)
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
   - Bulk/Massa: rapporti, timing, calorie surplus
   - Cut/Definizione: rapporti, timing, calorie deficit
   - Mantenimento: rapporti, timing
   - Recomp: strategie

2. **TIMING NUTRIZIONALE**
   - Pre-workout (30min, 1h, 2h prima)
   - Intra-workout
   - Post-workout (finestra anabolica)
   - Prima di dormire

3. **ALIMENTI TOP PER ATLETI**
   - Proteine complete (con valori per 100g)
   - Carboidrati complessi
   - Grassi sani
   - Micronutrienti essenziali

4. **IDRATAZIONE**
   - Quantità base
   - Durante allenamento
   - Elettroliti
   - Segni disidratazione

5. **INTEGRAZIONE**
   - Essenziali (creatina, proteine, etc)
   - Opzionali
   - Timing ottimale
   - Dosaggi

6. **PIANI TIPO**
   - Giornata bulk (3000+ kcal)
   - Giornata cut (1800-2200 kcal)
   - Giornata allenamento vs riposo

7. **ERRORI COMUNI**
   - Da evitare
   - Miti da sfatare

Formato Markdown strutturato con tabelle dove appropriato. In italiano, pratico e basato su evidenze scientifiche."""

    try:
        content = generate_with_groq(prompt)

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
        ("SHOULDER_IMPINGEMENT", "Conflitto subacromiale, tendinite cuffia"),
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

        prompt = f"""Genera un protocollo di RIABILITAZIONE completo per {injury_desc} in formato JSON.

{{
  "injury_id": "{injury_id}",
  "injury_name": "{injury_desc.split(',')[0]}",
  "description": "Descrizione della patologia",
  "common_causes": ["causa1", "causa2"],
  "symptoms": ["sintomo1", "sintomo2"],
  "red_flags": ["quando andare dal medico"],
  "phases": [
    {{
      "phase": 1,
      "name": "Acuta",
      "duration_days": "3-7",
      "goals": ["ridurre dolore", "proteggere"],
      "exercises": [
        {{
          "name": "Esercizio",
          "sets": 3,
          "reps": "10-15",
          "frequency": "2x/giorno",
          "notes": "istruzioni"
        }}
      ],
      "avoid": ["cosa evitare"],
      "modalities": ["ghiaccio", "riposo"]
    }},
    {{
      "phase": 2,
      "name": "Subacuta",
      "duration_days": "7-21",
      "goals": ["recuperare mobilità", "iniziare rinforzo"],
      "exercises": [...],
      "avoid": [...],
      "modalities": [...]
    }},
    {{
      "phase": 3,
      "name": "Rinforzo",
      "duration_days": "21-42",
      "goals": ["recuperare forza", "stabilità"],
      "exercises": [...],
      "avoid": [...],
      "modalities": [...]
    }},
    {{
      "phase": 4,
      "name": "Ritorno Sport",
      "duration_days": "42+",
      "goals": ["ritorno attività completa"],
      "exercises": [...],
      "criteria": ["criteri per tornare"]
    }}
  ],
  "prevention": ["strategie prevenzione"],
  "prognosis": "tempo medio recupero"
}}

Rispondi SOLO con JSON valido."""

        try:
            result = generate_with_groq(prompt)
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                protocol = json.loads(result[json_start:json_end])
                all_protocols.append(protocol)
                print(f"    ✅ Added protocol for {injury_id}")
            time.sleep(2)
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
    print("🚀 IronRep Dataset Generator")
    print("=" * 60)

    if GROQ_API_KEY == "gsk_your_key_here":
        print("\n⚠️  GROQ_API_KEY not set!")
        print("Please set: export GROQ_API_KEY=your_actual_key")
        return

    print(f"\n📁 Output directories:")
    print(f"   Knowledge Base: {KB_DIR}")
    print(f"   Final Data: {FINAL_DIR}")

    # Generate all datasets
    generate_movement_standards()
    generate_fitness_recipes()
    generate_nutrition_guidelines()
    generate_injury_rehab_protocols()

    print("\n" + "=" * 60)
    print("✅ All datasets generated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
