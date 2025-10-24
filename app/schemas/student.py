from pydantic import BaseModel, Field
from typing import Optional
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
    
    class Config:
        json_schema_extra = {
            "example": {
                "school_id": "123e4567-e89b-12d3-a456-426614174000",
                "first_name": "John",
                "last_name": "Doe",
                "dob": "2010-05-15",
                "gender": "male",
                "class_id": "123e4567-e89b-12d3-a456-426614174001"
            }
        }

class StudentUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Student's first name")
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Student's last name")
    class_id: Optional[UUID] = Field(default=None, description="ID of the class the student is enrolled in")
    
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "class_id": "123e4567-e89b-12d3-a456-426614174002"
            }
        }

class StudentResponse(BaseModel):
    student_id: UUID
    school_id: UUID
    first_name: str
    last_name: str
    gender: Optional[Gender] = None
    class_id: Optional[UUID] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174003",
                "school_id": "123e4567-e89b-12d3-a456-426614174000",
                "first_name": "John",
                "last_name": "Doe",
                "gender": "male",
                "class_id": "123e4567-e89b-12d3-a456-426614174001"
            }
        }
