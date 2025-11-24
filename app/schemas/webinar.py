from pydantic import BaseModel, Field, UUID4
from typing import Optional, List
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum

class WebinarCategory(str, Enum):
    STUDENT_WELLBEING = "Student Wellbeing"
    MENTAL_HEALTH = "Mental Health"
    CRISIS_MANAGEMENT = "Crisis Management"
    PROFESSIONAL_DEVELOPMENT = "Professional Development"
    COMMUNICATION = "Communication"
    SELF_CARE = "Self-Care"
    SAFETY = "Safety"
    LEARNING_DISABILITIES = "Learning Disabilities"
    COUNSELING_SKILLS = "Counseling Skills"
    CURRICULUM = "Curriculum"
    INCLUSION = "Inclusion"

class WebinarStatus(str, Enum):
    UPCOMING = "Upcoming"
    LIVE = "Live"
    RECORDED = "Recorded"
    CANCELLED = "Cancelled"

class WebinarLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    ALL_LEVELS = "All Levels"

class RegistrationStatus(str, Enum):
    REGISTERED = "Registered"
    ATTENDED = "Attended"
    CANCELLED = "Cancelled"

# Base schemas
class WebinarBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    speaker_name: str
    speaker_title: Optional[str] = None
    speaker_bio: Optional[str] = None
    speaker_image_url: Optional[str] = None
    date: datetime
    duration_minutes: int = Field(..., gt=0)
    category: WebinarCategory
    status: WebinarStatus = WebinarStatus.UPCOMING
    level: WebinarLevel
    price: Decimal = Field(default=Decimal("0.00"), ge=0)
    topics: Optional[List[str]] = []
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    max_attendees: Optional[int] = Field(None, gt=0)

class WebinarCreate(WebinarBase):
    pass

class WebinarUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    speaker_name: Optional[str] = None
    speaker_title: Optional[str] = None
    speaker_bio: Optional[str] = None
    speaker_image_url: Optional[str] = None
    date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    category: Optional[WebinarCategory] = None
    status: Optional[WebinarStatus] = None
    level: Optional[WebinarLevel] = None
    price: Optional[Decimal] = Field(None, ge=0)
    topics: Optional[List[str]] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    max_attendees: Optional[int] = Field(None, gt=0)

class WebinarResponse(WebinarBase):
    webinar_id: UUID4
    attendee_count: int = 0
    views: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WebinarListResponse(BaseModel):
    webinars: List[WebinarResponse]
    total: int
    page: int
    page_size: int

# Registration schemas
class WebinarRegistrationCreate(BaseModel):
    webinar_id: UUID4

class WebinarRegistrationResponse(BaseModel):
    registration_id: UUID4
    webinar_id: UUID4
    user_id: UUID4
    school_id: UUID4
    status: RegistrationStatus
    registered_at: datetime
    attended_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    class Config:
        from_attributes = True

