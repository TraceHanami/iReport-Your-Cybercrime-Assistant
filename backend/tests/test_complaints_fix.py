# test_complaints_fix.py
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_complaints_fix():
    print("🧪 Testing Complaints Endpoint Fix")
    print("=" * 50)
    
    # Login as admin
    login_data = {"email": "admin@ireport.com", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("❌ Failed to login")
        return
    
    token = response.json().get('token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test the complaints root endpoint
    response = requests.get(f"{BASE_URL}/complaints", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ /api/complaints endpoint working!")
        print(f"   Found {data.get('count', 0)} complaints")
        print(f"   Status: {response.status_code}")
    else:
        print(f"❌ /api/complaints endpoint failed: {response.status_code}")
        print(f"   Response: {response.text}")
    
    print("=" * 50)

if __name__ == "__main__":
    test_complaints_fix()