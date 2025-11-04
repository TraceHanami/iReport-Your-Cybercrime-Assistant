from flask import Flask
from database.connection import db
from sqlalchemy import inspect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ireport.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    try:
        # Test database connection
        db.engine.connect()
        print("✓ Database connection successful")
        
        # Test if tables can be created
        from database.models import User
        db.create_all()
        print("✓ Tables created successfully")
        
        # List all tables using inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✓ Tables in database: {tables}")
        
    except Exception as e:
        print(f"✗ Error: {e}")