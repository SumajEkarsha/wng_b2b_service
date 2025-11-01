from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, cases, students, observations, 
    assessments, schools, classes, teachers, counsellors, school_admin, resources,
    calendar_events, consent_records, goals, ai_recommendations, risk_alerts,
    activities, daily_boosters, session_notes, templates
)

api_router = APIRouter()

# Authentication endpoints (no auth required)
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Onboarding endpoints
api_router.include_router(schools.router, prefix="/schools", tags=["schools"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(classes.router, prefix="/classes", tags=["classes"])
api_router.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
api_router.include_router(counsellors.router, prefix="/counsellors", tags=["counsellors"])
api_router.include_router(school_admin.router, prefix="/school-admin", tags=["school-admin"])

# Core endpoints
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(observations.router, prefix="/observations", tags=["observations"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])

# Mental health endpoints
api_router.include_router(session_notes.router, prefix="/session-notes", tags=["session-notes"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])
api_router.include_router(ai_recommendations.router, prefix="/ai-recommendations", tags=["ai-recommendations"])
api_router.include_router(risk_alerts.router, prefix="/risk-alerts", tags=["risk-alerts"])
api_router.include_router(consent_records.router, prefix="/consent-records", tags=["consent-records"])
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(daily_boosters.router, prefix="/daily-boosters", tags=["daily-boosters"])
api_router.include_router(calendar_events.router, prefix="/calendar-events", tags=["calendar-events"])
