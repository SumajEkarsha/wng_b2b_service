from sqlalchemy import Column, String, Date, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class Student(Base):
    __tablename__ = "students"
    
    student_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.school_id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    pseudonym = Column(String, nullable=True)
    dob = Column(Date, nullable=True)
    gender = Column(SQLEnum(Gender), nullable=True)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.class_id"), nullable=True)
    parent_email = Column(String, nullable=True)
    parent_phone = Column(String, nullable=True)
    additional_info = Column(JSON, nullable=True)  # Renamed from metadata to avoid SQLAlchemy conflict
    
    # Relationships
    school = relationship("School", back_populates="students")
    class_obj = relationship("Class", back_populates="students")
    cases = relationship("Case", back_populates="student")
    assessments = relationship("Assessment", back_populates="student")
    observations = relationship("Observation", back_populates="student")
