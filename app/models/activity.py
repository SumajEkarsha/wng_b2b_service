from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Enum as SQLEnum, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class ActivityType(str, enum.Enum):
    MINDFULNESS = "MINDFULNESS"
    SOCIAL_SKILLS = "SOCIAL_SKILLS"
    EMOTIONAL_REGULATION = "EMOTIONAL_REGULATION"
    ACADEMIC_SUPPORT = "ACADEMIC_SUPPORT"
    TEAM_BUILDING = "TEAM_BUILDING"

class Activity(Base):
    __tablename__ = "activities"
    
    activity_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.school_id"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(SQLEnum(ActivityType), nullable=False)
    duration = Column(Integer, nullable=True)  # Duration in minutes
    target_grades = Column(ARRAY(String), nullable=True)
    materials = Column(ARRAY(String), nullable=True)
    instructions = Column(ARRAY(Text), nullable=True)
    objectives = Column(ARRAY(String), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school = relationship("School", back_populates="activities")
    creator = relationship("User", back_populates="activities_created")
