import os
import sys
import uuid
import asyncio
from fastapi.testclient import TestClient

# Add src to path
sys.path.append("/app")

from src.interfaces.api.main import app
from src.infrastructure.persistence.database import SessionLocal
from src.infrastructure.persistence.models import UserModel
from src.infrastructure.security.security import create_access_token
from datetime import datetime

client = TestClient(app)

def reproduce_500():
    print("🚀 Reproducing Wizard 500 Error...")
    
    db = SessionLocal()
    try:
        # Create Test User
        email = f"wiz_crash_{uuid.uuid4().hex[:8]}@ironrep.com"
        user = UserModel(
            id=str(uuid.uuid4()),
            email=email,
            name="Crash Dummy",
            is_active=True,
            is_onboarded=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(user)
        db.commit()
        
        token = create_access_token(data={"sub": email})
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ User Created: {email}")

        # Minimal Payload (Empty Context)
        payload = {
            "initial_context": {}
        }
        
        print("📨 Sending Request to /api/wizard/complete-silent (Empty Context)...")
        res = client.post("/api/wizard/complete-silent", json=payload, headers=headers)
        
        print(f"📡 Status Code: {res.status_code}")
        if res.status_code == 500:
            print("❌ REPRODUCTION SUCCESSFUL: 500 Error")
            print("Response:", res.text)
        elif res.status_code == 200:
            print("✅ Unexpected Success (No 500)")
            print(res.json())
        else:
            print(f"⚠️ Other Error: {res.status_code}")
            print(res.text)

    except Exception as e:
        print(f"❌ Exception in script: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reproduce_500()
