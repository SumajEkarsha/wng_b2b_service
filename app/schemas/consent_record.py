from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.consent_record import ConsentType, ConsentStatus


class ConsentRecordBase(BaseModel):
    parent_name: Optional[str] = None
    consent_type: ConsentType
    status: ConsentStatus = ConsentStatus.PENDING
    documents: Optional[List[str]] = None


class ConsentRecordCreate(ConsentRecordBase):
    student_id: UUID


class ConsentRecordUpdate(BaseModel):
    parent_name: Optional[str] = None
    status: Optional[ConsentStatus] = None
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    documents: Optional[List[str]] = None


class ConsentRecord(ConsentRecordBase):
    consent_id: UUID
    student_id: UUID
    granted_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
