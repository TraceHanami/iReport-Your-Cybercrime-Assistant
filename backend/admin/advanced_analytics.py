from database.connection import db
from database.models import Complaint, User, PoliceOfficer, Volunteer, CaseAssignment
from sqlalchemy import func, and_, extract, case
from datetime import datetime, timedelta
import json
import pandas as pd

class AdvancedAnalytics:
    def __init__(self):
        pass
    
    def get_trend_analysis(self, days=90):
        """Analyze crime trends over time"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Daily trends
            daily_trends = db.session.query(
                func.date(Complaint.created_at).label('date'),
                func.count(Complaint.id).label('total_cases'),
                func.avg(case((Complaint.priority.in_(['high', 'critical']), 1), else_=0)).label('high_priority_rate')
            ).filter(
                Complaint.created_at >= start_date
            ).group_by('date').order_by('date').all()
            
            # Weekly patterns
            weekly_patterns = db.session.query(
                extract('dow', Complaint.created_at).label('day_of_week'),
                func.count(Complaint.id).label('case_count')
            ).filter(
                Complaint.created_at >= start_date
            ).group_by('day_of_week').all()
            
            # Crime type trends
            crime_trends = db.session.query(
                Complaint.crime_type,
                func.count(Complaint.id).label('count'),
                func.avg(case((Complaint.status == 'resolved', 1), else_=0)).label('resolution_rate')
            ).filter(
                Complaint.created_at >= start_date
            ).group_by(Complaint.crime_type).all()
            
            return {
                'daily_trends': [
                    {
                        'date': trend.date.isoformat() if hasattr(trend.date, 'isoformat') else str(trend.date),
                        'total_cases': trend.total_cases,
                        'high_priority_rate': float(trend.high_priority_rate or 0)
                    } for trend in daily_trends
                ],
                'weekly_patterns': [
                    {
                        'day_of_week': int(pattern.day_of_week) if pattern.day_of_week else 0,
                        'day_name': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][int(pattern.day_of_week) if pattern.day_of_week else 0],
                        'case_count': pattern.case_count
                    } for pattern in weekly_patterns
                ],
                'crime_trends': [
                    {
                        'crime_type': trend.crime_type or 'other',
                        'count': trend.count,
                        'resolution_rate': float(trend.resolution_rate or 0)
                    } for trend in crime_trends
                ]
            }
        except Exception as e:
            print(f"Error in trend analysis: {e}")
            return {
                'daily_trends': [],
                'weekly_patterns': [],
                'crime_trends': []
            }
    
    def get_geospatial_heatmap(self):
        """Generate geospatial heatmap data"""
        try:
            heatmap_data = db.session.query(
                Complaint.state,
                Complaint.district,
                func.count(Complaint.id).label('case_count'),
                func.avg(case((Complaint.priority.in_(['high', 'critical']), 1), else_=0)).label('high_priority_density')
            ).group_by(Complaint.state, Complaint.district).all()
            
            return [
                {
                    'state': data.state or 'Unknown',
                    'district': data.district or 'Unknown',
                    'case_count': data.case_count,
                    'high_priority_density': float(data.high_priority_density or 0),
                    'intensity': min(data.case_count / 10, 1.0) if data.case_count > 0 else 0
                } for data in heatmap_data
            ]
        except Exception as e:
            print(f"Error in geospatial heatmap: {e}")
            return []
    
    def get_predictive_insights(self):
        """Generate predictive insights using simple ML patterns"""
        try:
            # Recent trend analysis for predictions
            recent_cases = Complaint.query.filter(
                Complaint.created_at >= datetime.utcnow() - timedelta(days=30)
            ).all()
            
            if not recent_cases:
                return {
                    'emerging_trends': [],
                    'time_patterns': {},
                    'risk_assessment': {'high_risk_areas': [], 'recommended_patrols': []}
                }
            
            # Simple pattern detection
            crime_types = [case.crime_type or 'other' for case in recent_cases]
            from collections import Counter
            common_crimes = Counter(crime_types).most_common(3)
            
            # Time-based patterns
            morning_cases = len([c for c in recent_cases if c.created_at and 6 <= c.created_at.hour < 12])
            evening_cases = len([c for c in recent_cases if c.created_at and 18 <= c.created_at.hour < 24])
            
            insights = {
                'emerging_trends': [
                    {
                        'crime_type': crime[0],
                        'frequency': crime[1],
                        'trend': 'increasing' if crime[1] > len(recent_cases) / 10 else 'stable'
                    } for crime in common_crimes
                ],
                'time_patterns': {
                    'morning_cases': morning_cases,
                    'evening_cases': evening_cases,
                    'peak_hours': 'Evening' if evening_cases > morning_cases else 'Morning'
                },
                'risk_assessment': {
                    'high_risk_areas': self.get_high_risk_areas(),
                    'recommended_patrols': self.generate_patrol_recommendations()
                }
            }
            
            return insights
        except Exception as e:
            print(f"Error in predictive insights: {e}")
            return {
                'emerging_trends': [],
                'time_patterns': {},
                'risk_assessment': {'high_risk_areas': [], 'recommended_patrols': []}
            }
    
    def get_high_risk_areas(self):
        """Identify high-risk areas based on case density and priority"""
        try:
            risk_data = db.session.query(
                Complaint.district,
                func.count(Complaint.id).label('total_cases'),
                func.avg(case((Complaint.priority.in_(['high', 'critical']), 1), else_=0)).label('high_priority_rate'),
                func.avg(case((Complaint.status == 'resolved', 1), else_=0)).label('resolution_rate')
            ).group_by(Complaint.district).all()
            
            high_risk = []
            for data in risk_data:
                if data.total_cases > 0:
                    risk_score = (data.total_cases * 0.4 + 
                                 (data.high_priority_rate or 0) * 0.4 + 
                                 (1 - (data.resolution_rate or 0)) * 0.2)
                    
                    if risk_score > 0.3:  # Lower threshold for demo
                        high_risk.append({
                            'district': data.district or 'Unknown',
                            'risk_score': round(risk_score, 2),
                            'total_cases': data.total_cases,
                            'high_priority_rate': float(data.high_priority_rate or 0),
                            'resolution_rate': float(data.resolution_rate or 0)
                        })
            
            return sorted(high_risk, key=lambda x: x['risk_score'], reverse=True)[:5]
        except Exception as e:
            print(f"Error in high risk areas: {e}")
            return []
    
    def generate_patrol_recommendations(self):
        """Generate patrol recommendations based on analytics"""
        try:
            high_risk_areas = self.get_high_risk_areas()
            time_patterns = self.get_trend_analysis(30).get('weekly_patterns', [])
            
            if not time_patterns:
                return []
            
            peak_day = max(time_patterns, key=lambda x: x.get('case_count', 0))
            
            recommendations = []
            for area in high_risk_areas[:3]:  # Top 3 high-risk areas
                recommendations.append({
                    'district': area['district'],
                    'priority': 'High',
                    'recommended_patrols': [
                        {'time': 'Morning (6-12)', 'day': peak_day.get('day_name', 'Monday')},
                        {'time': 'Evening (18-24)', 'day': peak_day.get('day_name', 'Monday')}
                    ],
                    'rationale': f"High case density ({area['total_cases']} cases) with {area['high_priority_rate']*100:.1f}% high-priority cases"
                })
            
            return recommendations
        except Exception as e:
            print(f"Error in patrol recommendations: {e}")
            return []
    
    def get_performance_metrics(self):
        """Comprehensive performance metrics"""
        try:
            # Officer performance
            officers = PoliceOfficer.query.filter_by(is_active=True).all()
            officer_metrics = []
            
            for officer in officers:
                assigned_cases = CaseAssignment.query.filter_by(police_officer_id=officer.id).count()
                resolved_cases = Complaint.query.join(CaseAssignment).filter(
                    CaseAssignment.police_officer_id == officer.id,
                    Complaint.status == 'resolved'
                ).count()
                
                if assigned_cases > 0:
                    efficiency = resolved_cases / assigned_cases
                    avg_resolution_time = self.get_avg_resolution_time(officer.id)
                    
                    officer_metrics.append({
                        'officer_name': officer.user.full_name if officer.user else 'Unknown',
                        'badge_number': officer.badge_number or 'N/A',
                        'assigned_cases': assigned_cases,
                        'resolved_cases': resolved_cases,
                        'efficiency_rate': round(efficiency, 2),
                        'avg_resolution_days': avg_resolution_time,
                        'performance_score': round((efficiency * 0.6 + (1 - min(avg_resolution_time/30, 1)) * 0.4) * 100, 1)
                    })
            
            # System metrics
            total_cases = Complaint.query.count()
            resolved_cases = Complaint.query.filter_by(status='resolved').count()
            avg_system_resolution = self.get_avg_resolution_time()
            
            return {
                'officer_performance': sorted(officer_metrics, key=lambda x: x.get('performance_score', 0), reverse=True),
                'system_metrics': {
                    'total_cases': total_cases,
                    'resolved_cases': resolved_cases,
                    'resolution_rate': round(resolved_cases / total_cases * 100, 1) if total_cases > 0 else 0,
                    'avg_resolution_days': avg_system_resolution,
                    'active_officers': len(officers),
                    'case_backlog': total_cases - resolved_cases
                }
            }
        except Exception as e:
            print(f"Error in performance metrics: {e}")
            return {
                'officer_performance': [],
                'system_metrics': {}
            }
    
    def get_avg_resolution_time(self, officer_id=None):
        """Calculate average resolution time in days"""
        try:
            query = Complaint.query.filter(
                Complaint.status == 'resolved',
                Complaint.resolved_date.isnot(None)
            )
            
            if officer_id:
                query = query.join(CaseAssignment).filter(CaseAssignment.police_officer_id == officer_id)
            
            resolved_cases = query.all()
            
            if not resolved_cases:
                return 0
            
            total_days = 0
            valid_cases = 0
            for case in resolved_cases:
                if case.resolved_date and case.created_at:
                    resolution_time = (case.resolved_date - case.created_at).days
                    total_days += resolution_time
                    valid_cases += 1
            
            return round(total_days / valid_cases, 1) if valid_cases > 0 else 0
        except Exception as e:
            print(f"Error in resolution time calculation: {e}")
            return 0

# Global analytics instance
advanced_analytics = AdvancedAnalytics()