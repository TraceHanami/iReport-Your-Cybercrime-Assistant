import os
import sys
from flask import Flask

def create_app():
    """Create and configure the Flask app"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ireport.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    from database.connection import db
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
        print("Database tables created!")
    
    # Register blueprints
    from auth.routes import auth_bp
    from complaints.routes import complaints_bp
    from complaints.track_routes import track_bp
    from police.routes import police_bp
    from admin.routes import admin_bp
    from chatbot.routes import chatbot_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(complaints_bp, url_prefix='/api/complaints')
    app.register_blueprint(track_bp, url_prefix='/api/track')
    app.register_blueprint(police_bp, url_prefix='/api/police')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')
    
    @app.route('/')
    def index():
        return {
            "message": "iReport Backend API",
            "version": "2.0.0",
            "status": "Running"
        }
    
    return app

if __name__ == '__main__':
    # Create directories
    os.makedirs('uploads/evidence', exist_ok=True)
    os.makedirs('uploads/profiles', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    app = create_app()
    print("Server starting on http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)