from sqlalchemy import Column, ForeignKey, DateTime, Enum as SQLEnum, Integer, Text, Date, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class BookingStatus(str, enum.Enum):
    REQUESTED = "Requested"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"

class TherapistBooking(Base):
    __tablename__ = "therapist_bookings"
    
    booking_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    therapist_id = Column(UUID(as_uuid=True), ForeignKey("therapists.therapist_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id", ondelete="SET NULL"), nullable=True, index=True)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.school_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Appointment details
    appointment_date = Column(Date, nullable=False, index=True)
    appointment_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=60)
    
    # Booking status
    status = Column(SQLEnum(BookingStatus), nullable=False, default=BookingStatus.REQUESTED, index=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    therapist = relationship("Therapist", back_populates="bookings")
    user = relationship("User", back_populates="therapist_bookings")
    student = relationship("Student", back_populates="therapist_bookings")
    school = relationship("School")

