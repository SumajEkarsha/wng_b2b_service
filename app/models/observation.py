from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class Severity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Observation(Base):
    __tablename__ = "observations"
    
    observation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id"), nullable=False)
    reported_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    severity = Column(SQLEnum(Severity), nullable=False)
    category = Column(String, nullable=True)
    content = Column(Text, nullable=True)  # Text content (optional, but one of content/audio_url required)
    audio_url = Column(String, nullable=True)  # Audio recording URL (optional, but one of content/audio_url required)
    ai_summary = Column(Text, nullable=True)  # AI-generated summary of observation
    processed = Column(Boolean, default=False, nullable=False)  # Whether observation has been reviewed/processed
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="observations")
    reporter = relationship("User", foreign_keys=[reported_by], back_populates="observations_reported")
