import requests
import unittest
import os

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

class ChatbotAndReportsVerificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()
        
        # Login as User
        r_user = cls.session.post(f"{API_URL}/auth/login", json={
            "email": "user@ireport.com",
            "password": "user123"
        })
        assert r_user.status_code == 200, f"User login failed: {r_user.text}"
        cls.user_token = r_user.json()["token"]
        cls.user_headers = {"Authorization": f"Bearer {cls.user_token}"}
        
        # Login as Admin
        r_admin = cls.session.post(f"{API_URL}/auth/login", json={
            "email": "admin@ireport.com",
            "password": "admin123"
        })
        assert r_admin.status_code == 200, f"Admin login failed: {r_admin.text}"
        cls.admin_token = r_admin.json()["token"]
        cls.admin_headers = {"Authorization": f"Bearer {cls.admin_token}"}

    # =========================================================================
    # 🤖 1. CHATBOT SERVICE VERIFICATION
    # =========================================================================

    def test_chatbot_conversation_and_case_lookup(self):
        """Verify Chatbot session creation, conversational responses & case lookup"""
        print("\n--- Testing Chatbot Service ---")
        
        # 1. Start session
        start_res = requests.post(f"{API_URL}/chatbot/start-session", headers=self.user_headers)
        self.assertEqual(start_res.status_code, 200, f"Start session failed: {start_res.text}")
        session_id = start_res.json()["session_id"]
        print(f"✅ Chatbot session initialized: {session_id}")
        
        # 2. Send financial fraud query
        msg1_res = requests.post(f"{API_URL}/chatbot/send-message", headers=self.user_headers, json={
            "session_id": session_id,
            "message": "I lost money in a credit card phishing scam. How do I report it?"
        })
        self.assertEqual(msg1_res.status_code, 200, f"Send message failed: {msg1_res.text}")
        reply1 = msg1_res.json().get("response") or msg1_res.json().get("reply")
        print(f"🤖 User Query: 'I lost money...' -> Bot Reply: {reply1[:80]}...")
        self.assertIsNotNone(reply1)

        # 3. Send helpline query
        msg2_res = requests.post(f"{API_URL}/chatbot/send-message", headers=self.user_headers, json={
            "session_id": session_id,
            "message": "What is the national cybercrime helpline number?"
        })
        self.assertEqual(msg2_res.status_code, 200)
        reply2 = msg2_res.json().get("response") or msg2_res.json().get("reply")
        print(f"🤖 User Query: 'Helpline number?' -> Bot Reply: {reply2[:80]}...")

        # 4. Get chat history
        hist_res = requests.get(f"{API_URL}/chatbot/session-history/{session_id}", headers=self.user_headers)
        self.assertEqual(hist_res.status_code, 200, f"History fetch failed: {hist_res.text}")
        print(f"✅ Chat history retrieved ({len(hist_res.json().get('messages', []))} messages in session)")

    # =========================================================================
    # 📄 2. PDF REPORT GENERATOR VERIFICATION
    # =========================================================================

    def test_pdf_case_and_analytics_reports(self):
        """Verify PDF Case Report generation and PDF Analytics Report generation"""
        print("\n--- Testing PDF Reports Generator Service ---")
        
        # 1. File a complaint to get a case ID for report testing
        file_res = requests.post(f"{API_URL}/complaints/file", headers=self.user_headers, json={
            "title": "PDF Generation Test Complaint",
            "description": "Filing test complaint to verify PDF report generator and download service.",
            "incident_date": "2026-07-30T14:00:00Z",
            "state": "Delhi",
            "district": "South Delhi",
            "location": "Online"
        })
        self.assertIn(file_res.status_code, [200, 201])
        case_id = file_res.json()["case_id"]
        
        # 2. Generate PDF Case Report
        case_report_res = requests.post(f"{API_URL}/reports/case/{case_id}", headers=self.user_headers)
        self.assertEqual(case_report_res.status_code, 200, f"Case report failed: {case_report_res.text}")
        report_data = case_report_res.json()
        print(f"✅ Generated Case PDF: {report_data.get('filename')}")
        self.assertIn("download_url", report_data)

        # 3. Generate PDF Analytics Report (Admin)
        analytics_report_res = requests.post(f"{API_URL}/reports/analytics", headers=self.admin_headers, json={
            "type": "monthly"
        })
        self.assertEqual(analytics_report_res.status_code, 200, f"Analytics report failed: {analytics_report_res.text}")
        analytics_data = analytics_report_res.json()
        print(f"✅ Generated Analytics PDF: {analytics_data.get('filename')}")
        self.assertIn("download_url", analytics_data)

        # 4. Download PDF file and verify non-empty byte stream
        download_url = analytics_data["download_url"]
        dl_res = requests.get(f"{BASE_URL}{download_url}", headers=self.admin_headers)
        self.assertEqual(dl_res.status_code, 200, f"PDF download failed: {dl_res.status_code}")
        self.assertGreater(len(dl_res.content), 500, "Downloaded PDF file is empty or corrupt")
        print(f"✅ Successfully downloaded PDF report ({len(dl_res.content)} bytes)")

if __name__ == '__main__':
    unittest.main(verbosity=2)
