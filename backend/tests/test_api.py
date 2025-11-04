import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_api():
    print("Testing iReport API...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/")
        print(f"✓ Root endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")
    
    # Test login with seeded admin user
    login_data = {
        "email": "admin@ireport.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('token')
            print(f"✓ Admin login successful - Token: {token[:20]}...")
            
            # Test complaints endpoint with token
            headers = {'Authorization': f'Bearer {token}'}
            complaints_response = requests.get(f"{BASE_URL}/complaints/my-complaints", headers=headers)
            print(f"✓ Complaints endpoint: {complaints_response.status_code}")
            
        else:
            print(f"✗ Admin login failed: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"✗ Login test failed: {e}")
    
    # Test public endpoints
    try:
        track_response = requests.get(f"{BASE_URL}/track/case/IR20241024ABCD1234")
        print(f"✓ Track endpoint: {track_response.status_code}")
    except Exception as e:
        print(f"✗ Track endpoint failed: {e}")

if __name__ == "__main__":
    test_api()