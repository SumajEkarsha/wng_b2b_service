from sqlalchemy import Column, String, Text, JSON, ForeignKey, DateTime, Enum as SQLEnum, Integer, ARRAY, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class ResourceType(str, enum.Enum):
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    ARTICLE = "ARTICLE"
    RESEARCH_PAPER = "RESEARCH_PAPER"
    SPECIAL = "SPECIAL"

class ResourceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"

class Resource(Base):
    __tablename__ = "resources"
    
    resource_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.school_id"), nullable=True)  # Null = global resource
    type = Column(SQLEnum(ResourceType), nullable=False)
    status = Column(SQLEnum(ResourceStatus), nullable=False, default=ResourceStatus.PUBLISHED)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    video_url = Column(String, nullable=True)
    audio_url = Column(String, nullable=True)
    article_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    
    author_name = Column(String, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    posted_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    duration_seconds = Column(Integer, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    category = Column(String, nullable=True)
    target_audience = Column(ARRAY(String), nullable=True)
    view_count = Column(Integer, default=0)
    additional_metadata = Column(JSON, nullable=True)
    
    # Pricing fields
    is_free = Column(Boolean, nullable=False, default=True)
    price = Column(Numeric(10, 2), nullable=True)  # Price with 2 decimal places
    currency = Column(String(3), nullable=True, default="USD")  # ISO 4217 currency code
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    school = relationship("School", back_populates="resources")
    author = relationship("User", back_populates="resources_authored")
