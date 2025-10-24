from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.case import Case
from app.models.school import School
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_counsellor(
    counsellor_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new counsellor"""
    # Ensure role is counsellor
    if counsellor_data.role != UserRole.COUNSELLOR:
        raise HTTPException(
            status_code=400,
            detail="Role must be 'counsellor' for this endpoint"
        )
    
    # Validate school exists
    school = db.query(School).filter(School.school_id == counsellor_data.school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == counsellor_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    from app.core.security import get_password_hash
    
    # Convert Pydantic models to dict for JSON storage
    profile_dict = counsellor_data.profile.dict() if counsellor_data.profile and hasattr(counsellor_data.profile, 'dict') else counsellor_data.profile
    availability_dict = counsellor_data.availability.dict() if counsellor_data.availability and hasattr(counsellor_data.availability, 'dict') else counsellor_data.availability
    
    counsellor = User(
        email=counsellor_data.email,
        display_name=counsellor_data.display_name,
        role=UserRole.COUNSELLOR,
        phone=counsellor_data.phone,
        school_id=counsellor_data.school_id,
        hashed_password=get_password_hash(counsellor_data.password),
        profile=profile_dict,
        availability=availability_dict
    )
    
    db.add(counsellor)
    db.commit()
    db.refresh(counsellor)
    return counsellor

@router.get("/", response_model=List[UserResponse])
async def list_counsellors(
    school_id: UUID,  # Required parameter
    skip: int = 0,
    limit: int = 100,
    specialization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all counsellors in a school"""
    query = db.query(User).filter(
        User.school_id == school_id,
        User.role == UserRole.COUNSELLOR
    )
    
    # Filter by specialization if provided
    if specialization:
        query = query.filter(
            User.profile.contains({"specializations": [specialization]})
        )
    
    counsellors = query.offset(skip).limit(limit).all()
    return counsellors

@router.get("/{counsellor_id}", response_model=UserResponse)
async def get_counsellor(
    counsellor_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific counsellor by ID"""
    counsellor = db.query(User).filter(
        User.user_id == counsellor_id,
        User.role == UserRole.COUNSELLOR
    ).first()
    
    if not counsellor:
        raise HTTPException(status_code=404, detail="Counsellor not found")
    return counsellor

@router.get("/{counsellor_id}/cases", response_model=List[dict])
async def get_counsellor_cases(
    counsellor_id: UUID,
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all cases assigned to a counsellor"""
    counsellor = db.query(User).filter(
        User.user_id == counsellor_id,
        User.role == UserRole.COUNSELLOR
    ).first()
    
    if not counsellor:
        raise HTTPException(status_code=404, detail="Counsellor not found")
    
    query = db.query(Case).filter(Case.assigned_counsellor == counsellor_id)
    
    if status:
        query = query.filter(Case.status == status)
    
    if risk_level:
        query = query.filter(Case.risk_level == risk_level)
    
    cases = query.all()
    
    return [
        {
            "case_id": str(c.case_id),
            "student_id": str(c.student_id),
            "status": c.status.value,
            "risk_level": c.risk_level.value,
            "tags": c.tags,
            "created_at": c.created_at.isoformat(),
            "closed_at": c.closed_at.isoformat() if c.closed_at else None
        }
        for c in cases
    ]

@router.get("/{counsellor_id}/caseload", response_model=dict)
async def get_counsellor_caseload(
    counsellor_id: UUID,
    db: Session = Depends(get_db)
):
    """Get counsellor's caseload statistics"""
    counsellor = db.query(User).filter(
        User.user_id == counsellor_id,
        User.role == UserRole.COUNSELLOR
    ).first()
    
    if not counsellor:
        raise HTTPException(status_code=404, detail="Counsellor not found")
    
    from app.models.case import CaseStatus, RiskLevel
    
    # Get all cases
    all_cases = db.query(Case).filter(Case.assigned_counsellor == counsellor_id).all()
    
    # Calculate statistics
    total_cases = len(all_cases)
    active_cases = len([c for c in all_cases if c.status != CaseStatus.CLOSED])
    closed_cases = len([c for c in all_cases if c.status == CaseStatus.CLOSED])
    
    # By risk level
    critical = len([c for c in all_cases if c.risk_level == RiskLevel.CRITICAL and c.status != CaseStatus.CLOSED])
    high = len([c for c in all_cases if c.risk_level == RiskLevel.HIGH and c.status != CaseStatus.CLOSED])
    medium = len([c for c in all_cases if c.risk_level == RiskLevel.MEDIUM and c.status != CaseStatus.CLOSED])
    low = len([c for c in all_cases if c.risk_level == RiskLevel.LOW and c.status != CaseStatus.CLOSED])
    
    # By status
    intake = len([c for c in all_cases if c.status == CaseStatus.INTAKE])
    assessment = len([c for c in all_cases if c.status == CaseStatus.ASSESSMENT])
    intervention = len([c for c in all_cases if c.status == CaseStatus.INTERVENTION])
    monitoring = len([c for c in all_cases if c.status == CaseStatus.MONITORING])
    
    return {
        "counsellor_id": str(counsellor_id),
        "counsellor_name": counsellor.display_name,
        "total_cases": total_cases,
        "active_cases": active_cases,
        "closed_cases": closed_cases,
        "by_risk_level": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low
        },
        "by_status": {
            "intake": intake,
            "assessment": assessment,
            "intervention": intervention,
            "monitoring": monitoring,
            "closed": closed_cases
        }
    }

@router.patch("/{counsellor_id}", response_model=UserResponse)
async def update_counsellor(
    counsellor_id: UUID,
    counsellor_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update counsellor information"""
    counsellor = db.query(User).filter(
        User.user_id == counsellor_id,
        User.role == UserRole.COUNSELLOR
    ).first()
    
    if not counsellor:
        raise HTTPException(status_code=404, detail="Counsellor not found")
    
    update_data = counsellor_update.dict(exclude_unset=True)
    
    # Convert Pydantic models to dict for JSON storage
    if 'profile' in update_data and update_data['profile'] is not None:
        if hasattr(update_data['profile'], 'dict'):
            update_data['profile'] = update_data['profile'].dict()
    
    if 'availability' in update_data and update_data['availability'] is not None:
        if hasattr(update_data['availability'], 'dict'):
            update_data['availability'] = update_data['availability'].dict()
    
    for field, value in update_data.items():
        setattr(counsellor, field, value)
    
    db.commit()
    db.refresh(counsellor)
    return counsellor

@router.delete("/{counsellor_id}")
async def delete_counsellor(
    counsellor_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a counsellor"""
    counsellor = db.query(User).filter(
        User.user_id == counsellor_id,
        User.role == UserRole.COUNSELLOR
    ).first()
    
    if not counsellor:
        raise HTTPException(status_code=404, detail="Counsellor not found")
    
    # Check if counsellor has assigned cases
    cases = db.query(Case).filter(Case.assigned_counsellor == counsellor_id).count()
    if cases > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete counsellor. They have {cases} assigned case(s). Please reassign cases first."
        )
    
    db.delete(counsellor)
    db.commit()
    return {"success": True, "message": "Counsellor deleted successfully", "counsellor_id": str(counsellor_id)}
