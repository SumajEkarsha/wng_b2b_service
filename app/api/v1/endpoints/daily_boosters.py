from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db
from app.models.daily_booster import DailyBooster, BoosterType
from app.schemas.daily_booster import (
    DailyBooster as DailyBoosterSchema,
    DailyBoosterCreate,
    DailyBoosterUpdate
)

router = APIRouter()


@router.get("/", response_model=List[DailyBoosterSchema])
def get_daily_boosters(
    skip: int = 0,
    limit: int = 100,
    school_id: UUID = None,
    booster_type: BoosterType = None,
    db: Session = Depends(get_db)
):
    """Get all daily boosters with optional filtering"""
    query = db.query(DailyBooster)
    if school_id:
        query = query.filter(DailyBooster.school_id == school_id)
    if booster_type:
        query = query.filter(DailyBooster.type == booster_type)
    return query.offset(skip).limit(limit).all()


@router.get("/{booster_id}", response_model=DailyBoosterSchema)
def get_daily_booster(booster_id: UUID, db: Session = Depends(get_db)):
    """Get a specific daily booster by ID"""
    booster = db.query(DailyBooster).filter(DailyBooster.booster_id == booster_id).first()
    if not booster:
        raise HTTPException(status_code=404, detail="Daily booster not found")
    return booster


@router.post("/", response_model=DailyBoosterSchema, status_code=201)
def create_daily_booster(booster: DailyBoosterCreate, db: Session = Depends(get_db)):
    """Create a new daily booster"""
    # TODO: Get created_by from authenticated user
    db_booster = DailyBooster(**booster.model_dump(), created_by=booster.school_id or UUID('00000000-0000-0000-0000-000000000000'))
    db.add(db_booster)
    db.commit()
    db.refresh(db_booster)
    return db_booster


@router.put("/{booster_id}", response_model=DailyBoosterSchema)
def update_daily_booster(
    booster_id: UUID,
    booster: DailyBoosterUpdate,
    db: Session = Depends(get_db)
):
    """Update a daily booster"""
    db_booster = db.query(DailyBooster).filter(DailyBooster.booster_id == booster_id).first()
    if not db_booster:
        raise HTTPException(status_code=404, detail="Daily booster not found")
    
    for key, value in booster.model_dump(exclude_unset=True).items():
        setattr(db_booster, key, value)
    
    db.commit()
    db.refresh(db_booster)
    return db_booster


@router.delete("/{booster_id}", status_code=204)
def delete_daily_booster(booster_id: UUID, db: Session = Depends(get_db)):
    """Delete a daily booster"""
    db_booster = db.query(DailyBooster).filter(DailyBooster.booster_id == booster_id).first()
    if not db_booster:
        raise HTTPException(status_code=404, detail="Daily booster not found")
    
    db.delete(db_booster)
    db.commit()
    return None
