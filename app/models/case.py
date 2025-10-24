from sqlalchemy import Column, String, Text, Boolean, JSON, ForeignKey, DateTime, Enum as SQLEnum, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class CaseStatus(str, enum.Enum):
    INTAKE = "intake"
    ASSESSMENT = "assessment"
    INTERVENTION = "intervention"
    MONITORING = "monitoring"
    CLOSED = "closed"

class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EntryVisibility(str, enum.Enum):
    PRIVATE = "private"
    SHARED = "shared"

class EntryType(str, enum.Enum):
    SESSION_NOTE = "session_note"
    OBSERVATION = "observation"
    ASSESSMENT_RESULT = "assessment_result"
    CONTACT_LOG = "contact_log"

class Case(Base):
    __tablename__ = "cases"
    
    case_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    status = Column(SQLEnum(CaseStatus), nullable=False, default=CaseStatus.INTAKE)
    risk_level = Column(SQLEnum(RiskLevel), nullable=False, default=RiskLevel.LOW)
    tags = Column(ARRAY(String), nullable=True)
    assigned_counsellor = Column(UUID(as_uuid=True), nullable=True)
    ai_summary = Column(Text, nullable=True)  # AI-generated case summary
    processed = Column(Boolean, default=False, nullable=False)  # Whether case has been reviewed/processed
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="cases")
    creator = relationship("User", foreign_keys=[created_by], back_populates="cases_created")
    journal_entries = relationship("JournalEntry", back_populates="case")

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    entry_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.case_id"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    visibility = Column(SQLEnum(EntryVisibility), nullable=False, default=EntryVisibility.SHARED)
    type = Column(SQLEnum(EntryType), nullable=False)
    content = Column(Text, nullable=True)  # Text content (optional, but one of content/audio_url required)
    audio_url = Column(String, nullable=True)  # Audio recording URL (optional, but one of content/audio_url required)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    case = relationship("Case", back_populates="journal_entries")
    author = relationship("User", back_populates="journal_entries")
