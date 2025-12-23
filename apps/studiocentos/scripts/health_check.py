import requests
import sys
import time

def check_service(name, url, expected_code=200):
    print(f"Checking {name} at {url}...", end=" ")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_code:
            print("✅ OK")
            return True
        else:
            print(f"❌ FAIL (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def run_tests():
    print("=== SYSTEM HEALTH CHECK ===")

    # 1. Frontend
    frontend_ok = check_service("Frontend", "http://localhost:3000")

    # 2. Backend Health (Direct)
    backend_ok = check_service("Backend Health (Direct)", "http://localhost:8002/api/v1/health")

    # 2b. Backend Health (via Nginx Proxy)
    proxy_ok = check_service("Backend Health (via Proxy)", "http://localhost/api/v1/health")

    # 3. AI Microservice Health
    ai_ok = check_service("AI Microservice Health", "http://localhost:8001/health")

    success = frontend_ok and backend_ok and proxy_ok and ai_ok

    if success:
        print("\n✅ SYSTEM OPERATIONAL")
        sys.exit(0)
    else:
        print("\n❌ SYSTEM ISSUES DETECTED")
        sys.exit(1)

if __name__ == "__main__":
    # Wait for services to be fully ready
    print("Waiting 5s for services to stabilize...")
    time.sleep(5)
    run_tests()
