#!/usr/bin/env python3
"""
Comprehensive seed script for mental health platform with 4 schools
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models import *
from app.models.assessment import AssessmentTemplate, StudentResponse
from app.models.case import CaseStatus, RiskLevel, JournalEntry, EntryVisibility, EntryType
from app.models.user import UserRole
from app.models.student import Gender, RiskLevel as StudentRiskLevel, ConsentStatus as StudentConsentStatus
from app.models.observation import Severity
from app.models.resource import ResourceType, ResourceStatus
from app.models.activity import ActivityType
from app.models.risk_alert import AlertLevel, AlertType, AlertStatus
from app.models.ai_recommendation import RecommendationType, ConfidenceLevel
from app.models.consent_record import ConsentType, ConsentStatus
from app.models.goal import GoalStatus
from app.models.daily_booster import BoosterType, DifficultyLevel
from app.models.calendar_event import EventType, EventStatus
from app.models.session_note import SessionType
from datetime import datetime, date, timedelta
import random

def seed_database():
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("SEEDING DATABASE - MENTAL HEALTH PLATFORM")
        print("="*60 + "\n")
        
        # ============ SCHOOLS ============
        print("Creating schools...")
        schools_data = [
            {
                "name": "Greenwood High School",
                "address": "123 Education Lane",
                "city": "Springfield",
                "state": "Illinois",
                "country": "USA",
                "phone": "+1-555-0100",
                "email": "admin@greenwood.edu",
                "website": "https://greenwood.edu",
                "timezone": "America/Chicago"
            },
            {
                "name": "Riverside Academy",
                "address": "456 River Road",
                "city": "Portland",
                "state": "Oregon",
                "country": "USA",
                "phone": "+1-555-0200",
                "email": "info@riverside.edu",
                "website": "https://riverside.edu",
                "timezone": "America/Los_Angeles"
            },
            {
                "name": "Oakmont International School",
                "address": "789 Oak Street",
                "city": "Boston",
                "state": "Massachusetts",
                "country": "USA",
                "phone": "+1-555-0300",
                "email": "contact@oakmont.edu",
                "website": "https://oakmont.edu",
                "timezone": "America/New_York"
            },
            {
                "name": "Sunnydale Middle School",
                "address": "321 Sunny Avenue",
                "city": "San Diego",
                "state": "California",
                "country": "USA",
                "phone": "+1-555-0400",
                "email": "hello@sunnydale.edu",
                "website": "https://sunnydale.edu",
                "timezone": "America/Los_Angeles"
            }
        ]
        
        schools = []
        for school_data in schools_data:
            school = School(
                **school_data,
                academic_year="2024-2025",
                settings={"enable_ai": True, "parent_portal": True}
            )
            schools.append(school)
        
        db.add_all(schools)
        db.flush()
        print(f"✅ Created {len(schools)} schools")
        
        # ============ USERS ============
        print("Creating users...")
        users = []
        
        # School 1 - Greenwood High School
        users.extend([
            User(school_id=schools[0].school_id, role=UserRole.PRINCIPAL, email="principal@greenwood.edu",
                 hashed_password=get_password_hash("password123"), display_name="Dr. Margaret Thompson",
                 phone="+1-555-0101"),
            User(school_id=schools[0].school_id, role=UserRole.COUNSELLOR, email="counsellor1@greenwood.edu",
                 hashed_password=get_password_hash("password123"), display_name="Dr. Sarah Johnson",
                 phone="+1-555-0102", profile={"specializations": ["Anxiety", "Depression"]}),
            User(school_id=schools[0].school_id, role=UserRole.COUNSELLOR, email="counsellor2@greenwood.edu",
                 hashed_password=get_password_hash("password123"), display_name="Mr. David Chen",
                 phone="+1-555-0103"),
            User(school_id=schools[0].school_id, role=UserRole.TEACHER, email="teacher1@greenwood.edu",
                 hashed_password=get_password_hash("password123"), display_name="Ms. Emily Rodriguez",
                 phone="+1-555-0104"),
            User(school_id=schools[0].school_id, role=UserRole.TEACHER, email="teacher2@greenwood.edu",
                 hashed_password=get_password_hash("password123"), display_name="Mr. James Wilson",
                 phone="+1-555-0105"),
        ])
        
        # School 2 - Riverside Academy
        users.extend([
            User(school_id=schools[1].school_id, role=UserRole.PRINCIPAL, email="principal@riverside.edu",
                 hashed_password=get_password_hash("password123"), display_name="Mr. Robert Martinez",
                 phone="+1-555-0201"),
            User(school_id=schools[1].school_id, role=UserRole.COUNSELLOR, email="counsellor@riverside.edu",
                 hashed_password=get_password_hash("password123"), display_name="Dr. Amanda Foster",
                 phone="+1-555-0202"),
            User(school_id=schools[1].school_id, role=UserRole.TEACHER, email="teacher@riverside.edu",
                 hashed_password=get_password_hash("password123"), display_name="Ms. Jennifer Lee",
                 phone="+1-555-0203"),
        ])
        
        # School 3 - Oakmont International
        users.extend([
            User(school_id=schools[2].school_id, role=UserRole.PRINCIPAL, email="principal@oakmont.edu",
                 hashed_password=get_password_hash("password123"), display_name="Dr. Patricia Williams",
                 phone="+1-555-0301"),
            User(school_id=schools[2].school_id, role=UserRole.COUNSELLOR, email="counsellor@oakmont.edu",
                 hashed_password=get_password_hash("password123"), display_name="Ms. Rachel Green",
                 phone="+1-555-0302"),
            User(school_id=schools[2].school_id, role=UserRole.TEACHER, email="teacher@oakmont.edu",
                 hashed_password=get_password_hash("password123"), display_name="Mr. Michael Brown",
                 phone="+1-555-0303"),
        ])
        
        # School 4 - Sunnydale Middle School
        users.extend([
            User(school_id=schools[3].school_id, role=UserRole.PRINCIPAL, email="principal@sunnydale.edu",
                 hashed_password=get_password_hash("password123"), display_name="Ms. Linda Garcia",
                 phone="+1-555-0401"),
            User(school_id=schools[3].school_id, role=UserRole.COUNSELLOR, email="counsellor@sunnydale.edu",
                 hashed_password=get_password_hash("password123"), display_name="Mr. Thomas Anderson",
                 phone="+1-555-0402"),
            User(school_id=schools[3].school_id, role=UserRole.TEACHER, email="teacher@sunnydale.edu",
                 hashed_password=get_password_hash("password123"), display_name="Mrs. Susan Miller",
                 phone="+1-555-0403"),
        ])
        
        db.add_all(users)
        db.flush()
        print(f"✅ Created {len(users)} users")
        
        # Get counsellors and teachers for each school
        counsellors = {i: [u for u in users if u.school_id == schools[i].school_id and u.role == UserRole.COUNSELLOR] 
                      for i in range(4)}
        teachers = {i: [u for u in users if u.school_id == schools[i].school_id and u.role == UserRole.TEACHER] 
                   for i in range(4)}
        
        # ============ CLASSES ============
        print("Creating classes...")
        classes = []
        
        # School 1 classes
        for grade, section in [("5", "A"), ("5", "B"), ("8", "A"), ("10", "A"), ("12", "A")]:
            classes.append(Class(
                school_id=schools[0].school_id,
                name=f"Grade {grade}-{section}",
                grade=grade,
                section=section,
                academic_year="2024-2025",
                teacher_id=random.choice(teachers[0]).user_id if teachers[0] else None,
                capacity=30
            ))
        
        # School 2 classes
        for grade, section in [("6", "A"), ("7", "A"), ("9", "A")]:
            classes.append(Class(
                school_id=schools[1].school_id,
                name=f"Grade {grade}-{section}",
                grade=grade,
                section=section,
                academic_year="2024-2025",
                teacher_id=teachers[1][0].user_id if teachers[1] else None,
                capacity=28
            ))
        
        # School 3 classes
        for grade, section in [("7", "A"), ("8", "A"), ("11", "A")]:
            classes.append(Class(
                school_id=schools[2].school_id,
                name=f"Grade {grade}-{section}",
                grade=grade,
                section=section,
                academic_year="2024-2025",
                teacher_id=teachers[2][0].user_id if teachers[2] else None,
                capacity=25
            ))
        
        # School 4 classes
        for grade, section in [("6", "A"), ("7", "A"), ("8", "A")]:
            classes.append(Class(
                school_id=schools[3].school_id,
                name=f"Grade {grade}-{section}",
                grade=grade,
                section=section,
                academic_year="2024-2025",
                teacher_id=teachers[3][0].user_id if teachers[3] else None,
                capacity=30
            ))
        
        db.add_all(classes)
        db.flush()
        print(f"✅ Created {len(classes)} classes")
        
        # ============ STUDENTS ============
        print("Creating students...")
        first_names = ["Alex", "Emma", "Noah", "Olivia", "Liam", "Sophia", "Ethan", "Ava", "Mason", "Isabella",
                      "James", "Mia", "Benjamin", "Charlotte", "Lucas", "Amelia", "Henry", "Harper", "Jack", "Evelyn"]
        last_names = ["Williams", "Brown", "Davis", "Miller", "Garcia", "Martinez", "Lopez", "Gonzalez", "Wilson",
                     "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "White", "Harris", "Martin", "Thompson"]
        
        students = []
        for i, cls in enumerate(classes):
            # 5-8 students per class
            num_students = random.randint(5, 8)
            for j in range(num_students):
                birth_year = 2024 - int(cls.grade) - 5
                student = Student(
                    school_id=cls.school_id,
                    first_name=random.choice(first_names),
                    last_name=random.choice(last_names),
                    roll_number=f"2024{i:02d}{j:02d}",
                    grade=cls.grade,
                    dob=date(birth_year, random.randint(1, 12), random.randint(1, 28)),
                    gender=random.choice([Gender.MALE, Gender.FEMALE]),
                    class_id=cls.class_id,
                    parent_email=f"parent{i}{j}@email.com",
                    parent_phone=f"+1-555-{1000+i*10+j}",
                    risk_level=random.choice([StudentRiskLevel.LOW, StudentRiskLevel.LOW, StudentRiskLevel.MEDIUM, StudentRiskLevel.HIGH]),
                    wellbeing_score=random.randint(60, 95),
                    last_assessment=date.today() - timedelta(days=random.randint(1, 30)),
                    consent_status=random.choice([StudentConsentStatus.GRANTED, StudentConsentStatus.GRANTED, StudentConsentStatus.PENDING])
                )
                students.append(student)
        
        db.add_all(students)
        db.flush()
        print(f"✅ Created {len(students)} students")
        
        # ============ CASES ============
        print("Creating cases...")
        high_risk_students = [s for s in students if s.risk_level in [StudentRiskLevel.HIGH, StudentRiskLevel.MEDIUM]][:10]
        cases = []
        
        for student in high_risk_students:
            school_counsellors = counsellors[schools.index(next(s for s in schools if s.school_id == student.school_id))]
            if school_counsellors:
                case = Case(
                    student_id=student.student_id,
                    created_by=school_counsellors[0].user_id,
                    status=random.choice([CaseStatus.INTAKE, CaseStatus.ASSESSMENT, CaseStatus.INTERVENTION, CaseStatus.MONITORING]),
                    risk_level=RiskLevel.HIGH if student.risk_level == StudentRiskLevel.HIGH else RiskLevel.MEDIUM,
                    assigned_counsellor=school_counsellors[0].user_id,
                    tags=random.sample(["anxiety", "depression", "social-skills", "trauma", "behavioral"], k=2),
                    ai_summary=f"Case for {student.first_name} {student.last_name} - monitoring progress"
                )
                cases.append(case)
        
        db.add_all(cases)
        db.flush()
        print(f"✅ Created {len(cases)} cases")
        
        # ============ SESSION NOTES ============
        print("Creating session notes...")
        session_notes = []
        for case in cases[:5]:
            school_counsellors = counsellors[schools.index(next(s for s in schools if s.school_id == 
                                            next(st for st in students if st.student_id == case.student_id).school_id))]
            if school_counsellors:
                session_notes.append(SessionNote(
                    case_id=case.case_id,
                    counsellor_id=school_counsellors[0].user_id,
                    date=datetime.utcnow() - timedelta(days=random.randint(1, 14)),
                    duration=45,
                    type=SessionType.INDIVIDUAL,
                    summary="Student showing progress in managing anxiety symptoms",
                    interventions=["CBT techniques", "Breathing exercises"],
                    next_steps=["Continue weekly sessions", "Practice coping strategies"]
                ))
        
        db.add_all(session_notes)
        db.flush()
        print(f"✅ Created {len(session_notes)} session notes")
        
        # ============ GOALS ============
        print("Creating goals...")
        goals = []
        for case in cases[:5]:
            goals.extend([
                Goal(
                    case_id=case.case_id,
                    title="Reduce anxiety symptoms",
                    description="Work on managing anxiety through CBT techniques",
                    target_date=datetime.utcnow() + timedelta(days=90),
                    status=GoalStatus.IN_PROGRESS,
                    progress=random.randint(20, 60)
                ),
                Goal(
                    case_id=case.case_id,
                    title="Improve social interactions",
                    description="Build confidence in peer relationships",
                    target_date=datetime.utcnow() + timedelta(days=60),
                    status=GoalStatus.IN_PROGRESS,
                    progress=random.randint(30, 70)
                )
            ])
        
        db.add_all(goals)
        db.flush()
        print(f"✅ Created {len(goals)} goals")
        
        # ============ AI RECOMMENDATIONS ============
        print("Creating AI recommendations...")
        ai_recommendations = []
        for case in cases[:3]:
            ai_recommendations.append(AIRecommendation(
                type=RecommendationType.INTERVENTION,
                confidence=ConfidenceLevel.HIGH,
                rationale="Pattern analysis shows consistent anxiety indicators",
                recommendation="Consider implementing CBT techniques within the next week",
                model_version="MindBridge-v2.3",
                related_student_id=case.student_id,
                related_case_id=case.case_id,
                is_reviewed=random.choice([True, False])
            ))
        
        db.add_all(ai_recommendations)
        db.flush()
        print(f"✅ Created {len(ai_recommendations)} AI recommendations")
        
        # ============ RISK ALERTS ============
        print("Creating risk alerts...")
        risk_alerts = []
        high_risk_cases = [c for c in cases if c.risk_level == RiskLevel.HIGH][:3]
        for case in high_risk_cases:
            school_counsellors = counsellors[schools.index(next(s for s in schools if s.school_id == 
                                            next(st for st in students if st.student_id == case.student_id).school_id))]
            if school_counsellors:
                risk_alerts.append(RiskAlert(
                    student_id=case.student_id,
                    level=AlertLevel.HIGH,
                    type=random.choice([AlertType.EMOTIONAL, AlertType.BEHAVIORAL]),
                    description="Student showing signs of severe distress",
                    triggers=["Academic pressure", "Social isolation"],
                    recommendations=["Immediate counseling", "Parent consultation"],
                    assigned_to=school_counsellors[0].user_id,
                    status=AlertStatus.IN_REVIEW
                ))
        
        db.add_all(risk_alerts)
        db.flush()
        print(f"✅ Created {len(risk_alerts)} risk alerts")
        
        # ============ CONSENT RECORDS ============
        print("Creating consent records...")
        consent_records = []
        for student in students[:20]:
            consent_records.append(ConsentRecord(
                student_id=student.student_id,
                parent_name=f"Parent of {student.first_name}",
                consent_type=ConsentType.ASSESSMENT,
                status=ConsentStatus.GRANTED if student.consent_status == StudentConsentStatus.GRANTED else ConsentStatus.PENDING,
                granted_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)) if student.consent_status == StudentConsentStatus.GRANTED else None,
                expires_at=datetime.utcnow() + timedelta(days=180) if student.consent_status == StudentConsentStatus.GRANTED else None,
                documents=["consent-form.pdf"]
            ))
        
        db.add_all(consent_records)
        db.flush()
        print(f"✅ Created {len(consent_records)} consent records")
        
        # ============ ACTIVITIES ============
        print("Creating activities...")
        activities_data = [
            {"title": "Mindful Breathing Circle", "type": ActivityType.MINDFULNESS, "duration": 20,
             "description": "Calming group activity focusing on deep breathing",
             "target_grades": ["6", "7", "8"], "materials": ["Comfortable seating", "Timer"],
             "instructions": ["Form a circle", "Guide breathing", "Share experiences"],
             "objectives": ["Reduce stress", "Improve emotional regulation"]},
            {"title": "Emotion Check-In Wheel", "type": ActivityType.EMOTIONAL_REGULATION, "duration": 15,
             "description": "Interactive activity to identify emotions",
             "target_grades": ["5", "6", "7"], "materials": ["Emotion wheel printouts", "Colored pencils"],
             "instructions": ["Distribute materials", "Identify emotions", "Group discussion"],
             "objectives": ["Increase emotional awareness", "Improve vocabulary"]},
            {"title": "Team Building Challenge", "type": ActivityType.TEAM_BUILDING, "duration": 30,
             "description": "Cooperative games requiring teamwork",
             "target_grades": ["7", "8", "9"], "materials": ["Props", "Challenge cards"],
             "instructions": ["Explain challenge", "Form teams", "Debrief"],
             "objectives": ["Build cooperation", "Improve communication"]},
        ]
        
        activities = []
        for school in schools[:2]:
            school_counsellors = counsellors[schools.index(school)]
            if school_counsellors:
                for activity_data in activities_data:
                    activities.append(Activity(
                        school_id=school.school_id,
                        created_by=school_counsellors[0].user_id,
                        **activity_data
                    ))
        
        db.add_all(activities)
        db.flush()
        print(f"✅ Created {len(activities)} activities")
        
        # ============ DAILY BOOSTERS ============
        print("Creating daily boosters...")
        boosters_data = [
            {"title": "The Gratitude Chain", "type": BoosterType.STORY, "duration": 7,
             "description": "Inspiring story about gratitude", "purpose": "Build positive mindset",
             "target_grades": ["5", "6", "7", "8"], "difficulty": DifficultyLevel.EASY,
             "full_instructions": "Read story about gratitude, discuss, share one thing grateful for today"},
            {"title": "Brain Teaser Warm-Up", "type": BoosterType.PUZZLE, "duration": 7,
             "description": "Collaborative riddles and puzzles", "purpose": "Activate critical thinking",
             "target_grades": ["6", "7", "8", "9"], "difficulty": DifficultyLevel.MEDIUM,
             "full_instructions": "Present riddles, allow discussion, celebrate creative thinking"},
            {"title": "Energizer Stretch", "type": BoosterType.MOVEMENT, "duration": 5,
             "description": "Guided stretching sequence", "purpose": "Reduce restlessness",
             "target_grades": ["5", "6", "7", "8"], "difficulty": DifficultyLevel.EASY,
             "full_instructions": "Lead stretching: reach high, side bends, shoulder rolls, deep breathing",
             "materials": ["Clear space"]},
        ]
        
        daily_boosters = []
        for school in schools:
            school_counsellors = counsellors[schools.index(school)]
            if school_counsellors:
                for booster_data in boosters_data:
                    daily_boosters.append(DailyBooster(
                        school_id=school.school_id,
                        created_by=school_counsellors[0].user_id,
                        **booster_data
                    ))
        
        db.add_all(daily_boosters)
        db.flush()
        print(f"✅ Created {len(daily_boosters)} daily boosters")
        
        # ============ CALENDAR EVENTS ============
        print("Creating calendar events...")
        calendar_events = []
        for case in cases[:5]:
            school_counsellors = counsellors[schools.index(next(s for s in schools if s.school_id == 
                                            next(st for st in students if st.student_id == case.student_id).school_id))]
            if school_counsellors:
                event_date = datetime.utcnow() + timedelta(days=random.randint(1, 14))
                calendar_events.append(CalendarEvent(
                    school_id=next(st for st in students if st.student_id == case.student_id).school_id,
                    title=f"Counseling Session - {next(st for st in students if st.student_id == case.student_id).first_name}",
                    description="Weekly individual counseling session",
                    type=EventType.SESSION,
                    start_time=event_date.replace(hour=10, minute=0),
                    end_time=event_date.replace(hour=10, minute=45),
                    location="Counseling Office",
                    attendees=[school_counsellors[0].user_id],
                    status=EventStatus.SCHEDULED,
                    related_case_id=case.case_id,
                    related_student_id=case.student_id,
                    created_by=school_counsellors[0].user_id
                ))
        
        db.add_all(calendar_events)
        db.flush()
        print(f"✅ Created {len(calendar_events)} calendar events")
        
        # ============ OBSERVATIONS ============
        print("Creating observations...")
        observations = []
        for student in students[:15]:
            school_teachers = teachers[schools.index(next(s for s in schools if s.school_id == student.school_id))]
            if school_teachers:
                observations.append(Observation(
                    student_id=student.student_id,
                    reported_by=school_teachers[0].user_id,
                    severity=random.choice([Severity.LOW, Severity.MEDIUM, Severity.HIGH]),
                    category=random.choice(["behavioral", "social", "emotional", "academic"]),
                    content=f"Observation for {student.first_name}: showing signs of {random.choice(['withdrawal', 'anxiety', 'stress', 'difficulty concentrating'])}",
                    ai_summary="AI-generated summary of observation"
                ))
        
        db.add_all(observations)
        db.flush()
        print(f"✅ Created {len(observations)} observations")
        
        # ============ RESOURCES ============
        print("Creating resources...")
        resources_data = [
            {"type": ResourceType.VIDEO, "title": "Understanding Anxiety in Teens",
             "description": "Comprehensive guide to recognizing anxiety",
             "video_url": "https://example.com/videos/anxiety.mp4",
             "author_name": "Dr. Emily Chen", "duration_seconds": 1200,
             "tags": ["anxiety", "teens"], "category": "anxiety"},
            {"type": ResourceType.VIDEO, "title": "Mindfulness Exercises",
             "description": "Simple mindfulness techniques",
             "video_url": "https://example.com/videos/mindfulness.mp4",
             "author_name": "Sarah Johnson", "duration_seconds": 600,
             "tags": ["mindfulness", "meditation"], "category": "stress-management"},
            {"type": ResourceType.ARTICLE, "title": "Supporting Students in Crisis",
             "description": "Practical strategies for immediate support",
             "article_url": "https://example.com/articles/crisis",
             "author_name": "Dr. Amanda Foster",
             "tags": ["crisis", "support"], "category": "crisis-intervention"},
        ]
        
        resources = []
        for resource_data in resources_data:
            resources.append(Resource(
                school_id=None,
                status=ResourceStatus.PUBLISHED,
                posted_date=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
                view_count=random.randint(50, 500),
                target_audience=["counsellors", "teachers"],
                **resource_data
            ))
        
        db.add_all(resources)
        db.flush()
        print(f"✅ Created {len(resources)} resources")
        
        db.commit()
        
        print("\n" + "="*60)
        print("DATABASE SEEDED SUCCESSFULLY!")
        print("="*60)
        print(f"✅ {len(schools)} schools")
        print(f"✅ {len(users)} users")
        print(f"✅ {len(classes)} classes")
        print(f"✅ {len(students)} students")
        print(f"✅ {len(cases)} cases")
        print(f"✅ {len(session_notes)} session notes")
        print(f"✅ {len(goals)} goals")
        print(f"✅ {len(ai_recommendations)} AI recommendations")
        print(f"✅ {len(risk_alerts)} risk alerts")
        print(f"✅ {len(consent_records)} consent records")
        print(f"✅ {len(activities)} activities")
        print(f"✅ {len(daily_boosters)} daily boosters")
        print(f"✅ {len(calendar_events)} calendar events")
        print(f"✅ {len(observations)} observations")
        print(f"✅ {len(resources)} resources")
        print("\n" + "="*60)
        print("SAMPLE LOGIN CREDENTIALS:")
        print("="*60)
        print("School 1 (Greenwood):")
        print("  Email: counsellor1@greenwood.edu")
        print("  Password: password123")
        print("\nSchool 2 (Riverside):")
        print("  Email: counsellor@riverside.edu")
        print("  Password: password123")
        print("\nSchool 3 (Oakmont):")
        print("  Email: counsellor@oakmont.edu")
        print("  Password: password123")
        print("\nSchool 4 (Sunnydale):")
        print("  Email: counsellor@sunnydale.edu")
        print("  Password: password123")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
