from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.resource import ResourceType, ResourceStatus

class ResourceMetadata(BaseModel):
    """Additional metadata for resources"""
    language: Optional[str] = Field(default="English", description="Content language")
    reading_level: Optional[str] = Field(default=None, description="Reading level (e.g., Elementary, Middle School)")
    format: Optional[str] = Field(default=None, description="Format details")
    source: Optional[str] = Field(default=None, description="Original source or publisher")
    license: Optional[str] = Field(default=None, description="Content license")
    
    class Config:
        json_schema_extra = {
            "example": {
                "language": "English",
                "reading_level": "High School",
                "format": "MP4",
                "source": "Mental Health Foundation",
                "license": "Creative Commons"
            }
        }

class ResourceCreate(BaseModel):
    school_id: Optional[UUID] = Field(default=None, description="School ID (null for global resources)")
    type: ResourceType = Field(..., description="Type of resource")
    status: ResourceStatus = Field(default=ResourceStatus.PUBLISHED, description="Publication status")
    title: str = Field(..., min_length=1, max_length=300, description="Resource title")
    description: Optional[str] = Field(default=None, description="Detailed description")
    video_url: Optional[str] = Field(default=None, description="Video URL (required for video type)")
    audio_url: Optional[str] = Field(default=None, description="Audio URL (required for audio type)")
    article_url: Optional[str] = Field(default=None, description="Article URL (required for article type)")
    thumbnail_url: Optional[str] = Field(default=None, description="Thumbnail image URL")
    author_name: str = Field(..., description="Author or creator name")
    author_id: Optional[UUID] = Field(default=None, description="Author user ID if internal")
    posted_date: Optional[datetime] = Field(default=None, description="Publication date")
    duration_seconds: Optional[int] = Field(default=None, ge=0, description="Duration in seconds (for video/audio)")
    tags: Optional[List[str]] = Field(default=None, description="Tags for categorization")
    category: Optional[str] = Field(default=None, description="Primary category")
    target_audience: Optional[List[str]] = Field(default=None, description="Target audience (e.g., students, parents, teachers)")
    additional_metadata: Optional[ResourceMetadata] = Field(default=None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "school_id": None,
                "type": "video",
                "status": "published",
                "title": "Understanding Anxiety in Teens: Recognition and Management",
                "description": "A comprehensive 20-minute guide to recognizing and managing anxiety in adolescents. This evidence-based video covers common anxiety symptoms in teenagers, the difference between normal worry and clinical anxiety, practical coping strategies including breathing exercises and cognitive techniques, and guidance on when to seek professional help. Features interviews with mental health professionals and real stories from teens who have successfully managed their anxiety.",
                "video_url": "https://resources.mentalhealthfoundation.org/videos/teen-anxiety-guide.mp4",
                "audio_url": None,
                "article_url": None,
                "thumbnail_url": "https://resources.mentalhealthfoundation.org/thumbnails/teen-anxiety-guide.jpg",
                "author_name": "Dr. Sarah Johnson, Clinical Psychologist",
                "author_id": None,
                "posted_date": "2024-10-15T10:00:00Z",
                "duration_seconds": 1200,
                "tags": ["anxiety", "mental-health", "teens", "coping-strategies", "adolescent-health", "stress-management"],
                "category": "Mental Health Education",
                "target_audience": ["students", "parents", "teachers", "counsellors"],
                "additional_metadata": {
                    "language": "English",
                    "reading_level": "High School",
                    "format": "MP4, 1080p",
                    "source": "Mental Health Foundation",
                    "license": "Creative Commons BY-NC-SA 4.0"
                }
            }
        }

class ResourceUpdate(BaseModel):
    type: Optional[ResourceType] = Field(default=None, description="Type of resource")
    status: Optional[ResourceStatus] = Field(default=None, description="Publication status")
    title: Optional[str] = Field(default=None, min_length=1, max_length=300, description="Resource title")
    description: Optional[str] = Field(default=None, description="Detailed description")
    video_url: Optional[str] = Field(default=None, description="Video URL")
    audio_url: Optional[str] = Field(default=None, description="Audio URL")
    article_url: Optional[str] = Field(default=None, description="Article URL")
    thumbnail_url: Optional[str] = Field(default=None, description="Thumbnail image URL")
    author_name: Optional[str] = Field(default=None, description="Author or creator name")
    author_id: Optional[UUID] = Field(default=None, description="Author user ID")
    posted_date: Optional[datetime] = Field(default=None, description="Publication date")
    duration_seconds: Optional[int] = Field(default=None, ge=0, description="Duration in seconds")
    tags: Optional[List[str]] = Field(default=None, description="Tags for categorization")
    category: Optional[str] = Field(default=None, description="Primary category")
    target_audience: Optional[List[str]] = Field(default=None, description="Target audience")
    additional_metadata: Optional[ResourceMetadata] = Field(default=None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "published",
                "tags": ["anxiety", "mental-health", "teens", "updated"]
            }
        }

class ResourceResponse(BaseModel):
    resource_id: UUID
    school_id: Optional[UUID] = None
    type: ResourceType
    status: ResourceStatus
    title: str
    description: Optional[str] = None
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    article_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    author_name: str
    author_id: Optional[UUID] = None
    posted_date: datetime
    duration_seconds: Optional[int] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    target_audience: Optional[List[str]] = None
    view_count: int
    additional_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "resource_id": "123e4567-e89b-12d3-a456-426614174080",
                "school_id": None,
                "type": "video",
                "status": "published",
                "title": "Understanding Anxiety in Teens",
                "description": "A comprehensive guide to recognizing and managing anxiety in adolescents.",
                "video_url": "https://example.com/videos/anxiety-teens.mp4",
                "audio_url": None,
                "article_url": None,
                "thumbnail_url": "https://example.com/thumbnails/anxiety-teens.jpg",
                "author_name": "Dr. Sarah Johnson",
                "author_id": None,
                "posted_date": "2024-10-15T10:00:00Z",
                "duration_seconds": 1200,
                "tags": ["anxiety", "mental-health", "teens"],
                "category": "Mental Health Education",
                "target_audience": ["students", "parents", "teachers"],
                "view_count": 1523,
                "additional_metadata": {
                    "language": "English",
                    "source": "Mental Health Foundation"
                },
                "created_at": "2024-10-15T09:00:00Z",
                "updated_at": "2024-10-20T14:30:00Z"
            }
        }

class ResourceListResponse(BaseModel):
    resource_id: UUID
    type: ResourceType
    status: ResourceStatus
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    author_name: str
    posted_date: datetime
    duration_seconds: Optional[int] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    view_count: int
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "resource_id": "123e4567-e89b-12d3-a456-426614174080",
                "type": "video",
                "status": "published",
                "title": "Understanding Anxiety in Teens",
                "description": "A comprehensive guide to recognizing and managing anxiety.",
                "thumbnail_url": "https://example.com/thumbnails/anxiety-teens.jpg",
                "author_name": "Dr. Sarah Johnson",
                "posted_date": "2024-10-15T10:00:00Z",
                "duration_seconds": 1200,
                "tags": ["anxiety", "mental-health", "teens"],
                "category": "Mental Health Education",
                "view_count": 1523
            }
        }
