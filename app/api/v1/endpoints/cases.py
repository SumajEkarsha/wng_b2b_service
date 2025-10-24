from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.models.case import Case, JournalEntry
from app.models.student import Student
from app.models.user import User
from app.schemas.case import CaseCreate, CaseResponse, JournalEntryCreate, JournalEntryResponse

router = APIRouter()

@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(case_data: CaseCreate, db: Session = Depends(get_db)):
    case = Case(
        student_id=case_data.student_id,
        created_by=case_data.created_by,
        risk_level=case_data.initial_risk
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(case_id: UUID, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.get("/", response_model=List[CaseResponse])
async def list_cases(school_id: UUID = None, student_id: UUID = None, status: str = None, risk_level: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(Case)
    
    if school_id:
        query = query.join(Case.student).filter(Student.school_id == school_id)
    if student_id:
        query = query.filter(Case.student_id == student_id)
    if status:
        query = query.filter(Case.status == status)
    if risk_level:
        query = query.filter(Case.risk_level == risk_level)
    
    return query.offset(skip).limit(limit).all()

@router.post("/{case_id}/journal", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
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
    return entry

@router.get("/{case_id}/journal", response_model=List[JournalEntryResponse])
async def get_journal_entries(case_id: UUID, db: Session = Depends(get_db)):
    return db.query(JournalEntry).filter(JournalEntry.case_id == case_id).all()

@router.post("/{case_id}/process", response_model=CaseResponse)
async def process_case(case_id: UUID, db: Session = Depends(get_db)):
    """Mark a case as processed/reviewed"""
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case.processed = True
    db.commit()
    db.refresh(case)
    return case
