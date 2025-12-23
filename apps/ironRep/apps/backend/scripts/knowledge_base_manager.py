"""
Knowledge Base Manager - Sistema centralizzato per gestione RAG.

Funzionalità:
1. Ingestione dati USDA con valori nutrizionali completi
2. Ingestione prodotti Open Food Facts
3. Aggiornamento automatico del knowledge base
4. Verifica stato e statistiche

Eseguire con:
    python scripts/knowledge_base_manager.py status
    python scripts/knowledge_base_manager.py ingest-usda
    python scripts/knowledge_base_manager.py ingest-openfoodfacts
    python scripts/knowledge_base_manager.py full-update
"""
import csv
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add app to path (works in Docker container)
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.ai.rag_service import get_rag_service
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
# USDA può essere in due posizioni (con o senza sottocartella usda_fndds)
USDA_DIR_1 = DATA_DIR / "external" / "usda_fndds" / "FoodData_Central_survey_food_csv_2024-10-31"
USDA_DIR_2 = DATA_DIR / "external" / "FoodData_Central_survey_food_csv_2024-10-31"
USDA_DIR = USDA_DIR_1 if USDA_DIR_1.exists() else USDA_DIR_2
OFF_DIR = DATA_DIR / "external" / "openfoodfacts"


class KnowledgeBaseManager:
    """Manager centralizzato per il Knowledge Base RAG."""

    def __init__(self):
        self.rag = get_rag_service()

    def get_status(self) -> Dict:
        """Ottieni stato attuale del knowledge base."""
        try:
            data = self.rag.collection.get()

            # Conta per categoria e sorgente
            categories = {}
            sources = {}
            types = {}

            for meta in data.get('metadatas', []):
                cat = meta.get('category', 'unknown')
                src = meta.get('source', 'unknown')
                typ = meta.get('type', 'unknown')

                categories[cat] = categories.get(cat, 0) + 1
                sources[src] = sources.get(src, 0) + 1
                types[typ] = types.get(typ, 0) + 1

            return {
                "total_documents": len(data['ids']),
                "by_category": categories,
                "by_source": dict(sorted(sources.items(), key=lambda x: -x[1])[:20]),
                "by_type": types
            }
        except Exception as e:
            return {"error": str(e)}

    def print_status(self):
        """Stampa stato formattato."""
        status = self.get_status()

        print("=" * 60)
        print("📊 KNOWLEDGE BASE STATUS")
        print("=" * 60)

        if "error" in status:
            print(f"❌ Errore: {status['error']}")
            return

        print(f"📚 Totale documenti: {status['total_documents']}")
        print()

        print("📂 Per CATEGORIA:")
        for cat, count in sorted(status['by_category'].items(), key=lambda x: -x[1]):
            print(f"   {cat}: {count}")

        print()
        print("📁 Per TIPO:")
        for typ, count in sorted(status['by_type'].items(), key=lambda x: -x[1]):
            print(f"   {typ}: {count}")

        print()
        print("🔗 Top SORGENTI:")
        for src, count in list(status['by_source'].items())[:10]:
            src_short = src[-50:] if len(src) > 50 else src
            print(f"   {src_short}: {count}")

    def ingest_usda_with_nutrients(self, limit: Optional[int] = None) -> int:
        """
        Ingerisci dati USDA con valori nutrizionali completi.

        Il dataset USDA FNDDS ha una struttura specifica dove food_nutrient.csv
        contiene nutrient_id che NON corrispondono a nutrient.csv.
        Usiamo la mappatura diretta dai nutrient_id nel food_nutrient.
        """
        if not USDA_DIR.exists():
            logger.error(f"Directory USDA non trovata: {USDA_DIR}")
            return 0

        print("⏳ Caricando dati USDA...")

        # Mappa nutrient_id FNDDS -> nome (basata su analisi del dataset)
        # Questi ID sono specifici per FNDDS, non per il file nutrient.csv generico
        fndds_nutrient_map = {
            208: "Energy",  # kcal
            203: "Protein",
            204: "Total Fat",
            205: "Carbohydrate",
            291: "Fiber",
            269: "Sugars",
            301: "Calcium",
            303: "Iron",
            307: "Sodium",
            401: "Vitamin C",
            318: "Vitamin A",
            601: "Cholesterol",
            606: "Saturated Fat",
            645: "Monounsaturated Fat",
            646: "Polyunsaturated Fat"
        }

        # Carica food_nutrient
        print("   Caricando valori nutrizionali...")
        food_nutrients = {}

        with open(USDA_DIR / 'food_nutrient.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    fdc_id = int(row['fdc_id'])
                    nutrient_id = int(row['nutrient_id'])
                    amount = float(row['amount']) if row['amount'] else 0

                    if nutrient_id in fndds_nutrient_map:
                        if fdc_id not in food_nutrients:
                            food_nutrients[fdc_id] = {}
                        food_nutrients[fdc_id][fndds_nutrient_map[nutrient_id]] = amount
                except (ValueError, KeyError):
                    continue

        print(f"   ✅ Nutrienti caricati per {len(food_nutrients)} alimenti")

        # Carica porzioni
        print("   Caricando porzioni...")
        portions = {}
        with open(USDA_DIR / 'food_portion.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    fdc_id = int(row['fdc_id'])
                    if fdc_id not in portions:
                        portions[fdc_id] = []
                    if row.get('portion_description'):
                        portions[fdc_id].append({
                            'desc': row['portion_description'],
                            'grams': float(row['gram_weight']) if row.get('gram_weight') else 0
                        })
                except (ValueError, KeyError):
                    continue

        print(f"   ✅ Porzioni caricate per {len(portions)} alimenti")

        # Carica alimenti
        print("   Caricando lista alimenti...")
        foods = []
        with open(USDA_DIR / 'food.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                foods.append({
                    'fdc_id': int(row['fdc_id']),
                    'name': row['description']
                })

        if limit:
            foods = foods[:limit]

        print(f"   ✅ {len(foods)} alimenti da processare")

        # Prima rimuovi documenti USDA esistenti
        print("   Rimuovendo vecchi documenti USDA...")
        try:
            existing = self.rag.collection.get(where={"source": "usda_fndds"})
            if existing['ids']:
                self.rag.collection.delete(ids=existing['ids'])
                print(f"   ✅ Rimossi {len(existing['ids'])} documenti esistenti")
        except Exception as e:
            print(f"   ⚠️ Errore rimozione: {e}")

        # Crea documenti
        print("   Creando documenti per ChromaDB...")
        documents = []
        ids = []
        metadatas = []

        for food in foods:
            fdc_id = food['fdc_id']
            nutrients = food_nutrients.get(fdc_id, {})
            food_portions = portions.get(fdc_id, [])

            # Crea documento ricco
            doc_parts = [
                f"# {food['name']}",
                f"FDC ID: {fdc_id}",
                "",
                "## Valori Nutrizionali (per 100g)"
            ]

            if nutrients:
                if 'Energy' in nutrients:
                    doc_parts.append(f"- Calorie: {nutrients['Energy']:.0f} kcal")
                if 'Protein' in nutrients:
                    doc_parts.append(f"- Proteine: {nutrients['Protein']:.1f}g")
                if 'Carbohydrate' in nutrients:
                    doc_parts.append(f"- Carboidrati: {nutrients['Carbohydrate']:.1f}g")
                if 'Total Fat' in nutrients:
                    doc_parts.append(f"- Grassi: {nutrients['Total Fat']:.1f}g")
                if 'Fiber' in nutrients:
                    doc_parts.append(f"- Fibre: {nutrients['Fiber']:.1f}g")
                if 'Sugars' in nutrients:
                    doc_parts.append(f"- Zuccheri: {nutrients['Sugars']:.1f}g")
                if 'Saturated Fat' in nutrients:
                    doc_parts.append(f"- Grassi saturi: {nutrients['Saturated Fat']:.1f}g")
                if 'Sodium' in nutrients:
                    doc_parts.append(f"- Sodio: {nutrients['Sodium']:.0f}mg")
                if 'Cholesterol' in nutrients:
                    doc_parts.append(f"- Colesterolo: {nutrients['Cholesterol']:.0f}mg")

            # Aggiungi porzioni
            if food_portions:
                doc_parts.append("")
                doc_parts.append("## Porzioni Standard")
                for p in food_portions[:3]:
                    if p['grams'] > 0:
                        doc_parts.append(f"- {p['desc']}: {p['grams']:.0f}g")

            # Keywords per ricerca
            name_lower = food['name'].lower()
            tags = []

            if any(x in name_lower for x in ['chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'egg']):
                tags.append('proteina')
            if any(x in name_lower for x in ['rice', 'pasta', 'bread', 'oat', 'cereal']):
                tags.append('carboidrati')
            if any(x in name_lower for x in ['milk', 'cheese', 'yogurt']):
                tags.append('latticini')
            if any(x in name_lower for x in ['vegetable', 'broccoli', 'spinach', 'salad']):
                tags.append('verdure')
            if any(x in name_lower for x in ['fruit', 'apple', 'banana', 'orange']):
                tags.append('frutta')

            if tags:
                doc_parts.append(f"\nCategorie: {', '.join(tags)}")

            documents.append("\n".join(doc_parts))
            ids.append(f"usda_{fdc_id}")
            metadatas.append({
                "source": "usda_fndds",
                "type": "food",
                "category": "nutrition",
                "food_name": food['name'],
                "has_nutrients": "yes" if nutrients else "no"
            })

        # Batch insert
        print(f"   Ingerendo {len(documents)} documenti in ChromaDB...")
        batch_size = 100
        total_added = 0

        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            batch_metas = metadatas[i:i+batch_size]

            try:
                self.rag.collection.add(
                    documents=batch_docs,
                    ids=batch_ids,
                    metadatas=batch_metas
                )
                total_added += len(batch_docs)

                if total_added % 500 == 0:
                    print(f"      Progresso: {total_added}/{len(documents)}")
            except Exception as e:
                print(f"   ❌ Errore batch {i}: {e}")

        print(f"✅ Ingeriti {total_added} alimenti USDA con nutrienti!")
        return total_added

    def ingest_openfoodfacts(self, country: str = "it") -> int:
        """Ingerisci prodotti Open Food Facts."""

        products_file = OFF_DIR / f"products_{country}.json"

        if not products_file.exists():
            print(f"❌ File non trovato: {products_file}")
            print("   Esegui prima: python scripts/download_openfoodfacts.py")
            return 0

        print(f"⏳ Caricando prodotti Open Food Facts ({country})...")

        with open(products_file, 'r', encoding='utf-8') as f:
            products = json.load(f)

        print(f"   ✅ {len(products)} prodotti caricati")

        # Rimuovi esistenti
        print("   Rimuovendo vecchi documenti OFF...")
        try:
            existing = self.rag.collection.get(where={"source": f"openfoodfacts_{country}"})
            if existing['ids']:
                self.rag.collection.delete(ids=existing['ids'])
                print(f"   ✅ Rimossi {len(existing['ids'])} documenti")
        except Exception as e:
            print(f"   ⚠️ Errore rimozione: {e}")

        # Crea documenti
        documents = []
        ids = []
        metadatas = []

        for p in products:
            nutrients = p.get('nutrients', {})

            doc_parts = [
                f"# {p['name']}",
                f"Marca: {p.get('brand', 'N/A')}",
                f"Codice a barre: {p.get('code', 'N/A')}",
                ""
            ]

            # Nutriscore
            if p.get('nutriscore'):
                doc_parts.append(f"Nutri-Score: {p['nutriscore'].upper()}")
            if p.get('nova_group'):
                doc_parts.append(f"NOVA Group: {p['nova_group']}")

            # Nutrienti
            doc_parts.append("")
            doc_parts.append("## Valori Nutrizionali (per 100g)")
            doc_parts.append(f"- Calorie: {nutrients.get('calories', 0):.0f} kcal")
            doc_parts.append(f"- Proteine: {nutrients.get('protein_g', 0):.1f}g")
            doc_parts.append(f"- Carboidrati: {nutrients.get('carbs_g', 0):.1f}g")
            doc_parts.append(f"- Grassi: {nutrients.get('fat_g', 0):.1f}g")
            doc_parts.append(f"- Fibre: {nutrients.get('fiber_g', 0):.1f}g")
            doc_parts.append(f"- Zuccheri: {nutrients.get('sugar_g', 0):.1f}g")
            doc_parts.append(f"- Sale: {nutrients.get('salt_g', 0):.2f}g")

            # Allergeni
            if p.get('allergens'):
                allergens = [a.replace('en:', '') for a in p['allergens']]
                doc_parts.append(f"\n⚠️ Allergeni: {', '.join(allergens)}")

            # Ingredienti
            if p.get('ingredients'):
                ingredients = p['ingredients'][:200] + "..." if len(p.get('ingredients', '')) > 200 else p.get('ingredients', '')
                doc_parts.append(f"\nIngredienti: {ingredients}")

            documents.append("\n".join(doc_parts))
            ids.append(f"off_{country}_{p.get('code', len(ids))}")
            metadatas.append({
                "source": f"openfoodfacts_{country}",
                "type": "food",
                "category": "nutrition",
                "food_name": p['name'],
                "brand": p.get('brand', ''),
                "barcode": p.get('code', ''),
                "nutriscore": p.get('nutriscore', '')
            })

        # Batch insert
        print(f"   Ingerendo {len(documents)} prodotti...")
        batch_size = 100
        total_added = 0

        for i in range(0, len(documents), batch_size):
            try:
                self.rag.collection.add(
                    documents=documents[i:i+batch_size],
                    ids=ids[i:i+batch_size],
                    metadatas=metadatas[i:i+batch_size]
                )
                total_added += min(batch_size, len(documents) - i)
            except Exception as e:
                print(f"   ❌ Errore: {e}")

        print(f"✅ Ingeriti {total_added} prodotti Open Food Facts!")
        return total_added

    def full_update(self):
        """Esegui aggiornamento completo del knowledge base."""

        print("=" * 60)
        print("🔄 AGGIORNAMENTO COMPLETO KNOWLEDGE BASE")
        print(f"   Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)

        total = 0

        # 1. Re-inizializza base (esercizi, ricette, medical)
        print("\n1️⃣ Re-inizializzando knowledge base core...")
        try:
            core_count = self.rag.reinitialize_knowledge_base('/app/data')
            total += core_count
            print(f"   ✅ {core_count} documenti core")
        except Exception as e:
            print(f"   ⚠️ Errore core: {e}")
            # Fallback path locale
            try:
                core_count = self.rag.reinitialize_knowledge_base(str(DATA_DIR))
                total += core_count
                print(f"   ✅ {core_count} documenti core (path locale)")
            except Exception as e2:
                print(f"   ❌ Errore: {e2}")

        # 2. USDA
        print("\n2️⃣ Ingerendo dati USDA...")
        usda_count = self.ingest_usda_with_nutrients()
        total += usda_count

        # 3. Open Food Facts
        print("\n3️⃣ Ingerendo Open Food Facts...")
        for country in ["it", "fr", "de", "es"]:
            if (OFF_DIR / f"products_{country}.json").exists():
                off_count = self.ingest_openfoodfacts(country)
                total += off_count

        # Riepilogo
        print()
        print("=" * 60)
        print(f"✅ AGGIORNAMENTO COMPLETATO!")
        print(f"   Totale documenti: {total}")
        print("=" * 60)

        self.print_status()

        return total

    def test_search(self, query: str, k: int = 5):
        """Testa una ricerca nel knowledge base."""
        print(f"\n🔍 Ricerca: \"{query}\"")
        print("-" * 40)

        results = self.rag.retrieve_context(query, k=k)

        for i, r in enumerate(results, 1):
            name = r['metadata'].get('food_name', r['metadata'].get('exercise_name', r['metadata'].get('source', 'unknown')))
            source = r['metadata'].get('source', 'unknown')
            score = r['relevance_score']

            print(f"[{i}] {name[:40]}...")
            print(f"    Fonte: {source[:30]}, Score: {score:.3f}")
            print()


def main():
    parser = argparse.ArgumentParser(description="Knowledge Base Manager")
    parser.add_argument("action", choices=["status", "ingest-usda", "ingest-off", "full-update", "test"],
                       help="Azione da eseguire")
    parser.add_argument("--country", default="it", help="Paese per Open Food Facts")
    parser.add_argument("--limit", type=int, default=None, help="Limite documenti")
    parser.add_argument("--query", default="high protein food", help="Query per test")

    args = parser.parse_args()

    manager = KnowledgeBaseManager()

    if args.action == "status":
        manager.print_status()

    elif args.action == "ingest-usda":
        manager.ingest_usda_with_nutrients(limit=args.limit)

    elif args.action == "ingest-off":
        manager.ingest_openfoodfacts(args.country)

    elif args.action == "full-update":
        manager.full_update()

    elif args.action == "test":
        manager.test_search(args.query)


if __name__ == "__main__":
    main()
