from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.response import success_response
from app.models.user import User, UserRole
from app.models.class_model import Class
from app.models.school import School
from app.models.student import Student
from app.models.case import Case, CaseStatus, RiskLevel
from app.models.observation import Observation, Severity
from app.models.assessment import Assessment
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()

@router.post("/")
async def create_teacher(
    teacher_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new teacher"""
    # Ensure role is teacher
    if teacher_data.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=400,
            detail="Role must be 'teacher' for this endpoint"
        )
    
    # Validate school exists
    school = db.query(School).filter(School.school_id == teacher_data.school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == teacher_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    from app.core.security import get_password_hash
    
    # Convert Pydantic models to dict for JSON storage
    profile_dict = teacher_data.profile.dict() if teacher_data.profile and hasattr(teacher_data.profile, 'dict') else teacher_data.profile
    availability_dict = teacher_data.availability.dict() if teacher_data.availability and hasattr(teacher_data.availability, 'dict') else teacher_data.availability
    
    teacher = User(
        email=teacher_data.email,
        display_name=teacher_data.display_name,
        role=UserRole.TEACHER,
        phone=teacher_data.phone,
        school_id=teacher_data.school_id,
        hashed_password=get_password_hash(teacher_data.password),
        profile=profile_dict,
        availability=availability_dict
    )
    
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return success_response(teacher)

@router.get("/")
async def list_teachers(
    school_id: UUID,  # Required parameter
    skip: int = 0,
    limit: int = 100,
    subject: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all teachers in a school"""
    query = db.query(User).filter(
        User.school_id == school_id,
        User.role == UserRole.TEACHER
    )
    
    # Filter by subject if provided
    if subject:
        # Search in profile JSON field
        query = query.filter(
            User.profile.contains({"subjects": [subject]})
        )
    
    teachers = query.offset(skip).limit(limit).all()
    return success_response(teachers)

@router.get("/{teacher_id}")
async def get_teacher(
    teacher_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific teacher by ID"""
    teacher = db.query(User).filter(
        User.user_id == teacher_id,
        User.role == UserRole.TEACHER
    ).first()
    
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return success_response(teacher)

@router.get("/{teacher_id}/classes")
async def get_teacher_classes(
    teacher_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all classes assigned to a teacher"""
    teacher = db.query(User).filter(
        User.user_id == teacher_id,
        User.role == UserRole.TEACHER
    ).first()
    
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    classes = db.query(Class).filter(Class.teacher_id == teacher_id).all()
    
    return success_response([{
        "class_id": str(c.class_id),
        "name": c.name,
        "grade": c.grade,
        "section": c.section,
        "capacity": c.capacity,
        "academic_year": c.academic_year
    } for c in classes])

@router.get("/{teacher_id}/students")
async def get_teacher_students(
    teacher_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all students taught by this teacher (across all their classes)"""
    teacher = db.query(User).filter(
        User.user_id == teacher_id,
        User.role == UserRole.TEACHER
    ).first()
    
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Get all classes taught by this teacher
    classes = db.query(Class).filter(Class.teacher_id == teacher_id).all()
    
    # Get all students in those classes
    students = []
    for class_obj in classes:
        for student in class_obj.students:
            students.append({
                "student_id": str(student.student_id),
                "first_name": student.first_name,
                "last_name": student.last_name,
                "class_name": class_obj.name,
                "class_id": str(class_obj.class_id),
                "gender": student.gender.value if student.gender else None
            })
    
    return success_response(students)

@router.get("/{teacher_id}/dashboard")
async def get_teacher_dashboard(
    teacher_id: UUID,
    db: Session = Depends(get_db)
):
    """Get comprehensive teacher dashboard with class insights and student wellbeing"""
    teacher = db.query(User).filter(
        User.user_id == teacher_id,
        User.role == UserRole.TEACHER
    ).first()
    
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Get all classes taught by this teacher
    classes = db.query(Class).filter(Class.teacher_id == teacher_id).all()
    class_ids = [c.class_id for c in classes]
    
    # Get all students in these classes
    students = db.query(Student).filter(Student.class_id.in_(class_ids)).all() if class_ids else []
    student_ids = [s.student_id for s in students]
    
    # Total counts
    total_students = len(students)
    total_classes = len(classes)
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_observations = db.query(Observation).filter(
        Observation.student_id.in_(student_ids),
        Observation.timestamp >= thirty_days_ago
    ).count() if student_ids else 0
    
    # Import assessment models
    from app.models.assessment import StudentResponse, AssessmentTemplate
    
    # Count recent distinct assessments (last 30 days)
    recent_assessments_count = db.query(StudentResponse).filter(
        StudentResponse.student_id.in_(student_ids),
        StudentResponse.completed_at >= thirty_days_ago
    ).distinct(StudentResponse.assessment_id).count() if student_ids else 0
    
    # Get ALL completed assessment responses for students
    all_completed_responses = db.query(StudentResponse).filter(
        StudentResponse.student_id.in_(student_ids),
        StudentResponse.completed_at.isnot(None)
    ).all() if student_ids else []
    
    # Calculate assessment analytics
    assessment_scores = []
    assessment_by_category = {}
    student_assessment_count = {}
    
    for response in all_completed_responses:
        if response.score is not None:
            assessment_scores.append(response.score)
        
        # Track by student
        if response.student_id not in student_assessment_count:
            student_assessment_count[response.student_id] = 0
        student_assessment_count[response.student_id] += 1
        
        # Get assessment category
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
    
    # Student assessment completion details
    students_with_assessments = []
    students_without_assessments = []
    
    for student in students:
        student_responses = [r for r in all_completed_responses if r.student_id == student.student_id]
        assessments_count = len(set(r.assessment_id for r in student_responses))
        
        if assessments_count > 0:
            # Calculate average score for this student
            scores = [r.score for r in student_responses if r.score is not None]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            # Get most recent assessment
            recent = max(student_responses, key=lambda r: r.completed_at if r.completed_at else datetime.min)
            
            # Check if student has active case
            case = db.query(Case).filter(
                Case.student_id == student.student_id,
                Case.status != CaseStatus.CLOSED
            ).first()
            
            students_with_assessments.append({
                "student_id": str(student.student_id),
                "student_name": f"{student.first_name} {student.last_name}",
                "class_id": str(student.class_id) if student.class_id else None,
                "assessments_completed": assessments_count,
                "total_responses": len(student_responses),
                "average_score": round(avg_score, 2),
                "last_assessment_date": recent.completed_at.isoformat() if recent.completed_at else None,
                "has_active_case": case is not None,
                "risk_level": case.risk_level.value if case else None
            })
        else:
            students_without_assessments.append({
                "student_id": str(student.student_id),
                "student_name": f"{student.first_name} {student.last_name}",
                "class_id": str(student.class_id) if student.class_id else None
            })
    
    # Sort by number of assessments completed (descending)
    students_with_assessments.sort(key=lambda x: x["assessments_completed"], reverse=True)
    
    # Recent assessments details (last 30 days)
    recent_assessments_list = db.query(Assessment).join(
        StudentResponse, Assessment.assessment_id == StudentResponse.assessment_id
    ).filter(
        StudentResponse.student_id.in_(student_ids),
        StudentResponse.completed_at >= thirty_days_ago
    ).distinct().limit(10).all() if student_ids else []
    
    recent_assessments_detail = []
    for assessment in recent_assessments_list:
        template = db.query(AssessmentTemplate).filter(
            AssessmentTemplate.template_id == assessment.template_id
        ).first()
        
        responses = db.query(StudentResponse).filter(
            StudentResponse.assessment_id == assessment.assessment_id,
            StudentResponse.student_id.in_(student_ids),
            StudentResponse.completed_at >= thirty_days_ago
        ).all()
        
        scores = [r.score for r in responses if r.score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        recent_assessments_detail.append({
            "assessment_id": str(assessment.assessment_id),
            "title": assessment.title,
            "template_name": template.name if template else "Unknown",
            "category": template.category if template else None,
            "students_completed": len(set(r.student_id for r in responses)),
            "average_score": round(avg_score, 2),
            "created_at": assessment.created_at.isoformat() if assessment.created_at else None
        })
    
    # Cases and wellbeing
    active_cases = db.query(Case).filter(
        Case.student_id.in_(student_ids),
        Case.status != CaseStatus.CLOSED
    ).count()
    
    # Risk level breakdown
    critical_students = db.query(Case).filter(
        Case.student_id.in_(student_ids),
        Case.risk_level == RiskLevel.CRITICAL,
        Case.status != CaseStatus.CLOSED
    ).count()
    
    high_risk_students = db.query(Case).filter(
        Case.student_id.in_(student_ids),
        Case.risk_level == RiskLevel.HIGH,
        Case.status != CaseStatus.CLOSED
    ).count()
    
    medium_risk_students = db.query(Case).filter(
        Case.student_id.in_(student_ids),
        Case.risk_level == RiskLevel.MEDIUM,
        Case.status != CaseStatus.CLOSED
    ).count()
    
    # Calculate wellbeing percentage (students without active cases)
    students_at_risk = critical_students + high_risk_students + medium_risk_students
    wellbeing_percentage = ((total_students - students_at_risk) / total_students * 100) if total_students > 0 else 100
    
    return success_response({
        "teacher_id": str(teacher_id),
        "teacher_name": teacher.display_name,
        "overview": {
            "total_classes": total_classes,
            "total_students": total_students,
            "active_cases": active_cases,
            "overall_wellbeing_percentage": round(wellbeing_percentage, 1)
        },
        "student_wellbeing": {
            "students_at_risk": students_at_risk,
            "critical": critical_students,
            "high_risk": high_risk_students,
            "medium_risk": medium_risk_students,
            "healthy": total_students - students_at_risk
        },
        "assessment_analytics": {
            "total_assessments_completed": len(all_completed_responses),
            "recent_assessments_30_days": recent_assessments_count,
            "students_assessed": students_assessed,
            "students_not_assessed": len(students_without_assessments),
            "assessment_completion_rate": round(assessment_completion_rate, 1),
            "average_assessment_score": round(avg_assessment_score, 2),
            "by_category": category_breakdown,
            "recent_assessments": recent_assessments_detail,
            "students_with_assessments": students_with_assessments,
            "students_without_assessments": students_without_assessments
        },
        "recent_activity_30_days": {
            "observations": recent_observations,
            "assessments_completed": recent_assessments_count
        }
    })

@router.get("/{teacher_id}/classes-insights")
async def get_all_classes_insights(
    teacher_id: UUID,
    db: Session = Depends(get_db)
):
    """Get insights for all classes taught by this teacher"""
    teacher = db.query(User).filter(
        User.user_id == teacher_id,
        User.role == UserRole.TEACHER
    ).first()
    
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Get all classes taught by this teacher
    classes = db.query(Class).filter(Class.teacher_id == teacher_id).all()
    
    if not classes:
        return {
            "teacher_id": str(teacher_id),
            "teacher_name": teacher.display_name,
            "total_classes": 0,
            "classes": []
        }
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    classes_insights = []
    
    for class_obj in classes:
        # Get students in this class
        students = db.query(Student).filter(Student.class_id == class_obj.class_id).all()
        student_ids = [s.student_id for s in students]
        
        if not student_ids:
            classes_insights.append({
                "class_id": str(class_obj.class_id),
                "class_name": class_obj.name,
                "grade": class_obj.grade,
                "section": class_obj.section,
                "total_students": 0,
                "performance_metrics": {
                    "average_assessment_score": 0,
                    "completed_assessments": 0,
                    "assessments_per_student": 0
                },
                "wellbeing_metrics": {
                    "active_cases": 0,
                    "recent_observations": 0,
                    "observation_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0}
                },
                "students": []
            })
            continue
        
        # Get assessment performance via StudentResponse
        from app.models.assessment import StudentResponse as SR
        student_responses = db.query(SR).filter(
            SR.student_id.in_(student_ids),
            SR.completed_at.isnot(None)
        ).all() if student_ids else []
        
        total_score = 0
        completed_assessments = 0
        assessment_ids = set()
        
        for response in student_responses:
            if response.score is not None:
                total_score += response.score
                completed_assessments += 1
                assessment_ids.add(response.assessment_id)
        
        avg_performance = (total_score / completed_assessments) if completed_assessments > 0 else 0
        
        # Recent observations
        recent_observations = db.query(Observation).filter(
            Observation.student_id.in_(student_ids),
            Observation.timestamp >= thirty_days_ago
        ).all()
        
        obs_severity = {
            "critical": len([o for o in recent_observations if o.severity == Severity.CRITICAL]),
            "high": len([o for o in recent_observations if o.severity == Severity.HIGH]),
            "medium": len([o for o in recent_observations if o.severity == Severity.MEDIUM]),
            "low": len([o for o in recent_observations if o.severity == Severity.LOW])
        }
        
        # Active cases
        active_cases = db.query(Case).filter(
            Case.student_id.in_(student_ids),
            Case.status != CaseStatus.CLOSED
        ).count()
        
        # Student details with wellbeing status
        student_details = []
        for student in students:
            case = db.query(Case).filter(
                Case.student_id == student.student_id,
                Case.status != CaseStatus.CLOSED
            ).first()
            
            # Get recent assessment score from StudentResponse
            recent_response = db.query(SR).filter(
                SR.student_id == student.student_id,
                SR.completed_at.isnot(None)
            ).order_by(SR.completed_at.desc()).first()
            
            recent_score = None
            if recent_response and recent_response.score is not None:
                recent_score = recent_response.score
            
            student_details.append({
                "student_id": str(student.student_id),
                "name": f"{student.first_name} {student.last_name}",
                "gender": student.gender.value if student.gender else None,
                "wellbeing_status": case.risk_level.value if case else "healthy",
                "recent_assessment_score": recent_score,
                "has_active_case": case is not None
            })
        
        classes_insights.append({
            "class_id": str(class_obj.class_id),
            "class_name": class_obj.name,
            "grade": class_obj.grade,
            "section": class_obj.section,
            "total_students": len(students),
            "performance_metrics": {
                "average_assessment_score": round(avg_performance, 1),
                "completed_assessments": len(assessment_ids),
                "total_responses": completed_assessments,
                "assessments_per_student": round(len(assessment_ids) / len(students), 1) if students else 0
            },
            "wellbeing_metrics": {
                "active_cases": active_cases,
                "recent_observations": len(recent_observations),
                "observation_severity": obs_severity
            },
            "students": student_details
        })
    
    return success_response({
        "teacher_id": str(teacher_id),
        "teacher_name": teacher.display_name,
        "total_classes": len(classes),
        "classes": classes_insights
    })

@router.get("/{teacher_id}/class/{class_id}/insights")
async def get_class_insights(
    teacher_id: UUID,
    class_id: UUID,
    db: Session = Depends(get_db)
):
    """Get detailed insights for a specific class"""
    # Verify teacher owns this class
    class_obj = db.query(Class).filter(
        Class.class_id == class_id,
        Class.teacher_id == teacher_id
    ).first()
    
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found or not assigned to this teacher")
    
    # Get students in this class
    students = db.query(Student).filter(Student.class_id == class_id).all()
    student_ids = [s.student_id for s in students]
    
    # Get assessment performance via StudentResponse
    from app.models.assessment import StudentResponse as SR
    student_responses = db.query(SR).filter(
        SR.student_id.in_(student_ids),
        SR.completed_at.isnot(None)
    ).all() if student_ids else []
    
    # Calculate average scores
    total_score = 0
    completed_assessments = 0
    assessment_ids = set()
    
    for response in student_responses:
        if response.score is not None:
            total_score += response.score
            completed_assessments += 1
            assessment_ids.add(response.assessment_id)
    
    avg_performance = (total_score / completed_assessments) if completed_assessments > 0 else 0
    
    # Recent observations (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_observations = db.query(Observation).filter(
        Observation.student_id.in_(student_ids),
        Observation.timestamp >= thirty_days_ago
    ).all()
    
    # Observation severity breakdown
    obs_severity = {
        "critical": len([o for o in recent_observations if o.severity == Severity.CRITICAL]),
        "high": len([o for o in recent_observations if o.severity == Severity.HIGH]),
        "medium": len([o for o in recent_observations if o.severity == Severity.MEDIUM]),
        "low": len([o for o in recent_observations if o.severity == Severity.LOW])
    }
    
    # Active cases
    active_cases = db.query(Case).filter(
        Case.student_id.in_(student_ids),
        Case.status != CaseStatus.CLOSED
    ).count()
    
    # Student list with wellbeing status
    student_details = []
    for student in students:
        # Check if student has active case
        case = db.query(Case).filter(
            Case.student_id == student.student_id,
            Case.status != CaseStatus.CLOSED
        ).first()
        
        # Get recent assessment score from StudentResponse
        recent_response = db.query(SR).filter(
            SR.student_id == student.student_id,
            SR.completed_at.isnot(None)
        ).order_by(SR.completed_at.desc()).first()
        
        recent_score = None
        if recent_response and recent_response.score is not None:
            recent_score = recent_response.score
        
        student_details.append({
            "student_id": str(student.student_id),
            "name": f"{student.first_name} {student.last_name}",
            "gender": student.gender.value if student.gender else None,
            "wellbeing_status": case.risk_level.value if case else "healthy",
            "recent_assessment_score": recent_score,
            "has_active_case": case is not None
        })
    
    return success_response({
        "class_id": str(class_id),
        "class_name": class_obj.name,
        "grade": class_obj.grade,
        "section": class_obj.section,
        "total_students": len(students),
        "performance_metrics": {
            "average_assessment_score": round(avg_performance, 1),
            "completed_assessments": len(assessment_ids),
            "total_responses": completed_assessments,
            "assessments_per_student": round(len(assessment_ids) / len(students), 1) if students else 0
        },
        "wellbeing_metrics": {
            "active_cases": active_cases,
            "recent_observations": len(recent_observations),
            "observation_severity": obs_severity
        },
        "students": student_details
    })

@router.patch("/{teacher_id}")
async def update_teacher(
    teacher_id: UUID,
    teacher_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update teacher information"""
    teacher = db.query(User).filter(
        User.user_id == teacher_id,
        User.role == UserRole.TEACHER
    ).first()
    
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    update_data = teacher_update.dict(exclude_unset=True)
    
    # Convert Pydantic models to dict for JSON storage
    if 'profile' in update_data and update_data['profile'] is not None:
        if hasattr(update_data['profile'], 'dict'):
            update_data['profile'] = update_data['profile'].dict()
    
    if 'availability' in update_data and update_data['availability'] is not None:
        if hasattr(update_data['availability'], 'dict'):
            update_data['availability'] = update_data['availability'].dict()
    
    for field, value in update_data.items():
        setattr(teacher, field, value)
    
    db.commit()
    db.refresh(teacher)
    return success_response(teacher)

@router.delete("/{teacher_id}")
async def delete_teacher(
    teacher_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a teacher"""
    teacher = db.query(User).filter(
        User.user_id == teacher_id,
        User.role == UserRole.TEACHER
    ).first()
    
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Check if teacher has assigned classes
    classes = db.query(Class).filter(Class.teacher_id == teacher_id).count()
    if classes > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete teacher. They are assigned to {classes} class(es). Please reassign classes first."
        )
    
    db.delete(teacher)
    db.commit()
    return success_response({"message": "Teacher deleted successfully", "teacher_id": str(teacher_id)})
