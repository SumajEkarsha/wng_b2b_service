from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.core.response import success_response
from app.core.logging_config import get_logger
from app.models.student import Student
from app.models.school import School
from app.models.class_model import Class
from app.models.user import User, UserRole
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate

# Initialize logger
logger = get_logger(__name__)

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    logger.info(
        f"Creating student: {student_data.first_name} {student_data.last_name}",
        extra={"extra_data": {"school_id": str(student_data.school_id), "class_id": str(student_data.class_id) if student_data.class_id else None}}
    )
    
    # Validate school exists
    school = db.query(School).filter(School.school_id == student_data.school_id).first()
    if not school:
        logger.warning(f"Student creation failed - school not found: {student_data.school_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )

    # Validate class exists if class_id is provided
    if student_data.class_id:
        class_obj = db.query(Class).filter(Class.class_id == student_data.class_id).first()
        if not class_obj:
            logger.warning(f"Student creation failed - class not found: {student_data.class_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )

    # Auto-create parent if parent_email is provided (legacy field)
    created_parent_ids = []
    if student_data.parent_email:
        # Check if parent already exists with this email
        existing_parent = db.query(User).filter(
            User.email == student_data.parent_email,
            User.school_id == student_data.school_id
        ).first()
        
        if existing_parent:
            # Parent exists, add to parents_id list
            if existing_parent.role == UserRole.PARENT:
                created_parent_ids.append(existing_parent.user_id)
        else:
            # Create new parent user
            import uuid
            from app.core.security import get_password_hash
            
            # Use parent_name if provided, otherwise generate from email
            if student_data.parent_name:
                display_name = student_data.parent_name
            else:
                # Generate display name from email
                display_name = student_data.parent_email.split('@')[0].replace('.', ' ').title()
            
            new_parent = User(
                user_id=uuid.uuid4(),
                school_id=student_data.school_id,
                email=student_data.parent_email,
                display_name=display_name,
                phone=student_data.parent_phone,
                role=UserRole.PARENT,
                hashed_password=get_password_hash("Welcome123!")  # Default password
            )
            db.add(new_parent)
            db.flush()  # Flush to get the user_id
            created_parent_ids.append(new_parent.user_id)

    # Validate parents exist if parents_id is provided
    if student_data.parents_id:
        for parent_id in student_data.parents_id:
            parent = db.query(User).filter(User.user_id == parent_id, User.role == UserRole.PARENT).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent with ID {parent_id} not found or is not a parent"
                )
        # Merge with auto-created parents
        created_parent_ids.extend(student_data.parents_id)
    
    # Remove duplicates and set parents_id
    if created_parent_ids:
        created_parent_ids = list(set(created_parent_ids))
    
    # Create student with merged parent IDs
    student_dict = student_data.dict()
    if created_parent_ids:
        # Convert UUIDs to strings for JSON storage
        student_dict['parents_id'] = [str(pid) for pid in created_parent_ids]
    
    # Remove parent_name as it's not a Student model field (only used for parent creation)
    student_dict.pop('parent_name', None)
    
    student = Student(**student_dict)
    db.add(student)
    db.commit()
    db.refresh(student)
    
    logger.info(
        f"Student created successfully: {student.first_name} {student.last_name}",
        extra={"extra_data": {"student_id": str(student.student_id), "school_id": str(student.school_id), "class_id": str(student.class_id) if student.class_id else None}}
    )
    return success_response(student)

@router.get("/{student_id}")
async def get_student(student_id: UUID, db: Session = Depends(get_db)):
    logger.debug(f"Fetching student: {student_id}")
    
    student = db.query(Student).options(
        joinedload(Student.class_obj)
    ).filter(Student.student_id == student_id).first()
    if not student:
        logger.warning(f"Student not found: {student_id}")
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Enrich student data with class section information
    student_dict = {
        "student_id": student.student_id,
        "school_id": student.school_id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "pseudonym": student.pseudonym,
        "roll_number": student.roll_number,
        "dob": student.dob,
        "gender": student.gender.value if student.gender else None,
        "class_id": student.class_id,
        "grade": student.grade,
        "section": None,  # Will be populated from class
        "parents_id": student.parents_id,
        "parent_email": student.parent_email,
        "parent_phone": student.parent_phone,
        "risk_level": student.risk_level.value if student.risk_level else None,
        "wellbeing_score": student.wellbeing_score,
        "last_assessment": student.last_assessment,
        "consent_status": student.consent_status.value if student.consent_status else None,
        "notes": student.notes,
        "additional_info": student.additional_info
    }
    
    # Get section, grade, and class name from class if student is assigned to a class
    if student.class_obj:
        student_dict["section"] = student.class_obj.section
        student_dict["class_name"] = student.class_obj.name
        # Use class grade if student grade is not set
        if not student_dict["grade"] and student.class_obj.grade:
            student_dict["grade"] = student.class_obj.grade
    
    return success_response(student_dict)

@router.get("/")
async def list_students(school_id: UUID, skip: int = 0, limit: int = 300, class_id: UUID = None, db: Session = Depends(get_db)):
    logger.debug(
        f"Listing students for school: {school_id}",
        extra={"extra_data": {"school_id": str(school_id), "class_id": str(class_id) if class_id else None, "skip": skip, "limit": limit}}
    )
    
    query = db.query(Student).options(
        joinedload(Student.class_obj)
    ).filter(Student.school_id == school_id)
    if class_id:
        query = query.filter(Student.class_id == class_id)
    
    students = query.offset(skip).limit(limit).all()
    
    logger.debug(f"Found {len(students)} students")
    
    # Enrich student data with class section information
    students_data = []
    for student in students:
        student_dict = {
            "student_id": student.student_id,
            "school_id": student.school_id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "pseudonym": student.pseudonym,
            "roll_number": student.roll_number,
            "dob": student.dob,
            "gender": student.gender.value if student.gender else None,
            "class_id": student.class_id,
            "grade": student.grade,
            "section": None,  # Will be populated from class
            "parents_id": student.parents_id,
            "parent_email": student.parent_email,
            "parent_phone": student.parent_phone,
            "risk_level": student.risk_level.value if student.risk_level else None,
            "wellbeing_score": student.wellbeing_score,
            "last_assessment": student.last_assessment,
            "consent_status": student.consent_status.value if student.consent_status else None,
            "notes": student.notes,
            "additional_info": student.additional_info
        }
        
        # Get section, grade, and class name from class if student is assigned to a class
        if student.class_obj:
            student_dict["section"] = student.class_obj.section
            student_dict["class_name"] = student.class_obj.name
            # Use class grade if student grade is not set
            if not student_dict["grade"] and student.class_obj.grade:
                student_dict["grade"] = student.class_obj.grade
        
        students_data.append(student_dict)
    
    return success_response(students_data)

@router.patch("/{student_id}")
async def update_student(student_id: UUID, student_update: StudentUpdate, db: Session = Depends(get_db)):
    logger.info(f"Updating student: {student_id}")
    
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        logger.warning(f"Student update failed - not found: {student_id}")
        raise HTTPException(status_code=404, detail="Student not found")

    # Validate class exists if class_id is being updated
    update_data = student_update.dict(exclude_unset=True)
    logger.debug(f"Update fields: {list(update_data.keys())}")
    
    if "class_id" in update_data and update_data["class_id"] is not None:
        class_obj = db.query(Class).filter(Class.class_id == update_data["class_id"]).first()
        if not class_obj:
            logger.warning(f"Student update failed - class not found: {update_data['class_id']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )

    # Auto-create parent if parent_email is being updated (legacy field)
    created_parent_ids = []
    if "parent_email" in update_data and update_data["parent_email"]:
        # Check if parent already exists with this email
        existing_parent = db.query(User).filter(
            User.email == update_data["parent_email"],
            User.school_id == student.school_id
        ).first()
        
        if existing_parent:
            # Parent exists, add to parents_id list
            if existing_parent.role == UserRole.PARENT:
                created_parent_ids.append(existing_parent.user_id)
        else:
            # Create new parent user
            import uuid
            from app.core.security import get_password_hash
            
            # Use parent_name if provided, otherwise generate from email
            if update_data.get("parent_name"):
                display_name = update_data["parent_name"]
            else:
                # Generate display name from email
                display_name = update_data["parent_email"].split('@')[0].replace('.', ' ').title()
            
            new_parent = User(
                user_id=uuid.uuid4(),
                school_id=student.school_id,
                email=update_data["parent_email"],
                display_name=display_name,
                phone=update_data.get("parent_phone"),
                role=UserRole.PARENT,
                hashed_password=get_password_hash("Welcome123!")  # Default password
            )
            db.add(new_parent)
            db.flush()  # Flush to get the user_id
            created_parent_ids.append(new_parent.user_id)

    # Validate parents exist if parents_id is being updated
    if "parents_id" in update_data and update_data["parents_id"] is not None:
        for parent_id in update_data["parents_id"]:
            parent = db.query(User).filter(User.user_id == parent_id, User.role == UserRole.PARENT).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent with ID {parent_id} not found or is not a parent"
                )
        # Merge with auto-created parents
        created_parent_ids.extend(update_data["parents_id"])
    elif created_parent_ids:
        # If only parent_email was updated, merge with existing parents_id
        if student.parents_id:
            created_parent_ids.extend(student.parents_id)
    
    # Remove duplicates and update parents_id if we have any
    if created_parent_ids:
        # Convert UUIDs to strings for JSON storage
        update_data['parents_id'] = [str(pid) for pid in list(set(created_parent_ids))]

    # Remove parent_name as it's not a Student model field (only used for parent creation)
    update_data.pop('parent_name', None)

    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    
    logger.info(
        f"Student updated successfully: {student.first_name} {student.last_name}",
        extra={"extra_data": {"student_id": str(student_id)}}
    )
    return success_response(student)
