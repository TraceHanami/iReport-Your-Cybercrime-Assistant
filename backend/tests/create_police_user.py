from flask import Flask
from database.connection import db
from database.models import User, PoliceOfficer
from auth.models import Auth

# Create Flask app and configure it
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ireport.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

def create_police_users():
    with app.app_context():
        print("Creating additional police users...")
        
        # Create multiple police officers for testing
        police_officers = [
            {
                "email": "inspector.sharma@ireport.com",
                "password": "police123",
                "name": "Inspector Vikram Sharma",
                "badge": "DEL123457",
                "rank": "Inspector",
                "station": "South Delhi Police Station",
                "state": "Delhi",
                "district": "South Delhi"
            },
            {
                "email": "constable.singh@ireport.com", 
                "password": "police123",
                "name": "Constable Rajesh Singh",
                "badge": "DEL123458",
                "rank": "Constable",
                "station": "Central Police Station",
                "state": "Delhi",
                "district": "Central Delhi"
            }
        ]
        
        for officer_data in police_officers:
            if not User.query.filter_by(email=officer_data["email"]).first():
                # Create user
                user = User(
                    email=officer_data["email"],
                    password_hash=Auth.hash_password(officer_data["password"]),
                    full_name=officer_data["name"],
                    role='police',
                    is_verified=True
                )
                db.session.add(user)
                db.session.commit()
                
                # Create police officer profile
                officer = PoliceOfficer(
                    user_id=user.id,
                    badge_number=officer_data["badge"],
                    rank=officer_data["rank"],
                    station=officer_data["station"],
                    state=officer_data["state"],
                    district=officer_data["district"]
                )
                db.session.add(officer)
                print(f"✓ Police officer created: {officer_data['name']}")
        
        db.session.commit()
        print("✓ Police users created successfully!")

if __name__ == '__main__':
    create_police_users()