from flask import Blueprint, request, jsonify
from database.connection import db
from database.models import Complaint, User, CaseAssignment, CaseUpdate, PoliceOfficer, Volunteer
from auth.utils import token_required
from datetime import datetime
import logging

# Create the blueprint
track_bp = Blueprint('track', __name__)

logger = logging.getLogger(__name__)

# Helper function to safely get police officer attributes
def get_police_officer_info(police_officer):
    """Safely get police officer information with fallbacks for missing attributes"""
    if not police_officer:
        return {}
    
    try:
        user_info = police_officer.user
        return {
            "name": user_info.full_name if user_info else "Unknown Officer",
            "badge_number": getattr(police_officer, 'badge_number', 'N/A'),
            "department": getattr(police_officer, 'department', 'General Department'),
            "rank": getattr(police_officer, 'rank', 'Officer'),
            "station": getattr(police_officer, 'police_station', 'Local Station'),
            "contact_number": getattr(police_officer, 'contact_number', 'N/A')
        }
    except Exception as e:
        logger.error(f"Error getting police officer info: {e}")
        return {
            "name": "Unknown Officer",
            "badge_number": "N/A",
            "department": "General Department",
            "rank": "Officer",
            "station": "Local Station",
            "contact_number": "N/A"
        }

# Helper function to safely get volunteer attributes
def get_volunteer_info(volunteer):
    """Safely get volunteer information with fallbacks for missing attributes"""
    if not volunteer:
        return {}
    
    try:
        user_info = volunteer.user
        return {
            "name": user_info.full_name if user_info else "Unknown Volunteer",
            "specialization": getattr(volunteer, 'specialization', 'General'),
            "experience_level": getattr(volunteer, 'experience_level', 'Beginner'),
            "contact_number": getattr(volunteer, 'contact_number', 'N/A'),
            "availability": getattr(volunteer, 'availability', 'Unknown')
        }
    except Exception as e:
        logger.error(f"Error getting volunteer info: {e}")
        return {
            "name": "Unknown Volunteer",
            "specialization": "General",
            "experience_level": "Beginner",
            "contact_number": "N/A",
            "availability": "Unknown"
        }

@track_bp.route('/status/<case_id>', methods=['GET'])
def track_complaint(case_id):
    """Track complaint status (public access - no authentication required)"""
    try:
        logger.info(f"🔍 Tracking case: {case_id}")
        
        # Find complaint by case_id
        complaint = Complaint.query.filter_by(case_id=case_id).first()
        if not complaint:
            return jsonify({
                "success": False,
                "error": "Case not found"
            }), 404
        
        # Basic complaint info (publicly accessible)
        complaint_data = {
            "case_id": complaint.case_id,
            "title": complaint.title,
            "status": complaint.status,
            "priority": complaint.priority,
            "crime_type": complaint.crime_type,
            "incident_date": complaint.incident_date.isoformat() if complaint.incident_date else None,
            "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
            "updated_at": complaint.updated_at.isoformat() if complaint.updated_at else None,
            "state": complaint.state,
            "district": complaint.district,
            "location": complaint.location
        }
        
        # Add assignment info if available (with safe attribute access)
        assignments = CaseAssignment.query.filter_by(complaint_id=complaint.id).all()
        if assignments:
            assignment_data = []
            for assignment in assignments:
                assignee_info = {}
                if assignment.police_officer_id and assignment.police_officer:
                    police_info = get_police_officer_info(assignment.police_officer)
                    assignee_info = {
                        "type": "police",
                        "name": police_info.get("name", "Police Officer"),
                        "badge_number": police_info.get("badge_number", "N/A"),
                        "department": police_info.get("department", "General Department")
                    }
                elif assignment.volunteer_id and assignment.volunteer:
                    volunteer_info = get_volunteer_info(assignment.volunteer)
                    assignee_info = {
                        "type": "volunteer", 
                        "name": volunteer_info.get("name", "Community Volunteer"),
                        "specialization": volunteer_info.get("specialization", "General")
                    }
                
                assignment_data.append({
                    "assignee": assignee_info,
                    "assigned_date": assignment.assigned_date.isoformat() if assignment.assigned_date else None,
                    "status": assignment.status,
                    # FIX: Use getattr to safely access notes attribute
                    "notes": getattr(assignment, 'notes', 'No notes available')
                })
            
            complaint_data["assignments"] = assignment_data
        
        # Add public updates (non-sensitive ones)
        updates = CaseUpdate.query.filter_by(
            complaint_id=complaint.id
        ).filter(
            CaseUpdate.update_type.in_(['status_change', 'public_update', 'general_update'])
        ).order_by(CaseUpdate.created_at.desc()).limit(10).all()
        
        update_data = []
        for update in updates:
            update_data.append({
                "title": update.title,
                "description": update.description,
                "update_type": update.update_type,
                "created_at": update.created_at.isoformat() if update.created_at else None
            })
        
        complaint_data["updates"] = update_data
        
        logger.info(f"✅ Case tracking data retrieved for: {case_id}")
        return jsonify({
            "success": True,
            "data": complaint_data
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Track complaint error: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to track complaint",
            "message": str(e)
        }), 500
        
@track_bp.route('/details/<case_id>', methods=['GET'])
@token_required
def get_tracking_details(current_user, case_id):
    """Get detailed tracking info (requires authentication)"""
    try:
        logger.info(f"🔍 Getting detailed tracking for case: {case_id} by user {current_user.id}")
        
        complaint = Complaint.query.filter_by(case_id=case_id).first()
        if not complaint:
            return jsonify({
                "success": False,
                "error": "Case not found"
            }), 404
        
        # Check access rights
        if current_user.role == 'public' and complaint.user_id != current_user.id:
            return jsonify({
                "success": False,
                "error": "Access denied. You can only view your own cases."
            }), 403
        
        # Detailed complaint info
        complaint_data = {
            "case_id": complaint.case_id,
            "title": complaint.title,
            "description": complaint.description,
            "status": complaint.status,
            "priority": complaint.priority,
            "crime_type": complaint.crime_type,
            "ai_classification": complaint.ai_classification,
            "confidence_score": complaint.confidence_score,
            "incident_date": complaint.incident_date.isoformat() if complaint.incident_date else None,
            "state": complaint.state,
            "district": complaint.district,
            "location": complaint.location,
            "latitude": complaint.latitude,
            "longitude": complaint.longitude,
            "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
            "updated_at": complaint.updated_at.isoformat() if complaint.updated_at else None,
            "resolved_date": complaint.resolved_date.isoformat() if complaint.resolved_date else None,
            "is_anonymous": complaint.is_anonymous,
            "keywords": complaint.keywords
        }
        
        # Add victim information if available
        if complaint.victim_name:
            complaint_data["victim_info"] = {
                "name": complaint.victim_name,
                "age": complaint.victim_age,
                "gender": complaint.victim_gender,
                "contact": complaint.victim_contact
            }
        
        # Add incident details
        complaint_data["incident_details"] = {
            "is_missing_person": complaint.is_missing_person,
            "is_injury_involved": complaint.is_injury_involved,
            "is_property_damage": complaint.is_property_damage,
            "estimated_loss": complaint.estimated_loss,
            "injury_severity": complaint.injury_severity
        }
        
        # Add police complaint info if filed
        if complaint.police_complaint_filed:
            complaint_data["police_complaint"] = {
                "police_station": complaint.police_station,
                "complaint_number": complaint.police_complaint_number,
                "complaint_date": complaint.police_complaint_date.isoformat() if complaint.police_complaint_date else None
            }
        
        # Assignment details (with safe attribute access)
        assignments = CaseAssignment.query.filter_by(complaint_id=complaint.id).all()
        assignment_data = []
        
        for assignment in assignments:
            assignee_info = {}
            contact_info = {}
            
            if assignment.police_officer_id and assignment.police_officer:
                police_info = get_police_officer_info(assignment.police_officer)
                assignee_info = {
                    "type": "police",
                    "id": assignment.police_officer.id,
                    "name": police_info.get("name", "Unknown Officer"),
                    "badge_number": police_info.get("badge_number", "N/A"),
                    "department": police_info.get("department", "General Department"),
                    "rank": police_info.get("rank", "Officer"),
                    "specialization": getattr(assignment.police_officer, 'specialization', 'General')
                }
                contact_info = {
                    "station": police_info.get("station", "Local Station"),
                    "contact_number": police_info.get("contact_number", "N/A")
                }
            elif assignment.volunteer_id and assignment.volunteer:
                volunteer_info = get_volunteer_info(assignment.volunteer)
                assignee_info = {
                    "type": "volunteer",
                    "id": assignment.volunteer.id,
                    "name": volunteer_info.get("name", "Unknown Volunteer"),
                    "specialization": volunteer_info.get("specialization", "General"),
                    "experience_level": volunteer_info.get("experience_level", "Beginner")
                }
                contact_info = {
                    "contact_number": volunteer_info.get("contact_number", "N/A"),
                    "availability": volunteer_info.get("availability", "Unknown")
                }
            
            assignment_data.append({
                "id": assignment.id,
                "assignee": assignee_info,
                "contact": contact_info,
                "assigned_date": assignment.assigned_date.isoformat() if assignment.assigned_date else None,
                "status": assignment.status,
                "notes": getattr(assignment, 'notes', 'No notes available'),
            })
        
        complaint_data["assignments"] = assignment_data
        
        # All case updates
        updates = CaseUpdate.query.filter_by(complaint_id=complaint.id).order_by(CaseUpdate.created_at.desc()).all()
        update_data = []
        
        for update in updates:
            updater_info = {
                "name": update.updated_by_user.full_name if update.updated_by_user else "System",
                "role": update.updated_by_user.role if update.updated_by_user else "system"
            }
            
            update_data.append({
                "id": update.id,
                "title": update.title,
                "description": update.description,
                "update_type": update.update_type,
                "updated_by": updater_info,
                "created_at": update.created_at.isoformat() if update.created_at else None,
                "internal_notes": update.internal_notes if current_user.role in ['admin', 'police'] else None
            })
        
        complaint_data["updates"] = update_data
        
        # Evidence files and witness details
        if complaint.evidence_files:
            complaint_data["evidence"] = {
                "files": complaint.evidence_files,
                "witness_details": complaint.witness_details,
                "suspect_description": complaint.suspect_description
            }
        
        logger.info(f"✅ Detailed tracking data retrieved for: {case_id}")
        return jsonify({
            "success": True,
            "data": complaint_data
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Get tracking details error: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get tracking details",
            "message": str(e)
        }), 500

@track_bp.route('/test', methods=['GET'])
def test_tracking():
    """Test endpoint for tracking blueprint"""
    return jsonify({
        "success": True,
        "message": "Tracking blueprint is working!",
        "endpoints": {
            "track_status": "GET /api/track/status/<case_id>",
            "track_details": "GET /api/track/details/<case_id>",
            "update_location": "POST /api/track/update-location/<case_id>",
            "add_update": "POST /api/track/add-update/<case_id>",
            "assignment_status": "PUT /api/track/assignment-status/<case_id>",
            "timeline": "GET /api/track/timeline/<case_id>",
            "search": "GET /api/track/search",
            "stats": "GET /api/track/stats/<case_id>"
        }
    }), 200

@track_bp.route('/', methods=['GET'])
def track_home():
    """Tracking system home endpoint"""
    return jsonify({
        "success": True,
        "message": "Case Tracking System",
        "description": "Track and manage case progress with real-time updates",
        "version": "1.0",
        "endpoints": {
            "public_tracking": "GET /api/track/status/{case_id}",
            "detailed_tracking": "GET /api/track/details/{case_id} (Auth Required)",
            "case_search": "GET /api/track/search?case_id=&status=&crime_type=&location=",
            "case_timeline": "GET /api/track/timeline/{case_id} (Auth Required)",
            "case_statistics": "GET /api/track/stats/{case_id} (Auth Required)"
        }
    }), 200