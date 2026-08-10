import os
import sys

# Add project root and backend folder to system path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
backend_dir = os.path.join(root_dir, 'backend')

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Ensure working directory is backend for relative file lookups
os.chdir(backend_dir)

# Import app factory
from app import create_app
from database.connection import db

app = create_app()

# Auto-create database tables on serverless startup if needed
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Serverless DB table initialization warning: {e}")

# Vercel WSGI entry point
handler = app
