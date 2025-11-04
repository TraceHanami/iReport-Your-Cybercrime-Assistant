from database.connection import db
from database.models import PoliceOfficer, Complaint, CaseAssignment
from sqlalchemy import func, and_
from datetime import datetime, timedelta

class PerformanceTracker:
    def __init__(self):
        pass
    
    def calculate_officer_performance(self, officer_id, days=30):
        """Calculate performance metrics for a police officer"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            officer = PoliceOfficer.query.get(officer_id)
            if not officer:
                return None
            
            # Cases assigned in period
            assigned_cases = CaseAssignment.query.filter(
                and_(
                    CaseAssignment.police_officer_id == officer_id,
                    CaseAssignment.assigned_date >= start_date
                )
            ).count()
            
            # Cases resolved in period
            resolved_cases = Complaint.query.join(CaseAssignment).filter(
                and_(
                    CaseAssignment.police_officer_id == officer_id,
                    Complaint.status == 'resolved',
                    Complaint.resolved_date >= start_date,
                    Complaint.resolved_date <= end_date
                )
            ).count()
            
            # Average resolution time
            resolved_complaints = Complaint.query.join(CaseAssignment).filter(
                and_(
                    CaseAssignment.police_officer_id == officer_id,
                    Complaint.status == 'resolved',
                    Complaint.resolved_date.isnot(None),
                    Complaint.resolved_date >= start_date,
                    Complaint.resolved_date <= end_date
                )
            ).all()
            
            resolution_times = []
            for complaint in resolved_complaints:
                if complaint.resolved_date and complaint.created_at:
                    resolution_time = (complaint.resolved_date - complaint.created_at).total_seconds() / 86400  # days
                    resolution_times.append(resolution_time)
            
            avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
            
            # Priority-based performance
            high_priority_resolved = Complaint.query.join(CaseAssignment).filter(
                and_(
                    CaseAssignment.police_officer_id == officer_id,
                    Complaint.status == 'resolved',
                    Complaint.priority.in_(['high', 'critical']),
                    Complaint.resolved_date >= start_date,
                    Complaint.resolved_date <= end_date
                )
            ).count()
            
            # Current active cases
            active_cases = CaseAssignment.query.filter(
                and_(
                    CaseAssignment.police_officer_id == officer_id,
                    CaseAssignment.status == 'active'
                )
            ).count()
            
            # Calculate performance score
            performance_score = self.compute_performance_score(
                assigned_cases,
                resolved_cases,
                avg_resolution_time,
                high_priority_resolved,
                active_cases
            )
            
            return {
                'officer_id': officer_id,
                'officer_name': officer.user.full_name if officer.user else 'Unknown',
                'badge_number': officer.badge_number,
                'station': officer.station,
                'period': f'{days} days',
                'assigned_cases': assigned_cases,
                'resolved_cases': resolved_cases,
                'active_cases': active_cases,
                'resolution_rate': round((resolved_cases / assigned_cases * 100) if assigned_cases > 0 else 0, 2),
                'avg_resolution_days': round(avg_resolution_time, 2),
                'high_priority_resolved': high_priority_resolved,
                'performance_score': round(performance_score, 2),
                'performance_grade': self.get_performance_grade(performance_score)
            }
        except Exception as e:
            print(f"Error calculating officer performance: {e}")
            return None
    
    def compute_performance_score(self, assigned, resolved, avg_resolution, high_priority_resolved, active_cases):
        """Compute comprehensive performance score"""
        try:
            if assigned == 0:
                return 0
            
            # Base score from resolution rate (40% weight)
            resolution_rate = (resolved / assigned) * 100
            base_score = min(resolution_rate * 0.4, 40)
            
            # Resolution time score (30% weight) - faster is better
            resolution_time_score = 0
            if avg_resolution > 0:
                # Normalize: 0 days = 30 points, 30+ days = 0 points
                resolution_time_score = max(0, (30 - min(avg_resolution, 30)) / 30 * 30)
            
            # High priority resolution bonus (20% weight)
            priority_score = (high_priority_resolved / max(resolved, 1)) * 20
            
            # Case load management (10% weight) - balanced load is better
            load_score = 0
            if active_cases <= 10:  # Reasonable case load
                load_score = 10
            elif active_cases <= 20:  # Moderate load
                load_score = 5
            # More than 20 cases gets 0 points
            
            total_score = base_score + resolution_time_score + priority_score + load_score
            return min(total_score, 100)
        except Exception as e:
            print(f"Error computing performance score: {e}")
            return 0
    
    def get_performance_grade(self, score):
        """Convert score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    def get_team_performance(self, station=None, district=None):
        """Get performance metrics for a team of officers"""
        try:
            query = PoliceOfficer.query.filter_by(is_active=True)
            
            if station:
                query = query.filter_by(station=station)
            if district:
                query = query.filter_by(district=district)
            
            officers = query.all()
            
            team_performance = []
            for officer in officers:
                performance = self.calculate_officer_performance(officer.id)
                if performance:
                    team_performance.append(performance)
            
            # Calculate team averages
            if team_performance:
                avg_resolution_rate = sum(p['resolution_rate'] for p in team_performance) / len(team_performance)
                avg_performance_score = sum(p['performance_score'] for p in team_performance) / len(team_performance)
                total_resolved = sum(p['resolved_cases'] for p in team_performance)
                total_assigned = sum(p['assigned_cases'] for p in team_performance)
            else:
                avg_resolution_rate = 0
                avg_performance_score = 0
                total_resolved = 0
                total_assigned = 0
            
            return {
                'team_performance': team_performance,
                'team_metrics': {
                    'total_officers': len(team_performance),
                    'total_assigned_cases': total_assigned,
                    'total_resolved_cases': total_resolved,
                    'team_resolution_rate': round((total_resolved / total_assigned * 100) if total_assigned > 0 else 0, 2),
                    'avg_resolution_rate': round(avg_resolution_rate, 2),
                    'avg_performance_score': round(avg_performance_score, 2),
                    'performance_breakdown': {
                        'A+': len([p for p in team_performance if p['performance_grade'] == 'A+']),
                        'A': len([p for p in team_performance if p['performance_grade'] == 'A']),
                        'B': len([p for p in team_performance if p['performance_grade'] == 'B']),
                        'C': len([p for p in team_performance if p['performance_grade'] == 'C']),
                        'D': len([p for p in team_performance if p['performance_grade'] == 'D']),
                        'F': len([p for p in team_performance if p['performance_grade'] == 'F'])
                    }
                }
            }
        except Exception as e:
            print(f"Error getting team performance: {e}")
            return {'team_performance': [], 'team_metrics': {}}
    
    def update_officer_performance_scores(self):
        """Update performance scores for all officers in database"""
        try:
            officers = PoliceOfficer.query.filter_by(is_active=True).all()
            updated_count = 0
            
            for officer in officers:
                performance = self.calculate_officer_performance(officer.id)
                if performance:
                    officer.performance_score = performance['performance_score']
                    officer.current_case_load = CaseAssignment.query.filter_by(
                        police_officer_id=officer.id,
                        status='active'
                    ).count()
                    updated_count += 1
            
            db.session.commit()
            return updated_count
        except Exception as e:
            db.session.rollback()
            print(f"Error updating officer performance scores: {e}")
            return 0
    
    def get_performance_trends(self, officer_id, periods=6):
        """Get performance trends over multiple periods"""
        trends = []
        for i in range(periods):
            days = 30 * (i + 1)  # 30, 60, 90... days
            performance = self.calculate_officer_performance(officer_id, days)
            if performance:
                trends.append({
                    'period_days': days,
                    'performance_score': performance['performance_score'],
                    'resolution_rate': performance['resolution_rate'],
                    'avg_resolution_days': performance['avg_resolution_days']
                })
        
        return trends

# Global performance tracker instance
performance_tracker = PerformanceTracker()