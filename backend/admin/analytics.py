from database.connection import db
from database.models import Complaint, User, PoliceOfficer, Volunteer, CaseAssignment
from sqlalchemy import func, and_, case
from datetime import datetime, timedelta
from auth.utils import admin_required  

class AnalyticsEngine:
    def __init__(self):
        pass
    
    def get_case_analytics(self, days=30):
        """Get comprehensive case analytics"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Cases by status
            status_stats = db.session.query(
                Complaint.status,
                func.count(Complaint.id)
            ).filter(
                Complaint.created_at >= start_date
            ).group_by(Complaint.status).all()
            
            # Cases by priority
            priority_stats = db.session.query(
                Complaint.priority,
                func.count(Complaint.id)
            ).filter(
                Complaint.created_at >= start_date
            ).group_by(Complaint.priority).all()
            
            # Cases by crime type
            crime_stats = db.session.query(
                Complaint.crime_type,
                func.count(Complaint.id)
            ).filter(
                Complaint.created_at >= start_date
            ).group_by(Complaint.crime_type).all()
            
            # Daily case trends
            daily_trends = db.session.query(
                func.date(Complaint.created_at).label('date'),
                func.count(Complaint.id).label('count')
            ).filter(
                Complaint.created_at >= start_date
            ).group_by('date').order_by('date').all()
            
            # Resolution time statistics
            resolved_cases = Complaint.query.filter(
                and_(
                    Complaint.status == 'resolved',
                    Complaint.resolved_date.isnot(None),
                    Complaint.created_at >= start_date
                )
            ).all()
            
            resolution_times = []
            for case in resolved_cases:
                if case.resolved_date and case.created_at:
                    resolution_time = (case.resolved_date - case.created_at).days
                    resolution_times.append(resolution_time)
            
            avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
            
            return {
                'status_distribution': {status: count for status, count in status_stats if status},
                'priority_distribution': {priority: count for priority, count in priority_stats if priority},
                'crime_type_distribution': {crime_type: count for crime_type, count in crime_stats if crime_type},
                'daily_trends': [
                    {
                        'date': trend.date.isoformat() if hasattr(trend.date, 'isoformat') else str(trend.date), 
                        'count': trend.count
                    } for trend in daily_trends
                ],
                'resolution_metrics': {
                    'average_resolution_days': round(avg_resolution_time, 2),
                    'total_resolved_cases': len(resolved_cases)
                },
                'time_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                }
            }
        except Exception as e:
            print(f"Analytics error: {e}")
            return {
                'status_distribution': {},
                'priority_distribution': {},
                'crime_type_distribution': {},
                'daily_trends': [],
                'resolution_metrics': {'average_resolution_days': 0, 'total_resolved_cases': 0},
                'time_period': {'start_date': None, 'end_date': None, 'days': days}
            }
            
    def get_officer_performance(self):
        """Get police officer performance metrics"""
        try:
            officers = PoliceOfficer.query.filter_by(is_active=True).all()
            
            performance_data = []
            for officer in officers:
                # Cases assigned
                assigned_cases = CaseAssignment.query.filter_by(
                    police_officer_id=officer.id
                ).count()
                
                # Resolved cases
                resolved_cases = Complaint.query.join(CaseAssignment).filter(
                    CaseAssignment.police_officer_id == officer.id,
                    Complaint.status == 'resolved'
                ).count()
                
                # Average resolution time
                resolved_case_times = []
                resolved_complaints = Complaint.query.join(CaseAssignment).filter(
                    CaseAssignment.police_officer_id == officer.id,
                    Complaint.status == 'resolved',
                    Complaint.resolved_date.isnot(None)
                ).all()
                
                for complaint in resolved_complaints:
                    if complaint.resolved_date and complaint.created_at:
                        resolution_time = (complaint.resolved_date - complaint.created_at).days
                        resolved_case_times.append(resolution_time)
                
                avg_resolution = sum(resolved_case_times) / len(resolved_case_times) if resolved_case_times else 0
                
                performance_score = self.calculate_officer_score(
                    assigned_cases,
                    resolved_cases,
                    avg_resolution
                )
                
                performance_data.append({
                    'officer_id': officer.id,
                    'name': officer.user.full_name if officer.user else 'Unknown',
                    'badge_number': officer.badge_number or 'N/A',
                    'station': officer.station or 'Unknown',
                    'assigned_cases': assigned_cases,
                    'resolved_cases': resolved_cases,
                    'resolution_rate': round((resolved_cases / assigned_cases * 100) if assigned_cases > 0 else 0, 2),
                    'avg_resolution_days': round(avg_resolution, 2),
                    'performance_score': round(performance_score, 2)
                })
            
            return sorted(performance_data, key=lambda x: x['performance_score'], reverse=True)
        except Exception as e:
            print(f"Officer performance error: {e}")
            return []
    
    def calculate_officer_score(self, assigned, resolved, avg_resolution):
        """Calculate officer performance score"""
        if assigned == 0:
            return 0
        
        resolution_rate = resolved / assigned
        resolution_bonus = max(0, (30 - avg_resolution) / 30)  # Bonus for faster resolution
        
        base_score = resolution_rate * 100
        performance_score = base_score + (resolution_bonus * 20)
        
        return min(performance_score, 100)
    
    def get_volunteer_metrics(self):
        """Get volunteer performance metrics"""
        try:
            volunteers = Volunteer.query.filter_by(status='approved').all()
            
            volunteer_data = []
            for volunteer in volunteers:
                assigned_cases = CaseAssignment.query.filter_by(
                    volunteer_id=volunteer.id
                ).count()
                
                completed_cases = CaseAssignment.query.filter_by(
                    volunteer_id=volunteer.id
                ).join(Complaint).filter(
                    Complaint.status == 'resolved'
                ).count()
                
                volunteer_data.append({
                    'volunteer_id': volunteer.id,
                    'name': volunteer.user.full_name if volunteer.user else 'Unknown',
                    'state': volunteer.state or 'Unknown',
                    'district': volunteer.district or 'Unknown',
                    'skills': volunteer.skills,
                    'assigned_cases': assigned_cases,
                    'completed_cases': completed_cases,
                    'completion_rate': round((completed_cases / assigned_cases * 100) if assigned_cases > 0 else 0, 2),
                    'rating': volunteer.rating or 0
                })
            
            return volunteer_data
        except Exception as e:
            print(f"Volunteer metrics error: {e}")
            return []
    
    def get_geographical_insights(self):
        """Get geographical distribution of cases"""
        try:
            state_stats = db.session.query(
                Complaint.state,
                func.count(Complaint.id).label('case_count')
            ).group_by(Complaint.state).all()
            
            district_stats = db.session.query(
                Complaint.state,
                Complaint.district,
                func.count(Complaint.id).label('case_count')
            ).group_by(Complaint.state, Complaint.district).all()
            
            crime_by_region = db.session.query(
                Complaint.state,
                Complaint.crime_type,
                func.count(Complaint.id).label('count')
            ).group_by(Complaint.state, Complaint.crime_type).all()
            
            return {
                'state_distribution': [
                    {'state': stat.state or 'Unknown', 'case_count': stat.case_count} 
                    for stat in state_stats
                ],
                'district_distribution': [
                    {'state': stat.state or 'Unknown', 'district': stat.district or 'Unknown', 'case_count': stat.case_count} 
                    for stat in district_stats
                ],
                'crime_by_region': [
                    {'state': crime.state or 'Unknown', 'crime_type': crime.crime_type or 'other', 'count': crime.count} 
                    for crime in crime_by_region
                ]
            }
        except Exception as e:
            print(f"Geographical insights error: {e}")
            return {
                'state_distribution': [],
                'district_distribution': [],
                'crime_by_region': []
            }

# Global analytics instance
analytics_engine = AnalyticsEngine()