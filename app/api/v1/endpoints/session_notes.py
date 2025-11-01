from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db
from app.models.session_note import SessionNote
from app.schemas.session_note import SessionNote as SessionNoteSchema, SessionNoteCreate, SessionNoteUpdate

router = APIRouter()


@router.get("", response_model=List[SessionNoteSchema])
def get_session_notes(
    skip: int = 0,
    limit: int = 100,
    case_id: UUID = None,
    db: Session = Depends(get_db)
):
    """Get all session notes with optional filtering by case"""
    query = db.query(SessionNote)
    if case_id:
        query = query.filter(SessionNote.case_id == case_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{session_note_id}", response_model=SessionNoteSchema)
def get_session_note(session_note_id: UUID, db: Session = Depends(get_db)):
    """Get a specific session note by ID"""
    session_note = db.query(SessionNote).filter(SessionNote.session_note_id == session_note_id).first()
    if not session_note:
        raise HTTPException(status_code=404, detail="Session note not found")
    return session_note


@router.post("", response_model=SessionNoteSchema, status_code=201)
def create_session_note(session_note: SessionNoteCreate, db: Session = Depends(get_db)):
    """Create a new session note"""
    db_session_note = SessionNote(**session_note.model_dump())
    db.add(db_session_note)
    db.commit()
    db.refresh(db_session_note)
    return db_session_note


@router.put("/{session_note_id}", response_model=SessionNoteSchema)
def update_session_note(
    session_note_id: UUID,
    session_note: SessionNoteUpdate,
    db: Session = Depends(get_db)
):
    """Update a session note"""
    db_session_note = db.query(SessionNote).filter(SessionNote.session_note_id == session_note_id).first()
    if not db_session_note:
        raise HTTPException(status_code=404, detail="Session note not found")
    
    for key, value in session_note.model_dump(exclude_unset=True).items():
        setattr(db_session_note, key, value)
    
    db.commit()
    db.refresh(db_session_note)
    return db_session_note


@router.delete("/{session_note_id}", status_code=204)
def delete_session_note(session_note_id: UUID, db: Session = Depends(get_db)):
    """Delete a session note"""
    db_session_note = db.query(SessionNote).filter(SessionNote.session_note_id == session_note_id).first()
    if not db_session_note:
        raise HTTPException(status_code=404, detail="Session note not found")
    
    db.delete(db_session_note)
    db.commit()
    return None
