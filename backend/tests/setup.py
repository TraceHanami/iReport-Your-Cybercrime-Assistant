import nltk
import os
from flask import Flask
from database.connection import db

def setup_application():
    print("=== iReport Backend Setup ===")
    
    # Download NLTK data
    print("\n1. Downloading NLTK data...")
    try:
        nltk.data.find('tokenizers/punkt')
        print("✓ NLTK 'punkt' already installed")
    except LookupError:
        nltk.download('punkt')
        print("✓ NLTK 'punkt' downloaded")
    
    # Initialize database
    print("\n2. Initializing database...")
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ireport.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        from database.models import User, Volunteer, PoliceOfficer, Complaint, CaseAssignment, CaseUpdate
        db.create_all()
        print("✓ Database tables created")
    
    # Create directories
    print("\n3. Creating directories...")
    os.makedirs('uploads/evidence', exist_ok=True)
    os.makedirs('uploads/profiles', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    print("✓ Directories created")
    
    print("\n=== Setup completed successfully! ===")
    print("You can now run: python main.py")

if __name__ == '__main__':
    setup_application()