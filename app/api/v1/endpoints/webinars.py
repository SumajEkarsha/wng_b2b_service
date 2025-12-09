from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.core.response import success_response
from app.core.logging_config import get_logger
from app.models.webinar import Webinar, WebinarCategory, WebinarStatus, WebinarLevel
from app.models.webinar_registration import WebinarRegistration, RegistrationStatus
from app.schemas.webinar import (
    WebinarCreate, WebinarUpdate, WebinarResponse, WebinarListResponse,
    WebinarRegistrationCreate, WebinarRegistrationResponse
)

# Initialize logger
logger = get_logger(__name__)

router = APIRouter()

@router.get("")
async def list_webinars(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all webinars with optional filtering"""
    query = db.query(Webinar)
    
    if category and category != "all":
        query = query.filter(Webinar.category == category)
    
    if status and status != "all":
        query = query.filter(Webinar.status == status)
    
    if level:
        query = query.filter(Webinar.level == level)
    
    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(
            Webinar.title.ilike(pattern),
            Webinar.description.ilike(pattern),
            Webinar.speaker_name.ilike(pattern)
        ))
    
    query = query.order_by(Webinar.date.desc())
    total = query.count()
    webinars = query.offset(skip).limit(limit).all()
    
    return success_response({
        "webinars": webinars,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    })

@router.get("/my-registrations")
async def get_my_registrations(
    school_id: UUID,  # Changed from user_id to school_id
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get registrations for a school"""
    query = db.query(WebinarRegistration).filter(WebinarRegistration.school_id == school_id)
    
    if status:
        query = query.filter(WebinarRegistration.status == status)
    
    registrations = query.order_by(WebinarRegistration.registered_at.desc()).all()
    
    return success_response({"registrations": registrations})

@router.get("/{webinar_id}")
async def get_webinar(webinar_id: UUID, db: Session = Depends(get_db)):
    """Get a single webinar by ID"""
    webinar = db.query(Webinar).filter(Webinar.webinar_id == webinar_id).first()
    if not webinar:
        raise HTTPException(status_code=404, detail="Webinar not found")
    
    # Increment views
    webinar.views += 1
    db.commit()
    db.refresh(webinar)
    
    return success_response(webinar)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_webinar(webinar_data: WebinarCreate, db: Session = Depends(get_db)):
    """Create a new webinar (Admin only)"""
    webinar = Webinar(**webinar_data.dict())
    db.add(webinar)
    db.commit()
    db.refresh(webinar)
    return success_response(webinar)

@router.put("/{webinar_id}")
async def update_webinar(
    webinar_id: UUID,
    webinar_update: WebinarUpdate,
    db: Session = Depends(get_db)
):
    """Update a webinar (Admin only)"""
    webinar = db.query(Webinar).filter(Webinar.webinar_id == webinar_id).first()
    if not webinar:
        raise HTTPException(status_code=404, detail="Webinar not found")
    
    for field, value in webinar_update.dict(exclude_unset=True).items():
        setattr(webinar, field, value)
    
    webinar.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(webinar)
    return success_response(webinar)

@router.delete("/{webinar_id}")
async def delete_webinar(webinar_id: UUID, db: Session = Depends(get_db)):
    """Delete a webinar (Admin only)"""
    webinar = db.query(Webinar).filter(Webinar.webinar_id == webinar_id).first()
    if not webinar:
        raise HTTPException(status_code=404, detail="Webinar not found")
    
    db.delete(webinar)
    db.commit()
    return success_response({"message": "Webinar deleted successfully", "webinar_id": str(webinar_id)})

@router.post("/{webinar_id}/register")
async def register_for_webinar(
    webinar_id: UUID,
    school_id: UUID,
    user_id: UUID,  # Get from authenticated user
    db: Session = Depends(get_db)
):
    """Register for a webinar"""
    # Check if webinar exists
    webinar = db.query(Webinar).filter(Webinar.webinar_id == webinar_id).first()
    if not webinar:
        raise HTTPException(status_code=404, detail="Webinar not found")
    
    # Check if already registered
    existing = db.query(WebinarRegistration).filter(
        and_(
            WebinarRegistration.webinar_id == webinar_id,
            WebinarRegistration.school_id == school_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already registered for this webinar")
    
    # Check capacity
    if webinar.max_attendees and webinar.attendee_count >= webinar.max_attendees:
        raise HTTPException(status_code=400, detail="Webinar is full")
    
    # Create registration
    registration = WebinarRegistration(
        webinar_id=webinar_id,
        user_id=user_id,  # Use actual user_id from auth
        school_id=school_id,
        status=RegistrationStatus.REGISTERED
    )
    db.add(registration)
    
    # Update attendee count
    webinar.attendee_count += 1
    
    db.commit()
    db.refresh(registration)
    
    return success_response(registration)

@router.post("/{webinar_id}/unregister")
async def unregister_from_webinar(
    webinar_id: UUID,
    user_id: UUID,  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """Unregister current user from a webinar"""
    registration = db.query(WebinarRegistration).filter(
        and_(
            WebinarRegistration.webinar_id == webinar_id,
            WebinarRegistration.user_id == user_id,
            WebinarRegistration.status == RegistrationStatus.REGISTERED
        )
    ).first()
    
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    # Update registration status
    registration.status = RegistrationStatus.CANCELLED
    registration.cancelled_at = datetime.utcnow()
    
    # Update attendee count
    webinar = db.query(Webinar).filter(Webinar.webinar_id == webinar_id).first()
    if webinar:
        webinar.attendee_count = max(0, webinar.attendee_count - 1)
    
    db.commit()
    
    return success_response({"message": "Successfully unregistered", "registration_id": str(registration.registration_id)})
