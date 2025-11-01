from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.models.activity import Activity, ActivityType
from app.models.user import User
from app.schemas.activity import Activity as ActivitySchema, ActivityCreate, ActivityUpdate

router = APIRouter()


@router.get("/", response_model=List[ActivitySchema])
def get_activities(
    skip: int = 0,
    limit: int = 100,
    school_id: UUID = None,
    activity_type: ActivityType = None,
    db: Session = Depends(get_db)
):
    """Get all activities with optional filtering"""
    query = db.query(Activity)
    if school_id:
        query = query.filter(Activity.school_id == school_id)
    if activity_type:
        query = query.filter(Activity.type == activity_type)
    return query.offset(skip).limit(limit).all()


@router.get("/{activity_id}", response_model=ActivitySchema)
def get_activity(activity_id: UUID, db: Session = Depends(get_db)):
    """Get a specific activity by ID"""
    activity = db.query(Activity).filter(Activity.activity_id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.post("/", response_model=ActivitySchema, status_code=201)
async def create_activity(
    activity: ActivityCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new activity"""
    db_activity = Activity(
        **activity.model_dump(),
        created_by=current_user.user_id
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


@router.put("/{activity_id}", response_model=ActivitySchema)
async def update_activity(
    activity_id: UUID, 
    activity: ActivityUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an activity"""
    db_activity = db.query(Activity).filter(Activity.activity_id == activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    for key, value in activity.model_dump(exclude_unset=True).items():
        setattr(db_activity, key, value)
    
    db.commit()
    db.refresh(db_activity)
    return db_activity


@router.delete("/{activity_id}", status_code=204)
async def delete_activity(
    activity_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an activity"""
    db_activity = db.query(Activity).filter(Activity.activity_id == activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    db.delete(db_activity)
    db.commit()
    return None
