import random
import string
import re
from flask_mail import Message
from flask import current_app, request, jsonify
from functools import wraps
from auth.auth_handler import Auth
from database.models import User

def generate_otp(length=6):
    """Generate numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(email, otp, is_reset=False, language='en'):
    """Send OTP email with proper error handling"""
    from flask import current_app
    
    # Debug information
    print(f"🔧 Email Config Check:")
    print(f"   Email: {email}")
    print(f"   OTP: {otp}")
    print(f"   DEBUG_MODE: {current_app.config.get('DEBUG_MODE', False)}")
    print(f"   MAIL_SERVER: {current_app.config.get('MAIL_SERVER')}")
    
    # In development/debug mode, just log the OTP and return success
    if current_app.config.get('DEBUG_MODE', True) or not current_app.config.get('MAIL_SERVER'):
        print(f"📧 DEVELOPMENT MODE: OTP for {email} is {otp}")
        print(f"📧 Email would be sent to: {email}")
        print(f"📧 OTP Code: {otp}")
        print(f"📧 Valid for: 10 minutes")
        return True
    
    # Production mode - try to send actual email
    try:
        # Import inside function to avoid circular imports
        from flask_mail import Message
        
        # Check if mail extension is properly initialized
        if 'mail' not in current_app.extensions:
            print("❌ Mail extension not initialized")
            return False
            
        mail = current_app.extensions['mail']
        
        # Create email subject and body
        subject = "iReport - Verification Code" if not is_reset else "iReport - Password Reset Code"
        
        msg = Message(
            subject=subject,
            recipients=[email],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@ireport.gov.in'),
            body=f"""
            Your iReport verification code is: {otp}
            
            This code will expire in 10 minutes.
            
            If you didn't request this code, please ignore this email.
            
            - iReport Team
            """,
            html=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2196F3;">iReport</h2>
                <h3>Your Verification Code</h3>
                <p>Use the following code to {'reset your password' if is_reset else 'verify your account'}:</p>
                <div style="background: #f5f5f5; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; margin: 20px 0;">
                    {otp}
                </div>
                <p>This code will expire in 10 minutes.</p>
                <p>If you didn't request this code, please ignore this email.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">Indian Cyber Crime Coordination Centre</p>
            </div>
            """
        )
        
        # Send the email
        mail.send(msg)
        print(f"✅ OTP email successfully sent to {email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {email}: {str(e)}")
        
        # Even if email fails in production, log the OTP for debugging
        print(f"📧 BACKUP OTP LOG: {otp} for {email}")
        
        # In development, still return True to allow registration to proceed
        if current_app.config.get('DEBUG_MODE', True):
            return True
            
        return False
        
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    return True, "Password is valid"

# Authentication decorators
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Handle both "Bearer token" and just "token" formats
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(" ")[1]
                else:
                    token = auth_header
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            # Decode token using Auth class
            token_data = Auth.decode_token(token)
            
            # Check if decode returned an error
            if isinstance(token_data, dict) and 'error' in token_data:
                return jsonify({"error": token_data['error']}), 401
            
            # Get user_id from the decoded data
            user_id = token_data.get('user_id')
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
        @token_required
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

# Specific role decorators
def admin_required(f):
    return role_required('admin')(f)

def police_required(f):
    return role_required(['police', 'admin'])(f)

def volunteer_required(f):
    return role_required(['volunteer', 'police', 'admin'])(f)

def authenticated_user(f):
    return role_required(['public', 'volunteer', 'police', 'admin'])(f)