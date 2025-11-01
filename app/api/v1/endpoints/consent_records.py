from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db
from app.models.consent_record import ConsentRecord, ConsentStatus
from app.schemas.consent_record import (
    ConsentRecord as ConsentRecordSchema,
    ConsentRecordCreate,
    ConsentRecordUpdate
)

router = APIRouter()


@router.get("", response_model=List[ConsentRecordSchema])
def get_consent_records(
    skip: int = 0,
    limit: int = 100,
    student_id: UUID = None,
    status: ConsentStatus = None,
    db: Session = Depends(get_db)
):
    """Get all consent records with optional filtering"""
    query = db.query(ConsentRecord)
    if student_id:
        query = query.filter(ConsentRecord.student_id == student_id)
    if status:
        query = query.filter(ConsentRecord.status == status)
    return query.offset(skip).limit(limit).all()


@router.get("/{consent_id}", response_model=ConsentRecordSchema)
def get_consent_record(consent_id: UUID, db: Session = Depends(get_db)):
    """Get a specific consent record by ID"""
    consent = db.query(ConsentRecord).filter(ConsentRecord.consent_id == consent_id).first()
    if not consent:
        raise HTTPException(status_code=404, detail="Consent record not found")
    return consent


@router.post("", response_model=ConsentRecordSchema, status_code=201)
def create_consent_record(consent: ConsentRecordCreate, db: Session = Depends(get_db)):
    """Create a new consent record"""
    db_consent = ConsentRecord(**consent.model_dump())
    db.add(db_consent)
    db.commit()
    db.refresh(db_consent)
    return db_consent


@router.put("/{consent_id}", response_model=ConsentRecordSchema)
def update_consent_record(
    consent_id: UUID,
    consent: ConsentRecordUpdate,
    db: Session = Depends(get_db)
):
    """Update a consent record"""
    db_consent = db.query(ConsentRecord).filter(ConsentRecord.consent_id == consent_id).first()
    if not db_consent:
        raise HTTPException(status_code=404, detail="Consent record not found")
    
    for key, value in consent.model_dump(exclude_unset=True).items():
        setattr(db_consent, key, value)
    
    db.commit()
    db.refresh(db_consent)
    return db_consent


@router.delete("/{consent_id}", status_code=204)
def delete_consent_record(consent_id: UUID, db: Session = Depends(get_db)):
    """Delete a consent record"""
    db_consent = db.query(ConsentRecord).filter(ConsentRecord.consent_id == consent_id).first()
    if not db_consent:
        raise HTTPException(status_code=404, detail="Consent record not found")
    
    db.delete(db_consent)
    db.commit()
    return None
