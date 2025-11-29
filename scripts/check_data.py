from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.activity import Activity
from app.models.class_model import Class
from app.models.user import User, UserRole
from app.models.student import Student

# Setup DB connection
engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def check_data():
    print("--- Checking Data ---")
    
    # Get a Teacher
    teacher = db.query(User).filter(User.role == UserRole.TEACHER).first()
    if teacher:
        print(f"Teacher found: {teacher.display_name} ({teacher.user_id})")
    else:
        print("No Teacher found!")
        return

    # Get a Class taught by this teacher (or any class if not assigned)
    class_obj = db.query(Class).filter(Class.teacher_id == teacher.user_id).first()
    if not class_obj:
        class_obj = db.query(Class).first()
    
    if class_obj:
        print(f"Class found: {class_obj.name} ({class_obj.class_id})")
    else:
        print("No Class found!")
        return

    # Get Students in this class
    students = db.query(Student).filter(Student.class_id == class_obj.class_id).all()
    print(f"Students in class: {len(students)}")
    if students:
        print(f"Sample Student: {students[0].first_name} ({students[0].student_id})")

    # Get an Activity
    activity = db.query(Activity).first()
    if activity:
        print(f"Activity found: {activity.title} ({activity.activity_id})")
    else:
        print("No Activity found!")

if __name__ == "__main__":
    check_data()
