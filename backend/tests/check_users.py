from flask import Flask
from database.connection import db
from database.models import User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ireport.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    print("=== Checking Database Users ===")
    users = User.query.all()
    
    if not users:
        print("No users found in database!")
        print("Please run: python seed_data.py")
    else:
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  - ID: {user.id}, Email: {user.email}, Role: {user.role}, Active: {user.is_active}")

if __name__ == '__main__':
    pass