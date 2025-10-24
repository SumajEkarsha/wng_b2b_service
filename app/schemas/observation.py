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
                "student_id": "123e4567-e89b-12d3-a456-426614174007",
                "reported_by": "abc12345-e89b-12d3-a456-426614174055",
                "severity": "medium",
                "category": "behavioral",
                "content": "Student appeared withdrawn during class discussion today. Did not participate when called upon, avoided eye contact with peers and teacher. This is unusual behavior for Ethan, who typically is engaged and participates actively. Also noted decreased interaction during group work. Recommend follow-up with counselor.",
                "audio_url": None
            }
        }

class ObservationResponse(BaseModel):
    observation_id: UUID
    student_id: UUID
    reported_by: UUID
    reporter_name: str
    reporter_role: str
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
                "observation_id": "7f8e9012-e89b-12d3-a456-426614174088",
                "student_id": "123e4567-e89b-12d3-a456-426614174007",
                "reported_by": "abc12345-e89b-12d3-a456-426614174055",
                "reporter_name": "Ms. Sarah Johnson",
                "reporter_role": "teacher",
                "severity": "medium",
                "category": "behavioral",
                "content": "Student appeared withdrawn during class discussion today. Did not participate when called upon, avoided eye contact with peers and teacher. This is unusual behavior for Ethan, who typically is engaged and participates actively.",
                "audio_url": None,
                "ai_summary": "Teacher reports atypical withdrawn behavior and social disengagement. Student avoiding participation and peer interaction. Change from typical engaged behavior pattern warrants attention.",
                "processed": False,
                "timestamp": "2024-10-22T09:15:00Z"
            }
        }
