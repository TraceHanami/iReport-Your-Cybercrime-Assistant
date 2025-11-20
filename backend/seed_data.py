from flask import Flask
from database.connection import db
from database.models import User, PoliceOfficer, Volunteer, Complaint, VolunteerApplication, OTP, generate_case_id
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
                full_name='System Admin',
                role='admin',
                is_verified=True,
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()  # Commit to get ID for admin
            print("✓ Admin user created")
        
        # Create police officer
        if not User.query.filter_by(email='officer@ireport.com').first():
            police_user = User(
                email='officer@ireport.com',
                full_name='Inspector Raj Sharma',
                role='police',
                is_verified=True,
                is_active=True
            )
            police_user.set_password('police123')
            db.session.add(police_user)
            db.session.commit()
            
            officer = PoliceOfficer(
                user_id=police_user.id,
                badge_number='DEL123456',
                rank='Inspector',
                station='Central Police Station',
                state='Delhi',
                district='Central Delhi',
                department='Crime Branch',
                police_station='Central Police Station',
                contact_number='9876543210',
                specialization='Cyber Crime'
            )
            db.session.add(officer)
            db.session.commit()
            print("✓ Police officer created")
        
        # Create volunteer user
        if not User.query.filter_by(email='volunteer@ireport.com').first():
            volunteer_user = User(
                email='volunteer@ireport.com',
                full_name='Priya Singh',
                role='volunteer',
                is_verified=True,
                is_active=True
            )
            volunteer_user.set_password('volunteer123')
            db.session.add(volunteer_user)
            db.session.commit()
            
            # Get admin ID for approval
            admin = User.query.filter_by(email='admin@ireport.com').first()
            
            volunteer = Volunteer(
                user_id=volunteer_user.id,
                skills='First Aid, Counseling, Community Service',
                qualifications='BA in Social Work',
                experience='2 years',
                availability='Weekends',
                state='Delhi',
                district='Central Delhi',
                pincode='110001',
                address='A-123, Connaught Place, Delhi',
                date_of_birth=datetime(1990, 5, 15),
                gender='Female',
                id_proof_type='Aadhar',
                id_proof_number='1234-5678-9012',
                background_check=True,
                status='approved',
                rating=4.5,
                cases_handled=3,
                application_date=datetime.utcnow() - timedelta(days=30),
                approved_by=admin.id,
                approved_date=datetime.utcnow() - timedelta(days=25)
            )
            db.session.add(volunteer)
            db.session.commit()
            print("✓ Volunteer user created")
        
        # Create public user
        if not User.query.filter_by(email='public@ireport.com').first():
            public_user = User(
                email='public@ireport.com',
                full_name='Amit Kumar',
                role='public',
                phone='9876543210',
                is_verified=True,
                is_active=True
            )
            public_user.set_password('public123')
            db.session.add(public_user)
            db.session.commit()
            print("✓ Public user created")
        
        # Create sample complaints
        if not Complaint.query.first():
            # Get the public user
            public_user = User.query.filter_by(email='public@ireport.com').first()
            
            # Complaint 1: Theft
            complaint1 = Complaint(
                case_id=generate_case_id(),
                user_id=public_user.id,
                title='Stolen Mobile Phone',
                description='My mobile phone was stolen from my pocket in the market area yesterday evening. The phone is a Samsung Galaxy S21 worth ₹25,000.',
                incident_date=datetime.utcnow() - timedelta(days=1),
                state='Delhi',
                district='Central Delhi',
                location='Connaught Place Market',
                latitude=28.6333,
                longitude=77.2167,
                crime_type='theft',
                sub_category='mobile theft',
                victim_name='Amit Kumar',
                victim_age=25,
                victim_gender='Male',
                victim_contact='9876543210',
                is_missing_person=False,
                is_injury_involved=False,
                is_property_damage=True,
                estimated_loss=25000.0,
                police_complaint_filed=True,
                police_station='Central Police Station',
                police_complaint_number='FIR/456/2024',
                police_complaint_date=datetime.utcnow() - timedelta(days=1),
                priority='medium',
                ai_classification='Property Theft',
                confidence_score=0.85,
                keywords='stolen, mobile, phone, market, pocket',
                status='pending'
            )
            db.session.add(complaint1)
            
            # Complaint 2: Missing Person
            complaint2 = Complaint(
                case_id=generate_case_id(),
                user_id=public_user.id,
                title='Missing Elderly Person',
                description='My 65-year-old father went for a morning walk and hasn\'t returned. He was last seen near the park wearing blue shirt and black pants.',
                incident_date=datetime.utcnow() - timedelta(hours=6),
                state='Delhi',
                district='South Delhi',
                location='Lodhi Garden',
                latitude=28.5931,
                longitude=77.2197,
                crime_type='missing_person',
                sub_category='elderly missing',
                victim_name='Ramesh Chandra',
                victim_age=65,
                victim_gender='Male',
                victim_contact='9876543211',
                is_missing_person=True,
                is_injury_involved=False,
                is_property_damage=False,
                injury_severity='none',
                police_complaint_filed=True,
                police_station='South Delhi Police Station',
                police_complaint_number='FIR/457/2024',
                police_complaint_date=datetime.utcnow() - timedelta(hours=5),
                priority='high',
                ai_classification='Missing Person',
                confidence_score=0.92,
                keywords='missing, elderly, walk, park, blue shirt',
                status='assigned'
            )
            db.session.add(complaint2)
            db.session.commit()
            print("✓ Sample complaints created")
        
        # Create volunteer application
        if not VolunteerApplication.query.first():
            # Create a user for volunteer application
            if not User.query.filter_by(email='applicant@ireport.com').first():
                applicant_user = User(
                    email='applicant@ireport.com',
                    full_name='Rahul Verma',
                    role='public',
                    is_verified=True,
                    is_active=True
                )
                applicant_user.set_password('applicant123')
                db.session.add(applicant_user)
                db.session.commit()
                
                application = VolunteerApplication(
                    user_id=applicant_user.id,
                    skills='Community Outreach, Digital Literacy',
                    qualifications='B.Com Graduate',
                    experience='1 year volunteering',
                    availability='Evenings',
                    state='Delhi',
                    district='West Delhi',
                    pincode='110018',
                    address='B-45, Rajouri Garden, Delhi',
                    date_of_birth=datetime(1995, 8, 20),
                    gender='Male',
                    id_proof_type='Aadhar',
                    id_proof_number='9876-5432-1098',
                    motivation_letter='I want to help my community and make a difference in crime prevention and awareness.',
                    status='pending',
                    applied_date=datetime.utcnow() - timedelta(days=5)
                )
                db.session.add(application)
                db.session.commit()
                print("✓ Volunteer application created")
        
        # Create sample OTP entry
        if not OTP.query.first():
            otp_entry = OTP(
                email='test@ireport.com',
                otp='123456',
                is_reset=False,
                expires_at=datetime.utcnow() + timedelta(minutes=10)
            )
            db.session.add(otp_entry)
            db.session.commit()
            print("✓ Sample OTP entry created")
        
        print("✓ Sample data seeded successfully!")
        print("\nSample Login Credentials:")
        print("Admin: admin@ireport.com / admin123")
        print("Police: officer@ireport.com / police123")
        print("Volunteer: volunteer@ireport.com / volunteer123")
        print("Public: public@ireport.com / public123")
        print("Applicant: applicant@ireport.com / applicant123")

if __name__ == '__main__':
    seed_sample_data()