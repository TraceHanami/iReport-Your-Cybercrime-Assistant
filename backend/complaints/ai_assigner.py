from database.models import PoliceOfficer, Volunteer, Complaint, CaseAssignment
from database.connection import db
from sqlalchemy import func
from datetime import datetime

class CaseAssigner:
    def __init__(self):
        self.specializations = {
            # Updated specializations for new crime categories
            'violent_crime': ['violent_crime', 'special_operations', 'investigation', 'emergency_response'],
            'theft_robbery': ['property_crime', 'investigation', 'patrol', 'financial_crime'],
            'cyber_attack': ['cyber_crime', 'technical', 'investigation', 'digital_forensics'],
            'online_fraud': ['financial_crime', 'cyber_crime', 'investigation', 'fraud_unit'],
            'identity_theft': ['cyber_crime', 'financial_crime', 'investigation', 'identity_theft_unit'],
            'data_breach': ['cyber_crime', 'technical', 'investigation', 'digital_forensics'],
            'crypto_crime': ['cyber_crime', 'financial_crime', 'technical', 'crypto_investigation'],
            'social_media_crime': ['cyber_crime', 'special_victims', 'investigation', 'digital_forensics'],
            'dark_web_crime': ['cyber_crime', 'narcotics', 'investigation', 'undercover_operations'],
            'ai_ml_crime': ['cyber_crime', 'technical', 'investigation', 'emerging_technology'],
            'financial_crime': ['financial_crime', 'fraud_unit', 'investigation', 'white_collar'],
            'missing_person': ['missing_persons', 'investigation', 'patrol', 'search_rescue'],
            'property_damage': ['property_crime', 'patrol', 'investigation', 'community_policing'],
            'domestic_violence': ['special_victims', 'domestic_violence_unit', 'investigation', 'crisis_response'],
            'drug_crime': ['narcotics', 'special_operations', 'investigation', 'undercover_operations'],
            'sexual_offense': ['special_victims', 'sex_crimes_unit', 'investigation', 'crisis_response'],
            'online_harassment': ['cyber_crime', 'special_victims', 'investigation', 'community_policing'],
            'cyber_crime': ['cyber_crime', 'technical', 'investigation', 'digital_forensics'],
            'other': ['general', 'patrol', 'investigation', 'community_policing']
        }
        
        self.crime_priority_mapping = {
            'critical': ['violent_crime', 'missing_person', 'sexual_offense', 'cyber_attack', 'domestic_violence'],
            'high': ['theft_robbery', 'drug_crime', 'financial_crime', 'identity_theft', 'crypto_crime'],
            'medium': ['online_fraud', 'data_breach', 'property_damage', 'dark_web_crime', 'ai_ml_crime'],
            'low': ['social_media_crime', 'online_harassment']
        }

    def find_best_police_officer(self, complaint):
        """Find the best police officer for a case"""
        try:
            print(f"🔍 Searching for police officer for case: {complaint.case_id} in {complaint.district}, {complaint.state}")
            
            # Get officers in the same state and district
            potential_officers = PoliceOfficer.query.filter_by(
                state=complaint.state,
                district=complaint.district,
                is_active=True
            ).all()
            
            print(f"📊 Found {len(potential_officers)} officers in same district")
            
            if not potential_officers:
                # Fallback to state-level search
                potential_officers = PoliceOfficer.query.filter_by(
                    state=complaint.state,
                    is_active=True
                ).all()
                print(f"📊 Found {len(potential_officers)} officers in same state")
            
            # If still no officers, get any active officer
            if not potential_officers:
                potential_officers = PoliceOfficer.query.filter_by(is_active=True).all()
                print(f"📊 Found {len(potential_officers)} active officers nationwide")
            
            if not potential_officers:
                print("❌ No active police officers found in the system")
                return None
            
            best_officer = None
            best_score = -1
            
            for officer in potential_officers:
                score = self.calculate_officer_score(officer, complaint)
                print(f"👮 Officer {officer.user.full_name if officer.user else 'Unknown'}: Score {score}")
                
                if score > best_score:
                    best_score = score
                    best_officer = officer
            
            print(f"✅ Best officer: {best_officer.user.full_name if best_officer and best_officer.user else 'None'} with score {best_score}")
            return best_officer if best_score > 0 else None
            
        except Exception as e:
            print(f"❌ Error finding police officer: {e}")
            return None

    def calculate_officer_score(self, officer, complaint):
        """Calculate suitability score for officer"""
        score = 0
        
        # Case load factor (prefer officers with fewer cases)
        current_case_load = officer.current_case_load or 0
        case_load_factor = max(0, 20 - current_case_load)
        score += case_load_factor
        print(f"   Case load: {current_case_load} -> +{case_load_factor}")
        
        # Performance factor
        performance_score = officer.performance_score or 0
        score += performance_score * 3
        print(f"   Performance: {performance_score} -> +{performance_score * 3}")
        
        # Geographic matching
        if officer.district == complaint.district:
            score += 10  # Same district - high priority
            print(f"   Same district -> +10")
        elif officer.state == complaint.state:
            score += 5   # Same state - medium priority
            print(f"   Same state -> +5")
        
        # Jurisdiction matching
        if officer.jurisdiction and complaint.district in officer.jurisdiction:
            score += 8
            print(f"   Jurisdiction match -> +8")
        
        # Rank-based scoring (higher ranks get preference for serious crimes)
        rank_bonus = {
            'Commissioner': 15, 'Deputy Commissioner': 12, 'Assistant Commissioner': 10,
            'Inspector': 8, 'Sub-Inspector': 5, 'Constable': 2
        }
        rank_score = rank_bonus.get(officer.rank, 0)
        score += rank_score
        print(f"   Rank {officer.rank} -> +{rank_score}")
        
        # Specialization matching
        crime_type = complaint.crime_type
        if crime_type in self.specializations:
            # Simulate specialization matching based on officer's station/rank
            station_specializations = {
                'Cyber Crime Station': ['cyber_attack', 'online_fraud', 'identity_theft', 'data_breach', 'crypto_crime', 'social_media_crime', 'dark_web_crime', 'ai_ml_crime', 'cyber_crime'],
                'Economic Offenses Wing': ['financial_crime', 'online_fraud', 'identity_theft', 'crypto_crime'],
                'Narcotics Bureau': ['drug_crime', 'dark_web_crime'],
                'Special Victims Unit': ['domestic_violence', 'sexual_offense', 'online_harassment'],
                'Missing Persons Bureau': ['missing_person'],
                'Property Crime Unit': ['theft_robbery', 'property_damage'],
                'Violent Crime Unit': ['violent_crime']
            }
            
            for station_type, crimes in station_specializations.items():
                if officer.station and station_type in officer.station and crime_type in crimes:
                    score += 12
                    print(f"   Specialization match {station_type} -> +12")
                    break
        
        # Emergency response capability for critical/high priority cases
        if complaint.priority in ['critical', 'high']:
            if officer.station and ('emergency_response' in officer.station or 'Special Operations' in officer.rank):
                score += 8
                print(f"   Emergency response -> +8")
        
        print(f"   Total score: {score}")
        return score

    def find_volunteer_for_case(self, complaint):
        """Find suitable volunteer for LOW PRIORITY cases only"""
        try:
            print(f"🔍 Searching for volunteer for case: {complaint.case_id}")
            
            # ONLY assign volunteers to LOW priority cases
            if complaint.priority != 'low':
                print("❌ Volunteers only assigned to LOW priority cases")
                return None
            
            # Suitable crime types for volunteers (only low-risk cases)
            suitable_crimes_for_volunteers = [
                'social_media_crime', 'online_harassment', 'property_damage'
            ]
            
            if complaint.crime_type not in suitable_crimes_for_volunteers:
                print(f"❌ Crime type {complaint.crime_type} not suitable for volunteers")
                return None
            
            # Find volunteers in the same area
            potential_volunteers = Volunteer.query.filter_by(
                state=complaint.state,
                district=complaint.district,
                status='approved'
            ).all()
            
            print(f"📊 Found {len(potential_volunteers)} volunteers in same district")
            
            if not potential_volunteers:
                # Fallback to state-level search
                potential_volunteers = Volunteer.query.filter_by(
                    state=complaint.state,
                    status='approved'
                ).all()
                print(f"📊 Found {len(potential_volunteers)} volunteers in same state")
            
            if not potential_volunteers:
                print("❌ No approved volunteers found")
                return None
            
            best_volunteer = None
            best_score = -1
            
            for volunteer in potential_volunteers:
                score = self.calculate_volunteer_score(volunteer, complaint)
                print(f"🤝 Volunteer {volunteer.user.full_name if volunteer.user else 'Unknown'}: Score {score}")
                
                if score > best_score:
                    best_score = score
                    best_volunteer = volunteer
            
            print(f"✅ Best volunteer: {best_volunteer.user.full_name if best_volunteer and best_volunteer.user else 'None'} with score {best_score}")
            return best_volunteer if best_score > 0 else None
            
        except Exception as e:
            print(f"❌ Error finding volunteer: {e}")
            return None

    def calculate_volunteer_score(self, volunteer, complaint):
        """Calculate suitability score for volunteer"""
        score = 0
        
        # Rating factor (experienced volunteers get preference)
        rating = volunteer.rating or 0
        score += rating * 4
        print(f"   Rating: {rating} -> +{rating * 4}")
        
        # Experience factor
        cases_handled = volunteer.cases_handled or 0
        experience_bonus = min(cases_handled / 5, 10)  # Max 10 points for experience
        score += experience_bonus
        print(f"   Experience: {cases_handled} cases -> +{experience_bonus}")
        
        # Availability
        availability_bonus = {
            'full_time': 8,
            'part_time': 4,
            'weekends': 3,
            'evenings': 2
        }
        availability_score = availability_bonus.get(volunteer.availability, 0)
        score += availability_score
        print(f"   Availability: {volunteer.availability} -> +{availability_score}")
        
        # Background check (mandatory for assignment)
        if not volunteer.background_check:
            print("   ❌ No background check -> disqualify")
            return 0  # No assignment without background check
        score += 6
        print(f"   Background check -> +6")
        
        # Skills matching for low-priority cases
        crime_skill_mapping = {
            'online_harassment': ['counseling', 'community outreach', 'social work', 'mental health'],
            'social_media_crime': ['digital literacy', 'social media', 'community outreach', 'tech support'],
            'property_damage': ['community service', 'construction', 'handyman', 'coordination']
        }
        
        if volunteer.skills:
            skills_list = [skill.strip().lower() for skill in volunteer.skills.split(',')]
            required_skills = crime_skill_mapping.get(complaint.crime_type, [])
            
            for skill in required_skills:
                if any(skill in volunteer_skill for volunteer_skill in skills_list):
                    score += 5
                    print(f"   Skill match: {skill} -> +5")
                    break
        
        # Geographic proximity
        if volunteer.district == complaint.district:
            score += 8
            print(f"   Same district -> +8")
        elif volunteer.state == complaint.state:
            score += 4
            print(f"   Same state -> +4")
        
        print(f"   Total score: {score}")
        return score

    def auto_assign_case(self, complaint):
        """Automatically assign case - ONLY LOW PRIORITY to volunteers"""
        try:
            print(f"🔍 Auto-assigning case: {complaint.case_id} | Crime: {complaint.crime_type} | Priority: {complaint.priority}")
            
            # CRITICAL priority - always police, highest urgency
            if complaint.priority == 'critical':
                print("🚨 CRITICAL priority case - assigning to highest available police officer")
                officer = self.find_best_police_officer(complaint)
                if officer:
                    print(f"✅ Assigned to Officer: {officer.user.full_name} ({officer.badge_number})")
                    return officer, 'police'
                else:
                    print("❌ No police officer available for critical case!")
                    return None, None
            
            # HIGH priority - always police, urgent cases
            elif complaint.priority == 'high':
                print("🔴 HIGH priority case - assigning to police")
                officer = self.find_best_police_officer(complaint)
                if officer:
                    print(f"✅ Assigned to Officer: {officer.user.full_name} ({officer.badge_number})")
                    return officer, 'police'
                else:
                    print("❌ No suitable police officer found for high priority case")
                    return None, None
            
            # MEDIUM priority - always police, no volunteer assignment
            elif complaint.priority == 'medium':
                print("🟡 MEDIUM priority case - assigning to police (volunteers not allowed)")
                officer = self.find_best_police_officer(complaint)
                if officer:
                    print(f"✅ Assigned to Officer: {officer.user.full_name} ({officer.badge_number})")
                    return officer, 'police'
                else:
                    print("❌ No suitable police officer found for medium priority case")
                    return None, None
            
            # LOW priority - ONLY cases that can be assigned to volunteers
            else:  # low priority
                print("🟢 LOW priority case - eligible for volunteer assignment")
                volunteer = self.find_volunteer_for_case(complaint)
                if volunteer:
                    print(f"✅ Assigned to Volunteer: {volunteer.user.full_name}")
                    return volunteer, 'volunteer'
                else:
                    print("🟢 No suitable volunteer found, trying police as fallback")
                    # Fallback to police if no volunteer available
                    officer = self.find_best_police_officer(complaint)
                    if officer:
                        print(f"✅ Fallback: Assigned to Officer: {officer.user.full_name}")
                        return officer, 'police'
                    else:
                        print("❌ No suitable assignee found for low priority case")
                        return None, None
                    
        except Exception as e:
            print(f"❌ Auto-assign error: {e}")
            return None, None

    def create_case_assignment(self, complaint, assignee, assignee_type):
        """Create a case assignment record in the database"""
        try:
            print(f"📝 Creating assignment for case {complaint.case_id} to {assignee_type}")
            
            assignment = CaseAssignment(
                complaint_id=complaint.id,
                assigned_date=datetime.utcnow(),
                status='assigned'
            )
            
            if assignee_type == 'police':
                assignment.police_officer_id = assignee.id
                # Update officer's case load
                assignee.current_case_load = (assignee.current_case_load or 0) + 1
                print(f"👮 Updated officer case load: {assignee.current_case_load}")
            elif assignee_type == 'volunteer':
                assignment.volunteer_id = assignee.id
                # Update volunteer's case count
                assignee.cases_handled = (assignee.cases_handled or 0) + 1
                print(f"🤝 Updated volunteer cases handled: {assignee.cases_handled}")
            
            db.session.add(assignment)
            db.session.commit()
            
            print(f"✅ Case assignment created for {assignee_type}: {assignee.user.full_name if assignee.user else 'Unknown'}")
            return assignment
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating case assignment: {e}")
            return None

    def get_assignment_recommendation(self, complaint):
        """Get assignment recommendation without actually assigning"""
        try:
            print(f"💡 Getting assignment recommendation for case: {complaint.case_id}")
            
            police_score = 0
            volunteer_score = 0
            
            # Calculate police suitability
            best_officer = self.find_best_police_officer(complaint)
            if best_officer:
                police_score = self.calculate_officer_score(best_officer, complaint)
            
            # Calculate volunteer suitability (only for low priority)
            if complaint.priority == 'low':
                best_volunteer = self.find_volunteer_for_case(complaint)
                if best_volunteer:
                    volunteer_score = self.calculate_volunteer_score(best_volunteer, complaint)
            
            recommendation = {
                'police_score': police_score,
                'volunteer_score': volunteer_score,
                'recommended_type': 'volunteer' if complaint.priority == 'low' and volunteer_score > police_score else 'police',
                'suitable_officers': PoliceOfficer.query.filter_by(
                    state=complaint.state, is_active=True
                ).count(),
                'suitable_volunteers': Volunteer.query.filter_by(
                    state=complaint.state, status='approved'
                ).count() if complaint.priority == 'low' else 0,
                'assignment_rules': {
                    'critical': 'Police Only',
                    'high': 'Police Only', 
                    'medium': 'Police Only',
                    'low': 'Volunteer Preferred, Police Fallback'
                }
            }
            
            print(f"✅ Recommendation: {recommendation}")
            return recommendation
            
        except Exception as e:
            print(f"❌ Recommendation error: {e}")
            return None

    def reassign_case(self, complaint, reason="Reassignment requested"):
        """Reassign a case to a new officer/volunteer"""
        try:
            print(f"🔄 Reassigning case: {complaint.case_id}")
            
            # Close current assignment
            current_assignment = CaseAssignment.query.filter_by(
                complaint_id=complaint.id,
                status='assigned'
            ).first()
            
            if current_assignment:
                current_assignment.status = 'reassigned'
                current_assignment.notes = reason
                
                # Decrement case load for police officer
                if current_assignment.police_officer_id:
                    officer = PoliceOfficer.query.get(current_assignment.police_officer_id)
                    if officer and officer.current_case_load > 0:
                        officer.current_case_load -= 1
                        print(f"👮 Decremented officer case load: {officer.current_case_load}")
            
            # Find new assignee
            new_assignee, assignee_type = self.auto_assign_case(complaint)
            
            if new_assignee:
                # Create new assignment
                new_assignment = self.create_case_assignment(complaint, new_assignee, assignee_type)
                return new_assignment, assignee_type
            else:
                print("❌ No suitable assignee found for reassignment")
                return None, None
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Reassignment error: {e}")
            return None, None

# Global assigner instance
case_assigner = CaseAssigner()