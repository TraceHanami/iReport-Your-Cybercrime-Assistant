# police/routes.py - COMPLETE FIXED VERSION
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.connection import db
from database.models import PoliceOfficer, Complaint, CaseAssignment, CaseUpdate, User
from datetime import datetime
import logging

# Create blueprint
police_bp = Blueprint('police', __name__)

# Setup logging
logger = logging.getLogger(__name__)

# Public test endpoint
@police_bp.route('/test-public', methods=['GET'])
def test_public():
    """Public test endpoint to verify police blueprint is accessible"""
    return jsonify({
        "message": "Police blueprint is accessible!",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

# Test endpoint with auth
@police_bp.route('/test', methods=['GET'])
@jwt_required()
def test_auth():
    """Test endpoint with authentication"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        return jsonify({
            "message": "Police authenticated route is working!",
            "user_id": current_user_id,
            "user_role": current_user.role if current_user else "Unknown",
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Police Dashboard
@police_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def police_dashboard():
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
            
        # Check if user is police
        if current_user.role != 'police':
            return jsonify({"error": "Access denied. Police role required."}), 403
            
        police_user = PoliceOfficer.query.filter_by(user_id=current_user.id).first()
        if not police_user:
            return jsonify({"error": "Police officer profile not found"}), 404
        
        # Get assigned cases
        assigned_cases = CaseAssignment.query.filter_by(
            police_officer_id=police_user.id
        ).join(Complaint).order_by(Complaint.created_at.desc()).all()
        
        cases_data = []
        for assignment in assigned_cases:
            complaint = assignment.complaint
            cases_data.append({
                "case_id": complaint.case_id,
                "title": complaint.title,
                "priority": complaint.priority,
                "crime_type": complaint.crime_type,
                "status": complaint.status,
                "incident_date": complaint.incident_date.isoformat() if complaint.incident_date else None,
                "assigned_date": assignment.assigned_date.isoformat() if assignment.assigned_date else None,
                "district": complaint.district,
                "state": complaint.state
            })
        
        # Statistics
        total_cases = len(assigned_cases)
        resolved_cases = Complaint.query.join(CaseAssignment).filter(
            CaseAssignment.police_officer_id == police_user.id,
            Complaint.status == 'resolved'
        ).count()
        
        pending_cases = total_cases - resolved_cases
        
        # High priority cases
        high_priority_cases = Complaint.query.join(CaseAssignment).filter(
            CaseAssignment.police_officer_id == police_user.id,
            Complaint.priority.in_(['high', 'critical']),
            Complaint.status.in_(['assigned', 'in_progress'])
        ).count()
        
        return jsonify({
            "officer": {
                "name": current_user.full_name,
                "badge_number": police_user.badge_number,
                "rank": police_user.rank,
                "station": police_user.station,
                "district": police_user.district,
                "state": police_user.state,
                "performance_score": police_user.performance_score,
                "current_case_load": police_user.current_case_load
            },
            "stats": {
                "total_cases": total_cases,
                "resolved_cases": resolved_cases,
                "pending_cases": pending_cases,
                "high_priority_cases": high_priority_cases,
                "resolution_rate": round((resolved_cases / total_cases * 100) if total_cases > 0 else 0, 2)
            },
            "assigned_cases": cases_data
        }), 200
        
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get Police Cases
@police_bp.route('/cases', methods=['GET'])
@jwt_required()
def get_police_cases():
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
            
        # Check if user is police
        if current_user.role != 'police':
            return jsonify({"error": "Access denied. Police role required."}), 403
            
        police_user = PoliceOfficer.query.filter_by(user_id=current_user.id).first()
        if not police_user:
            return jsonify({"error": "Police officer profile not found"}), 404
        
        status_filter = request.args.get('status', 'all')
        priority_filter = request.args.get('priority')
        crime_type_filter = request.args.get('crime_type')
        
        query = Complaint.query.join(CaseAssignment).filter(
            CaseAssignment.police_officer_id == police_user.id
        )
        
        if status_filter != 'all':
            query = query.filter(Complaint.status == status_filter)
        
        if priority_filter:
            query = query.filter(Complaint.priority == priority_filter)
        
        if crime_type_filter:
            query = query.filter(Complaint.crime_type == crime_type_filter)
        
        cases = query.order_by(Complaint.created_at.desc()).all()
        
        cases_data = []
        for complaint in cases:
            # Get the latest update
            latest_update = CaseUpdate.query.filter_by(
                complaint_id=complaint.id
            ).order_by(CaseUpdate.created_at.desc()).first()
            
            cases_data.append({
                "case_id": complaint.case_id,
                "title": complaint.title,
                "description": complaint.description,
                "status": complaint.status,
                "priority": complaint.priority,
                "crime_type": complaint.crime_type,
                "incident_date": complaint.incident_date.isoformat() if complaint.incident_date else None,
                "victim_name": complaint.victim_name,
                "victim_age": complaint.victim_age,
                "victim_gender": complaint.victim_gender,
                "location": f"{complaint.district}, {complaint.state}",
                "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
                "last_updated": complaint.updated_at.isoformat() if complaint.updated_at else None,
                "latest_update": latest_update.description if latest_update else None
            })
        
        return jsonify({
            "cases": cases_data,
            "total": len(cases_data),
            "filters": {
                "status": status_filter,
                "priority": priority_filter,
                "crime_type": crime_type_filter
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get cases error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Update Case
@police_bp.route('/update-case/<case_id>', methods=['POST'])
@jwt_required()
def update_case(case_id):
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
            
        # Check if user is police
        if current_user.role != 'police':
            return jsonify({"error": "Access denied. Police role required."}), 403
            
        police_user = PoliceOfficer.query.filter_by(user_id=current_user.id).first()
        if not police_user:
            return jsonify({"error": "Police officer profile not found"}), 404
        
        data = request.get_json()
        
        complaint = Complaint.query.filter_by(case_id=case_id).first()
        if not complaint:
            return jsonify({"error": "Case not found"}), 404
        
        # Check if officer is assigned to this case
        assignment = CaseAssignment.query.filter_by(
            complaint_id=complaint.id,
            police_officer_id=police_user.id
        ).first()
        
        if not assignment:
            return jsonify({"error": "Not assigned to this case"}), 403
        
        # Update case status if provided
        if 'status' in data:
            old_status = complaint.status
            complaint.status = data['status']
            complaint.updated_at = datetime.utcnow()
            
            if data['status'] == 'resolved':
                complaint.resolved_date = datetime.utcnow()
        
        # Add case update
        case_update = CaseUpdate(
            complaint_id=complaint.id,
            updated_by=current_user.id,
            update_type=data.get('update_type', 'status_update'),
            title=data.get('title', 'Case Update'),
            description=data.get('description', ''),
            internal_notes=data.get('internal_notes'),
            evidence_files=data.get('evidence_files')
        )
        
        db.session.add(case_update)
        db.session.commit()
        
        return jsonify({
            "message": "Case updated successfully",
            "case_id": case_id,
            "new_status": data.get('status', complaint.status),
            "update_id": case_update.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update case error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get Case Details
@police_bp.route('/case-details/<case_id>', methods=['GET'])
@jwt_required()
def get_case_details(case_id):
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
            
        # Check if user is police
        if current_user.role != 'police':
            return jsonify({"error": "Access denied. Police role required."}), 403
            
        police_user = PoliceOfficer.query.filter_by(user_id=current_user.id).first()
        if not police_user:
            return jsonify({"error": "Police officer profile not found"}), 404
        
        complaint = Complaint.query.filter_by(case_id=case_id).first()
        if not complaint:
            return jsonify({"error": "Case not found"}), 404
        
        # Check if officer is assigned to this case
        assignment = CaseAssignment.query.filter_by(
            complaint_id=complaint.id,
            police_officer_id=police_user.id
        ).first()
        
        if not assignment:
            return jsonify({"error": "Not assigned to this case"}), 403
        
        # Get case updates
        updates = CaseUpdate.query.filter_by(
            complaint_id=complaint.id
        ).order_by(CaseUpdate.created_at.desc()).all()
        
        updates_data = []
        for update in updates:
            updates_data.append({
                "id": update.id,
                "update_type": update.update_type,
                "title": update.title,
                "description": update.description,
                "internal_notes": update.internal_notes,
                "evidence_files": update.evidence_files,
                "updated_by": update.updated_by_user.full_name if update.updated_by_user else "System",
                "created_at": update.created_at.isoformat() if update.created_at else None
            })
        
        case_data = {
            "case_id": complaint.case_id,
            "title": complaint.title,
            "description": complaint.description,
            "status": complaint.status,
            "priority": complaint.priority,
            "crime_type": complaint.crime_type,
            "incident_date": complaint.incident_date.isoformat() if complaint.incident_date else None,
            "state": complaint.state,
            "district": complaint.district,
            "location": complaint.location,
            "latitude": complaint.latitude,
            "longitude": complaint.longitude,
            "victim_name": complaint.victim_name,
            "victim_age": complaint.victim_age,
            "victim_gender": complaint.victim_gender,
            "victim_contact": complaint.victim_contact,
            "is_missing_person": complaint.is_missing_person,
            "is_injury_involved": complaint.is_injury_involved,
            "is_property_damage": complaint.is_property_damage,
            "estimated_loss": complaint.estimated_loss,
            "injury_severity": complaint.injury_severity,
            "police_complaint_filed": complaint.police_complaint_filed,
            "police_station": complaint.police_station,
            "police_complaint_number": complaint.police_complaint_number,
            "witness_details": complaint.witness_details,
            "suspect_description": complaint.suspect_description,
            "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
            "updated_at": complaint.updated_at.isoformat() if complaint.updated_at else None,
            "resolved_date": complaint.resolved_date.isoformat() if complaint.resolved_date else None,
            "updates": updates_data
        }
        
        return jsonify(case_data), 200
        
    except Exception as e:
        logger.error(f"Case details error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get Officer Performance
@police_bp.route('/performance', methods=['GET'])
@jwt_required()
def get_officer_performance():
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
            
        # Check if user is police
        if current_user.role != 'police':
            return jsonify({"error": "Access denied. Police role required."}), 403
            
        police_user = PoliceOfficer.query.filter_by(user_id=current_user.id).first()
        if not police_user:
            return jsonify({"error": "Police officer profile not found"}), 404
        
        # Basic performance calculation
        assigned_cases = CaseAssignment.query.filter_by(police_officer_id=police_user.id).count()
        resolved_cases = Complaint.query.join(CaseAssignment).filter(
            CaseAssignment.police_officer_id == police_user.id,
            Complaint.status == 'resolved'
        ).count()
        
        performance = {
            "officer_id": police_user.id,
            "name": current_user.full_name,
            "badge_number": police_user.badge_number,
            "total_cases": assigned_cases,
            "resolved_cases": resolved_cases,
            "resolution_rate": round((resolved_cases / assigned_cases * 100) if assigned_cases > 0 else 0, 2),
            "performance_score": police_user.performance_score,
            "current_case_load": police_user.current_case_load,
            "station": police_user.station,
            "rank": police_user.rank
        }
        
        return jsonify(performance), 200
        
    except Exception as e:
        logger.error(f"Performance error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get Team Performance
@police_bp.route('/team-performance', methods=['GET'])
@jwt_required()
def get_team_performance():
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
            
        # Check if user is police
        if current_user.role != 'police':
            return jsonify({"error": "Access denied. Police role required."}), 403
            
        police_user = PoliceOfficer.query.filter_by(user_id=current_user.id).first()
        if not police_user:
            return jsonify({"error": "Police officer profile not found"}), 404
        
        # Get team members from same station
        team_officers = PoliceOfficer.query.filter_by(
            station=police_user.station,
            is_active=True
        ).all()
        
        team_data = []
        for officer in team_officers:
            assigned_cases = CaseAssignment.query.filter_by(police_officer_id=officer.id).count()
            resolved_cases = Complaint.query.join(CaseAssignment).filter(
                CaseAssignment.police_officer_id == officer.id,
                Complaint.status == 'resolved'
            ).count()
            
            team_data.append({
                "name": officer.user.full_name if officer.user else "Unknown",
                "badge_number": officer.badge_number,
                "rank": officer.rank,
                "total_cases": assigned_cases,
                "resolved_cases": resolved_cases,
                "resolution_rate": round((resolved_cases / assigned_cases * 100) if assigned_cases > 0 else 0, 2),
                "performance_score": officer.performance_score,
                "current_case_load": officer.current_case_load
            })
        
        return jsonify({
            "station": police_user.station,
            "team_members": len(team_data),
            "performance": team_data
        }), 200
        
    except Exception as e:
        logger.error(f"Team performance error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Update Availability
@police_bp.route('/availability', methods=['PUT'])
@jwt_required()
def update_availability():
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
            
        # Check if user is police
        if current_user.role != 'police':
            return jsonify({"error": "Access denied. Police role required."}), 403
            
        police_user = PoliceOfficer.query.filter_by(user_id=current_user.id).first()
        if not police_user:
            return jsonify({"error": "Police officer profile not found"}), 404
        
        data = request.get_json()
        is_active = data.get('is_active')
        
        if is_active is None:
            return jsonify({"error": "is_active field is required"}), 400
        
        police_user.is_active = bool(is_active)
        police_user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "message": f"Availability updated to {'active' if police_user.is_active else 'inactive'}",
            "is_active": police_user.is_active
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Availability update error: {str(e)}")
        return jsonify({"error": str(e)}), 500