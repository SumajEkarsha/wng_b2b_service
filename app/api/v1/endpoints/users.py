from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.school import School
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.api.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # Validate school exists
    school = db.query(School).filter(School.school_id == user_data.school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Convert Pydantic models to dict for JSON storage
    profile_dict = user_data.profile.dict() if user_data.profile and hasattr(user_data.profile, 'dict') else user_data.profile
    availability_dict = user_data.availability.dict() if user_data.availability and hasattr(user_data.availability, 'dict') else user_data.availability
    
    user = User(
        email=user_data.email,
        display_name=user_data.display_name,
        role=user_data.role,
        phone=user_data.phone,
        school_id=user_data.school_id,
        hashed_password=get_password_hash(user_data.password),
        profile=profile_dict,
        availability=availability_dict
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/", response_model=List[UserResponse])
async def list_users(
    school_id: UUID = None,
    role: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all users with optional filtering by school and role"""
    query = db.query(User)
    
    if school_id:
        query = query.filter(User.school_id == school_id)
    if role:
        query = query.filter(User.role == role)
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.dict(exclude_unset=True)
    
    # Convert Pydantic models to dict for JSON storage
    if 'profile' in update_data and update_data['profile'] is not None:
        if hasattr(update_data['profile'], 'dict'):
            update_data['profile'] = update_data['profile'].dict()
    
    if 'availability' in update_data and update_data['availability'] is not None:
        if hasattr(update_data['availability'], 'dict'):
            update_data['availability'] = update_data['availability'].dict()
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a user"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check for dependencies based on role
    from app.models.case import Case
    from app.models.class_model import Class
    from app.models.user import UserRole
    
    dependencies = []
    
    # Check if user created any cases
    cases_created = db.query(Case).filter(Case.created_by == user_id).count()
    if cases_created > 0:
        dependencies.append(f"{cases_created} case(s) created")
    
    # Check if counsellor has assigned cases
    if user.role == UserRole.COUNSELLOR:
        assigned_cases = db.query(Case).filter(Case.assigned_counsellor == user_id).count()
        if assigned_cases > 0:
            dependencies.append(f"{assigned_cases} assigned case(s)")
    
    # Check if teacher has assigned classes
    if user.role == UserRole.TEACHER:
        assigned_classes = db.query(Class).filter(Class.teacher_id == user_id).count()
        if assigned_classes > 0:
            dependencies.append(f"{assigned_classes} assigned class(es)")
    
    if dependencies:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete user. They have: {', '.join(dependencies)}. Please reassign or remove these first."
        )
    
    db.delete(user)
    db.commit()
    
    return {
        "success": True,
        "message": "User deleted successfully",
        "user_id": str(user_id),
        "email": user.email
    }
