from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.class_model import Class
from app.models.school import School
from app.models.student import Student
from app.models.case import Case, CaseStatus, RiskLevel
from app.models.observation import Observation, Severity
from app.models.assessment import Assessment
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
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
    return teacher

@router.get("/", response_model=List[UserResponse])
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
    return teachers

@router.get("/{teacher_id}", response_model=UserResponse)
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
    return teacher

@router.get("/{teacher_id}/classes", response_model=List[dict])
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
    
    return [
        {
            "class_id": str(c.class_id),
            "name": c.name,
            "grade": c.grade,
            "section": c.section,
            "capacity": c.capacity,
            "academic_year": c.academic_year
        }
        for c in classes
    ]

@router.get("/{teacher_id}/students", response_model=List[dict])
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
    
    return students

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
    students = db.query(Student).filter(Student.class_id.in_(class_ids)).all()
    student_ids = [s.student_id for s in students]
    
    # Total counts
    total_students = len(students)
    total_classes = len(classes)
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_observations = db.query(Observation).filter(
        Observation.student_id.in_(student_ids),
        Observation.timestamp >= thirty_days_ago
    ).count()
    
    recent_assessments = db.query(Assessment).filter(
        Assessment.student_id.in_(student_ids),
        Assessment.completed_at >= thirty_days_ago
    ).count()
    
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
    
    return {
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
        "recent_activity_30_days": {
            "observations": recent_observations,
            "assessments_completed": recent_assessments
        }
    }

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
        
        # Get assessment performance
        assessments = db.query(Assessment).filter(
            Assessment.student_id.in_(student_ids)
        ).all()
        
        total_score = 0
        completed_assessments = 0
        for assessment in assessments:
            if assessment.scores and assessment.completed_at:
                if isinstance(assessment.scores, dict) and 'overall' in assessment.scores:
                    total_score += assessment.scores['overall']
                    completed_assessments += 1
        
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
            
            recent_assessment = db.query(Assessment).filter(
                Assessment.student_id == student.student_id
            ).order_by(Assessment.completed_at.desc()).first()
            
            recent_score = None
            if recent_assessment and recent_assessment.scores:
                if isinstance(recent_assessment.scores, dict) and 'overall' in recent_assessment.scores:
                    recent_score = recent_assessment.scores['overall']
            
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
                "completed_assessments": completed_assessments,
                "assessments_per_student": round(completed_assessments / len(students), 1) if students else 0
            },
            "wellbeing_metrics": {
                "active_cases": active_cases,
                "recent_observations": len(recent_observations),
                "observation_severity": obs_severity
            },
            "students": student_details
        })
    
    return {
        "teacher_id": str(teacher_id),
        "teacher_name": teacher.display_name,
        "total_classes": len(classes),
        "classes": classes_insights
    }

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
    
    # Get assessment performance
    assessments = db.query(Assessment).filter(
        Assessment.student_id.in_(student_ids)
    ).all()
    
    # Calculate average scores
    total_score = 0
    completed_assessments = 0
    for assessment in assessments:
        if assessment.scores and assessment.completed_at:
            # Assuming scores is a dict with overall score
            if isinstance(assessment.scores, dict) and 'overall' in assessment.scores:
                total_score += assessment.scores['overall']
                completed_assessments += 1
    
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
        
        # Get recent assessment score
        recent_assessment = db.query(Assessment).filter(
            Assessment.student_id == student.student_id
        ).order_by(Assessment.completed_at.desc()).first()
        
        recent_score = None
        if recent_assessment and recent_assessment.scores:
            if isinstance(recent_assessment.scores, dict) and 'overall' in recent_assessment.scores:
                recent_score = recent_assessment.scores['overall']
        
        student_details.append({
            "student_id": str(student.student_id),
            "name": f"{student.first_name} {student.last_name}",
            "gender": student.gender.value if student.gender else None,
            "wellbeing_status": case.risk_level.value if case else "healthy",
            "recent_assessment_score": recent_score,
            "has_active_case": case is not None
        })
    
    return {
        "class_id": str(class_id),
        "class_name": class_obj.name,
        "grade": class_obj.grade,
        "section": class_obj.section,
        "total_students": len(students),
        "performance_metrics": {
            "average_assessment_score": round(avg_performance, 1),
            "completed_assessments": completed_assessments,
            "assessments_per_student": round(completed_assessments / len(students), 1) if students else 0
        },
        "wellbeing_metrics": {
            "active_cases": active_cases,
            "recent_observations": len(recent_observations),
            "observation_severity": obs_severity
        },
        "students": student_details
    }

@router.patch("/{teacher_id}", response_model=UserResponse)
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
    return teacher

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
    return {"success": True, "message": "Teacher deleted successfully", "teacher_id": str(teacher_id)}
