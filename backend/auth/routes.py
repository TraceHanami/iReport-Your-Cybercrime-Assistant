from flask import Blueprint, request, jsonify, current_app
import random
import string
from database.connection import db
from database.models import User, OTP
from auth.auth_handler import Auth
from auth.utils import generate_otp, send_otp_email, token_required, validate_email, validate_password
from datetime import datetime, timedelta
from flask_mail import Message, Mail
from sqlalchemy import func

# Create blueprint
auth_bp = Blueprint('auth', __name__)

def generate_otp(length=6):
    """Generate a numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(email, otp, is_reset=False):
    """Send OTP email to user"""
    try:
        mail = Mail(current_app)
        
        subject = 'iReport - Verify Your Account' if not is_reset else 'iReport - Password Reset OTP'
        
        msg = Message(
            subject=subject,
            recipients=[email],
            sender=current_app.config.get('MAIL_USERNAME', 'noreply@ireport.com')
        )
        
        if is_reset:
            msg.body = f'''
            You requested a password reset for your iReport account.
            
            Your reset code is: {otp}
            
            This code will expire in 10 minutes.
            
            If you didn't request this reset, please ignore this email.
            
            Best regards,
            iReport Team
            '''
            
            msg.html = f'''
            <h2>iReport - Password Reset</h2>
            <p>You requested a password reset for your iReport account.</p>
            <p>Your reset code is: <strong>{otp}</strong></p>
            <p>This code will expire in 10 minutes.</p>
            <p>If you didn't request this reset, please ignore this email.</p>
            <br>
            <p>Best regards,<br>iReport Team</p>
            '''
        else:
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
        print(f"✅ OTP {otp} sent to {email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        if current_app.config.get('DEBUG'):
            print(f"DEBUG: OTP for {email} is {otp}")
        return False

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print(f"📥 Received registration data: {data}")
        
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
        
        # Generate and store OTP in database
        otp = generate_otp()
        # ✅ FIX: Use otp_code instead of otp
        otp_record = OTP(
            email=data['email'],
            otp_code=otp,  # Changed from 'otp' to 'otp_code'
            is_reset=False,
            is_used=False,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.session.add(otp_record)
        db.session.commit()
        
        print(f"✅ OTP generated and saved to database: {otp} for {data['email']}")
        
        # Send OTP email
        email_sent = send_otp_email(data['email'], otp)
        
        response_data = {
            'success': True,
            'message': 'Registration successful. Please check your email for verification code.',
            'requires_verification': True,
            'email': data['email']
        }
        
        if current_app.config.get('DEBUG') or not email_sent:
            response_data["debug_otp"] = otp
            response_data["debug_mode"] = True
            
        return jsonify(response_data), 201
        
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
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
        print(f"📥 OTP Verification data: {data}")
        
        email = data.get('email', '').strip().lower()
        otp_attempt = data.get('otp', '').strip()
        is_reset = data.get('is_reset', False)
        
        if not email or not otp_attempt:
            print("❌ Missing email or OTP")
            return jsonify({
                'success': False,
                'message': 'Email and OTP are required'
            }), 400
        
        print(f"🔍 Checking OTP for: {email}, is_reset: {is_reset}")
        
        # For ALL OTP types, don't check is_used during verification
        otp_record = OTP.query.filter(
            func.lower(OTP.email) == email,
            OTP.is_reset == is_reset,
            OTP.expires_at > datetime.utcnow()
        ).order_by(OTP.created_at.desc()).first()
        
        if not otp_record:
            print(f"❌ No valid OTP found for: {email} (is_reset={is_reset})")
            return jsonify({
                'success': False,
                'message': 'Invalid or expired OTP'
            }), 404
        
        print(f"✅ OTP found: {otp_record.otp_code}, is_used: {otp_record.is_used}, expires: {otp_record.expires_at}")
        
        # Verify OTP code
        if otp_record.otp_code != otp_attempt:
            print(f"❌ Invalid OTP. Expected: {otp_record.otp_code}, Got: {otp_attempt}")
            return jsonify({
                'success': False,
                'message': 'Invalid OTP'
            }), 400
        
        print("✅ OTP validated successfully")
        
        # ✅ CRITICAL FIX: Only mark as used for registration OTPs, NOT for reset OTPs
        if not is_reset:
            otp_record.is_used = True
            # For registration OTPs, verify the user
            user = User.query.filter(func.lower(User.email) == email).first()
            if not user:
                print(f"❌ User not found: {email}")
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404
            
            user.is_verified = True
            user.verified_at = datetime.utcnow()
            print(f"✅ User verified: {email}")
        
        # ✅ IMPORTANT: Only commit if we made changes (for registration)
        if not is_reset:
            db.session.commit()
            print(f"✅ Registration OTP marked as used and user verified: {email}")
        else:
            print(f"✅ Reset OTP verified (not marked as used yet): {email}")
        
        return jsonify({
            'success': True,
            'message': 'Account verified successfully' if not is_reset else 'OTP verified successfully',
            'requires_password_reset': is_reset 
        })
        
    except Exception as e:
        print(f"❌ OTP verification error: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Verification failed: {str(e)}'
        }), 500
                
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        print(f"📧 Forgot Password - Received data: {data}")
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            print("❌ Missing email in request")
            return jsonify({"error": "Email is required"}), 400
        
        print(f"🔍 Looking up user: {email}")
        
        # Use case-insensitive search for user
        user = User.query.filter(func.lower(User.email) == email).first()
        
        # For security, always return success even if user doesn't exist
        if not user:
            print(f"⚠️ User not found (but returning success for security): {email}")
            return jsonify({
                "message": "If your email is registered, you will receive a reset OTP shortly",
                "success": True
            }), 200
        
        print(f"✅ User found: {user.email}")
        
        # Generate reset OTP
        reset_otp = generate_otp()
        print(f"🔐 Generated reset OTP: {reset_otp}")
        
        # ✅ FIX: Use otp_code instead of otp
        otp_record = OTP(
            email=email,
            otp_code=reset_otp,  # Changed from 'otp' to 'otp_code'
            is_reset=True,
            is_used=False,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.session.add(otp_record)
        db.session.commit()
        print("✅ Reset OTP saved to database")
        
        # Send reset OTP email
        email_sent = send_otp_email(email, reset_otp, is_reset=True)
        print(f"📨 Reset email sent: {email_sent}")
        
        response_data = {
            "message": "If your email is registered, you will receive a reset OTP shortly",
            "success": True,
            "email_sent": email_sent
        }
        
        # Include OTP in debug mode
        if current_app.config.get('DEBUG', False):
            response_data["debug_otp"] = reset_otp
            response_data["debug_mode"] = True
            
        return jsonify(response_data), 200
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Forgot password error: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Password reset request failed",
            "success": False
        }), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        print(f"🔄 Reset Password - Received data: {data}")
        
        required_fields = ['email', 'otp', 'new_password']
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing required field: {field}")
                return jsonify({
                    "error": f"Missing required field: {field}",
                    "success": False
                }), 400
        
        email = data['email'].strip().lower()
        otp_attempt = data['otp'].strip()
        new_password = data['new_password']
        
        print(f"🔍 Processing reset for: {email}")
        
        # Check OTP in database - allow OTPs that are not used yet
        otp_record = OTP.query.filter(
            func.lower(OTP.email) == email,
            OTP.is_reset == True,
            OTP.expires_at > datetime.utcnow()
        ).order_by(OTP.created_at.desc()).first()
        
        if not otp_record:
            print(f"❌ No valid reset OTP found for: {email}")
            return jsonify({
                "error": "OTP not found or expired",
                "success": False
            }), 400
        
        print(f"✅ OTP record found: {otp_record.otp_code}, is_used: {otp_record.is_used}")
        
        # Verify OTP code
        if otp_record.otp_code != otp_attempt:
            print(f"❌ Invalid OTP. Expected: {otp_record.otp_code}, Got: {otp_attempt}")
            return jsonify({
                "error": "Invalid OTP",
                "success": False
            }), 400
        
        print("✅ OTP validated successfully")
        
        # Update password
        user = User.query.filter(func.lower(User.email) == email).first()
        if not user:
            print(f"❌ User not found: {email}")
            return jsonify({
                "error": "User not found",
                "success": False
            }), 404
        
        print(f"🔐 Setting new password for user: {user.email}")
        print(f"🔐 New password length: {len(new_password)}")
        
        # Set the new password
        user.set_password(new_password)
        
        # ✅ AUTO-VERIFY USER after successful password reset
        if not user.is_verified:
            user.is_verified = True
            user.verified_at = datetime.utcnow()
            print(f"✅ Auto-verified user: {user.email}")
        
        # Verify the password was set
        print(f"🔐 Verifying password was set...")
        password_check = user.check_password(new_password)
        print(f"🔐 Immediate password verification: {password_check}")
        
        otp_record.is_used = True  # Mark OTP as used only after successful password reset
        db.session.commit()
        
        print(f"✅ Password reset successful for: {email}")
        print(f"✅ User verification status: {user.is_verified}")
        
        return jsonify({
            "message": "Password reset successful",
            "success": True,
            "user_verified": user.is_verified
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Reset password error: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Password reset failed",
            "success": False
        }), 500
                                
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password')
        
        print(f"🔑 Login attempt for: {email}")
        print(f"📧 Email received (normalized): {email}")
        print(f"🔒 Password received: {'*' * len(password) if password else 'None'}")
        
        if not email or not password:
            print("❌ Missing email or password")
            return jsonify({"error": "Email and password are required"}), 400
        
        # Use case-insensitive query
        user = User.query.filter(func.lower(User.email) == email).first()
        
        if not user:
            print(f"❌ User not found in database: {email}")
            return jsonify({"error": "Invalid credentials"}), 401
        
        print(f"✅ User found: {user.email}, ID: {user.id}")
        print(f"📊 User details - Verified: {user.is_verified}, Role: {user.role}")
        
        # Check password
        password_valid = user.check_password(password)
        print(f"🔑 Password check result: {password_valid}")
        
        if not password_valid:
            print(f"❌ Invalid password for user: {email}")
            return jsonify({"error": "Invalid credentials"}), 401
        
        if not user.is_verified:
            print(f"❌ User not verified: {email}")
            return jsonify({"error": "Please verify your email first"}), 403
        
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
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Login failed"}), 500

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400
        
        # Check if user exists
        user = User.query.filter(func.lower(User.email) == email).first()
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
        # ✅ FIX: Use otp_code instead of otp
        otp_record = OTP(
            email=email,
            otp_code=otp,  # Changed from 'otp' to 'otp_code'
            is_reset=False,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.session.add(otp_record)
        db.session.commit()
        
        # Send new OTP email
        email_sent = send_otp_email(email, otp)
        
        response_data = {
            'success': True,
            'message': 'New verification code sent to your email'
        }
        
        if current_app.config.get('DEBUG') or not email_sent:
            response_data["debug_otp"] = otp
            
        return jsonify(response_data)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to resend OTP: {str(e)}'
        }), 500

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
    return jsonify({
        'mail_server': current_app.config.get('MAIL_SERVER'),
        'mail_username': current_app.config.get('MAIL_USERNAME'),
        'mail_password_set': bool(current_app.config.get('MAIL_PASSWORD')),
        'mail_extensions_loaded': 'mail' in current_app.extensions,
        'debug_mode': current_app.config.get('DEBUG', False)
    })