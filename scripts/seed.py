#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import engine, SessionLocal, Base
from app.core.security import get_password_hash
from app.models import School, User, Student, Class, Case, Observation, Assessment, Resource
from app.models.case import CaseStatus, RiskLevel, JournalEntry, EntryVisibility, EntryType
from app.models.user import UserRole
from app.models.student import Gender
from app.models.observation import Severity
from app.models.resource import ResourceType, ResourceStatus
from datetime import datetime, date, timedelta

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        school1 = School(
            name="Greenwood High School",
            address="123 Education Lane",
            city="Springfield",
            state="Illinois",
            country="USA",
            phone="+1-555-0100",
            email="admin@greenwood.edu",
            website="https://greenwood.edu",
            timezone="America/Chicago",
            academic_year="2024-2025",
            settings={"enable_ai": True, "parent_portal": True}
        )
        
        school2 = School(
            name="Riverside Academy",
            address="456 River Road",
            city="Portland",
            state="Oregon",
            country="USA",
            phone="+1-555-0200",
            email="info@riverside.edu",
            website="https://riverside.edu",
            timezone="America/Los_Angeles",
            academic_year="2024-2025"
        )
        
        db.add_all([school1, school2])
        db.flush()
        
        principal1 = User(
            school_id=school1.school_id,
            role=UserRole.PRINCIPAL,
            email="principal@greenwood.edu",
            hashed_password=get_password_hash("password123"),
            display_name="Dr. Margaret Thompson",
            phone="+1-555-0101",
            profile={
                "qualifications": ["PhD in Education", "20 years experience"],
                "specializations": ["School Leadership"]
            }
        )
        
        counsellor1 = User(
            school_id=school1.school_id,
            role=UserRole.COUNSELLOR,
            email="counsellor1@greenwood.edu",
            hashed_password=get_password_hash("password123"),
            display_name="Dr. Sarah Johnson",
            phone="+1-555-0102",
            profile={
                "qualifications": ["MA in Psychology", "Licensed Counselor"],
                "specializations": ["Anxiety", "Depression", "Trauma"],
                "languages": ["English", "Spanish"]
            },
            availability={
                "monday": ["09:00-17:00"],
                "tuesday": ["09:00-17:00"],
                "wednesday": ["09:00-17:00"],
                "thursday": ["09:00-17:00"],
                "friday": ["09:00-15:00"]
            }
        )
        
        counsellor2 = User(
            school_id=school1.school_id,
            role=UserRole.COUNSELLOR,
            email="counsellor2@greenwood.edu",
            hashed_password=get_password_hash("password123"),
            display_name="Mr. David Chen",
            phone="+1-555-0103",
            profile={
                "qualifications": ["MSW", "LCSW"],
                "specializations": ["Behavioral Issues", "Family Therapy"],
                "languages": ["English", "Mandarin"]
            }
        )
        
        teacher1 = User(
            school_id=school1.school_id,
            role=UserRole.TEACHER,
            email="teacher1@greenwood.edu",
            hashed_password=get_password_hash("password123"),
            display_name="Ms. Emily Rodriguez",
            phone="+1-555-0104",
            profile={
                "subjects": ["Mathematics", "Science"],
                "experience_years": 8
            }
        )
        
        teacher2 = User(
            school_id=school1.school_id,
            role=UserRole.TEACHER,
            email="teacher2@greenwood.edu",
            hashed_password=get_password_hash("password123"),
            display_name="Mr. James Wilson",
            phone="+1-555-0105",
            profile={
                "subjects": ["English", "Social Studies"],
                "experience_years": 12
            }
        )
        
        teacher3 = User(
            school_id=school1.school_id,
            role=UserRole.TEACHER,
            email="teacher3@greenwood.edu",
            hashed_password=get_password_hash("password123"),
            display_name="Mrs. Lisa Anderson",
            phone="+1-555-0106",
            profile={
                "subjects": ["Physical Education", "Health"],
                "experience_years": 5
            }
        )
        
        principal2 = User(
            school_id=school2.school_id,
            role=UserRole.PRINCIPAL,
            email="principal@riverside.edu",
            hashed_password=get_password_hash("password123"),
            display_name="Mr. Robert Martinez",
            phone="+1-555-0201"
        )
        
        counsellor3 = User(
            school_id=school2.school_id,
            role=UserRole.COUNSELLOR,
            email="counsellor@riverside.edu",
            hashed_password=get_password_hash("password123"),
            display_name="Dr. Amanda Foster",
            phone="+1-555-0202"
        )
        
        db.add_all([principal1, counsellor1, counsellor2, teacher1, teacher2, teacher3, principal2, counsellor3])
        db.flush()
        
        class_5a = Class(
            school_id=school1.school_id,
            name="Grade 5-A",
            grade="5",
            section="A",
            academic_year="2024-2025",
            teacher_id=teacher1.user_id,
            capacity=30
        )
        
        class_5b = Class(
            school_id=school1.school_id,
            name="Grade 5-B",
            grade="5",
            section="B",
            academic_year="2024-2025",
            teacher_id=teacher2.user_id,
            capacity=30
        )
        
        class_8a = Class(
            school_id=school1.school_id,
            name="Grade 8-A",
            grade="8",
            section="A",
            academic_year="2024-2025",
            teacher_id=teacher3.user_id,
            capacity=28
        )
        
        class_10a = Class(
            school_id=school1.school_id,
            name="Grade 10-A",
            grade="10",
            section="A",
            academic_year="2024-2025",
            teacher_id=teacher1.user_id,
            capacity=25
        )
        
        class_12a = Class(
            school_id=school1.school_id,
            name="Grade 12-A",
            grade="12",
            section="A",
            academic_year="2024-2025",
            teacher_id=teacher2.user_id,
            capacity=25
        )
        
        db.add_all([class_5a, class_5b, class_8a, class_10a, class_12a])
        db.flush()
        
        students_data = [
            {"first_name": "Alex", "last_name": "Williams", "gender": Gender.MALE, "dob": date(2014, 3, 15), "class_id": class_5a.class_id, "parent_email": "williams@email.com", "parent_phone": "+1-555-1001"},
            {"first_name": "Emma", "last_name": "Brown", "gender": Gender.FEMALE, "dob": date(2014, 7, 22), "class_id": class_5a.class_id, "parent_email": "brown@email.com", "parent_phone": "+1-555-1002"},
            {"first_name": "Noah", "last_name": "Davis", "gender": Gender.MALE, "dob": date(2014, 5, 10), "class_id": class_5a.class_id, "parent_email": "davis@email.com", "parent_phone": "+1-555-1003"},
            {"first_name": "Olivia", "last_name": "Miller", "gender": Gender.FEMALE, "dob": date(2014, 9, 8), "class_id": class_5a.class_id, "parent_email": "miller@email.com", "parent_phone": "+1-555-1004"},
            {"first_name": "Liam", "last_name": "Garcia", "gender": Gender.MALE, "dob": date(2014, 2, 18), "class_id": class_5b.class_id, "parent_email": "garcia@email.com", "parent_phone": "+1-555-1005"},
            {"first_name": "Sophia", "last_name": "Martinez", "gender": Gender.FEMALE, "dob": date(2014, 11, 25), "class_id": class_5b.class_id, "parent_email": "martinez@email.com", "parent_phone": "+1-555-1006"},
            {"first_name": "Ethan", "last_name": "Lopez", "gender": Gender.MALE, "dob": date(2011, 4, 12), "class_id": class_8a.class_id, "parent_email": "lopez@email.com", "parent_phone": "+1-555-1007"},
            {"first_name": "Ava", "last_name": "Gonzalez", "gender": Gender.FEMALE, "dob": date(2011, 8, 30), "class_id": class_8a.class_id, "parent_email": "gonzalez@email.com", "parent_phone": "+1-555-1008"},
            {"first_name": "Mason", "last_name": "Wilson", "gender": Gender.MALE, "dob": date(2011, 6, 5), "class_id": class_8a.class_id, "parent_email": "wilson@email.com", "parent_phone": "+1-555-1009"},
            {"first_name": "Isabella", "last_name": "Anderson", "gender": Gender.FEMALE, "dob": date(2009, 1, 20), "class_id": class_10a.class_id, "parent_email": "anderson@email.com", "parent_phone": "+1-555-1010"},
            {"first_name": "James", "last_name": "Thomas", "gender": Gender.MALE, "dob": date(2009, 10, 14), "class_id": class_10a.class_id, "parent_email": "thomas@email.com", "parent_phone": "+1-555-1011"},
            {"first_name": "Mia", "last_name": "Taylor", "gender": Gender.FEMALE, "dob": date(2009, 3, 28), "class_id": class_10a.class_id, "parent_email": "taylor@email.com", "parent_phone": "+1-555-1012"},
            {"first_name": "Benjamin", "last_name": "Moore", "gender": Gender.MALE, "dob": date(2007, 5, 16), "class_id": class_12a.class_id, "parent_email": "moore@email.com", "parent_phone": "+1-555-1013"},
            {"first_name": "Charlotte", "last_name": "Jackson", "gender": Gender.FEMALE, "dob": date(2007, 12, 3), "class_id": class_12a.class_id, "parent_email": "jackson@email.com", "parent_phone": "+1-555-1014"},
            {"first_name": "Lucas", "last_name": "White", "gender": Gender.MALE, "dob": date(2007, 7, 9), "class_id": class_12a.class_id, "parent_email": "white@email.com", "parent_phone": "+1-555-1015"},
        ]
        
        students = []
        for student_data in students_data:
            student = Student(
                school_id=school1.school_id,
                **student_data
            )
            students.append(student)
        
        db.add_all(students)
        db.flush()
        
        case1 = Case(
            student_id=students[0].student_id,
            created_by=counsellor1.user_id,
            status=CaseStatus.INTERVENTION,
            risk_level=RiskLevel.MEDIUM,
            assigned_counsellor=counsellor1.user_id,
            tags=["anxiety", "social-skills"],
            ai_summary="Student showing moderate anxiety, working on social skills development with positive progress"
        )
        
        case2 = Case(
            student_id=students[1].student_id,
            created_by=counsellor1.user_id,
            status=CaseStatus.MONITORING,
            risk_level=RiskLevel.LOW,
            assigned_counsellor=counsellor1.user_id,
            tags=["adjustment", "peer-relationships"],
            ai_summary="Student making progress in peer relationships, monitoring for continued improvement"
        )
        
        case3 = Case(
            student_id=students[6].student_id,
            created_by=counsellor2.user_id,
            status=CaseStatus.ASSESSMENT,
            risk_level=RiskLevel.HIGH,
            assigned_counsellor=counsellor2.user_id,
            tags=["depression", "self-harm-risk"],
            ai_summary="High-risk case: Student presenting with depression symptoms. External referral recommended and parent meeting scheduled"
        )
        
        case4 = Case(
            student_id=students[12].student_id,
            created_by=counsellor1.user_id,
            status=CaseStatus.INTAKE,
            risk_level=RiskLevel.MEDIUM,
            assigned_counsellor=counsellor1.user_id,
            tags=["exam-stress", "burnout"],
            ai_summary="New case: Exam-related stress and sleep disturbance. Starting stress management intervention"
        )
        
        db.add_all([case1, case2, case3, case4])
        db.flush()
        
        # Create journal entries for cases
        journal1 = JournalEntry(
            case_id=case1.case_id,
            author_id=counsellor1.user_id,
            visibility=EntryVisibility.SHARED,
            type=EntryType.SESSION_NOTE,
            content="Initial session completed. Student expressed concerns about social interactions and peer relationships. Agreed on weekly sessions focused on social skills development.",
            created_at=datetime.utcnow() - timedelta(days=14)
        )
        
        journal2 = JournalEntry(
            case_id=case1.case_id,
            author_id=counsellor1.user_id,
            visibility=EntryVisibility.SHARED,
            type=EntryType.SESSION_NOTE,
            content="Second session - practiced conversation starters and active listening techniques. Student showed improvement in eye contact and engagement.",
            created_at=datetime.utcnow() - timedelta(days=7)
        )
        
        journal3 = JournalEntry(
            case_id=case2.case_id,
            author_id=counsellor1.user_id,
            visibility=EntryVisibility.SHARED,
            type=EntryType.SESSION_NOTE,
            content="Follow-up session. Student reports making a new friend in class. Discussed strategies for maintaining friendships and handling conflicts.",
            created_at=datetime.utcnow() - timedelta(days=10)
        )
        
        journal4 = JournalEntry(
            case_id=case3.case_id,
            author_id=counsellor2.user_id,
            visibility=EntryVisibility.PRIVATE,
            type=EntryType.ASSESSMENT_RESULT,
            content="PHQ-9 assessment completed. Score: 18 (moderately severe depression). Recommend continued monitoring and potential referral to external mental health services.",
            created_at=datetime.utcnow() - timedelta(days=5)
        )
        
        journal5 = JournalEntry(
            case_id=case3.case_id,
            author_id=counsellor2.user_id,
            visibility=EntryVisibility.SHARED,
            type=EntryType.CONTACT_LOG,
            content="Parent contacted. Discussed assessment results and recommended external support options. Parents agreed to schedule appointment with psychiatrist.",
            created_at=datetime.utcnow() - timedelta(days=3)
        )
        
        journal6 = JournalEntry(
            case_id=case4.case_id,
            author_id=counsellor1.user_id,
            visibility=EntryVisibility.SHARED,
            type=EntryType.SESSION_NOTE,
            content="Intake session. Student reports high stress levels due to upcoming board exams. Sleep pattern disrupted. Discussed stress management techniques and time management strategies.",
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        
        db.add_all([journal1, journal2, journal3, journal4, journal5, journal6])
        db.flush()
        
        obs1 = Observation(
            student_id=students[0].student_id,
            reported_by=teacher1.user_id,
            severity=Severity.MEDIUM,
            category="behavioral",
            content="Student appears withdrawn during group activities. Reluctant to participate in class discussions.",
            ai_summary="Student showing signs of social withdrawal in group settings"
        )
        
        obs2 = Observation(
            student_id=students[1].student_id,
            reported_by=teacher1.user_id,
            severity=Severity.LOW,
            category="social",
            content="Difficulty making friends. Prefers to work alone.",
            ai_summary="Student demonstrates preference for solitary activities"
        )
        
        obs3 = Observation(
            student_id=students[6].student_id,
            reported_by=teacher3.user_id,
            severity=Severity.HIGH,
            category="emotional",
            content="Student showed signs of distress. Mentioned feeling hopeless. Immediate counselor referral made.",
            ai_summary="High priority: Student expressing hopelessness, immediate intervention required"
        )
        
        obs4 = Observation(
            student_id=students[12].student_id,
            reported_by=teacher2.user_id,
            severity=Severity.MEDIUM,
            category="academic-stress",
            content="Student expressed extreme anxiety about upcoming exams. Sleep deprivation reported.",
            ai_summary="Exam-related anxiety affecting sleep patterns"
        )
        
        obs5 = Observation(
            student_id=students[2].student_id,
            reported_by=teacher1.user_id,
            severity=Severity.LOW,
            category="behavioral",
            content="Occasional disruptive behavior in class. Seeking attention.",
            ai_summary="Minor behavioral concern: Attention-seeking behavior observed"
        )
        
        db.add_all([obs1, obs2, obs3, obs4, obs5])
        db.flush()
        
        assess1 = Assessment(
            student_id=students[0].student_id,
            created_by=counsellor1.user_id,
            responses={
                "q1_feeling_nervous": "sometimes",
                "q2_worry_control": "often",
                "q3_social_comfort": "rarely",
                "q4_sleep_quality": "poor"
            },
            scores={
                "anxiety_score": 18,
                "social_score": 12,
                "overall_wellbeing": 65
            },
            completed_at=datetime.utcnow()
        )
        
        assess2 = Assessment(
            student_id=students[6].student_id,
            created_by=counsellor2.user_id,
            responses={
                "q1_mood": "very_low",
                "q2_interest_loss": "yes",
                "q3_hopelessness": "often",
                "q4_self_harm_thoughts": "sometimes"
            },
            scores={
                "depression_score": 24,
                "risk_score": 8,
                "overall_wellbeing": 35
            },
            completed_at=datetime.utcnow()
        )
        
        assess3 = Assessment(
            student_id=students[12].student_id,
            created_by=counsellor1.user_id,
            responses={
                "q1_exam_stress": "very_high",
                "q2_sleep_hours": "4-5",
                "q3_concentration": "poor",
                "q4_physical_symptoms": "yes"
            },
            scores={
                "stress_score": 22,
                "burnout_risk": 7,
                "overall_wellbeing": 50
            },
            completed_at=datetime.utcnow()
        )
        
        db.add_all([assess1, assess2, assess3])
        db.flush()
        
        resource1 = Resource(
            school_id=None,
            type=ResourceType.VIDEO,
            status=ResourceStatus.PUBLISHED,
            title="Understanding Anxiety in Teens",
            description="A comprehensive guide to recognizing and managing anxiety in adolescents.",
            video_url="https://example.com/videos/anxiety-teens.mp4",
            thumbnail_url="https://example.com/thumbnails/anxiety-teens.jpg",
            author_name="Dr. Emily Chen",
            author_id=counsellor1.user_id,
            posted_date=datetime.utcnow() - timedelta(days=30),
            duration_seconds=1200,
            tags=["anxiety", "teens", "mental-health", "coping-strategies"],
            category="anxiety",
            target_audience=["counsellors", "teachers", "parents"],
            view_count=245,
            additional_metadata={"language": "en", "subtitles": ["en", "es"]}
        )
        
        resource2 = Resource(
            school_id=None,
            type=ResourceType.VIDEO,
            status=ResourceStatus.PUBLISHED,
            title="Mindfulness Exercises for Students",
            description="Simple mindfulness techniques that students can practice daily.",
            video_url="https://example.com/videos/mindfulness-students.mp4",
            thumbnail_url="https://example.com/thumbnails/mindfulness.jpg",
            author_name="Sarah Johnson",
            posted_date=datetime.utcnow() - timedelta(days=15),
            duration_seconds=600,
            tags=["mindfulness", "meditation", "stress-relief", "self-care"],
            category="stress-management",
            target_audience=["students", "teachers"],
            view_count=189,
            additional_metadata={"difficulty": "beginner"}
        )
        
        resource3 = Resource(
            school_id=None,
            type=ResourceType.AUDIO,
            status=ResourceStatus.PUBLISHED,
            title="Guided Meditation for Exam Stress",
            description="A calming guided meditation to help students manage exam anxiety.",
            audio_url="https://example.com/audio/exam-stress-meditation.mp3",
            thumbnail_url="https://example.com/thumbnails/meditation-audio.jpg",
            author_name="Lisa Anderson",
            posted_date=datetime.utcnow() - timedelta(days=20),
            duration_seconds=480,
            tags=["meditation", "exam-stress", "anxiety", "relaxation"],
            category="stress-management",
            target_audience=["students"],
            view_count=156,
            additional_metadata={"format": "mp3", "bitrate": "320kbps"}
        )
        
        resource4 = Resource(
            school_id=None,
            type=ResourceType.ARTICLE,
            status=ResourceStatus.PUBLISHED,
            title="10 Ways to Support a Student in Crisis",
            description="Practical strategies for teachers and counsellors to provide immediate support.",
            article_url="https://example.com/articles/support-student-crisis",
            thumbnail_url="https://example.com/thumbnails/crisis-support.jpg",
            author_name="Dr. Amanda Foster",
            posted_date=datetime.utcnow() - timedelta(days=25),
            tags=["crisis-intervention", "support", "teachers", "counselling"],
            category="crisis-intervention",
            target_audience=["counsellors", "teachers"],
            view_count=567,
            additional_metadata={"reading_time_minutes": 8}
        )
        
        resource5 = Resource(
            school_id=school1.school_id,
            type=ResourceType.VIDEO,
            status=ResourceStatus.PUBLISHED,
            title=f"{school1.name} - Counselling Services Overview",
            description="Learn about the mental health support services available at our school.",
            video_url="https://example.com/videos/school-services.mp4",
            thumbnail_url="https://example.com/thumbnails/school-services.jpg",
            author_name="School Counselling Team",
            author_id=counsellor1.user_id,
            posted_date=datetime.utcnow() - timedelta(days=60),
            duration_seconds=420,
            tags=["school-services", "counselling", "resources"],
            category="school-specific",
            target_audience=["students", "parents"],
            view_count=89,
            additional_metadata={"school_year": "2024-2025"}
        )
        
        db.add_all([resource1, resource2, resource3, resource4, resource5])
        db.commit()
        
        print(f"Seeded: 2 schools, 8 staff, 5 classes, {len(students)} students, 4 cases with 6 journal entries, 5 observations, 3 assessments, 5 resources")
        print(f"Login: counsellor1@greenwood.edu / password123")
        print(f"School ID: {school1.school_id}")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
