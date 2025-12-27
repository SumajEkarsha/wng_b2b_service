from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db
from app.core.logging_config import get_logger
from app.models.ai_recommendation import AIRecommendation
from app.schemas.ai_recommendation import (
    AIRecommendation as AIRecommendationSchema,
    AIRecommendationCreate,
    AIRecommendationUpdate
)

# Initialize logger
logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[AIRecommendationSchema])
def get_ai_recommendations(
    skip: int = 0,
    limit: int = 100,
    student_id: UUID = None,
    case_id: UUID = None,
    is_reviewed: bool = None,
    db: Session = Depends(get_db)
):
    """Get all AI recommendations with optional filtering"""
    query = db.query(AIRecommendation)
    if student_id:
        query = query.filter(AIRecommendation.related_student_id == student_id)
    if case_id:
        query = query.filter(AIRecommendation.related_case_id == case_id)
    if is_reviewed is not None:
        query = query.filter(AIRecommendation.is_reviewed == is_reviewed)
    return query.offset(skip).limit(limit).all()


@router.get("/{recommendation_id}", response_model=AIRecommendationSchema)
def get_ai_recommendation(recommendation_id: UUID, db: Session = Depends(get_db)):
    """Get a specific AI recommendation by ID"""
    recommendation = db.query(AIRecommendation).filter(
        AIRecommendation.recommendation_id == recommendation_id
    ).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="AI recommendation not found")
    return recommendation


@router.post("/", response_model=AIRecommendationSchema, status_code=201)
def create_ai_recommendation(recommendation: AIRecommendationCreate, db: Session = Depends(get_db)):
    """Create a new AI recommendation"""
    db_recommendation = AIRecommendation(**recommendation.model_dump())
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation


@router.put("/{recommendation_id}", response_model=AIRecommendationSchema)
def update_ai_recommendation(
    recommendation_id: UUID,
    recommendation: AIRecommendationUpdate,
    db: Session = Depends(get_db)
):
    """Update an AI recommendation (typically to mark as reviewed)"""
    db_recommendation = db.query(AIRecommendation).filter(
        AIRecommendation.recommendation_id == recommendation_id
    ).first()
    if not db_recommendation:
        raise HTTPException(status_code=404, detail="AI recommendation not found")
    
    for key, value in recommendation.model_dump(exclude_unset=True).items():
        setattr(db_recommendation, key, value)
    
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation


@router.delete("/{recommendation_id}", status_code=204)
def delete_ai_recommendation(recommendation_id: UUID, db: Session = Depends(get_db)):
    """Delete an AI recommendation"""
    db_recommendation = db.query(AIRecommendation).filter(
        AIRecommendation.recommendation_id == recommendation_id
    ).first()
    if not db_recommendation:
        raise HTTPException(status_code=404, detail="AI recommendation not found")
    
    db.delete(db_recommendation)
    db.commit()
    return None
