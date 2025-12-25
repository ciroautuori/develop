import sys
import os
import asyncio
import json
from datetime import datetime

# Add app to path
sys.path.append("/app")

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.interfaces.api.main import app
from src.infrastructure.persistence.database import get_db, SessionLocal
from src.infrastructure.security.security import create_access_token
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.interfaces.api.main import app
from src.infrastructure.persistence.database import get_db, SessionLocal
from src.infrastructure.security.security import create_access_token
from src.infrastructure.persistence.models import UserModel

# Initialize TestClient
client = TestClient(app)

def verify_internal():
    print("\n" + "="*80)
    print("🏋️ INTERNAL GYM READINESS VERIFICATION 🏋️")
    print("="*80 + "\n")

    db = SessionLocal()
    try:
        # Step 1: Create User directly
        print("📝 Step 1: Creating 'GymReady' test user via DB...")
        timestamp = datetime.now().strftime("%H%M%S")
        email = f"gym_ready_{timestamp}@ironrep.com"
        
        # Check if exists
        existing = db.query(UserModel).filter(UserModel.email == email).first()
        if existing:
            db.delete(existing)
            db.commit()

        # Create UserModel
        new_user = UserModel(
            id=f"test-{timestamp}",
            email=email,
            name="Gym Tester",
            is_active=True,
            is_onboarded=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(new_user)
        db.commit()
        
        user_id = new_user.id
        print(f"✅ User created in DB: {user_id}")

        # Generate Token
        print("\n🔑 Step 2: Generating Access Token...")
        token = create_access_token(data={"sub": email})
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Token generated")

        # Step 3: Silent Wizard Completion
        print("\n🤫 Step 3: Triggering Silent Wizard Completion (API)...")
        payload = {
            "initial_context": {
                "intake": {
                    "age": 30,
                    "weight": 85,
                    "height": 180,
                    "sex": "male",
                    "primaryGoal": "muscle_gain",
                    "experience": "intermediate",
                    "daysPerWeek": 4,
                    "hasInjury": True
                },
                "injuryDetails": {
                    "diagnosis": "Ernia L5-S1",
                    "location": "Lombare",
                    "painLevel": 6,
                    "injury_description": "Dolore acuto test",
                    "injury_date": "2023-01-01"
                },
                "foodPreferences": {
                    "liked": ["Chicken", "Rice"],
                    "disliked": ["Fish"]
                }
            }
        }

        # Note: /complete-silent might be receiving body directly or nested.
        # Checking WizardOrchestrator: it sends: { initial_context: ... }
        
        response = client.post("/api/wizard/complete-silent", json=payload, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Silent Completion Failed: {response.status_code}")
            print(response.text)
            return False
            
        data = response.json()
        print(f"✅ Silent Profile Built: {data.get('session_id')}")

        # Step 4: Finalize Onboarding / Generate Plans
        print("\n🏁 Step 4: Generating Plans (API)...")
        
        # Trigger Coach
        resp = client.post(
            "/api/plans/coach/generate",
            headers=headers,
            json={"focus": "muscle_gain", "days_available": 4}
        )
        if resp.status_code in [200, 201]:
             print("✅ Coach Plan Generated")
        else:
             print(f"⚠️ Coach Plan Gen Failed: {resp.status_code} - {resp.text}")

        # Trigger Medical
        resp = client.post(
            "/api/plans/medical/generate-protocol",
            headers=headers,
            json={"target_areas": ["Ernia L5-S1"], "current_pain_level": 6}
        )
        if resp.status_code in [200, 201]:
             print("✅ Medical Protocol Generated")
        else:
             print(f"⚠️ Medical Gen Failed: {resp.status_code} - {resp.text}")

        # Step 5: Verification
        print("\n🔍 Step 5: Verifying final state...")
        
        # Get Coach Plan
        resp = client.get("/api/plans/coach/current", headers=headers)
        if resp.status_code == 200:
            plan = resp.json()
            if plan:
                print(f"  ✅ Coach Plan: OK ({len(plan.get('workout_sessions', []))} sessions)")
            else:
                print("  ❌ Coach Plan: Empty Response")
        else:
            print("  ❌ Coach Plan: Not Found")
            
        return True

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = verify_internal()
    sys.exit(0 if success else 1)
