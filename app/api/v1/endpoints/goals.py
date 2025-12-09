from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db
from app.core.logging_config import get_logger
from app.models.goal import Goal
from app.schemas.goal import Goal as GoalSchema, GoalCreate, GoalUpdate

# Initialize logger
logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=List[GoalSchema])
def get_goals(
    skip: int = 0,
    limit: int = 100,
    case_id: UUID = None,
    db: Session = Depends(get_db)
):
    """Get all goals with optional filtering by case"""
    logger.debug("Listing goals", extra={"extra_data": {"case_id": str(case_id) if case_id else None}})
    query = db.query(Goal)
    if case_id:
        query = query.filter(Goal.case_id == case_id)
    goals = query.offset(skip).limit(limit).all()
    logger.debug(f"Found {len(goals)} goals")
    return goals


@router.get("/{goal_id}", response_model=GoalSchema)
def get_goal(goal_id: UUID, db: Session = Depends(get_db)):
    """Get a specific goal by ID"""
    logger.debug(f"Fetching goal: {goal_id}")
    goal = db.query(Goal).filter(Goal.goal_id == goal_id).first()
    if not goal:
        logger.warning(f"Goal not found: {goal_id}")
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.post("", response_model=GoalSchema, status_code=201)
def create_goal(goal: GoalCreate, db: Session = Depends(get_db)):
    """Create a new goal"""
    logger.info("Creating goal", extra={"extra_data": {"case_id": str(goal.case_id) if hasattr(goal, 'case_id') else None}})
    db_goal = Goal(**goal.model_dump())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    logger.info(f"Goal created", extra={"extra_data": {"goal_id": str(db_goal.goal_id)}})
    return db_goal


@router.put("/{goal_id}", response_model=GoalSchema)
def update_goal(goal_id: UUID, goal: GoalUpdate, db: Session = Depends(get_db)):
    """Update a goal"""
    logger.info(f"Updating goal: {goal_id}")
    db_goal = db.query(Goal).filter(Goal.goal_id == goal_id).first()
    if not db_goal:
        logger.warning(f"Goal update failed - not found: {goal_id}")
        raise HTTPException(status_code=404, detail="Goal not found")
    
    for key, value in goal.model_dump(exclude_unset=True).items():
        setattr(db_goal, key, value)
    
    db.commit()
    db.refresh(db_goal)
    logger.info(f"Goal updated", extra={"extra_data": {"goal_id": str(goal_id)}})
    return db_goal


@router.delete("/{goal_id}", status_code=204)
def delete_goal(goal_id: UUID, db: Session = Depends(get_db)):
    """Delete a goal"""
    logger.info(f"Deleting goal: {goal_id}")
    db_goal = db.query(Goal).filter(Goal.goal_id == goal_id).first()
    if not db_goal:
        logger.warning(f"Goal deletion failed - not found: {goal_id}")
        raise HTTPException(status_code=404, detail="Goal not found")
    
    db.delete(db_goal)
    db.commit()
    logger.info(f"Goal deleted", extra={"extra_data": {"goal_id": str(goal_id)}})
    return None
