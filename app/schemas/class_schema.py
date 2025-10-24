from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID

class ClassAdditionalInfo(BaseModel):
    """Additional information for a class"""
    room_number: Optional[str] = Field(default=None, description="Classroom number")
    schedule: Optional[Dict[str, str]] = Field(default=None, description="Class schedule (day: time)")
    subjects: Optional[list[str]] = Field(default=None, description="Subjects taught in this class")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "room_number": "B-204",
                "schedule": {
                    "Monday": "09:00-10:30",
                    "Wednesday": "09:00-10:30",
                    "Friday": "09:00-10:30"
                },
                "subjects": ["Mathematics", "Algebra II"],
                "notes": "Advanced placement class"
            }
        }

class ClassCreate(BaseModel):
    school_id: UUID = Field(..., description="ID of the school this class belongs to")
    name: str = Field(..., min_length=1, max_length=200, description="Class name")
    grade: str = Field(..., description="Grade level (e.g., 9, 10, 11, 12)")
    section: Optional[str] = Field(default=None, description="Section identifier (e.g., A, B, C)")
    academic_year: Optional[str] = Field(default=None, description="Academic year (e.g., 2024-2025)")
    teacher_id: Optional[UUID] = Field(default=None, description="ID of the assigned teacher")
    capacity: Optional[int] = Field(default=None, ge=1, le=100, description="Maximum student capacity")
    additional_info: Optional[ClassAdditionalInfo] = Field(default=None, description="Additional class information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "school_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Algebra II - Section A",
                "grade": "10",
                "section": "A",
                "academic_year": "2024-2025",
                "teacher_id": "123e4567-e89b-12d3-a456-426614174015",
                "capacity": 30,
                "additional_info": {
                    "room_number": "B-204",
                    "schedule": {
                        "Monday": "09:00-10:30",
                        "Wednesday": "09:00-10:30"
                    },
                    "subjects": ["Mathematics", "Algebra II"]
                }
            }
        }

class ClassUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Class name")
    grade: Optional[str] = Field(default=None, description="Grade level")
    section: Optional[str] = Field(default=None, description="Section identifier")
    academic_year: Optional[str] = Field(default=None, description="Academic year")
    teacher_id: Optional[UUID] = Field(default=None, description="ID of the assigned teacher")
    capacity: Optional[int] = Field(default=None, ge=1, le=100, description="Maximum student capacity")
    additional_info: Optional[ClassAdditionalInfo] = Field(default=None, description="Additional class information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "teacher_id": "123e4567-e89b-12d3-a456-426614174016",
                "capacity": 32
            }
        }

class ClassResponse(BaseModel):
    class_id: UUID
    school_id: UUID
    name: str
    grade: str
    section: Optional[str] = None
    academic_year: Optional[str] = None
    teacher_id: Optional[UUID] = None
    capacity: Optional[int] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "class_id": "123e4567-e89b-12d3-a456-426614174001",
                "school_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Algebra II - Section A",
                "grade": "10",
                "section": "A",
                "academic_year": "2024-2025",
                "teacher_id": "123e4567-e89b-12d3-a456-426614174015",
                "capacity": 30
            }
        }
