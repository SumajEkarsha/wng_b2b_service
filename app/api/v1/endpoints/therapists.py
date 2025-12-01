from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date, time
from app.core.database import get_db
from app.core.response import success_response
from app.models.therapist import Therapist, AvailabilityStatus
from app.models.therapist_booking import TherapistBooking, BookingStatus
from app.schemas.therapist import (
    TherapistCreate, TherapistUpdate, TherapistResponse, TherapistListResponse,
    TherapistBookingCreate, TherapistBookingUpdate, TherapistBookingResponse
)
from app.models.user import User, UserRole

router = APIRouter()

@router.get("")
async def list_therapists(
    skip: int = 0,
    limit: int = 100,
    specialty: Optional[str] = None,
    city: Optional[str] = None,
    availability_status: Optional[str] = None,
    min_rating: Optional[float] = None,
    language: Optional[str] = None,
    min_experience: Optional[int] = None,
    search: Optional[str] = None,
    verified_only: bool = False,
    db: Session = Depends(get_db)
):
    """List all therapists with optional filtering"""
    query = db.query(Therapist)
    
    if specialty:
        query = query.filter(Therapist.specialty == specialty)
    
    if city:
        query = query.filter(Therapist.city == city)
    
    if availability_status:
        query = query.filter(Therapist.availability_status == availability_status)
    
    if min_rating:
        query = query.filter(Therapist.rating >= min_rating)
    
    if language:
        # Search in JSON array
        query = query.filter(Therapist.languages.contains([language]))
    
    if min_experience:
        query = query.filter(Therapist.experience_years >= min_experience)
    
    if verified_only:
        query = query.filter(Therapist.verified == True)
    
    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(
            Therapist.name.ilike(pattern),
            Therapist.specialty.ilike(pattern),
            Therapist.bio.ilike(pattern)
        ))
    
    query = query.order_by(Therapist.rating.desc(), Therapist.review_count.desc())
    total = query.count()
    therapists = query.offset(skip).limit(limit).all()
    
    return success_response({
        "therapists": therapists,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    })



@router.get("/my-bookings")
async def get_my_bookings(
    user_id: UUID,  # TODO: Get from auth token
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get current user's therapist bookings"""
    query = db.query(TherapistBooking).filter(TherapistBooking.user_id == user_id)
    
    if status:
        query = query.filter(TherapistBooking.status == status)
    
    bookings = query.options(joinedload(TherapistBooking.therapist)).order_by(TherapistBooking.appointment_date.desc()).all()
    
    return success_response({"bookings": bookings})

@router.get("/{therapist_id}")
async def get_therapist(therapist_id: UUID, db: Session = Depends(get_db)):
    """Get a single therapist by ID"""
    therapist = db.query(Therapist).filter(Therapist.therapist_id == therapist_id).first()
    if not therapist:
        raise HTTPException(status_code=404, detail="Therapist not found")
    
    return success_response(therapist)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_therapist(therapist_data: TherapistCreate, db: Session = Depends(get_db)):
    """Create a new therapist (Admin only)"""
    therapist = Therapist(**therapist_data.dict())
    db.add(therapist)
    db.commit()
    db.refresh(therapist)
    return success_response(therapist)

@router.put("/{therapist_id}")
async def update_therapist(
    therapist_id: UUID,
    therapist_update: TherapistUpdate,
    db: Session = Depends(get_db)
):
    """Update a therapist (Admin only)"""
    therapist = db.query(Therapist).filter(Therapist.therapist_id == therapist_id).first()
    if not therapist:
        raise HTTPException(status_code=404, detail="Therapist not found")
    
    for field, value in therapist_update.dict(exclude_unset=True).items():
        setattr(therapist, field, value)
    
    therapist.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(therapist)
    return success_response(therapist)

@router.delete("/{therapist_id}")
async def delete_therapist(therapist_id: UUID, db: Session = Depends(get_db)):
    """Delete a therapist (Admin only)"""
    therapist = db.query(Therapist).filter(Therapist.therapist_id == therapist_id).first()
    if not therapist:
        raise HTTPException(status_code=404, detail="Therapist not found")
    
    db.delete(therapist)
    db.commit()
    return success_response({"message": "Therapist deleted successfully", "therapist_id": str(therapist_id)})

@router.post("/{therapist_id}/book")
async def book_therapist(
    therapist_id: UUID,
    booking_data: TherapistBookingCreate,
    user_id: UUID,  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """Book an appointment with a therapist"""
    # Check if therapist exists
    therapist = db.query(Therapist).filter(Therapist.therapist_id == therapist_id).first()
    if not therapist:
        raise HTTPException(status_code=404, detail="Therapist not found")
    
    if therapist.availability_status == AvailabilityStatus.UNAVAILABLE:
        raise HTTPException(status_code=400, detail="Therapist is currently unavailable")

    # Auto-register therapist as counselor if not already registered
    # First, get the booking user to find their school
    booker = db.query(User).filter(User.user_id == user_id).first()
    if booker and booker.school_id:
        # Check if this therapist is already a counselor at this school
        # We check by looking for a counselor with this therapist_id in their profile
        # Note: Using cast to String because User.profile is JSON type, not JSONB, so contains() might fail
        from sqlalchemy import cast, String
        
        existing_counsellor = db.query(User).filter(
            User.school_id == booker.school_id,
            User.role == UserRole.COUNSELLOR,
            cast(User.profile, String).like(f'%"marketplace_therapist_id": "{str(therapist_id)}"%')
        ).first()

        if not existing_counsellor:
            # Register the therapist as a counselor
            from app.core.security import get_password_hash
            import uuid
            
            # Create a unique email for the counselor at this school
            # Format: therapist.firstname.lastname.schoolid@calmbridge.edu (mock)
            safe_name = therapist.name.lower().replace(" ", ".").replace("dr.", "").replace("ms.", "").replace("mr.", "").strip(".")
            mock_email = f"{safe_name}.{str(booker.school_id)[:8]}@calmbridge.edu"
            
            # Check if email exists (unlikely with school ID suffix but good to be safe)
            if db.query(User).filter(User.email == mock_email).first():
                mock_email = f"{safe_name}.{str(booker.school_id)[:8]}.{str(uuid.uuid4())[:4]}@calmbridge.edu"

            new_counsellor = User(
                email=mock_email,
                hashed_password=get_password_hash("Welcome123!"), # Default password
                display_name=therapist.name,
                role=UserRole.COUNSELLOR,
                school_id=booker.school_id,
                profile={
                    "bio": therapist.bio,
                    "specializations": [therapist.specialty] + (therapist.areas_of_expertise or []),
                    "languages": therapist.languages,
                    "marketplace_therapist_id": str(therapist_id),
                    "image_url": therapist.profile_image_url
                },
                availability={
                    "status": "Available",
                    "hours": "9:00 AM - 5:00 PM"
                }
            )
            db.add(new_counsellor)
            db.commit()
            db.refresh(new_counsellor)
            print(f"Auto-registered therapist {therapist.name} as counselor for school {booker.school_id}")

    # Create booking
    booking = TherapistBooking(
        therapist_id=therapist_id,
        user_id=user_id,
        school_id=booker.school_id if booker else None,
        **booking_data.dict(exclude={'therapist_id'})
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    return success_response(booking)

@router.put("/bookings/{booking_id}")
async def update_booking(
    booking_id: UUID,
    booking_update: TherapistBookingUpdate,
    db: Session = Depends(get_db)
):
    """Update a booking"""
    booking = db.query(TherapistBooking).filter(TherapistBooking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    for field, value in booking_update.dict(exclude_unset=True).items():
        setattr(booking, field, value)
    
    booking.updated_at = datetime.utcnow()
    
    # Update status timestamps
    if booking.status == BookingStatus.CONFIRMED and not booking.confirmed_at:
        booking.confirmed_at = datetime.utcnow()
    elif booking.status == BookingStatus.CANCELLED and not booking.cancelled_at:
        booking.cancelled_at = datetime.utcnow()
    elif booking.status == BookingStatus.COMPLETED and not booking.completed_at:
        booking.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(booking)
    return success_response(booking)

@router.post("/bookings/{booking_id}/cancel")
async def cancel_booking(
    booking_id: UUID,
    cancellation_reason: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Cancel a booking"""
    booking = db.query(TherapistBooking).filter(TherapistBooking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Booking is already cancelled")
    
    if booking.status == BookingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Cannot cancel a completed booking")
    
    booking.status = BookingStatus.CANCELLED
    booking.cancelled_at = datetime.utcnow()
    if cancellation_reason:
        booking.cancellation_reason = cancellation_reason
    
    db.commit()
    db.refresh(booking)
    
    return success_response({"message": "Booking cancelled successfully", "booking": booking})
