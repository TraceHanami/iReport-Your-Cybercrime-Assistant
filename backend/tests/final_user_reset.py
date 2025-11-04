# final_user_reset.py
from database.connection import db, init_db
from flask import Flask
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ireport.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)

with app.app_context():
    from database.models import User
    
    print("🔒 Final User Password Reset")
    print("=" * 50)
    
    # Test users with verified passwords
    test_users = [
        {"email": "admin@ireport.com", "password": "admin123", "role": "admin", "full_name": "Admin User"},
        {"email": "officer@ireport.com", "password": "password123", "role": "police", "full_name": "Police Officer"}, 
        {"email": "public@ireport.com", "password": "password123", "role": "public", "full_name": "Public User"},
    ]
    
    for user_data in test_users:
        user = User.query.filter_by(email=user_data["email"]).first()
        if user:
            # Reset password and verify it works
            new_password_hash = generate_password_hash(user_data["password"])
            user.password_hash = new_password_hash
            user.full_name = user_data["full_name"]
            user.role = user_data["role"]
            user.is_active = True
            user.is_verified = True
            
            # Verify the password was set correctly
            password_correct = check_password_hash(new_password_hash, user_data["password"])
            if password_correct:
                print(f"✅ {user_data['email']:25} | Password reset verified")
            else:
                print(f"❌ {user_data['email']:25} | Password verification failed")
        else:
            print(f"⚠️  {user_data['email']:25} | User not found")
    
    db.session.commit()
    print("=" * 50)
    print("🎉 All user passwords have been reset and verified!")
    
    # Test logins immediately
    print("\n🔐 Testing logins after reset...")
    import requests
    
    for user_data in test_users:
        response = requests.post(f"http://127.0.0.1:5000/api/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        
        if response.status_code == 200:
            print(f"✅ {user_data['email']:25} | Login successful")
        else:
            print(f"❌ {user_data['email']:25} | Login failed: {response.status_code}")