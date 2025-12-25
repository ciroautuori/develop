
import asyncio
import httpx
import sys

BASE_URL = "http://localhost:8000/api/v1"

async def test_agents():
    print("🚀 Starting E2E Tests for AI Agents...")
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        # 1. Get a bando ID
        try:
            resp = await client.get(f"{BASE_URL}/bandi/recent?limit=1")
            if resp.status_code != 200 or not resp.json():
                print("❌ No bandi found to test.")
                return
            
            bando_id = resp.json()[0]['id']
            titolo = resp.json()[0]['titolo']
            print(f"📦 Testing with Bando: {titolo} (ID: {bando_id})")
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return
        
        # 2. Test Deep Analysis
        print("🔍 Triggering Deep Analysis...")
        try:
            resp = await client.post(f"{BASE_URL}/bandi/{bando_id}/analyze")
            if resp.status_code == 200:
                print("✅ Deep Analysis Successful!")
                analysis = resp.json()
                print(f"📈 Feasibility Score: {analysis.get('feasibility_score')}")
                print(f"📝 SWOT: {analysis.get('swot')}")
            else:
                print(f"❌ Deep Analysis Failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            
        # 3. Test Draft Generation
        print("✍️ Triggering Draft Generation...")
        try:
            resp = await client.post(f"{BASE_URL}/bandi/{bando_id}/draft")
            if resp.status_code == 200:
                print("✅ Draft Generation Successful!")
                draft = resp.json().get("draft", "")
                print(f"📄 Draft Length: {len(draft)} chars")
                print(f"预览: {draft[:300]}...")
            else:
                print(f"❌ Draft Generation Failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"❌ Drafting error: {e}")

if __name__ == "__main__":
    asyncio.run(test_agents())
