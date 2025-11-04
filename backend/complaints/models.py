from datetime import datetime
import uuid
from database.connection import db

def generate_case_id():
    timestamp = datetime.utcnow().strftime('%Y%m%d')
    unique_id = uuid.uuid4().hex[:8].upper()
    return f"IR{timestamp}{unique_id}"