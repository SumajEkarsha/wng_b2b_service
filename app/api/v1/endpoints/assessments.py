from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.models.assessment import Assessment
from app.schemas.assessment import AssessmentCreate, AssessmentResponse, AssessmentSubmit

router = APIRouter()

@router.post("/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_data: AssessmentCreate,
    db: Session = Depends(get_db)
):
    assessment = Assessment(
        template_id=assessment_data.template_id,
        student_id=assessment_data.student_id,
        created_by=assessment_data.created_by
    )
    
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment

@router.post("/{assessment_id}/submit", response_model=AssessmentResponse)
async def submit_assessment(
    assessment_id: UUID,
    submission: AssessmentSubmit,
    db: Session = Depends(get_db)
):
    assessment = db.query(Assessment).filter(Assessment.assessment_id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Convert Pydantic model to dict if needed
    responses_dict = submission.responses.dict() if hasattr(submission.responses, 'dict') else submission.responses
    
    # Store responses
    assessment.responses = responses_dict
    assessment.completed_at = datetime.utcnow()
    
    # Calculate scores automatically
    assessment.scores = calculate_assessment_scores(responses_dict)
    
    db.commit()
    db.refresh(assessment)
    return assessment

@router.get("/{assessment_id}/score", response_model=dict)
async def get_assessment_score(
    assessment_id: UUID,
    db: Session = Depends(get_db)
):
    assessment = db.query(Assessment).filter(Assessment.assessment_id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Placeholder for scoring logic
    return {
        "assessment_id": str(assessment.assessment_id),
        "scores": assessment.scores or {},
        "completed_at": assessment.completed_at
    }

@router.get("/", response_model=List[AssessmentResponse])
async def list_assessments(
    student_id: UUID,  # Required parameter
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Assessment).filter(Assessment.student_id == student_id)
    assessments = query.offset(skip).limit(limit).all()
    return assessments
