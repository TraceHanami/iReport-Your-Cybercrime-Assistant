import random
import string
from flask_mail import Message
from flask import current_app, request, jsonify
from functools import wraps
from auth.auth_handler import Auth
from database.connection import db
from database.models import User

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(email, otp, language='en'):
    subject = "Your iReport Verification OTP"
    body = f"""
    Dear User,
    
    Your OTP for iReport verification is: {otp}
    
    This OTP is valid for 10 minutes.
    
    Regards,
    iReport Team
    """
    
    try:
        # Check if mail is configured
        if not hasattr(current_app, 'extensions') or 'mail' not in current_app.extensions:
            print("⚠️ Mail not configured - returning False")
            return False
            
        msg = Message(
            subject=subject,
            recipients=[email],
            body=body,
            sender=current_app.config.get('MAIL_USERNAME', 'noreply@ireport.com')
        )
        current_app.extensions['mail'].send(msg)
        print(f"✅ OTP email sent to {email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Authentication decorators
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            # Decode token
            data = Auth.decode_token(token)
            
            # Check if decode returned an error
            if isinstance(data, dict) and 'error' in data:
                return jsonify({"error": data['error']}), 401
            
            # Get user_id from the decoded data
            user_id = data.get('user_id')
            if not user_id:
                return jsonify({"error": "Invalid token payload"}), 401
            
            current_user = User.query.get(user_id)
            
            if not current_user:
                return jsonify({"error": "User not found"}), 401
            
            if not current_user.is_active:
                return jsonify({"error": "Account is deactivated"}), 403
                
        except Exception as e:
            print(f"Token validation error: {e}")
            return jsonify({"error": "Invalid token"}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def role_required(required_roles):
    """
    Decorator to require specific roles for access
    required_roles can be a string or list of roles
    """
    def decorator(f):
        @wraps(f)
        @token_required  # This ensures the user is authenticated first
        def decorated_function(current_user, *args, **kwargs):
            # Convert single role to list for consistent handling
            if isinstance(required_roles, str):
                roles_needed = [required_roles]
            else:
                roles_needed = required_roles
            
            # Check if user has any of the required roles
            if current_user.role not in roles_needed:
                return jsonify({
                    'error': f'Insufficient permissions. Required roles: {", ".join(roles_needed)}. Your role: {current_user.role}'
                }), 403
            
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

# Specific role decorators (these depend on role_required)
def admin_required(f):
    return role_required(['admin'])(f)

def police_required(f):
    return role_required(['police', 'admin'])(f)

def volunteer_required(f):
    return role_required(['volunteer', 'police', 'admin'])(f)

def authenticated_user(f):
    return role_required(['public', 'volunteer', 'police', 'admin'])(f)