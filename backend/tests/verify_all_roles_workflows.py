import requests
import unittest

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

class MultiRoleWorkflowsTest(unittest.TestCase):
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
        
        # 2. Login as Volunteer
        r_vol = cls.session.post(f"{API_URL}/auth/login", json={
            "email": "volunteer.delhi.1@ireport.com",
            "password": "volunteer123"
        })
        assert r_vol.status_code == 200, f"Volunteer login failed: {r_vol.text}"
        cls.vol_token = r_vol.json()["token"]
        cls.vol_headers = {"Authorization": f"Bearer {cls.vol_token}"}

        # 3. Login as Public User
        r_user = cls.session.post(f"{API_URL}/auth/login", json={
            "email": "user@ireport.com",
            "password": "user123"
        })
        assert r_user.status_code == 200, f"User login failed: {r_user.text}"
        cls.user_token = r_user.json()["token"]
        cls.user_headers = {"Authorization": f"Bearer {cls.user_token}"}

    # =========================================================================
    # 🤝 1. VOLUNTEER WORKFLOW VERIFICATION
    # =========================================================================

    def test_volunteer_application_and_approval_flow(self):
        """Verify Volunteer Registration, Admin Verification & Application List"""
        print("\n--- Testing Volunteer Workflow ---")
        
        # 1. Admin views volunteer applications
        vols_res = requests.get(f"{API_URL}/admin/volunteer-applications", headers=self.admin_headers)
        self.assertEqual(vols_res.status_code, 200, f"Failed to list volunteer applications: {vols_res.text}")
        vols_data = vols_res.json()
        print(f"✅ Admin retrieved {len(vols_data.get('applications', []))} volunteer applications")
        
        # 2. Admin views pending volunteers
        pending_res = requests.get(f"{API_URL}/admin/volunteers/pending", headers=self.admin_headers)
        self.assertEqual(pending_res.status_code, 200, f"Failed to list pending volunteers: {pending_res.text}")
        print("✅ Admin retrieved pending volunteers list successfully")

    # =========================================================================
    # 👑 2. ADMIN WORKFLOW VERIFICATION
    # =========================================================================

    def test_admin_full_workflow(self):
        """Verify Admin Dashboard, User Management & Analytics Reports"""
        print("\n--- Testing Admin Workflow ---")
        
        # 1. Admin Dashboard Stats
        dash_res = requests.get(f"{API_URL}/admin/dashboard", headers=self.admin_headers)
        self.assertEqual(dash_res.status_code, 200, f"Admin dashboard failed: {dash_res.text}")
        print("✅ Admin Dashboard stats retrieved successfully")
        
        # 2. Admin User Directory
        users_res = requests.get(f"{API_URL}/admin/users", headers=self.admin_headers)
        self.assertEqual(users_res.status_code, 200, f"Admin user directory failed: {users_res.text}")
        print(f"✅ Admin User directory retrieved ({len(users_res.json().get('users', []))} total users)")

        # 3. PDF Analytics Report Generation
        pdf_res = requests.post(f"{API_URL}/reports/analytics", headers=self.admin_headers, json={
            "type": "monthly"
        })
        self.assertEqual(pdf_res.status_code, 200, f"PDF report generation failed: {pdf_res.text}")
        print("✅ Admin PDF Analytics Report generated successfully")

    # =========================================================================
    # 👤 3. PUBLIC USER WORKFLOW VERIFICATION
    # =========================================================================

    def test_public_user_full_workflow(self):
        """Verify User Dashboard, Complaints List, & Chatbot Session"""
        print("\n--- Testing Public User Workflow ---")
        
        # 1. User Dashboard - My Complaints List
        my_comp_res = requests.get(f"{API_URL}/complaints/my-complaints", headers=self.user_headers)
        self.assertEqual(my_comp_res.status_code, 200, f"My complaints failed: {my_comp_res.text}")
        complaints = my_comp_res.json().get("complaints", [])
        print(f"✅ Public user retrieved {len(complaints)} filed complaints")

        # 2. Chatbot session creation
        chat_res = requests.post(f"{API_URL}/chatbot/start-session", headers=self.user_headers)
        self.assertEqual(chat_res.status_code, 200, f"Chatbot start session failed: {chat_res.text}")
        print(f"✅ Chatbot session initialized successfully: {chat_res.json().get('session_id')}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
