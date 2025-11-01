#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import engine, SessionLocal, Base
from app.core.security import get_password_hash
from app.models import School, User, Student, Class, Case, Observation, Resource
from app.models.assessment import Assessment, AssessmentTemplate, StudentResponse, QuestionType
from app.models.case import CaseStatus, RiskLevel, JournalEntry, EntryVisibility, EntryType
from app.models.user import UserRole
from app.models.student import Gender
from app.models.observation import Severity
from app.models.resource import ResourceType, ResourceStatus
from app.models.activity import Activity, ActivityType
from datetime import datetime, date, timedelta
import random

# Helper function to generate realistic student data
def generate_student_data(school_id, class_id, start_index, count, grade_year):
    """Generate realistic student data with parents"""
    first_names_male = ["Alex", "Noah", "Liam", "Ethan", "Mason", "James", "Benjamin", "Lucas", "Henry", "Sebastian",
                        "Jack", "Owen", "Daniel", "Matthew", "Jackson", "Logan", "David", "Joseph", "Samuel", "Michael",
                        "Elijah", "Oliver", "William", "Ryan", "Nathan", "Caleb", "Dylan", "Tyler", "Andrew", "Joshua",
                        "Christopher", "Anthony", "Thomas", "Charles", "Isaiah", "Gabriel", "Carter", "Jayden", "John", "Luke"]
    
    first_names_female = ["Emma", "Olivia", "Ava", "Sophia", "Isabella", "Mia", "Charlotte", "Amelia", "Harper", "Ella",
                          "Emily", "Madison", "Abigail", "Lily", "Chloe", "Grace", "Zoe", "Hannah", "Victoria", "Aria",
                          "Scarlett", "Natalie", "Addison", "Lillian", "Brooklyn", "Layla", "Evelyn", "Claire", "Stella", "Audrey",
                          "Zoey", "Penelope", "Riley", "Nora", "Hazel", "Camila", "Violet", "Aurora", "Savannah", "Bella"]
    
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
                  "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
                  "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
                  "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"]
    
    parent_first_names = ["Mary", "John", "Sarah", "Michael", "Lisa", "David", "Jennifer", "Robert", "Linda", "James",
                          "Patricia", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Karen", "Charles"]
    
    students = []
    parents = []
    birth_year = 2024 - grade_year
    
    for i in range(count):
        gender = random.choice([Gender.MALE, Gender.FEMALE])
        first_name = random.choice(first_names_male if gender == Gender.MALE else first_names_female)
        last_name = random.choice(last_names)
        
        # Generate birth date
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        dob = date(birth_year, month, day)
        
        # Generate parent data (1-2 parents per student)
        num_parents = random.choice([1, 2])
        student_parents = []
        
        for p in range(num_parents):
            parent_first_name = random.choice(parent_first_names)
            parent_display_name = f"{parent_first_name} {last_name}"
            parent_email = f"{last_name.lower()}.{parent_first_name.lower()}{start_index+i}p{p}@email.com"
            parent_phone = f"+1-555-{random.randint(1000, 9999)}"
            
            parent_data = {
                "school_id": school_id,
                "display_name": parent_display_name,
                "email": parent_email,
                "phone": parent_phone,
                "student_index": start_index + i  # To link back to student
            }
            parents.append(parent_data)
            student_parents.append(parent_data)
        
        students.append({
            "school_id": school_id,
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "dob": dob,
            "class_id": class_id,
            "parent_email": student_parents[0]["email"],  # Legacy field
            "parent_phone": student_parents[0]["phone"],  # Legacy field
            "parent_data": student_parents  # For linking
        })
    
    return students, parents

def seed_database():
    # Drop and recreate all tables for a fresh start
    print("\n" + "="*70)
    print("PREPARING DATABASE FOR SEEDING")
    print("="*70 + "\n")
    
    print("🗑️  Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tables dropped")
    
    print("\n🔨 Creating fresh tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("SEEDING DATABASE WITH 2 SCHOOLS - 250 STUDENTS EACH")
        print("="*70 + "\n")
        
        # === SCHOOLS ===
        print("📚 Creating schools...")
        school1 = School(
            name="Lincoln High School",
            address="500 Education Boulevard",
            city="Springfield",
            state="Illinois",
            country="USA",
            phone="+1-555-0100",
            email="admin@lincoln.edu",
            website="https://lincoln.edu",
            timezone="America/Chicago",
            academic_year="2024-2025",
            settings={"enable_ai": True, "parent_portal": True}
        )
        
        school2 = School(
            name="Washington Academy",
            address="750 Knowledge Avenue",
            city="Portland",
            state="Oregon",
            country="USA",
            phone="+1-555-0200",
            email="info@washington.edu",
            website="https://washington.edu",
            timezone="America/Los_Angeles",
            academic_year="2024-2025",
            settings={"enable_ai": True, "parent_portal": True}
        )
        
        db.add_all([school1, school2])
        db.flush()
        print(f"✅ Created 2 schools")
        
        # === SCHOOL 1 STAFF ===
        print("\n👥 Creating staff for School 1...")
        
        # Principal
        principal1 = User(
            school_id=school1.school_id,
            role=UserRole.PRINCIPAL,
            email="principal@lincoln.edu",
            hashed_password=get_password_hash("password123"),
            display_name="Dr. Margaret Thompson",
            phone="+1-555-0101",
            profile={
                "qualifications": ["PhD in Education", "25 years experience"],
                "specializations": ["School Leadership", "Curriculum Development"]
            }
        )
        
        # Counsellors (6 for 250 students - ratio of ~42 students per counselor)
        counsellors_s1 = [
            User(
                school_id=school1.school_id,
                role=UserRole.COUNSELLOR,
                email=f"counsellor{i}@lincoln.edu",
                hashed_password=get_password_hash("password123"),
                display_name=name,
                phone=f"+1-555-010{i+1}",
                profile={
                    "qualifications": quals,
                    "specializations": specs,
                    "languages": langs
                },
                availability={
                    "monday": ["09:00-17:00"],
                    "tuesday": ["09:00-17:00"],
                    "wednesday": ["09:00-17:00"],
                    "thursday": ["09:00-17:00"],
                    "friday": ["09:00-15:00"]
                }
            )
            for i, (name, quals, specs, langs) in enumerate([
                ("Dr. Sarah Johnson", ["PhD in Psychology", "Licensed Counselor"], ["Anxiety", "Depression", "Trauma"], ["English", "Spanish"]),
                ("Mr. David Chen", ["MSW", "LCSW"], ["Behavioral Issues", "Family Therapy"], ["English", "Mandarin"]),
                ("Dr. Emily Rodriguez", ["MA in Counseling"], ["Academic Stress", "Career Counseling"], ["English", "Spanish"]),
                ("Ms. Rachel Green", ["MA in Psychology"], ["Grief", "Bullying", "Social Skills"], ["English"]),
                ("Mr. Kevin Patel", ["PhD in Educational Psychology"], ["Learning Disabilities", "ADHD"], ["English", "Hindi"]),
                ("Dr. Michelle Brown", ["PhD in Clinical Psychology"], ["Eating Disorders", "Self-Esteem", "Body Image"], ["English"])
            ])
        ]
        
        # Teachers (12 for multiple classes - need more for 10 classes)
        teachers_s1 = [
            User(
                school_id=school1.school_id,
                role=UserRole.TEACHER,
                email=f"teacher{i}@lincoln.edu",
                hashed_password=get_password_hash("password123"),
                display_name=name,
                phone=f"+1-555-011{i}",
                profile={"subjects": subjects, "experience_years": exp}
            )
            for i, (name, subjects, exp) in enumerate([
                ("Ms. Emily Anderson", ["Mathematics", "Science"], 8),
                ("Mr. James Wilson", ["English", "Social Studies"], 12),
                ("Mrs. Lisa Martinez", ["Physical Education", "Health"], 5),
                ("Mr. Robert Brown", ["Science", "Biology"], 10),
                ("Ms. Jennifer Lee", ["English Literature", "Writing"], 7),
                ("Mr. Michael Davis", ["History", "Geography"], 15),
                ("Ms. Patricia White", ["Mathematics", "Computer Science"], 6),
                ("Mr. Christopher Hall", ["Art", "Music"], 9),
                ("Ms. Angela Garcia", ["Spanish", "French"], 11),
                ("Mr. Thomas Wright", ["Chemistry", "Physics"], 13),
                ("Ms. Sarah Miller", ["Mathematics", "Statistics"], 9),
                ("Mr. Daniel Taylor", ["English", "Drama"], 8)
            ], 1)
        ]
        
        db.add_all([principal1] + counsellors_s1 + teachers_s1)
        db.flush()
        print(f"✅ Created 1 principal, 6 counsellors, 12 teachers for School 1")
        
        # === SCHOOL 2 STAFF ===
        print("\n👥 Creating staff for School 2...")
        
        # Principal
        principal2 = User(
            school_id=school2.school_id,
            role=UserRole.PRINCIPAL,
            email="principal@washington.edu",
            hashed_password=get_password_hash("password123"),
            display_name="Mr. Robert Martinez",
            phone="+1-555-0201",
            profile={
                "qualifications": ["EdD in Educational Leadership", "20 years experience"],
                "specializations": ["School Administration", "Student Wellbeing"]
            }
        )
        
        # Counsellors (6 for 250 students - ratio of ~42 students per counselor)
        counsellors_s2 = [
            User(
                school_id=school2.school_id,
                role=UserRole.COUNSELLOR,
                email=f"counsellor{i}@washington.edu",
                hashed_password=get_password_hash("password123"),
                display_name=name,
                phone=f"+1-555-020{i+1}",
                profile={
                    "qualifications": quals,
                    "specializations": specs,
                    "languages": langs
                },
                availability={
                    "monday": ["09:00-17:00"],
                    "tuesday": ["09:00-17:00"],
                    "wednesday": ["09:00-17:00"],
                    "thursday": ["09:00-17:00"],
                    "friday": ["09:00-15:00"]
                }
            )
            for i, (name, quals, specs, langs) in enumerate([
                ("Dr. Amanda Foster", ["PhD in Clinical Psychology"], ["ADHD", "Learning Disabilities", "Autism"], ["English"]),
                ("Ms. Maria Gonzalez", ["MA in Counseling"], ["Anxiety", "Depression", "Self-Esteem"], ["English", "Spanish"]),
                ("Mr. Daniel Kim", ["MSW", "LICSW"], ["Substance Abuse", "Peer Pressure", "Crisis"], ["English", "Korean"]),
                ("Dr. Linda Carter", ["PhD in Psychology"], ["Trauma", "PTSD", "Family Issues"], ["English"]),
                ("Ms. Priya Sharma", ["MA in School Counseling"], ["Academic Stress", "Career Planning"], ["English", "Hindi"]),
                ("Dr. James Anderson", ["PhD in Educational Psychology"], ["Behavioral Issues", "Social Skills"], ["English"])
            ])
        ]
        
        # Teachers (12 for multiple classes - need more for 10 classes)
        teachers_s2 = [
            User(
                school_id=school2.school_id,
                role=UserRole.TEACHER,
                email=f"teacher{i}@washington.edu",
                hashed_password=get_password_hash("password123"),
                display_name=name,
                phone=f"+1-555-021{i}",
                profile={"subjects": subjects, "experience_years": exp}
            )
            for i, (name, subjects, exp) in enumerate([
                ("Ms. Jennifer Taylor", ["Mathematics", "Algebra"], 9),
                ("Mr. Michael Brown", ["History", "Social Studies"], 14),
                ("Mrs. Susan Clark", ["English", "Literature"], 8),
                ("Mr. David Wilson", ["Science", "Chemistry"], 11),
                ("Ms. Karen Moore", ["Physical Education", "Sports"], 6),
                ("Mr. Richard Jackson", ["Computer Science", "Technology"], 10),
                ("Ms. Nancy White", ["Biology", "Environmental Science"], 12),
                ("Mr. Paul Harris", ["Mathematics", "Geometry"], 7),
                ("Ms. Laura Martin", ["Art", "Design"], 9),
                ("Mr. Steven Thompson", ["Music", "Drama"], 15),
                ("Ms. Rebecca Adams", ["English", "Creative Writing"], 10),
                ("Mr. George Martinez", ["Science", "Physics"], 13)
            ], 1)
        ]
        
        db.add_all([principal2] + counsellors_s2 + teachers_s2)
        db.flush()
        print(f"✅ Created 1 principal, 6 counsellors, 12 teachers for School 2")
        
        # === CLASSES FOR SCHOOL 1 ===
        print("\n📖 Creating classes for School 1...")
        classes_s1 = []
        
        # Create 10 classes (Grades 9-12, with varying sections) - 25 students per class = 250 total
        # Grade 9: 3 sections (75 students)
        # Grade 10: 3 sections (75 students)
        # Grade 11: 2 sections (50 students)
        # Grade 12: 2 sections (50 students)
        class_distribution = [
            ("9", ["A", "B", "C"]),
            ("10", ["A", "B", "C"]),
            ("11", ["A", "B"]),
            ("12", ["A", "B"])
        ]
        
        for grade, sections in class_distribution:
            for section in sections:
                teacher = random.choice(teachers_s1)
                class_obj = Class(
                    school_id=school1.school_id,
                    name=f"Grade {grade}-{section}",
                    grade=grade,
                    section=section,
                    academic_year="2024-2025",
                    teacher_id=teacher.user_id,
                    capacity=25
                )
                classes_s1.append(class_obj)
        
        db.add_all(classes_s1)
        db.flush()
        print(f"✅ Created {len(classes_s1)} classes for School 1")
        
        # === CLASSES FOR SCHOOL 2 ===
        print("\n📖 Creating classes for School 2...")
        classes_s2 = []
        
        # Create 10 classes (Grades 9-12, with varying sections) - 25 students per class = 250 total
        # Grade 9: 3 sections (75 students)
        # Grade 10: 3 sections (75 students)
        # Grade 11: 2 sections (50 students)
        # Grade 12: 2 sections (50 students)
        class_distribution = [
            ("9", ["A", "B", "C"]),
            ("10", ["A", "B", "C"]),
            ("11", ["A", "B"]),
            ("12", ["A", "B"])
        ]
        
        for grade, sections in class_distribution:
            for section in sections:
                teacher = random.choice(teachers_s2)
                class_obj = Class(
                    school_id=school2.school_id,
                    name=f"Grade {grade}-{section}",
                    grade=grade,
                    section=section,
                    academic_year="2024-2025",
                    teacher_id=teacher.user_id,
                    capacity=25
                )
                classes_s2.append(class_obj)
        
        db.add_all(classes_s2)
        db.flush()
        print(f"✅ Created {len(classes_s2)} classes for School 2")
        
        # === PARENTS & STUDENTS FOR SCHOOL 1 ===
        print("\n👨‍👩‍👧‍👦 Creating parents for School 1...")
        students_s1_data = []
        parents_s1_data = []
        
        # Distribute students across classes (exactly 25 per class for 250 total)
        for i, class_obj in enumerate(classes_s1):
            grade_num = int(class_obj.grade)
            grade_year = grade_num  # Age calculation
            student_count = 25  # Fixed 25 students per class
            students_data, parents_data = generate_student_data(
                school1.school_id, 
                class_obj.class_id, 
                i * 25, 
                student_count, 
                grade_year
            )
            students_s1_data.extend(students_data)
            parents_s1_data.extend(parents_data)
        
        # Create parent users
        parents_s1 = []
        for parent_data in parents_s1_data:
            parent = User(
                school_id=parent_data["school_id"],
                role=UserRole.PARENT,
                email=parent_data["email"],
                hashed_password=get_password_hash("password123"),
                display_name=parent_data["display_name"],
                phone=parent_data["phone"],
                profile={
                    "preferred_contact_method": "email",
                    "languages": ["English"]
                }
            )
            parents_s1.append(parent)
        
        db.add_all(parents_s1)
        db.flush()
        print(f"✅ Created {len(parents_s1)} parents for School 1")
        
        # Create students and link to parents
        print("\n👨‍🎓 Creating students for School 1...")
        students_s1 = []
        for student_data in students_s1_data:
            # Find parent IDs for this student
            parent_ids = [p.user_id for p in parents_s1 
                         if any(pd["student_index"] == students_s1_data.index(student_data) 
                               for pd in parents_s1_data 
                               if pd["email"] == p.email)]
            
            # Remove parent_data before creating Student object
            parent_data_list = student_data.pop("parent_data", [])
            
            # Link parents by email matching
            linked_parent_ids = []
            for pd in parent_data_list:
                for parent in parents_s1:
                    if parent.email == pd["email"]:
                        linked_parent_ids.append(str(parent.user_id))
                        break
            
            student = Student(
                **student_data,
                parents_id=linked_parent_ids if linked_parent_ids else None
            )
            students_s1.append(student)
        
        db.add_all(students_s1)
        db.flush()
        print(f"✅ Created {len(students_s1)} students for School 1")
        
        # === PARENTS & STUDENTS FOR SCHOOL 2 ===
        print("\n👨‍👩‍👧‍👦 Creating parents for School 2...")
        students_s2_data = []
        parents_s2_data = []
        
        # Distribute students across classes (exactly 25 per class for 250 total)
        for i, class_obj in enumerate(classes_s2):
            grade_num = int(class_obj.grade)
            grade_year = grade_num  # Age calculation
            student_count = 25  # Fixed 25 students per class
            students_data, parents_data = generate_student_data(
                school2.school_id, 
                class_obj.class_id, 
                i * 25, 
                student_count, 
                grade_year
            )
            students_s2_data.extend(students_data)
            parents_s2_data.extend(parents_data)
        
        # Create parent users
        parents_s2 = []
        for parent_data in parents_s2_data:
            parent = User(
                school_id=parent_data["school_id"],
                role=UserRole.PARENT,
                email=parent_data["email"],
                hashed_password=get_password_hash("password123"),
                display_name=parent_data["display_name"],
                phone=parent_data["phone"],
                profile={
                    "preferred_contact_method": "email",
                    "languages": ["English"]
                }
            )
            parents_s2.append(parent)
        
        db.add_all(parents_s2)
        db.flush()
        print(f"✅ Created {len(parents_s2)} parents for School 2")
        
        # Create students and link to parents
        print("\n👨‍🎓 Creating students for School 2...")
        students_s2 = []
        for student_data in students_s2_data:
            # Remove parent_data before creating Student object
            parent_data_list = student_data.pop("parent_data", [])
            
            # Link parents by email matching
            linked_parent_ids = []
            for pd in parent_data_list:
                for parent in parents_s2:
                    if parent.email == pd["email"]:
                        linked_parent_ids.append(str(parent.user_id))
                        break
            
            student = Student(
                **student_data,
                parents_id=linked_parent_ids if linked_parent_ids else None
            )
            students_s2.append(student)
        
        db.add_all(students_s2)
        db.flush()
        print(f"✅ Created {len(students_s2)} students for School 2")
        
        all_students = students_s1 + students_s2
        
        # === CASES ===
        print("\n📋 Creating cases...")
        cases = []
        
        # School 1 Cases (12-15% of students have cases - ~30-38 cases for 250 students)
        case_count_s1 = int(len(students_s1) * 0.14)
        for i in range(case_count_s1):
            student = random.choice(students_s1)
            counsellor = random.choice(counsellors_s1)
            status = random.choice(list(CaseStatus))
            risk = random.choice(list(RiskLevel))
            
            tags_options = [
                ["anxiety", "social-skills"],
                ["depression", "self-harm-risk"],
                ["adhd", "focus-issues"],
                ["bullying", "trauma"],
                ["exam-stress", "burnout"],
                ["family-issues", "adjustment"],
                ["grief", "loss"],
                ["substance-abuse-risk", "peer-pressure"],
                ["eating-concerns", "body-image"],
                ["academic-stress", "perfectionism"]
            ]
            
            case = Case(
                student_id=student.student_id,
                created_by=counsellor.user_id,
                status=status,
                risk_level=risk,
                assigned_counsellor=counsellor.user_id,
                tags=random.choice(tags_options),
                ai_summary=f"Case for {student.first_name} {student.last_name}: {status.value} status with {risk.value} risk level"
            )
            cases.append(case)
        
        # School 2 Cases (12-15% of students have cases - ~30-38 cases for 250 students)
        case_count_s2 = int(len(students_s2) * 0.14)
        for i in range(case_count_s2):
            student = random.choice(students_s2)
            counsellor = random.choice(counsellors_s2)
            status = random.choice(list(CaseStatus))
            risk = random.choice(list(RiskLevel))
            
            tags_options = [
                ["anxiety", "social-skills"],
                ["depression", "self-harm-risk"],
                ["adhd", "focus-issues"],
                ["bullying", "trauma"],
                ["exam-stress", "burnout"],
                ["family-issues", "adjustment"],
                ["grief", "loss"],
                ["substance-abuse-risk", "peer-pressure"],
                ["eating-concerns", "body-image"],
                ["academic-stress", "perfectionism"]
            ]
            
            case = Case(
                student_id=student.student_id,
                created_by=counsellor.user_id,
                status=status,
                risk_level=risk,
                assigned_counsellor=counsellor.user_id,
                tags=random.choice(tags_options),
                ai_summary=f"Case for {student.first_name} {student.last_name}: {status.value} status with {risk.value} risk level"
            )
            cases.append(case)
        
        db.add_all(cases)
        db.flush()
        print(f"✅ Created {len(cases)} cases ({case_count_s1} for School 1, {case_count_s2} for School 2)")
        
        # === JOURNAL ENTRIES ===
        print("\n📝 Creating journal entries...")
        journal_entries = []
        
        for case in cases:
            # 2-4 journal entries per case
            entry_count = random.randint(2, 4)
            for j in range(entry_count):
                entry = JournalEntry(
                    case_id=case.case_id,
                    author_id=case.assigned_counsellor,
                    visibility=random.choice(list(EntryVisibility)),
                    type=random.choice(list(EntryType)),
                    content=f"Session note {j+1} for case {case.case_id}. Student showing progress in treatment plan.",
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                journal_entries.append(entry)
        
        db.add_all(journal_entries)
        db.flush()
        print(f"✅ Created {len(journal_entries)} journal entries")
        
        # === OBSERVATIONS ===
        print("\n👁️ Creating observations...")
        observations = []
        
        # School 1 Observations (8-10% of students - ~20-25 observations for 250 students)
        obs_count_s1 = int(len(students_s1) * 0.09)
        for i in range(obs_count_s1):
            student = random.choice(students_s1)
            teacher = random.choice(teachers_s1)
            severity = random.choice(list(Severity))
            
            categories = ["behavioral", "social", "emotional", "academic-stress", "academic", "health"]
            category = random.choice(categories)
            
            obs = Observation(
                student_id=student.student_id,
                reported_by=teacher.user_id,
                severity=severity,
                category=category,
                content=f"Observation for {student.first_name}: {category} concern noted in class.",
                ai_summary=f"{severity.value} severity {category} observation"
            )
            observations.append(obs)
        
        # School 2 Observations (8-10% of students - ~20-25 observations for 250 students)
        obs_count_s2 = int(len(students_s2) * 0.09)
        for i in range(obs_count_s2):
            student = random.choice(students_s2)
            teacher = random.choice(teachers_s2)
            severity = random.choice(list(Severity))
            
            categories = ["behavioral", "social", "emotional", "academic-stress", "academic", "health"]
            category = random.choice(categories)
            
            obs = Observation(
                student_id=student.student_id,
                reported_by=teacher.user_id,
                severity=severity,
                category=category,
                content=f"Observation for {student.first_name}: {category} concern noted in class.",
                ai_summary=f"{severity.value} severity {category} observation"
            )
            observations.append(obs)
        
        db.add_all(observations)
        db.flush()
        print(f"✅ Created {len(observations)} observations ({obs_count_s1} for School 1, {obs_count_s2} for School 2)")
        
        # === ASSESSMENT TEMPLATES ===
        print("\n📊 Creating assessment templates...")
        
        # PHQ-9 Depression Screening
        template_phq9 = AssessmentTemplate(
            name="PHQ-9 Depression Screening",
            description="Patient Health Questionnaire - 9 items for depression screening",
            category="depression",
            created_by=counsellors_s1[0].user_id,
            questions=[
                {
                    "question_id": f"q{i}",
                    "question_text": text,
                    "question_type": "rating_scale",
                    "required": True,
                    "min_value": 0,
                    "max_value": 3,
                    "answer_options": [
                        {"option_id": "0", "text": "Not at all", "value": 0},
                        {"option_id": "1", "text": "Several days", "value": 1},
                        {"option_id": "2", "text": "More than half the days", "value": 2},
                        {"option_id": "3", "text": "Nearly every day", "value": 3}
                    ]
                }
                for i, text in enumerate([
                    "Little interest or pleasure in doing things",
                    "Feeling down, depressed, or hopeless",
                    "Trouble falling or staying asleep, or sleeping too much",
                    "Feeling tired or having little energy"
                ], 1)
            ],
            scoring_rules={
                "total_score": "sum_all",
                "severity_ranges": {
                    "minimal": [0, 4],
                    "mild": [5, 9],
                    "moderate": [10, 14],
                    "moderately_severe": [15, 19],
                    "severe": [20, 27]
                }
            }
        )
        
        # GAD-7 Anxiety Screening
        template_gad7 = AssessmentTemplate(
            name="GAD-7 Anxiety Screening",
            description="Generalized Anxiety Disorder - 7 items",
            category="anxiety",
            created_by=counsellors_s1[0].user_id,
            questions=[
                {
                    "question_id": f"q{i}",
                    "question_text": text,
                    "question_type": "rating_scale",
                    "required": True,
                    "min_value": 0,
                    "max_value": 3,
                    "answer_options": [
                        {"option_id": "0", "text": "Not at all", "value": 0},
                        {"option_id": "1", "text": "Several days", "value": 1},
                        {"option_id": "2", "text": "More than half the days", "value": 2},
                        {"option_id": "3", "text": "Nearly every day", "value": 3}
                    ]
                }
                for i, text in enumerate([
                    "Feeling nervous, anxious, or on edge",
                    "Not being able to stop or control worrying",
                    "Worrying too much about different things"
                ], 1)
            ],
            scoring_rules={
                "total_score": "sum_all",
                "severity_ranges": {
                    "minimal": [0, 4],
                    "mild": [5, 9],
                    "moderate": [10, 14],
                    "severe": [15, 21]
                }
            }
        )
        
        # Academic Stress Assessment
        template_stress = AssessmentTemplate(
            name="Academic Stress & Burnout Assessment",
            description="Assessment for exam-related stress and burnout symptoms",
            category="stress",
            created_by=counsellors_s2[0].user_id,
            questions=[
                {
                    "question_id": "q1",
                    "question_text": "How would you rate your current stress level about exams?",
                    "question_type": "rating_scale",
                    "required": True,
                    "min_value": 0,
                    "max_value": 10,
                    "answer_options": [
                        {"option_id": str(i), "text": str(i), "value": i} for i in range(11)
                    ]
                },
                {
                    "question_id": "q2",
                    "question_text": "How many hours of sleep do you get on average?",
                    "question_type": "multiple_choice",
                    "required": True,
                    "answer_options": [
                        {"option_id": "less_4", "text": "Less than 4 hours", "value": 4},
                        {"option_id": "4_6", "text": "4-6 hours", "value": 3},
                        {"option_id": "6_8", "text": "6-8 hours", "value": 1},
                        {"option_id": "more_8", "text": "More than 8 hours", "value": 0}
                    ]
                },
                {
                    "question_id": "q3",
                    "question_text": "Do you experience physical symptoms (headaches, stomach issues, etc.)?",
                    "question_type": "yes_no",
                    "required": True
                }
            ],
            scoring_rules={
                "total_score": "sum_all",
                "high_risk_threshold": 15
            }
        )
        
        # Wellbeing Check
        template_wellbeing = AssessmentTemplate(
            name="Social-Emotional Wellbeing Check",
            description="General wellbeing assessment for students",
            category="wellbeing",
            created_by=counsellors_s2[1].user_id,
            questions=[
                {
                    "question_id": "q1",
                    "question_text": "How happy do you feel at school?",
                    "question_type": "rating_scale",
                    "required": True,
                    "min_value": 1,
                    "max_value": 5,
                    "answer_options": [
                        {"option_id": str(i), "text": str(i), "value": i} for i in range(1, 6)
                    ]
                },
                {
                    "question_id": "q2",
                    "question_text": "I have friends I can count on",
                    "question_type": "multiple_choice",
                    "required": True,
                    "answer_options": [
                        {"option_id": "strongly_disagree", "text": "Strongly Disagree", "value": 1},
                        {"option_id": "disagree", "text": "Disagree", "value": 2},
                        {"option_id": "neutral", "text": "Neutral", "value": 3},
                        {"option_id": "agree", "text": "Agree", "value": 4},
                        {"option_id": "strongly_agree", "text": "Strongly Agree", "value": 5}
                    ]
                }
            ],
            scoring_rules={
                "total_score": "sum_all",
                "low_wellbeing_threshold": 4
            }
        )
        
        db.add_all([template_phq9, template_gad7, template_stress, template_wellbeing])
        db.flush()
        print(f"✅ Created 4 assessment templates")
        
        # === ASSESSMENTS ===
        print("\n📝 Creating assessments...")
        assessments = []
        
        # School 1 Assessments (1 per class for all 10 classes)
        for class_obj in classes_s1:
            counsellor = random.choice(counsellors_s1)
            template = random.choice([template_phq9, template_gad7, template_stress, template_wellbeing])
            
            assessment = Assessment(
                template_id=template.template_id,
                school_id=school1.school_id,
                class_id=class_obj.class_id,
                title=f"{template.name} - {class_obj.name}",
                created_by=counsellor.user_id,
                notes=f"Assessment for {class_obj.name}"
            )
            assessments.append(assessment)
        
        # School 2 Assessments (1 per class for all 10 classes)
        for class_obj in classes_s2:
            counsellor = random.choice(counsellors_s2)
            template = random.choice([template_phq9, template_gad7, template_stress, template_wellbeing])
            
            assessment = Assessment(
                template_id=template.template_id,
                school_id=school2.school_id,
                class_id=class_obj.class_id,
                title=f"{template.name} - {class_obj.name}",
                created_by=counsellor.user_id,
                notes=f"Assessment for {class_obj.name}"
            )
            assessments.append(assessment)
        
        db.add_all(assessments)
        db.flush()
        print(f"✅ Created {len(assessments)} assessments")
        
        # === STUDENT RESPONSES ===
        print("\n✍️ Creating student responses...")
        responses = []
        
        # Create responses for some students in each assessment
        for assessment in assessments:
            # Get students from the class
            class_students = [s for s in all_students if s.class_id == assessment.class_id]
            # 40-60% of students complete the assessment (10-15 students per class of 25)
            responding_students = random.sample(class_students, min(len(class_students), random.randint(10, 15)))
            
            for student in responding_students:
                # Get template questions
                template = next((t for t in [template_phq9, template_gad7, template_stress, template_wellbeing] 
                               if t.template_id == assessment.template_id), None)
                
                if template:
                    for question in template.questions:
                        # Generate random response
                        if question["question_type"] == "rating_scale":
                            value = random.randint(question["min_value"], question["max_value"])
                            score = float(value)
                        elif question["question_type"] == "multiple_choice":
                            option = random.choice(question["answer_options"])
                            value = option["option_id"]
                            score = float(option["value"])
                        elif question["question_type"] == "yes_no":
                            value = random.choice([True, False])
                            score = 1.0 if value else 0.0
                        else:
                            value = 0
                            score = 0.0
                        
                        response = StudentResponse(
                            assessment_id=assessment.assessment_id,
                            student_id=student.student_id,
                            question_id=question["question_id"],
                            question_text=question["question_text"],
                            answer={"value": value},
                            score=score,
                            completed_at=datetime.utcnow() - timedelta(days=random.randint(1, 14))
                        )
                        responses.append(response)
        
        db.add_all(responses)
        db.flush()
        print(f"✅ Created {len(responses)} student responses")
        
        # === RESOURCES ===
        print("\n📚 Creating resources...")
        resources = []
        
        # Global Resources
        global_resources_data = [
            {
                "type": ResourceType.VIDEO,
                "title": "Understanding Anxiety in Teens",
                "description": "A comprehensive guide to recognizing and managing anxiety in adolescents.",
                "video_url": "https://example.com/videos/anxiety-teens.mp4",
                "thumbnail_url": "https://example.com/thumbnails/anxiety-teens.jpg",
                "author_name": "Dr. Emily Chen",
                "duration_seconds": 1200,
                "tags": ["anxiety", "teens", "mental-health", "coping-strategies"],
                "category": "anxiety",
                "target_audience": ["counsellors", "teachers", "parents"],
                "view_count": 245
            },
            {
                "type": ResourceType.VIDEO,
                "title": "Mindfulness Exercises for Students",
                "description": "Simple mindfulness techniques that students can practice daily.",
                "video_url": "https://example.com/videos/mindfulness-students.mp4",
                "thumbnail_url": "https://example.com/thumbnails/mindfulness.jpg",
                "author_name": "Sarah Johnson",
                "duration_seconds": 600,
                "tags": ["mindfulness", "meditation", "stress-relief", "self-care"],
                "category": "stress-management",
                "target_audience": ["students", "teachers"],
                "view_count": 189
            },
            {
                "type": ResourceType.AUDIO,
                "title": "Guided Meditation for Exam Stress",
                "description": "A calming guided meditation to help students manage exam anxiety.",
                "audio_url": "https://example.com/audio/exam-stress-meditation.mp3",
                "thumbnail_url": "https://example.com/thumbnails/meditation-audio.jpg",
                "author_name": "Lisa Anderson",
                "duration_seconds": 480,
                "tags": ["meditation", "exam-stress", "anxiety", "relaxation"],
                "category": "stress-management",
                "target_audience": ["students"],
                "view_count": 156
            },
            {
                "type": ResourceType.ARTICLE,
                "title": "10 Ways to Support a Student in Crisis",
                "description": "Practical strategies for teachers and counsellors to provide immediate support.",
                "article_url": "https://example.com/articles/support-student-crisis",
                "thumbnail_url": "https://example.com/thumbnails/crisis-support.jpg",
                "author_name": "Dr. Amanda Foster",
                "tags": ["crisis-intervention", "support", "teachers", "counselling"],
                "category": "crisis-intervention",
                "target_audience": ["counsellors", "teachers"],
                "view_count": 567
            }
        ]
        
        for data in global_resources_data:
            resource = Resource(
                school_id=None,
                status=ResourceStatus.PUBLISHED,
                posted_date=datetime.utcnow() - timedelta(days=random.randint(10, 60)),
                **data
            )
            resources.append(resource)
        
        # School 1 Specific Resources
        for i in range(3):
            resource = Resource(
                school_id=school1.school_id,
                type=random.choice([ResourceType.VIDEO, ResourceType.ARTICLE]),
                status=ResourceStatus.PUBLISHED,
                title=f"Lincoln High School - Resource {i+1}",
                description=f"School-specific resource for Lincoln High School students and staff.",
                video_url=f"https://example.com/videos/school1-resource{i+1}.mp4" if i % 2 == 0 else None,
                article_url=f"https://example.com/articles/school1-resource{i+1}" if i % 2 == 1 else None,
                thumbnail_url=f"https://example.com/thumbnails/school1-{i+1}.jpg",
                author_name="School Counselling Team",
                author_id=counsellors_s1[0].user_id,
                posted_date=datetime.utcnow() - timedelta(days=random.randint(5, 40)),
                duration_seconds=random.randint(300, 900) if i % 2 == 0 else None,
                tags=["school-services", "counselling", "resources"],
                category="school-specific",
                target_audience=["students", "parents"],
                view_count=random.randint(50, 150)
            )
            resources.append(resource)
        
        # School 2 Specific Resources
        for i in range(3):
            resource = Resource(
                school_id=school2.school_id,
                type=random.choice([ResourceType.VIDEO, ResourceType.ARTICLE]),
                status=ResourceStatus.PUBLISHED,
                title=f"Washington Academy - Resource {i+1}",
                description=f"School-specific resource for Washington Academy students and staff.",
                video_url=f"https://example.com/videos/school2-resource{i+1}.mp4" if i % 2 == 0 else None,
                article_url=f"https://example.com/articles/school2-resource{i+1}" if i % 2 == 1 else None,
                thumbnail_url=f"https://example.com/thumbnails/school2-{i+1}.jpg",
                author_name="Counseling Department",
                author_id=counsellors_s2[0].user_id,
                posted_date=datetime.utcnow() - timedelta(days=random.randint(5, 40)),
                duration_seconds=random.randint(300, 900) if i % 2 == 0 else None,
                tags=["school-services", "support", "resources"],
                category="school-specific",
                target_audience=["students", "parents"],
                view_count=random.randint(50, 150)
            )
            resources.append(resource)
        
        db.add_all(resources)
        db.flush()
        print(f"✅ Created {len(resources)} resources")
        
        # === ACTIVITIES ===
        print("\n🎯 Creating wellbeing activities...")
        activities = []
        
        # School 1 Activities
        activities_s1_data = [
            {
                "title": "Mindful Breathing Exercise",
                "description": "A simple breathing exercise to help students calm their minds and reduce anxiety.",
                "type": ActivityType.MINDFULNESS,
                "duration": 10,
                "target_grades": ["9", "10", "11", "12"],
                "materials": ["Quiet space", "Optional: calming music", "Timer"],
                "instructions": [
                    "Have students sit comfortably with feet flat on the floor",
                    "Ask them to close their eyes or look down gently",
                    "Guide them to breathe in slowly through the nose for 4 counts",
                    "Hold the breath for 4 counts",
                    "Exhale slowly through the mouth for 6 counts",
                    "Repeat for 5-10 cycles"
                ],
                "objectives": [
                    "Reduce stress and anxiety",
                    "Improve focus and concentration",
                    "Develop self-regulation skills"
                ]
            },
            {
                "title": "Active Listening Practice",
                "description": "Partner activity to develop active listening skills and empathy.",
                "type": ActivityType.SOCIAL_SKILLS,
                "duration": 20,
                "target_grades": ["9", "10", "11"],
                "materials": ["Timer", "Conversation prompt cards"],
                "instructions": [
                    "Pair students up with partners",
                    "Explain the roles: Speaker and Listener",
                    "Speaker shares for 3 minutes on a given topic",
                    "Listener practices active listening",
                    "Listener summarizes what they heard",
                    "Switch roles and repeat"
                ],
                "objectives": [
                    "Develop active listening skills",
                    "Practice empathy and understanding",
                    "Improve communication abilities"
                ]
            },
            {
                "title": "Emotion Thermometer",
                "description": "Visual tool to help students identify and manage their emotional intensity.",
                "type": ActivityType.EMOTIONAL_REGULATION,
                "duration": 15,
                "target_grades": ["9", "10", "11", "12"],
                "materials": ["Emotion thermometer printouts", "Colored markers"],
                "instructions": [
                    "Introduce the emotion thermometer concept (0-10 scale)",
                    "Discuss different emotions and their intensity levels",
                    "Have students identify their current emotion",
                    "Rate the intensity on their thermometer",
                    "Discuss coping strategies for different levels"
                ],
                "objectives": [
                    "Develop emotional awareness",
                    "Learn to rate emotional intensity",
                    "Practice self-regulation strategies"
                ]
            },
            {
                "title": "Growth Mindset Challenge",
                "description": "Activities to help students develop a growth mindset and overcome challenges.",
                "type": ActivityType.ACADEMIC_SUPPORT,
                "duration": 40,
                "target_grades": ["9", "10", "11", "12"],
                "materials": ["Growth mindset posters", "Challenge cards", "Reflection journals"],
                "instructions": [
                    "Introduce fixed vs. growth mindset concepts",
                    "Share examples of famous failures turned successes",
                    "Have students identify a current challenge",
                    "Reframe the challenge with growth mindset language",
                    "Create action steps to overcome the challenge"
                ],
                "objectives": [
                    "Develop growth mindset thinking",
                    "Reframe academic challenges positively",
                    "Build resilience and perseverance"
                ]
            },
            {
                "title": "Team Building Circle",
                "description": "Group activity to build trust and connection among students.",
                "type": ActivityType.TEAM_BUILDING,
                "duration": 25,
                "target_grades": ["9", "10", "11"],
                "materials": ["Open space", "Optional: music"],
                "instructions": [
                    "Have students stand in a circle",
                    "Each person shares something positive",
                    "Practice active listening as a group",
                    "Discuss teamwork and communication",
                    "Reflect on the experience"
                ],
                "objectives": [
                    "Practice teamwork and collaboration",
                    "Build trust and connection",
                    "Improve communication"
                ]
            }
        ]
        
        for data in activities_s1_data:
            activity = Activity(
                school_id=school1.school_id,
                created_by=counsellors_s1[0].user_id,
                **data
            )
            activities.append(activity)
        
        # School 2 Activities
        activities_s2_data = [
            {
                "title": "Body Scan Meditation",
                "description": "Guided meditation to help students release tension throughout their body.",
                "type": ActivityType.MINDFULNESS,
                "duration": 15,
                "target_grades": ["9", "10", "11", "12"],
                "materials": ["Comfortable seating or mats", "Quiet space"],
                "instructions": [
                    "Have students lie down or sit comfortably",
                    "Guide attention to the top of the head",
                    "Slowly move awareness down through each body part",
                    "Notice any tension or sensations without judgment",
                    "End at the toes, then bring awareness back"
                ],
                "objectives": [
                    "Increase body awareness",
                    "Release physical tension",
                    "Practice mindfulness"
                ]
            },
            {
                "title": "Compliment Circle",
                "description": "Positive group activity where students practice giving genuine compliments.",
                "type": ActivityType.SOCIAL_SKILLS,
                "duration": 25,
                "target_grades": ["9", "10", "11"],
                "materials": ["Circle seating arrangement"],
                "instructions": [
                    "Arrange students in a circle",
                    "Explain the importance of genuine compliments",
                    "Each student takes a turn in the center",
                    "Classmates share one genuine compliment",
                    "Reflect on how it felt to give and receive"
                ],
                "objectives": [
                    "Build self-esteem and confidence",
                    "Practice giving positive feedback",
                    "Strengthen classroom community"
                ]
            },
            {
                "title": "Coping Skills Toolbox",
                "description": "Students create a personalized collection of coping strategies.",
                "type": ActivityType.EMOTIONAL_REGULATION,
                "duration": 30,
                "target_grades": ["9", "10", "11", "12"],
                "materials": ["Boxes or containers", "Art supplies", "Coping strategy cards"],
                "instructions": [
                    "Discuss what coping skills are and why they're important",
                    "Brainstorm different types of coping strategies",
                    "Have students decorate their toolbox",
                    "Identify 5-10 personal coping strategies",
                    "Create visual reminders for each strategy"
                ],
                "objectives": [
                    "Identify personal coping strategies",
                    "Create tangible emotional support tools",
                    "Practice healthy stress management"
                ]
            },
            {
                "title": "Study Skills Workshop",
                "description": "Practical workshop teaching effective study techniques and time management.",
                "type": ActivityType.ACADEMIC_SUPPORT,
                "duration": 45,
                "target_grades": ["9", "10", "11", "12"],
                "materials": ["Planners or calendars", "Study technique handouts"],
                "instructions": [
                    "Assess current study habits with a quiz",
                    "Introduce various study techniques",
                    "Demonstrate effective note-taking",
                    "Practice time-blocking for assignments",
                    "Create a personalized study schedule"
                ],
                "objectives": [
                    "Learn effective study techniques",
                    "Improve time management skills",
                    "Reduce academic stress"
                ]
            },
            {
                "title": "Collaborative Art Project",
                "description": "Group creates a unified piece of art teaching cooperation and shared vision.",
                "type": ActivityType.TEAM_BUILDING,
                "duration": 35,
                "target_grades": ["9", "10", "11"],
                "materials": ["Large canvas or paper", "Various art supplies"],
                "instructions": [
                    "Divide class into groups of 4-6",
                    "Assign or let groups choose a theme",
                    "Each person gets a section to work on",
                    "Encourage discussion about overall vision",
                    "Complete the project together"
                ],
                "objectives": [
                    "Practice collaboration and compromise",
                    "Appreciate diverse perspectives",
                    "Work toward a shared goal"
                ]
            }
        ]
        
        for data in activities_s2_data:
            activity = Activity(
                school_id=school2.school_id,
                created_by=counsellors_s2[0].user_id,
                **data
            )
            activities.append(activity)
        
        db.add_all(activities)
        db.flush()
        print(f"✅ Created {len(activities)} wellbeing activities")
        
        # === COMMIT ALL CHANGES ===
        db.commit()
        
        # === PRINT SUMMARY ===
        print("\n" + "="*70)
        print("DATABASE SEEDED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📊 SUMMARY:")
        print(f"  ✅ 2 schools")
        print(f"  ✅ 2 principals")
        print(f"  ✅ 12 counsellors (6 per school)")
        print(f"  ✅ 24 teachers (12 per school)")
        print(f"  ✅ {len(parents_s1) + len(parents_s2)} parents ({len(parents_s1)} + {len(parents_s2)})")
        print(f"  ✅ {len(classes_s1) + len(classes_s2)} classes ({len(classes_s1)} + {len(classes_s2)})")
        print(f"  ✅ {len(all_students)} students ({len(students_s1)} + {len(students_s2)})")
        print(f"  ✅ {len(cases)} cases")
        print(f"  ✅ {len(journal_entries)} journal entries")
        print(f"  ✅ {len(observations)} observations")
        print(f"  ✅ 4 assessment templates")
        print(f"  ✅ {len(assessments)} assessments")
        print(f"  ✅ {len(responses)} student responses")
        print(f"  ✅ {len(resources)} resources")
        print(f"  ✅ {len(activities)} wellbeing activities")
        
        print(f"\n" + "="*70)
        print(f"SCHOOL DETAILS:")
        print("="*70)
        print(f"\n1. {school1.name} (ID: {school1.school_id})")
        print(f"   📍 Location: {school1.city}, {school1.state}")
        print(f"   👥 Staff: 1 Principal, 6 Counsellors, 12 Teachers, {len(parents_s1)} Parents")
        print(f"   📚 Classes: {len(classes_s1)} (25 students each)")
        print(f"   👨‍🎓 Students: {len(students_s1)}")
        print(f"   📋 Cases: {case_count_s1}")
        print(f"   👁️ Observations: {obs_count_s1}")
        
        print(f"\n2. {school2.name} (ID: {school2.school_id})")
        print(f"   📍 Location: {school2.city}, {school2.state}")
        print(f"   👥 Staff: 1 Principal, 6 Counsellors, 12 Teachers, {len(parents_s2)} Parents")
        print(f"   📚 Classes: {len(classes_s2)} (25 students each)")
        print(f"   👨‍🎓 Students: {len(students_s2)}")
        print(f"   📋 Cases: {case_count_s2}")
        print(f"   👁️ Observations: {obs_count_s2}")
        
        print(f"\n" + "="*70)
        print(f"LOGIN CREDENTIALS (Password: password123):")
        print("="*70)
        print(f"\n🏫 School 1 - {school1.name}:")
        print(f"   Principal: principal@lincoln.edu")
        print(f"   Counsellor: counsellor1@lincoln.edu")
        print(f"   Teacher: teacher1@lincoln.edu")
        print(f"   Parent: {parents_s1[0].email if parents_s1 else 'N/A'}")
        
        print(f"\n🏫 School 2 - {school2.name}:")
        print(f"   Principal: principal@washington.edu")
        print(f"   Counsellor: counsellor1@washington.edu")
        print(f"   Teacher: teacher1@washington.edu")
        print(f"   Parent: {parents_s2[0].email if parents_s2 else 'N/A'}")
        
        print(f"\n" + "="*70)
        print(f"✨ Database seeding completed successfully!")
        print("="*70 + "\n")
        
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
