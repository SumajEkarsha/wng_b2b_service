from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
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
    
    # === OPTIMIZED ASSESSMENT DATA ===
    from app.models.assessment import StudentResponse, AssessmentTemplate
    
    # Count recent distinct assessments (last 30 days)
    recent_assessments_count = db.query(StudentResponse).filter(
        StudentResponse.student_id.in_(student_ids),
        StudentResponse.completed_at >= thirty_days_ago
    ).distinct(StudentResponse.assessment_id).count() if student_ids else 0
    
    # Get all completed assessment responses with eager loading
    all_completed_responses = db.query(StudentResponse).options(
        joinedload(StudentResponse.assessment).joinedload(Assessment.template)
    ).filter(
        StudentResponse.student_id.in_(student_ids),
        StudentResponse.completed_at.isnot(None)
    ).all() if student_ids else []
    
    # Pre-load all students at once
    students_map = {}
    if student_ids:
        students_list = db.query(Student).options(
            joinedload(Student.class_obj)
        ).filter(Student.student_id.in_(student_ids)).all()
        students_map = {s.student_id: s for s in students_list}
    
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
        
        # Get assessment category from eager-loaded relationship
        if response.assessment and response.assessment.template:
            category = response.assessment.template.category or "General"
            if category not in assessment_by_category:
                assessment_by_category[category] = {"total_score": 0, "count": 0, "scores": []}
            if response.score is not None:
                assessment_by_category[category]["total_score"] += response.score
                assessment_by_category[category]["count"] += 1
                assessment_by_category[category]["scores"].append(response.score)
        
        # Track by grade using pre-loaded students
        student = students_map.get(response.student_id)
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
    students_not_assessed = total_students - students_assessed
    assessment_completion_rate = (students_assessed / total_students * 100) if total_students > 0 else 0
    
    # Category breakdown
    category_breakdown = []
    for category, data in assessment_by_category.items():
        avg_score = data["total_score"] / data["count"] if data["count"] > 0 else 0
        category_breakdown.append({
            "category": category,
            "average_score": round(avg_score, 2),
            "total_assessments": data["count"]
        })
    
    # Grade level breakdown
    grade_breakdown = []
    for grade, data in assessment_by_grade.items():
        avg_score = data["total_score"] / data["count"] if data["count"] > 0 else 0
        grade_breakdown.append({
            "grade": grade,
            "average_score": round(avg_score, 2),
            "total_assessments": data["count"]
        })
    
    # Sort by grade
    grade_breakdown.sort(key=lambda x: x["grade"])
    
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
    
    # Calculate monthly trends (last 6 months)
    from dateutil.relativedelta import relativedelta
    monthly_trends = []
    for i in range(5, -1, -1):  # Last 6 months
        month_start = datetime.utcnow() - relativedelta(months=i)
        month_end = month_start + relativedelta(months=1)
        month_name = month_start.strftime("%b %Y")
        
        # Cases opened/closed in this month
        month_cases_opened = db.query(Case).filter(
            Case.student_id.in_(student_ids),
            Case.created_at >= month_start,
            Case.created_at < month_end
        ).count() if student_ids else 0
        
        month_cases_closed = db.query(Case).filter(
            Case.student_id.in_(student_ids),
            Case.closed_at >= month_start,
            Case.closed_at < month_end
        ).count() if student_ids else 0
        
        # Assessments completed in this month
        month_assessments = db.query(StudentResponse).filter(
            StudentResponse.student_id.in_(student_ids),
            StudentResponse.completed_at >= month_start,
            StudentResponse.completed_at < month_end
        ).count() if student_ids else 0
        
        # Average wellbeing score for this month
        month_responses = db.query(StudentResponse).filter(
            StudentResponse.student_id.in_(student_ids),
            StudentResponse.completed_at >= month_start,
            StudentResponse.completed_at < month_end,
            StudentResponse.score.isnot(None)
        ).all() if student_ids else []
        
        month_scores = [r.score for r in month_responses if r.score is not None]
        month_avg_score = sum(month_scores) / len(month_scores) if month_scores else 0
        
        monthly_trends.append({
            "month": month_name,
            "wellbeingIndex": round(month_avg_score, 1),
            "casesOpened": month_cases_opened,
            "casesClosed": month_cases_closed,
            "assessmentsCompleted": month_assessments
        })
    
    # Get class-level metrics with eager loading
    classes = db.query(Class).options(
        joinedload(Class.teacher)
    ).filter(Class.school_id == school_id).all()
    
    # Pre-load all students with their classes
    all_students_with_classes = db.query(Student).options(
        joinedload(Student.class_obj)
    ).filter(Student.school_id == school_id).all()
    
    # Group students by class
    students_by_class = {}
    for student in all_students_with_classes:
        if student.class_id:
            if student.class_id not in students_by_class:
                students_by_class[student.class_id] = []
            students_by_class[student.class_id].append(student.student_id)
    
    # Pre-load all cases for the school
    all_cases = db.query(Case).filter(
        Case.student_id.in_(student_ids),
        Case.status != CaseStatus.CLOSED
    ).all() if student_ids else []
    
    # Group cases by student
    cases_by_student = {}
    for case in all_cases:
        cases_by_student[case.student_id] = case
    
    # Pre-load assessment responses grouped by student
    responses_by_student = {}
    for response in all_completed_responses:
        if response.student_id not in responses_by_student:
            responses_by_student[response.student_id] = []
        if response.score is not None:
            responses_by_student[response.student_id].append(response.score)
    
    class_metrics = []
    for class_obj in classes:
        class_student_ids = students_by_class.get(class_obj.class_id, [])
        
        if not class_student_ids:
            continue
        
        # Count at-risk students in this class
        at_risk_count = sum(
            1 for sid in class_student_ids 
            if sid in cases_by_student and cases_by_student[sid].risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
        
        # Calculate average wellbeing for this class
        class_scores = []
        for sid in class_student_ids:
            if sid in responses_by_student:
                class_scores.extend(responses_by_student[sid])
        
        class_wellbeing = round(sum(class_scores) / len(class_scores), 1) if class_scores else 0
        
        class_metrics.append({
            "id": str(class_obj.class_id),
            "name": class_obj.name,
            "grade": class_obj.grade,
            "section": class_obj.section or "",
            "teacher": class_obj.teacher.display_name if class_obj.teacher else "Unassigned",
            "totalStudents": len(class_student_ids),
            "wellbeingIndex": class_wellbeing,
            "atRiskCount": at_risk_count
        })
    
    # Sort classes by grade
    class_metrics.sort(key=lambda x: (x["grade"], x["section"]))
    
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
            "students_not_assessed": students_not_assessed,
            "assessment_completion_rate": round(assessment_completion_rate, 1),
            "average_assessment_score": round(avg_assessment_score, 2),
            "by_category": category_breakdown,
            "by_grade": grade_breakdown,
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
        },
        "monthly_trends": monthly_trends,
        "class_metrics": class_metrics,
        "counsellor_workload": []  # Will be populated by separate endpoint
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
    
    # Query active cases with eager loading
    query = db.query(Case).options(
        joinedload(Case.student)
    ).filter(
        Case.student_id.in_(student_ids),
        Case.status != CaseStatus.CLOSED
    )
    
    if risk_level:
        query = query.filter(Case.risk_level == risk_level)
    else:
        # Default: show medium, high, and critical only
        query = query.filter(Case.risk_level.in_([RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]))
    
    cases = query.offset(skip).limit(limit).all()
    
    # Batch load counsellors
    counsellor_ids = [c.assigned_counsellor for c in cases if c.assigned_counsellor]
    counsellors_map = {}
    if counsellor_ids:
        counsellors = db.query(User).filter(User.user_id.in_(counsellor_ids)).all()
        counsellors_map = {c.user_id: c for c in counsellors}
    
    result = []
    for case in cases:
        student = case.student
        counsellor = counsellors_map.get(case.assigned_counsellor) if case.assigned_counsellor else None
        
        # Get parent information from student record
        parents_data = []
        if student.parent_email or student.parent_phone:
            # Create a parent entry from student's parent fields
            parent_info = {
                "name": "Parent/Guardian",
                "relationship": "Parent/Guardian",
                "phone": student.parent_phone,
                "email": student.parent_email,
                "is_primary": True,
                "consent_given": student.consent_status.value == "GRANTED" if student.consent_status else None
            }
            parents_data.append(parent_info)
        
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
            "days_open": (datetime.utcnow() - case.created_at).days,
            "parents": parents_data
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
    
    # Batch load all cases for these counsellors
    counsellor_ids = [c.user_id for c in counsellors]
    all_cases = db.query(Case).filter(
        Case.assigned_counsellor.in_(counsellor_ids)
    ).all() if counsellor_ids else []
    
    # Group cases by counsellor
    cases_by_counsellor = {}
    for case in all_cases:
        if case.assigned_counsellor not in cases_by_counsellor:
            cases_by_counsellor[case.assigned_counsellor] = []
        cases_by_counsellor[case.assigned_counsellor].append(case)
    
    workload = []
    for counsellor in counsellors:
        counsellor_cases = cases_by_counsellor.get(counsellor.user_id, [])
        total_cases = len(counsellor_cases)
        active_cases = sum(1 for c in counsellor_cases if c.status != CaseStatus.CLOSED)
        critical = sum(1 for c in counsellor_cases if c.risk_level == RiskLevel.CRITICAL and c.status != CaseStatus.CLOSED)
        high = sum(1 for c in counsellor_cases if c.risk_level == RiskLevel.HIGH and c.status != CaseStatus.CLOSED)
        
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
