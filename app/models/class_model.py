from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Class(Base):
    __tablename__ = "classes"
    
    class_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.school_id"), nullable=False)
    name = Column(String, nullable=False)  # e.g., "Grade 5-A"
    grade = Column(String, nullable=False)  # e.g., "5", "9", "12"
    section = Column(String, nullable=True)  # e.g., "A", "B", "C"
    academic_year = Column(String, nullable=True)  # e.g., "2024-2025"
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)  # Class teacher
    capacity = Column(Integer, nullable=True)
    additional_info = Column(JSON, nullable=True)
    
    # Relationships
    school = relationship("School", back_populates="classes")
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="classes_taught")
    students = relationship("Student", back_populates="class_obj")
