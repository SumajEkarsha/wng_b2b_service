from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.calendar_event import EventType, EventStatus


class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: EventType
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: Optional[List[UUID]] = None
    status: EventStatus = EventStatus.SCHEDULED


class CalendarEventCreate(CalendarEventBase):
    school_id: UUID
    related_case_id: Optional[UUID] = None
    related_student_id: Optional[UUID] = None


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[EventType] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    attendees: Optional[List[UUID]] = None
    status: Optional[EventStatus] = None
    related_case_id: Optional[UUID] = None
    related_student_id: Optional[UUID] = None


class CalendarEvent(CalendarEventBase):
    event_id: UUID
    school_id: UUID
    related_case_id: Optional[UUID]
    related_student_id: Optional[UUID]
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
