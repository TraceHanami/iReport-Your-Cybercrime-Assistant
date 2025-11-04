from flask import Flask
from database.connection import db
from database.models import User, Complaint, PoliceOfficer, Volunteer, CaseAssignment, CaseUpdate

# Create Flask app and configure it
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ireport.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

def view_database_entries():
    with app.app_context():
        print("=== DATABASE ENTRIES ===")
        
        print("\n--- USERS ---")
        users = User.query.all()
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Role: {user.role}, Verified: {user.is_verified}")
        
        print("\n--- COMPLAINTS ---")
        complaints = Complaint.query.all()
        for complaint in complaints:
            print(f"Case ID: {complaint.case_id}, Title: {complaint.title}, Status: {complaint.status}, Priority: {complaint.priority}")
        
        print("\n--- POLICE OFFICERS ---")
        officers = PoliceOfficer.query.all()
        for officer in officers:
            user = User.query.get(officer.user_id)
            print(f"Name: {user.full_name if user else 'N/A'}, Badge: {officer.badge_number}, Station: {officer.station}, Cases: {officer.current_case_load}")
        
        print("\n--- VOLUNTEERS ---")
        volunteers = Volunteer.query.all()
        for volunteer in volunteers:
            user = User.query.get(volunteer.user_id)
            print(f"Name: {user.full_name if user else 'N/A'}, Status: {volunteer.status}, District: {volunteer.district}")
        
        print("\n--- CASE ASSIGNMENTS ---")
        assignments = CaseAssignment.query.all()
        for assignment in assignments:
            print(f"Case ID: {assignment.complaint_id}, Type: {assignment.assignment_type}, Status: {assignment.status}")

if __name__ == '__main__':
    view_database_entries()