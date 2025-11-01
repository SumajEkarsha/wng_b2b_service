from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.session_note import SessionType


class SessionNoteBase(BaseModel):
    date: datetime
    duration: Optional[int] = None
    type: SessionType
    summary: Optional[str] = None
    interventions: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None


class SessionNoteCreate(SessionNoteBase):
    case_id: UUID
    counsellor_id: UUID


class SessionNoteUpdate(BaseModel):
    date: Optional[datetime] = None
    duration: Optional[int] = None
    type: Optional[SessionType] = None
    summary: Optional[str] = None
    interventions: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None


class SessionNote(SessionNoteBase):
    session_note_id: UUID
    case_id: UUID
    counsellor_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
