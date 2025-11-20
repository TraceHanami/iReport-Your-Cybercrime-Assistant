from flask import Blueprint, request, jsonify, current_app
import random
import string
from database.connection import db
from database.models import User, OTP
from auth.auth_handler import Auth
from auth.utils import generate_otp, send_otp_email, token_required, validate_email, validate_password
from datetime import datetime, timedelta

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Store OTPs temporarily (in production, use Redis)
otp_storage = {}

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print(f"📥 Received registration data: {data}")  # Debug log
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'phone', 'role', 'password']
        for field in required_fields:
            if not data.get(field):
                print(f"❌ Missing required field: {field}")
                return jsonify({
                    'success': False,
                    'message': f'{field} is required'
                }), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            print(f"❌ User already exists: {data['email']}")
            return jsonify({
                'success': False,
                'message': 'User with this email already exists'
            }), 409
        
        print("✅ Validation passed, creating user...")
        
        # Create new user
        user = User(
            full_name=data['full_name'],
            email=data['email'],
            phone=data['phone'],
            role=data['role'],
            is_verified=False,
            badge_number=data.get('badge_number'),
            station=data.get('station'),
            state=data.get('state'),
            district=data.get('district')
        )
        user.set_password(data['password'])
        
        print(f"✅ User object created: {user.email}")
        
        db.session.add(user)
        db.session.commit()
        print("✅ User saved to database")
        
        # Generate and send OTP
        otp = generate_otp()
        otp_storage[data['email']] = {
            'otp': otp,
            'expires_at': datetime.utcnow() + timedelta(minutes=10)
        }
        
        print(f"✅ OTP generated: {otp} for {data['email']}")
        
        # Send OTP email
        send_otp_email(data['email'], otp)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful. Please check your email for verification code.',
            'requires_verification': True,
            'email': data['email']
        }), 201
        
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Registration failed: {str(e)}'
        }), 500
        
@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        print(f"📥 OTP Verification data: {data}")  # Debug log
        
        email = data.get('email')
        otp = data.get('otp')
        
        if not email or not otp:
            print("❌ Missing email or OTP")
            return jsonify({
                'success': False,
                'message': 'Email and OTP are required'
            }), 400
        
        print(f"🔍 Checking OTP for: {email}")
        
        # Check if OTP exists and is valid
        stored_otp_data = otp_storage.get(email)
        if not stored_otp_data:
            print(f"❌ No OTP found for: {email}")
            return jsonify({
                'success': False,
                'message': 'No verification pending for this email'
            }), 404
        
        print(f"✅ OTP found, checking expiration...")
        
        if datetime.utcnow() > stored_otp_data['expires_at']:
            del otp_storage[email]
            print(f"❌ OTP expired for: {email}")
            return jsonify({
                'success': False,
                'message': 'OTP has expired'
            }), 400
        
        if stored_otp_data['otp'] != otp:
            print(f"❌ Invalid OTP. Expected: {stored_otp_data['otp']}, Got: {otp}")
            return jsonify({
                'success': False,
                'message': 'Invalid OTP'
            }), 400
        
        print(f"✅ OTP validated for: {email}")
        
        # OTP is valid, verify user
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"❌ User not found: {email}")
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        user.is_verified = True
        user.verified_at = datetime.utcnow()
        db.session.commit()
        
        print(f"✅ User verified: {email}")
        
        # Clean up OTP
        del otp_storage[email]
        
        # Generate auth token (if using JWT)
        # from auth.utils import generate_token
        # token = generate_token(user.id)
        
        # For now, return success without token
        return jsonify({
            'success': True,
            'message': 'Account verified successfully',
            # 'token': token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        print(f"❌ OTP verification error: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        
        return jsonify({
            'success': False,
            'message': f'Verification failed: {str(e)}'
        }), 500
        
@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400
        
        # Check if user exists and is not verified
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        if user.is_verified:
            return jsonify({
                'success': False,
                'message': 'User is already verified'
            }), 400
        
        # Generate new OTP
        otp = generate_otp()
        otp_storage[email] = {
            'otp': otp,
            'expires_at': datetime.utcnow() + timedelta(minutes=10)
        }
        
        # Send new OTP email
        send_otp_email(email, otp)
        
        return jsonify({
            'success': True,
            'message': 'New verification code sent to your email'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to resend OTP: {str(e)}'
        }), 500

def generate_otp(length=6):
    """Generate a numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(email, otp):
    """Send OTP email to user"""
    try:
        from flask_mail import Mail
        mail = Mail(current_app)
        
        msg = Message(
            subject='iReport - Verify Your Account',
            recipients=[email],
            sender=current_app.config['MAIL_USERNAME']
        )
        
        msg.body = f'''
        Thank you for registering with iReport!
        
        Your verification code is: {otp}
        
        This code will expire in 10 minutes.
        
        If you didn't request this verification, please ignore this email.
        
        Best regards,
        iReport Team
        '''
        
        msg.html = f'''
        <h2>iReport - Verify Your Account</h2>
        <p>Thank you for registering with iReport!</p>
        <p>Your verification code is: <strong>{otp}</strong></p>
        <p>This code will expire in 10 minutes.</p>
        <p>If you didn't request this verification, please ignore this email.</p>
        <br>
        <p>Best regards,<br>iReport Team</p>
        '''
        
        mail.send(msg)
        print(f"OTP {otp} sent to {email}")  # For development
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        # Don't fail registration if email fails in development
        if current_app.config.get('DEBUG_MODE'):
            print(f"DEBUG: OTP for {email} is {otp}")

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password')
        
        print(f"🔑 Login attempt for: {email}")
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        if not user.check_password(password):  # Use the model method
            return jsonify({"error": "Invalid credentials"}), 401
        
        if not user.is_active:
            return jsonify({"error": "Account is deactivated"}), 403
        
        # Generate token
        token = Auth.generate_token(user.id, user.role)
        
        print(f"✅ Login successful for {user.email}, role: {user.role}")
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({"error": "Login failed"}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            # Don't reveal whether user exists for security
            return jsonify({"message": "If the email exists, a reset OTP has been sent"}), 200
        
        # Generate reset OTP
        reset_otp = generate_otp()
        
        # Store in database
        otp_record = OTP(
            email=email,
            otp=reset_otp,
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            is_reset=True
        )
        db.session.add(otp_record)
        db.session.commit()
        
        # Send reset OTP
        email_sent = send_otp_email(email, reset_otp, is_reset=True)
        
        response_data = {
            "message": "If the email exists, a reset OTP has been sent",
            "email_sent": email_sent
        }
        
        # Include OTP in debug mode or if email failed
        if current_app.config.get('DEBUG', False) or not email_sent:
            response_data["debug_otp"] = reset_otp
            response_data["debug_mode"] = True
            
        return jsonify(response_data), 200
            
    except Exception as e:
        print(f"❌ Forgot password error: {e}")
        return jsonify({"error": "Password reset request failed"}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        
        required_fields = ['email', 'otp', 'new_password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        email = data['email'].strip().lower()
        otp_attempt = data['otp'].strip()
        new_password = data['new_password']
        
        # Validate password strength
        is_valid_password, password_msg = validate_password(new_password)
        if not is_valid_password:
            return jsonify({"error": password_msg}), 400
        
        # Check OTP in database
        otp_record = OTP.query.filter_by(email=email, is_reset=True).order_by(OTP.created_at.desc()).first()
        
        if not otp_record:
            return jsonify({"error": "OTP not found or expired"}), 400
        
        # Check OTP expiration
        if otp_record.is_expired():
            db.session.delete(otp_record)
            db.session.commit()
            return jsonify({"error": "OTP expired"}), 400
        
        if otp_record.otp != otp_attempt:
            return jsonify({"error": "Invalid OTP"}), 400
        
        # Update password
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user.set_password(new_password)
        db.session.delete(otp_record)  # Remove used OTP
        db.session.commit()
        
        return jsonify({"message": "Password reset successful"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Reset password error: {e}")
        return jsonify({"error": "Password reset failed"}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user profile"""
    try:
        return jsonify({
            "user": current_user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/test', methods=['GET'])
def test_auth():
    return jsonify({"message": "Auth blueprint is working!", "status": "success"}), 200


@auth_bp.route('/debug-email', methods=['GET'])
def debug_email():
    from flask import current_app
    return jsonify({
        'mail_server': current_app.config.get('MAIL_SERVER'),
        'mail_username': current_app.config.get('MAIL_USERNAME'),
        'mail_password_set': bool(current_app.config.get('MAIL_PASSWORD')),
        'mail_extensions_loaded': 'mail' in current_app.extensions,
        'debug_mode': current_app.config.get('DEBUG_MODE', False)
    })