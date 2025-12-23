"""
Script per scaricare prodotti Open Food Facts (Italia/Europa).

Open Food Facts è un database open source con milioni di prodotti alimentari
con codici a barre, valori nutrizionali, ingredienti, allergeni, ecc.

Eseguire con:
    python scripts/download_openfoodfacts.py --country it --limit 5000
    python scripts/download_openfoodfacts.py --country world --limit 10000
"""
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import urllib.request
import urllib.parse

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "external" / "openfoodfacts"


def fetch_products(
    country: str = "it",
    page_size: int = 100,
    max_products: int = 5000,
    categories: Optional[List[str]] = None
) -> List[Dict]:
    """
    Scarica prodotti da Open Food Facts API.

    Args:
        country: Codice paese (it, fr, de, es, world)
        page_size: Prodotti per pagina (max 100)
        max_products: Limite totale prodotti
        categories: Lista categorie da filtrare (opzionale)

    Returns:
        Lista di prodotti con dati nutrizionali
    """
    products = []
    page = 1

    # Base URL per paese
    if country == "world":
        base_url = "https://world.openfoodfacts.org"
    else:
        base_url = f"https://{country}.openfoodfacts.org"

    print(f"📥 Scaricando da {base_url}...")
    print(f"   Target: {max_products} prodotti")

    while len(products) < max_products:
        # Costruisci URL API
        params = {
            "action": "process",
            "json": "1",
            "page_size": min(page_size, 100),
            "page": page,
            "fields": "code,product_name,brands,categories_tags,nutriments,ingredients_text,allergens_tags,labels_tags,quantity,serving_size,nutriscore_grade,nova_group,ecoscore_grade,image_url"
        }

        # Filtra per categorie se specificato
        if categories:
            params["tagtype_0"] = "categories"
            params["tag_contains_0"] = "contains"
            params["tag_0"] = categories[0]

        url = f"{base_url}/cgi/search.pl?" + urllib.parse.urlencode(params)

        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "IronRep-NutritionBot/1.0 (contact@ironrep.app)"
            })

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))

            page_products = data.get("products", [])

            if not page_products:
                print(f"   ⚠️ Pagina {page} vuota, fine dati")
                break

            # Filtra prodotti con dati nutrizionali validi
            valid_products = []
            for p in page_products:
                nutriments = p.get("nutriments", {})
                if (p.get("product_name") and
                    nutriments.get("energy-kcal_100g") is not None):
                    valid_products.append({
                        "code": p.get("code", ""),
                        "name": p.get("product_name", ""),
                        "brand": p.get("brands", ""),
                        "categories": p.get("categories_tags", []),
                        "quantity": p.get("quantity", ""),
                        "serving_size": p.get("serving_size", ""),
                        "nutriscore": p.get("nutriscore_grade", ""),
                        "nova_group": p.get("nova_group", ""),
                        "ecoscore": p.get("ecoscore_grade", ""),
                        "ingredients": p.get("ingredients_text", ""),
                        "allergens": p.get("allergens_tags", []),
                        "labels": p.get("labels_tags", []),
                        "nutrients": {
                            "calories": nutriments.get("energy-kcal_100g", 0),
                            "protein_g": nutriments.get("proteins_100g", 0),
                            "carbs_g": nutriments.get("carbohydrates_100g", 0),
                            "fat_g": nutriments.get("fat_100g", 0),
                            "fiber_g": nutriments.get("fiber_100g", 0),
                            "sugar_g": nutriments.get("sugars_100g", 0),
                            "salt_g": nutriments.get("salt_100g", 0),
                            "saturated_fat_g": nutriments.get("saturated-fat_100g", 0),
                            "sodium_mg": nutriments.get("sodium_100g", 0) * 1000 if nutriments.get("sodium_100g") else 0
                        },
                        "image_url": p.get("image_url", "")
                    })

            products.extend(valid_products)

            print(f"   Pagina {page}: +{len(valid_products)} prodotti (totale: {len(products)})")

            page += 1

            # Rate limiting
            time.sleep(0.5)

            # Safety check
            if page > 500:
                print("   ⚠️ Limite pagine raggiunto")
                break

        except Exception as e:
            print(f"   ❌ Errore pagina {page}: {e}")
            time.sleep(2)
            page += 1
            continue

    return products[:max_products]


def save_products(products: List[Dict], country: str):
    """Salva prodotti su file JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / f"products_{country}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"💾 Salvati {len(products)} prodotti in {output_file}")
    return output_file


def download_italian_products(limit: int = 5000):
    """Scarica prodotti italiani con focus su categorie fitness-friendly."""

    print("🇮🇹 Scaricando prodotti ITALIANI...")

    # Scarica mix di categorie
    all_products = []

    # Prima scarica prodotti generici italiani
    products = fetch_products(country="it", max_products=limit)
    all_products.extend(products)

    # Salva
    save_products(all_products, "it")

    return all_products


def download_european_products(limit: int = 3000):
    """Scarica prodotti da altri paesi europei."""

    countries = ["fr", "de", "es"]
    per_country = limit // len(countries)

    all_products = []

    for country in countries:
        print(f"\n🇪🇺 Scaricando prodotti da {country.upper()}...")
        products = fetch_products(country=country, max_products=per_country)
        all_products.extend(products)
        save_products(products, country)

    return all_products


def main():
    parser = argparse.ArgumentParser(description="Scarica prodotti Open Food Facts")
    parser.add_argument("--country", default="it", help="Paese (it, fr, de, es, world)")
    parser.add_argument("--limit", type=int, default=5000, help="Max prodotti")
    parser.add_argument("--all-eu", action="store_true", help="Scarica da tutti i paesi EU")

    args = parser.parse_args()

    print("=" * 60)
    print("📦 OPEN FOOD FACTS DOWNLOADER")
    print("=" * 60)

    if args.all_eu:
        # Scarica Italia + altri EU
        it_products = download_italian_products(args.limit)
        eu_products = download_european_products(args.limit // 2)

        # Combina tutto
        all_products = it_products + eu_products
        save_products(all_products, "eu_combined")

        print(f"\n✅ Totale: {len(all_products)} prodotti europei scaricati!")
    else:
        products = fetch_products(country=args.country, max_products=args.limit)
        save_products(products, args.country)
        print(f"\n✅ {len(products)} prodotti scaricati!")


if __name__ == "__main__":
    main()
