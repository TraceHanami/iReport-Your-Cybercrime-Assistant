from flask import Flask
from database.connection import db
from database.models import User
from auth.models import Auth

# Create Flask app and configure it
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ireport.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

def create_test_users():
    with app.app_context():
        print("Creating test users...")
        
        # Test public user
        if not User.query.filter_by(email='test@example.com').first():
            test_user = User(
                email='test@example.com',
                password_hash=Auth.hash_password('test123'),
                full_name='Test User',
                role='public',
                is_verified=True
            )
            db.session.add(test_user)
            print("✓ Test user created: test@example.com / test123")
        
        db.session.commit()
        print("✓ Test users created successfully!")

if __name__ == '__main__':
    create_test_users()