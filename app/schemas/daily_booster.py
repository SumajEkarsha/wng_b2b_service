from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.daily_booster import BoosterType, DifficultyLevel


class DailyBoosterBase(BaseModel):
    title: str
    type: BoosterType
    duration: Optional[int] = None
    description: Optional[str] = None
    purpose: Optional[str] = None
    target_grades: Optional[List[str]] = None
    difficulty: DifficultyLevel
    full_instructions: str
    materials: Optional[List[str]] = None


class DailyBoosterCreate(DailyBoosterBase):
    school_id: Optional[UUID] = None


class DailyBoosterUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[BoosterType] = None
    duration: Optional[int] = None
    description: Optional[str] = None
    purpose: Optional[str] = None
    target_grades: Optional[List[str]] = None
    difficulty: Optional[DifficultyLevel] = None
    full_instructions: Optional[str] = None
    materials: Optional[List[str]] = None


class DailyBooster(DailyBoosterBase):
    booster_id: UUID
    school_id: Optional[UUID]
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
