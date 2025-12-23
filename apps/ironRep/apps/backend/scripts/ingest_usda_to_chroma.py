"""
Script per ingerire i dati USDA FNDDS in ChromaDB.

Questo script:
1. Legge i CSV USDA (food.csv, food_nutrient.csv, nutrient.csv)
2. Crea documenti ricchi di testo per ogni alimento
3. Li carica in ChromaDB per il RAG

Eseguire con:
    python scripts/ingest_usda_to_chroma.py
"""
import csv
import os
import sys
from pathlib import Path
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from infrastructure.ai.rag_service import get_rag_service
from infrastructure.logging import get_logger

logger = get_logger(__name__)

# Paths
USDA_DIR = Path(__file__).parent.parent / "data" / "external" / "usda_fndds" / "FoodData_Central_survey_food_csv_2024-10-31"


def load_nutrients_map() -> Dict[int, str]:
    """Carica la mappa nutrient_id -> nome nutriente."""
    nutrient_map = {}
    nutrient_file = USDA_DIR / "nutrient.csv"

    with open(nutrient_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            nutrient_map[int(row['id'])] = row['name']

    logger.info(f"Caricati {len(nutrient_map)} nutrienti")
    return nutrient_map


def load_food_nutrients(nutrient_map: Dict[int, str]) -> Dict[int, Dict[str, float]]:
    """Carica i valori nutrizionali per ogni food_id."""
    food_nutrients = {}
    nutrient_file = USDA_DIR / "food_nutrient.csv"

    # Nutrienti chiave che vogliamo tracciare
    key_nutrients = {
        'Energy': 'calories',
        'Protein': 'protein_g',
        'Total lipid (fat)': 'fat_g',
        'Carbohydrate, by difference': 'carbs_g',
        'Fiber, total dietary': 'fiber_g',
        'Sugars, total including NLEA': 'sugar_g',
        'Calcium, Ca': 'calcium_mg',
        'Iron, Fe': 'iron_mg',
        'Sodium, Na': 'sodium_mg',
        'Vitamin C, total ascorbic acid': 'vitamin_c_mg',
        'Vitamin A, RAE': 'vitamin_a_mcg',
        'Cholesterol': 'cholesterol_mg',
    }

    with open(nutrient_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fdc_id = int(row['fdc_id'])
            nutrient_id = int(row['nutrient_id'])

            nutrient_name = nutrient_map.get(nutrient_id, '')

            if nutrient_name in key_nutrients:
                if fdc_id not in food_nutrients:
                    food_nutrients[fdc_id] = {}

                try:
                    amount = float(row['amount']) if row['amount'] else 0
                    food_nutrients[fdc_id][key_nutrients[nutrient_name]] = amount
                except ValueError:
                    pass

    logger.info(f"Caricati nutrienti per {len(food_nutrients)} alimenti")
    return food_nutrients


def load_foods() -> List[Dict]:
    """Carica la lista degli alimenti."""
    foods = []
    food_file = USDA_DIR / "food.csv"

    with open(food_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            foods.append({
                'fdc_id': int(row['fdc_id']),
                'description': row['description'],
                'data_type': row.get('data_type', ''),
                'publication_date': row.get('publication_date', '')
            })

    logger.info(f"Caricati {len(foods)} alimenti")
    return foods


def load_portions() -> Dict[int, List[Dict]]:
    """Carica le porzioni per ogni alimento."""
    portions = {}
    portion_file = USDA_DIR / "food_portion.csv"

    with open(portion_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fdc_id = int(row['fdc_id'])
            if fdc_id not in portions:
                portions[fdc_id] = []

            if row['portion_description']:
                portions[fdc_id].append({
                    'description': row['portion_description'],
                    'gram_weight': float(row['gram_weight']) if row['gram_weight'] else 0
                })

    logger.info(f"Caricate porzioni per {len(portions)} alimenti")
    return portions


def create_food_document(food: Dict, nutrients: Dict, portions: List[Dict]) -> str:
    """Crea un documento testuale ricco per un alimento."""
    doc_parts = [
        f"# {food['description']}",
        f"FDC ID: {food['fdc_id']}",
        ""
    ]

    # Nutrienti
    if nutrients:
        doc_parts.append("## Valori Nutrizionali (per 100g)")

        if 'calories' in nutrients:
            doc_parts.append(f"- Calorie: {nutrients['calories']:.0f} kcal")
        if 'protein_g' in nutrients:
            doc_parts.append(f"- Proteine: {nutrients['protein_g']:.1f}g")
        if 'carbs_g' in nutrients:
            doc_parts.append(f"- Carboidrati: {nutrients['carbs_g']:.1f}g")
        if 'fat_g' in nutrients:
            doc_parts.append(f"- Grassi: {nutrients['fat_g']:.1f}g")
        if 'fiber_g' in nutrients:
            doc_parts.append(f"- Fibre: {nutrients['fiber_g']:.1f}g")
        if 'sugar_g' in nutrients:
            doc_parts.append(f"- Zuccheri: {nutrients['sugar_g']:.1f}g")
        if 'sodium_mg' in nutrients:
            doc_parts.append(f"- Sodio: {nutrients['sodium_mg']:.0f}mg")
        if 'cholesterol_mg' in nutrients:
            doc_parts.append(f"- Colesterolo: {nutrients['cholesterol_mg']:.0f}mg")

    # Porzioni
    if portions:
        doc_parts.append("\n## Porzioni Standard")
        for p in portions[:5]:  # Max 5 porzioni
            if p['gram_weight'] > 0:
                doc_parts.append(f"- {p['description']}: {p['gram_weight']:.0f}g")

    # Keywords per ricerca
    name_lower = food['description'].lower()
    keywords = []

    if any(x in name_lower for x in ['chicken', 'pollo', 'turkey', 'tacchino', 'beef', 'manzo', 'pork', 'maiale']):
        keywords.append('proteina animale')
    if any(x in name_lower for x in ['fish', 'pesce', 'salmon', 'salmone', 'tuna', 'tonno']):
        keywords.append('pesce omega-3')
    if any(x in name_lower for x in ['egg', 'uovo', 'uova']):
        keywords.append('uova proteine')
    if any(x in name_lower for x in ['rice', 'riso', 'pasta', 'bread', 'pane', 'oat', 'avena']):
        keywords.append('carboidrati cereali')
    if any(x in name_lower for x in ['milk', 'latte', 'cheese', 'formaggio', 'yogurt']):
        keywords.append('latticini calcio')
    if any(x in name_lower for x in ['vegetable', 'verdura', 'broccoli', 'spinach', 'spinaci']):
        keywords.append('verdure fibre vitamine')
    if any(x in name_lower for x in ['fruit', 'frutta', 'apple', 'mela', 'banana', 'orange', 'arancia']):
        keywords.append('frutta vitamine')

    if keywords:
        doc_parts.append(f"\nCategorie: {', '.join(keywords)}")

    return "\n".join(doc_parts)


def ingest_usda_to_chroma(limit: int = None):
    """
    Ingerisce i dati USDA in ChromaDB.

    Args:
        limit: Numero massimo di alimenti da ingerire (None = tutti)
    """
    logger.info("=== INGESTIONE USDA -> CHROMA ===")

    # Verifica che i file esistano
    if not USDA_DIR.exists():
        logger.error(f"Directory USDA non trovata: {USDA_DIR}")
        logger.error("Esegui prima: python data/external/download_datasets.py")
        return

    # Carica dati
    nutrient_map = load_nutrients_map()
    food_nutrients = load_food_nutrients(nutrient_map)
    foods = load_foods()
    portions = load_portions()

    # Limita se richiesto
    if limit:
        foods = foods[:limit]
        logger.info(f"Limitato a {limit} alimenti per test")

    # Prepara documenti
    documents = []
    ids = []
    metadatas = []

    for food in foods:
        fdc_id = food['fdc_id']
        nutrients = food_nutrients.get(fdc_id, {})
        food_portions = portions.get(fdc_id, [])

        doc = create_food_document(food, nutrients, food_portions)

        documents.append(doc)
        ids.append(f"usda_{fdc_id}")
        metadatas.append({
            "source": "usda_fndds",
            "type": "food",
            "category": "nutrition",
            "fdc_id": str(fdc_id),
            "food_name": food['description']
        })

    logger.info(f"Preparati {len(documents)} documenti per ingestione")

    # Ingerisci in ChromaDB
    rag = get_rag_service()

    # Batch insert per performance
    batch_size = 100
    total_added = 0

    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        batch_metas = metadatas[i:i+batch_size]

        try:
            rag.collection.add(
                documents=batch_docs,
                ids=batch_ids,
                metadatas=batch_metas
            )
            total_added += len(batch_docs)
            logger.info(f"Aggiunti {total_added}/{len(documents)} documenti...")
        except Exception as e:
            logger.error(f"Errore batch {i}: {e}")

    logger.info(f"✅ Ingestione completata! {total_added} alimenti USDA in ChromaDB")

    # Verifica
    try:
        collection = rag.collection.get()
        logger.info(f"📊 Totale documenti in ChromaDB: {len(collection['ids'])}")
    except Exception as e:
        logger.warning(f"Errore verifica: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingerisci dati USDA in ChromaDB")
    parser.add_argument("--limit", type=int, default=None, help="Limita numero alimenti (per test)")
    args = parser.parse_args()

    ingest_usda_to_chroma(limit=args.limit)
