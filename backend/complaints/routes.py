from flask import Blueprint, request, jsonify
from database.connection import db
from database.models import Complaint, User, CaseAssignment, CaseUpdate
from complaints.ai_classifier import classify_complaint, extract_keywords, crime_classifier
from complaints.ai_assigner import case_assigner
from auth.auth_handler import Auth
from auth.utils import token_required
import json
from datetime import datetime

complaints_bp = Blueprint('complaints', __name__)

# Helper function for auto assignment - ADD THIS FUNCTION
def auto_assign_case(complaint):
    """Auto-assign case using AI assigner"""
    try:
        print(f"🤖 Auto-assigning case {complaint.case_id} of type {complaint.crime_type}")
        
        # Use the case_assigner to find the best assignee
        assignee, assignee_type = case_assigner.auto_assign_case(complaint)
        
        if assignee and assignee_type:
            # Create the assignment record in database
            assignment = case_assigner.create_case_assignment(complaint, assignee, assignee_type)
            
            if assignment:
                assignee_name = assignee.user.full_name if assignee.user else "Unknown"
                
                # Determine department based on assignee type and crime type
                if assignee_type == 'police':
                    department_map = {
                        'cyber_crime': 'Cyber Crime Department',
                        'violent_crime': 'Violent Crimes Unit', 
                        'financial_crime': 'Financial Crimes Unit',
                        'drug_crime': 'Narcotics Division',
                        'sexual_offense': 'Special Victims Unit',
                        'missing_person': 'Missing Persons Bureau'
                    }
                    department = department_map.get(complaint.crime_type, 'General Investigations')
                    badge_info = f" (Badge: {assignee.badge_number})" if hasattr(assignee, 'badge_number') and assignee.badge_number else ""
                else:
                    department = 'Community Volunteers'
                    badge_info = ""
                
                return {
                    "assignee_name": f"{assignee_name}{badge_info}",
                    "department": department,
                    "assignee_type": assignee_type,
                    "assignment_id": assignment.id
                }
        
        return None
        
    except Exception as e:
        print(f"❌ Auto-assignment error: {e}")
        return None

@complaints_bp.route('/', methods=['GET'])
@token_required
def get_all_complaints(current_user):
    """Get all complaints (for admin/police)"""
    try:
        # Check if user has permission to view all complaints
        if current_user.role not in ['admin', 'police']:
            return jsonify({"error": "Access denied. Admin or police role required."}), 403
        
        # Get query parameters for filtering
        status = request.args.get('status')
        crime_type = request.args.get('crime_type')
        priority = request.args.get('priority')
        
        # Build query
        query = Complaint.query
        
        if status:
            query = query.filter(Complaint.status == status)
        if crime_type:
            query = query.filter(Complaint.crime_type == crime_type)
        if priority:
            query = query.filter(Complaint.priority == priority)
        
        complaints = query.order_by(Complaint.created_at.desc()).all()
        
        result = []
        for complaint in complaints:
            complaint_data = {
                "case_id": complaint.case_id,
                "title": complaint.title,
                "status": complaint.status,
                "priority": complaint.priority,
                "crime_type": complaint.crime_type,
                "incident_date": complaint.incident_date.isoformat() if complaint.incident_date else None,
                "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
                "location": complaint.location,
                "district": complaint.district,
                "state": complaint.state
            }
            
            # Add user info for admin
            if current_user.role == 'admin':
                complaint_data["user"] = {
                    "name": complaint.user.full_name if complaint.user else "Unknown",
                    "email": complaint.user.email if complaint.user else "Unknown"
                }
            
            result.append(complaint_data)
        
        return jsonify({
            "complaints": result,
            "count": len(complaints),
            "filters": {
                "status": status,
                "crime_type": crime_type,
                "priority": priority
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@complaints_bp.route('/file', methods=['POST'])
@token_required
def file_complaint(current_user):
    try:
        data = request.get_json()
        print(f"📝 Complaint filing attempt by user {current_user.id}")
        
        # Check if this is an anonymous complaint
        is_anonymous = data.get('is_anonymous', False)
        anonymous_email = data.get('anonymous_email')
        
        # For anonymous complaints, user_id can be null or use a system user
        user_id = current_user.id if not is_anonymous else None
        
        # Handle both 'landmark' and 'location' fields for backward compatibility
        location = data.get('location') or data.get('landmark', '')
        
        # Validate required fields
        required_fields = ['title', 'description', 'incident_date', 'state', 'district']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Generate case ID
        case_id = Complaint.generate_case_id()
        print(f"🔍 Generated case ID: {case_id}")
        
        # AI Classification
        crime_type, priority = classify_complaint(data['description'])
        print(f"🤖 AI Classification - Crime: {crime_type}, Priority: {priority}")
        
        # Create complaint
        complaint = Complaint(
            case_id=case_id,
            user_id=user_id,  # Can be null for anonymous
            title=data['title'],
            description=data['description'],
            incident_date=datetime.fromisoformat(data['incident_date'].replace('Z', '+00:00')),
            state=data['state'],
            district=data['district'],
            location=location,
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            crime_type=crime_type,
            sub_category=data.get('sub_category'),
            victim_name=data.get('victim_name'),
            victim_age=data.get('victim_age'),
            victim_gender=data.get('victim_gender'),
            victim_contact=data.get('victim_contact'),
            is_missing_person=data.get('is_missing_person', False),
            is_injury_involved=data.get('is_injury_involved', False),
            is_property_damage=data.get('is_property_damage', False),
            estimated_loss=data.get('estimated_loss'),
            injury_severity=data.get('injury_severity'),
            police_complaint_filed=data.get('police_complaint_filed', False),
            police_station=data.get('police_station'),
            police_complaint_number=data.get('police_complaint_number'),
            police_complaint_date=datetime.fromisoformat(data['police_complaint_date'].replace('Z', '+00:00')) if data.get('police_complaint_date') else None,
            is_anonymous=is_anonymous,
            anonymous_email=anonymous_email,
            priority=priority,
            ai_classification=crime_type,
            confidence_score=0.85,
            keywords=", ".join(extract_keywords(data['description'])),
            evidence_files=data.get('evidence_files'),
            witness_details=data.get('witness_details'),
            suspect_description=data.get('suspect_description')
        )
        
        db.session.add(complaint)
        db.session.commit()
        
        print(f"✅ Complaint saved to database with ID: {complaint.id}")
        print(f"📝 Complaint type: {'Anonymous' if is_anonymous else 'Registered User'}")
        
        # Auto-assign case based on priority and crime type
        assignment_result = auto_assign_case(complaint)
        
        return jsonify({
            "message": "Complaint filed successfully",
            "case_id": case_id,
            "priority": priority,
            "crime_type": crime_type,
            "is_anonymous": is_anonymous,
            "assigned_to": assignment_result.get('assignee_name') if assignment_result else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Complaint filing error: {e}")
        return jsonify({"error": str(e)}), 500

@complaints_bp.route('/file-anonymous', methods=['POST'])
def file_anonymous_complaint():
    """File a complaint without requiring user authentication"""
    try:
        data = request.get_json()
        print("📝 Anonymous complaint filing attempt")
        
        # Validate required fields
        required_fields = ['title', 'description', 'incident_date', 'state', 'district']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Generate case ID
        case_id = Complaint.generate_case_id()
        print(f"🔍 Generated case ID: {case_id}")
        
        # AI Classification
        crime_type, priority = classify_complaint(data['description'])
        print(f"🤖 AI Classification - Crime: {crime_type}, Priority: {priority}")
        
        # Create anonymous complaint
        complaint = Complaint(
            case_id=case_id,
            user_id=None,  # No user associated
            title=data['title'],
            description=data['description'],
            incident_date=datetime.fromisoformat(data['incident_date'].replace('Z', '+00:00')),
            state=data['state'],
            district=data['district'],
            location=data.get('location', ''),
            crime_type=crime_type,
            is_anonymous=True,
            anonymous_email=data.get('anonymous_email'),
            priority=priority,
            ai_classification=crime_type,
            confidence_score=0.85,
            keywords=", ".join(extract_keywords(data['description']))
        )
        
        db.session.add(complaint)
        db.session.commit()
        
        print(f"✅ Anonymous complaint saved with ID: {complaint.id}")
        
        # Auto-assign case
        assignment_result = auto_assign_case(complaint)
        
        return jsonify({
            "message": "Anonymous complaint filed successfully",
            "case_id": case_id,
            "priority": priority,
            "crime_type": crime_type,
            "note": "Please save this case ID for tracking purposes"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Anonymous complaint filing error: {e}")
        return jsonify({"error": str(e)}), 500
    
@complaints_bp.route('/my-complaints', methods=['GET'])
@token_required
def get_my_complaints(current_user):
    try:
        print(f"📋 Getting complaints for user {current_user.id}")
        complaints = Complaint.query.filter_by(user_id=current_user.id).order_by(Complaint.created_at.desc()).all()
        
        result = []
        for complaint in complaints:
            result.append({
                "case_id": complaint.case_id,
                "title": complaint.title,
                "status": complaint.status,
                "priority": complaint.priority,
                "crime_type": complaint.crime_type,
                "incident_date": complaint.incident_date.isoformat() if complaint.incident_date else None,
                "created_at": complaint.created_at.isoformat() if complaint.created_at else None
            })
        
        print(f"✅ Retrieved {len(result)} complaints for user")
        return jsonify({"complaints": result, "total": len(result)}), 200
        
    except Exception as e:
        print(f"❌ Get my complaints error: {e}")
        return jsonify({"error": str(e)}), 500

@complaints_bp.route('/details/<case_id>', methods=['GET'])
@token_required
def get_complaint_details(current_user, case_id):
    try:
        print(f"🔍 Getting details for case: {case_id}")
        complaint = Complaint.query.filter_by(case_id=case_id).first()
        if not complaint:
            return jsonify({"error": "Complaint not found"}), 404
        
        # Check access rights
        if current_user.role == 'public' and complaint.user_id != current_user.id:
            return jsonify({"error": "Access denied"}), 403
        
        # Prepare response data
        complaint_data = {
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
            "victim_name": complaint.victim_name,
            "victim_age": complaint.victim_age,
            "victim_gender": complaint.victim_gender,
            "is_missing_person": complaint.is_missing_person,
            "is_injury_involved": complaint.is_injury_involved,
            "estimated_loss": complaint.estimated_loss,
            "police_complaint_filed": complaint.police_complaint_filed,
            "police_station": complaint.police_station,
            "police_complaint_number": complaint.police_complaint_number,
            "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
            "updated_at": complaint.updated_at.isoformat() if complaint.updated_at else None
        }
        
        # Add assignment info for police/admin
        if current_user.role in ['police', 'admin']:
            assignments = CaseAssignment.query.filter_by(complaint_id=complaint.id).all()
            assignment_data = []
            
            for assignment in assignments:
                assignee_info = {}
                if assignment.police_officer_id and assignment.police_officer:
                    assignee_info = {
                        "type": "police",
                        "name": assignment.police_officer.user.full_name if assignment.police_officer.user else "Unknown",
                        "badge_number": assignment.police_officer.badge_number
                    }
                elif assignment.volunteer_id and assignment.volunteer:
                    assignee_info = {
                        "type": "volunteer",
                        "name": assignment.volunteer.user.full_name if assignment.volunteer.user else "Unknown"
                    }
                
                assignment_data.append({
                    "assignee": assignee_info,
                    "assigned_date": assignment.assigned_date.isoformat() if assignment.assigned_date else None,
                    "status": assignment.status
                })
            
            complaint_data["assignments"] = assignment_data
            
            # Add case updates
            updates = CaseUpdate.query.filter_by(complaint_id=complaint.id).order_by(CaseUpdate.created_at.desc()).all()
            update_data = []
            
            for update in updates:
                update_data.append({
                    "title": update.title,
                    "description": update.description,
                    "update_type": update.update_type,
                    "updated_by": update.updated_by_user.full_name if update.updated_by_user else "System",
                    "created_at": update.created_at.isoformat() if update.created_at else None
                })
            
            complaint_data["updates"] = update_data
        
        print(f"✅ Case details retrieved successfully")
        return jsonify(complaint_data), 200
        
    except Exception as e:
        print(f"❌ Get complaint details error: {e}")
        return jsonify({"error": str(e)}), 500

@complaints_bp.route('/update-status/<case_id>', methods=['PUT'])
@token_required
def update_case_status(current_user, case_id):
    """Update case status (for police/admin)"""
    try:
        if current_user.role not in ['police', 'admin']:
            return jsonify({"error": "Access denied. Police or admin role required."}), 403
        
        data = request.get_json()
        if 'status' not in data:
            return jsonify({"error": "Status is required"}), 400
        
        complaint = Complaint.query.filter_by(case_id=case_id).first()
        if not complaint:
            return jsonify({"error": "Case not found"}), 404
        
        # Update status
        complaint.status = data['status']
        complaint.updated_at = datetime.utcnow()
        
        # If resolved, set resolved date
        if data['status'] == 'resolved':
            complaint.resolved_date = datetime.utcnow()
        
        # Create update record
        update = CaseUpdate(
            complaint_id=complaint.id,
            updated_by=current_user.id,
            update_type='status_change',
            title=f"Status updated to {data['status']}",
            description=data.get('description', f"Case status changed to {data['status']}"),
            internal_notes=data.get('internal_notes')
        )
        
        db.session.add(update)
        db.session.commit()
        
        return jsonify({
            "message": "Case status updated successfully",
            "case_id": case_id,
            "new_status": data['status']
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Add a simple test endpoint
@complaints_bp.route('/test', methods=['GET'])
def test_complaints():
    return jsonify({"message": "Complaints blueprint is working!"}), 200