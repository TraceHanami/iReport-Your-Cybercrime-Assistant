# fix_delhi_police.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database.models import User, PoliceOfficer
from database.connection import db
from datetime import datetime

def fix_missing_officers():
    with app.app_context():
        print("🔧 Fixing Missing Delhi Police Officer Profiles...")
        
        # Fix police_delhi_1@ireport.com (ID: 2)
        user1 = User.query.get(2)
        if user1 and not PoliceOfficer.query.filter_by(user_id=2).first():
            officer1 = PoliceOfficer(
                user_id=2,
                badge_number="PD_DEL_001",
                rank="Senior Officer",
                station="Delhi Central Station",
                district="Central Delhi", 
                state="Delhi",
                is_active=True,
                performance_score=85.0,
                current_case_load=0,
                created_at=datetime.utcnow()
            )
            db.session.add(officer1)
            print(f"✅ Created officer profile for {user1.email}")
        
        # Fix police_delhi_2@ireport.com (ID: 3)  
        user2 = User.query.get(3)
        if user2 and not PoliceOfficer.query.filter_by(user_id=3).first():
            officer2 = PoliceOfficer(
                user_id=3,
                badge_number="PD_DEL_002",
                rank="Officer",
                station="Delhi South Station",
                district="South Delhi",
                state="Delhi",
                is_active=True,
                performance_score=78.0,
                current_case_load=0,
                created_at=datetime.utcnow()
            )
            db.session.add(officer2)
            print(f"✅ Created officer profile for {user2.email}")
        
        db.session.commit()
        print("🎯 Delhi police officer profiles created successfully!")

if __name__ == "__main__":
    fix_missing_officers()