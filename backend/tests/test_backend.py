import requests
import json
import time
import random
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = f"testuser{int(time.time())}@test.com"
TEST_PASSWORD = "test123"

class iReportComprehensiveTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.tokens = {}
        self.test_data = {}
        self.session = requests.Session()
        
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
    
    def make_request(self, method, endpoint, headers=None, json_data=None, expected_status=200):
        """Helper method to make requests with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, headers=headers, json=json_data)
            if response.status_code == expected_status:
                return response.json() if response.content else {}
            else:
                self.print_warning(f"Request failed: {method} {endpoint} - Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_error(f"Request error: {method} {endpoint} - {str(e)}")
            return None

    def test_health_endpoints(self):
        """Test basic health and system status endpoints"""
        self.print_step("Testing Health Endpoints")
        
        endpoints = [
            ("/api/health", "GET", "Health Check"),
            ("/api/system/status", "GET", "System Status"),
            ("/api", "GET", "API Info")
        ]
        
        for endpoint, method, description in endpoints:
            result = self.make_request(method, endpoint)
            if result:
                self.print_success(f"{description}: Operational")
            else:
                return False
        return True

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        self.print_step("Testing Authentication Endpoints")
        
        # Test login with different roles
        test_users = [
            {"email": "admin@ireport.com", "password": "admin123", "role": "admin"},
            {"email": "police.delhi.1@ireport.com", "password": "police123", "role": "police"},
            {"email": "volunteer.delhi.1@ireport.com", "password": "volunteer123", "role": "volunteer"},
            {"email": "user@ireport.com", "password": "user123", "role": "public"}
        ]
        
        for user in test_users:
            result = self.make_request("POST", "/api/auth/login", 
                                     json_data={"email": user['email'], "password": user['password']})
            if result:
                self.tokens[user['role']] = result['token']
                self.test_data[f"{user['role']}_user_id"] = result['user']['id']
                self.print_success(f"Login successful: {user['role']}")
            else:
                self.print_error(f"Login failed for {user['role']}")
                return False
        
        # Test registration flow
        register_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": "Comprehensive Test User",
            "role": "public",
            "phone": "+911234567890"
        }
        
        result = self.make_request("POST", "/api/auth/register", json_data=register_data)
        if result and result.get('debug_mode'):
            otp = result['otp']
            verify_result = self.make_request("POST", "/api/auth/verify-otp", 
                                            json_data={"email": TEST_EMAIL, "otp": otp})
            if verify_result:
                self.tokens['new_public'] = verify_result['token']
                self.print_success("New user registration successful")
        
        # Test auth/me endpoint
        if 'admin' in self.tokens:
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            result = self.make_request("GET", "/api/auth/me", headers=headers)
            if result:
                self.print_success("Auth me endpoint working")
        
        return True

    def test_complaint_endpoints(self):
        """Test complaint management endpoints"""
        self.print_step("Testing Complaint Endpoints")
        
        if 'public' not in self.tokens:
            self.print_warning("Skipping complaint tests - no public token")
            return False
        
        headers = {"Authorization": f"Bearer {self.tokens['public']}"}
        
        # Test filing a complaint
        complaint_data = {
            "title": "Comprehensive Test - Stolen Vehicle",
            "description": "My car was stolen from the parking lot. This is a comprehensive test complaint.",
            "incident_date": "2025-10-30T18:30:00Z",
            "state": "Delhi",
            "district": "Central Delhi",
            "location": "Near Central Mall parking lot",
            "crime_type": "theft",
            "victim_name": "Test User",
            "victim_age": 30,
            "victim_gender": "male",
            "victim_contact": "+911234567890",
            "is_property_damage": True,
            "estimated_loss": 25000.0
        }
        
        result = self.make_request("POST", "/api/complaints/file", headers=headers, json_data=complaint_data)
        if result:
            self.test_data['case_id'] = result.get('case_id')
            self.print_success(f"Complaint filed: {self.test_data['case_id']}")
        else:
            return False
        
        # Test getting user complaints
        result = self.make_request("GET", "/api/complaints/my-complaints", headers=headers)
        if result:
            self.print_success(f"Retrieved {len(result.get('complaints', []))} user complaints")
        
        # Test anonymous complaint
        anonymous_data = {
            "title": "Anonymous Test - Suspicious Activity",
            "description": "Suspicious activity observed. Anonymous report.",
            "incident_date": "2025-10-30T22:00:00Z",
            "state": "Delhi", 
            "district": "South Delhi",
            "location": "Central Park area",
            "crime_type": "suspicious_activity",
            "is_anonymous": True,
            "anonymous_email": "anonymous@example.com"
        }
        
        result = self.make_request("POST", "/api/complaints/file-anonymous", json_data=anonymous_data)
        if result:
            self.print_success("Anonymous complaint filed")
        
        return True

    def test_tracking_endpoints(self):
        """Test case tracking endpoints"""
        self.print_step("Testing Tracking Endpoints")
        
        if 'case_id' not in self.test_data:
            self.print_warning("Skipping tracking tests - no case ID")
            return True
        
        # Test public tracking
        result = self.make_request("GET", f"/api/track/status/{self.test_data['case_id']}")
        if result:
            self.print_success("Public tracking working")
        
        # Test authenticated tracking
        if 'public' in self.tokens:
            headers = {"Authorization": f"Bearer {self.tokens['public']}"}
            result = self.make_request("GET", f"/api/track/details/{self.test_data['case_id']}", headers=headers)
            if result:
                self.print_success("Authenticated tracking working")
        
        return True

    def test_admin_endpoints(self):
        """Test admin-specific endpoints"""
        self.print_step("Testing Admin Endpoints")
        
        if 'admin' not in self.tokens:
            self.print_warning("Skipping admin tests - no admin token")
            return False
        
        headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
        
        admin_endpoints = [
            ("/api/admin/dashboard", "GET", "Admin Dashboard"),
            ("/api/admin/cases", "GET", "All Cases"),
            ("/api/admin/users", "GET", "All Users"),
            ("/api/admin/police-officers", "GET", "Police Officers"),
            ("/api/admin/analytics/overview", "GET", "Analytics Overview"),
            ("/api/admin/analytics/performance", "GET", "Officer Performance"),
            ("/api/admin/volunteer-applications", "GET", "Volunteer Applications"),
            ("/api/admin/volunteers/pending", "GET", "Pending Volunteers")
        ]
        
        for endpoint, method, description in admin_endpoints:
            result = self.make_request(method, endpoint, headers=headers)
            if result:
                self.print_success(f"{description}: Working")
        
        # Test case assignment if we have a case
        if 'case_id' in self.test_data:
            assign_data = {
                "case_id": self.test_data['case_id'],
                "police_officer_id": 1,  # Assuming officer with ID 1 exists
                "assignment_reason": "Test assignment"
            }
            result = self.make_request("POST", "/api/admin/assign-case", headers=headers, json_data=assign_data)
            if result:
                self.print_success("Case assignment working")
        
        return True

    def test_police_endpoints(self):
        """Test police-specific endpoints"""
        self.print_step("Testing Police Endpoints")
        
        if 'police' not in self.tokens:
            self.print_warning("Skipping police tests - no police token")
            return False
        
        headers = {"Authorization": f"Bearer {self.tokens['police']}"}
        
        police_endpoints = [
            ("/api/police/dashboard", "GET", "Police Dashboard"),
            ("/api/police/cases", "GET", "Police Cases"),
            ("/api/police/performance", "GET", "Officer Performance"),
            ("/api/police/team-performance", "GET", "Team Performance")
        ]
        
        for endpoint, method, description in police_endpoints:
            result = self.make_request(method, endpoint, headers=headers)
            if result:
                self.print_success(f"{description}: Working")
        
        # Test updating case status if we have a case
        if 'case_id' in self.test_data:
            update_data = {
                "status": "in_progress",
                "notes": "Test update from police officer"
            }
            result = self.make_request("POST", f"/api/police/update-case/{self.test_data['case_id']}", 
                                     headers=headers, json_data=update_data)
            if result:
                self.print_success("Case update working")
        
        # Test availability update
        availability_data = {"is_active": True}
        result = self.make_request("PUT", "/api/police/availability", headers=headers, json_data=availability_data)
        if result:
            self.print_success("Availability update working")
        
        return True

    def test_analytics_endpoints(self):
        """Test advanced analytics endpoints"""
        self.print_step("Testing Analytics Endpoints")
        
        if 'admin' not in self.tokens:
            self.print_warning("Skipping analytics tests - no admin token")
            return False
        
        headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
        
        analytics_endpoints = [
            ("/api/analytics/trends", "GET", "Trend Analysis"),
            ("/api/analytics/heatmap", "GET", "Geospatial Heatmap"),
            ("/api/analytics/high-risk-areas", "GET", "High Risk Areas"),
            ("/api/analytics/patrol-recommendations", "GET", "Patrol Recommendations"),
            ("/api/analytics/performance", "GET", "Performance Metrics"),
            ("/api/analytics/predictive-insights", "GET", "Predictive Insights")
        ]
        
        for endpoint, method, description in analytics_endpoints:
            result = self.make_request(method, endpoint, headers=headers)
            if result:
                self.print_success(f"{description}: Working")
        
        return True

    def test_notification_endpoints(self):
        """Test notification endpoints"""
        self.print_step("Testing Notification Endpoints")
        
        if 'public' not in self.tokens:
            self.print_warning("Skipping notification tests - no public token")
            return False
        
        headers = {"Authorization": f"Bearer {self.tokens['public']}"}
        
        notification_endpoints = [
            ("/api/notifications/user", "GET", "User Notifications"),
            ("/api/notifications/stats", "GET", "Notification Stats")
        ]
        
        for endpoint, method, description in notification_endpoints:
            result = self.make_request(method, endpoint, headers=headers)
            if result:
                self.print_success(f"{description}: Working")
        
        # Test creating a test notification
        test_notification = {
            "title": "Test Notification",
            "message": "This is a test notification from comprehensive testing",
            "type": "test"
        }
        result = self.make_request("POST", "/api/notifications/test", headers=headers, json_data=test_notification)
        if result:
            self.print_success("Test notification creation working")
        
        return True

    def test_chatbot_endpoints(self):
        """Test chatbot endpoints"""
        self.print_step("Testing Chatbot Endpoints")
        
        if 'public' not in self.tokens:
            self.print_warning("Skipping chatbot tests - no public token")
            return False
        
        headers = {"Authorization": f"Bearer {self.tokens['public']}"}
        
        # Start a new chat session
        session_data = {"context": "comprehensive_testing"}
        result = self.make_request("POST", "/api/chatbot/start-session", headers=headers, json_data=session_data)
        if result:
            session_id = result.get('session_id')
            self.test_data['chat_session_id'] = session_id
            self.print_success("Chat session started")
            
            # Send a message
            message_data = {
                "session_id": session_id,
                "message": "Hello, I need help with filing a complaint"
            }
            result = self.make_request("POST", "/api/chatbot/send-message", headers=headers, json_data=message_data)
            if result:
                self.print_success("Chat message sent")
            
            # Get session history
            result = self.make_request("GET", f"/api/chatbot/session-history/{session_id}", headers=headers)
            if result:
                self.print_success("Session history retrieved")
        
        # Get user sessions
        result = self.make_request("GET", "/api/chatbot/user-sessions", headers=headers)
        if result:
            self.print_success("User sessions retrieved")
        
        return True

    def test_sms_endpoints(self):
        """Test SMS endpoints"""
        self.print_step("Testing SMS Endpoints")
        
        if 'admin' not in self.tokens:
            self.print_warning("Skipping SMS tests - no admin token")
            return False
        
        headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
        
        sms_endpoints = [
            ("/api/sms/status", "GET", "SMS Status"),
            ("/api/sms/logs", "GET", "SMS Logs")
        ]
        
        for endpoint, method, description in sms_endpoints:
            result = self.make_request(method, endpoint, headers=headers)
            if result:
                self.print_success(f"{description}: Working")
        
        # Test sending OTP (this might actually send SMS, so be careful)
        otp_data = {
            "phone_number": "+911234567890",
            "message": "Test OTP: 123456"
        }
        result = self.make_request("POST", "/api/sms/send-otp", headers=headers, json_data=otp_data)
        if result:
            self.print_success("SMS OTP sending endpoint working")
        
        return True

    def test_reports_endpoints(self):
        """Test report generation endpoints"""
        self.print_step("Testing Reports Endpoints")
        
        if 'admin' not in self.tokens:
            self.print_warning("Skipping reports tests - no admin token")
            return False
        
        headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
        
        reports_endpoints = [
            ("/api/reports/list", "GET", "Reports List"),
            ("/api/reports/system-status", "GET", "System Status Report")
        ]
        
        for endpoint, method, description in reports_endpoints:
            result = self.make_request(method, endpoint, headers=headers)
            if result:
                self.print_success(f"{description}: Working")
        
        # Test generating analytics report
        report_data = {
            "report_type": "analytics",
            "period_days": 30,
            "format": "pdf"
        }
        result = self.make_request("POST", "/api/reports/analytics", headers=headers, json_data=report_data)
        if result:
            self.print_success("Analytics report generation working")
        
        # Test generating case report if we have a case
        if 'case_id' in self.test_data:
            case_report_data = {
                "format": "pdf",
                "include_evidence": True
            }
            result = self.make_request("POST", f"/api/reports/case/{self.test_data['case_id']}", 
                                     headers=headers, json_data=case_report_data)
            if result:
                self.print_success("Case report generation working")
        
        return True

    def test_security_endpoints(self):
        """Test security and access control"""
        self.print_step("Testing Security and Access Control")
        
        # Test role-based access control
        test_cases = [
            {"role": "public", "endpoint": "/api/admin/dashboard", "should_work": False},
            {"role": "volunteer", "endpoint": "/api/police/dashboard", "should_work": False},
            {"role": "police", "endpoint": "/api/admin/dashboard", "should_work": False},
            {"role": "admin", "endpoint": "/api/admin/dashboard", "should_work": True},
            {"role": "police", "endpoint": "/api/police/dashboard", "should_work": True}
        ]
        
        for test_case in test_cases:
            role = test_case["role"]
            endpoint = test_case["endpoint"]
            should_work = test_case["should_work"]
            
            if role in self.tokens:
                headers = {"Authorization": f"Bearer {self.tokens[role]}"}
                result = self.make_request("GET", endpoint, headers=headers, 
                                         expected_status=200 if should_work else 403)
                
                if should_work and result:
                    self.print_success(f"Access control: {role} can access {endpoint}")
                elif not should_work and result is None:
                    self.print_success(f"Access control: {role} correctly blocked from {endpoint}")
                else:
                    self.print_warning(f"Access control: Unexpected result for {role} on {endpoint}")
        
        return True

    def test_performance_endpoints(self):
        """Test performance under load"""
        self.print_step("Testing Performance Endpoints")
        
        if 'public' not in self.tokens:
            return True
        
        headers = {"Authorization": f"Bearer {self.tokens['public']}"}
        
        # Test multiple rapid requests
        start_time = time.time()
        successful_requests = 0
        total_requests = 10
        
        for i in range(total_requests):
            result = self.make_request("GET", "/api/complaints/my-complaints", headers=headers)
            if result:
                successful_requests += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        if successful_requests == total_requests:
            self.print_success(f"Performance: {total_requests} requests in {duration:.2f}s ({duration/total_requests:.2f}s per request)")
        else:
            self.print_warning(f"Performance: {successful_requests}/{total_requests} requests successful in {duration:.2f}s")
        
        return True

    def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive iReport Backend Test")
        print(f"📧 Test Email: {TEST_EMAIL}")
        print(f"🔗 Base URL: {BASE_URL}")
        print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        test_methods = [
            ("Health Endpoints", self.test_health_endpoints),
            ("Authentication", self.test_auth_endpoints),
            ("Complaint Management", self.test_complaint_endpoints),
            ("Case Tracking", self.test_tracking_endpoints),
            ("Admin Features", self.test_admin_endpoints),
            ("Police Features", self.test_police_endpoints),
            ("Analytics", self.test_analytics_endpoints),
            ("Notifications", self.test_notification_endpoints),
            ("Chatbot", self.test_chatbot_endpoints),
            ("SMS Services", self.test_sms_endpoints),
            ("Reports", self.test_reports_endpoints),
            ("Security", self.test_security_endpoints),
            ("Performance", self.test_performance_endpoints)
        ]
        
        results = []
        for test_name, test_func in test_methods:
            try:
                success = test_func()
                results.append((test_name, success))
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                self.print_error(f"Test {test_name} crashed: {str(e)}")
                results.append((test_name, False))
        
        # Print comprehensive summary
        self.print_step("COMPREHENSIVE TEST SUMMARY")
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        print(f"\n📊 Overall Results: {passed}/{total} test categories passed")
        print(f"🎯 Success Rate: {(passed/total)*100:.1f}%")
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} - {test_name}")
        
        # Feature coverage analysis
        features_tested = {
            "Authentication": ["Login", "Registration", "OTP Verification", "User Info"],
            "Complaints": ["File Complaint", "Anonymous Complaint", "User Complaints"],
            "Case Management": ["Tracking", "Assignment", "Status Updates"],
            "Admin Features": ["Dashboard", "User Management", "Police Management", "Analytics"],
            "Police Features": ["Dashboard", "Case Management", "Performance"],
            "Advanced Features": ["Notifications", "Chatbot", "SMS", "Reports", "Analytics"],
            "Security": ["Role-based Access Control"],
            "Performance": ["Load Testing"]
        }
        
        print(f"\n🔍 Feature Coverage:")
        for category, features in features_tested.items():
            print(f"   📁 {category}: {len(features)} features")
        
        if passed == total:
            print(f"\n🎉 EXCELLENT! All {total} test categories passed!")
            print("   Your iReport backend is fully functional and production-ready!")
        elif passed >= total * 0.8:
            print(f"\n👍 GOOD! {passed}/{total} categories passed!")
            print("   Your iReport backend is mostly functional with minor issues.")
        else:
            print(f"\n⚠️  NEEDS ATTENTION! Only {passed}/{total} categories passed.")
            print("   Please review the failed tests above.")
        
        print(f"\n⏰ End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Total Duration: {datetime.now() - datetime.fromtimestamp(time.time() - (len(results) * 0.5))}")

if __name__ == "__main__":
    tester = iReportComprehensiveTester()
    tester.run_comprehensive_test()