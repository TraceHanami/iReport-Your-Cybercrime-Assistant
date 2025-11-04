from pydantic import BaseModel, validator, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CrimeType(str, Enum):
    THEFT = "theft"
    ASSAULT = "assault"
    FRAUD = "fraud"
    CYBER_CRIME = "cyber_crime"
    MISSING_PERSON = "missing_person"
    PROPERTY_DAMAGE = "property_damage"
    HARASSMENT = "harassment"
    DRUG_OFFENSE = "drug_offense"
    OTHER = "other"

class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CaseStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class ComplaintBase(BaseModel):
    title: str
    description: str
    incident_date: datetime
    state: str
    district: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Victim Information
    victim_name: str
    victim_age: int
    victim_gender: str
    victim_contact: Optional[str] = None
    
    # Incident Details
    is_missing_person: bool = False
    is_injury_involved: bool = False
    is_property_damage: bool = False
    estimated_loss: Optional[float] = None
    injury_severity: Optional[str] = None
    
    # Police Complaint
    police_complaint_filed: bool = False
    police_station: Optional[str] = None
    police_complaint_number: Optional[str] = None
    police_complaint_date: Optional[datetime] = None
    
    # Anonymous Reporting
    is_anonymous: bool = False
    anonymous_email: Optional[EmailStr] = None
    
    # Additional Information
    witness_details: Optional[str] = None
    suspect_description: Optional[str] = None

class ComplaintCreate(ComplaintBase):
    @validator('victim_age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v
    
    @validator('estimated_loss')
    def validate_loss(cls, v):
        if v is not None and v < 0:
            raise ValueError('Estimated loss cannot be negative')
        return v

class ComplaintResponse(ComplaintBase):
    case_id: str
    status: CaseStatus
    priority: PriorityLevel
    crime_type: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CaseUpdateSchema(BaseModel):
    update_type: str
    title: str
    description: str
    internal_notes: Optional[str] = None

class CaseAssignmentSchema(BaseModel):
    assignee_type: str
    assignee_id: int
    assignment_reason: Optional[str] = None

class TrackCaseResponse(BaseModel):
    case_id: str
    title: str
    status: str
    priority: str
    current_status: str
    updates: List[dict]
    created_at: datetime
    last_updated: datetime

class SuspectSearchSchema(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    crime_type: Optional[str] = None
    danger_level: Optional[str] = None