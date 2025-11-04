from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from datetime import datetime
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

socketio = SocketIO(cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"])

class NotificationManager:
    def __init__(self):
        self.user_connections = {}  # user_id -> list of socket_ids
    
    def init_app(self, app):
        socketio.init_app(app)
        self.setup_handlers()
        logger.info("Notification manager initialized")
    
    def setup_handlers(self):
        @socketio.on('connect')
        def handle_connect():
            logger.info(f"Client connected: {request.sid}")
            emit('connected', {'message': 'Connected to notification server', 'sid': request.sid})
        
        @socketio.on('disconnect')
        def handle_disconnect():
            user_id = None
            for uid, sids in self.user_connections.items():
                if request.sid in sids:
                    user_id = uid
                    sids.remove(request.sid)
                    if not sids:  # Remove user if no more connections
                        del self.user_connections[uid]
                    break
            logger.info(f"Client disconnected: {request.sid}, User: {user_id}")
        
        @socketio.on('join_user')
        def handle_join_user(data):
            try:
                user_id = data.get('user_id')
                token = data.get('token')
                
                if not user_id:
                    emit('error', {'message': 'User ID is required'})
                    return
                
                # TODO: Validate token here if needed
                
                # Remove from any previous rooms
                for room in request.rooms:
                    if room != request.sid:  # Don't leave default room
                        leave_room(room)
                
                # Join user room
                join_room(str(user_id))
                
                # Track connection
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = []
                
                if request.sid not in self.user_connections[user_id]:
                    self.user_connections[user_id].append(request.sid)
                
                logger.info(f"User {user_id} joined notification room with SID: {request.sid}")
                emit('joined', {
                    'message': f'Joined notification room for user {user_id}',
                    'user_id': user_id,
                    'connections_count': len(self.user_connections[user_id])
                })
                
            except Exception as e:
                logger.error(f"Error joining user room: {e}")
                emit('error', {'message': 'Failed to join notification room'})
        
        @socketio.on('leave_user')
        def handle_leave_user(data):
            user_id = data.get('user_id')
            if user_id:
                leave_room(str(user_id))
                if user_id in self.user_connections and request.sid in self.user_connections[user_id]:
                    self.user_connections[user_id].remove(request.sid)
                    if not self.user_connections[user_id]:
                        del self.user_connections[user_id]
                logger.info(f"User {user_id} left notification room")
        
        @socketio.on('case_update')
        def handle_case_update(data):
            try:
                case_id = data.get('case_id')
                message = data.get('message')
                user_id = data.get('user_id')  # Optional: specific user to notify
                
                if user_id:
                    self.send_user_notification(
                        user_id,
                        'case_update',
                        'Case Updated',
                        message,
                        {'case_id': case_id, 'action': 'update'}
                    )
                else:
                    self.send_case_notification(case_id, message)
                    
            except Exception as e:
                logger.error(f"Error handling case update: {e}")
        
        @socketio.on('ping')
        def handle_ping():
            emit('pong', {'timestamp': datetime.utcnow().isoformat()})
    
    def send_user_notification(self, user_id, notification_type, title, message, data=None):
        """Send notification to specific user"""
        try:
            user_id_str = str(user_id)
            
            # Create notification payload
            notification = {
                'id': f"notif_{datetime.utcnow().timestamp()}",
                'type': notification_type,
                'title': title,
                'message': message,
                'data': data or {},
                'timestamp': datetime.utcnow().isoformat(),
                'read': False
            }
            
            # Send via Socket.IO
            if user_id_str in self.user_connections:
                emit('notification', notification, room=user_id_str)
                logger.info(f"Real-time notification sent to user {user_id}: {title}")
            
            # Also store in database
            self.create_database_notification(user_id, notification_type, title, message, data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending user notification: {e}")
            return False
    
    def send_case_notification(self, case_id, message, notification_type='case_update'):
        """Send notification to all users involved in a case"""
        try:
            from database.models import Complaint, CaseAssignment
            from database.connection import db
            
            with db.app.app_context():
                case = Complaint.query.filter_by(case_id=case_id).first()
                if not case:
                    logger.warning(f"Case {case_id} not found for notification")
                    return
                
                # Notify complainant
                self.send_user_notification(
                    case.user_id,
                    notification_type,
                    'Case Update',
                    f"Your case '{case.title}' has been updated: {message}",
                    {'case_id': case_id, 'case_title': case.title, 'action': 'update'}
                )
                
                # Notify assigned officers/volunteers
                assignments = CaseAssignment.query.filter_by(complaint_id=case.id).all()
                for assignment in assignments:
                    if assignment.police_officer_id and assignment.police_officer:
                        officer = assignment.police_officer
                        self.send_user_notification(
                            officer.user_id,
                            notification_type,
                            'Case Assignment Update',
                            f"Case '{case.title}' has been updated: {message}",
                            {'case_id': case_id, 'case_title': case.title, 'action': 'update'}
                        )
                    elif assignment.volunteer_id and assignment.volunteer:
                        volunteer = assignment.volunteer
                        self.send_user_notification(
                            volunteer.user_id,
                            notification_type,
                            'Case Assignment Update', 
                            f"Case '{case.title}' has been updated: {message}",
                            {'case_id': case_id, 'case_title': case.title, 'action': 'update'}
                        )
                
                logger.info(f"Case notifications sent for case {case_id}")
                
        except Exception as e:
            logger.error(f"Error sending case notifications: {e}")
    
    def create_database_notification(self, user_id, notification_type, title, message, data=None):
        """Create notification record in database"""
        try:
            from database.models import Notification
            from database.connection import db
            
            with db.app.app_context():
                notification = Notification(
                    user_id=user_id,
                    type=notification_type,
                    title=title,
                    message=message,
                    data=json.dumps(data) if data else None
                )
                
                db.session.add(notification)
                db.session.commit()
                logger.info(f"Database notification created for user {user_id}: {title}")
                
        except Exception as e:
            logger.error(f"Error creating database notification: {e}")
    
    def get_connection_stats(self):
        """Get connection statistics"""
        total_connections = sum(len(sids) for sids in self.user_connections.values())
        connected_users = len(self.user_connections)
        
        return {
            'total_connections': total_connections,
            'connected_users': connected_users,
            'user_connections': self.user_connections
        }
    
    def broadcast_system_notification(self, title, message, data=None):
        """Broadcast notification to all connected users"""
        try:
            notification = {
                'id': f"system_{datetime.utcnow().timestamp()}",
                'type': 'system',
                'title': title,
                'message': message,
                'data': data or {},
                'timestamp': datetime.utcnow().isoformat(),
                'read': False
            }
            
            emit('notification', notification, broadcast=True)
            logger.info(f"System broadcast notification: {title}")
            
        except Exception as e:
            logger.error(f"Error broadcasting system notification: {e}")

# Global notification manager instance
notification_manager = NotificationManager()