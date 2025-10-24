from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.core.response import success_response
from app.models.student import Student
from app.models.school import School
from app.models.class_model import Class
from app.models.user import User, UserRole
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    # Validate school exists
    school = db.query(School).filter(School.school_id == student_data.school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )

    # Validate class exists if class_id is provided
    if student_data.class_id:
        class_obj = db.query(Class).filter(Class.class_id == student_data.class_id).first()
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )

    # Validate parents exist if parents_id is provided
    if student_data.parents_id:
        for parent_id in student_data.parents_id:
            parent = db.query(User).filter(User.user_id == parent_id, User.role == UserRole.PARENT).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent with ID {parent_id} not found or is not a parent"
                )

    student = Student(**student_data.dict())
    db.add(student)
    db.commit()
    db.refresh(student)
    return success_response(student)

@router.get("/{student_id}")
async def get_student(student_id: UUID, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return success_response(student)

@router.get("/")
async def list_students(school_id: UUID, skip: int = 0, limit: int = 100, class_id: UUID = None, db: Session = Depends(get_db)):
    query = db.query(Student).filter(Student.school_id == school_id)
    if class_id:
        query = query.filter(Student.class_id == class_id)
    return success_response(query.offset(skip).limit(limit).all())

@router.patch("/{student_id}")
async def update_student(student_id: UUID, student_update: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Validate class exists if class_id is being updated
    update_data = student_update.dict(exclude_unset=True)
    if "class_id" in update_data and update_data["class_id"] is not None:
        class_obj = db.query(Class).filter(Class.class_id == update_data["class_id"]).first()
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )

    # Validate parents exist if parents_id is being updated
    if "parents_id" in update_data and update_data["parents_id"] is not None:
        for parent_id in update_data["parents_id"]:
            parent = db.query(User).filter(User.user_id == parent_id, User.role == UserRole.PARENT).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent with ID {parent_id} not found or is not a parent"
                )

    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return success_response(student)
