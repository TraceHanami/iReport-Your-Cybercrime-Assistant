# check_police_data.py
import sys
import os
# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database.models import User, PoliceOfficer

def check_police_credentials():
    with app.app_context():
        print("🔍 Checking Police Credentials and Data...")
        
        # Check police users
        police_users = User.query.filter_by(role='police').all()
        print(f"\n📊 Found {len(police_users)} police users:")
        
        for user in police_users:
            print(f"\n👮 User: {user.email}")
            print(f"   ID: {user.id}")
            print(f"   Name: {user.full_name}")
            print(f"   Active: {user.is_active}")
            print(f"   Verified: {getattr(user, 'is_verified', 'N/A')}")  # Fixed attribute name
            
            # Check police officer profile
            officer = PoliceOfficer.query.filter_by(user_id=user.id).first()
            if officer:
                print(f"   ✅ Police Officer Profile:")
                print(f"      Badge: {officer.badge_number}")
                print(f"      Rank: {officer.rank}")
                print(f"      Station: {officer.station}")
                print(f"      District: {officer.district}")
                print(f"      Active: {officer.is_active}")
                print(f"      Case Load: {officer.current_case_load}")
                print(f"      Performance: {officer.performance_score}")
            else:
                print(f"   ❌ NO Police Officer Profile Found!")
        
        # Check specific test user
        test_user = User.query.filter_by(email="police_delhi_1@ireport.com").first()
        if test_user:
            print(f"\n🎯 Test Police User Details:")
            print(f"   Email: {test_user.email}")
            print(f"   Password Hash: {test_user.password_hash[:20]}...")
            print(f"   Created: {test_user.created_at}")
            
            # Test password
            if test_user.check_password('police123'):
                print(f"   ✅ Password 'police123' is CORRECT")
            else:
                print(f"   ❌ Password 'police123' is INCORRECT")
            
            officer = PoliceOfficer.query.filter_by(user_id=test_user.id).first()
            if officer:
                print(f"   ✅ Officer Profile Exists")
                print(f"      Badge: {officer.badge_number}")
                print(f"      Station: {officer.station}")
            else:
                print(f"   ❌ Missing Officer Profile")
        else:
            print(f"\n❌ Test police user 'police_delhi_1@ireport.com' not found!")

if __name__ == "__main__":
    check_police_credentials()