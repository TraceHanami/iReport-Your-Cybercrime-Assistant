from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate
import os
from datetime import datetime
import logging
from dotenv import load_dotenv
import nltk
from sqlalchemy import text

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_blueprints(app):
    """Register all blueprints with lazy imports to avoid circular imports"""
    
    print("\n" + "="*80)
    print("🔍 DEBUG: STARTING BLUEPRINT REGISTRATION")
    print("="*80)
    
    blueprints = [
        ('auth.routes', 'auth_bp', '/api/auth'),
        ('complaints.routes', 'complaints_bp', '/api/complaints'),
        ('complaints.track_routes', 'track_bp', '/api/track'),
        ('police.routes', 'police_bp', '/api/police'),
        ('admin.routes', 'admin_bp', '/api/admin'),
        ('chatbot.routes', 'chatbot_bp', '/api/chatbot'),
        ('notifications.routes', 'notifications_bp', '/api/notifications'),
        ('sms.routes', 'sms_bp', '/api/sms'),
        ('admin.advanced_routes', 'advanced_analytics_bp', '/api/analytics'),
        ('reports.routes', 'reports_bp', '/api/reports')
    ]
    
    for module_path, bp_name, url_prefix in blueprints:
        try:
            print(f"\n🔄 Attempting to load {bp_name} from {module_path}...")
            
            # Try to import the module
            module = __import__(module_path, fromlist=[bp_name])
            print(f"   ✅ Module imported successfully")
            
            # Try to get the blueprint
            blueprint = getattr(module, bp_name)
            print(f"   ✅ Blueprint found: {blueprint.name}")
            
            # Register the blueprint
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            print(f"   ✅ Registered at: {url_prefix}")
            
            # Special detailed debug for SMS blueprint
            if bp_name == 'sms_bp':
                print(f"\n🎯 SMS BLUEPRINT DETAILED DEBUG:")
                print(f"   - Blueprint object: {blueprint}")
                print(f"   - Blueprint name: {blueprint.name}")
                print(f"   - URL prefix: {url_prefix}")
                print(f"   - Registered in app: {'sms' in app.blueprints}")
                
        except ImportError as e:
            print(f"❌ IMPORT ERROR: {e}")
            import traceback
            traceback.print_exc()
        except AttributeError as e:
            print(f"❌ ATTRIBUTE ERROR: {e}")
            print(f"   Available attributes in {module_path}: {[attr for attr in dir(module) if not attr.startswith('_')]}")
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("🔍 DEBUG: BLUEPRINT REGISTRATION COMPLETED")
    print("="*80)
    
    # Final verification
    print(f"\n📋 FINAL REGISTERED BLUEPRINTS:")
    for name, blueprint in app.blueprints.items():
        print(f"   - {name}")
    
    print(f"\n🌐 SMS ROUTES IN APP:")
    sms_route_count = 0
    for rule in app.url_map.iter_rules():
        if rule.endpoint.startswith('sms.'):
            print(f"   {rule.rule} -> {rule.endpoint}")
            sms_route_count += 1
    
    if sms_route_count == 0:
        print("   ❌ No SMS routes found!")
    else:
        print(f"   ✅ Found {sms_route_count} SMS routes")
            
def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ireport.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # DEBUG MODE FOR TESTING
    app.config['DEBUG_MODE'] = True

    # Initialize database FIRST
    from database.connection import db, init_db
    init_db(app)
    
    # THEN initialize extensions
    migrate = Migrate(app, db)
    mail = Mail(app)

    # Create upload directories
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'evidence'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'), exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('models', exist_ok=True)

    # Download NLTK punkt tokenizer if not already installed
    try:
        nltk.data.find('tokenizers/punkt')
        print("✓ NLTK 'punkt' tokenizer already installed")
    except LookupError:
        print("Downloading NLTK 'punkt' tokenizer...")
        nltk.download('punkt')
        print("✓ NLTK 'punkt' tokenizer downloaded successfully")

    # Frontend paths (relative to backend folder)
    FRONTEND_PAGES = os.path.join(os.path.dirname(__file__), '../frontend/pages')
    FRONTEND_ASSETS = os.path.join(os.path.dirname(__file__), '../frontend/assets')

    # Register blueprints
    register_blueprints(app)
    
    @app.route('/debug/sms-routes')
    def debug_sms_routes():
        """Debug endpoint to specifically check SMS routes"""
        sms_routes = []
        all_routes = []
    
        for rule in app.url_map.iter_rules():
            route_info = {
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': rule.rule
            }
            all_routes.append(route_info)
        
            if rule.endpoint.startswith('sms.'):
                sms_routes.append(route_info)
    
        return jsonify({
            'sms_routes_count': len(sms_routes),
            'sms_routes': sms_routes,
            'all_routes_count': len(all_routes),
            'registered_blueprints': list(app.blueprints.keys()),
            'sms_blueprint_registered': 'sms' in app.blueprints,
            'sms_module_status': 'Available' if 'sms' in app.blueprints else 'Missing'
        })
    
    # ==================== ROUTES ====================

    @app.route('/api/health')
    def api_health():
        return jsonify({
            "message": "iReport API is running", 
            "status": "healthy",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat()
        })

    @app.route('/api/system/status')
    def system_status():
        try:
            # Check database connection
            db.session.execute(text('SELECT 1'))
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
            logger.error(f"Database connection error: {e}")
        
        return jsonify({
            "status": "operational",
            "database": db_status,
            "services": {
                "sms": True,
                "analytics": True,
                "notifications": True,
                "chatbot": True,
                "report_generation": True
            },
            "timestamp": datetime.utcnow().isoformat()
        })

    @app.route('/api')
    def api_info():
        return jsonify({
            "message": "iReport Backend API",
            "version": "2.0.0",
            "endpoints": {
                "health": "/api/health",
                "system_status": "/api/system/status",
                "auth": "/api/auth/*",
                "complaints": "/api/complaints/*",
                "tracking": "/api/track/*",
                "analytics": "/api/analytics/*",
                "reports": "/api/reports/*",
                "sms": "/api/sms/*"
            },
            "timestamp": datetime.utcnow().isoformat()
        })

    # Serve frontend pages
    @app.route('/')
    def home():
        try:
            return send_from_directory(FRONTEND_PAGES, 'index.html')
        except FileNotFoundError:
            return jsonify({
                "message": "iReport Frontend",
                "status": "Backend is running",
                "frontend_dev_server": "http://localhost:3000"
            })

    @app.route('/<path:path>')
    def serve_frontend_path(path):
        try:
            return send_from_directory(FRONTEND_PAGES, path)
        except FileNotFoundError:
            return jsonify({
                "error": "Frontend resource not found",
                "path": path
            }), 404

    # Serve frontend assets (CSS, JS, images)
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        return send_from_directory(FRONTEND_ASSETS, filename)

    # ==================== ERROR HANDLERS ====================

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found",
            "timestamp": datetime.utcnow().isoformat()
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Server error: {error}")
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request",
            "timestamp": datetime.utcnow().isoformat()
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed",
            "timestamp": datetime.utcnow().isoformat()
        }), 405

    # ==================== DEBUG ROUTES ====================

    @app.route('/debug/routes')
    def debug_routes():
        """Debug endpoint to see all registered routes"""
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.rule.startswith('/api/'):
                routes.append({
                    'route': rule.rule,
                    'methods': list(rule.methods),
                    'endpoint': rule.endpoint
                })
        return jsonify({
            'api_routes': routes,
            'total_routes': len(routes)
        })

    @app.route('/debug/blueprints')
    def debug_blueprints():
        """Debug endpoint to see registered blueprints"""
        blueprints = list(app.blueprints.keys())
        return jsonify({
            'blueprints': blueprints,
            'total_blueprints': len(blueprints)
        })

    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    print("\n🎯 iReport Backend Server Starting...")
    print("📊 Version: 2.0.0")
    print("🌐 Host: http://0.0.0.0:5000")
    print("🔧 Debug Mode: True")
    
    # Print registered routes
    print("\n" + "="*70)
    print("🚀 iReport Backend Server - Registered API Routes")
    print("="*70)
    
    with app.app_context():
        api_routes = []
        for rule in app.url_map.iter_rules():
            if rule.rule.startswith('/api') or rule.rule == '/':
                methods = ', '.join(sorted([m for m in rule.methods if m not in ['OPTIONS', 'HEAD']]))
                api_routes.append((rule.rule, methods, rule.endpoint))
        
        # Sort routes for better readability
        api_routes.sort(key=lambda x: x[0])
        
        for route, methods, endpoint in api_routes:
            print(f"{route:50} {methods:25} {endpoint}")
    
    print("="*70)
    print("\n✅ Server ready! Test these endpoints:")
    print("   Health Check:    http://localhost:5000/api/health")
    print("   System Status:   http://localhost:5000/api/system/status")
    print("   SMS Debug:       http://localhost:5000/debug/sms-routes")
    print("   Frontend:        http://localhost:5000/")
    print("\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)