from datetime import datetime
from database.connection import db
from sqlalchemy import Text, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

def generate_case_id():
    timestamp = datetime.utcnow().strftime('%Y%m%d')
    unique_id = uuid.uuid4().hex[:8].upper()
    return f"IR{timestamp}{unique_id}"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(120), unique=True, nullable=False)
    password_hash = db.Column(String(255), nullable=False)
    full_name = db.Column(String(100), nullable=False)
    phone = db.Column(String(15))
    role = db.Column(String(20), nullable=False)  # 'public', 'volunteer', 'police', 'admin'
    is_verified = db.Column(Boolean, default=False)
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    language = db.Column(String(10), default='en')
    
    # OTP Verification fields
    otp_secret = db.Column(String(255))
    otp_created_at = db.Column(DateTime)
    
    # Relationships - FIXED: Specify foreign_keys to avoid ambiguity
    complaints = relationship('Complaint', backref='user', lazy=True)
    volunteer_profile = relationship('Volunteer', backref='user', uselist=False, lazy=True, foreign_keys='Volunteer.user_id')
    police_profile = relationship('PoliceOfficer', backref='user', uselist=False, lazy=True, foreign_keys='PoliceOfficer.user_id')

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary (exclude sensitive data)"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'language': self.language
        }

    def __repr__(self):
        return f'<User {self.email}>'

class Volunteer(db.Model):
    __tablename__ = 'volunteers'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'), unique=True)
    skills = db.Column(Text)
    qualifications = db.Column(Text)
    experience = db.Column(String(100))
    availability = db.Column(String(50))
    state = db.Column(String(50))
    district = db.Column(String(50))
    pincode = db.Column(String(10))
    address = db.Column(Text)
    date_of_birth = db.Column(DateTime)
    gender = db.Column(String(20))
    id_proof_type = db.Column(String(50))
    id_proof_number = db.Column(String(100))
    id_proof_file = db.Column(String(255))
    background_check = db.Column(Boolean, default=False)
    status = db.Column(String(20), default='pending')  # pending, approved, rejected
    rating = db.Column(Float, default=0.0)
    cases_handled = db.Column(Integer, default=0)
    application_date = db.Column(DateTime, default=datetime.utcnow)
    approved_by = db.Column(Integer, ForeignKey('users.id'))  # Admin who approved
    approved_date = db.Column(DateTime)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    assigned_cases = relationship('CaseAssignment', backref='volunteer', lazy=True)
    admin_approver = relationship('User', foreign_keys=[approved_by])

class PoliceOfficer(db.Model):
    __tablename__ = 'police_officers'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'), unique=True)
    badge_number = db.Column(String(50), unique=True)
    department = db.Column(db.String(100), default='General Department')
    rank = db.Column(db.String(50), default='Officer')
    police_station = db.Column(db.String(100), default='Local Station')
    contact_number = db.Column(db.String(20))
    specialization = db.Column(db.String(100))
    station = db.Column(String(100))
    state = db.Column(String(50))
    district = db.Column(String(50))
    jurisdiction = db.Column(Text)
    is_active = db.Column(Boolean, default=True)
    current_case_load = db.Column(Integer, default=0)
    performance_score = db.Column(Float, default=0.0)
    created_by = db.Column(Integer, ForeignKey('users.id'))  # Admin who created
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    assigned_cases = relationship('CaseAssignment', backref='police_officer', lazy=True)

class Complaint(db.Model):
    __tablename__ = 'complaints'
    
    id = db.Column(Integer, primary_key=True)
    case_id = db.Column(String(50), unique=True, nullable=False, default=generate_case_id)
    user_id = db.Column(Integer, ForeignKey('users.id'))
    
    # Anonymous Reporting
    is_anonymous = db.Column(Boolean, default=False)
    anonymous_email = db.Column(String(120))
    
    # Complaint Details (20 fields as required)
    title = db.Column(String(255), nullable=False)
    description = db.Column(Text, nullable=False)
    incident_date = db.Column(DateTime, nullable=False)
    report_date = db.Column(DateTime, default=datetime.utcnow)
    state = db.Column(String(50), nullable=False)
    district = db.Column(String(50), nullable=False)
    location = db.Column(Text)
    latitude = db.Column(Float)
    longitude = db.Column(Float)
    
    # Crime Type Classification
    crime_type = db.Column(String(100))
    sub_category = db.Column(String(100))
    
    # Victim Information
    victim_name = db.Column(String(100))
    victim_age = db.Column(Integer)
    victim_gender = db.Column(String(20))
    victim_contact = db.Column(String(15))
    
    # Incident Specifics
    is_missing_person = db.Column(Boolean, default=False)
    is_injury_involved = db.Column(Boolean, default=False)
    is_property_damage = db.Column(Boolean, default=False)
    estimated_loss = db.Column(Float)
    injury_severity = db.Column(String(50))
    
    # Police Complaint Details
    police_complaint_filed = db.Column(Boolean, default=False)
    police_station = db.Column(String(100))
    police_complaint_number = db.Column(String(100))
    police_complaint_date = db.Column(DateTime)
    
    # Anonymous Reporting
    is_anonymous = db.Column(Boolean, default=False)
    anonymous_email = db.Column(String(120))
    
    # AI Classification
    priority = db.Column(String(20), default='medium')  # low, medium, high, critical
    ai_classification = db.Column(String(100))
    confidence_score = db.Column(Float)
    keywords = db.Column(Text)
    
    # Status Tracking
    status = db.Column(String(50), default='pending')  # pending, assigned, in_progress, resolved, closed
    resolution = db.Column(Text)
    resolved_date = db.Column(DateTime)
    
    # Additional Fields
    evidence_files = db.Column(Text)  # JSON string of file paths
    witness_details = db.Column(Text)
    suspect_description = db.Column(Text)
    
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assignments = relationship('CaseAssignment', backref='complaint', lazy=True)
    updates = relationship('CaseUpdate', backref='complaint', lazy=True)

class CaseAssignment(db.Model):
    __tablename__ = 'case_assignments'
    
    id = db.Column(Integer, primary_key=True)
    complaint_id = db.Column(Integer, ForeignKey('complaints.id'), nullable=False)
    police_officer_id = db.Column(Integer, ForeignKey('police_officers.id'))
    volunteer_id = db.Column(Integer, ForeignKey('volunteers.id'))
    assigned_by = db.Column(Integer, ForeignKey('users.id'))  # Admin who assigned
    assignment_type = db.Column(String(20))  # 'police', 'volunteer'
    assignment_reason = db.Column(Text)
    assigned_date = db.Column(DateTime, default=datetime.utcnow)
    status = db.Column(String(20), default='active')
    
    assigned_by_user = relationship('User', foreign_keys=[assigned_by])

class CaseUpdate(db.Model):
    __tablename__ = 'case_updates'
    
    id = db.Column(Integer, primary_key=True)
    complaint_id = db.Column(Integer, ForeignKey('complaints.id'), nullable=False)
    updated_by = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    update_type = db.Column(String(50))  # status_change, evidence_added, note_added
    title = db.Column(String(255))
    description = db.Column(Text)
    evidence_files = db.Column(Text)  # JSON string of file paths
    internal_notes = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    updated_by_user = relationship('User', foreign_keys=[updated_by])

class OTPVerification(db.Model):
    __tablename__ = 'otp_verifications'
    
    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(120), nullable=False)
    otp_code = db.Column(String(10), nullable=False)
    purpose = db.Column(String(50), nullable=False)  # 'registration', 'password_reset'
    is_used = db.Column(Boolean, default=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    expires_at = db.Column(DateTime, nullable=False)

class VolunteerApplication(db.Model):
    __tablename__ = 'volunteer_applications'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    skills = db.Column(Text)
    qualifications = db.Column(Text)
    experience = db.Column(String(100))
    availability = db.Column(String(50))
    state = db.Column(String(50))
    district = db.Column(String(50))
    pincode = db.Column(String(10))
    address = db.Column(Text)
    date_of_birth = db.Column(DateTime)
    gender = db.Column(String(20))
    id_proof_type = db.Column(String(50))
    id_proof_number = db.Column(String(100))
    id_proof_file = db.Column(String(255))
    motivation_letter = db.Column(Text)
    status = db.Column(String(20), default='pending')  # pending, approved, rejected
    reviewed_by = db.Column(Integer, ForeignKey('users.id'))  # Admin who reviewed
    review_notes = db.Column(Text)
    applied_date = db.Column(DateTime, default=datetime.utcnow)
    reviewed_date = db.Column(DateTime)
    
    user = relationship('User', foreign_keys=[user_id])
    reviewer = relationship('User', foreign_keys=[reviewed_by])

class Suspect(db.Model):
    __tablename__ = 'suspects'
    
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100))
    alias = db.Column(String(100))
    age = db.Column(Integer)
    gender = db.Column(String(20))
    description = db.Column(Text)
    image_path = db.Column(String(255))
    birthmark = db.Column(Text)
    last_known_location = db.Column(String(255))
    state = db.Column(String(50))
    district = db.Column(String(50))
    danger_level = db.Column(String(20))  # low, medium, high, extreme
    status = db.Column(String(20), default='active')  # active, captured, deceased
    crime_type = db.Column(String(100))
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PhishingReport(db.Model):
    __tablename__ = 'phishing_reports'
    
    id = db.Column(Integer, primary_key=True)
    url = db.Column(Text, nullable=False)
    reported_by = db.Column(Integer, ForeignKey('users.id'))
    analysis_result = db.Column(Text)
    confidence_score = db.Column(Float)
    threat_level = db.Column(String(20))
    is_verified = db.Column(Boolean, default=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)

class LearningMaterial(db.Model):
    __tablename__ = 'learning_materials'
    
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(255), nullable=False)
    content = db.Column(Text, nullable=False)
    category = db.Column(String(100))
    difficulty_level = db.Column(String(20))
    language = db.Column(String(10), default='en')
    is_active = db.Column(Boolean, default=True)
    created_by = db.Column(Integer, ForeignKey('users.id'))
    created_at = db.Column(DateTime, default=datetime.utcnow)

class ChatbotSession(db.Model):
    __tablename__ = 'chatbot_sessions'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'))
    session_id = db.Column(String(100), unique=True)
    context = db.Column(Text)
    language = db.Column(String(10), default='en')
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = relationship('ChatbotMessage', backref='session', lazy=True)

class ChatbotMessage(db.Model):
    __tablename__ = 'chatbot_messages'
    
    id = db.Column(Integer, primary_key=True)
    session_id = db.Column(Integer, ForeignKey('chatbot_sessions.id'))
    message_type = db.Column(String(20))  # user, bot
    content = db.Column(Text)
    timestamp = db.Column(DateTime, default=datetime.utcnow)
    
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # case_update, system, alert, test
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.Text)  # JSON data for additional information
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))
    
    def to_dict(self):
        """Convert notification to dictionary"""
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SMSLog(db.Model):
    __tablename__ = 'sms_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50))  # otp, case_update, bulk_alert, police_alert, test
    status = db.Column(db.String(20))  # sent, failed
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "message": self.message,
            "message_type": self.message_type,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class OTP(db.Model):
    """OTP model for email verification and password reset"""
    __tablename__ = 'otps'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    otp = db.Column(db.String(6), nullable=False)
    is_reset = db.Column(db.Boolean, default=False)  # True for password reset, False for registration
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<OTP {self.email}>'
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at