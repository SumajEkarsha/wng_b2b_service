from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class SchoolSettings(BaseModel):
    """School-specific settings and configurations"""
    enable_parent_portal: Optional[bool] = Field(default=True, description="Enable parent access portal")
    enable_sso: Optional[bool] = Field(default=False, description="Enable Single Sign-On")
    notification_preferences: Optional[Dict[str, bool]] = Field(default=None, description="Notification settings")
    privacy_settings: Optional[Dict[str, Any]] = Field(default=None, description="Privacy and data sharing settings")
    custom_fields: Optional[Dict[str, Any]] = Field(default=None, description="Custom school-specific fields")
    
    class Config:
        json_schema_extra = {
            "example": {
                "enable_parent_portal": True,
                "enable_sso": False,
                "notification_preferences": {
                    "email_notifications": True,
                    "sms_notifications": False,
                    "weekly_reports": True
                },
                "privacy_settings": {
                    "share_with_district": False,
                    "anonymize_reports": True
                },
                "custom_fields": {
                    "district_id": "DIST-001",
                    "accreditation": "Regional Board"
                }
            }
        }

class SchoolCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="School name")
    address: Optional[str] = Field(default=None, description="Street address")
    city: Optional[str] = Field(default=None, description="City")
    state: Optional[str] = Field(default=None, description="State/Province")
    country: Optional[str] = Field(default=None, description="Country")
    phone: Optional[str] = Field(default=None, description="Contact phone number")
    email: Optional[EmailStr] = Field(default=None, description="Contact email")
    website: Optional[str] = Field(default=None, description="School website URL")
    timezone: str = Field(default="UTC", description="School timezone")
    academic_year: Optional[str] = Field(default=None, description="Current academic year (e.g., 2024-2025)")
    settings: Optional[Dict[str, Any]] = Field(default=None, description="School settings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Lincoln High School",
                "address": "123 Education Street",
                "city": "Springfield",
                "state": "IL",
                "country": "USA",
                "phone": "+1-555-0100",
                "email": "admin@lincolnhs.edu",
                "website": "https://www.lincolnhs.edu",
                "timezone": "America/Chicago",
                "academic_year": "2024-2025",
                "settings": {
                    "enable_parent_portal": True,
                    "enable_sso": False,
                    "notification_preferences": {
                        "email_notifications": True,
                        "sms_notifications": False,
                        "weekly_reports": True
                    },
                    "privacy_settings": {
                        "share_with_district": False,
                        "anonymize_reports": True
                    },
                    "custom_fields": {
                        "district_id": "DIST-IL-045",
                        "accreditation": "North Central Association"
                    }
                }
            }
        }

class SchoolUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200, description="School name")
    address: Optional[str] = Field(default=None, description="Street address")
    city: Optional[str] = Field(default=None, description="City")
    state: Optional[str] = Field(default=None, description="State/Province")
    country: Optional[str] = Field(default=None, description="Country")
    phone: Optional[str] = Field(default=None, description="Contact phone number")
    email: Optional[EmailStr] = Field(default=None, description="Contact email")
    website: Optional[str] = Field(default=None, description="School website URL")
    timezone: Optional[str] = Field(default=None, description="School timezone")
    academic_year: Optional[str] = Field(default=None, description="Current academic year")
    settings: Optional[SchoolSettings] = Field(default=None, description="School settings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone": "+1-555-0199",
                "academic_year": "2024-2025"
            }
        }

class SchoolResponse(BaseModel):
    school_id: UUID
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    timezone: str
    academic_year: Optional[str] = None
    needs_data_onboarding: Optional[bool] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "school_id": "614077c0-9cde-4955-a384-5a0d0a1a1ef5",
                "name": "Lincoln High School",
                "address": "123 Education Street",
                "city": "Springfield",
                "state": "IL",
                "country": "USA",
                "phone": "+1-555-0100",
                "email": "admin@lincolnhs.edu",
                "website": "https://www.lincolnhs.edu",
                "timezone": "America/Chicago",
                "academic_year": "2024-2025",
                "needs_data_onboarding": False
            }
        }


class SchoolOnboardingRequest(BaseModel):
    """Schema for school onboarding application"""
    schoolName: str = Field(..., min_length=3, description="School name")
    schoolType: str = Field(..., description="Type of school (public, private, charter, magnet)")
    establishedYear: str = Field(..., description="Year school was established")
    websiteUrl: Optional[str] = Field(default=None, description="School website URL")
    schoolEmail: EmailStr = Field(..., description="School email address")
    schoolPhone: str = Field(..., min_length=10, max_length=10, description="School phone number")
    registrationNumber: str = Field(..., min_length=3, description="School registration number")
    contactPersonName: str = Field(..., min_length=3, description="Contact person full name")
    contactPersonEmail: EmailStr = Field(..., description="Contact person email")
    contactPersonPhone: str = Field(..., min_length=10, max_length=10, description="Contact person phone")
    contactPersonDesignation: str = Field(..., description="Contact person designation")
    address: str = Field(..., min_length=10, description="Street address")
    city: str = Field(..., min_length=2, description="City")
    state: str = Field(..., description="State")
    zipCode: str = Field(..., min_length=6, max_length=6, description="PIN code")
    termsAccepted: bool = Field(..., description="Terms and conditions acceptance")
    
    class Config:
        json_schema_extra = {
            "example": {
                "schoolName": "Delhi Public School",
                "schoolType": "private",
                "establishedYear": "2000",
                "websiteUrl": "https://www.dpsdelhi.com",
                "schoolEmail": "admin@dpsdelhi.com",
                "schoolPhone": "9876543210",
                "registrationNumber": "DL/REG/2000/123",
                "contactPersonName": "Rajesh Kumar",
                "contactPersonEmail": "rajesh.kumar@dpsdelhi.com",
                "contactPersonPhone": "9876543211",
                "contactPersonDesignation": "Principal",
                "address": "Sector 45, Mathura Road",
                "city": "New Delhi",
                "state": "DL",
                "zipCode": "110025",
                "termsAccepted": True
            }
        }

class SchoolOnboardingResponse(BaseModel):
    """Response for school onboarding application"""
    message: str
    application_id: str
    school_email: str
    status: str
    submitted_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "School onboarding application submitted successfully",
                "application_id": "APP-2024-001",
                "school_email": "admin@testschool.com",
                "status": "pending_review",
                "submitted_at": "2024-10-29T10:30:00Z"
            }
        }
