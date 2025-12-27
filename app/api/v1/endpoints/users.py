from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
import os
import shutil
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.response import success_response
from app.core.logging_config import get_logger
from app.models.user import User
from app.models.school import School
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.api.dependencies import get_current_user

# Initialize logger
logger = get_logger(__name__)

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    logger.info(
        f"Creating user: {user_data.email}",
        extra={"extra_data": {"email": user_data.email, "role": str(user_data.role), "school_id": str(user_data.school_id)}}
    )
    
    # Validate school exists
    school = db.query(School).filter(School.school_id == user_data.school_id).first()
    if not school:
        logger.warning(f"User creation failed - school not found: {user_data.school_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )

    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.warning(f"User creation failed - email already registered: {user_data.email}")
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
    
    logger.info(
        f"User created successfully: {user.email}",
        extra={"extra_data": {"user_id": str(user.user_id), "email": user.email, "role": str(user.role)}}
    )
    return success_response(user)

@router.get("/")
async def list_users(
    school_id: UUID = None,
    role: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all users with optional filtering by school and role"""
    logger.debug(
        "Listing users",
        extra={"extra_data": {"school_id": str(school_id) if school_id else None, "role": role, "skip": skip, "limit": limit}}
    )
    
    query = db.query(User)

    if school_id:
        query = query.filter(User.school_id == school_id)
    if role:
        # Convert role string to uppercase to match enum values
        query = query.filter(User.role == role.upper())

    users = query.offset(skip).limit(limit).all()
    logger.debug(f"Found {len(users)} users")
    return success_response(users)

@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    logger.debug(f"Fetching user: {user_id}")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(user)

@router.patch("/{user_id}")
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    logger.info(f"Updating user: {user_id}")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        logger.warning(f"User update failed - not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.dict(exclude_unset=True)
    logger.debug(f"Update fields: {list(update_data.keys())}")

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
    
    logger.info(f"User updated successfully", extra={"extra_data": {"user_id": str(user_id)}})
    return success_response(user)

@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a user"""
    logger.info(f"Deleting user: {user_id}")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        logger.warning(f"User deletion failed - not found: {user_id}")
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
        logger.warning(
            f"User deletion blocked - has dependencies",
            extra={"extra_data": {"user_id": str(user_id), "dependencies": dependencies}}
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete user. They have: {', '.join(dependencies)}. Please reassign or remove these first."
        )

    db.delete(user)
    db.commit()
    
    logger.info(
        f"User deleted successfully",
        extra={"extra_data": {"user_id": str(user_id), "email": user.email}}
    )

    return success_response({
        "message": "User deleted successfully",
        "user_id": str(user_id),
        "email": user.email
    })

@router.post("/me/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a profile picture for the current user.
    """
    logger.info(
        f"Uploading profile picture for user: {current_user.user_id}",
        extra={"extra_data": {"user_id": str(current_user.user_id), "filename": file.filename, "content_type": file.content_type}}
    )
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        logger.warning(f"Profile picture upload failed - invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload an image."
        )

    # Create directory if it doesn't exist
    upload_dir = "uploads/profiles"
    os.makedirs(upload_dir, exist_ok=True)

    # Generate filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{current_user.user_id}{file_extension}"
    file_path = os.path.join(upload_dir, filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Profile picture upload failed - file save error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Update user profile_picture_url
    # Store relative path, frontend will need to handle base URL
    profile_picture_url = f"/uploads/profiles/{filename}"
    
    current_user.profile_picture_url = profile_picture_url
    db.commit()
    db.refresh(current_user)
    
    logger.info(
        f"Profile picture uploaded successfully",
        extra={"extra_data": {"user_id": str(current_user.user_id), "profile_picture_url": profile_picture_url}}
    )

    return success_response({
        "message": "Profile picture uploaded successfully",
        "profile_picture_url": profile_picture_url,
        "user_id": str(current_user.user_id)
    })
