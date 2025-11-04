from flask import Blueprint, request, jsonify
from .indian_sms import indian_sms_service  # Relative import
from auth.utils import token_required, admin_required, police_required
from database.connection import db
from database.models import User, Complaint, SMSLog
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)
sms_bp = Blueprint('sms', __name__)

def validate_phone_number(phone_number):
    """Validate phone number format"""
    # Basic validation for Indian numbers
    pattern = r'^(\+91[\-\s]?)?[6-9]\d{9}$'
    return re.match(pattern, phone_number) is not None

def log_sms_activity(phone_number, message, message_type, status, error_message=None):
    """Log SMS activity to database"""
    try:
        sms_log = SMSLog(
            phone_number=phone_number,
            message=message,
            message_type=message_type,
            status=status,
            error_message=error_message
        )
        db.session.add(sms_log)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to log SMS activity: {e}")
        db.session.rollback()

@sms_bp.route('/status', methods=['GET'])
@token_required
def get_sms_status(current_user):
    """Get SMS service status"""
    try:
        # Get SMS statistics
        total_sent = SMSLog.query.filter_by(status='sent').count()
        total_failed = SMSLog.query.filter_by(status='failed').count()
        
        # Recent activity (last 24 hours)
        yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_sent = SMSLog.query.filter(
            SMSLog.status == 'sent',
            SMSLog.created_at >= yesterday
        ).count()
        
        recent_failed = SMSLog.query.filter(
            SMSLog.status == 'failed', 
            SMSLog.created_at >= yesterday
        ).count()
        
        # Check Fast2SMS configuration
        is_configured = indian_sms_service.is_configured
        
        return jsonify({
            "service_configured": is_configured,
            "service_provider": "Fast2SMS" if is_configured else "Console Fallback",
            "providers_available": {
                "fast2sms": is_configured,
            },
            "statistics": {
                "total_sent": total_sent,
                "total_failed": total_failed,
                "success_rate": round((total_sent / (total_sent + total_failed) * 100) if (total_sent + total_failed) > 0 else 0, 2),
                "recent_sent_24h": recent_sent,
                "recent_failed_24h": recent_failed
            },
            "fast2sms_status": "Configured" if is_configured else "Not configured - using console mode"
        }), 200
        
    except Exception as e:
        logger.error(f"SMS status error: {e}")
        return jsonify({"error": str(e)}), 500

@sms_bp.route('/send-otp', methods=['POST'])
@token_required
def send_otp_sms(current_user):
    """Send OTP via SMS - FIXED VERSION"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        phone_number = data.get('phone_number')
        otp_code = data.get('otp_code')  # Changed from 'message' to 'otp_code'
        
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400
        
        if not otp_code:
            return jsonify({"error": "OTP code is required"}), 400
        
        # Validate phone number
        if not validate_phone_number(phone_number):
            return jsonify({"error": "Invalid phone number format. Use format: +919876543210 or 9876543210"}), 400
        
        # Create the message
        message = f"Your iReport verification code is: {otp_code}. Valid for 10 minutes."
        
        # Send SMS
        success, result = indian_sms_service.send_otp(phone_number, message)
        
        if success:
            # Log the SMS
            sms_log = SMSLog(
                phone_number=phone_number,
                message=message,
                message_type='otp',
                status='sent'
            )
            db.session.add(sms_log)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "OTP SMS sent successfully",
                "details": result,
                "phone_number": phone_number
            }), 200
        else:
            # Log failure
            sms_log = SMSLog(
                phone_number=phone_number,
                message=message,
                message_type='otp',
                status='failed',
                error_message=result
            )
            db.session.add(sms_log)
            db.session.commit()
            
            return jsonify({
                "success": False,
                "error": result,
                "phone_number": phone_number
            }), 400
            
    except Exception as e:
        logger.error(f"Send OTP SMS error: {str(e)}")
        return jsonify({"error": "Failed to send OTP SMS"}), 500
    
@sms_bp.route('/logs', methods=['GET'])
@admin_required
def get_sms_logs(current_user):
    """Get SMS logs (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        message_type = request.args.get('message_type')
        status = request.args.get('status')
        
        query = SMSLog.query
        
        if message_type:
            query = query.filter_by(message_type=message_type)
        
        if status:
            query = query.filter_by(status=status)
        
        logs = query.order_by(SMSLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        logs_data = []
        for log in logs.items:
            logs_data.append({
                "id": log.id,
                "phone_number": log.phone_number,
                "message_type": log.message_type,
                "status": log.status,
                "error_message": log.error_message,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })
        
        return jsonify({
            "logs": logs_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": logs.total,
                "pages": logs.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"SMS logs error: {e}")
        return jsonify({"error": str(e)}), 500

@sms_bp.route('/test', methods=['POST'])
@admin_required
def test_sms_service(current_user):
    """Test SMS service with a test message"""
    try:
        data = request.get_json()
        
        if 'phone_number' not in data:
            return jsonify({"error": "Phone number is required"}), 400
        
        # Validate phone number
        if not validate_phone_number(data['phone_number']):
            return jsonify({"error": "Invalid phone number format"}), 400
        
        test_message = "Test message from iReport system. This confirms SMS service is working properly."
        
        # Use Indian SMS service
        success, result = indian_sms_service.send_otp(data['phone_number'], test_message)
        
        # Log test activity
        log_sms_activity(
            data['phone_number'],
            test_message,
            'test',
            'sent' if success else 'failed',
            None if success else result
        )
        
        if success:
            return jsonify({
                "message": "Test SMS sent successfully",
                "phone_number": data['phone_number'],
                "details": result
            }), 200
        else:
            return jsonify({"error": f"Test SMS failed: {result}"}), 500
            
    except Exception as e:
        logger.error(f"Test SMS error: {e}")
        return jsonify({"error": str(e)}), 500

@sms_bp.route('/test-indian', methods=['POST'])
@token_required
def test_indian_sms(current_user):
    """Test Indian SMS service specifically"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number', '+919876543210')  # Default test number
        
        test_message = "iReport Indian SMS test - service is working!"
        
        success, result = indian_sms_service.send_otp(phone_number, test_message)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Indian SMS test successful",
                "details": result,
                "phone_number": phone_number
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result,
                "phone_number": phone_number
            }), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Simple health check for SMS
@sms_bp.route('/health', methods=['GET'])
def sms_health():
    return jsonify({
        "status": "SMS service is running",
        "provider": "Fast2SMS with console fallback",
        "configured": indian_sms_service.is_configured
    })