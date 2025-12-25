import requests
import base64
import json

# User provided keys
ID = "4a0cca579bd94da6a681497f36f11582"
SECRET = "72ec8b7b1b294c898eee839f866a03fc"

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except:
        return "Unknown"

def test_combination(client_id, client_secret, label):
    print(f"\n--- Testing {label} ---")
    print(f"ID: {client_id[:5]}...{client_id[-5:]}")
    print(f"Secret: {client_secret[:5]}...{client_secret[-5:]}")
    
    auth_str = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    token_url = "https://oauth.fatsecret.com/connect/token"
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials", "scope": "basic"}
    
    try:
        res = requests.post(token_url, headers=headers, data=data, timeout=10)
        if res.status_code == 200:
            print("✅ SUCCESS! Token acquired.")
            return True
        else:
            print(f"❌ FAILED: {res.status_code} - {res.text}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    ip = get_public_ip()
    print(f"DEBUG: Current Server Public IP: {ip}")
    
    # Try Combination 1 (ID as Client ID, SECRET as Client Secret)
    success1 = test_combination(ID, SECRET, "Normal (ID:SECRET)")
    
    # Try Combination 2 (SECRET as Client ID, ID as Client Secret)
    success2 = test_combination(SECRET, ID, "Swapped (SECRET:ID)")
    
    if not success1 and not success2:
        print("\n❌ BOTH COMBINATIONS FAILED.")
        print(f"If the keys are correct, please ensure IP {ip} is whitelisted in FatSecret Platform API preferences.")
    elif success1:
        print("\n✅ NORMAL Combination works!")
    else:
        print("\n✅ SWAPPED Combination works!")
