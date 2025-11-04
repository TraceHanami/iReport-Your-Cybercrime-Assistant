from flask import Blueprint, request, jsonify, send_file
from reports.generator import report_generator
from auth.utils import token_required, admin_required, police_required
import os
import logging

logger = logging.getLogger(__name__)

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/case/<case_id>', methods=['POST'])
@token_required
def generate_case_report(current_user, case_id):
    """Generate PDF report for a case"""
    try:
        from database.models import Complaint
        
        case = Complaint.query.filter_by(case_id=case_id).first()
        if not case:
            return jsonify({"error": "Case not found"}), 404
        
        # FIX: Use current_user.role instead of user_role
        if current_user.role == 'public' and case.user_id != current_user.id:
            return jsonify({"error": "Access denied"}), 403
        
        # For police, check if they are assigned to the case
        if current_user.role == 'police':
            from database.models import PoliceOfficer, CaseAssignment
            police_user = PoliceOfficer.query.filter_by(user_id=current_user.id).first()
            if police_user:
                assignment = CaseAssignment.query.filter_by(
                    complaint_id=case.id,
                    police_officer_id=police_user.id
                ).first()
                if not assignment:
                    return jsonify({"error": "Access denied - not assigned to this case"}), 403
        
        pdf_path = report_generator.generate_case_report(case_id)
        
        return jsonify({
            "message": "Report generated successfully",
            "download_url": f"/api/reports/download/{os.path.basename(pdf_path)}",
            "filename": os.path.basename(pdf_path),
            "case_id": case_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating case report: {e}")
        return jsonify({"error": f"Failed to generate report: {str(e)}"}), 500

@reports_bp.route('/analytics', methods=['POST'])
@admin_required
def generate_analytics_report(current_user):
    """Generate analytics report (Admin only)"""
    try:
        data = request.get_json() or {}
        report_type = data.get('type', 'monthly')
        
        # Validate report type
        valid_types = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']
        if report_type not in valid_types:
            return jsonify({"error": f"Invalid report type. Must be one of: {', '.join(valid_types)}"}), 400
        
        pdf_path = report_generator.generate_analytics_report(report_type)
        
        return jsonify({
            "message": "Analytics report generated successfully",
            "download_url": f"/api/reports/download/{os.path.basename(pdf_path)}",
            "filename": os.path.basename(pdf_path),
            "report_type": report_type
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating analytics report: {e}")
        return jsonify({"error": f"Failed to generate analytics report: {str(e)}"}), 500

@reports_bp.route('/download/<filename>', methods=['GET'])
@token_required
def download_report(current_user, filename):
    """Download generated report"""
    try:
        # Security check - ensure filename is safe
        if '..' in filename or filename.startswith('/'):
            return jsonify({"error": "Invalid filename"}), 400
        
        file_path = os.path.join('reports', filename)
        
        if not os.path.exists(file_path):
            return jsonify({"error": "Report not found"}), 404
        
        # For case reports, verify user has access to the case
        if filename.startswith('case_report_'):
            case_id_part = filename.replace('case_report_', '').split('_')[0]
            from database.models import Complaint
            
            case = Complaint.query.filter_by(case_id=case_id_part).first()
            if case:
                # FIX: Use current_user.role instead of user_role
                if current_user.role == 'public' and case.user_id != current_user.id:
                    return jsonify({"error": "Access denied"}), 403
                
                # For police, check assignment
                if current_user.role == 'police':
                    from database.models import PoliceOfficer, CaseAssignment
                    police_user = PoliceOfficer.query.filter_by(user_id=current_user.id).first()
                    if police_user:
                        assignment = CaseAssignment.query.filter_by(
                            complaint_id=case.id,
                            police_officer_id=police_user.id
                        ).first()
                        if not assignment:
                            return jsonify({"error": "Access denied"}), 403
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        return jsonify({"error": f"Failed to download report: {str(e)}"}), 500

@reports_bp.route('/list', methods=['GET'])
@token_required
def list_reports(current_user):
    """List available reports for the user"""
    try:
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            return jsonify({"reports": []})
        
        reports = []
        for filename in os.listdir(reports_dir):
            if filename.endswith('.pdf'):
                file_path = os.path.join(reports_dir, filename)
                file_stat = os.stat(file_path)
                
                report_info = {
                    "filename": filename,
                    "size": file_stat.st_size,
                    "created": file_stat.st_ctime,
                    "download_url": f"/api/reports/download/{filename}"
                }
                
                # Add type information
                if filename.startswith('case_report_'):
                    report_info["type"] = "case_report"
                    # Extract case ID if possible
                    try:
                        case_id = filename.replace('case_report_', '').split('_')[0]
                        report_info["case_id"] = case_id
                    except:
                        pass
                elif filename.startswith('analytics_report_'):
                    report_info["type"] = "analytics_report"
                
                reports.append(report_info)
        
        # Sort by creation time (newest first)
        reports.sort(key=lambda x: x["created"], reverse=True)
        
        return jsonify({
            "reports": reports,
            "total": len(reports)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        return jsonify({"error": f"Failed to list reports: {str(e)}"}), 500

@reports_bp.route('/cleanup', methods=['POST'])
@admin_required
def cleanup_reports(current_user):
    """Clean up old reports (Admin only)"""
    try:
        import time
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            return jsonify({"message": "No reports directory found", "deleted_count": 0})
        
        current_time = time.time()
        max_age = 7 * 24 * 60 * 60  # 7 days in seconds
        deleted_count = 0
        
        for filename in os.listdir(reports_dir):
            if filename.endswith('.pdf'):
                file_path = os.path.join(reports_dir, filename)
                file_age = current_time - os.path.getctime(file_path)
                
                if file_age > max_age:
                    os.remove(file_path)
                    deleted_count += 1
                    logger.info(f"Deleted old report: {filename}")
        
        return jsonify({
            "message": f"Cleaned up {deleted_count} old reports",
            "deleted_count": deleted_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error cleaning up reports: {e}")
        return jsonify({"error": f"Failed to cleanup reports: {str(e)}"}), 500

@reports_bp.route('/system-status', methods=['GET'])
@admin_required
def system_status(current_user):
    """Get report system status (Admin only)"""
    try:
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            return jsonify({
                "status": "active",
                "reports_dir_exists": False,
                "total_reports": 0,
                "total_size": 0
            })
        
        total_size = 0
        total_reports = 0
        
        for filename in os.listdir(reports_dir):
            if filename.endswith('.pdf'):
                file_path = os.path.join(reports_dir, filename)
                total_size += os.path.getsize(file_path)
                total_reports += 1
        
        return jsonify({
            "status": "active",
            "reports_dir_exists": True,
            "total_reports": total_reports,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({"error": f"Failed to get system status: {str(e)}"}), 500