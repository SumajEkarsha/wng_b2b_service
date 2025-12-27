from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db
from app.core.logging_config import get_logger
from app.models.consent_record import ConsentRecord, ConsentStatus
from app.schemas.consent_record import (
    ConsentRecord as ConsentRecordSchema,
    ConsentRecordCreate,
    ConsentRecordUpdate
)

# Initialize logger
logger = get_logger(__name__)

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
    logger.debug("Listing consent records", extra={"extra_data": {"student_id": str(student_id) if student_id else None, "status": str(status) if status else None}})
    query = db.query(ConsentRecord)
    if student_id:
        query = query.filter(ConsentRecord.student_id == student_id)
    if status:
        query = query.filter(ConsentRecord.status == status)
    records = query.offset(skip).limit(limit).all()
    logger.debug(f"Found {len(records)} consent records")
    return records


@router.get("/{consent_id}", response_model=ConsentRecordSchema)
def get_consent_record(consent_id: UUID, db: Session = Depends(get_db)):
    """Get a specific consent record by ID"""
    logger.debug(f"Fetching consent record: {consent_id}")
    consent = db.query(ConsentRecord).filter(ConsentRecord.consent_id == consent_id).first()
    if not consent:
        logger.warning(f"Consent record not found: {consent_id}")
        raise HTTPException(status_code=404, detail="Consent record not found")
    return consent


@router.post("", response_model=ConsentRecordSchema, status_code=201)
def create_consent_record(consent: ConsentRecordCreate, db: Session = Depends(get_db)):
    """Create a new consent record"""
    logger.info("Creating consent record", extra={"extra_data": {"student_id": str(consent.student_id) if hasattr(consent, 'student_id') else None}})
    db_consent = ConsentRecord(**consent.model_dump())
    db.add(db_consent)
    db.commit()
    db.refresh(db_consent)
    logger.info(f"Consent record created", extra={"extra_data": {"consent_id": str(db_consent.consent_id)}})
    return db_consent


@router.put("/{consent_id}", response_model=ConsentRecordSchema)
def update_consent_record(
    consent_id: UUID,
    consent: ConsentRecordUpdate,
    db: Session = Depends(get_db)
):
    """Update a consent record"""
    logger.info(f"Updating consent record: {consent_id}")
    db_consent = db.query(ConsentRecord).filter(ConsentRecord.consent_id == consent_id).first()
    if not db_consent:
        logger.warning(f"Consent record update failed - not found: {consent_id}")
        raise HTTPException(status_code=404, detail="Consent record not found")
    
    for key, value in consent.model_dump(exclude_unset=True).items():
        setattr(db_consent, key, value)
    
    db.commit()
    db.refresh(db_consent)
    logger.info(f"Consent record updated", extra={"extra_data": {"consent_id": str(consent_id)}})
    return db_consent


@router.delete("/{consent_id}", status_code=204)
def delete_consent_record(consent_id: UUID, db: Session = Depends(get_db)):
    """Delete a consent record"""
    logger.info(f"Deleting consent record: {consent_id}")
    db_consent = db.query(ConsentRecord).filter(ConsentRecord.consent_id == consent_id).first()
    if not db_consent:
        logger.warning(f"Consent record deletion failed - not found: {consent_id}")
        raise HTTPException(status_code=404, detail="Consent record not found")
    
    db.delete(db_consent)
    db.commit()
    logger.info(f"Consent record deleted", extra={"extra_data": {"consent_id": str(consent_id)}})
    return None
