from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class AssignmentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

class ActivityAssignment(Base):
    __tablename__ = "activity_assignments"
    
    assignment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activity_id = Column(UUID(as_uuid=True), ForeignKey("activities.activity_id"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.class_id"), nullable=False)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    due_date = Column(DateTime, nullable=True)
    status = Column(SQLEnum(AssignmentStatus), default=AssignmentStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    activity = relationship("Activity")
    class_obj = relationship("Class")
    assigner = relationship("User")
    submissions = relationship("ActivitySubmission", back_populates="assignment")
