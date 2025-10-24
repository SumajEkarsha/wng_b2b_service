from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.response import success_response
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.case import Case, CaseStatus, RiskLevel
from app.models.observation import Observation
from app.models.assessment import Assessment
from app.models.class_model import Class
from app.models.school import School
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()

@router.post("/")
async def create_school_admin(
    admin_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new principal/admin"""
    # Ensure role is principal or admin
    if admin_data.role not in [UserRole.PRINCIPAL, UserRole.ADMIN]:
        raise HTTPException(
            status_code=400,
            detail="Role must be 'principal' or 'admin' for this endpoint"
        )
    
    # Validate school exists
    school = db.query(School).filter(School.school_id == admin_data.school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == admin_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    from app.core.security import get_password_hash
    
    # Convert Pydantic models to dict for JSON storage
    profile_dict = admin_data.profile.dict() if admin_data.profile and hasattr(admin_data.profile, 'dict') else admin_data.profile
    availability_dict = admin_data.availability.dict() if admin_data.availability and hasattr(admin_data.availability, 'dict') else admin_data.availability
    
    admin = User(
        email=admin_data.email,
        display_name=admin_data.display_name,
        role=admin_data.role,
        phone=admin_data.phone,
        school_id=admin_data.school_id,
        hashed_password=get_password_hash(admin_data.password),
        profile=profile_dict,
        availability=availability_dict
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return success_response(admin)

@router.get("/")
async def list_school_admins(
    school_id: UUID,  # Required parameter
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all principals and admins in a school"""
    admins = db.query(User).filter(
        User.school_id == school_id,
        User.role.in_([UserRole.PRINCIPAL, UserRole.ADMIN])
    ).offset(skip).limit(limit).all()
    
    return success_response(admins)

@router.get("/{admin_id}")
async def get_school_admin(
    admin_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific principal/admin by ID"""
    admin = db.query(User).filter(
        User.user_id == admin_id,
        User.role.in_([UserRole.PRINCIPAL, UserRole.ADMIN])
    ).first()
    
    if not admin:
        raise HTTPException(status_code=404, detail="School admin not found")
    return success_response(admin)

@router.get("/dashboard/overview")
async def get_school_overview(
    school_id: UUID,  # Required parameter
    db: Session = Depends(get_db)
):
    """Get comprehensive school overview dashboard"""
    
    # Total counts
    total_students = db.query(Student).filter(Student.school_id == school_id).count()
    total_classes = db.query(Class).filter(Class.school_id == school_id).count()
    total_teachers = db.query(User).filter(
        User.school_id == school_id,
        User.role == UserRole.TEACHER
    ).count()
    total_counsellors = db.query(User).filter(
        User.school_id == school_id,
        User.role == UserRole.COUNSELLOR
    ).count()
    
    # Get all students for this school to filter cases
    student_ids = [s.student_id for s in db.query(Student.student_id).filter(Student.school_id == school_id).all()]
    
    # Cases statistics
    total_cases = db.query(Case).filter(Case.student_id.in_(student_ids)).count()
    active_cases = db.query(Case).filter(
        Case.student_id.in_(student_ids),
        Case.status != CaseStatus.CLOSED
    ).count()
    
    # Cases by risk level (active only)
    critical_cases = db.query(Case).filter(
        Case.student_id.in_(student_ids),
        Case.risk_level == RiskLevel.CRITICAL,
        Case.status != CaseStatus.CLOSED
    ).count()
    
    high_risk_cases = db.query(Case).filter(
        Case.student_id.in_(student_ids),
        Case.risk_level == RiskLevel.HIGH,
        Case.status != CaseStatus.CLOSED
    ).count()
    
    medium_risk_cases = db.query(Case).filter(
        Case.student_id.in_(student_ids),
        Case.risk_level == RiskLevel.MEDIUM,
        Case.status != CaseStatus.CLOSED
    ).count()
    
    low_risk_cases = db.query(Case).filter(
        Case.student_id.in_(student_ids),
        Case.risk_level == RiskLevel.LOW,
        Case.status != CaseStatus.CLOSED
    ).count()
    
    # Recent observations (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_observations = db.query(Observation).filter(
        Observation.student_id.in_(student_ids),
        Observation.timestamp >= thirty_days_ago
    ).count()
    
    # === COMPREHENSIVE ASSESSMENT DATA ===
    from app.models.assessment import StudentResponse, AssessmentTemplate
    
    # Count recent distinct assessments (last 30 days)
    recent_assessments_count = db.query(StudentResponse).filter(
        StudentResponse.student_id.in_(student_ids),
        StudentResponse.completed_at >= thirty_days_ago
    ).distinct(StudentResponse.assessment_id).count() if student_ids else 0
    
    # Get all completed assessment responses for school
    all_completed_responses = db.query(StudentResponse).filter(
        StudentResponse.student_id.in_(student_ids),
        StudentResponse.completed_at.isnot(None)
    ).all() if student_ids else []
    
    # Calculate assessment analytics
    assessment_scores = []
    assessment_by_category = {}
    assessment_by_grade = {}
    student_assessment_count = {}
    
    for response in all_completed_responses:
        if response.score is not None:
            assessment_scores.append(response.score)
        
        # Track by student
        if response.student_id not in student_assessment_count:
            student_assessment_count[response.student_id] = 0
        student_assessment_count[response.student_id] += 1
        
        # Get assessment category and student grade
        assessment = db.query(Assessment).filter(
            Assessment.assessment_id == response.assessment_id
        ).first()
        
        if assessment and assessment.template:
            category = assessment.template.category or "General"
            if category not in assessment_by_category:
                assessment_by_category[category] = {"total_score": 0, "count": 0, "scores": []}
            if response.score is not None:
                assessment_by_category[category]["total_score"] += response.score
                assessment_by_category[category]["count"] += 1
                assessment_by_category[category]["scores"].append(response.score)
        
        # Track by grade
        student = db.query(Student).filter(Student.student_id == response.student_id).first()
        if student and student.class_obj:
            grade = student.class_obj.grade
            if grade not in assessment_by_grade:
                assessment_by_grade[grade] = {"total_score": 0, "count": 0, "scores": []}
            if response.score is not None:
                assessment_by_grade[grade]["total_score"] += response.score
                assessment_by_grade[grade]["count"] += 1
                assessment_by_grade[grade]["scores"].append(response.score)
    
    # Calculate statistics
    avg_assessment_score = sum(assessment_scores) / len(assessment_scores) if assessment_scores else 0
    students_assessed = len(student_assessment_count)
    assessment_completion_rate = (students_assessed / total_students * 100) if total_students > 0 else 0
    
    # Category breakdown
    category_breakdown = []
    for category, data in assessment_by_category.items():
        avg_score = data["total_score"] / data["count"] if data["count"] > 0 else 0
        category_breakdown.append({
            "category": category,
            "average_score": round(avg_score, 2),
            "total_assessments": data["count"],
            "min_score": round(min(data["scores"]), 2) if data["scores"] else 0,
            "max_score": round(max(data["scores"]), 2) if data["scores"] else 0
        })
    
    # Grade level breakdown
    grade_breakdown = []
    for grade, data in assessment_by_grade.items():
        avg_score = data["total_score"] / data["count"] if data["count"] > 0 else 0
        grade_breakdown.append({
            "grade": grade,
            "average_score": round(avg_score, 2),
            "total_assessments": data["count"],
            "min_score": round(min(data["scores"]), 2) if data["scores"] else 0,
            "max_score": round(max(data["scores"]), 2) if data["scores"] else 0
        })
    
    # Sort by grade
    grade_breakdown.sort(key=lambda x: x["grade"])
    
    # Get all students with assessment completion details
    all_students = db.query(Student).filter(Student.school_id == school_id).all()
    students_with_assessments = []
    students_without_assessments = []
    
    for student in all_students:
        count = student_assessment_count.get(student.student_id, 0)
        
        if count > 0:
            student_responses = [r for r in all_completed_responses if r.student_id == student.student_id]
            total_score = sum(r.score for r in student_responses if r.score is not None)
            avg_score = total_score / count if count > 0 else 0
            
            # Get last assessment date
            last_assessment = max(student_responses, key=lambda r: r.completed_at if r.completed_at else datetime.min) if student_responses else None
            
            # Check if student has active case
            case = db.query(Case).filter(
                Case.student_id == student.student_id,
                Case.status != CaseStatus.CLOSED
            ).first()
            
            students_with_assessments.append({
                "student_id": str(student.student_id),
                "student_name": f"{student.first_name} {student.last_name}",
                "grade": student.class_obj.grade if student.class_obj else None,
                "class_name": student.class_obj.name if student.class_obj else None,
                "assessments_completed": len(set(r.assessment_id for r in student_responses)),
                "total_responses": count,
                "average_score": round(avg_score, 2),
                "last_assessment_date": last_assessment.completed_at.isoformat() if last_assessment and last_assessment.completed_at else None,
                "has_active_case": case is not None,
                "risk_level": case.risk_level.value if case else None
            })
        else:
            students_without_assessments.append({
                "student_id": str(student.student_id),
                "student_name": f"{student.first_name} {student.last_name}",
                "grade": student.class_obj.grade if student.class_obj else None,
                "class_name": student.class_obj.name if student.class_obj else None
            })
    
    # Sort by average score
    students_with_assessments.sort(key=lambda x: x["average_score"], reverse=True)
    top_performers = students_with_assessments[:10]
    underperformers = [s for s in reversed(students_with_assessments[-10:]) if s["average_score"] > 0]
    
    # Trend analysis (compare last 30 days vs previous 30 days)
    sixty_days_ago = datetime.utcnow() - timedelta(days=60)
    previous_period_responses = db.query(StudentResponse).filter(
        StudentResponse.student_id.in_(student_ids),
        StudentResponse.completed_at >= sixty_days_ago,
        StudentResponse.completed_at < thirty_days_ago
    ).all() if student_ids else []
    
    previous_scores = [r.score for r in previous_period_responses if r.score is not None]
    previous_avg = sum(previous_scores) / len(previous_scores) if previous_scores else 0
    
    recent_period_responses = db.query(StudentResponse).filter(
        StudentResponse.student_id.in_(student_ids),
        StudentResponse.completed_at >= thirty_days_ago
    ).all() if student_ids else []
    
    recent_scores = [r.score for r in recent_period_responses if r.score is not None]
    recent_avg = sum(recent_scores) / len(recent_scores) if recent_scores else 0
    
    trend = "improving" if recent_avg > previous_avg else "declining" if recent_avg < previous_avg else "stable"
    trend_change = round(((recent_avg - previous_avg) / previous_avg * 100), 2) if previous_avg > 0 else 0
    
    # At-risk percentage
    at_risk_students = critical_cases + high_risk_cases + medium_risk_cases
    at_risk_percent = (at_risk_students / total_students * 100) if total_students > 0 else 0
    
    return success_response({
        "school_id": str(school_id),
        "overview": {
            "total_students": total_students,
            "total_classes": total_classes,
            "total_teachers": total_teachers,
            "total_counsellors": total_counsellors
        },
        "mental_health_metrics": {
            "total_cases": total_cases,
            "active_cases": active_cases,
            "closed_cases": total_cases - active_cases,
            "at_risk_students": at_risk_students,
            "at_risk_percentage": round(at_risk_percent, 2)
        },
        "cases_by_risk_level": {
            "critical": critical_cases,
            "high": high_risk_cases,
            "medium": medium_risk_cases,
            "low": low_risk_cases
        },
        "assessment_analytics": {
            "total_assessments_completed": len(all_completed_responses),
            "recent_assessments_30_days": recent_assessments_count,
            "students_assessed": students_assessed,
            "students_not_assessed": len(students_without_assessments),
            "assessment_completion_rate": round(assessment_completion_rate, 1),
            "average_assessment_score": round(avg_assessment_score, 2),
            "by_category": category_breakdown,
            "by_grade": grade_breakdown,
            "top_performers": top_performers,
            "underperformers": underperformers,
            "students_with_assessments": students_with_assessments,
            "students_without_assessments": students_without_assessments,
            "trend_analysis": {
                "trend": trend,
                "change_percentage": trend_change,
                "previous_period_avg": round(previous_avg, 2),
                "recent_period_avg": round(recent_avg, 2),
                "previous_period_count": len(previous_scores),
                "recent_period_count": len(recent_scores)
            }
        },
        "recent_activity_30_days": {
            "observations": recent_observations,
            "assessments_completed": recent_assessments_count
        }
    })

@router.get("/dashboard/at-risk-students")
async def get_at_risk_students(
    school_id: UUID,  # Required parameter
    risk_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of at-risk students with their case details"""
    
    # Get all students for this school
    student_ids = [s.student_id for s in db.query(Student.student_id).filter(Student.school_id == school_id).all()]
    
    # Query active cases
    query = db.query(Case).filter(
        Case.student_id.in_(student_ids),
        Case.status != CaseStatus.CLOSED
    )
    
    if risk_level:
        query = query.filter(Case.risk_level == risk_level)
    else:
        # Default: show medium, high, and critical only
        query = query.filter(Case.risk_level.in_([RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]))
    
    cases = query.offset(skip).limit(limit).all()
    
    result = []
    for case in cases:
        student = db.query(Student).filter(Student.student_id == case.student_id).first()
        counsellor = db.query(User).filter(User.user_id == case.assigned_counsellor).first()
        
        result.append({
            "case_id": str(case.case_id),
            "student": {
                "student_id": str(student.student_id),
                "name": f"{student.first_name} {student.last_name}",
                "class_id": str(student.class_id) if student.class_id else None
            },
            "risk_level": case.risk_level.value,
            "status": case.status.value,
            "tags": case.tags,
            "assigned_counsellor": counsellor.display_name if counsellor else None,
            "created_at": case.created_at.isoformat(),
            "days_open": (datetime.utcnow() - case.created_at).days
        })
    
    return success_response({
        "school_id": str(school_id),
        "total_at_risk": len(result),
        "students": result
    })

@router.get("/dashboard/counsellor-workload")
async def get_counsellor_workload(
    school_id: UUID,  # Required parameter
    db: Session = Depends(get_db)
):
    """Get workload distribution across counsellors"""
    
    counsellors = db.query(User).filter(
        User.school_id == school_id,
        User.role == UserRole.COUNSELLOR
    ).all()
    
    workload = []
    for counsellor in counsellors:
        total_cases = db.query(Case).filter(Case.assigned_counsellor == counsellor.user_id).count()
        active_cases = db.query(Case).filter(
            Case.assigned_counsellor == counsellor.user_id,
            Case.status != CaseStatus.CLOSED
        ).count()
        
        critical = db.query(Case).filter(
            Case.assigned_counsellor == counsellor.user_id,
            Case.risk_level == RiskLevel.CRITICAL,
            Case.status != CaseStatus.CLOSED
        ).count()
        
        high = db.query(Case).filter(
            Case.assigned_counsellor == counsellor.user_id,
            Case.risk_level == RiskLevel.HIGH,
            Case.status != CaseStatus.CLOSED
        ).count()
        
        workload.append({
            "counsellor_id": str(counsellor.user_id),
            "name": counsellor.display_name,
            "email": counsellor.email,
            "total_cases": total_cases,
            "active_cases": active_cases,
            "high_priority_cases": critical + high,
            "availability": counsellor.availability
        })
    
    return success_response({
        "school_id": str(school_id),
        "total_counsellors": len(counsellors),
        "workload": workload
    })

@router.get("/dashboard/grade-level-analysis")
async def get_grade_level_analysis(
    school_id: UUID,  # Required parameter
    db: Session = Depends(get_db)
):
    """Get mental health metrics by grade level"""
    
    classes = db.query(Class).filter(Class.school_id == school_id).all()
    
    grade_data = {}
    for class_obj in classes:
        grade = class_obj.grade
        if grade not in grade_data:
            grade_data[grade] = {
                "grade": grade,
                "total_students": 0,
                "total_classes": 0,
                "active_cases": 0,
                "observations": 0
            }
        
        # Count students in this class
        students_count = db.query(Student).filter(Student.class_id == class_obj.class_id).count()
        grade_data[grade]["total_students"] += students_count
        grade_data[grade]["total_classes"] += 1
        
        # Get student IDs for this class
        student_ids = [s.student_id for s in db.query(Student.student_id).filter(Student.class_id == class_obj.class_id).all()]
        
        # Count active cases
        active_cases = db.query(Case).filter(
            Case.student_id.in_(student_ids),
            Case.status != CaseStatus.CLOSED
        ).count()
        grade_data[grade]["active_cases"] += active_cases
        
        # Count observations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        observations = db.query(Observation).filter(
            Observation.student_id.in_(student_ids),
            Observation.timestamp >= thirty_days_ago
        ).count()
        grade_data[grade]["observations"] += observations
    
    # Calculate percentages
    for grade in grade_data:
        total = grade_data[grade]["total_students"]
        if total > 0:
            grade_data[grade]["case_rate_percent"] = round(
                (grade_data[grade]["active_cases"] / total) * 100, 2
            )
        else:
            grade_data[grade]["case_rate_percent"] = 0
    
    return success_response({
        "school_id": str(school_id),
        "grade_levels": list(grade_data.values())
    })

@router.get("/reports/monthly-summary")
async def get_monthly_summary(
    school_id: UUID,  # Required parameter
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """Get monthly summary report"""
    
    from datetime import date
    from calendar import monthrange
    from app.models.assessment import StudentResponse
    
    # Get date range for the month
    _, last_day = monthrange(year, month)
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, last_day, 23, 59, 59)
    
    # Get all students for this school
    student_ids = [s.student_id for s in db.query(Student.student_id).filter(Student.school_id == school_id).all()]
    
    # Cases created this month
    cases_created = db.query(Case).filter(
        Case.student_id.in_(student_ids),
        Case.created_at >= start_date,
        Case.created_at <= end_date
    ).count()
    
    # Cases closed this month
    cases_closed = db.query(Case).filter(
        Case.student_id.in_(student_ids),
        Case.closed_at >= start_date,
        Case.closed_at <= end_date
    ).count()
    
    # Observations this month
    observations = db.query(Observation).filter(
        Observation.student_id.in_(student_ids),
        Observation.timestamp >= start_date,
        Observation.timestamp <= end_date
    ).count()
    
    # Assessments completed this month (distinct assessments)
    assessments = db.query(StudentResponse).filter(
        StudentResponse.student_id.in_(student_ids),
        StudentResponse.completed_at >= start_date,
        StudentResponse.completed_at <= end_date
    ).distinct(StudentResponse.assessment_id).count() if student_ids else 0
    
    return success_response({
        "school_id": str(school_id),
        "period": f"{year}-{month:02d}",
        "summary": {
            "cases_created": cases_created,
            "cases_closed": cases_closed,
            "observations_recorded": observations,
            "assessments_completed": assessments
        }
    })

@router.patch("/{admin_id}")
async def update_school_admin(
    admin_id: UUID,
    admin_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update school admin information"""
    admin = db.query(User).filter(
        User.user_id == admin_id,
        User.role.in_([UserRole.PRINCIPAL, UserRole.ADMIN])
    ).first()
    
    if not admin:
        raise HTTPException(status_code=404, detail="School admin not found")
    
    update_data = admin_update.dict(exclude_unset=True)
    
    # Convert Pydantic models to dict for JSON storage
    if 'profile' in update_data and update_data['profile'] is not None:
        if hasattr(update_data['profile'], 'dict'):
            update_data['profile'] = update_data['profile'].dict()
    
    if 'availability' in update_data and update_data['availability'] is not None:
        if hasattr(update_data['availability'], 'dict'):
            update_data['availability'] = update_data['availability'].dict()
    
    for field, value in update_data.items():
        setattr(admin, field, value)
    
    db.commit()
    db.refresh(admin)
    return success_response(admin)

@router.delete("/{admin_id}")
async def delete_school_admin(
    admin_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a school admin"""
    admin = db.query(User).filter(
        User.user_id == admin_id,
        User.role.in_([UserRole.PRINCIPAL, UserRole.ADMIN])
    ).first()
    
    if not admin:
        raise HTTPException(status_code=404, detail="School admin not found")
    
    db.delete(admin)
    db.commit()
    return success_response({"message": "School admin deleted successfully", "admin_id": str(admin_id)})
