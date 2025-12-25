import sys
import os
import json
from datetime import datetime

sys.path.append("/app")
from fastapi.testclient import TestClient
from src.interfaces.api.main import app
from src.infrastructure.persistence.database import SessionLocal
from src.infrastructure.persistence.models import UserModel
from src.infrastructure.security.security import create_access_token

client = TestClient(app)

def verify_nutrition_deep():
    print("\n" + "="*80)
    print("🥗 NUTRITION & FATSECRET DEEP VERIFICATION 🥗")
    print("="*80 + "\n")

    db = SessionLocal()
    try:
        # 1. Setup User
        timestamp = datetime.now().strftime("%H%M%S")
        email = f"nutri_tester_{timestamp}@ironrep.com"
        
        user = UserModel(
            id=f"nutri-{timestamp}",
            email=email,
            name="Nutrition Tester",
            is_active=True,
            is_onboarded=True,  # Skip wizard for this test
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(user)
        db.commit()
        
        token = create_access_token(data={"sub": email})
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ User Created: {email}")

        # 2. Test FatSecret Search
        print("\n🔎 Step 2: Testing FatSecret Search...")
        response = client.get("/api/foods/search?q=chicken", headers=headers)
        if response.status_code == 200:
            results = response.json()
            # FatSecret results structure check
            # Likely list or dict with 'foods'
            # Note: The router returns List[FoodSearchResponse] directly because of the logic:
            # return sorted(foods, key=score, reverse=True)
            # So results should be a LIST.
            if isinstance(results, list):
                count = len(results)
                if count > 0:
                    print(f"✅ FatSecret Working: Found {count} items for 'chicken'")
                    # Pick first item for recipe
                    fs_food = results[0]
                    print(f"   - Selected: {fs_food.get('name')} (ID: {fs_food.get('id')})")
                else:
                     print(f"⚠️ FatSecret: No results found (Empty List) - {results}")
            else:
                 print(f"⚠️ FatSecret: Unexpected format - {results}")
        else:
            print(f"❌ FatSecret Error: {response.status_code} - {response.text}")

        # 3. Test Recipe Creation (Custom)
        print("\n🍳 Step 3: Creating Custom Recipe...")
        # Need a valid food_id (let's mock one if FatSecret failed, or use real one)
        # Assuming FatSecret works, we use fs_food.get('id')
        fake_food_id = "12345" 
        
        recipe_payload = {
            "name": "Power Chicken Rice",
            "description": "Post workout meal",
            "ingredients": [
                {
                    "food_id": fake_food_id, # Required by schema
                    "grams": 200,            # Required by schema
                    "name": "Chicken Breast", 
                    "calories": 330, 
                    "protein": 62, 
                    "carbs": 0, 
                    "fat": 7
                },
                {
                    "food_id": "67890",
                    "grams": 100,
                    "name": "Rice", 
                    "calories": 130, 
                    "protein": 2, 
                    "carbs": 28, 
                    "fat": 0
                }
            ],
            "servings": 1,
            "prep_time_minutes": 20,
            "instructions": "Cook chicken. Cook rice. Eat."
        }
        res = client.post("/api/recipes/", json=recipe_payload, headers=headers)
        if res.status_code in [200, 201]:
            print("✅ Recipe Created Successfully")
        else:
            print(f"❌ Recipe Creation Failed: {res.status_code} - {res.text}")

        # 4. Retest Medical Plan (Fixing 404 check)
        print("\n👨‍⚕️ Step 4: Retesting Medical Plan...")
        # Correct Endpoint: /api/plans/medical/generate
        res = client.post(
            "/api/plans/medical/generate",
            headers=headers,
            json={"targetAreas": ["Lumbar"], "currentPainLevel": 5}
        )
        if res.status_code in [200, 201]:
            print("✅ Medical Protocol Generated")
        elif res.status_code == 404:
             print("❌ Medical Endpoint NOT FOUND (404) - Still failing path?")
        else:
             print(f"⚠️ Medical Error: {res.status_code} - {res.text}")

        return True

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    verify_nutrition_deep()
