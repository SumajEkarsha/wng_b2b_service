from pydantic import BaseModel, model_validator, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.case import CaseStatus, RiskLevel, EntryVisibility, EntryType

class CaseCreate(BaseModel):
    student_id: UUID = Field(..., description="ID of the student this case is for")
    created_by: UUID = Field(..., description="ID of the user creating the case")
    presenting_concerns: Optional[str] = Field(default=None, description="Initial concerns or reasons for opening the case")
    initial_risk: RiskLevel = Field(default=RiskLevel.LOW, description="Initial risk assessment level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174003",
                "created_by": "123e4567-e89b-12d3-a456-426614174010",
                "presenting_concerns": "Student showing signs of anxiety and social withdrawal. Teacher reports decreased participation in class.",
                "initial_risk": "medium"
            }
        }

class CaseUpdate(BaseModel):
    status: Optional[CaseStatus] = Field(default=None, description="Case status")
    risk_level: Optional[RiskLevel] = Field(default=None, description="Risk level assessment")
    tags: Optional[List[str]] = Field(default=None, description="Tags for categorization (e.g., anxiety, depression)")
    assigned_counsellor: Optional[UUID] = Field(default=None, description="ID of assigned counsellor")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "intervention",
                "risk_level": "high",
                "tags": ["anxiety", "social-withdrawal", "academic-stress"],
                "assigned_counsellor": "123e4567-e89b-12d3-a456-426614174020"
            }
        }

class CaseResponse(BaseModel):
    case_id: UUID
    student_id: UUID
    created_by: UUID
    status: CaseStatus
    risk_level: RiskLevel
    tags: Optional[List[str]] = None
    assigned_counsellor: Optional[UUID] = None
    ai_summary: Optional[str] = None
    processed: bool = False
    created_at: datetime
    closed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "case_id": "123e4567-e89b-12d3-a456-426614174030",
                "student_id": "123e4567-e89b-12d3-a456-426614174003",
                "created_by": "123e4567-e89b-12d3-a456-426614174010",
                "status": "intervention",
                "risk_level": "medium",
                "tags": ["anxiety", "social-withdrawal"],
                "assigned_counsellor": "123e4567-e89b-12d3-a456-426614174020",
                "ai_summary": "Student experiencing moderate anxiety related to academic performance and peer relationships.",
                "processed": False,
                "created_at": "2024-10-20T10:30:00Z",
                "closed_at": None
            }
        }

class JournalEntryCreate(BaseModel):
    case_id: UUID = Field(..., description="ID of the case this entry belongs to")
    author_id: UUID = Field(..., description="ID of the user creating the entry")
    visibility: EntryVisibility = Field(default=EntryVisibility.SHARED, description="Who can view this entry")
    type: EntryType = Field(..., description="Type of journal entry")
    content: Optional[str] = Field(default=None, description="Text content of the entry")
    audio_url: Optional[str] = Field(default=None, description="URL to audio recording")
    
    @model_validator(mode='after')
    def check_content_or_audio(self):
        if not self.content and not self.audio_url:
            raise ValueError('At least one of content or audio_url must be provided')
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "123e4567-e89b-12d3-a456-426614174030",
                "author_id": "123e4567-e89b-12d3-a456-426614174020",
                "visibility": "shared",
                "type": "session_note",
                "content": "Met with student for 45-minute session. Discussed coping strategies for test anxiety. Student was receptive and engaged. Assigned breathing exercises homework.",
                "audio_url": None
            }
        }

class JournalEntryResponse(BaseModel):
    entry_id: UUID
    case_id: UUID
    author_id: UUID
    visibility: EntryVisibility
    type: EntryType
    content: Optional[str] = None
    audio_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "entry_id": "123e4567-e89b-12d3-a456-426614174040",
                "case_id": "123e4567-e89b-12d3-a456-426614174030",
                "author_id": "123e4567-e89b-12d3-a456-426614174020",
                "visibility": "shared",
                "type": "session_note",
                "content": "Met with student for 45-minute session. Progress noted in anxiety management.",
                "audio_url": None,
                "created_at": "2024-10-20T14:30:00Z"
            }
        }
