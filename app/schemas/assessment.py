from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class AssessmentCreate(BaseModel):
    template_id: Optional[UUID] = Field(default=None, description="ID of the assessment template to use")
    student_id: UUID = Field(..., description="ID of the student being assessed")
    created_by: UUID = Field(..., description="ID of the user creating the assessment")
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "123e4567-e89b-12d3-a456-426614174060",
                "student_id": "123e4567-e89b-12d3-a456-426614174003",
                "created_by": "123e4567-e89b-12d3-a456-426614174020"
            }
        }

class AssessmentSubmit(BaseModel):
    responses: Dict[str, Any] = Field(..., description="Assessment responses as key-value pairs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "responses": {
                    "q1_feeling_sad": 3,
                    "q2_loss_of_interest": 2,
                    "q3_sleep_problems": 4,
                    "q4_energy_level": 2,
                    "q5_concentration": 3,
                    "q6_appetite_changes": 1,
                    "q7_feeling_worthless": 2,
                    "q8_thoughts_of_death": 0,
                    "notes": "Student reports increased stress due to upcoming exams"
                }
            }
        }

class AssessmentResponse(BaseModel):
    assessment_id: UUID
    template_id: Optional[UUID] = None
    student_id: UUID
    responses: Optional[Dict[str, Any]] = None
    scores: Optional[Dict[str, Any]] = None
    created_by: UUID
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "assessment_id": "123e4567-e89b-12d3-a456-426614174070",
                "template_id": "123e4567-e89b-12d3-a456-426614174060",
                "student_id": "123e4567-e89b-12d3-a456-426614174003",
                "responses": {
                    "q1_feeling_sad": 3,
                    "q2_loss_of_interest": 2,
                    "q3_sleep_problems": 4
                },
                "scores": {
                    "overall": 17,
                    "depression_subscale": 12,
                    "anxiety_subscale": 5,
                    "interpretation": "Moderate symptoms"
                },
                "created_by": "123e4567-e89b-12d3-a456-426614174020",
                "completed_at": "2024-10-20T15:45:00Z",
                "created_at": "2024-10-20T15:30:00Z"
            }
        }
