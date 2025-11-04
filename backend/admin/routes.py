# admin/routes.py - Complete version with all endpoints
from flask import Blueprint, request, jsonify
from database.connection import db
from database.models import User, Complaint, PoliceOfficer, Volunteer, CaseAssignment, CaseUpdate, VolunteerApplication
from auth.auth_handler import Auth
from auth.utils import admin_required, token_required   
from datetime import datetime, timedelta
from sqlalchemy import func, and_

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def admin_dashboard(current_user):
    try:
        # Overall statistics
        total_cases = Complaint.query.count()
        pending_cases = Complaint.query.filter_by(status='pending').count()
        assigned_cases = Complaint.query.filter_by(status='assigned').count()
        in_progress_cases = Complaint.query.filter_by(status='in_progress').count()
        resolved_cases = Complaint.query.filter_by(status='resolved').count()
        
        # Cases by priority
        priority_stats = db.session.query(
            Complaint.priority,
            func.count(Complaint.id)
        ).group_by(Complaint.priority).all()
        
        # Cases by crime type
        crime_stats = db.session.query(
            Complaint.crime_type,
            func.count(Complaint.id)
        ).group_by(Complaint.crime_type).all()
        
        # Recent cases
        recent_cases = Complaint.query.order_by(Complaint.created_at.desc()).limit(10).all()
        
        recent_cases_data = []
        for case in recent_cases:
            recent_cases_data.append({
                "case_id": case.case_id,
                "title": case.title,
                "priority": case.priority,
                "crime_type": case.crime_type,
                "status": case.status,
                "created_at": case.created_at.isoformat() if case.created_at else None
            })
        
        return jsonify({
            "stats": {
                "total_cases": total_cases,
                "pending_cases": pending_cases,
                "assigned_cases": assigned_cases,
                "in_progress_cases": in_progress_cases,
                "resolved_cases": resolved_cases
            },
            "priority_breakdown": {priority: count for priority, count in priority_stats if priority},
            "crime_breakdown": {crime_type: count for crime_type, count in crime_stats if crime_type},
            "recent_cases": recent_cases_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/cases', methods=['GET'])
@admin_required
def get_all_cases(current_user):
    try:
        status_filter = request.args.get('status', 'all')
        priority_filter = request.args.get('priority')
        crime_type_filter = request.args.get('crime_type')
        
        query = Complaint.query
        
        if status_filter != 'all':
            query = query.filter(Complaint.status == status_filter)
        
        if priority_filter:
            query = query.filter(Complaint.priority == priority_filter)
        
        if crime_type_filter:
            query = query.filter(Complaint.crime_type == crime_type_filter)
        
        cases = query.order_by(Complaint.created_at.desc()).all()
        
        cases_data = []
        for complaint in cases:
            # Get assignment info
            assignment = CaseAssignment.query.filter_by(complaint_id=complaint.id).first()
            assigned_to = None
            
            if assignment:
                if assignment.police_officer_id and assignment.police_officer:
                    assigned_to = {
                        "type": "police",
                        "name": assignment.police_officer.user.full_name,
                        "badge_number": assignment.police_officer.badge_number
                    }
                elif assignment.volunteer_id and assignment.volunteer:
                    assigned_to = {
                        "type": "volunteer", 
                        "name": assignment.volunteer.user.full_name
                    }
            
            cases_data.append({
                "id": complaint.id,
                "case_id": complaint.case_id,
                "title": complaint.title,
                "status": complaint.status,
                "priority": complaint.priority,
                "crime_type": complaint.crime_type,
                "state": complaint.state,
                "district": complaint.district,
                "assigned_to": assigned_to,
                "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
                "incident_date": complaint.incident_date.isoformat() if complaint.incident_date else None
            })
        
        return jsonify({"cases": cases_data, "total": len(cases_data)}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/assign-case', methods=['POST'])
@admin_required
def assign_case(current_user):
    """Assign a case to police officer or volunteer"""
    try:
        data = request.get_json()
        print(f"🔍 DEBUG: Assign case data received: {data}")
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Handle both field naming conventions for backward compatibility
        if 'police_officer_id' in data and 'assignee_type' not in data:
            data['assignee_type'] = 'police'
            data['assignee_id'] = data['police_officer_id']
        
        required_fields = ['case_id', 'assignee_type', 'assignee_id']
        for field in required_fields:
            if field not in data or not data[field]:
                print(f"❌ DEBUG: Missing or empty required field: {field}")
                return jsonify({"error": f"Missing or empty required field: {field}"}), 400
        
        case_id = data['case_id']
        assignee_type = data['assignee_type']
        assignee_id = data['assignee_id']
        assignment_reason = data.get('assignment_reason', 'Case assignment')
        
        # Get the case
        case = Complaint.query.filter_by(case_id=case_id).first()
        if not case:
            print(f"❌ DEBUG: Case not found: {case_id}")
            return jsonify({"error": "Case not found"}), 404
        
        # Check if case is already assigned
        existing_assignment = CaseAssignment.query.filter_by(
            complaint_id=case.id,
            status='active'
        ).first()
        
        if existing_assignment:
            print(f"❌ DEBUG: Case already assigned: {existing_assignment.id}")
            assigned_name = "Unknown"
            if existing_assignment.police_officer:
                assigned_name = existing_assignment.police_officer.user.full_name
            elif existing_assignment.volunteer:
                assigned_name = existing_assignment.volunteer.user.full_name
                
            return jsonify({
                "error": "Case is already assigned",
                "current_assignment": {
                    "assigned_to": assigned_name,
                    "assigned_date": existing_assignment.assigned_date.isoformat() if existing_assignment.assigned_date else None
                }
            }), 400
        
        # Validate assignee based on type
        if assignee_type == 'police':
            police_officer = PoliceOfficer.query.get(assignee_id)
            if not police_officer:
                print(f"❌ DEBUG: Police officer not found: {assignee_id}")
                return jsonify({"error": "Police officer not found"}), 404
            if not police_officer.is_active:
                return jsonify({"error": "Police officer is not active"}), 400
                
        elif assignee_type == 'volunteer':
            volunteer = Volunteer.query.get(assignee_id)
            if not volunteer:
                print(f"❌ DEBUG: Volunteer not found: {assignee_id}")
                return jsonify({"error": "Volunteer not found"}), 404
            if volunteer.status != 'approved':
                return jsonify({"error": "Volunteer is not approved"}), 400
        else:
            return jsonify({"error": "Invalid assignee type. Must be 'police' or 'volunteer'"}), 400
        
        # Create new assignment
        assignment = CaseAssignment(
            complaint_id=case.id,
            assignment_type=assignee_type,
            assigned_by=current_user.id,
            assigned_date=datetime.utcnow(),
            assignment_reason=assignment_reason,
            status='active'
        )
        
        if assignee_type == 'police':
            assignment.police_officer_id = assignee_id
        else:
            assignment.volunteer_id = assignee_id
        
        # Update case status
        case.status = 'assigned'
        case.updated_at = datetime.utcnow()
        
        # Create case update record
        case_update = CaseUpdate(
            complaint_id=case.id,
            updated_by=current_user.id,
            update_type='assignment',
            description=f"Case assigned to {assignee_type}: {assignee_id}",
            internal_notes=assignment_reason
        )
        
        db.session.add(assignment)
        db.session.add(case_update)
        db.session.commit()
        
        print(f"✅ DEBUG: Case assigned successfully: {case_id} to {assignee_type} {assignee_id}")
        return jsonify({
            "message": "Case assigned successfully",
            "assignment": {
                "case_id": case_id,
                "assignee_type": assignee_type,
                "assignee_id": assignee_id,
                "assigned_by": current_user.full_name,
                "assigned_date": assignment.assigned_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ DEBUG: Assignment error: {str(e)}")
        return jsonify({"error": f"Failed to assign case: {str(e)}"}), 500

@admin_bp.route('/reassign-case', methods=['POST'])
@admin_required
def reassign_case(current_user):
    """Reassign a case to a different officer or volunteer"""
    try:
        data = request.get_json()
        print(f"🔍 DEBUG: Reassign case data received: {data}")
        
        required_fields = ['case_id', 'new_assignee_type', 'new_assignee_id', 'reassignment_reason']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing or empty required field: {field}"}), 400
        
        case_id = data['case_id']
        new_assignee_type = data['new_assignee_type']
        new_assignee_id = data['new_assignee_id']
        reassignment_reason = data['reassignment_reason']
        
        # Get the case
        case = Complaint.query.filter_by(case_id=case_id).first()
        if not case:
            return jsonify({"error": "Case not found"}), 404
        
        # Get current active assignment
        current_assignment = CaseAssignment.query.filter_by(
            complaint_id=case.id,
            status='active'
        ).first()
        
        if not current_assignment:
            return jsonify({"error": "No active assignment found for this case"}), 400
        
        # Validate new assignee
        if new_assignee_type == 'police':
            new_assignee = PoliceOfficer.query.get(new_assignee_id)
            if not new_assignee:
                return jsonify({"error": "New police officer not found"}), 404
            if not new_assignee.is_active:
                return jsonify({"error": "New police officer is not active"}), 400
                
        elif new_assignee_type == 'volunteer':
            new_assignee = Volunteer.query.get(new_assignee_id)
            if not new_assignee:
                return jsonify({"error": "New volunteer not found"}), 404
            if new_assignee.status != 'approved':
                return jsonify({"error": "New volunteer is not approved"}), 400
        else:
            return jsonify({"error": "Invalid assignee type. Must be 'police' or 'volunteer'"}), 400
        
        # Deactivate current assignment
        current_assignment.status = 'inactive'
        current_assignment.unassigned_date = datetime.utcnow()
        current_assignment.unassigned_by = current_user.id
        current_assignment.unassignment_reason = f"Reassigned to {new_assignee_type} {new_assignee_id}: {reassignment_reason}"
        
        # Create new assignment
        new_assignment = CaseAssignment(
            complaint_id=case.id,
            assignment_type=new_assignee_type,
            assigned_by=current_user.id,
            assigned_date=datetime.utcnow(),
            assignment_reason=reassignment_reason,
            status='active',
            previous_assignment_id=current_assignment.id
        )
        
        if new_assignee_type == 'police':
            new_assignment.police_officer_id = new_assignee_id
        else:
            new_assignment.volunteer_id = new_assignee_id
        
        # Update case status remains 'assigned'
        case.updated_at = datetime.utcnow()
        
        # Create case update record
        case_update = CaseUpdate(
            complaint_id=case.id,
            updated_by=current_user.id,
            update_type='reassignment',
            description=f"Case reassigned from {current_assignment.assignment_type} to {new_assignee_type}",
            internal_notes=reassignment_reason
        )
        
        db.session.add(new_assignment)
        db.session.add(case_update)
        db.session.commit()
        
        print(f"✅ DEBUG: Case reassigned successfully: {case_id} to {new_assignee_type} {new_assignee_id}")
        return jsonify({
            "message": "Case reassigned successfully",
            "reassignment": {
                "case_id": case_id,
                "previous_assignee_type": current_assignment.assignment_type,
                "new_assignee_type": new_assignee_type,
                "new_assignee_id": new_assignee_id,
                "reassigned_by": current_user.full_name,
                "reassigned_date": new_assignment.assigned_date.isoformat(),
                "reason": reassignment_reason
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ DEBUG: Reassignment error: {str(e)}")
        return jsonify({"error": f"Failed to reassign case: {str(e)}"}), 500

@admin_bp.route('/unassign-case', methods=['POST'])
@admin_required
def unassign_case(current_user):
    """Remove assignment from a case"""
    try:
        data = request.get_json()
        print(f"🔍 DEBUG: Unassign case data received: {data}")
        
        if 'case_id' not in data:
            return jsonify({"error": "Missing case_id"}), 400
        
        case_id = data['case_id']
        unassignment_reason = data.get('reason', 'Admin unassignment')
        
        case = Complaint.query.filter_by(case_id=case_id).first()
        if not case:
            return jsonify({"error": "Case not found"}), 404
        
        assignment = CaseAssignment.query.filter_by(
            complaint_id=case.id, 
            status='active'
        ).first()
        
        if not assignment:
            return jsonify({"error": "No active assignment found for this case"}), 400
        
        # Mark assignment as inactive
        assignment.status = 'inactive'
        assignment.unassigned_date = datetime.utcnow()
        assignment.unassigned_by = current_user.id
        assignment.unassignment_reason = unassignment_reason
        
        # Update case status back to pending
        case.status = 'pending'
        case.updated_at = datetime.utcnow()
        
        # Create case update record
        case_update = CaseUpdate(
            complaint_id=case.id,
            updated_by=current_user.id,
            update_type='unassignment',
            description="Case unassigned",
            internal_notes=unassignment_reason
        )
        
        db.session.add(case_update)
        db.session.commit()
        
        print(f"✅ DEBUG: Case unassigned successfully: {case_id}")
        return jsonify({
            "message": "Case unassigned successfully",
            "unassignment": {
                "case_id": case_id,
                "unassigned_by": current_user.full_name,
                "unassigned_date": assignment.unassigned_date.isoformat(),
                "reason": unassignment_reason
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ DEBUG: Unassignment error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users(current_user):
    try:
        role_filter = request.args.get('role')
        
        query = User.query
        
        if role_filter:
            query = query.filter(User.role == role_filter)
        
        users = query.order_by(User.created_at.desc()).all()
        
        users_data = []
        for user in users:
            user_data = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_verified": user.is_verified,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            
            # Add role-specific data
            if user.role == 'police' and user.police_profile:
                user_data["badge_number"] = user.police_profile.badge_number
                user_data["station"] = user.police_profile.station
                user_data["rank"] = user.police_profile.rank
            
            elif user.role == 'volunteer' and user.volunteer_profile:
                user_data["status"] = user.volunteer_profile.status
                user_data["state"] = user.volunteer_profile.state
                user_data["district"] = user.volunteer_profile.district
                user_data["rating"] = user.volunteer_profile.rating
            
            users_data.append(user_data)
        
        return jsonify({"users": users_data, "total": len(users_data)}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/create-police', methods=['POST'])
@admin_required
def create_police_officer(current_user):
    try:
        data = request.get_json()
        
        required_fields = ['email', 'password', 'full_name', 'badge_number', 'station', 'state', 'district']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "User already exists with this email"}), 409
        
        # Check if badge number is unique
        if PoliceOfficer.query.filter_by(badge_number=data['badge_number']).first():
            return jsonify({"error": "Badge number already exists"}), 409
        
        # Create user
        new_user = User(
            email=data['email'],
            password_hash=Auth.hash_password(data['password']),
            full_name=data['full_name'],
            phone=data.get('phone'),
            role='police',
            is_verified=True,
            language=data.get('language', 'en')
        )
        
        db.session.add(new_user)
        db.session.flush()  # Get the user ID
        
        # Create police officer profile
        police_officer = PoliceOfficer(
            user_id=new_user.id,
            badge_number=data['badge_number'],
            rank=data.get('rank', 'Officer'),
            station=data['station'],
            state=data['state'],
            district=data['district'],
            jurisdiction=data.get('jurisdiction'),
            contact_number=data.get('contact_number'),
            created_by=current_user.id
        )
        
        db.session.add(police_officer)
        db.session.commit()
        
        return jsonify({
            "message": "Police officer created successfully",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "role": new_user.role
            },
            "police_officer": {
                "badge_number": police_officer.badge_number,
                "station": police_officer.station,
                "rank": police_officer.rank
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Police creation error: {e}")
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/volunteer-applications', methods=['GET'])
@admin_required
def get_volunteer_applications(current_user):
    try:
        status_filter = request.args.get('status', 'pending')
        
        query = VolunteerApplication.query
        
        if status_filter != 'all':
            query = query.filter(VolunteerApplication.status == status_filter)
        
        applications = query.order_by(VolunteerApplication.applied_date.desc()).all()
        
        applications_data = []
        for app in applications:
            applications_data.append({
                "id": app.id,
                "user_id": app.user_id,
                "full_name": app.user.full_name if app.user else "Unknown",
                "email": app.user.email if app.user else "Unknown",
                "skills": app.skills,
                "qualifications": app.qualifications,
                "experience": app.experience,
                "state": app.state,
                "district": app.district,
                "status": app.status,
                "applied_date": app.applied_date.isoformat() if app.applied_date else None,
                "reviewed_date": app.reviewed_date.isoformat() if app.reviewed_date else None
            })
        
        return jsonify({"applications": applications_data, "total": len(applications_data)}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/volunteer-applications/<int:application_id>/review', methods=['POST'])
@admin_required
def review_volunteer_application(current_user, application_id):
    try:
        data = request.get_json()
        
        application = VolunteerApplication.query.get(application_id)
        if not application:
            return jsonify({"error": "Application not found"}), 404
        
        if 'approve' not in data:
            return jsonify({"error": "Missing approve field"}), 400
        
        if data['approve']:
            # Approve application - convert user to volunteer
            application.status = 'approved'
            application.reviewed_by = current_user.id
            application.reviewed_date = datetime.utcnow()
            application.review_notes = data.get('review_notes', '')
            
            # Update user role
            user = application.user
            user.role = 'volunteer'
            
            # Create volunteer profile
            volunteer = Volunteer(
                user_id=user.id,
                skills=application.skills,
                qualifications=application.qualifications,
                experience=application.experience,
                state=application.state,
                district=application.district,
                address=application.address,
                date_of_birth=application.date_of_birth,
                gender=application.gender,
                id_proof_type=application.id_proof_type,
                id_proof_number=application.id_proof_number,
                id_proof_file=application.id_proof_file,
                status='approved',
                approved_by=current_user.id,
                approved_date=datetime.utcnow()
            )
            
            db.session.add(volunteer)
            message = "Volunteer application approved successfully"
        else:
            # Reject application
            application.status = 'rejected'
            application.reviewed_by = current_user.id
            application.reviewed_date = datetime.utcnow()
            application.review_notes = data.get('review_notes', '')
            message = "Volunteer application rejected"
        
        db.session.commit()
        
        return jsonify({"message": message}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Volunteer review error: {e}")
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/volunteers/pending', methods=['GET'])
@admin_required
def get_pending_volunteers(current_user):
    try:
        pending_volunteers = Volunteer.query.filter_by(status='pending').all()
        
        volunteers_data = []
        for volunteer in pending_volunteers:
            volunteers_data.append({
                "id": volunteer.id,
                "user_id": volunteer.user_id,
                "full_name": volunteer.user.full_name if volunteer.user else "Unknown",
                "email": volunteer.user.email if volunteer.user else "Unknown",
                "skills": volunteer.skills,
                "qualifications": volunteer.qualifications,
                "experience": volunteer.experience,
                "state": volunteer.state,
                "district": volunteer.district,
                "applied_at": volunteer.created_at.isoformat() if volunteer.created_at else None
            })
        
        return jsonify({"volunteers": volunteers_data, "total": len(volunteers_data)}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/volunteers/<int:volunteer_id>/verify', methods=['POST'])
@admin_required
def verify_volunteer(current_user, volunteer_id):
    try:
        data = request.get_json()
        
        volunteer = Volunteer.query.get(volunteer_id)
        if not volunteer:
            return jsonify({"error": "Volunteer not found"}), 404
        
        if data.get('approve', False):
            volunteer.status = 'approved'
            volunteer.background_check = True
            volunteer.approved_by = current_user.id
            volunteer.approved_date = datetime.utcnow()
            message = "Volunteer approved successfully"
        else:
            volunteer.status = 'rejected'
            message = "Volunteer rejected"
        
        db.session.commit()
        
        return jsonify({"message": message}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/police-officers', methods=['GET'])
@admin_required
def get_police_officers(current_user):
    try:
        officers = PoliceOfficer.query.filter_by(is_active=True).all()
        
        officers_data = []
        for officer in officers:
            officers_data.append({
                "id": officer.id,
                "user_id": officer.user_id,
                "name": officer.user.full_name if officer.user else "Unknown",
                "badge_number": officer.badge_number,
                "rank": officer.rank,
                "station": officer.station,
                "state": officer.state,
                "district": officer.district,
                "current_case_load": officer.current_case_load,
                "performance_score": officer.performance_score
            })
        
        return jsonify({"officers": officers_data}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/analytics/overview', methods=['GET'])
@admin_required
def get_analytics_overview(current_user):
    try:
        # Basic analytics implementation
        days = request.args.get('days', 30, type=int)
        
        # Case statistics for the period
        start_date = datetime.utcnow() - timedelta(days=days)
        
        total_cases_period = Complaint.query.filter(Complaint.created_at >= start_date).count()
        resolved_cases_period = Complaint.query.filter(
            Complaint.resolved_date >= start_date
        ).count()
        
        # Cases by status
        status_stats = db.session.query(
            Complaint.status,
            func.count(Complaint.id)
        ).filter(Complaint.created_at >= start_date).group_by(Complaint.status).all()
        
        analytics = {
            "period_days": days,
            "total_cases": total_cases_period,
            "resolved_cases": resolved_cases_period,
            "resolution_rate": round((resolved_cases_period / total_cases_period * 100) if total_cases_period > 0 else 0, 2),
            "status_breakdown": {status: count for status, count in status_stats}
        }
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/analytics/performance', methods=['GET'])
@admin_required
def get_officer_performance(current_user):
    try:
        # Basic officer performance
        officers = PoliceOfficer.query.filter_by(is_active=True).all()
        
        performance_data = []
        for officer in officers:
            # Count assigned cases
            assigned_cases = CaseAssignment.query.filter_by(
                police_officer_id=officer.id,
                status='active'
            ).count()
            
            # Count resolved cases
            resolved_cases = Complaint.query.filter(
                Complaint.id.in_(
                    db.session.query(CaseAssignment.complaint_id).filter_by(
                        police_officer_id=officer.id
                    )
                ),
                Complaint.status == 'resolved'
            ).count()
            
            performance_data.append({
                "officer_id": officer.id,
                "name": officer.user.full_name if officer.user else "Unknown",
                "badge_number": officer.badge_number,
                "station": officer.station,
                "assigned_cases": assigned_cases,
                "resolved_cases": resolved_cases,
                "performance_score": officer.performance_score
            })
        
        return jsonify({"officer_performance": performance_data}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/case-assignments', methods=['GET'])
@admin_required
def get_case_assignments(current_user):
    """Get all case assignments with filters"""
    try:
        status_filter = request.args.get('status', 'active')
        assignee_type_filter = request.args.get('assignee_type')
        
        query = CaseAssignment.query
        
        if status_filter != 'all':
            query = query.filter(CaseAssignment.status == status_filter)
        
        if assignee_type_filter:
            query = query.filter(CaseAssignment.assignment_type == assignee_type_filter)
        
        assignments = query.order_by(CaseAssignment.assigned_date.desc()).all()
        
        assignments_data = []
        for assignment in assignments:
            assignee_name = "Unknown"
            if assignment.police_officer and assignment.police_officer.user:
                assignee_name = assignment.police_officer.user.full_name
            elif assignment.volunteer and assignment.volunteer.user:
                assignee_name = assignment.volunteer.user.full_name
            
            assignments_data.append({
                "id": assignment.id,
                "case_id": assignment.complaint.case_id if assignment.complaint else "Unknown",
                "case_title": assignment.complaint.title if assignment.complaint else "Unknown",
                "assignee_type": assignment.assignment_type,
                "assignee_name": assignee_name,
                "assigned_by": assignment.assigned_by_user.full_name if assignment.assigned_by_user else "Unknown",
                "assigned_date": assignment.assigned_date.isoformat() if assignment.assigned_date else None,
                "status": assignment.status,
                "assignment_reason": assignment.assignment_reason
            })
        
        return jsonify({"assignments": assignments_data, "total": len(assignments_data)}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500