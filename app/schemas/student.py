from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from uuid import UUID
from app.models.student import Gender

class StudentCreate(BaseModel):
    school_id: UUID = Field(..., description="ID of the school the student belongs to")
    first_name: str = Field(..., min_length=1, max_length=100, description="Student's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Student's last name")
    dob: Optional[date] = Field(default=None, description="Date of birth")
    gender: Optional[Gender] = Field(default=None, description="Student's gender")
    class_id: Optional[UUID] = Field(default=None, description="ID of the class the student is enrolled in")
    parents_id: Optional[List[UUID]] = Field(default=None, description="List of parent/guardian UUIDs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "school_id": "614077c0-9cde-4955-a384-5a0d0a1a1ef5",
                "first_name": "Ethan",
                "last_name": "Lopez",
                "dob": "2010-05-15",
                "gender": "male",
                "class_id": "8f3c4567-e89b-12d3-a456-426614174033",
                "parents_id": ["9a2b3c4d-e89b-12d3-a456-426614174045", "9a2b3c4d-e89b-12d3-a456-426614174046"]
            }
        }

class StudentUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Student's first name")
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Student's last name")
    class_id: Optional[UUID] = Field(default=None, description="ID of the class the student is enrolled in")
    parents_id: Optional[List[UUID]] = Field(default=None, description="List of parent/guardian UUIDs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "class_id": "123e4567-e89b-12d3-a456-426614174002",
                "parents_id": ["123e4567-e89b-12d3-a456-426614174003"]
            }
        }

class StudentResponse(BaseModel):
    student_id: UUID
    school_id: UUID
    first_name: str
    last_name: str
    gender: Optional[Gender] = None
    class_id: Optional[UUID] = None
    parents_id: Optional[List[UUID]] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174007",
                "school_id": "614077c0-9cde-4955-a384-5a0d0a1a1ef5",
                "first_name": "Ethan",
                "last_name": "Lopez",
                "gender": "male",
                "class_id": "8f3c4567-e89b-12d3-a456-426614174033",
                "parents_id": ["9a2b3c4d-e89b-12d3-a456-426614174045", "9a2b3c4d-e89b-12d3-a456-426614174046"]
            }
        }
