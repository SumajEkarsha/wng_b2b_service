from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, any_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.api.dependencies import get_db, get_current_user
from app.models.calendar_event import CalendarEvent, EventStatus
from app.models.user import User
from app.schemas.calendar_event import (
    CalendarEvent as CalendarEventSchema,
    CalendarEventCreate,
    CalendarEventUpdate
)

router = APIRouter()


@router.get("/", response_model=List[CalendarEventSchema])
def get_calendar_events(
    skip: int = 0,
    limit: int = 100,
    school_id: UUID = None,
    case_id: UUID = None,
    student_id: UUID = None,
    status: EventStatus = None,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    """Get all calendar events with optional filtering"""
    query = db.query(CalendarEvent)
    if school_id:
        query = query.filter(CalendarEvent.school_id == school_id)
    if case_id:
        query = query.filter(CalendarEvent.related_case_id == case_id)
    if student_id:
        query = query.filter(CalendarEvent.related_student_id == student_id)
    if status:
        query = query.filter(CalendarEvent.status == status)
    if start_date:
        query = query.filter(CalendarEvent.start_time >= start_date)
    if end_date:
        query = query.filter(CalendarEvent.end_time <= end_date)
    return query.order_by(CalendarEvent.start_time).offset(skip).limit(limit).all()


@router.get("/my-events", response_model=List[CalendarEventSchema])
async def get_my_calendar_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get calendar events for the current user (where they are an attendee or creator)"""
    query = db.query(CalendarEvent).filter(
        or_(
            CalendarEvent.created_by == current_user.user_id,
            CalendarEvent.attendees.any(current_user.user_id)
        )
    )
    
    if start_date:
        query = query.filter(CalendarEvent.start_time >= start_date)
    if end_date:
        query = query.filter(CalendarEvent.end_time <= end_date)
    
    return query.order_by(CalendarEvent.start_time).all()


@router.get("/check-availability", response_model=dict)
async def check_availability(
    start_time: datetime,
    end_time: datetime,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if a time slot is available for the current user"""
    conflicts = db.query(CalendarEvent).filter(
        or_(
            CalendarEvent.created_by == current_user.user_id,
            CalendarEvent.attendees.any(current_user.user_id)
        ),
        CalendarEvent.status != EventStatus.CANCELLED,
        # Check for time overlap
        or_(
            (CalendarEvent.start_time <= start_time) & (CalendarEvent.end_time > start_time),
            (CalendarEvent.start_time < end_time) & (CalendarEvent.end_time >= end_time),
            (CalendarEvent.start_time >= start_time) & (CalendarEvent.end_time <= end_time)
        )
    ).all()
    
    return {
        "available": len(conflicts) == 0,
        "conflicts": [
            {
                "event_id": str(c.event_id),
                "title": c.title,
                "start_time": c.start_time.isoformat(),
                "end_time": c.end_time.isoformat()
            }
            for c in conflicts
        ]
    }


@router.get("/{event_id}", response_model=CalendarEventSchema)
def get_calendar_event(event_id: UUID, db: Session = Depends(get_db)):
    """Get a specific calendar event by ID"""
    event = db.query(CalendarEvent).filter(CalendarEvent.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    return event


@router.post("/", response_model=CalendarEventSchema, status_code=201)
async def create_calendar_event(
    event: CalendarEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    allow_conflicts: bool = False
):
    """Create a new calendar event with conflict detection"""
    
    # Check for time conflicts with existing events for the current user
    if not allow_conflicts:
        conflicts = db.query(CalendarEvent).filter(
            or_(
                CalendarEvent.created_by == current_user.user_id,
                CalendarEvent.attendees.any(current_user.user_id)
            ),
            CalendarEvent.status != EventStatus.CANCELLED,
            # Check for time overlap
            or_(
                # New event starts during existing event
                (CalendarEvent.start_time <= event.start_time) & (CalendarEvent.end_time > event.start_time),
                # New event ends during existing event
                (CalendarEvent.start_time < event.end_time) & (CalendarEvent.end_time >= event.end_time),
                # New event completely contains existing event
                (CalendarEvent.start_time >= event.start_time) & (CalendarEvent.end_time <= event.end_time)
            )
        ).all()
        
        if conflicts:
            conflict_details = [
                {
                    "event_id": str(c.event_id),
                    "title": c.title,
                    "start_time": c.start_time.isoformat(),
                    "end_time": c.end_time.isoformat()
                }
                for c in conflicts
            ]
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Time conflict detected. You already have events scheduled during this time.",
                    "conflicts": conflict_details
                }
            )
    
    db_event = CalendarEvent(
        **event.model_dump(),
        created_by=current_user.user_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@router.put("/{event_id}", response_model=CalendarEventSchema)
async def update_calendar_event(
    event_id: UUID,
    event: CalendarEventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    allow_conflicts: bool = False
):
    """Update a calendar event with conflict detection"""
    db_event = db.query(CalendarEvent).filter(CalendarEvent.event_id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    
    # If updating time, check for conflicts
    update_data = event.model_dump(exclude_unset=True)
    if ('start_time' in update_data or 'end_time' in update_data) and not allow_conflicts:
        new_start = update_data.get('start_time', db_event.start_time)
        new_end = update_data.get('end_time', db_event.end_time)
        
        conflicts = db.query(CalendarEvent).filter(
            CalendarEvent.event_id != event_id,  # Exclude current event
            or_(
                CalendarEvent.created_by == current_user.user_id,
                CalendarEvent.attendees.any(current_user.user_id)
            ),
            CalendarEvent.status != EventStatus.CANCELLED,
            # Check for time overlap
            or_(
                (CalendarEvent.start_time <= new_start) & (CalendarEvent.end_time > new_start),
                (CalendarEvent.start_time < new_end) & (CalendarEvent.end_time >= new_end),
                (CalendarEvent.start_time >= new_start) & (CalendarEvent.end_time <= new_end)
            )
        ).all()
        
        if conflicts:
            conflict_details = [
                {
                    "event_id": str(c.event_id),
                    "title": c.title,
                    "start_time": c.start_time.isoformat(),
                    "end_time": c.end_time.isoformat()
                }
                for c in conflicts
            ]
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Time conflict detected. You already have events scheduled during this time.",
                    "conflicts": conflict_details
                }
            )
    
    for key, value in update_data.items():
        setattr(db_event, key, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event


@router.delete("/{event_id}", status_code=204)
async def delete_calendar_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a calendar event"""
    db_event = db.query(CalendarEvent).filter(CalendarEvent.event_id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    
    db.delete(db_event)
    db.commit()
    return None
