from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from app.core.config import settings
from app.models.activity_assignment import ActivityAssignment
from app.models.activity import Activity
import uuid

# Setup DB connection
engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def verify_relationship():
    print("--- Verifying Activity Assignment Relationship ---")
    
    # Get an assignment
    assignment = db.query(ActivityAssignment).options(
        joinedload(ActivityAssignment.activity)
    ).first()
    
    if not assignment:
        print("No assignments found.")
        return

    print(f"Assignment ID: {assignment.assignment_id}")
    print(f"Activity ID: {assignment.activity_id}")
    
    if assignment.activity:
        print(f"Activity Title: {assignment.activity.title}")
        print("Relationship is working!")
    else:
        print("Activity relationship is None!")
        # Check if activity exists manually
        activity = db.query(Activity).filter(Activity.activity_id == assignment.activity_id).first()
        if activity:
            print(f"Activity exists in DB: {activity.title}")
        else:
            print("Activity does NOT exist in DB (Foreign Key violation?)")

if __name__ == "__main__":
    verify_relationship()
