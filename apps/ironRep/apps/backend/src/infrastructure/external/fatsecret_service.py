import os
import requests
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import re

class FatSecretService:
    """
    Service per interagire con FatSecret Platform API.
    """

    def __init__(self):
        self.client_id = os.getenv("FATSECRET_CLIENT_ID")
        self.client_secret = os.getenv("FATSECRET_CLIENT_SECRET")
        self.api_url = os.getenv("FATSECRET_API_URL", "https://platform.fatsecret.com/rest/server.api")
        self.token_url = "https://oauth.fatsecret.com/connect/token"
        self.default_language = os.getenv("FATSECRET_LANGUAGE", "it")
        self.default_region = os.getenv("FATSECRET_REGION", "IT")
        self.access_token = None
        self.token_expires_at = None
        
        # FAIL FAST in Production
        if os.getenv("ENVIRONMENT") == "production":
             if not self.client_id or not self.client_secret:
                 raise RuntimeError("FATSECRET_CLIENT_ID and FATSECRET_CLIENT_SECRET are REQUIRED in production.")

    # Keywords indicating prepared dishes (not pure ingredients)
    EXCLUDED_KEYWORDS = [
        # English connectors
        " with ", " and ", " in ", " on ", " over ",
        # Cooking methods (EN)
        "sauce", "soup", "stew", "casserole", "pie", "cake",
        "filled", "stuffed", "cooked", "baked", "fried", "grilled", "roasted",
        "sauteed", "steamed", "braised", "poached", "smoked", "cured",
        # Prepared foods (EN)
        "sandwich", "salad", "meal", "dinner", "lunch", "breakfast",
        "combo", "platter", "plate", "bowl", "wrap", "burrito", "taco",
        "pizza", "burger", "hot dog", "fries", "nuggets",
        "prepared", "ready", "frozen", "microwaveable",
        # Italian cooking methods and dishes
        "risotto", "asado", "arrosto", "fritto", "al forno", "alla",
        "parmigiana", "parmigiano", "bolognese", "carbonara", "amatriciana",
        "marinara", "arrabbiata", "puttanesca", "alfredo",
        # Spanish cooking terms
        "asado", "frito", "guisado", "estofado", "relleno", "adobado",
        "veracruz", "mexicano", "casero", "preparado",
        # Generic dish indicators
        "recipe", "ricetta", "receta", "dish", "piatto", "plato",
    ]

    def _is_pure_ingredient(self, name: str) -> bool:
        """Check if food is a pure ingredient (not a prepared dish)."""
        name_lower = name.lower()
        return not any(kw in name_lower for kw in self.EXCLUDED_KEYWORDS)

    def _get_access_token(self) -> str:
        """Ottieni access token OAuth 2.0."""
        if not self.client_id or not self.client_secret:
            raise RuntimeError("FatSecret credentials not found (FATSECRET_CLIENT_ID/FATSECRET_CLIENT_SECRET).")

        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token

        try:
            # Encode credentials
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            # Request token
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {
                "grant_type": "client_credentials",
                "scope": "basic"
            }

            response = requests.post(self.token_url, headers=headers, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.token_expires_at = datetime.now() + timedelta(seconds=token_data["expires_in"] - 60)

            return self.access_token
        except Exception as e:
            raise RuntimeError(f"Failed to get FatSecret token: {e}")

    def _make_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Esegui richiesta API."""
        token = self._get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
        }

        # FatSecret uses URL query parameters
        params["method"] = method
        params["format"] = "json"

        try:
            response = requests.get(self.api_url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"FatSecret API error: {e}")

    def search_foods(self, query: str, page: int = 0, max_results: int = 50) -> List[Dict[str, Any]]:
        params = {
            "search_expression": query,
            "page_number": page,
            "max_results": min(max_results, 50),
            "language": self.default_language,
            "region": self.default_region,
        }

        result = self._make_request("foods.search", params)

        if "foods" not in result or "food" not in result["foods"]:
            return []

        foods = result["foods"]["food"]
        if not isinstance(foods, list):
            foods = [foods]

        return [self._transform_food_item(food) for food in foods]

    def get_food_details(self, food_id: str) -> Dict[str, Any]:
        params = {"food_id": food_id}
        result = self._make_request("food.get.v2", params)

        return self._transform_food_details(result["food"])

    def get_food_categories(self) -> List[Dict[str, str]]:
        return [
            {"id": "protein", "name": "Proteine", "icon": "🥩"},
            {"id": "carbs", "name": "Carboidrati", "icon": "🍞"},
            {"id": "vegetables", "name": "Verdure", "icon": "🥬"},
            {"id": "fruits", "name": "Frutta", "icon": "🍎"},
            {"id": "dairy", "name": "Latticini", "icon": "🥛"},
            {"id": "fats", "name": "Grassi", "icon": "🥑"},
            {"id": "snacks", "name": "Snack", "icon": "🍿"},
            {"id": "beverages", "name": "Bevande", "icon": "☕"},
        ]

    def _transform_food_item(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        desc = raw.get("food_description", "")

        calories = float(self._extract_calories(desc) or 0)
        protein = float(self._extract_macro(desc, "Protein") or 0)
        carbs = float(self._extract_macro(desc, "Carbs") or 0)
        fat = float(self._extract_macro(desc, "Fat") or 0)

        grams = self._extract_serving_grams(desc)
        if grams and grams > 0:
            # SAFETY GUARD: Only scale if grams reasonable (e.g. not 0.1g or >1000g outlier)
            # and if the detected 'grams' isn't actually the 'per 100g' standard itself.
            if 1 <= grams <= 1000:
                # If description says "Per 100g", factor is 1.0.
                factor = 100.0 / grams
                calories = calories * factor
                protein = protein * factor
                carbs = carbs * factor
                fat = fat * factor

        return {
            "id": str(raw["food_id"]),
            "name": raw["food_name"],
            "brand": raw.get("brand_name"),
            "type": raw.get("food_type", "generic"),
            "description": desc,
            "url": raw.get("food_url"),
            "calories": round(calories, 2),
            "protein": round(protein, 2),
            "carbs": round(carbs, 2),
            "fat": round(fat, 2),
        }

    def _transform_food_details(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        servings = raw.get("servings", {}).get("serving", [])
        if not isinstance(servings, list):
            servings = [servings]

        return {
            "id": raw["food_id"],
            "name": raw["food_name"],
            "brand": raw.get("brand_name"),
            "type": raw.get("food_type", "generic"),
            "url": raw.get("food_url"),
            "servings": [
                {
                    "id": s["serving_id"],
                    "description": s["serving_description"],
                    "metric_amount": float(s.get("metric_serving_amount", 0)),
                    "metric_unit": s.get("metric_serving_unit", "g"),
                    "calories": float(s.get("calories", 0)),
                    "protein": float(s.get("protein", 0)),
                    "carbs": float(s.get("carbohydrate", 0)),
                    "fat": float(s.get("fat", 0)),
                    "fiber": float(s.get("fiber", 0)),
                    "sugar": float(s.get("sugar", 0)),
                    "sodium": float(s.get("sodium", 0)),
                }
                for s in servings
            ],
            # Fallback macros from first serving or description
            "calories": float(servings[0].get("calories", 0)) if servings else 0,
            "protein": float(servings[0].get("protein", 0)) if servings else 0,
            "carbs": float(servings[0].get("carbohydrate", 0)) if servings else 0,
            "fat": float(servings[0].get("fat", 0)) if servings else 0,
        }

        """
        Extract numerical value of calories (kcal) from description string.
        Handles: "Calories: 123kcal", "123 kcal", "Energy: 123kJ" (converts to kcal).
        """
        desc = (description or "").strip()
        if not desc:
            return 0

        # Pattern 1: Explicit kcal (most reliable)
        # Matches: "Calories: 105kcal", "Energy: 105 kcal", "105kcal"
        kcal_match = re.search(r"(?i)(?:calories|energy|kcal)[:\s]*(\d+)(?:\.\d+)?\s*kcal\b", desc)
        if kcal_match:
            try:
                return int(float(kcal_match.group(1)))
            except Exception:
                pass

        # Pattern 2: Explicit kJ (convert to kcal)
        # Matches: "Energy: 420kJ", "420 kJ"
        kj_match = re.search(r"(?i)(?:energy|kj)[:\s]*(\d+)(?:\.\d+)?\s*kj\b", desc)
        if kj_match:
            try:
                kj_val = float(kj_match.group(1))
                return int(round(kj_val / 4.184))
            except Exception:
                pass

        # Pattern 3: Fallback "Calories: 123" (assume kcal if no unit)
        generic_match = re.search(r"(?i)(?:calories|energy)[:\s]*(\d+)(?:\.\d+)?\s*(?:\||$|-)", desc)
        if generic_match:
            try:
                return int(float(generic_match.group(1)))
            except Exception:
                return 0

        return 0

    def _extract_calories(self, description: str) -> float:
        """Extract calories from FatSecret food description.
        
        Handles patterns like:
        - 'Calories: 350kcal'
        - 'Calories: 350kJ' (converts to kcal)
        - 'Calories: 350.5kcal'
        """
        import re
        desc = (description or "").strip()
        if not desc:
            return 0.0
        
        # Try kcal pattern first
        match = re.search(r"Calories:\s*([\d.]+)\s*kcal", desc, re.IGNORECASE)
        if match:
            return float(match.group(1))
        
        # Try kJ pattern (convert to kcal: divide by 4.184)
        match = re.search(r"Calories:\s*([\d.]+)\s*kJ", desc, re.IGNORECASE)
        if match:
            return float(match.group(1)) / 4.184
        
        # Try bare number pattern (assume kcal)
        match = re.search(r"Calories:\s*([\d.]+)", desc, re.IGNORECASE)
        if match:
            return float(match.group(1))
        
        return 0.0

    def _extract_macro(self, description: str, macro: str) -> float:
        import re
        match = re.search(rf"{macro}:\s*([\d.]+)g", description)
        return float(match.group(1)) if match else 0.0

    def _extract_serving_grams(self, description: str) -> Optional[float]:
        desc = (description or "").strip()
        if not desc:
            return None

        # Common FatSecret patterns:
        # - "Per 100g - Calories: ..."
        # - "Per 1 serving (250g) - Calories: ..."
        # - "Per 250g - Calories: ..."
        m = re.search(r"(?i)\bper\s+(?:[^\-]*?)\(\s*([\d.]+)\s*g\s*\)", desc)
        if m:
            try:
                return float(m.group(1))
            except Exception:
                return None

        m = re.search(r"(?i)\bper\s+([\d.]+)\s*g\b", desc)
        if m:
            try:
                return float(m.group(1))
            except Exception:
                return None

        # Pattern 1: "Per 1 serving (123g) - ..."
        m1 = re.search(r"(?i)per\s+\d+\s*serving\s*\(\s*([\d.]+)\s*g\s*\)", desc)
        if m1:
             return float(m1.group(1))

        # Pattern 2: "Per 123g - ..." (Standard header)
        m2 = re.search(r"(?i)^per\s+([\d.]+)\s*g\s*-", desc)
        if m2:
             return float(m2.group(1))
        
        # Pattern 3: - "... | 123g left" (Sometimes at end)
        return None

fatsecret_service = FatSecretService()
