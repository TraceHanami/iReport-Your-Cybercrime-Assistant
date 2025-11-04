# test_final.py
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def get_auth_token(email, password):
    """Get authentication token for testing"""
    try:
        login_data = {
            "email": email,
            "password": password
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            return data.get('token')
        else:
            print(f"Login failed for {email}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Login error for {email}: {e}")
        return None

def test_all_endpoints():
    # Get authentication tokens
    admin_token = get_auth_token("admin@ireport.com", "admin123")
    public_token = get_auth_token("public@ireport.com", "password123")
    
    print("🧪 Testing iReport API Endpoints...")
    print("=" * 60)
    
    # Public endpoints (no auth required)
    public_endpoints = [
        "/health",
        "/system/status",
        "",
        "/auth/login",
        "/auth/register",
        "/track/case/IR2025102883F90314"
    ]
    
    for endpoint in public_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}") if endpoint != "/auth/login" and endpoint != "/auth/register" else requests.post(f"{BASE_URL}{endpoint}", json={"email": "test@test.com", "password": "test"})
            status_emoji = "✅" if response.status_code in [200, 201] else "⚠️ " if response.status_code == 404 else "❌"
            print(f"{status_emoji} {endpoint:25} | Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint:25} | ERROR: {e}")
    
    print("\n🔐 Testing authenticated endpoints...")
    
    # Authenticated endpoints (require token)
    if admin_token:
        auth_headers = {"Authorization": f"Bearer {admin_token}"}
        auth_endpoints = [
            "/complaints",
            "/complaints/my-complaints",
            "/analytics/trends",
            "/analytics/heatmap",
            "/admin/dashboard",
            "/admin/cases"
        ]
        
        for endpoint in auth_endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=auth_headers)
                status_emoji = "✅" if response.status_code == 200 else "❌"
                print(f"{status_emoji} {endpoint:25} | Status: {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint:25} | ERROR: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_all_endpoints()