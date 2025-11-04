from app import create_app
from database.connection import db

def init_database():
    """Initialize the database and create all tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📊 Created tables: {tables}")

if __name__ == '__main__':
    init_database()