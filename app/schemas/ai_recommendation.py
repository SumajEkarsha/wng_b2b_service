from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.ai_recommendation import RecommendationType, ConfidenceLevel


class AIRecommendationBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    type: RecommendationType
    confidence: ConfidenceLevel
    rationale: Optional[str] = None
    recommendation: str
    model_version: Optional[str] = None


class AIRecommendationCreate(AIRecommendationBase):
    related_student_id: Optional[UUID] = None
    related_case_id: Optional[UUID] = None


class AIRecommendationUpdate(BaseModel):
    is_reviewed: Optional[bool] = None
    reviewed_by: Optional[UUID] = None


class AIRecommendation(AIRecommendationBase):
    recommendation_id: UUID
    related_student_id: Optional[UUID]
    related_case_id: Optional[UUID]
    is_reviewed: bool
    reviewed_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
