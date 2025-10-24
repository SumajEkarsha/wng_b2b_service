from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.models.observation import Observation
from app.schemas.observation import ObservationCreate, ObservationResponse

router = APIRouter()

@router.post("/", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED)
async def create_observation(
    observation_data: ObservationCreate,
    db: Session = Depends(get_db)
):
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
    return observation

@router.get("/", response_model=List[ObservationResponse])
async def list_observations(
    student_id: UUID,  # Required parameter
    skip: int = 0,
    limit: int = 100,
    severity: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Observation).filter(Observation.student_id == student_id)
    if severity:
        query = query.filter(Observation.severity == severity)
    observations = query.offset(skip).limit(limit).all()
    return observations

@router.get("/{observation_id}", response_model=ObservationResponse)
async def get_observation(
    observation_id: UUID,
    db: Session = Depends(get_db)
):
    observation = db.query(Observation).filter(Observation.observation_id == observation_id).first()
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    return observation

@router.post("/{observation_id}/process", response_model=ObservationResponse)
async def process_observation(
    observation_id: UUID,
    db: Session = Depends(get_db)
):
    """Mark an observation as processed/reviewed"""
    observation = db.query(Observation).filter(Observation.observation_id == observation_id).first()
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    
    observation.processed = True
    db.commit()
    db.refresh(observation)
    return observation
