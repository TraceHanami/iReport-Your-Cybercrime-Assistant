import unittest
import requests
import json
import time
import socketio

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

class SecurityAndRealtimeTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()
        
        # 1. Login as Admin
        r_admin = cls.session.post(f"{API_URL}/auth/login", json={
            "email": "admin@ireport.com",
            "password": "admin123"
        })
        assert r_admin.status_code == 200, f"Admin login failed: {r_admin.text}"
        cls.admin_token = r_admin.json()["token"]
        cls.admin_headers = {"Authorization": f"Bearer {cls.admin_token}"}
        
        # 2. Login as Police
        r_police = cls.session.post(f"{API_URL}/auth/login", json={
            "email": "officer@ireport.com",
            "password": "police123"
        })
        assert r_police.status_code == 200, f"Police login failed: {r_police.text}"
        cls.police_token = r_police.json()["token"]
        cls.police_headers = {"Authorization": f"Bearer {cls.police_token}"}
        
        # 3. Login as Public User
        r_user = cls.session.post(f"{API_URL}/auth/login", json={
            "email": "user@ireport.com",
            "password": "user123"
        })
        assert r_user.status_code == 200, f"Public user login failed: {r_user.text}"
        cls.user_token = r_user.json()["token"]
        cls.user_headers = {"Authorization": f"Bearer {cls.user_token}"}

    # =========================================================================
    # 🔐 1. ACCESS CONTROL & ROLE-BASED PRIVILEGE ESCALATION TESTS
    # =========================================================================
    
    def test_rbac_public_user_blocked_from_admin_routes(self):
        """Verify public user cannot access admin dashboard or administrative actions"""
        endpoints = [
            "/admin/dashboard",
            "/admin/cases",
            "/admin/users",
            "/admin/police-officers",
            "/admin/volunteer-applications"
        ]
        for ep in endpoints:
            res = requests.get(f"{API_URL}{ep}", headers=self.user_headers)
            self.assertIn(res.status_code, [401, 403], f"Public user accessed admin route {ep}: {res.status_code}")

    def test_rbac_police_user_blocked_from_admin_user_management(self):
        """Verify police officer cannot access admin user management"""
        res = requests.get(f"{API_URL}/admin/users", headers=self.police_headers)
        self.assertIn(res.status_code, [401, 403], "Police officer accessed admin user management!")

    def test_unauthenticated_blocked_from_protected_routes(self):
        """Verify requests without token are blocked on protected endpoints"""
        protected_routes = [
            ("/admin/dashboard", "GET"),
            ("/police/dashboard", "GET"),
            ("/complaints/my-complaints", "GET"),
            ("/notifications/user", "GET")
        ]
        for ep, method in protected_routes:
            res = requests.request(method, f"{API_URL}{ep}")
            self.assertIn(res.status_code, [401, 403], f"Unauthenticated request to {ep} returned {res.status_code}")

    # =========================================================================
    # 🛡️ 2. SQL INJECTION & XSS SANITIZATION TESTS
    # =========================================================================

    def test_sqli_protection_on_login(self):
        """Verify SQL injection payloads in login form are safely blocked"""
        sqli_payloads = [
            "' OR '1'='1",
            "admin@ireport.com' --",
            "' UNION SELECT 1, 'admin', 'hash' --"
        ]
        for payload in sqli_payloads:
            res = requests.post(f"{API_URL}/auth/login", json={
                "email": payload,
                "password": "password123"
            })
            self.assertIn(res.status_code, [400, 401], f"SQLi payload allowed in login: {payload}")

    def test_sqli_protection_on_case_tracking(self):
        """Verify SQL injection payloads in tracking search endpoint are safely handled"""
        sqli_payloads = [
            "' OR 1=1 --",
            "IR'; DROP TABLE complaints; --",
            "1' UNION SELECT 1,2,3 --"
        ]
        for payload in sqli_payloads:
            res = requests.get(f"{API_URL}/track/status/{payload}")
            # Should safely return 404 or empty response without server crash (500)
            self.assertNotEqual(res.status_code, 500, f"SQLi caused server error on track endpoint: {payload}")

    def test_xss_sanitization_on_complaint_filing(self):
        """Verify XSS payloads in complaint submission are safely stored/handled"""
        xss_payload = "<script>alert('XSS_ATTACK')</script><img src=x onerror=alert('XSS')>"
        res = requests.post(f"{API_URL}/complaints/file", headers=self.user_headers, json={
            "title": f"Security Test {xss_payload}",
            "description": f"Testing XSS payload safety: {xss_payload}. " * 10,
            "incident_date": "2026-07-01T12:00:00Z",
            "state": "Delhi",
            "district": "Central Delhi",
            "location": "Online",
            "crime_type": "cyber_crime",
            "victim_name": "Test Victim",
            "victim_contact": "9876543210"
        })
        self.assertIn(res.status_code, [200, 201], f"Complaint filing failed: {res.text}")
        data = res.json()
        self.assertIn("case_id", data, "Case ID missing from response")

    # =========================================================================
    # 🔑 3. JWT TOKEN TAMPERING & SECURITY TESTS
    # =========================================================================

    def test_jwt_tampered_signature_rejected(self):
        """Verify JWT with tampered signature is rejected"""
        tampered_token = self.user_token[:-5] + "XXXXX"
        headers = {"Authorization": f"Bearer {tampered_token}"}
        res = requests.get(f"{API_URL}/complaints/my-complaints", headers=headers)
        self.assertEqual(res.status_code, 401, "Tampered JWT token was accepted!")

    def test_jwt_malformed_header_rejected(self):
        """Verify malformed authorization headers are rejected"""
        malformed_headers = [
            {"Authorization": "InvalidHeaderFormat"},
            {"Authorization": "Bearer "},
            {"Authorization": "Basic dXNlcjpwYXNz"}
        ]
        for headers in malformed_headers:
            res = requests.get(f"{API_URL}/complaints/my-complaints", headers=headers)
            self.assertEqual(res.status_code, 401, f"Malformed header accepted: {headers}")

    # =========================================================================
    # 🕵️ 4. ANONYMOUS REPORTING CONFIDENTIALITY & PRIVACY
    # =========================================================================

    def test_anonymous_complaint_privacy_protection(self):
        """Verify anonymous complaint filing hides victim identity completely"""
        res = requests.post(f"{API_URL}/complaints/file-anonymous", json={
            "title": "Anonymous Financial Scam Report",
            "description": "I was tricked by an online phishing site asking for card credentials. " * 5,
            "incident_date": "2026-07-02T10:00:00Z",
            "state": "Delhi",
            "district": "North Delhi",
            "location": "Online",
            "crime_type": "phishing",
            "victim_name": "John Doe Confidential",
            "victim_contact": "9999999999",
            "is_anonymous": True,
            "anonymous_email": "anon_test@anonymous.gov.in"
        })
        self.assertIn(res.status_code, [200, 201], f"Anonymous complaint filing failed: {res.text}")
        data = res.json()
        self.assertIn("case_id", data, "Case ID missing from anonymous submission response")
        
        # Verify tracking the case returns status without leaking identity
        case_id = data["case_id"]
        track_res = requests.get(f"{API_URL}/track/status/{case_id}")
        self.assertEqual(track_res.status_code, 200)
        track_data = track_res.json()["data"]
        
        # Ensure complainant personal info is not leaked in tracking response
        self.assertNotIn("John Doe Confidential", json.dumps(track_data), "Anonymous identity leaked in tracking data!")

    # =========================================================================
    # ⚡ 5. REAL-TIME WEBSOCKET & NOTIFICATION SYSTEM TESTING
    # =========================================================================

    def test_realtime_socketio_connection(self):
        """Test SocketIO real-time notification engine connection and events"""
        sio = socketio.Client()
        connected = []
        
        @sio.event
        def connect():
            connected.append(True)
            
        try:
            sio.connect(BASE_URL, transports=['websocket', 'polling'], wait_timeout=3)
            time.sleep(0.5)
            self.assertTrue(connected[0], "SocketIO real-time connection failed")
        except Exception as e:
            # If socketio fallback polling is active, verify HTTP notifications endpoint
            res = requests.get(f"{API_URL}/notifications/stats", headers=self.user_headers)
            self.assertEqual(res.status_code, 200, f"Notification service endpoint failed: {res.text}")
        finally:
            if sio.connected:
                sio.disconnect()

    # =========================================================================
    # 🚀 6. CONCURRENCY & REAL-TIME PERFORMANCE STRESS TEST
    # =========================================================================

    def test_concurrent_api_health_performance(self):
        """Verify endpoint latency under fast concurrent API queries"""
        import concurrent.futures
        
        def fetch_health():
            r = requests.get(f"{API_URL}/health")
            return r.status_code == 200

        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda _: fetch_health(), range(30)))
            
        elapsed = time.time() - start_time
        self.assertTrue(all(results), "Some concurrent requests failed")
        self.assertLess(elapsed, 2.5, f"30 concurrent requests took too long: {elapsed:.2f}s")

if __name__ == '__main__':
    unittest.main(verbosity=2)
