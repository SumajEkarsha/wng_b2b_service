from pydantic import BaseModel, Field, UUID4
from typing import Optional, List
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum

class AvailabilityStatus(str, Enum):
    AVAILABLE = "Available"
    LIMITED = "Limited"
    UNAVAILABLE = "Unavailable"

class BookingStatus(str, Enum):
    REQUESTED = "Requested"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"

# Therapist schemas
class TherapistBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    specialty: str
    bio: Optional[str] = None
    location: str
    city: str
    state: Optional[str] = None
    distance_km: Optional[Decimal] = None
    experience_years: int = Field(..., ge=0)
    languages: List[str]
    availability_status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    consultation_fee_min: Decimal = Field(..., ge=0)
    consultation_fee_max: Decimal = Field(..., ge=0)
    qualifications: Optional[List[dict]] = []
    areas_of_expertise: Optional[List[str]] = []
    profile_image_url: Optional[str] = None
    verified: bool = False

class TherapistCreate(TherapistBase):
    pass

class TherapistUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    specialty: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    languages: Optional[List[str]] = None
    availability_status: Optional[AvailabilityStatus] = None
    consultation_fee_min: Optional[Decimal] = Field(None, ge=0)
    consultation_fee_max: Optional[Decimal] = Field(None, ge=0)
    qualifications: Optional[List[dict]] = None
    areas_of_expertise: Optional[List[str]] = None
    profile_image_url: Optional[str] = None
    verified: Optional[bool] = None

class TherapistResponse(TherapistBase):
    therapist_id: UUID4
    rating: Decimal
    review_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TherapistListResponse(BaseModel):
    therapists: List[TherapistResponse]
    total: int
    page: int
    page_size: int

# Booking schemas
class TherapistBookingCreate(BaseModel):
    therapist_id: UUID4
    student_id: Optional[UUID4] = None
    appointment_date: date
    appointment_time: time
    duration_minutes: int = Field(default=60, gt=0)
    notes: Optional[str] = None

class TherapistBookingUpdate(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    notes: Optional[str] = None
    status: Optional[BookingStatus] = None
    cancellation_reason: Optional[str] = None

class TherapistBookingResponse(BaseModel):
    booking_id: UUID4
    therapist_id: UUID4
    user_id: UUID4
    student_id: Optional[UUID4] = None
    appointment_date: date
    appointment_time: time
    duration_minutes: int
    status: BookingStatus
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    therapist: Optional[TherapistResponse] = None

    class Config:
        from_attributes = True

class TherapistBookingListResponse(BaseModel):
    bookings: List[TherapistBookingResponse]
    total: int
    page: int
    page_size: int
