from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.activity import Activity
from app.models.class_model import Class
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.activity_assignment import ActivityAssignment, AssignmentStatus
from app.models.activity_submission import ActivitySubmission, SubmissionStatus, FileType
from datetime import datetime, timedelta
import uuid
import random

# Setup DB connection
engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed_activities():
    print("--- Seeding Comprehensive Activity Data ---")
    
    # 1. Get required entities
    teacher = db.query(User).filter(User.role == UserRole.TEACHER).first()
    if not teacher:
        print("No Teacher found! Aborting.")
        return

    classes = db.query(Class).filter(Class.teacher_id == teacher.user_id).all()
    if not classes:
        print("Teacher has no classes. Fetching all classes.")
        classes = db.query(Class).all()
    
    activities = db.query(Activity).all()
    
    if not classes or not activities:
        print("Missing Classes or Activities. Aborting.")
        return

    print(f"Found {len(classes)} classes and {len(activities)} activities.")

    count_assignments = 0
    count_submissions = 0

    # 2. Loop through classes and activities
    for class_obj in classes:
        students = db.query(Student).filter(Student.class_id == class_obj.class_id).all()
        if not students:
            print(f"Skipping class {class_obj.name} (No students)")
            continue

        # Assign random 3-5 activities to each class
        selected_activities = random.sample(activities, min(len(activities), random.randint(3, 5)))
        
        for activity in selected_activities:
            # Check if assignment already exists
            existing = db.query(ActivityAssignment).filter(
                ActivityAssignment.class_id == class_obj.class_id,
                ActivityAssignment.activity_id == activity.activity_id
            ).first()
            
            if existing:
                continue

            # Create Assignment
            assignment = ActivityAssignment(
                assignment_id=uuid.uuid4(),
                activity_id=activity.activity_id,
                class_id=class_obj.class_id,
                assigned_by=teacher.user_id,
                due_date=datetime.utcnow() + timedelta(days=random.randint(-5, 14)), # Some past due, some future
                status=AssignmentStatus.ACTIVE,
                created_at=datetime.utcnow()
            )
            db.add(assignment)
            count_assignments += 1

            # Create Submissions
            for student in students:
                # 80% chance a student has interacted with the assignment
                if random.random() > 0.2:
                    status = SubmissionStatus.PENDING
                    file_url = None
                    file_type = None
                    submitted_at = None
                    feedback = None
                    
                    rand = random.random()
                    # 40% Verified, 30% Submitted, 30% Pending (if interacted)
                    if rand > 0.6:
                        status = SubmissionStatus.VERIFIED
                        file_url = "https://placehold.co/600x400/png"
                        file_type = FileType.IMAGE
                        submitted_at = datetime.utcnow() - timedelta(days=random.randint(1, 5))
                        feedback = random.choice([
                            "Great work!", "Well done.", "Excellent effort.", "Good job, keep it up!"
                        ])
                    elif rand > 0.3:
                        status = SubmissionStatus.SUBMITTED
                        file_url = "https://placehold.co/600x400/png"
                        file_type = FileType.IMAGE
                        submitted_at = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
                    
                    # If status is PENDING, we just create the record as a placeholder (or not create it? 
                    # The current logic assumes PENDING means 'assigned but not submitted' if we create it.
                    # But usually PENDING submissions are created when assignment is made.
                    # Let's create it for all students, but update status for some.
                    
                    submission = ActivitySubmission(
                        submission_id=uuid.uuid4(),
                        assignment_id=assignment.assignment_id,
                        student_id=student.student_id,
                        file_url=file_url,
                        file_type=file_type,
                        status=status,
                        feedback=feedback,
                        submitted_at=submitted_at,
                        created_at=datetime.utcnow()
                    )
                    db.add(submission)
                    count_submissions += 1
                else:
                    # 20% students haven't even started (Pending, no submission record? 
                    # Or Pending record? The dashboard expects records.
                    # Let's create PENDING record for everyone to be safe, as per my logic in dashboard)
                    submission = ActivitySubmission(
                        submission_id=uuid.uuid4(),
                        assignment_id=assignment.assignment_id,
                        student_id=student.student_id,
                        status=SubmissionStatus.PENDING,
                        created_at=datetime.utcnow()
                    )
                    db.add(submission)
                    count_submissions += 1

    db.commit()
    print(f"Seeding Complete! Created {count_assignments} assignments and {count_submissions} submissions.")

if __name__ == "__main__":
    seed_activities()
