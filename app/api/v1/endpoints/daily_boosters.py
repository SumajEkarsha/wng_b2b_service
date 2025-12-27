from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db
from app.core.logging_config import get_logger
from app.models.daily_booster import DailyBooster, BoosterType
from app.schemas.daily_booster import (
    DailyBooster as DailyBoosterSchema,
    DailyBoosterCreate,
    DailyBoosterUpdate
)

# Initialize logger
logger = get_logger(__name__)

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
    logger.debug("Listing daily boosters", extra={"extra_data": {"school_id": str(school_id) if school_id else None, "booster_type": str(booster_type) if booster_type else None}})
    query = db.query(DailyBooster)
    if school_id:
        query = query.filter(DailyBooster.school_id == school_id)
    if booster_type:
        query = query.filter(DailyBooster.type == booster_type)
    boosters = query.offset(skip).limit(limit).all()
    logger.debug(f"Found {len(boosters)} daily boosters")
    return boosters


@router.get("/{booster_id}", response_model=DailyBoosterSchema)
def get_daily_booster(booster_id: UUID, db: Session = Depends(get_db)):
    """Get a specific daily booster by ID"""
    logger.debug(f"Fetching daily booster: {booster_id}")
    booster = db.query(DailyBooster).filter(DailyBooster.booster_id == booster_id).first()
    if not booster:
        logger.warning(f"Daily booster not found: {booster_id}")
        raise HTTPException(status_code=404, detail="Daily booster not found")
    return booster


@router.post("/", response_model=DailyBoosterSchema, status_code=201)
def create_daily_booster(booster: DailyBoosterCreate, db: Session = Depends(get_db)):
    """Create a new daily booster"""
    logger.info("Creating daily booster", extra={"extra_data": {"school_id": str(booster.school_id) if booster.school_id else None}})
    # TODO: Get created_by from authenticated user
    db_booster = DailyBooster(**booster.model_dump(), created_by=booster.school_id or UUID('00000000-0000-0000-0000-000000000000'))
    db.add(db_booster)
    db.commit()
    db.refresh(db_booster)
    logger.info(f"Daily booster created", extra={"extra_data": {"booster_id": str(db_booster.booster_id)}})
    return db_booster


@router.put("/{booster_id}", response_model=DailyBoosterSchema)
def update_daily_booster(
    booster_id: UUID,
    booster: DailyBoosterUpdate,
    db: Session = Depends(get_db)
):
    """Update a daily booster"""
    logger.info(f"Updating daily booster: {booster_id}")
    db_booster = db.query(DailyBooster).filter(DailyBooster.booster_id == booster_id).first()
    if not db_booster:
        logger.warning(f"Daily booster update failed - not found: {booster_id}")
        raise HTTPException(status_code=404, detail="Daily booster not found")
    
    for key, value in booster.model_dump(exclude_unset=True).items():
        setattr(db_booster, key, value)
    
    db.commit()
    db.refresh(db_booster)
    logger.info(f"Daily booster updated", extra={"extra_data": {"booster_id": str(booster_id)}})
    return db_booster


@router.delete("/{booster_id}", status_code=204)
def delete_daily_booster(booster_id: UUID, db: Session = Depends(get_db)):
    """Delete a daily booster"""
    logger.info(f"Deleting daily booster: {booster_id}")
    db_booster = db.query(DailyBooster).filter(DailyBooster.booster_id == booster_id).first()
    if not db_booster:
        logger.warning(f"Daily booster deletion failed - not found: {booster_id}")
        raise HTTPException(status_code=404, detail="Daily booster not found")
    
    db.delete(db_booster)
    db.commit()
    logger.info(f"Daily booster deleted", extra={"extra_data": {"booster_id": str(booster_id)}})
    return None
