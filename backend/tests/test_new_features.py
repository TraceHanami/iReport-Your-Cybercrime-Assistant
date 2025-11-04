import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"
ADMIN_EMAIL = "admin@ireport.com"
ADMIN_PASSWORD = "admin123"

def get_auth_token(email, password):
    response = requests.post(f"{BASE_URL}/auth/login", 
                           json={"email": email, "password": password})
    return response.json().get('token') if response.status_code == 200 else None

def test_new_features():
    print("=== Testing New Advanced Features ===\n")
    
    admin_token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
    headers = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
    
    # Test advanced analytics endpoints
    analytics_endpoints = [
        ("GET", "/analytics/trends", "Trend analysis"),
        ("GET", "/analytics/heatmap", "Geospatial heatmap"),
        ("GET", "/analytics/predictive-insights", "Predictive insights"),
        ("GET", "/analytics/performance", "Performance metrics"),
        ("GET", "/analytics/patrol-recommendations", "Patrol recommendations"),
    ]
    
    for method, endpoint, description in analytics_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            status = "✓" if response.status_code == 200 else "✗"
            print(f"{status} {description}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Data received: {len(str(data))} bytes")
        except Exception as e:
            print(f"✗ {description}: ERROR - {e}")
    
    # Test SMS status
    try:
        response = requests.get(f"{BASE_URL}/sms/status", headers=headers)
        status = "✓" if response.status_code == 200 else "✗"
        print(f"{status} SMS service status: {response.status_code}")
        if response.status_code == 200:
            print(f"   SMS configured: {response.json().get('configured', False)}")
    except Exception as e:
        print(f"✗ SMS status: ERROR - {e}")
    
    # Test notifications
    try:
        response = requests.get(f"{BASE_URL}/notifications/user", headers=headers)
        status = "✓" if response.status_code == 200 else "✗"
        print(f"{status} Notifications: {response.status_code}")
    except Exception as e:
        print(f"✗ Notifications: ERROR - {e}")
    
    # Test report generation
    try:
        response = requests.post(f"{BASE_URL}/reports/analytics", 
                               json={"type": "monthly"}, 
                               headers=headers)
        if response.status_code == 200:
            print("✓ Analytics report generation: 200")
            data = response.json()
            print(f"   Download URL: {data.get('download_url')}")
        else:
            print(f"✗ Analytics report generation: {response.status_code}")
    except Exception as e:
        print(f"✗ Analytics report generation: ERROR - {e}")

if __name__ == "__main__":
    test_new_features()