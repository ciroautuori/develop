
import sys
import json
import os
import urllib.request
import urllib.error

# CONFIG
BASE_URL = "http://localhost:8000/api"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdXRjaXJAZ21haWwuY29tIiwiZXhwIjoxNzY3MjY3NzE2fQ.QxIv7etV2zyAy01TCYbXWhtj9M5GMcgqEGp94AUTdLw"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def request(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, headers=HEADERS, method=method)
    if data:
        req.data = json.dumps(data).encode('utf-8')
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.read().decode('utf-8')}")
        raise
    except Exception as e:
        print(f"❌ Network Error: {e}")
        raise

def step(name):
    print(f"\n🔹 STEP: {name}")

def run_test():
    print("🚀 STARTING E2E WIZARD TEST (API Only)")
    
    # 1. Start Wizard (Intake)
    step("1. Start Wizard (Intake)")
    
    intake_payload = {
        "biometrics": {
            "age": 30,
            "weight": 80,
            "height": 180,
            "sex": "male"
        },
        "initial_context": {
            "goals": ["muscle_gain"],
            "experience_level": "intermediate",
            "hasInjury": True, 
            "wantNutrition": True,
            # Visual Step Data
            "injuryDetails": {
                "diagnosis": "L5-S1 Hernia",
                "painLevel": 4, 
                "description": "Mild pain during deadlifts",
                "date": "2023-01-01"
            },
            "foodPreferences": {
                "liked": ["Chicken", "Rice"],
                "disliked": ["Broccoli"],
                "allergies": ["Peanuts"]
            }
        }
    }
    
    try:
        data = request("POST", "/wizard/start", intake_payload)
        session_id = data.get("session_id")
        print(f"✅ Wizard Started. Session ID: {session_id}")
        print(f"🤖 Initial Message: {data.get('message')}")
        
    except Exception as e:
        print(f"❌ Failed to start wizard: {e}")
        return

    # 2. Check Smart Skip
    initial_msg = data.get("message", "").lower()
    if "pain" in initial_msg or "injury" in initial_msg:
         print("⚠️ WARNING: Agent mentions injury immediately.")
    
    # 3. Chat Loop (Simulated)
    step("2. Chat Interaction")
    
    msg1 = "Yes, I want to confirm muscle gain."
    print(f"👤 User: {msg1}")
    
    chat_payload = {"session_id": session_id, "message": msg1}
    data = request("POST", "/wizard/message", chat_payload)
    print(f"🤖 Agent: {data.get('message')}")
    
    if data.get("completed"):
        print("🎉 Wizard Completed early!")

    # 4. Completion & Plan Generation
    step("3. Complete Onboarding")
    
    # A. Update Profile Helper (Skip actual call for now as we focus on Wizard Agent logic)
    step("3b. Trigger Plan Generation")
    try:
        print("🤖 Finishing chat to trigger plan generation...")
        finish_payload = {"session_id": session_id, "message": "Yes, please generate my plan."}
        data = request("POST", "/wizard/message", finish_payload)
        print(f"🤖 User: 'Yes, please generate my plan.'")
        print(f"🤖 Agent: {data.get('message')}")
        
        if data.get("completed"):
             print("✅ Wizard marked as COMPLETED by backend.")
             if data.get("initialization"):
                 print("✅ Agents Initialized:", data['initialization'])
        else:
             print("⚠️ Wizard did not complete. Might need more turns.")

    except Exception as e:
        print(f"❌ Failed to trigger completion: {e}")

if __name__ == "__main__":
    run_test()

if __name__ == "__main__":
    run_test()
