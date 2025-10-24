from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.core.response import success_response
from app.models.observation import Observation
from app.models.user import User, UserRole
from app.schemas.observation import ObservationCreate, ObservationResponse

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_observation(
    observation_data: ObservationCreate,
    db: Session = Depends(get_db)
):
    # Validate reporter exists
    reporter = db.query(User).filter(User.user_id == observation_data.reported_by).first()
    if not reporter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporter not found"
        )

    observation = Observation(
        student_id=observation_data.student_id,
        reported_by=observation_data.reported_by,
        severity=observation_data.severity,
        category=observation_data.category,
        content=observation_data.content,
        audio_url=observation_data.audio_url
    )

    db.add(observation)
    db.commit()
    db.refresh(observation)

    # Build response with reporter information
    response_data = {
        "observation_id": observation.observation_id,
        "student_id": observation.student_id,
        "reported_by": observation.reported_by,
        "reporter_name": reporter.display_name,
        "reporter_role": reporter.role.value,
        "severity": observation.severity,
        "category": observation.category,
        "content": observation.content,
        "audio_url": observation.audio_url,
        "ai_summary": observation.ai_summary,
        "processed": observation.processed,
        "timestamp": observation.timestamp
    }

    return success_response(response_data)

@router.get("/")
async def list_observations(
    student_id: UUID,  # Required parameter
    skip: int = 0,
    limit: int = 100,
    severity: str = None,
    db: Session = Depends(get_db)
):
    # Fetch observations with reporter information
    query = (
        db.query(Observation)
        .options(joinedload(Observation.reporter))
        .filter(Observation.student_id == student_id)
    )
    if severity:
        query = query.filter(Observation.severity == severity)

    observations = query.offset(skip).limit(limit).all()

    # Build response data with reporter information
    result = []
    for observation in observations:
        observation_data = {
            "observation_id": observation.observation_id,
            "student_id": observation.student_id,
            "reported_by": observation.reported_by,
            "reporter_name": observation.reporter.display_name if observation.reporter else None,
            "reporter_role": observation.reporter.role.value if observation.reporter else None,
            "severity": observation.severity,
            "category": observation.category,
            "content": observation.content,
            "audio_url": observation.audio_url,
            "ai_summary": observation.ai_summary,
            "processed": observation.processed,
            "timestamp": observation.timestamp
        }
        result.append(observation_data)

    return success_response(result)

@router.get("/{observation_id}")
async def get_observation(
    observation_id: UUID,
    db: Session = Depends(get_db)
):
    # Fetch observation with reporter information
    observation = (
        db.query(Observation)
        .options(joinedload(Observation.reporter))
        .filter(Observation.observation_id == observation_id)
        .first()
    )

    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")

    # Build response data with reporter information
    response_data = {
        "observation_id": observation.observation_id,
        "student_id": observation.student_id,
        "reported_by": observation.reported_by,
        "reporter_name": observation.reporter.display_name if observation.reporter else None,
        "reporter_role": observation.reporter.role.value if observation.reporter else None,
        "severity": observation.severity,
        "category": observation.category,
        "content": observation.content,
        "audio_url": observation.audio_url,
        "ai_summary": observation.ai_summary,
        "processed": observation.processed,
        "timestamp": observation.timestamp
    }

    return success_response(response_data)

@router.post("/{observation_id}/process")
async def process_observation(
    observation_id: UUID,
    db: Session = Depends(get_db)
):
    """Mark an observation as processed/reviewed"""
    # Fetch observation with reporter information
    observation = (
        db.query(Observation)
        .options(joinedload(Observation.reporter))
        .filter(Observation.observation_id == observation_id)
        .first()
    )

    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")

    observation.processed = True
    db.commit()
    db.refresh(observation)

    # Build response data with reporter information
    response_data = {
        "observation_id": observation.observation_id,
        "student_id": observation.student_id,
        "reported_by": observation.reported_by,
        "reporter_name": observation.reporter.display_name if observation.reporter else None,
        "reporter_role": observation.reporter.role.value if observation.reporter else None,
        "severity": observation.severity,
        "category": observation.category,
        "content": observation.content,
        "audio_url": observation.audio_url,
        "ai_summary": observation.ai_summary,
        "processed": observation.processed,
        "timestamp": observation.timestamp
    }

    return success_response(response_data)
