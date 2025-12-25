import sys
import os
import requests
import base64
from datetime import datetime

# FORCE HARDCODED VALUES to bypass Docker Env Vars (which might be wrong)
# Hypothesis: ID is 4a0cca... (The one sitting alone)
CLIENT_ID = "4a0cca579bd94da6a681497f36f11582"
# Hypothesis: Secret is 72ec8... (Labeled "Client Secret Key")
CLIENT_SECRET = "72ec8b7b1b294c898eee839f866a03fc"

print(f"DEBUG: Testing HARDCODED Swapped Keys...")
print(f"DEBUG: Using Client ID: {CLIENT_ID[:5]}...{CLIENT_ID[-5:]}")

def get_token():
    try:
        credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        url = "https://oauth.fatsecret.com/connect/token"
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials", "scope": "basic"}
        
        print(f"DEBUG: Requesting token from {url}...")
        res = requests.post(url, headers=headers, data=data, timeout=10)
        
        if res.status_code == 200:
            token = res.json()["access_token"]
            print(f"✅ Token Acquired: {token[:10]}...")
            return token
        else:
            print(f"❌ Token Failed: {res.status_code} - {res.text}")
            return None
    except Exception as e:
        print(f"❌ Token Exception: {e}")
        return None

def search_chicken(token):
    if not token: return
    
    try:
        url = "https://platform.fatsecret.com/rest/server.api"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "method": "foods.search",
            "search_expression": "pollo",
            "format": "json",
            "max_results": 5,
            "region": "IT",      # Critical: Italy
            "language": "it"     # Critical: Italian
        }
        
        print(f"DEBUG: Searching 'pollo' (Region: IT)...")
        res = requests.get(url, headers=headers, params=params, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            # print(f"RAW: {data}")
            
            foods = data.get("foods", {}).get("food", [])
            if foods:
                print(f"✅ Search Success! Found: {len(foods)} items.")
                for i, f in enumerate(foods):
                    print(f"   {i+1}. {f['food_name']} (Type: {f.get('food_type')}, Brand: {f.get('brand_name')})")
            else:
                 print(f"⚠️ Search returned empty list. Raw: {data}")
        else:
            print(f"❌ Search Failed: {res.status_code} - {res.text}")
    
    except Exception as e:
         print(f"❌ Search Exception: {e}")

if __name__ == "__main__":
    token = get_token()
    search_chicken(token)
