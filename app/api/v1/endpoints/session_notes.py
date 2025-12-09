from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db
from app.core.logging_config import get_logger
from app.models.session_note import SessionNote
from app.schemas.session_note import SessionNote as SessionNoteSchema, SessionNoteCreate, SessionNoteUpdate

# Initialize logger
logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=List[SessionNoteSchema])
def get_session_notes(
    skip: int = 0,
    limit: int = 100,
    case_id: UUID = None,
    db: Session = Depends(get_db)
):
    """Get all session notes with optional filtering by case"""
    logger.debug("Listing session notes", extra={"extra_data": {"case_id": str(case_id) if case_id else None}})
    query = db.query(SessionNote)
    if case_id:
        query = query.filter(SessionNote.case_id == case_id)
    notes = query.offset(skip).limit(limit).all()
    logger.debug(f"Found {len(notes)} session notes")
    return notes


@router.get("/{session_note_id}", response_model=SessionNoteSchema)
def get_session_note(session_note_id: UUID, db: Session = Depends(get_db)):
    """Get a specific session note by ID"""
    logger.debug(f"Fetching session note: {session_note_id}")
    session_note = db.query(SessionNote).filter(SessionNote.session_note_id == session_note_id).first()
    if not session_note:
        logger.warning(f"Session note not found: {session_note_id}")
        raise HTTPException(status_code=404, detail="Session note not found")
    return session_note


@router.post("", response_model=SessionNoteSchema, status_code=201)
def create_session_note(session_note: SessionNoteCreate, db: Session = Depends(get_db)):
    """Create a new session note"""
    logger.info("Creating session note", extra={"extra_data": {"case_id": str(session_note.case_id) if hasattr(session_note, 'case_id') else None}})
    db_session_note = SessionNote(**session_note.model_dump())
    db.add(db_session_note)
    db.commit()
    db.refresh(db_session_note)
    logger.info(f"Session note created", extra={"extra_data": {"session_note_id": str(db_session_note.session_note_id)}})
    return db_session_note


@router.put("/{session_note_id}", response_model=SessionNoteSchema)
def update_session_note(
    session_note_id: UUID,
    session_note: SessionNoteUpdate,
    db: Session = Depends(get_db)
):
    """Update a session note"""
    logger.info(f"Updating session note: {session_note_id}")
    db_session_note = db.query(SessionNote).filter(SessionNote.session_note_id == session_note_id).first()
    if not db_session_note:
        logger.warning(f"Session note update failed - not found: {session_note_id}")
        raise HTTPException(status_code=404, detail="Session note not found")
    
    for key, value in session_note.model_dump(exclude_unset=True).items():
        setattr(db_session_note, key, value)
    
    db.commit()
    db.refresh(db_session_note)
    logger.info(f"Session note updated", extra={"extra_data": {"session_note_id": str(session_note_id)}})
    return db_session_note


@router.delete("/{session_note_id}", status_code=204)
def delete_session_note(session_note_id: UUID, db: Session = Depends(get_db)):
    """Delete a session note"""
    logger.info(f"Deleting session note: {session_note_id}")
    db_session_note = db.query(SessionNote).filter(SessionNote.session_note_id == session_note_id).first()
    if not db_session_note:
        logger.warning(f"Session note deletion failed - not found: {session_note_id}")
        raise HTTPException(status_code=404, detail="Session note not found")
    
    db.delete(db_session_note)
    db.commit()
    logger.info(f"Session note deleted", extra={"extra_data": {"session_note_id": str(session_note_id)}})
    return None
