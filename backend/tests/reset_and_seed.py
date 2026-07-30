from flask import Flask
from database.connection import db
from database.models import User, PoliceOfficer, Volunteer, Complaint
from auth.models import Auth
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ireport.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def reset_and_seed():
    with app.app_context():
        print("Resetting and seeding database...")
        
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        print("✓ Database reset")
        
        # Create admin user
        admin = User(
            email='admin@ireport.com',
            password_hash=Auth.hash_password('admin123'),
            full_name='System Admin',
            role='admin',
            is_verified=True
        )
        db.session.add(admin)
        print("✓ Admin user created")
        
        # Create police officer
        police_user = User(
            email='officer@ireport.com',
            password_hash=Auth.hash_password('police123'),
            full_name='Inspector Raj Sharma',
            role='police',
            is_verified=True
        )
        db.session.add(police_user)
        db.session.commit()
        
        officer = PoliceOfficer(
            user_id=police_user.id,
            badge_number='DEL123456',
            rank='Inspector',
            station='Central Police Station',
            state='Delhi',
            district='Central Delhi'
        )
        db.session.add(officer)
        print("✓ Police officer created")
        
        # Create public user
        public_user = User(
            email='public@ireport.com',
            password_hash=Auth.hash_password('public123'),
            full_name='Amit Kumar',
            role='public',
            is_verified=True
        )
        db.session.add(public_user)
        db.session.commit()
        print("✓ Public user created")
        
        # Create sample complaint
        complaint = Complaint(
            case_id=Complaint.generate_case_id(),
            user_id=public_user.id,
            title='Sample Theft Case',
            description='Mobile phone stolen from restaurant table.',
            incident_date=datetime.utcnow() - timedelta(days=1),
            state='Delhi',
            district='Central Delhi',
            location='Connaught Place',
            victim_name='Amit Kumar',
            victim_age=25,
            victim_gender='Male',
            victim_contact='9876543210',
            is_missing_person=False,
            is_injury_involved=False,
            is_property_damage=True,
            estimated_loss=25000.0,
            crime_type='theft',
            priority='medium',
            status='pending'
        )
        db.session.add(complaint)
        print("✓ Sample complaint created")
        
        db.session.commit()
        print("✓ Database seeded successfully!")
        print("\nTest credentials:")
        print("  Admin: admin@ireport.com / admin123")
        print("  Police: officer@ireport.com / police123") 
        print("  Public: public@ireport.com / public123")

if __name__ == '__main__':
    reset_and_seed()