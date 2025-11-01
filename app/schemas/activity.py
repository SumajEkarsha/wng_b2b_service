from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.activity import ActivityType


class ActivityBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: ActivityType
    duration: Optional[int] = None
    target_grades: Optional[List[str]] = None
    materials: Optional[List[str]] = None
    instructions: Optional[List[str]] = None
    objectives: Optional[List[str]] = None


class ActivityCreate(ActivityBase):
    school_id: Optional[UUID] = None


class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[ActivityType] = None
    duration: Optional[int] = None
    target_grades: Optional[List[str]] = None
    materials: Optional[List[str]] = None
    instructions: Optional[List[str]] = None
    objectives: Optional[List[str]] = None


class Activity(ActivityBase):
    activity_id: UUID
    school_id: Optional[UUID]
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
