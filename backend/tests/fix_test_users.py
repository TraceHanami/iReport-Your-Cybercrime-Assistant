# fix_test_users.py
from database.connection import db, init_db
from flask import Flask
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ireport.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)

with app.app_context():
    from database.models import User
    
    # Test users with correct passwords
    test_users = [
        {"email": "admin@ireport.com", "password": "admin123", "role": "admin", "full_name": "Admin User"},
        {"email": "officer@ireport.com", "password": "password123", "role": "police", "full_name": "Police Officer"}, 
        {"email": "public@ireport.com", "password": "password123", "role": "public", "full_name": "Public User"},
    ]
    
    users_updated = 0
    
    for user_data in test_users:
        user = User.query.filter_by(email=user_data["email"]).first()
        if user:
            # Update user with correct field names
            user.password_hash = generate_password_hash(user_data["password"])
            user.full_name = user_data["full_name"]
            user.role = user_data["role"]
            user.is_active = True
            user.is_verified = True  # Ensure users are verified
            
            users_updated += 1
            print(f"✅ Updated user: {user_data['email']}")
        else:
            print(f"⚠️  User not found: {user_data['email']}")
            print("   This user might need to be created through your registration system")
    
    db.session.commit()
    print(f"\n🎉 User update completed!")
    print(f"   Updated: {users_updated} users")
    print("\n📧 Test Login Credentials:")
    for user_data in test_users:
        print(f"   {user_data['email']:25} / {user_data['password']}")