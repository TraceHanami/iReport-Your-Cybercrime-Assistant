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
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if not existing_user:
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
                existing_user = user
                print(f"✅ {user_data['role'].title()} user created: {user_data['name']}")
            
            # Ensure police officer profile exists
            if user_data['role'] == 'police':
                if not PoliceOfficer.query.filter_by(user_id=existing_user.id).first():
                    officer = PoliceOfficer(
                        user_id=existing_user.id,
                        badge_number=f"DEL{existing_user.id:04d}",
                        rank='Inspector',
                        station='Central Police Station',
                        state=user_data['state'],
                        district=user_data['district'],
                        department='Crime Branch',
                        police_station='Central Police Station',
                        contact_number=user_data['phone'],
                        specialization='Cyber Crime'
                    )
                    db.session.add(officer)
                    db.session.commit()
                    print(f"✅ Police officer profile created for {existing_user.full_name}")

            # Ensure volunteer profile exists
            if user_data['role'] == 'volunteer':
                if not Volunteer.query.filter_by(user_id=existing_user.id).first():
                    volunteer = Volunteer(
                        user_id=existing_user.id,
                        skills='Digital Literacy, Community Outreach',
                        qualifications='Graduate',
                        experience='1 year',
                        availability='Weekends',
                        state=user_data['state'],
                        district=user_data['district'],
                        pincode='110001',
                        address='Delhi',
                        status='approved',
                        approved_by=1
                    )
                    db.session.add(volunteer)
                    db.session.commit()
                    print(f"✅ Volunteer profile created for {existing_user.full_name}")

        print("\n🎉 Data seeding completed successfully!")
        print("\n📋 LOGIN CREDENTIALS:")
        print("👑 Admin: admin@ireport.com / admin123")
        print("👮 Police: police.delhi.1@ireport.com / police123")
        print("🤝 Volunteer: volunteer.delhi.1@ireport.com / volunteer123")
        print("👤 Public: user@ireport.com / user123")

if __name__ == '__main__':
    seed_initial_data()