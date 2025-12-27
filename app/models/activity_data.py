"""
Activity models for the separate activity database.
This database has a different schema with JSONB activity_data.
"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

# Separate Base for activity database to avoid conflicts
ActivityBase = declarative_base()


class ActivityData(ActivityBase):
    """Activity model for the activity database (different schema)."""
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True)
    activity_id = Column(Text, unique=True, index=True)
    activity_name = Column(Text)
    framework = Column(Text)
    age = Column(Integer)
    diagnosis = Column(Text)
    cognitive = Column(Text)
    sensory = Column(Text)
    activity_data = Column(JSONB)  # Contains all activity details
    themes = Column(Text)
    setting = Column(Text)
    supervision = Column(Text)
    duration_pref = Column(Text)
    risk_level = Column(Text)
    skill_level = Column(Text)


class GeneratedActivityData(ActivityBase):
    """Generated Activity model for AI-generated activities."""
    __tablename__ = "generatedactivities"
    
    id = Column(Integer, primary_key=True)
    activity_id = Column(Text, unique=True, index=True)
    activity_name = Column(Text)
    framework = Column(Text)
    age = Column(Integer)
    diagnosis = Column(Text)
    cognitive = Column(Text)
    sensory = Column(Text)
    themes = Column(Text)
    setting = Column(Text)
    supervision = Column(Text)
    duration_pref = Column(Text)
    risk_level = Column(Text)
    skill_level = Column(Text)
    activity_data = Column(JSONB)  # Contains all activity details

