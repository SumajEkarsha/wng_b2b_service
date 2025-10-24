from fastapi import APIRouter
from app.api.v1.endpoints import (
    users, cases, students, observations, 
    assessments, schools, classes, teachers, counsellors, school_admin, resources
)

api_router = APIRouter()

# Onboarding endpoints
api_router.include_router(schools.router, prefix="/schools", tags=["schools"])
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
