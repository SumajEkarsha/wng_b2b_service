from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.core.response import success_response
from app.models.class_model import Class
from app.models.school import School
from app.models.user import User, UserRole
from app.schemas.class_schema import ClassCreate, ClassResponse, ClassUpdate

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_class(
    class_data: ClassCreate,
    db: Session = Depends(get_db)
):
    # Validate school exists
    school = db.query(School).filter(School.school_id == class_data.school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"School not found"
        )

    # Validate teacher exists if teacher_id is provided
    if class_data.teacher_id:
        teacher = db.query(User).filter(User.user_id == class_data.teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teacher not found"
            )
        if teacher.role != UserRole.TEACHER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User is not a teacher"
            )

    class_obj = Class(**class_data.dict())
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    
    # Serialize to dictionary
    class_dict = {
        "class_id": str(class_obj.class_id),
        "school_id": str(class_obj.school_id),
        "name": class_obj.name,
        "grade": class_obj.grade,
        "section": class_obj.section,
        "academic_year": class_obj.academic_year,
        "teacher_id": str(class_obj.teacher_id) if class_obj.teacher_id else None,
        "capacity": class_obj.capacity,
        "additional_info": class_obj.additional_info
    }
    return success_response(class_dict)

@router.get("/")
async def list_classes(
    school_id: UUID,  # Required parameter
    skip: int = 0,
    limit: int = 100,
    grade: str = None,
    section: str = None,
    teacher_id: UUID = None,
    db: Session = Depends(get_db)
):
    query = db.query(Class).options(
        joinedload(Class.teacher)
    ).filter(Class.school_id == school_id)
    if grade:
        query = query.filter(Class.grade == grade)
    if section:
        query = query.filter(Class.section == section)
    if teacher_id:
        query = query.filter(Class.teacher_id == teacher_id)
    classes = query.offset(skip).limit(limit).all()
    
    # Serialize classes to dictionaries to avoid JSON serialization issues with relationships
    classes_data = []
    for class_obj in classes:
        class_dict = {
            "class_id": str(class_obj.class_id),
            "school_id": str(class_obj.school_id),
            "name": class_obj.name,
            "grade": class_obj.grade,
            "section": class_obj.section,
            "academic_year": class_obj.academic_year,
            "teacher_id": str(class_obj.teacher_id) if class_obj.teacher_id else None,
            "capacity": class_obj.capacity,
            "additional_info": class_obj.additional_info
        }
        classes_data.append(class_dict)
    
    return success_response(classes_data)

@router.get("/{class_id}")
async def get_class(
    class_id: UUID,
    db: Session = Depends(get_db)
):
    class_obj = db.query(Class).options(
        joinedload(Class.teacher)
    ).filter(Class.class_id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Serialize to dictionary
    class_dict = {
        "class_id": str(class_obj.class_id),
        "school_id": str(class_obj.school_id),
        "name": class_obj.name,
        "grade": class_obj.grade,
        "section": class_obj.section,
        "academic_year": class_obj.academic_year,
        "teacher_id": str(class_obj.teacher_id) if class_obj.teacher_id else None,
        "capacity": class_obj.capacity,
        "additional_info": class_obj.additional_info
    }
    return success_response(class_dict)

@router.patch("/{class_id}")
async def update_class(
    class_id: UUID,
    class_update: ClassUpdate,
    db: Session = Depends(get_db)
):
    class_obj = db.query(Class).filter(Class.class_id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    # Validate teacher exists if teacher_id is being updated
    update_data = class_update.dict(exclude_unset=True)
    if "teacher_id" in update_data and update_data["teacher_id"] is not None:
        teacher = db.query(User).filter(User.user_id == update_data["teacher_id"]).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Teacher not found"
            )
        if teacher.role != UserRole.TEACHER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User is not a teacher"
            )

    for field, value in update_data.items():
        setattr(class_obj, field, value)

    db.commit()
    db.refresh(class_obj)
    
    # Serialize to dictionary
    class_dict = {
        "class_id": str(class_obj.class_id),
        "school_id": str(class_obj.school_id),
        "name": class_obj.name,
        "grade": class_obj.grade,
        "section": class_obj.section,
        "academic_year": class_obj.academic_year,
        "teacher_id": str(class_obj.teacher_id) if class_obj.teacher_id else None,
        "capacity": class_obj.capacity,
        "additional_info": class_obj.additional_info
    }
    return success_response(class_dict)

@router.delete("/{class_id}")
async def delete_class(
    class_id: UUID,
    db: Session = Depends(get_db)
):
    class_obj = db.query(Class).filter(Class.class_id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    db.delete(class_obj)
    db.commit()
    return success_response({"message": "Class deleted successfully", "class_id": str(class_id)})
