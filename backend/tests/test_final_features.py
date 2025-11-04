# test_final_features_fixed.py
import requests
import json

# CORRECT: BASE_URL without /api
BASE_URL = "http://127.0.0.1:5000"

def get_auth_token(email, password):
    """Get authentication token with correct URL"""
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                               json={"email": email, "password": password})
        
        if response.status_code == 200:
            return response.json().get('token')
        else:
            print(f"Login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_all_features():
    print("=== FINAL TEST: All iReport Advanced Features ===\n")
    
    # Get admin token - CORRECT URL
    admin_token = get_auth_token("admin@ireport.com", "admin123")
    if not admin_token:
        print("✗ Cannot test features - admin login failed")
        return
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    print("=== Advanced Analytics ===")
    analytics_endpoints = [
        "/api/analytics/trends",
        "/api/analytics/heatmap", 
        "/api/analytics/predictive-insights",
        "/api/analytics/performance",
        "/api/analytics/patrol-recommendations",
    ]
    
    for endpoint in analytics_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ {endpoint.split('/')[-1]}: 200")
            else:
                print(f"✗ {endpoint.split('/')[-1]}: {response.status_code}")
        except Exception as e:
            print(f"✗ {endpoint.split('/')[-1]}: ERROR - {e}")
    
    print("\n=== Communication Features ===")
    try:
        response = requests.get(f"{BASE_URL}/api/sms/status", headers=headers)
        if response.status_code == 200:
            print(f"✓ SMS service status: 200")
        else:
            print(f"✗ SMS service status: {response.status_code}")
    except Exception as e:
        print(f"✗ SMS status: ERROR - {e}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/notifications/user", headers=headers)
        if response.status_code == 200:
            print(f"✓ Notifications: 200")
        else:
            print(f"✗ Notifications: {response.status_code}")
    except Exception as e:
        print(f"✗ Notifications: ERROR - {e}")
    
    print("\n=== Report Generation ===")
    try:
        response = requests.post(f"{BASE_URL}/api/reports/analytics", 
                               json={"type": "monthly"}, 
                               headers=headers)
        if response.status_code == 200:
            print("✓ Analytics report generation: 200")
        else:
            print(f"✗ Analytics report generation: {response.status_code}")
    except Exception as e:
        print(f"✗ Analytics report generation: ERROR - {e}")
    
    print("\n=== System Summary ===")
    try:
        response = requests.get(f"{BASE_URL}/api/system/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ System Status: {data.get('status')}")
        else:
            print(f"✗ System status: {response.status_code}")
    except Exception as e:
        print(f"✗ System status: ERROR - {e}")

if __name__ == "__main__":
    test_all_features()