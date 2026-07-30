from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

class Auth:
    @staticmethod
    def generate_token(user_id, role):
        """Generate JWT token"""
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': str(user_id),
            'role': role
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def decode_token(token):
        """Decode JWT token - returns dict with user_id and role"""
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return {
                'user_id': int(payload['sub']),
                'role': payload['role'],
                'exp': payload['exp']
            }
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}
        except jwt.InvalidTokenError as e:
            return {"error": f"Invalid token: {str(e)}"}

    @staticmethod
    def hash_password(password):
        """Hash password using werkzeug security"""
        return generate_password_hash(password)

    @staticmethod
    def check_password(password_hash, password):
        """Check password against hash"""
        return check_password_hash(password_hash, password)