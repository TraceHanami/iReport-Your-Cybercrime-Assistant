from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database.connection import db
from datetime import datetime

class PoliceOfficer(db.Model):
    __tablename__ = "police_officers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    badge_number = Column(String(50), unique=True, nullable=False)
    rank = Column(String(50))  # Example: "Inspector", "Sub-Inspector", "Constable"
    station = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    jurisdiction = Column(Text)
    contact_number = Column(String(15))
    is_active = Column(Boolean, default=True)
    current_case_load = Column(Integer, default=0)
    performance_score = Column(Integer, default=0)
    specialization = Column(String(100))  # Example: "Cyber Crime", "Narcotics", "Traffic"
    experience_years = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="police_profile")
    assigned_cases = relationship("CaseAssignment", back_populates="police_officer")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "badge_number": self.badge_number,
            "rank": self.rank,
            "station": self.station,
            "state": self.state,
            "district": self.district,
            "jurisdiction": self.jurisdiction,
            "contact_number": self.contact_number,
            "is_active": self.is_active,
            "current_case_load": self.current_case_load,
            "performance_score": self.performance_score,
            "specialization": self.specialization,
            "experience_years": self.experience_years,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }