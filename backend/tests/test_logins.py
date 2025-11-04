# test_logins.py
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_logins():
    print("🔐 Testing User Logins")
    print("=" * 50)
    
    test_users = [
        {"email": "admin@ireport.com", "password": "admin123", "role": "admin"},
        {"email": "officer@ireport.com", "password": "password123", "role": "police"},
        {"email": "public@ireport.com", "password": "password123", "role": "public"},
    ]
    
    successful_logins = 0
    
    for user in test_users:
        login_data = {
            "email": user["email"],
            "password": user["password"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token', 'No token')
                successful_logins += 1
                print(f"✅ {user['role']:8} | {user['email']:25} | Login successful")
                print(f"   Token: {token[:30]}...")
            else:
                error_msg = response.json().get('error', 'Unknown error')
                print(f"❌ {user['role']:8} | {user['email']:25} | Login failed: {response.status_code}")
                print(f"   Error: {error_msg}")
                
        except Exception as e:
            print(f"💥 {user['role']:8} | {user['email']:25} | Error: {e}")
    
    print("=" * 50)
    print(f"\n📊 Results: {successful_logins}/{len(test_users)} successful logins")
    
    if successful_logins == len(test_users):
        print("🎉 All test users can login successfully!")
    else:
        print("\n💡 If some logins failed, you can:")
        print("   1. Register new users at /api/auth/register")
        print("   2. Use existing working users for testing")
        print("   3. Check your database for existing users")

if __name__ == "__main__":
    test_logins()