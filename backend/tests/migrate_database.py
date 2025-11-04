# migrate_database.py
from app import app
from database.connection import db
from database.models import PoliceOfficer
from sqlalchemy import text

def migrate_database():
    with app.app_context():
        try:
            # Add missing columns if they don't exist
            with db.engine.connect() as conn:
                # Check if department column exists
                result = conn.execute(text("PRAGMA table_info(police_officers)"))
                columns = [row[1] for row in result]
                
                if 'department' not in columns:
                    print("➕ Adding department column...")
                    conn.execute(text("ALTER TABLE police_officers ADD COLUMN department VARCHAR(100) DEFAULT 'General Department'"))
                
                if 'rank' not in columns:
                    print("➕ Adding rank column...")
                    conn.execute(text("ALTER TABLE police_officers ADD COLUMN rank VARCHAR(50) DEFAULT 'Officer'"))
                
                if 'police_station' not in columns:
                    print("➕ Adding police_station column...")
                    conn.execute(text("ALTER TABLE police_officers ADD COLUMN police_station VARCHAR(100) DEFAULT 'Local Station'"))
                
                if 'contact_number' not in columns:
                    print("➕ Adding contact_number column...")
                    conn.execute(text("ALTER TABLE police_officers ADD COLUMN contact_number VARCHAR(20)"))
                
                if 'specialization' not in columns:
                    print("➕ Adding specialization column...")
                    conn.execute(text("ALTER TABLE police_officers ADD COLUMN specialization VARCHAR(100)"))
                
                conn.commit()
            
            print("✅ Database migration complete!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    migrate_database()