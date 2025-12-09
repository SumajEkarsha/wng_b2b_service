from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.core.database import get_activity_db
from app.core.logging_config import get_logger
from app.models.activity_data import ActivityData
from app.core.s3_service import s3_service

# Initialize logger
logger = get_logger(__name__)

router = APIRouter()


@router.get("/")
def get_activities(
    skip: int = 0,
    limit: int = 100,
    age: Optional[int] = Query(None, description="Filter by age"),
    diagnosis: Optional[str] = Query(None, description="Filter by diagnosis (e.g., ADHD, Anxiety)"),
    themes: Optional[str] = Query(None, description="Filter by themes (comma-separated)"),
    include_flashcards: bool = Query(False, description="Include S3 flashcard images in response"),
    db: Session = Depends(get_activity_db)
):
    """
    Get all activities with optional filtering.
    
    Filters:
    - age: Filter by exact age
    - diagnosis: Filter by diagnosis (case-insensitive partial match)
    - themes: Filter by themes (comma-separated, e.g., "Emotional Regulation,Motor Skills")
    - include_flashcards: If true, includes base64 flashcard images from S3
    """
    logger.debug(
        "Fetching activities",
        extra={"extra_data": {"age": age, "diagnosis": diagnosis, "themes": themes, "skip": skip, "limit": limit}}
    )
    
    query = db.query(ActivityData)
    
    # Filter by age
    if age is not None:
        query = query.filter(ActivityData.age == age)
    
    # Filter by diagnosis (case-insensitive partial match)
    if diagnosis:
        query = query.filter(ActivityData.diagnosis.ilike(f"%{diagnosis}%"))
    
    activities = query.offset(skip).limit(limit).all()
    logger.debug(f"Found {len(activities)} activities from database")
    
    # Parse themes filter
    theme_list = [t.strip().lower() for t in themes.split(",")] if themes else []
    
    result = []
    for activity in activities:
        act_data = activity.activity_data or {}
        
        # Filter by themes in Python (since themes are in JSONB)
        if theme_list:
            act_themes = act_data.get("Themes", [])
            act_themes_lower = " ".join([t.lower() for t in act_themes]) if isinstance(act_themes, list) else ""
            
            # Check if any theme partially matches
            if not any(t in act_themes_lower for t in theme_list):
                continue
        
        # Build response
        activity_response = {
            "activity_id": activity.activity_id,
            "activity_name": act_data.get("Activity Name") or activity.activity_name,
            "description": act_data.get("Activity Description"),
            "therapy_goal": act_data.get("Therapy Goal"),
            "learning_goal": act_data.get("Learning Goal"),
            "age": act_data.get("Age") or activity.age,
            "themes": act_data.get("Themes", []),
            "diagnosis": act_data.get("Diagnosis") or activity.diagnosis,
            "framework": activity.framework,
            "setting": activity.setting,
            "supervision": activity.supervision,
            "duration": activity.duration_pref,
            "risk_level": activity.risk_level,
            "skill_level": activity.skill_level,
            "cognitive": activity.cognitive,
            "sensory": activity.sensory,
            "instructions": act_data.get("Instructions", {}),
            "flashcards": None
        }
        
        if include_flashcards:
            activity_response["flashcards"] = s3_service.fetch_flashcards(activity.activity_id)
        
        result.append(activity_response)
    
    return {
        "filters": {
            "age": age,
            "diagnosis": diagnosis,
            "themes": theme_list if theme_list else None
        },
        "count": len(result),
        "activities": result
    }


@router.get("/{activity_id}")
def get_activity(
    activity_id: str, 
    include_flashcards: bool = Query(False, description="Include S3 flashcard images"),
    db: Session = Depends(get_activity_db)
):
    """Get a specific activity by ID"""
    logger.debug(f"Fetching activity: {activity_id}")
    
    activity = db.query(ActivityData).filter(ActivityData.activity_id == activity_id).first()
    if not activity:
        logger.warning(f"Activity not found: {activity_id}")
        raise HTTPException(status_code=404, detail="Activity not found")
    
    act_data = activity.activity_data or {}
    
    result = {
        "activity_id": activity.activity_id,
        "activity_name": act_data.get("Activity Name") or activity.activity_name,
        "description": act_data.get("Activity Description"),
        "therapy_goal": act_data.get("Therapy Goal"),
        "learning_goal": act_data.get("Learning Goal"),
        "age": act_data.get("Age") or activity.age,
        "themes": act_data.get("Themes", []),
        "diagnosis": act_data.get("Diagnosis") or activity.diagnosis,
        "framework": activity.framework,
        "setting": activity.setting,
        "supervision": activity.supervision,
        "duration": activity.duration_pref,
        "risk_level": activity.risk_level,
        "skill_level": activity.skill_level,
        "cognitive": activity.cognitive,
        "sensory": activity.sensory,
        "instructions": act_data.get("Instructions", {}),
        "flashcards": None
    }
    
    if include_flashcards:
        result["flashcards"] = s3_service.fetch_flashcards(activity.activity_id)
    
    return result



