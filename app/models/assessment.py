from sqlalchemy import Column, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

class Assessment(Base):
    __tablename__ = "assessments"
    
    assessment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), nullable=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id"), nullable=False)
    responses = Column(JSON, nullable=True)
    scores = Column(JSON, nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="assessments")
