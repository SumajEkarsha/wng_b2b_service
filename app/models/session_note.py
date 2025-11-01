from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Enum as SQLEnum, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class SessionType(str, enum.Enum):
    INDIVIDUAL = "INDIVIDUAL"
    GROUP = "GROUP"
    ASSESSMENT = "ASSESSMENT"
    CONSULTATION = "CONSULTATION"

class SessionNote(Base):
    __tablename__ = "session_notes"
    
    session_note_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.case_id"), nullable=False)
    counsellor_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    duration = Column(Integer, nullable=True)  # Duration in minutes
    type = Column(SQLEnum(SessionType), nullable=False)
    summary = Column(Text, nullable=True)
    interventions = Column(ARRAY(String), nullable=True)
    next_steps = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    case = relationship("Case", back_populates="session_notes")
    counsellor = relationship("User", back_populates="session_notes")
