from flask import Blueprint, request, jsonify
from notifications.socket_manager import notification_manager
from database.connection import db
from database.models import User, Notification
from auth.utils import token_required
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/user', methods=['GET'])
@token_required
def get_user_notifications(current_user):
    """Get user's notifications"""
    try:
        # Get query parameters
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 50))
        
        query = Notification.query.filter_by(user_id=current_user.id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
        
        result = []
        for notification in notifications:
            result.append({
                'id': notification.id,
                'type': notification.type,
                'title': notification.title,
                'message': notification.message,
                'data': notification.data,
                'is_read': notification.is_read,
                'read_at': notification.read_at.isoformat() if notification.read_at else None,
                'created_at': notification.created_at.isoformat() if notification.created_at else None
            })
        
        # Get unread count
        unread_count = Notification.query.filter_by(
            user_id=current_user.id, 
            is_read=False
        ).count()
        
        return jsonify({
            "notifications": result,
            "unread_count": unread_count,
            "total": len(result)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
@token_required
def mark_notification_read(current_user, notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id
        ).first()
        
        if not notification:
            return jsonify({"error": "Notification not found"}), 404
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "message": "Notification marked as read",
            "notification_id": notification_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('/read-all', methods=['PUT'])
@token_required
def mark_all_notifications_read(current_user):
    """Mark all user notifications as read"""
    try:
        updated_count = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).update({
            'is_read': True, 
            'read_at': datetime.utcnow()
        })
        
        db.session.commit()
        
        return jsonify({
            "message": f"Marked {updated_count} notifications as read",
            "updated_count": updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@token_required
def delete_notification(current_user, notification_id):
    """Delete a notification"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id
        ).first()
        
        if not notification:
            return jsonify({"error": "Notification not found"}), 404
        
        db.session.delete(notification)
        db.session.commit()
        
        return jsonify({
            "message": "Notification deleted successfully",
            "notification_id": notification_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('/clear-all', methods=['DELETE'])
@token_required
def clear_all_notifications(current_user):
    """Clear all user notifications"""
    try:
        deleted_count = Notification.query.filter_by(
            user_id=current_user.id
        ).delete()
        
        db.session.commit()
        
        return jsonify({
            "message": f"Cleared {deleted_count} notifications",
            "deleted_count": deleted_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('/test', methods=['POST'])
@token_required
def test_notification(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        title = data.get('title', 'Test Notification')
        message = data.get('message', 'This is a test notification')
        notification_type = data.get('type', 'test')
        
        # Create notification
        notification = Notification(
            user_id=current_user.id,
            type=notification_type,
            title=title,
            message=message,
            data=json.dumps({"test": True}),
            is_read=False
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Test notification created",
            "notification": notification.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Test notification error: {str(e)}")
        return jsonify({"error": "Failed to create test notification"}), 500
    
@notifications_bp.route('/stats', methods=['GET'])
@token_required
def get_notification_stats(current_user):
    """Get notification statistics for user"""
    try:
        total_notifications = Notification.query.filter_by(
            user_id=current_user.id
        ).count()
        
        unread_notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).count()
        
        # Count by type
        type_counts = db.session.query(
            Notification.type,
            db.func.count(Notification.id)
        ).filter(
            Notification.user_id == current_user.id
        ).group_by(Notification.type).all()
        
        return jsonify({
            "stats": {
                "total": total_notifications,
                "unread": unread_notifications,
                "read": total_notifications - unread_notifications,
                "by_type": dict(type_counts)
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500