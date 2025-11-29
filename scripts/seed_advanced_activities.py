from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.activity import Activity, ActivityType
from app.models.user import User, UserRole
from app.models.school import School
from datetime import datetime
import uuid

# Setup DB connection
engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed_advanced_activities():
    """Create advanced activities for counselors only"""
    print("--- Seeding Advanced Counselor Activities ---")
    
    # Get all schools
    schools = db.query(School).all()
    if not schools:
        print("No schools found! Aborting.")
        return
        
    print(f"Found {len(schools)} schools. Creating advanced activities for each...")
    
    total_created = 0
    
    # Advanced activities data
    advanced_activities = [
        {
            "title": "CBT Deep Dive: Cognitive Restructuring",
            "description": "Advanced cognitive behavioral therapy techniques for identifying and challenging cognitive distortions.",
            "type": ActivityType.COGNITIVE_DEVELOPMENT,
            "duration": 60,
            "target_grades": ["6", "7", "8", "9", "10", "11", "12"],
            "diagnosis": ["ANXIETY_DISORDERS", "DEPRESSION"],
            "materials": ["CBT Worksheets", "Thought Records", "Whiteboard"],
            "instructions": [
                "Explain the cognitive triangle (Thoughts, Feelings, Behaviors)",
                "Identify automatic negative thoughts",
                "Look for evidence for and against the thought",
                "Develop a balanced alternative thought"
            ],
            "objectives": [
                "Master cognitive restructuring techniques",
                "Reduce intensity of negative emotions",
                "Develop long-term coping mechanisms"
            ]
        },
        {
            "title": "Trauma Processing: Narrative Exposure",
            "description": "Structured approach to processing traumatic memories through narrative exposure therapy techniques.",
            "type": ActivityType.SOCIAL_EMOTIONAL_DEVELOPMENT,
            "duration": 90,
            "target_grades": ["8", "9", "10", "11", "12"],
            "diagnosis": ["TRAUMA_PTSD"],
            "materials": ["Timeline paper", "Markers", "Safe space objects"],
            "instructions": [
                "Establish safety and grounding",
                "Create a lifeline of life events",
                "Identify traumatic hotspots",
                "Begin narrative construction with support"
            ],
            "objectives": [
                "Integrate traumatic memories",
                "Reduce avoidance behaviors",
                "Reclaim personal narrative"
            ]
        },
        {
            "title": "DBT Skills: Distress Tolerance",
            "description": "Intensive training in Dialectical Behavior Therapy skills for managing crisis situations.",
            "type": ActivityType.SOCIAL_EMOTIONAL_DEVELOPMENT,
            "duration": 60,
            "target_grades": ["7", "8", "9", "10", "11", "12"],
            "diagnosis": ["ANXIETY_DISORDERS", "DEPRESSION", "TRAUMA_PTSD"],
            "materials": ["Ice packs", "Sensory kit", "DBT handouts"],
            "instructions": [
                "Teach TIPP skills (Temperature, Intense exercise, Paced breathing, Paired muscle relaxation)",
                "Practice self-soothing with five senses",
                "Role-play crisis scenarios",
                "Create a crisis survival plan"
            ],
            "objectives": [
                "Survive crisis situations without making them worse",
                "Regulate extreme emotions",
                "Increase distress tolerance threshold"
            ]
        },
        {
            "title": "Advanced Social Skills: Nuance & Context",
            "description": "High-level social skills training focusing on non-verbal cues, sarcasm, and complex social dynamics.",
            "type": ActivityType.SOCIAL_EMOTIONAL_DEVELOPMENT,
            "duration": 45,
            "target_grades": ["6", "7", "8", "9", "10"],
            "diagnosis": ["AUTISM_SPECTRUM_DISORDER", "ADHD"],
            "materials": ["Video clips", "Scenario cards", "Role-play scripts"],
            "instructions": [
                "Analyze video clips for subtle social cues",
                "Discuss context-dependent behaviors",
                "Practice interpreting tone of voice and sarcasm",
                "Role-play complex social conflicts"
            ],
            "objectives": [
                "Interpret subtle non-verbal communication",
                "Navigate complex social hierarchies",
                "Understand context and nuance"
            ]
        }
    ]
    
    # Iterate through each school
    for school in schools:
        print(f"Processing school: {school.name}")
        
        # Find a counselor for this school
        creator = db.query(User).filter(
            User.school_id == school.school_id,
            User.role == UserRole.COUNSELLOR
        ).first()
        
        if not creator:
            # Fallback to any user if no counselor (shouldn't happen in prod but possible in dev)
            creator = db.query(User).filter(User.school_id == school.school_id).first()
            
        if not creator:
            print(f"  - No user found for school {school.name}. Skipping.")
            continue
            
        # Create activities
        school_count = 0
        for activity_data in advanced_activities:
            # Check if activity already exists
            existing = db.query(Activity).filter(
                Activity.school_id == school.school_id,
                Activity.title == activity_data["title"]
            ).first()
            
            if existing:
                # Ensure it's marked as counselor only
                if not existing.is_counselor_only:
                    existing.is_counselor_only = True
                    db.add(existing)
                    print(f"    - Updated existing activity to be counselor-only: {activity_data['title']}")
                continue
            
            activity = Activity(
                activity_id=uuid.uuid4(),
                school_id=school.school_id,
                title=activity_data["title"],
                description=activity_data["description"],
                type=activity_data["type"],
                duration=activity_data["duration"],
                target_grades=activity_data["target_grades"],
                diagnosis=activity_data["diagnosis"],
                materials=activity_data.get("materials", []),
                instructions=activity_data.get("instructions", []),
                objectives=activity_data.get("objectives", []),
                is_counselor_only=True,  # MARK AS COUNSELOR ONLY
                created_by=creator.user_id,
                created_at=datetime.utcnow()
            )
            db.add(activity)
            school_count += 1
            total_created += 1
            
        print(f"  - Created {school_count} advanced activities for {school.name}")
    
    db.commit()
    print(f"✅ Total created: {total_created} advanced counselor activities")

if __name__ == "__main__":
    seed_advanced_activities()
    db.close()
