import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"
ADMIN_EMAIL = "admin@ireport.com"
ADMIN_PASSWORD = "admin123"

def get_auth_token(email, password):
    response = requests.post(f"{BASE_URL}/auth/login", 
                           json={"email": email, "password": password})
    return response.json().get('token') if response.status_code == 200 else None

def test_advanced_features():
    print("=== Testing Advanced Features ===\n")
    
    admin_token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
    headers = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
    
    # Test advanced analytics
    endpoints = [
        ("GET", "/analytics/trends", "Trend analysis"),
        ("GET", "/analytics/heatmap", "Geospatial heatmap"),
        ("GET", "/analytics/predictive-insights", "Predictive insights"),
        ("GET", "/analytics/performance", "Performance metrics"),
        ("GET", "/analytics/patrol-recommendations", "Patrol recommendations"),
        ("GET", "/sms/status", "SMS service status"),
        ("GET", "/notifications/user", "User notifications")
    ]
    
    for method, endpoint, description in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            status = "✓" if response.status_code == 200 else "✗"
            print(f"{status} {description}: {response.status_code}")
        except Exception as e:
            print(f"✗ {description}: ERROR - {e}")
    
    # Test report generation
    try:
        response = requests.post(f"{BASE_URL}/reports/analytics", 
                               json={"type": "monthly"}, 
                               headers=headers)
        if response.status_code == 200:
            print("✓ Analytics report generation: 200")
        else:
            print(f"✗ Analytics report generation: {response.status_code}")
    except Exception as e:
        print(f"✗ Analytics report generation: ERROR - {e}")

if __name__ == "__main__":
    test_advanced_features()