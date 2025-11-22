from app import create_app
from database.connection import db
from database.models import User, PoliceOfficer, Volunteer
from auth.auth_handler import Auth
from datetime import datetime

def seed_initial_data():
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting data seeding...")
        
        # Create admin user
        if not User.query.filter_by(email='admin@ireport.com').first():
            admin_user = User(
                email='admin@ireport.com',
                password_hash=Auth.hash_password('admin123'),
                full_name='System Administrator',
                phone='+911234567890',
                role='admin',
                is_verified=True,
                verified_at=datetime.utcnow()
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Admin user created")

        # Simple test users
        test_users = [
            {
                'email': 'police.delhi.1@ireport.com',
                'name': 'Rajesh Sharma',
                'phone': '+919876543210',
                'role': 'police',
                'password': 'police123',
                'state': 'Delhi',
                'district': 'Central Delhi'
            },
            {
                'email': 'volunteer.delhi.1@ireport.com',
                'name': 'Anjali Patel',
                'phone': '+919876543211',
                'role': 'volunteer',
                'password': 'volunteer123',
                'state': 'Delhi',
                'district': 'Central Delhi'
            },
            {
                'email': 'user@ireport.com',
                'name': 'Rahul Kumar',
                'phone': '+919876543212',
                'role': 'public',
                'password': 'user123',
                'state': 'Delhi',
                'district': 'Central Delhi'
            }
        ]

        for user_data in test_users:
            if not User.query.filter_by(email=user_data['email']).first():
                user = User(
                    email=user_data['email'],
                    password_hash=Auth.hash_password(user_data['password']),
                    full_name=user_data['name'],
                    phone=user_data['phone'],
                    role=user_data['role'],
                    is_verified=True,
                    verified_at=datetime.utcnow(),
                    state=user_data['state'],
                    district=user_data['district']
                )
                db.session.add(user)
                db.session.commit()
                print(f"✅ {user_data['role'].title()} user created: {user_data['name']}")

        print("\n🎉 Data seeding completed successfully!")
        print("\n📋 LOGIN CREDENTIALS:")
        print("👑 Admin: admin@ireport.com / admin123")
        print("👮 Police: police.delhi.1@ireport.com / police123")
        print("🤝 Volunteer: volunteer.delhi.1@ireport.com / volunteer123")
        print("👤 Public: user@ireport.com / user123")

if __name__ == '__main__':
    seed_initial_data()