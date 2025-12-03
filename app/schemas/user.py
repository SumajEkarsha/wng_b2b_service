from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Union
from datetime import datetime
from uuid import UUID
from app.models.user import UserRole

# Profile Schemas for Different Roles

class TeacherProfile(BaseModel):
    """Profile schema for teachers"""
    subjects: Optional[List[str]] = Field(default=[], description="Subjects taught (e.g., Mathematics, English)")
    qualifications: Optional[List[str]] = Field(default=[], description="Educational qualifications (e.g., M.Ed, B.Sc)")
    years_experience: Optional[int] = Field(default=0, description="Years of teaching experience")
    certifications: Optional[List[str]] = Field(default=[], description="Additional certifications (e.g., Special Education)")
    grade_levels: Optional[List[str]] = Field(default=[], description="Grade levels taught (e.g., 9, 10, 11, 12)")
    bio: Optional[str] = Field(default=None, description="Brief biography")
    
    class Config:
        json_schema_extra = {
            "example": {
                "subjects": ["Mathematics", "Physics"],
                "qualifications": ["M.Ed Mathematics", "B.Sc Physics"],
                "years_experience": 10,
                "certifications": ["Special Education", "Trauma-Informed Care"],
                "grade_levels": ["9", "10", "11"],
                "bio": "Passionate about making math accessible to all students"
            }
        }

class CounsellorProfile(BaseModel):
    """Profile schema for counsellors"""
    specializations: Optional[List[str]] = Field(default=[], description="Areas of expertise (e.g., Anxiety, Depression, Trauma)")
    qualifications: Optional[List[str]] = Field(default=[], description="Professional qualifications and degrees")
    license_number: Optional[str] = Field(default=None, description="Professional license number")
    license_type: Optional[str] = Field(default=None, description="Type of license (e.g., LCSW, LPC, LMFT)")
    languages: Optional[List[str]] = Field(default=["English"], description="Languages spoken")
    certifications: Optional[List[str]] = Field(default=[], description="Therapeutic certifications (e.g., CBT, DBT)")
    years_experience: Optional[int] = Field(default=0, description="Years of counseling experience")
    approach: Optional[str] = Field(default=None, description="Therapeutic approach/philosophy")
    bio: Optional[str] = Field(default=None, description="Professional biography")
    
    class Config:
        json_schema_extra = {
            "example": {
                "specializations": ["Anxiety", "Depression", "Trauma", "ADHD"],
                "qualifications": ["Licensed Clinical Social Worker", "M.A. Counseling Psychology"],
                "license_number": "LCSW-12345",
                "license_type": "LCSW",
                "languages": ["English", "Spanish"],
                "certifications": ["CBT Certified", "DBT Trained", "Play Therapy"],
                "years_experience": 8,
                "approach": "Cognitive Behavioral Therapy with trauma-informed care",
                "bio": "Dedicated to supporting adolescent mental health"
            }
        }

class PrincipalProfile(BaseModel):
    """Profile schema for principals"""
    qualifications: Optional[List[str]] = Field(default=[], description="Educational leadership qualifications")
    years_in_role: Optional[int] = Field(default=0, description="Years as principal")
    years_in_education: Optional[int] = Field(default=0, description="Total years in education")
    previous_schools: Optional[List[str]] = Field(default=[], description="Previous schools led")
    certifications: Optional[List[str]] = Field(default=[], description="Leadership certifications")
    bio: Optional[str] = Field(default=None, description="Professional biography")
    
    class Config:
        json_schema_extra = {
            "example": {
                "qualifications": ["Ed.D Educational Leadership", "M.Ed School Administration"],
                "years_in_role": 5,
                "years_in_education": 20,
                "previous_schools": ["Lincoln High School", "Washington Middle School"],
                "certifications": ["School Leadership Certificate", "Mental Health First Aid"],
                "bio": "Committed to creating a supportive learning environment"
            }
        }

class AdminProfile(BaseModel):
    """Profile schema for administrators"""
    qualifications: Optional[List[str]] = Field(default=[], description="Administrative qualifications")
    department: Optional[str] = Field(default=None, description="Department or area of responsibility")
    years_experience: Optional[int] = Field(default=0, description="Years of administrative experience")
    certifications: Optional[List[str]] = Field(default=[], description="Relevant certifications")
    bio: Optional[str] = Field(default=None, description="Professional biography")
    
    class Config:
        json_schema_extra = {
            "example": {
                "qualifications": ["M.Ed Educational Administration", "B.A. Psychology"],
                "department": "Student Services",
                "years_experience": 12,
                "certifications": ["Mental Health First Aid", "Crisis Intervention"],
                "bio": "Focused on student wellbeing and support services"
            }
        }

class ParentProfile(BaseModel):
    """Profile schema for parents"""
    preferred_contact_method: Optional[str] = Field(default="email", description="Preferred contact method")
    languages: Optional[List[str]] = Field(default=["English"], description="Languages spoken")
    emergency_contact: Optional[bool] = Field(default=True, description="Can be contacted in emergencies")
    relationship: Optional[str] = Field(default=None, description="Relationship to student (e.g., Mother, Father, Guardian)")
    occupation: Optional[str] = Field(default=None, description="Occupation (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "preferred_contact_method": "email",
                "languages": ["English", "Spanish"],
                "emergency_contact": True,
                "relationship": "Mother",
                "occupation": "Software Engineer"
            }
        }

# Availability Schema

class AvailabilityBlock(BaseModel):
    """Time block for availability"""
    day: str = Field(..., description="Day of week (Monday-Sunday)")
    start_time: str = Field(..., description="Start time (HH:MM format)")
    end_time: str = Field(..., description="End time (HH:MM format)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "day": "Monday",
                "start_time": "09:00",
                "end_time": "15:00"
            }
        }

class Availability(BaseModel):
    """Weekly availability schedule"""
    blocks: List[AvailabilityBlock] = Field(default=[], description="Available time blocks")
    timezone: Optional[str] = Field(default="UTC", description="Timezone")
    notes: Optional[str] = Field(default=None, description="Additional availability notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "blocks": [
                    {"day": "Monday", "start_time": "09:00", "end_time": "15:00"},
                    {"day": "Tuesday", "start_time": "09:00", "end_time": "15:00"},
                    {"day": "Wednesday", "start_time": "09:00", "end_time": "12:00"}
                ],
                "timezone": "America/New_York",
                "notes": "Available for emergency consultations after hours"
            }
        }

# User Schemas

class UserBase(BaseModel):
    email: EmailStr
    display_name: str
    role: UserRole
    phone: Optional[str] = None
    profile_picture_url: Optional[str] = None

class UserCreate(UserBase):
    password: str
    school_id: UUID
    profile: Optional[Union[TeacherProfile, CounsellorProfile, PrincipalProfile, AdminProfile, ParentProfile, dict]] = None
    availability: Optional[Union[Availability, dict]] = None
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "email": "david.chen@lincolnhs.edu",
                    "display_name": "Dr. David Chen",
                    "role": "counsellor",
                    "phone": "+1-555-0123",
                    "password": "SecurePassword123!",
                    "school_id": "614077c0-9cde-4955-a384-5a0d0a1a1ef5",
                    "profile": {
                        "specializations": ["Anxiety", "Depression", "Trauma", "Academic Stress"],
                        "qualifications": ["Licensed Clinical Social Worker", "M.A. Counseling Psychology"],
                        "license_number": "LCSW-12345",
                        "license_type": "LCSW",
                        "languages": ["English", "Mandarin"],
                        "certifications": ["CBT Certified", "DBT Trained", "Play Therapy"],
                        "years_experience": 8,
                        "approach": "Cognitive Behavioral Therapy with trauma-informed care",
                        "bio": "Dedicated to supporting adolescent mental health and wellbeing"
                    },
                    "availability": {
                        "blocks": [
                            {"day": "Monday", "start_time": "08:00", "end_time": "16:00"},
                            {"day": "Tuesday", "start_time": "08:00", "end_time": "16:00"},
                            {"day": "Wednesday", "start_time": "08:00", "end_time": "16:00"},
                            {"day": "Thursday", "start_time": "08:00", "end_time": "16:00"},
                            {"day": "Friday", "start_time": "08:00", "end_time": "14:00"}
                        ],
                        "timezone": "America/Chicago",
                        "notes": "Available for emergency consultations after hours by appointment"
                    }
                },
                {
                    "email": "sarah.johnson@lincolnhs.edu",
                    "display_name": "Ms. Sarah Johnson",
                    "role": "teacher",
                    "phone": "+1-555-0145",
                    "password": "TeacherPass456!",
                    "school_id": "614077c0-9cde-4955-a384-5a0d0a1a1ef5",
                    "profile": {
                        "subjects": ["Mathematics", "Algebra II", "Calculus"],
                        "qualifications": ["M.Ed Mathematics Education", "B.Sc Mathematics"],
                        "years_experience": 12,
                        "certifications": ["Advanced Placement Certified", "Special Education"],
                        "grade_levels": ["9", "10", "11", "12"],
                        "bio": "Passionate about making mathematics accessible and engaging for all students"
                    },
                    "availability": {
                        "blocks": [
                            {"day": "Monday", "start_time": "07:30", "end_time": "15:30"},
                            {"day": "Tuesday", "start_time": "07:30", "end_time": "15:30"},
                            {"day": "Wednesday", "start_time": "07:30", "end_time": "15:30"},
                            {"day": "Thursday", "start_time": "07:30", "end_time": "15:30"},
                            {"day": "Friday", "start_time": "07:30", "end_time": "15:30"}
                        ],
                        "timezone": "America/Chicago",
                        "notes": "Office hours: Tuesday and Thursday 3:30-4:30 PM"
                    }
                },
                {
                    "email": "jane.doe@email.com",
                    "display_name": "Jane Doe",
                    "role": "parent",
                    "phone": "+1-555-0178",
                    "password": "ParentPass789!",
                    "school_id": "614077c0-9cde-4955-a384-5a0d0a1a1ef5",
                    "profile": {
                        "preferred_contact_method": "email",
                        "languages": ["English"],
                        "emergency_contact": True,
                        "relationship": "Mother",
                        "occupation": "Software Engineer"
                    }
                }
            ]
        }

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    phone: Optional[str] = None
    profile_picture_url: Optional[str] = None
    profile: Optional[Union[TeacherProfile, CounsellorProfile, PrincipalProfile, AdminProfile, ParentProfile, dict]] = None
    availability: Optional[Union[Availability, dict]] = None

class UserResponse(UserBase):
    user_id: UUID
    school_id: UUID
    profile_picture_url: Optional[str] = None
    profile: Optional[dict] = None
    availability: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174021",
                "email": "david.chen@lincolnhs.edu",
                "display_name": "Dr. David Chen",
                "role": "counsellor",
                "phone": "+1-555-0123",
                "school_id": "614077c0-9cde-4955-a384-5a0d0a1a1ef5",
                "profile": {
                    "specializations": ["Anxiety", "Depression", "Trauma", "Academic Stress"],
                    "qualifications": ["Licensed Clinical Social Worker", "M.A. Counseling Psychology"],
                    "license_number": "LCSW-12345",
                    "license_type": "LCSW",
                    "languages": ["English", "Mandarin"],
                    "certifications": ["CBT Certified", "DBT Trained", "Play Therapy"],
                    "years_experience": 8,
                    "approach": "Cognitive Behavioral Therapy with trauma-informed care",
                    "bio": "Dedicated to supporting adolescent mental health and wellbeing"
                },
                "availability": {
                    "blocks": [
                        {"day": "Monday", "start_time": "08:00", "end_time": "16:00"},
                        {"day": "Tuesday", "start_time": "08:00", "end_time": "16:00"},
                        {"day": "Wednesday", "start_time": "08:00", "end_time": "16:00"},
                        {"day": "Thursday", "start_time": "08:00", "end_time": "16:00"},
                        {"day": "Friday", "start_time": "08:00", "end_time": "14:00"}
                    ],
                    "timezone": "America/Chicago",
                    "notes": "Available for emergency consultations after hours by appointment"
                },
                "created_at": "2024-01-15T10:30:00Z"
            }
        }

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[UUID] = None
