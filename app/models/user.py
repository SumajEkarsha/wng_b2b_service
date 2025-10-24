from sqlalchemy import Column, String, JSON, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    COUNSELLOR = "counsellor"
    TEACHER = "teacher"
    PRINCIPAL = "principal"
    PARENT = "parent"
    CLINICIAN = "clinician"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.school_id"), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=True)
    display_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    profile = Column(JSON, nullable=True)  # qualifications, languages, specialties
    availability = Column(JSON, nullable=True)  # weekly blocks
    auth_provider = Column(JSON, nullable=True)  # SSO metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school = relationship("School", back_populates="users")
    cases_created = relationship("Case", foreign_keys="Case.created_by", back_populates="creator")
    journal_entries = relationship("JournalEntry", back_populates="author")
    classes_taught = relationship("Class", foreign_keys="Class.teacher_id", back_populates="teacher")
    resources_authored = relationship("Resource", back_populates="author")
