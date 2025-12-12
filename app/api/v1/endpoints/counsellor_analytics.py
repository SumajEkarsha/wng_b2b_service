"""
Counsellor Analytics API - Optimized Version
Uses batch queries, eager loading, and efficient aggregations.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, and_, or_, case, desc, text
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta, date
import statistics
import json

from app.core.database import get_db
from app.core.response import success_response
from app.core.logging_config import get_logger
from app.models.student import Student, RiskLevel
from app.models.school import School
from app.models.class_model import Class
from app.models.user import User
from app.models.assessment import Assessment, AssessmentTemplate, StudentResponse
from app.models.activity_assignment import ActivityAssignment
from app.models.activity_submission import ActivitySubmission, SubmissionStatus
from app.models.webinar import Webinar
from app.models.student_engagement import (
    StudentAppSession, StudentDailyStreak, 
    StudentStreakSummary, StudentWebinarAttendance
)

logger = get_logger(__name__)
router = APIRouter()


# ============== HELPER FUNCTIONS ==============

def get_date_range(days: int = 30):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def safe_mean(values: List[float]) -> Optional[float]:
    return round(statistics.mean(values), 1) if values else None


# ============== 1. SCHOOL OVERVIEW (OPTIMIZED) ==============

@router.get("/overview")
async def get_school_overview(
    school_id: UUID,
    days: int = Query(30, description="Filter to last N days"),
    db: Session = Depends(get_db)
):
    """School-wide aggregated analytics - optimized with batch queries."""
    school = db.query(School).filter(School.school_id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    start_date, end_date = get_date_range(days)
    start_datetime = datetime.combine(start_date, datetime.min.time())
    
    # Single query for student counts and risk distribution
    student_stats = db.query(
        func.count(Student.student_id).label('total'),
        func.avg(Student.wellbeing_score).label('avg_wellbeing'),
        func.sum(case((Student.risk_level == RiskLevel.LOW, 1), else_=0)).label('low_risk'),
        func.sum(case((Student.risk_level == RiskLevel.MEDIUM, 1), else_=0)).label('medium_risk'),
        func.sum(case((Student.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]), 1), else_=0)).label('high_risk')
    ).filter(Student.school_id == school_id).first()
    
    total_students = student_stats.total or 0
    
    # Class count
    total_classes = db.query(func.count(Class.class_id)).filter(Class.school_id == school_id).scalar() or 0
    
    # Get student IDs for this school (single query)
    student_ids = [s[0] for s in db.query(Student.student_id).filter(Student.school_id == school_id).all()]
    
    if not student_ids:
        return success_response({
            "school_id": school_id,
            "school_name": school.name,
            "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "days": days},
            "summary": {"total_students": 0, "total_classes": 0},
            "risk_distribution": {"low": 0, "medium": 0, "high": 0},
            "engagement": {},
            "top_performers": [],
            "at_risk_students": []
        })
    
    # Batch query for streak stats
    streak_stats = db.query(
        func.avg(StudentStreakSummary.current_streak).label('avg_streak')
    ).filter(StudentStreakSummary.student_id.in_(student_ids)).first()
    
    # Batch query for app sessions
    app_stats = db.query(
        func.count(StudentAppSession.id).label('total_sessions')
    ).filter(
        StudentAppSession.student_id.in_(student_ids),
        StudentAppSession.session_start >= start_datetime
    ).first()
    
    # Batch query for activity completion
    activity_stats = db.query(
        func.count(ActivitySubmission.submission_id).label('total'),
        func.sum(case((ActivitySubmission.status.in_([SubmissionStatus.SUBMITTED, SubmissionStatus.VERIFIED]), 1), else_=0)).label('completed')
    ).filter(ActivitySubmission.student_id.in_(student_ids)).first()
    
    # Batch query for assessment completion
    assessment_stats = db.query(
        func.count(func.distinct(StudentResponse.assessment_id)).label('completed')
    ).filter(
        StudentResponse.student_id.in_(student_ids),
        StudentResponse.completed_at.isnot(None)
    ).first()
    
    # Top performers - single optimized query
    top_performers_query = db.query(
        Student.student_id,
        Student.first_name,
        Student.last_name,
        Student.wellbeing_score,
        Student.class_id,
        StudentStreakSummary.current_streak
    ).join(
        StudentStreakSummary, Student.student_id == StudentStreakSummary.student_id
    ).filter(
        Student.school_id == school_id
    ).order_by(desc(StudentStreakSummary.current_streak)).limit(5).all()
    
    # Get class names for top performers
    class_ids = [t.class_id for t in top_performers_query if t.class_id]
    class_names = {c.class_id: c.name for c in db.query(Class.class_id, Class.name).filter(Class.class_id.in_(class_ids)).all()} if class_ids else {}
    
    top_performers = [{
        "student_id": t.student_id,
        "student_name": f"{t.first_name} {t.last_name}",
        "class_name": class_names.get(t.class_id),
        "daily_streak": t.current_streak or 0,
        "wellbeing_score": t.wellbeing_score
    } for t in top_performers_query]
    
    # At-risk students - single optimized query
    at_risk_query = db.query(
        Student.student_id,
        Student.first_name,
        Student.last_name,
        Student.wellbeing_score,
        Student.risk_level,
        Student.class_id,
        StudentStreakSummary.last_active_date
    ).outerjoin(
        StudentStreakSummary, Student.student_id == StudentStreakSummary.student_id
    ).filter(
        Student.school_id == school_id,
        Student.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
    ).limit(10).all()
    
    # Get class names for at-risk
    at_risk_class_ids = [a.class_id for a in at_risk_query if a.class_id]
    at_risk_class_names = {c.class_id: c.name for c in db.query(Class.class_id, Class.name).filter(Class.class_id.in_(at_risk_class_ids)).all()} if at_risk_class_ids else {}
    
    at_risk_students = [{
        "student_id": a.student_id,
        "student_name": f"{a.first_name} {a.last_name}",
        "class_name": at_risk_class_names.get(a.class_id),
        "wellbeing_score": a.wellbeing_score,
        "risk_level": a.risk_level.value if a.risk_level else "low",
        "last_active": a.last_active_date.isoformat() if a.last_active_date else None
    } for a in at_risk_query]
    
    # Calculate completion rates
    activity_completion = round((activity_stats.completed or 0) / (activity_stats.total or 1) * 100, 1)
    
    return success_response({
        "school_id": school_id,
        "school_name": school.name,
        "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "days": days},
        "summary": {
            "total_students": total_students,
            "total_classes": total_classes,
            "avg_wellbeing_score": round(student_stats.avg_wellbeing, 1) if student_stats.avg_wellbeing else None,
            "avg_activity_completion": activity_completion,
            "avg_daily_streak": round(streak_stats.avg_streak, 1) if streak_stats.avg_streak else 0,
            "total_app_openings": app_stats.total_sessions or 0
        },
        "risk_distribution": {
            "low": student_stats.low_risk or 0,
            "medium": student_stats.medium_risk or 0,
            "high": student_stats.high_risk or 0
        },
        "engagement": {
            "total_app_openings": app_stats.total_sessions or 0,
            "total_assessments_completed": assessment_stats.completed or 0,
            "total_activities_completed": activity_stats.completed or 0
        },
        "top_performers": top_performers,
        "at_risk_students": at_risk_students
    })



# ============== 2. CLASS LIST (OPTIMIZED) ==============

@router.get("/classes")
async def get_classes_analytics(
    school_id: UUID,
    search: Optional[str] = None,
    grade: Optional[str] = None,
    days: int = Query(30, description="Filter to last N days"),
    db: Session = Depends(get_db)
):
    """Analytics for all classes - optimized with batch queries."""
    start_date, end_date = get_date_range(days)
    
    # Base query with teacher join
    query = db.query(Class).options(
        joinedload(Class.teacher)
    ).filter(Class.school_id == school_id)
    
    if grade:
        query = query.filter(Class.grade == grade)
    if search:
        query = query.join(User, Class.teacher_id == User.user_id, isouter=True).filter(
            or_(Class.name.ilike(f"%{search}%"), User.display_name.ilike(f"%{search}%"))
        )
    
    classes = query.all()
    class_ids = [c.class_id for c in classes]
    
    if not class_ids:
        return success_response({"total_classes": 0, "classes": []})
    
    # Batch query: student counts and wellbeing by class
    student_stats = db.query(
        Student.class_id,
        func.count(Student.student_id).label('count'),
        func.avg(Student.wellbeing_score).label('avg_wellbeing'),
        func.sum(case((Student.risk_level == RiskLevel.LOW, 1), else_=0)).label('low'),
        func.sum(case((Student.risk_level == RiskLevel.MEDIUM, 1), else_=0)).label('medium'),
        func.sum(case((Student.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]), 1), else_=0)).label('high')
    ).filter(Student.class_id.in_(class_ids)).group_by(Student.class_id).all()
    
    student_stats_map = {s.class_id: s for s in student_stats}
    
    # Batch query: get all student IDs per class
    students_by_class = {}
    for row in db.query(Student.class_id, Student.student_id).filter(Student.class_id.in_(class_ids)).all():
        students_by_class.setdefault(row.class_id, []).append(row.student_id)
    
    all_student_ids = [sid for sids in students_by_class.values() for sid in sids]
    
    # Batch query: streak averages by student
    streak_map = {}
    if all_student_ids:
        for row in db.query(StudentStreakSummary.student_id, StudentStreakSummary.current_streak).filter(
            StudentStreakSummary.student_id.in_(all_student_ids)
        ).all():
            streak_map[row.student_id] = row.current_streak or 0
    
    # Batch query: activity stats by student
    activity_stats_map = {}
    if all_student_ids:
        activity_query = db.query(
            ActivitySubmission.student_id,
            func.count(ActivitySubmission.submission_id).label('total'),
            func.sum(case((ActivitySubmission.status.in_([SubmissionStatus.SUBMITTED, SubmissionStatus.VERIFIED]), 1), else_=0)).label('completed')
        ).filter(ActivitySubmission.student_id.in_(all_student_ids)).group_by(ActivitySubmission.student_id).all()
        
        for row in activity_query:
            activity_stats_map[row.student_id] = {'total': row.total, 'completed': row.completed}
    
    # Build response
    class_analytics = []
    for cls in classes:
        stats = student_stats_map.get(cls.class_id)
        class_student_ids = students_by_class.get(cls.class_id, [])
        
        # Calculate class-level metrics
        class_streaks = [streak_map.get(sid, 0) for sid in class_student_ids]
        avg_streak = safe_mean(class_streaks) or 0
        
        total_activities = sum(activity_stats_map.get(sid, {}).get('total', 0) for sid in class_student_ids)
        completed_activities = sum(activity_stats_map.get(sid, {}).get('completed', 0) for sid in class_student_ids)
        activity_completion = round(completed_activities / total_activities * 100, 1) if total_activities > 0 else 0
        
        class_analytics.append({
            "class_id": cls.class_id,
            "name": cls.name,
            "grade": cls.grade,
            "section": cls.section,
            "teacher_id": cls.teacher_id,
            "teacher_name": cls.teacher.display_name if cls.teacher else None,
            "total_students": stats.count if stats else 0,
            "metrics": {
                "avg_wellbeing": round(stats.avg_wellbeing, 1) if stats and stats.avg_wellbeing else None,
                "activity_completion": activity_completion,
                "avg_daily_streak": avg_streak
            },
            "risk_distribution": {
                "low": stats.low if stats else 0,
                "medium": stats.medium if stats else 0,
                "high": stats.high if stats else 0
            },
            "at_risk_count": stats.high if stats else 0
        })
    
    return success_response({"total_classes": len(class_analytics), "classes": class_analytics})


# ============== 3. SINGLE CLASS (OPTIMIZED) ==============

@router.get("/classes/{class_id}")
async def get_class_analytics(
    class_id: UUID,
    days: int = Query(30, description="Filter to last N days"),
    db: Session = Depends(get_db)
):
    """Detailed analytics for a specific class - optimized."""
    start_date, end_date = get_date_range(days)
    start_datetime = datetime.combine(start_date, datetime.min.time())
    
    cls = db.query(Class).options(joinedload(Class.teacher)).filter(Class.class_id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Get all students with their IDs
    students = db.query(
        Student.student_id, Student.first_name, Student.last_name,
        Student.wellbeing_score, Student.risk_level
    ).filter(Student.class_id == class_id).all()
    
    student_ids = [s.student_id for s in students]
    
    if not student_ids:
        return success_response({
            "class_id": class_id, "name": cls.name, "total_students": 0,
            "metrics": {}, "risk_distribution": {"low": 0, "medium": 0, "high": 0}, "students": []
        })
    
    # Batch queries
    streak_map = {row.student_id: row for row in db.query(
        StudentStreakSummary.student_id, StudentStreakSummary.current_streak, StudentStreakSummary.last_active_date
    ).filter(StudentStreakSummary.student_id.in_(student_ids)).all()}
    
    assessment_counts = {row.student_id: row.count for row in db.query(
        StudentResponse.student_id, func.count(func.distinct(StudentResponse.assessment_id)).label('count')
    ).filter(StudentResponse.student_id.in_(student_ids), StudentResponse.completed_at.isnot(None)
    ).group_by(StudentResponse.student_id).all()}
    
    activity_counts = {row.student_id: row.completed for row in db.query(
        ActivitySubmission.student_id,
        func.sum(case((ActivitySubmission.status.in_([SubmissionStatus.SUBMITTED, SubmissionStatus.VERIFIED]), 1), else_=0)).label('completed')
    ).filter(ActivitySubmission.student_id.in_(student_ids)).group_by(ActivitySubmission.student_id).all()}
    
    # App session stats
    app_stats = db.query(
        func.count(StudentAppSession.id).label('total'),
        func.sum(StudentAppSession.duration_minutes).label('duration')
    ).filter(StudentAppSession.student_id.in_(student_ids), StudentAppSession.session_start >= start_datetime).first()
    
    # Build student list
    student_list = []
    wellbeing_scores = []
    risk_dist = {"low": 0, "medium": 0, "high": 0}
    
    for s in students:
        streak = streak_map.get(s.student_id)
        risk = s.risk_level.value.lower() if s.risk_level else "low"
        if risk in ["high", "critical"]:
            risk_dist["high"] += 1
        elif risk == "medium":
            risk_dist["medium"] += 1
        else:
            risk_dist["low"] += 1
        
        if s.wellbeing_score:
            wellbeing_scores.append(s.wellbeing_score)
        
        student_list.append({
            "student_id": s.student_id,
            "name": f"{s.first_name} {s.last_name}",
            "wellbeing_score": s.wellbeing_score,
            "risk_level": risk,
            "daily_streak": streak.current_streak if streak else 0,
            "assessments_completed": assessment_counts.get(s.student_id, 0),
            "activities_completed": activity_counts.get(s.student_id, 0),
            "last_active": streak.last_active_date.isoformat() if streak and streak.last_active_date else None
        })
    
    avg_app = round((app_stats.total or 0) / len(students), 1) if students else 0
    avg_session = round((app_stats.duration or 0) / (app_stats.total or 1), 1)
    
    return success_response({
        "class_id": class_id,
        "name": cls.name,
        "grade": cls.grade,
        "section": cls.section,
        "teacher": {"id": cls.teacher.user_id, "name": cls.teacher.display_name, "email": cls.teacher.email} if cls.teacher else None,
        "total_students": len(students),
        "metrics": {
            "avg_wellbeing": safe_mean(wellbeing_scores),
            "avg_daily_streak": safe_mean([streak_map.get(s.student_id, type('', (), {'current_streak': 0})()).current_streak or 0 for s in students] if streak_map else [0]),
            "avg_app_openings": avg_app,
            "avg_session_time": avg_session
        },
        "risk_distribution": risk_dist,
        "students": student_list
    })



# ============== 4. STUDENT LIST (OPTIMIZED) ==============

@router.get("/students")
async def get_students_analytics(
    school_id: UUID,
    class_id: Optional[UUID] = None,
    search: Optional[str] = None,
    risk_level: Optional[str] = Query(None, description="Filter: low, medium, high"),
    days: int = Query(30, description="Filter to last N days"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Paginated student list with analytics - optimized."""
    start_date, end_date = get_date_range(days)
    start_datetime = datetime.combine(start_date, datetime.min.time())
    
    # Build base query
    query = db.query(Student).filter(Student.school_id == school_id)
    
    if class_id:
        query = query.filter(Student.class_id == class_id)
    if search:
        query = query.filter(or_(
            Student.first_name.ilike(f"%{search}%"),
            Student.last_name.ilike(f"%{search}%")
        ))
    if risk_level:
        risk_map = {"low": RiskLevel.LOW, "medium": RiskLevel.MEDIUM, "high": RiskLevel.HIGH}
        if risk_level.lower() in risk_map:
            query = query.filter(Student.risk_level == risk_map[risk_level.lower()])
    
    total_students = query.count()
    total_pages = (total_students + limit - 1) // limit
    
    students = query.offset((page - 1) * limit).limit(limit).all()
    student_ids = [s.student_id for s in students]
    
    if not student_ids:
        return success_response({"total_students": total_students, "page": page, "limit": limit, "total_pages": total_pages, "students": []})
    
    # Batch queries
    class_ids = list(set(s.class_id for s in students if s.class_id))
    class_names = {c.class_id: c.name for c in db.query(Class.class_id, Class.name).filter(Class.class_id.in_(class_ids)).all()} if class_ids else {}
    
    streak_map = {row.student_id: row for row in db.query(
        StudentStreakSummary.student_id, StudentStreakSummary.current_streak, 
        StudentStreakSummary.max_streak, StudentStreakSummary.last_active_date
    ).filter(StudentStreakSummary.student_id.in_(student_ids)).all()}
    
    assessment_counts = {row.student_id: row.count for row in db.query(
        StudentResponse.student_id, func.count(func.distinct(StudentResponse.assessment_id)).label('count')
    ).filter(StudentResponse.student_id.in_(student_ids), StudentResponse.completed_at.isnot(None)
    ).group_by(StudentResponse.student_id).all()}
    
    activity_stats = {row.student_id: (row.total, row.completed) for row in db.query(
        ActivitySubmission.student_id,
        func.count(ActivitySubmission.submission_id).label('total'),
        func.sum(case((ActivitySubmission.status.in_([SubmissionStatus.SUBMITTED, SubmissionStatus.VERIFIED]), 1), else_=0)).label('completed')
    ).filter(ActivitySubmission.student_id.in_(student_ids)).group_by(ActivitySubmission.student_id).all()}
    
    app_counts = {row.student_id: row.count for row in db.query(
        StudentAppSession.student_id, func.count(StudentAppSession.id).label('count')
    ).filter(StudentAppSession.student_id.in_(student_ids), StudentAppSession.session_start >= start_datetime
    ).group_by(StudentAppSession.student_id).all()}
    
    # Build response
    student_list = []
    for s in students:
        streak = streak_map.get(s.student_id)
        acts = activity_stats.get(s.student_id, (0, 0))
        
        student_list.append({
            "student_id": s.student_id,
            "name": f"{s.first_name} {s.last_name}",
            "class_id": s.class_id,
            "class_name": class_names.get(s.class_id),
            "wellbeing_score": s.wellbeing_score,
            "risk_level": s.risk_level.value.lower() if s.risk_level else "low",
            "daily_streak": streak.current_streak if streak else 0,
            "max_streak": streak.max_streak if streak else 0,
            "last_active": streak.last_active_date.isoformat() if streak and streak.last_active_date else None,
            "assessments_completed": assessment_counts.get(s.student_id, 0),
            "activities_completed": acts[1] or 0,
            "activities_total": acts[0] or 0,
            "app_openings": app_counts.get(s.student_id, 0)
        })
    
    return success_response({
        "total_students": total_students,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "students": student_list
    })


# ============== 5. SINGLE STUDENT (OPTIMIZED) ==============

@router.get("/students/{student_id}")
async def get_student_detailed_analytics(
    student_id: UUID,
    days: int = Query(30, description="Filter to last N days"),
    db: Session = Depends(get_db)
):
    """Comprehensive student analytics - optimized."""
    start_date, end_date = get_date_range(days)
    start_datetime = datetime.combine(start_date, datetime.min.time())
    
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    class_obj = db.query(Class).filter(Class.class_id == student.class_id).first() if student.class_id else None
    
    # Single queries for all metrics
    streak = db.query(StudentStreakSummary).filter(StudentStreakSummary.student_id == student_id).first()
    
    app_stats = db.query(
        func.count(StudentAppSession.id).label('count'),
        func.sum(StudentAppSession.duration_minutes).label('duration')
    ).filter(StudentAppSession.student_id == student_id, StudentAppSession.session_start >= start_datetime).first()
    
    assessment_count = db.query(func.count(func.distinct(StudentResponse.assessment_id))).filter(
        StudentResponse.student_id == student_id, StudentResponse.completed_at.isnot(None)
    ).scalar() or 0
    
    assessment_total = db.query(func.count(Assessment.assessment_id)).filter(
        Assessment.class_id == student.class_id
    ).scalar() if student.class_id else 0
    
    activity_stats = db.query(
        func.count(ActivitySubmission.submission_id).label('total'),
        func.sum(case((ActivitySubmission.status.in_([SubmissionStatus.SUBMITTED, SubmissionStatus.VERIFIED]), 1), else_=0)).label('completed')
    ).filter(ActivitySubmission.student_id == student_id).first()
    
    webinar_stats = db.query(
        func.count(StudentWebinarAttendance.id).label('total'),
        func.sum(case((StudentWebinarAttendance.attended == True, 1), else_=0)).label('attended')
    ).filter(StudentWebinarAttendance.student_id == student_id).first()
    
    # Streak history (last 7 days)
    streak_history = db.query(StudentDailyStreak).filter(
        StudentDailyStreak.student_id == student_id,
        StudentDailyStreak.date >= end_date - timedelta(days=7)
    ).order_by(StudentDailyStreak.date.desc()).all()
    
    weekly_data = [{
        "day": sh.date.strftime("%a"),
        "date": sh.date.isoformat(),
        "app_opened": sh.app_opened,
        "activity_completed": sh.activity_completed
    } for sh in streak_history]
    
    total_app = app_stats.count or 0
    total_duration = app_stats.duration or 0
    
    return success_response({
        "student_id": student_id,
        "name": f"{student.first_name} {student.last_name}",
        "email": student.parent_email,
        "class": {"id": class_obj.class_id, "name": class_obj.name, "grade": class_obj.grade, "section": class_obj.section} if class_obj else None,
        "profile": {
            "date_of_birth": student.dob.isoformat() if student.dob else None,
            "gender": student.gender.value.lower() if student.gender else None,
            "parent_contact": student.parent_phone
        },
        "current_metrics": {
            "wellbeing_score": student.wellbeing_score,
            "risk_level": student.risk_level.value.lower() if student.risk_level else "low",
            "daily_streak": streak.current_streak if streak else 0,
            "max_streak": streak.max_streak if streak else 0,
            "last_active": streak.last_active_date.isoformat() if streak and streak.last_active_date else None
        },
        "engagement": {
            "total_app_openings": total_app,
            "avg_session_time": round(total_duration / total_app, 1) if total_app > 0 else 0,
            "total_time_spent": total_duration,
            "assessments_completed": assessment_count,
            "assessments_total": assessment_total,
            "activities_completed": activity_stats.completed or 0,
            "activities_total": activity_stats.total or 0,
            "webinars_attended": webinar_stats.attended or 0,
            "webinars_total": webinar_stats.total or 0
        },
        "streak_history": {
            "current_streak": streak.current_streak if streak else 0,
            "max_streak": streak.max_streak if streak else 0,
            "weekly_data": weekly_data
        }
    })



# ============== 6. STUDENT ASSESSMENTS (OPTIMIZED) ==============

@router.get("/students/{student_id}/assessments")
async def get_student_assessment_history(
    student_id: UUID,
    include_responses: bool = Query(False),
    days: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Student assessment history - optimized."""
    student = db.query(Student.student_id, Student.first_name, Student.last_name).filter(
        Student.student_id == student_id
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get responses with eager loading
    query = db.query(StudentResponse).options(
        joinedload(StudentResponse.assessment).joinedload(Assessment.template)
    ).filter(StudentResponse.student_id == student_id, StudentResponse.completed_at.isnot(None))
    
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(StudentResponse.completed_at >= cutoff)
    
    responses = query.order_by(StudentResponse.completed_at.desc()).all()
    
    # Group by assessment
    assessment_map = {}
    for r in responses:
        a_id = r.assessment_id
        if a_id not in assessment_map:
            template = r.assessment.template
            assessment_map[a_id] = {
                "assessment_id": a_id,
                "template_id": template.template_id,
                "template_name": template.name,
                "category": template.category,
                "completed_at": r.completed_at,
                "total_score": 0.0,
                "max_score": len(template.questions) * 5,
                "total_questions": len(template.questions),
                "questions_answered": 0,
                "responses": [] if include_responses else None
            }
        
        assessment_map[a_id]["total_score"] += r.score or 0
        assessment_map[a_id]["questions_answered"] += 1
        
        if include_responses:
            assessment_map[a_id]["responses"].append({
                "question_id": r.question_id,
                "question_text": r.question_text,
                "answer_value": r.answer,
                "score": r.score
            })
    
    # Add risk level
    assessments = []
    for a in assessment_map.values():
        ratio = a["total_score"] / a["max_score"] if a["max_score"] > 0 else 0
        a["risk_level"] = "low" if ratio < 0.33 else ("medium" if ratio < 0.66 else "high")
        assessments.append(a)
    
    return success_response({
        "student_id": student_id,
        "student_name": f"{student.first_name} {student.last_name}",
        "total_assessments": len(assessments),
        "assessments": assessments
    })


# ============== 7. STUDENT ACTIVITIES (OPTIMIZED) ==============

@router.get("/students/{student_id}/activities")
async def get_student_activity_history(
    student_id: UUID,
    status: Optional[str] = None,
    days: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Student activity history - optimized."""
    student = db.query(Student.student_id, Student.first_name, Student.last_name).filter(
        Student.student_id == student_id
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Status breakdown (always get full stats)
    status_stats = db.query(
        ActivitySubmission.status,
        func.count(ActivitySubmission.submission_id).label('count')
    ).filter(ActivitySubmission.student_id == student_id).group_by(ActivitySubmission.status).all()
    
    status_breakdown = {"pending": 0, "submitted": 0, "verified": 0, "rejected": 0}
    for row in status_stats:
        status_breakdown[row.status.value.lower()] = row.count
    
    # Filtered query
    query = db.query(ActivitySubmission).options(
        joinedload(ActivitySubmission.assignment).joinedload(ActivityAssignment.activity)
    ).filter(ActivitySubmission.student_id == student_id)
    
    if status:
        try:
            query = query.filter(ActivitySubmission.status == SubmissionStatus(status.upper()))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    if days:
        query = query.filter(ActivitySubmission.created_at >= datetime.utcnow() - timedelta(days=days))
    
    submissions = query.order_by(ActivitySubmission.created_at.desc()).all()
    
    activities = [{
        "submission_id": sub.submission_id,
        "activity_id": sub.assignment.activity.activity_id if sub.assignment and sub.assignment.activity else None,
        "activity_title": sub.assignment.activity.title if sub.assignment and sub.assignment.activity else None,
        "activity_type": sub.assignment.activity.type.value if sub.assignment and sub.assignment.activity and sub.assignment.activity.type else None,
        "assigned_at": sub.assignment.created_at if sub.assignment else None,
        "due_date": sub.assignment.due_date if sub.assignment else None,
        "submitted_at": sub.submitted_at,
        "status": sub.status.value,
        "feedback": sub.feedback,
        "file_url": sub.file_url
    } for sub in submissions]
    
    return success_response({
        "student_id": student_id,
        "student_name": f"{student.first_name} {student.last_name}",
        "total_activities": sum(status_breakdown.values()),
        "status_breakdown": status_breakdown,
        "activities": activities
    })


# ============== 8. STUDENT WEBINARS (OPTIMIZED) ==============

@router.get("/students/{student_id}/webinars")
async def get_student_webinar_history(
    student_id: UUID,
    attended: Optional[bool] = None,
    days: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Student webinar history - optimized."""
    student = db.query(Student.student_id, Student.first_name, Student.last_name).filter(
        Student.student_id == student_id
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Stats
    stats = db.query(
        func.count(StudentWebinarAttendance.id).label('total'),
        func.sum(case((StudentWebinarAttendance.attended == True, 1), else_=0)).label('attended')
    ).filter(StudentWebinarAttendance.student_id == student_id).first()
    
    total = stats.total or 0
    attended_count = stats.attended or 0
    
    # Filtered query
    query = db.query(StudentWebinarAttendance).options(
        joinedload(StudentWebinarAttendance.webinar)
    ).filter(StudentWebinarAttendance.student_id == student_id)
    
    if attended is not None:
        query = query.filter(StudentWebinarAttendance.attended == attended)
    if days:
        query = query.filter(StudentWebinarAttendance.created_at >= datetime.utcnow() - timedelta(days=days))
    
    attendances = query.all()
    
    webinars = [{
        "webinar_id": att.webinar.webinar_id if att.webinar else None,
        "title": att.webinar.title if att.webinar else None,
        "description": att.webinar.description if att.webinar else None,
        "scheduled_at": att.webinar.date if att.webinar else None,
        "duration_minutes": att.webinar.duration_minutes if att.webinar else None,
        "host": {"name": att.webinar.speaker_name} if att.webinar else None,
        "attended": att.attended,
        "join_time": att.join_time,
        "leave_time": att.leave_time,
        "watch_duration_minutes": att.watch_duration_minutes,
        "recording_url": att.webinar.video_url if att.webinar else None
    } for att in attendances]
    
    return success_response({
        "student_id": student_id,
        "student_name": f"{student.first_name} {student.last_name}",
        "total_webinars": total,
        "attended_count": attended_count,
        "missed_count": total - attended_count,
        "attendance_rate": round(attended_count / total * 100, 1) if total > 0 else 0,
        "webinars": webinars
    })


# ============== 9. STUDENT STREAK (OPTIMIZED) ==============

@router.get("/students/{student_id}/streak")
async def get_student_streak_details(
    student_id: UUID,
    days: int = Query(30),
    db: Session = Depends(get_db)
):
    """Student streak details - optimized."""
    student = db.query(Student.student_id, Student.first_name, Student.last_name).filter(
        Student.student_id == student_id
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    streak_summary = db.query(StudentStreakSummary).filter(
        StudentStreakSummary.student_id == student_id
    ).first()
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Get daily streaks with session durations in one query
    daily_data = db.query(
        StudentDailyStreak.date,
        StudentDailyStreak.app_opened,
        StudentDailyStreak.app_open_time,
        StudentDailyStreak.activity_completed,
        StudentDailyStreak.activities_count,
        StudentDailyStreak.streak_maintained,
        func.coalesce(func.sum(StudentAppSession.duration_minutes), 0).label('session_duration')
    ).outerjoin(
        StudentAppSession,
        and_(
            StudentAppSession.student_id == student_id,
            func.date(StudentAppSession.session_start) == StudentDailyStreak.date
        )
    ).filter(
        StudentDailyStreak.student_id == student_id,
        StudentDailyStreak.date >= start_date,
        StudentDailyStreak.date <= end_date
    ).group_by(
        StudentDailyStreak.id
    ).order_by(StudentDailyStreak.date.desc()).all()
    
    daily_history = [{
        "date": d.date.isoformat(),
        "day_of_week": d.date.strftime("%A"),
        "app_opened": d.app_opened,
        "app_open_time": d.app_open_time.isoformat() if d.app_open_time else None,
        "activity_completed": d.activity_completed,
        "activities_count": d.activities_count,
        "session_duration_minutes": d.session_duration or 0,
        "streak_maintained": d.streak_maintained
    } for d in daily_data]
    
    # Weekly summary
    weekly_summary = []
    for i in range(4):
        week_start = end_date - timedelta(days=end_date.weekday()) - timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        
        week_data = [d for d in daily_data if week_start <= d.date <= week_end]
        days_active = len([d for d in week_data if d.app_opened])
        activities = sum(d.activities_count for d in week_data)
        total_time = sum(d.session_duration or 0 for d in week_data)
        
        weekly_summary.append({
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "days_active": days_active,
            "activities_completed": activities,
            "avg_session_time": round(total_time / days_active, 1) if days_active > 0 else 0
        })
    
    return success_response({
        "student_id": student_id,
        "student_name": f"{student.first_name} {student.last_name}",
        "current_streak": streak_summary.current_streak if streak_summary else 0,
        "max_streak": streak_summary.max_streak if streak_summary else 0,
        "total_active_days": streak_summary.total_active_days if streak_summary else 0,
        "streak_start_date": streak_summary.streak_start_date.isoformat() if streak_summary and streak_summary.streak_start_date else None,
        "daily_history": daily_history,
        "weekly_summary": weekly_summary
    })
