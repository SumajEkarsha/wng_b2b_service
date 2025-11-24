from sqlalchemy import Column, String, Text, JSON, ForeignKey, DateTime, Enum as SQLEnum, Integer, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class WebinarCategory(str, enum.Enum):
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

class WebinarStatus(str, enum.Enum):
    UPCOMING = "Upcoming"
    LIVE = "Live"
    RECORDED = "Recorded"
    CANCELLED = "Cancelled"

class WebinarLevel(str, enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    ALL_LEVELS = "All Levels"

class Webinar(Base):
    __tablename__ = "webinars"
    
    webinar_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Speaker information
    speaker_name = Column(String, nullable=False)
    speaker_title = Column(String, nullable=True)
    speaker_bio = Column(Text, nullable=True)
    speaker_image_url = Column(String, nullable=True)
    
    # Scheduling
    date = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False)
    
    # Classification
    category = Column(SQLEnum(WebinarCategory), nullable=False, index=True)
    status = Column(SQLEnum(WebinarStatus), nullable=False, default=WebinarStatus.UPCOMING, index=True)
    level = Column(SQLEnum(WebinarLevel), nullable=False)
    
    # Pricing
    price = Column(Numeric(10, 2), nullable=False, default=0)  # 0 means free
    
    # Content
    topics = Column(JSON, nullable=True)  # Array of topic strings
    video_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    
    # Capacity and metrics
    max_attendees = Column(Integer, nullable=True)  # Null = unlimited
    attendee_count = Column(Integer, default=0)
    views = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    registrations = relationship("WebinarRegistration", back_populates="webinar", cascade="all, delete-orphan")
