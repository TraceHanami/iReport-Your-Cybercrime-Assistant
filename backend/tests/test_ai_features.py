import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = f"testuser{int(time.time())}@test.com"
TEST_PASSWORD = "test123"

class iReportTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.tokens = {}
        self.test_data = {}
        
    def print_step(self, message):
        print(f"\n{'='*60}")
        print(f"🔧 {message}")
        print(f"{'='*60}")
    
    def print_success(self, message):
        print(f"✅ {message}")
    
    def print_error(self, message):
        print(f"❌ {message}")
    
    def print_info(self, message):
        print(f"ℹ️  {message}")
    
    def print_warning(self, message):
        print(f"⚠️  {message}")
    
    def test_health_endpoints(self):
        """Test basic health and system status endpoints"""
        self.print_step("Testing Health Endpoints")
        
        try:
            # Test API health
            response = requests.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Health Check: {data['message']}")
            else:
                self.print_error(f"Health Check failed: {response.status_code}")
                return False
            
            # Test system status
            response = requests.get(f"{self.base_url}/api/system/status")
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"System Status: {data['status']}")
                self.print_info(f"Database: {data['database']}")
            else:
                self.print_error(f"System Status failed: {response.status_code}")
                return False
            
            # Test API info
            response = requests.get(f"{self.base_url}/api")
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"API Info: {data['message']} v{data['version']}")
            else:
                self.print_error(f"API Info failed: {response.status_code}")
                return False
                
            return True
            
        except Exception as e:
            self.print_error(f"Health endpoints test failed: {str(e)}")
            return False
    
    def test_auth_flow(self):
        """Test complete authentication flow"""
        self.print_step("Testing Authentication Flow")
        
        try:
            # First, test login with existing test users (skip registration for now)
            test_users = [
                {"email": "admin@ireport.com", "password": "admin123", "role": "admin"},
                {"email": "police1@ireport.com", "password": "police123", "role": "police"},
                {"email": "volunteer1@ireport.com", "password": "volunteer123", "role": "volunteer"},
                {"email": "user@ireport.com", "password": "user123", "role": "public"}
            ]
            
            for user in test_users:
                response = requests.post(f"{self.base_url}/api/auth/login", 
                                       json={"email": user['email'], "password": user['password']})
                
                if response.status_code == 200:
                    data = response.json()
                    self.tokens[user['role']] = data['token']
                    self.test_data[f"{user['role']}_user_id"] = data['user']['id']
                    self.print_success(f"Login successful: {user['role']} (ID: {data['user']['id']})")
                else:
                    self.print_error(f"Login failed for {user['role']}: {response.status_code} - {response.text}")
                    return False
            
            # Test registration with debug mode (return OTP in response)
            register_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "full_name": "Test User",
                "role": "public",
                "phone": "+911234567890"
            }
            
            response = requests.post(f"{self.base_url}/api/auth/register", 
                                   json=register_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('debug_mode'):
                    otp = data.get('otp', 'DEBUG_OTP')
                    self.print_success(f"Registration in debug mode - OTP: {otp}")
                    
                    # Verify OTP with the provided OTP
                    verify_data = {
                        "email": TEST_EMAIL,
                        "otp": otp
                    }
                    
                    response = requests.post(f"{self.base_url}/api/auth/verify-otp", 
                                           json=verify_data)
                    
                    if response.status_code == 201:
                        data = response.json()
                        self.tokens['new_public'] = data['token']
                        self.test_data['new_public_user_id'] = data['user']['id']
                        self.print_success(f"New user registered - ID: {data['user']['id']}")
                    else:
                        self.print_warning(f"New user registration failed: {response.status_code} - {response.text}")
                else:
                    self.print_warning("Registration succeeded but not in debug mode - check email for OTP")
            else:
                self.print_warning(f"New user registration failed: {response.status_code} - {response.text}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Auth flow test failed: {str(e)}")
            return False
    
    def test_complaint_management(self):
        """Test complaint filing and management"""
        self.print_step("Testing Complaint Management")
        
        try:
            if 'public' not in self.tokens:
                self.print_warning("Skipping complaint test - no public user token")
                return True
            
            headers = {"Authorization": f"Bearer {self.tokens['public']}"}
            
            # File a new complaint
            complaint_data = {
                "title": "Test Complaint - Stolen Bicycle",
                "description": "My bicycle was stolen from outside the supermarket yesterday evening around 7 PM.",
                "incident_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "state": "Delhi",
                "district": "Central Delhi",
                "location": "Outside Supermarket, Connaught Place",
                "victim_name": "Rahul Sharma",
                "victim_age": 28,
                "victim_gender": "Male",
                "victim_contact": "+919876543210",
                "is_property_damage": False,
                "estimated_loss": 5000,
                "police_complaint_filed": True,
                "police_station": "Connaught Place Police Station",
                "witness_details": "Security guard saw two suspicious persons",
                "suspect_description": "Two males, aged 20-25, wearing black jackets"
            }
            
            response = requests.post(f"{self.base_url}/api/complaints/file", 
                                   json=complaint_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.test_data['case_id'] = data['case_id']
                self.print_success(f"Complaint filed successfully - Case ID: {data['case_id']}")
                self.print_info(f"Priority: {data['priority']}, Crime Type: {data['crime_type']}")
            else:
                self.print_error(f"Complaint filing failed: {response.status_code} - {response.text}")
                return False
            
            # Test getting user's complaints
            response = requests.get(f"{self.base_url}/api/complaints/my-complaints", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Retrieved {len(data.get('complaints', []))} user complaints")
            else:
                self.print_error(f"Get user complaints failed: {response.status_code}")
            
            # Test case tracking
            if 'case_id' in self.test_data:
                response = requests.get(f"{self.base_url}/api/track/case/{self.test_data['case_id']}", 
                                      headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self.print_success(f"Case tracking working - Status: {data.get('status', 'Unknown')}")
                else:
                    self.print_error(f"Case tracking failed: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Complaint management test failed: {str(e)}")
            return False
    
    def test_admin_features(self):
        """Test admin-specific features"""
        self.print_step("Testing Admin Features")
        
        try:
            if 'admin' not in self.tokens:
                self.print_error("Skipping admin test - no admin token")
                return False
            
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            
            # Test admin dashboard
            response = requests.get(f"{self.base_url}/api/admin/dashboard", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Admin dashboard loaded - Total cases: {data['stats']['total_cases']}")
            else:
                self.print_error(f"Admin dashboard failed: {response.status_code} - {response.text}")
                return False
            
            # Test get all cases
            response = requests.get(f"{self.base_url}/api/admin/cases", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Retrieved {data['total']} cases for admin")
            else:
                self.print_error(f"Get all cases failed: {response.status_code}")
            
            # Test get all users
            response = requests.get(f"{self.base_url}/api/admin/users", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Retrieved {data['total']} users for admin")
            else:
                self.print_error(f"Get all users failed: {response.status_code}")
            
            # Test police officers list
            response = requests.get(f"{self.base_url}/api/admin/police-officers", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Retrieved {len(data['officers'])} police officers")
            else:
                self.print_error(f"Get police officers failed: {response.status_code}")
            
            # Test analytics
            response = requests.get(f"{self.base_url}/api/admin/analytics/overview", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Analytics loaded - Period: {data.get('period_days', 'N/A')} days")
            else:
                self.print_error(f"Analytics failed: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Admin features test failed: {str(e)}")
            return False
    
    def test_police_features(self):
        """Test police-specific features"""
        self.print_step("Testing Police Features")
        
        try:
            if 'police' not in self.tokens:
                self.print_error("Skipping police test - no police token")
                return False
            
            headers = {"Authorization": f"Bearer {self.tokens['police']}"}
            
            # Test police dashboard
            response = requests.get(f"{self.base_url}/api/police/dashboard", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_success("Police dashboard loaded successfully")
            else:
                self.print_error(f"Police dashboard failed: {response.status_code} - {response.text}")
                return False
            
            # Test police cases
            response = requests.get(f"{self.base_url}/api/police/cases", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Retrieved {len(data.get('cases', []))} police cases")
            else:
                self.print_error(f"Get police cases failed: {response.status_code}")
            
            # Test performance metrics
            response = requests.get(f"{self.base_url}/api/police/performance", 
                                  headers=headers)
            
            if response.status_code == 200:
                self.print_success("Police performance metrics loaded")
            else:
                self.print_error(f"Police performance failed: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Police features test failed: {str(e)}")
            return False
    
    def test_advanced_features(self):
        """Test advanced features like analytics, notifications, etc."""
        self.print_step("Testing Advanced Features")
        
        try:
            if 'admin' not in self.tokens:
                self.print_error("Skipping advanced features test - no admin token")
                return False
            
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            
            # Test advanced analytics
            response = requests.get(f"{self.base_url}/api/analytics/trends", 
                                  headers=headers)
            
            if response.status_code == 200:
                self.print_success("Advanced analytics trends loaded")
            else:
                self.print_warning(f"Advanced analytics failed: {response.status_code}")
            
            # Test notifications
            if 'public' in self.tokens:
                headers_public = {"Authorization": f"Bearer {self.tokens['public']}"}
                response = requests.get(f"{self.base_url}/api/notifications/user", 
                                      headers=headers_public)
                
                if response.status_code == 200:
                    data = response.json()
                    self.print_success(f"Notifications loaded - Count: {len(data.get('notifications', []))}")
                else:
                    self.print_warning(f"Notifications failed: {response.status_code}")
            
            # Test chatbot
            if 'public' in self.tokens:
                headers_public = {"Authorization": f"Bearer {self.tokens['public']}"}
                response = requests.get(f"{self.base_url}/api/chatbot/user-sessions", 
                                      headers=headers_public)
                
                if response.status_code == 200:
                    self.print_success("Chatbot sessions accessible")
                else:
                    self.print_warning(f"Chatbot failed: {response.status_code}")
            
            # Test reports
            response = requests.get(f"{self.base_url}/api/reports/list", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Reports list loaded - Count: {len(data.get('reports', []))}")
            else:
                self.print_warning(f"Reports list failed: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Advanced features test failed: {str(e)}")
            return False
    
    def test_role_based_access(self):
        """Test that role-based access control is working"""
        self.print_step("Testing Role-Based Access Control")
        
        try:
            # Test that public user cannot access admin endpoints
            if 'public' in self.tokens:
                headers_public = {"Authorization": f"Bearer {self.tokens['public']}"}
                response = requests.get(f"{self.base_url}/api/admin/dashboard", 
                                      headers=headers_public)
                
                if response.status_code == 403:
                    self.print_success("Public user correctly blocked from admin dashboard")
                else:
                    self.print_warning(f"Public user access control unexpected: {response.status_code}")
            
            # Test that volunteer cannot access police endpoints
            if 'volunteer' in self.tokens:
                headers_volunteer = {"Authorization": f"Bearer {self.tokens['volunteer']}"}
                response = requests.get(f"{self.base_url}/api/police/dashboard", 
                                      headers=headers_volunteer)
                
                if response.status_code == 403:
                    self.print_success("Volunteer correctly blocked from police dashboard")
                else:
                    self.print_warning(f"Volunteer access control unexpected: {response.status_code}")
            
            # Test that police can access their own endpoints
            if 'police' in self.tokens:
                headers_police = {"Authorization": f"Bearer {self.tokens['police']}"}
                response = requests.get(f"{self.base_url}/api/police/dashboard", 
                                      headers=headers_police)
                
                if response.status_code == 200:
                    self.print_success("Police can access their dashboard")
                else:
                    self.print_error(f"Police access failed: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Role-based access test failed: {str(e)}")
            return False
    
    def run_complete_test(self):
        """Run all tests"""
        print("🚀 Starting Complete iReport Backend Feature Test")
        print(f"📧 Test Email: {TEST_EMAIL}")
        print(f"🔗 Base URL: {BASE_URL}")
        print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        tests = [
            ("Health Endpoints", self.test_health_endpoints),
            ("Authentication Flow", self.test_auth_flow),
            ("Complaint Management", self.test_complaint_management),
            ("Admin Features", self.test_admin_features),
            ("Police Features", self.test_police_features),
            ("Advanced Features", self.test_advanced_features),
            ("Role-Based Access", self.test_role_based_access)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                success = test_func()
                results.append((test_name, success))
                time.sleep(1)  # Small delay between tests
            except Exception as e:
                self.print_error(f"Test {test_name} crashed: {str(e)}")
                results.append((test_name, False))
        
        # Print summary
        self.print_step("TEST SUMMARY")
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        print(f"\n📊 Results: {passed}/{total} tests passed")
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} - {test_name}")
        
        if passed == total:
            print(f"\n🎉 ALL TESTS PASSED! Your iReport backend is fully functional!")
        else:
            print(f"\n⚠️  {total - passed} tests failed. Please check the errors above.")
        
        print(f"\n⏰ End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    tester = iReportTester()
    tester.run_complete_test()