# test_all_endpoints.py
import requests
import json
from test_config import TEST_USERS, BASE_URL  # Use the unified config

def get_auth_token(email, password):
    """Get authentication token"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            return response.json().get('token')
        else:
            print(f"Login failed for {email}: {response.status_code} - {response.json().get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Login error for {email}: {e}")
        return None

def test_all_endpoints():
    print("=== Testing All iReport API Endpoints ===")
    print()
    
    # Get tokens for all users
    admin_token = get_auth_token(TEST_USERS["admin"]["email"], TEST_USERS["admin"]["password"])
    police_token = get_auth_token(TEST_USERS["police"]["email"], TEST_USERS["police"]["password"])
    public_token = get_auth_token(TEST_USERS["public"]["email"], TEST_USERS["public"]["password"])
    
    # Test public endpoints
    endpoints = [
        ("GET", "/", None, "Root endpoint"),
        ("GET", "/track/case/IR2025102883F90314", None, "Track case"),
    ]
    
    for method, endpoint, headers, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers)
            
            if response.status_code in [200, 201]:
                print(f"✓ {description}: {response.status_code}")
            else:
                print(f"✗ {description}: {response.status_code}")
        except Exception as e:
            print(f"✗ {description}: ERROR - {e}")
    
    # Test login
    if admin_token:
        print(f"✓ Login: 200")
    else:
        print(f"✗ Login: Failed")
    
    # Test admin endpoints
    if admin_token:
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        admin_endpoints = [
            ("GET", "/admin/dashboard", admin_headers, "Admin dashboard"),
            ("GET", "/admin/cases", admin_headers, "All cases"),
            ("GET", "/admin/users", admin_headers, "All users"),
            ("GET", "/admin/volunteers/pending", admin_headers, "Pending volunteers"),
        ]
        
        for method, endpoint, headers, description in admin_endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                if response.status_code == 200:
                    print(f"✓ {description}: {response.status_code}")
                else:
                    print(f"✗ {description}: {response.status_code}")
            except Exception as e:
                print(f"✗ {description}: ERROR - {e}")
    
    # Test police endpoints
    if police_token:
        police_headers = {"Authorization": f"Bearer {police_token}"}
        police_endpoints = [
            ("GET", "/police/dashboard", police_headers, "Police dashboard"),
            ("GET", "/police/cases", police_headers, "Police cases"),
        ]
        
        for method, endpoint, headers, description in police_endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                if response.status_code == 200:
                    print(f"✓ {description}: {response.status_code}")
                else:
                    print(f"✗ {description}: {response.status_code}")
            except Exception as e:
                print(f"✗ {description}: ERROR - {e}")
    else:
        print(f"✗ Police dashboard: 401")
        print(f"✗ Police cases: 401")
    
    # Test user endpoints
    if public_token:
        public_headers = {"Authorization": f"Bearer {public_token}"}
        try:
            response = requests.get(f"{BASE_URL}/complaints/my-complaints", headers=public_headers)
            if response.status_code == 200:
                print(f"✓ User complaints: {response.status_code}")
            else:
                print(f"✗ User complaints: {response.status_code}")
        except Exception as e:
            print(f"✗ User complaints: ERROR - {e}")
    else:
        print(f"✗ User complaints: 401")

    print("\n=== Testing Complaint Creation ===")
    
    if public_token:
        public_headers = {"Authorization": f"Bearer {public_token}"}
        complaint_data = {
            "title": "Test Complaint",
            "description": "This is a test complaint for system testing",
            "incident_date": "2025-10-28T10:00:00Z",
            "state": "Test State",
            "district": "Test District", 
            "location": "Test Location",
            "victim_name": "Test Victim",
            "victim_age": 30,
            "victim_gender": "other",
            "crime_type": "harassment"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/complaints/file", 
                                   json=complaint_data, 
                                   headers=public_headers)
            if response.status_code == 201:
                data = response.json()
                print(f"✓ Complaint filed successfully!")
                print(f"   Case ID: {data.get('case_id')}")
                print(f"   Priority: {data.get('priority')}")
                print(f"   Crime Type: {data.get('crime_type')}")
                print(f"   Assigned to: {data.get('assigned_to', 'police')}")
                
                # Store the case ID for tracking
                case_id = data.get('case_id')
            else:
                print(f"✗ Complaint filing failed: {response.status_code}")
                print(f"   Response: {response.text}")
                case_id = None
        except Exception as e:
            print(f"✗ Complaint filing error: {e}")
            case_id = None
    else:
        print("✗ Could not login as public user")
        case_id = None

    print("\n=== Testing Case Assignment ===")
    
    if admin_token:
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        try:
            # Get all cases
            response = requests.get(f"{BASE_URL}/admin/cases", headers=admin_headers)
            if response.status_code == 200:
                data = response.json()
                cases = data.get('complaints', [])
                print(f"✓ Found {len(cases)} cases in system")
                if cases:
                    sample_case = cases[0]
                    print(f"   Sample case: {sample_case.get('case_id')} - {sample_case.get('title')} - {sample_case.get('crime_type', '').title()} Case")
                    
                    # Test case details
                    if case_id:  # Use the newly created case
                        details_response = requests.get(f"{BASE_URL}/complaints/details/{case_id}", headers=admin_headers)
                        if details_response.status_code == 200:
                            print(f"✓ Case details retrieved for {case_id}")
                        else:
                            print(f"✗ Could not get details for {case_id}: {details_response.status_code}")
            else:
                print(f"✗ Could not fetch cases: {response.status_code}")
        except Exception as e:
            print(f"✗ Case assignment test error: {e}")

    print("\n=== Testing Chatbot ===")
    
    if public_token:
        public_headers = {"Authorization": f"Bearer {public_token}"}
        try:
            # Start chat session
            session_response = requests.post(f"{BASE_URL}/chatbot/start-session", headers=public_headers)
            if session_response.status_code == 200:
                session_data = session_response.json()
                session_id = session_data.get('session_id')
                print(f"✓ Chat session started: {session_id}")
                
                # Send a message
                message_data = {
                    "session_id": session_id,
                    "message": "How do I file a complaint?"
                }
                message_response = requests.post(f"{BASE_URL}/chatbot/send-message", 
                                               json=message_data, 
                                               headers=public_headers)
                if message_response.status_code == 200:
                    message_data = message_response.json()
                    bot_response = message_data.get('response', '')
                    print(f"✓ Chatbot response: {bot_response[:80]}...")
                else:
                    print(f"✗ Chatbot message failed: {message_response.status_code}")
            else:
                print(f"✗ Chatbot session failed: {session_response.status_code}")
        except Exception as e:
            print(f"✗ Chatbot test error: {e}")
    else:
        print("✗ Could not login for chatbot test")

    # Final summary
    if case_id:
        print(f"\n🎉 New case created: {case_id}")
        print(f"Track it at: {BASE_URL}/track/case/{case_id}")

if __name__ == "__main__":
    test_all_endpoints()