from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.risk_alert import AlertLevel, AlertType, AlertStatus


class RiskAlertBase(BaseModel):
    level: AlertLevel
    type: AlertType
    description: str
    triggers: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    status: AlertStatus = AlertStatus.NEW


class RiskAlertCreate(RiskAlertBase):
    student_id: UUID
    assigned_to: Optional[UUID] = None


class RiskAlertUpdate(BaseModel):
    level: Optional[AlertLevel] = None
    type: Optional[AlertType] = None
    description: Optional[str] = None
    triggers: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    assigned_to: Optional[UUID] = None
    status: Optional[AlertStatus] = None


class RiskAlert(RiskAlertBase):
    alert_id: UUID
    student_id: UUID
    assigned_to: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
