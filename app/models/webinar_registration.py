from sqlalchemy import Column, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class RegistrationStatus(str, enum.Enum):
    REGISTERED = "Registered"
    ATTENDED = "Attended"
    CANCELLED = "Cancelled"

class WebinarRegistration(Base):
    __tablename__ = "webinar_registrations"
    
    registration_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    webinar_id = Column(UUID(as_uuid=True), ForeignKey("webinars.webinar_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.school_id", ondelete="CASCADE"), nullable=False, index=True)
    
    status = Column(SQLEnum(RegistrationStatus), nullable=False, default=RegistrationStatus.REGISTERED)
    
    registered_at = Column(DateTime, default=datetime.utcnow)
    attended_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Relationships
    webinar = relationship("Webinar", back_populates="registrations")
    user = relationship("User", back_populates="webinar_registrations")
    school = relationship("School")

