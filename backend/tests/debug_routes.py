# test_auth_working.py
import requests
import json

BASE_URL = "http://localhost:5000"

def test_auth_system():
    print("🧪 Testing Authentication System:")
    print("=" * 60)
    
    # Test 1: Auth test endpoint
    print("1. Testing auth test endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/test")
        print(f"   GET Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: {data['message']}")
        else:
            print(f"   ❌ FAILED: {response.text}")
    except Exception as e:
        print(f"   💥 ERROR: {e}")
    
    # Test 2: Login with admin user
    print("\n2. Testing admin login...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@ireport.com", "password": "admin123"},
            headers={"Content-Type": "application/json"}
        )
        print(f"   POST Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: {data['message']}")
            print(f"   User: {data['user']['email']} (Role: {data['user']['role']})")
            print(f"   Token: {data['token'][:50]}...")
            admin_token = data['token']
        else:
            print(f"   ❌ FAILED: {response.text}")
            admin_token = None
    except Exception as e:
        print(f"   💥 ERROR: {e}")
        admin_token = None
    
    # Test 3: Login with public user
    print("\n3. Testing public user login...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "user@ireport.com", "password": "user123"},
            headers={"Content-Type": "application/json"}
        )
        print(f"   POST Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: {data['message']}")
            print(f"   User: {data['user']['email']} (Role: {data['user']['role']})")
            public_token = data['token']
        else:
            print(f"   ❌ FAILED: {response.text}")
            public_token = None
    except Exception as e:
        print(f"   💥 ERROR: {e}")
        public_token = None
    
    # Test 4: Test registration (if we have tokens, we can test more)
    print("\n4. Testing user registration...")
    try:
        test_email = f"testuser{hash('test')}@test.com"
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": test_email,
                "password": "test123",
                "full_name": "Test User",
                "phone": "+911234567890",
                "role": "public"
            },
            headers={"Content-Type": "application/json"}
        )
        print(f"   POST Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: {data['message']}")
            if data.get('debug_mode'):
                print(f"   OTP: {data.get('otp')}")
        else:
            print(f"   ❌ FAILED: {response.text}")
    except Exception as e:
        print(f"   💥 ERROR: {e}")
    
    return admin_token, public_token

if __name__ == "__main__":
    admin_token, public_token = test_auth_system()
    
    if admin_token and public_token:
        print(f"\n🎉 AUTHENTICATION SYSTEM IS WORKING!")
        print(f"   Admin token: {admin_token[:30]}...")
        print(f"   Public token: {public_token[:30]}...")
    else:
        print(f"\n⚠️  Some authentication tests failed")