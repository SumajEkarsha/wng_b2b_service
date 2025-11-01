from sqlalchemy import Column, JSON, ForeignKey, DateTime, String, Text, Integer, Float, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    RATING_SCALE = "rating_scale"
    TEXT = "text"
    YES_NO = "yes_no"
    LIKERT_SCALE = "likert_scale"

class AssessmentTemplate(Base):
    __tablename__ = "assessment_templates"
    
    template_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # e.g., "depression", "anxiety", "behavioral"
    questions = Column(JSON, nullable=False)  # Array of question objects
    scoring_rules = Column(JSON, nullable=True)  # Rules for calculating scores
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    assessments = relationship("Assessment", back_populates="template")

class Assessment(Base):
    __tablename__ = "assessments"
    
    assessment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("assessment_templates.template_id"), nullable=False)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.school_id"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.class_id"), nullable=True)  # Optional: assign to specific class
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    title = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    excluded_students = Column(ARRAY(UUID(as_uuid=True)), nullable=True, default=[])  # Students excluded from this assessment

    # Relationships
    template = relationship("AssessmentTemplate", back_populates="assessments")
    school = relationship("School")
    class_obj = relationship("Class")
    creator = relationship("User", foreign_keys=[created_by], back_populates="assessments_created")
    responses = relationship("StudentResponse", back_populates="assessment", cascade="all, delete-orphan")

class StudentResponse(Base):
    __tablename__ = "student_responses"
    
    response_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.assessment_id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id"), nullable=False)
    question_id = Column(String(100), nullable=False)
    question_text = Column(Text, nullable=False)
    answer = Column(JSON, nullable=False)
    score = Column(Float, nullable=True)
    completed_at = Column(DateTime, nullable=True)  # When this student completed all questions
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="responses")
    student = relationship("Student")
