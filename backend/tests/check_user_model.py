# check_user_model.py
from database.connection import db, init_db
from flask import Flask
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ireport.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)

with app.app_context():
    from database.models import User
    
    print("🔍 User Model Structure:")
    print("=" * 50)
    
    # Check User class attributes
    user_attrs = [attr for attr in dir(User) if not attr.startswith('_')]
    print("User class attributes:")
    for attr in user_attrs:
        print(f"  - {attr}")
    
    print("\n📋 User table columns:")
    # Check table columns
    if hasattr(User, '__table__'):
        for column in User.__table__.columns:
            print(f"  - {column.name}: {column.type}")
    
    print("\n👤 Sample users in database:")
    users = User.query.all()
    for user in users[:5]:  # Show first 5 users
        print(f"  - {user.email} (ID: {user.id}, Role: {getattr(user, 'role', 'N/A')})")
    
    print("=" * 50)