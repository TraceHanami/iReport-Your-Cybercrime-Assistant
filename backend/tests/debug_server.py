# debug_server.py
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def debug_server():
    print("🔍 Debugging Server Endpoints")
    print("=" * 60)
    
    # Test basic endpoints
    endpoints = [
        ("GET", "/api/health"),
        ("GET", "/api/system/status"),
        ("GET", "/api"),
        ("POST", "/api/auth/login"),
        ("GET", "/api/track/case/IR2025102883F90314")
    ]
    
    for method, endpoint in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json={})
            
            print(f"{method:6} {endpoint:40} | {response.status_code}")
            
            if response.status_code == 405:
                # Try to get allowed methods
                try:
                    options_response = requests.options(f"{BASE_URL}{endpoint}")
                    if 'Allow' in options_response.headers:
                        print(f"       Allowed methods: {options_response.headers['Allow']}")
                except:
                    pass
                    
        except Exception as e:
            print(f"{method:6} {endpoint:40} | ERROR: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    debug_server()