from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID

from app.api.dependencies import get_db
from app.core.response import success_response
from app.models.risk_alert import RiskAlert, AlertStatus, AlertLevel
from app.models.student import Student
from app.models.user import User
from app.schemas.risk_alert import RiskAlert as RiskAlertSchema, RiskAlertCreate, RiskAlertUpdate

router = APIRouter()


@router.get("")
def get_risk_alerts(
    skip: int = 0,
    limit: int = 100,
    school_id: Optional[UUID] = Query(None),
    student_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    assigned_to: Optional[UUID] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all risk alerts with optional filtering"""
    query = db.query(RiskAlert).options(
        joinedload(RiskAlert.student),
        joinedload(RiskAlert.assigned_user)
    )
    
    # Filter by school if provided
    if school_id:
        student_ids = [s.student_id for s in db.query(Student.student_id).filter(Student.school_id == school_id).all()]
        query = query.filter(RiskAlert.student_id.in_(student_ids))
    
    if student_id:
        query = query.filter(RiskAlert.student_id == student_id)
    if status:
        query = query.filter(RiskAlert.status == status.upper())
    if level:
        query = query.filter(RiskAlert.level == level.upper())
    if assigned_to:
        query = query.filter(RiskAlert.assigned_to == assigned_to)
    
    alerts = query.order_by(RiskAlert.created_at.desc()).offset(skip).limit(limit).all()
    
    # Build response using eager-loaded relationships
    result = []
    for alert in alerts:
        result.append({
            "id": str(alert.alert_id),
            "studentId": str(alert.student_id),
            "studentName": f"{alert.student.first_name} {alert.student.last_name}" if alert.student else "Unknown",
            "level": alert.level.value.lower(),
            "type": alert.type.value.lower(),
            "description": alert.description,
            "triggers": alert.triggers or [],
            "recommendations": alert.recommendations or [],
            "assignedTo": alert.assigned_user.display_name if alert.assigned_user else "Unassigned",
            "assignedToId": str(alert.assigned_to) if alert.assigned_to else None,
            "status": alert.status.value.lower().replace('_', '-'),
            "createdAt": alert.created_at.isoformat(),
            "updatedAt": alert.updated_at.isoformat() if alert.updated_at else None
        })
    
    return success_response(result)


@router.get("/{alert_id}", response_model=RiskAlertSchema)
def get_risk_alert(alert_id: UUID, db: Session = Depends(get_db)):
    """Get a specific risk alert by ID"""
    alert = db.query(RiskAlert).filter(RiskAlert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Risk alert not found")
    return alert


@router.post("", response_model=RiskAlertSchema, status_code=201)
def create_risk_alert(alert: RiskAlertCreate, db: Session = Depends(get_db)):
    """Create a new risk alert"""
    db_alert = RiskAlert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.put("/{alert_id}", response_model=RiskAlertSchema)
def update_risk_alert(alert_id: UUID, alert: RiskAlertUpdate, db: Session = Depends(get_db)):
    """Update a risk alert"""
    db_alert = db.query(RiskAlert).filter(RiskAlert.alert_id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Risk alert not found")
    
    for key, value in alert.model_dump(exclude_unset=True).items():
        setattr(db_alert, key, value)
    
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.delete("/{alert_id}", status_code=204)
def delete_risk_alert(alert_id: UUID, db: Session = Depends(get_db)):
    """Delete a risk alert"""
    db_alert = db.query(RiskAlert).filter(RiskAlert.alert_id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Risk alert not found")
    
    db.delete(db_alert)
    db.commit()
    return None
