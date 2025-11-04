from database.connection import db
from database.models import Complaint, CaseUpdate
from datetime import datetime

class ComplaintPreview:
    def generate_case_preview(self, complaint_id):
        """Generate a comprehensive case preview for reporting"""
        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            return None
        
        # Get case updates
        updates = CaseUpdate.query.filter_by(
            complaint_id=complaint_id
        ).order_by(CaseUpdate.created_at.desc()).all()
        
        # Generate timeline
        timeline = self.generate_timeline(complaint, updates)
        
        # Generate summary statistics
        statistics = self.generate_statistics(complaint)
        
        preview = {
            'case_overview': {
                'case_id': complaint.case_id,
                'title': complaint.title,
                'status': complaint.status,
                'priority': complaint.priority,
                'crime_type': complaint.crime_type,
                'created_date': complaint.created_at.strftime('%Y-%m-%d'),
                'last_updated': complaint.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            },
            'victim_information': {
                'name': complaint.victim_name,
                'age': complaint.victim_age,
                'gender': complaint.victim_gender,
                'contact': complaint.victim_contact or 'Not provided'
            },
            'incident_details': {
                'date': complaint.incident_date.strftime('%Y-%m-%d %H:%M:%S'),
                'location': f"{complaint.location}, {complaint.district}, {complaint.state}",
                'description': complaint.description,
                'is_missing_person': 'Yes' if complaint.is_missing_person else 'No',
                'is_injury_involved': 'Yes' if complaint.is_injury_involved else 'No',
                'estimated_loss': f"₹{complaint.estimated_loss:,.2f}" if complaint.estimated_loss else 'Not specified'
            },
            'police_information': {
                'filed': 'Yes' if complaint.police_complaint_filed else 'No',
                'station': complaint.police_station or 'Not specified',
                'complaint_number': complaint.police_complaint_number or 'Not assigned',
                'filing_date': complaint.police_complaint_date.strftime('%Y-%m-%d') if complaint.police_complaint_date else 'Not filed'
            },
            'timeline': timeline,
            'statistics': statistics,
            'report_generated': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return preview
    
    def generate_timeline(self, complaint, updates):
        """Generate case timeline"""
        timeline = []
        
        # Case creation
        timeline.append({
            'event': 'Case Created',
            'description': 'Complaint filed through iReport system',
            'timestamp': complaint.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'type': 'system'
        })
        
        # Case assignment if assigned
        if complaint.status != 'pending':
            assignment_event = {
                'event': 'Case Assigned',
                'description': f'Case assigned for investigation',
                'timestamp': complaint.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'assignment'
            }
            timeline.append(assignment_event)
        
        # Case updates
        for update in updates:
            timeline.append({
                'event': update.title,
                'description': update.description,
                'timestamp': update.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'type': update.update_type,
                'updated_by': update.updated_by_user.full_name if update.updated_by_user else 'System'
            })
        
        # Case resolution if resolved
        if complaint.status == 'resolved' and complaint.resolved_date:
            timeline.append({
                'event': 'Case Resolved',
                'description': complaint.resolution or 'Case successfully resolved',
                'timestamp': complaint.resolved_date.strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'resolution'
            })
        
        # Sort timeline by timestamp
        timeline.sort(key=lambda x: x['timestamp'], reverse=True)
        return timeline
    
    def generate_statistics(self, complaint):
        """Generate case statistics"""
        time_to_assignment = None
        if complaint.status != 'pending':
            # Find assignment time (simplified)
            assignment_updates = CaseUpdate.query.filter_by(
                complaint_id=complaint.id,
                update_type='assignment'
            ).first()
            
            if assignment_updates:
                time_to_assignment = (assignment_updates.created_at - complaint.created_at).total_seconds() / 3600  # hours
        
        current_duration = (datetime.utcnow() - complaint.created_at).total_seconds() / 86400  # days
        
        return {
            'days_since_filing': round(current_duration, 2),
            'hours_to_assignment': round(time_to_assignment, 2) if time_to_assignment else 'Not assigned',
            'update_count': CaseUpdate.query.filter_by(complaint_id=complaint.id).count(),
            'priority_level': complaint.priority,
            'confidence_score': f"{complaint.confidence_score * 100:.1f}%" if complaint.confidence_score else 'Not available'
        }
    
    def generate_public_preview(self, case_id):
        """Generate public-facing case preview (limited information)"""
        complaint = Complaint.query.filter_by(case_id=case_id).first()
        if not complaint:
            return None
        
        return {
            'case_id': complaint.case_id,
            'status': complaint.status,
            'priority': complaint.priority,
            'crime_type': complaint.crime_type,
            'district': complaint.district,
            'state': complaint.state,
            'created_date': complaint.created_at.strftime('%Y-%m-%d'),
            'last_updated': complaint.updated_at.strftime('%Y-%m-%d'),
            'updates_count': CaseUpdate.query.filter_by(complaint_id=complaint.id).count()
        }

# Global preview generator
complaint_preview = ComplaintPreview()