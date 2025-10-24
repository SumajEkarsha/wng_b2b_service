from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.core.response import success_response
from app.models.case import Case, JournalEntry
from app.models.student import Student
from app.models.user import User, UserRole
from app.models.class_model import Class
from app.schemas.case import CaseCreate, CaseResponse, CaseDetailResponse, JournalEntryCreate, JournalEntryResponse

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_case(case_data: CaseCreate, db: Session = Depends(get_db)):
    case = Case(
        student_id=case_data.student_id,
        created_by=case_data.created_by,
        risk_level=case_data.initial_risk
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return success_response(case)

@router.get("/{case_id}")
async def get_case(case_id: UUID, db: Session = Depends(get_db)):
    # Fetch case with related student, class, and teacher data
    case = (
        db.query(Case)
        .options(
            joinedload(Case.student)
            .joinedload(Student.class_obj)
            .joinedload(Class.teacher)
        )
        .filter(Case.case_id == case_id)
        .first()
    )

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Fetch counsellor data if assigned
    counsellor = None
    if case.assigned_counsellor:
        counsellor = (
            db.query(User)
            .filter(User.user_id == case.assigned_counsellor, User.role == UserRole.COUNSELLOR)
            .first()
        )

    # Fetch parents data
    parents = []
    if case.student.parents_id:
        parents = (
            db.query(User)
            .filter(
                User.user_id.in_(case.student.parents_id),
                User.role == UserRole.PARENT
            )
            .all()
        )

    # Build response data
    response_data = {
        "case": case,
        "student": {
            "student_id": case.student.student_id,
            "first_name": case.student.first_name,
            "last_name": case.student.last_name,
            "gender": case.student.gender,
            "class_id": case.student.class_id,
            "class_name": case.student.class_obj.name if case.student.class_obj else None,
            "parents_id": case.student.parents_id
        },
        "teacher": None,
        "counsellor": None,
        "parents": []
    }

    # Add teacher data if exists
    if case.student.class_obj and case.student.class_obj.teacher:
        teacher = case.student.class_obj.teacher
        response_data["teacher"] = {
            "user_id": teacher.user_id,
            "display_name": teacher.display_name,
            "email": teacher.email,
            "phone": teacher.phone
        }

    # Add counsellor data if exists
    if counsellor:
        response_data["counsellor"] = {
            "user_id": counsellor.user_id,
            "display_name": counsellor.display_name,
            "email": counsellor.email,
            "phone": counsellor.phone
        }

    # Add parents data
    for parent in parents:
        response_data["parents"].append({
            "user_id": parent.user_id,
            "display_name": parent.display_name,
            "email": parent.email,
            "phone": parent.phone
        })

    return success_response(response_data)

@router.get("/")
async def list_cases(school_id: UUID = None, student_id: UUID = None, status: str = None, risk_level: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Build base query with joined loads for efficient fetching
    query = (
        db.query(Case)
        .options(
            joinedload(Case.student)
            .joinedload(Student.class_obj)
            .joinedload(Class.teacher)
        )
    )

    if school_id:
        query = query.join(Case.student).filter(Student.school_id == school_id)
    if student_id:
        query = query.filter(Case.student_id == student_id)
    if status:
        query = query.filter(Case.status == status)
    if risk_level:
        query = query.filter(Case.risk_level == risk_level)

    cases = query.offset(skip).limit(limit).all()

    # Get all counsellor IDs and parent IDs to fetch in batch
    counsellor_ids = [case.assigned_counsellor for case in cases if case.assigned_counsellor]
    all_parent_ids = []
    for case in cases:
        if case.student.parents_id:
            all_parent_ids.extend(case.student.parents_id)

    # Fetch counsellors in batch
    counsellors = {}
    if counsellor_ids:
        counsellor_results = (
            db.query(User)
            .filter(User.user_id.in_(counsellor_ids), User.role == UserRole.COUNSELLOR)
            .all()
        )
        counsellors = {c.user_id: c for c in counsellor_results}

    # Fetch parents in batch
    parents = {}
    if all_parent_ids:
        parent_results = (
            db.query(User)
            .filter(User.user_id.in_(all_parent_ids), User.role == UserRole.PARENT)
            .all()
        )
        parents = {p.user_id: p for p in parent_results}

    # Build response data for each case
    result = []
    for case in cases:
        counsellor = counsellors.get(case.assigned_counsellor) if case.assigned_counsellor else None

        # Get parents for this student
        case_parents = []
        if case.student.parents_id:
            for parent_id in case.student.parents_id:
                parent = parents.get(parent_id)
                if parent:
                    case_parents.append({
                        "user_id": parent.user_id,
                        "display_name": parent.display_name,
                        "email": parent.email,
                        "phone": parent.phone
                    })

        case_data = {
            "case": case,
            "student": {
                "student_id": case.student.student_id,
                "first_name": case.student.first_name,
                "last_name": case.student.last_name,
                "gender": case.student.gender,
                "class_id": case.student.class_id,
                "class_name": case.student.class_obj.name if case.student.class_obj else None,
                "parents_id": case.student.parents_id
            },
            "teacher": None,
            "counsellor": None,
            "parents": case_parents
        }

        # Add teacher data if exists
        if case.student.class_obj and case.student.class_obj.teacher:
            teacher = case.student.class_obj.teacher
            case_data["teacher"] = {
                "user_id": teacher.user_id,
                "display_name": teacher.display_name,
                "email": teacher.email,
                "phone": teacher.phone
            }

        # Add counsellor data if exists
        if counsellor:
            case_data["counsellor"] = {
                "user_id": counsellor.user_id,
                "display_name": counsellor.display_name,
                "email": counsellor.email,
                "phone": counsellor.phone
            }

        result.append(case_data)

    return success_response(result)

@router.post("/{case_id}/journal", status_code=status.HTTP_201_CREATED)
async def create_journal_entry(case_id: UUID, entry_data: JournalEntryCreate, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    entry = JournalEntry(
        case_id=case_id,
        author_id=entry_data.author_id,
        visibility=entry_data.visibility,
        type=entry_data.type,
        content=entry_data.content,
        audio_url=entry_data.audio_url
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return success_response(entry)

@router.get("/{case_id}/journal")
async def get_journal_entries(case_id: UUID, db: Session = Depends(get_db)):
    # Fetch journal entries with author information
    journal_entries = (
        db.query(JournalEntry)
        .options(joinedload(JournalEntry.author))
        .filter(JournalEntry.case_id == case_id)
        .order_by(JournalEntry.created_at.desc())
        .all()
    )

    # Build response data with author names
    result = []
    for entry in journal_entries:
        entry_data = {
            "entry_id": entry.entry_id,
            "case_id": entry.case_id,
            "author_id": entry.author_id,
            "author_name": entry.author.display_name if entry.author else None,
            "visibility": entry.visibility,
            "type": entry.type,
            "content": entry.content,
            "audio_url": entry.audio_url,
            "created_at": entry.created_at
        }
        result.append(entry_data)

    return success_response(result)

@router.post("/{case_id}/process")
async def process_case(case_id: UUID, db: Session = Depends(get_db)):
    """Mark a case as processed/reviewed"""
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case.processed = True
    db.commit()
    db.refresh(case)
    return success_response(case)
