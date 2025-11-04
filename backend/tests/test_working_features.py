# test_working_features_fixed.py
import requests
import json

# CORRECT: BASE_URL without /api
BASE_URL = "http://127.0.0.1:5000"

def get_auth_token(email, password):
    """Get authentication token with correct URL"""
    try:
        # CORRECT: /api/auth/login (not /api/api/auth/login)
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                               json={"email": email, "password": password})
        
        print(f"Login response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Login successful for {email}")
            return data.get('token')
        else:
            print(f"✗ Login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Login error: {e}")
        return None

def test_basic_functionality():
    """Test basic endpoints without auth"""
    print("=== Testing Basic Functionality ===\n")
    
    # Test health endpoint - CORRECT URL
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health endpoint: 200")
            print(f"   Status: {data.get('status')}")
        else:
            print(f"✗ Health endpoint: {response.status_code}")
    except Exception as e:
        print(f"✗ Health endpoint: ERROR - {e}")
    
    # Test track case - CORRECT URL
    try:
        response = requests.get(f"{BASE_URL}/api/track/case/IR2025102883F90314")
        if response.status_code == 200:
            print(f"✓ Track case: 200")
        else:
            print(f"✗ Track case: {response.status_code}")
    except Exception as e:
        print(f"✗ Track case: ERROR - {e}")

def test_authentication():
    """Test authentication with different users"""
    print("\n=== Testing Authentication ===\n")
    
    users = [
        ("admin@ireport.com", "admin123", "Admin"),
        ("officer@ireport.com", "password123", "Police Officer"),
        ("public@ireport.com", "password123", "Public User")
    ]
    
    tokens = {}
    
    for email, password, role in users:
        token = get_auth_token(email, password)
        if token:
            tokens[role.lower()] = token
            print(f"✓ {role} authentication: SUCCESS")
            
            # Test authenticated endpoint
            headers = {'Authorization': f'Bearer {token}'}
            if role == "Admin":
                test_endpoint = "/api/admin/dashboard"
            elif role == "Police Officer":
                test_endpoint = "/api/police/dashboard"
            else:
                test_endpoint = "/api/complaints/my-complaints"
            
            try:
                response = requests.get(f"{BASE_URL}{test_endpoint}", headers=headers)
                print(f"   Endpoint: {response.status_code}")
            except Exception as e:
                print(f"   Endpoint error: {e}")
        else:
            print(f"✗ {role} authentication: FAILED")
    
    return tokens

def test_advanced_features(tokens):
    """Test advanced features with admin user"""
    print("\n=== Testing Advanced Features ===\n")
    
    admin_token = tokens.get("admin")
    if not admin_token:
        print("✗ Cannot test advanced features - admin login failed")
        return
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Test analytics endpoints - CORRECT URLS
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
                print(f"✓ {endpoint.split('/')[-1]}: 200")
            else:
                print(f"✗ {endpoint.split('/')[-1]}: {response.status_code}")
        except Exception as e:
            print(f"✗ {endpoint.split('/')[-1]}: ERROR - {e}")
    
    # Test other endpoints
    other_endpoints = [
        "/api/sms/status",
        "/api/notifications/user",
    ]
    
    for endpoint in other_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            if response.status_code == 200:
                print(f"✓ {endpoint.split('/')[-1]}: 200")
            else:
                print(f"✗ {endpoint.split('/')[-1]}: {response.status_code}")
        except Exception as e:
            print(f"✗ {endpoint.split('/')[-1]}: ERROR - {e}")
    
    # Test report generation
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

def test_complaint_creation(tokens):
    """Test creating a new complaint"""
    print("\n=== Testing Complaint Creation ===\n")
    
    public_token = tokens.get("public user")
    if not public_token:
        print("✗ Cannot test complaint creation - public login failed")
        return
    
    headers = {'Authorization': f'Bearer {public_token}'}
    
    complaint_data = {
        "title": "Fixed Test - Theft Case",
        "description": "Testing with corrected URLs.",
        "incident_date": "2025-10-28T10:00:00Z",
        "state": "Delhi",
        "district": "Test District",
        "location": "Test Location",
        "victim_name": "Test User",
        "victim_age": 30,
        "victim_gender": "Male",
        "is_missing_person": False,
        "is_injury_involved": False,
        "is_property_damage": False,
        "police_complaint_filed": False,
        "is_anonymous": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/complaints/file", 
                               json=complaint_data, 
                               headers=headers)
        
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Complaint filed successfully!")
            print(f"   Case ID: {data['case_id']}")
            return data['case_id']
        else:
            print(f"✗ Failed to file complaint: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Complaint creation error: {e}")
        return None

if __name__ == "__main__":
    test_basic_functionality()
    tokens = test_authentication()
    test_advanced_features(tokens)
    new_case_id = test_complaint_creation(tokens)
    
    if new_case_id:
        print(f"\n🎉 New test case created: {new_case_id}")
        print(f"Track it at: {BASE_URL}/api/track/case/{new_case_id}")