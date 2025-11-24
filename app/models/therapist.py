from sqlalchemy import Column, String, Text, JSON, DateTime, Integer, Numeric, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class AvailabilityStatus(str, enum.Enum):
    AVAILABLE = "Available"
    LIMITED = "Limited"
    UNAVAILABLE = "Unavailable"

class Therapist(Base):
    __tablename__ = "therapists"
    
    therapist_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    name = Column(String, nullable=False, index=True)
    specialty = Column(String, nullable=False, index=True)
    bio = Column(Text, nullable=True)
    
    # Ratings and reviews
    rating = Column(Numeric(3, 2), nullable=False, default=0.0)  # 0.00 to 5.00
    review_count = Column(Integer, nullable=False, default=0)
    
    # Location
    location = Column(String, nullable=False, index=True)  # Full address
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=True)
    distance_km = Column(Numeric(10, 2), nullable=True)  # Calculated distance from user
    
    # Professional details
    experience_years = Column(Integer, nullable=False)
    languages = Column(JSON, nullable=False)  # Array of language strings
    
    # Availability and pricing
    availability_status = Column(SQLEnum(AvailabilityStatus), nullable=False, default=AvailabilityStatus.AVAILABLE, index=True)
    consultation_fee_min = Column(Numeric(10, 2), nullable=False)
    consultation_fee_max = Column(Numeric(10, 2), nullable=False)
    
    # Additional information
    qualifications = Column(JSON, nullable=True)  # Array of qualification objects
    areas_of_expertise = Column(JSON, nullable=True)  # Array of expertise strings
    
    # Media
    profile_image_url = Column(String, nullable=True)
    
    # Verification
    verified = Column(Boolean, nullable=False, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = relationship("TherapistBooking", back_populates="therapist", cascade="all, delete-orphan")
