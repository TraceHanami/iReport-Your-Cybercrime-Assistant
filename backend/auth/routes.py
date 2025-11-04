from flask import Blueprint, request, jsonify, current_app
from database.connection import db
from database.models import User, Volunteer, PoliceOfficer, OTP
from auth.auth_handler import Auth
from auth.utils import generate_otp, send_otp_email, token_required
from datetime import datetime, timedelta

# Create blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        phone = data.get('phone')
        role = data.get('role', 'public')

        print(f"📧 Registration attempt for: {email}")

        # Validate input
        if not all([email, password, full_name, phone]):
            return jsonify({"error": "All fields are required"}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "User already exists"}), 400

        # Create new user
        new_user = User(
            email=email,
            password_hash=Auth.hash_password(password),
            full_name=full_name,
            phone=phone,
            role=role,
            is_verified=False,
            is_active=True
        )

        db.session.add(new_user)
        db.session.commit()

        # Generate OTP
        otp = generate_otp()
        print(f"🔐 OTP generated for {email}: {otp}")
        
        # Store OTP in database
        otp_record = OTP(
            email=email,
            otp=otp,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.session.add(otp_record)
        db.session.commit()

        # In debug mode, return OTP in response
        if current_app.config.get('DEBUG_MODE', False):
            print(f"🔐 DEBUG OTP for {email}: {otp}")
            return jsonify({
                "message": "Registration successful. OTP sent to email.",
                "debug_mode": True,
                "otp": otp,
                "email": email
            }), 200
        else:
            # Production: send actual email
            try:
                send_otp_email(email, otp)
                print(f"✅ OTP email sent to {email}")
                return jsonify({
                    "message": "Registration successful. OTP sent to email.",
                    "email_sent": True
                }), 200
            except Exception as e:
                print(f"❌ Email sending failed: {e}")
                return jsonify({
                    "message": "Registration successful but email failed. Use debug OTP.",
                    "debug_mode": True,
                    "otp": otp,
                    "email": email,
                    "email_sent": False
                }), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Registration error: {e}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        
        if 'email' not in data or 'otp' not in data:
            return jsonify({"error": "Email and OTP are required"}), 400
        
        email = data['email']
        otp_attempt = data['otp']
        
        print(f"🔍 Verifying OTP for {email}: {otp_attempt}")
        
        # Check OTP in database
        otp_record = OTP.query.filter_by(email=email).order_by(OTP.created_at.desc()).first()
        
        if not otp_record:
            return jsonify({"error": "OTP not found or expired"}), 404
        
        # Check if OTP is expired
        if datetime.utcnow() > otp_record.expires_at:
            db.session.delete(otp_record)
            db.session.commit()
            return jsonify({"error": "OTP expired"}), 400
        
        if otp_record.otp != otp_attempt:
            return jsonify({"error": "Invalid OTP"}), 400
        
        # OTP verified, update user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user.is_verified = True
        db.session.delete(otp_record)  # Remove used OTP
        db.session.commit()
        
        # Generate token
        token = Auth.generate_token(user.id, user.role)
        
        print(f"✅ OTP verified for {email}, user ID: {user.id}")
        
        return jsonify({
            "message": "Account verified successfully",
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_verified": user.is_verified
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ OTP verification error: {e}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print(f"🔑 Login attempt for: {data.get('email')}")
        
        if 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email and password are required"}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        if not Auth.check_password(user.password_hash, data['password']):
            return jsonify({"error": "Invalid credentials"}), 401
        
        if not user.is_active:
            return jsonify({"error": "Account is deactivated"}), 403
        
        # Generate token
        token = Auth.generate_token(user.id, user.role)
        
        print(f"✅ Login successful for {user.email}, role: {user.role}")
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_verified": user.is_verified
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        
        if 'email' not in data:
            return jsonify({"error": "Email is required"}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Generate reset OTP
        reset_otp = generate_otp()
        
        # Store in database
        otp_record = OTP(
            email=data['email'],
            otp=reset_otp,
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            is_reset=True
        )
        db.session.add(otp_record)
        db.session.commit()
        
        # Send reset OTP with fallback
        try:
            if send_otp_email(data['email'], reset_otp):
                return jsonify({"message": "Password reset OTP sent"}), 200
            else:
                return jsonify({
                    "message": "Password reset OTP generated",
                    "otp": reset_otp,
                    "email_sent": False,
                    "debug_mode": True
                }), 200
        except Exception:
            return jsonify({
                "message": "Password reset OTP generated",
                "otp": reset_otp,
                "email_sent": False,
                "debug_mode": True
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        
        required_fields = ['email', 'otp', 'new_password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        email = data['email']
        
        # Check OTP in database
        otp_record = OTP.query.filter_by(email=email, is_reset=True).order_by(OTP.created_at.desc()).first()
        
        if not otp_record:
            return jsonify({"error": "OTP not found or expired"}), 404
        
        # Check OTP expiration
        if datetime.utcnow() > otp_record.expires_at:
            db.session.delete(otp_record)
            db.session.commit()
            return jsonify({"error": "OTP expired"}), 400
        
        if otp_record.otp != data['otp']:
            return jsonify({"error": "Invalid OTP"}), 400
        
        # Update password
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user.password_hash = Auth.hash_password(data['new_password'])
        db.session.delete(otp_record)  # Remove used OTP
        db.session.commit()
        
        return jsonify({"message": "Password reset successful"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user profile"""
    try:
        return jsonify({
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "role": current_user.role,
                "phone": current_user.phone,
                "is_verified": current_user.is_verified,
                "is_active": current_user.is_active
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Test endpoint to verify the blueprint is working
@auth_bp.route('/test', methods=['GET', 'POST'])
def test_auth():
    return jsonify({"message": "Auth blueprint is working!", "method": request.method}), 200