from flask import Flask
from database.connection import db
from database.models import User, PoliceOfficer, Volunteer, Complaint
from auth.models import Auth
from datetime import datetime, timedelta

# Create Flask app and configure it
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ireport.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

def seed_sample_data():
    with app.app_context():
        print("Seeding sample data...")
        
        # Create admin user
        if not User.query.filter_by(email='admin@ireport.com').first():
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
        if not User.query.filter_by(email='officer@ireport.com').first():
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
        if not User.query.filter_by(email='public@ireport.com').first():
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
        if not Complaint.query.first():
            from database.models import generate_case_id
            
            # Get the public user
            public_user = User.query.filter_by(email='public@ireport.com').first()
            
            complaint = Complaint(
                case_id=generate_case_id(),
                user_id=public_user.id,
                title='Stolen Mobile Phone',
                description='My mobile phone was stolen from my pocket in the market area yesterday evening.',
                incident_date=datetime.utcnow() - timedelta(days=1),
                state='Delhi',
                district='Central Delhi',
                location='Connaught Place Market',
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
        print("✓ Sample data seeded successfully!")

if __name__ == '__main__':
    seed_sample_data()