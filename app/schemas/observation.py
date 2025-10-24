from pydantic import BaseModel, field_validator, model_validator, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.observation import Severity

class ObservationCreate(BaseModel):
    student_id: UUID = Field(..., description="ID of the student being observed")
    reported_by: UUID = Field(..., description="ID of the user reporting the observation")
    severity: Severity = Field(..., description="Severity level of the observation")
    category: Optional[str] = Field(default=None, description="Category of observation (e.g., behavioral, emotional, academic)")
    content: Optional[str] = Field(default=None, description="Text description of the observation")
    audio_url: Optional[str] = Field(default=None, description="URL to audio recording of the observation")
    
    @model_validator(mode='after')
    def check_content_or_audio(self):
        if not self.content and not self.audio_url:
            raise ValueError('At least one of content or audio_url must be provided')
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174003",
                "reported_by": "123e4567-e89b-12d3-a456-426614174015",
                "severity": "medium",
                "category": "behavioral",
                "content": "Student appeared withdrawn during class discussion. Did not participate when called upon and avoided eye contact. This is unusual behavior for this student.",
                "audio_url": None
            }
        }

class ObservationResponse(BaseModel):
    observation_id: UUID
    student_id: UUID
    reported_by: UUID
    severity: Severity
    category: Optional[str] = None
    content: Optional[str] = None
    audio_url: Optional[str] = None
    ai_summary: Optional[str] = None
    processed: bool = False
    timestamp: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "observation_id": "123e4567-e89b-12d3-a456-426614174050",
                "student_id": "123e4567-e89b-12d3-a456-426614174003",
                "reported_by": "123e4567-e89b-12d3-a456-426614174015",
                "severity": "medium",
                "category": "behavioral",
                "content": "Student appeared withdrawn during class discussion.",
                "audio_url": None,
                "ai_summary": "Student showing signs of social withdrawal and reduced engagement in classroom activities.",
                "processed": False,
                "timestamp": "2024-10-20T09:15:00Z"
            }
        }
