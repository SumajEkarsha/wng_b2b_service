from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.models.school import School
from app.schemas.school import SchoolCreate, SchoolResponse, SchoolUpdate

router = APIRouter()

@router.post("/", response_model=SchoolResponse, status_code=status.HTTP_201_CREATED)
async def create_school(
    school_data: SchoolCreate,
    db: Session = Depends(get_db)
):
    school = School(**school_data.dict())
    db.add(school)
    db.commit()
    db.refresh(school)
    return school

@router.get("/", response_model=List[SchoolResponse])
async def list_schools(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    schools = db.query(School).offset(skip).limit(limit).all()
    return schools

@router.get("/{school_id}", response_model=SchoolResponse)
async def get_school(
    school_id: UUID,
    db: Session = Depends(get_db)
):
    school = db.query(School).filter(School.school_id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school

@router.patch("/{school_id}", response_model=SchoolResponse)
async def update_school(
    school_id: UUID,
    school_update: SchoolUpdate,
    db: Session = Depends(get_db)
):
    school = db.query(School).filter(School.school_id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    for field, value in school_update.dict(exclude_unset=True).items():
        setattr(school, field, value)
    
    db.commit()
    db.refresh(school)
    return school

@router.delete("/{school_id}")
async def delete_school(
    school_id: UUID,
    db: Session = Depends(get_db)
):
    school = db.query(School).filter(School.school_id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    # Check for dependent records before deletion
    dependent_records = []
    
    if school.users:
        dependent_records.append(f"{len(school.users)} user(s)")
    if school.students:
        dependent_records.append(f"{len(school.students)} student(s)")
    if school.classes:
        dependent_records.append(f"{len(school.classes)} class(es)")
    if school.resources:
        dependent_records.append(f"{len(school.resources)} resource(s)")
    
    if dependent_records:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Contact Technical Support to request the deletion process."
        )
    
    db.delete(school)
    db.commit()
    return {"success": True, "message": "School deleted successfully", "school_id": str(school_id)}
