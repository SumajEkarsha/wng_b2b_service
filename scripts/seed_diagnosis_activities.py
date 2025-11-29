from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.activity import Activity, ActivityType
from app.models.user import User, UserRole
from datetime import datetime
import uuid

from app.models.school import School

# Setup DB connection
engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed_diagnosis_activities():
    """Create activities with diagnosis categories for ALL schools"""
    print("--- Seeding Diagnosis-Based Activities for ALL Schools ---")
    
    # 1. Get all schools
    schools = db.query(School).all()
    if not schools:
        print("No schools found! Aborting.")
        return
        
    print(f"Found {len(schools)} schools. Creating activities for each...")
    
    total_created = 0
    
    # Diagnosis categories
    diagnosis_categories = {
        "SPECIAL_NEEDS": [
            "VISUAL_IMPAIRMENT",
            "HEARING_IMPAIRMENT",
            "INTELLECTUAL_DISABILITIES",
            "LEARNING_DISABILITIES"
        ],
        "MENTAL_HEALTH": [
            "ANXIETY_DISORDERS",
            "DEPRESSION",
            "ADHD",
            "TRAUMA_PTSD",
            "AUTISM_SPECTRUM_DISORDER"
        ]
    }
    
    # Sample activities with diagnosis tags
    diagnosis_activities = [
        # Visual Impairment Activities
        {
            "title": "Audio Description Theater",
            "description": "Develop descriptive listening skills through audio storytelling and theater activities.",
            "type": ActivityType.LANGUAGE_COMMUNICATION_DEVELOPMENT,
            "duration": 45,
            "target_grades": ["3", "4", "5"],
            "diagnosis": ["VISUAL_IMPAIRMENT"],
            "materials": ["Audio books", "Soundscape recordings", "Braille scripts"],
            "instructions": [
                "Play audio story or scene",
                "Students describe what they hear",
                "Discuss imagery created by sound",
                "Students create their own audio descriptions"
            ],
            "objectives": [
                "Enhance auditory processing skills",
                "Develop descriptive language",
                "Build confidence in verbal communication"
            ]
        },
        {
            "title": "Tactile Art Exploration",
            "description": "Create and explore art through touch using textured materials.",
            "type": ActivityType.COGNITIVE_DEVELOPMENT,
            "duration": 50,
            "target_grades": ["1", "2", "3", "4"],
            "diagnosis": ["VISUAL_IMPAIRMENT"],
            "materials": ["Textured fabrics", "Clay", "Sandpaper", "String"],
            "instructions": [
                "Present various textured materials",
                "Students explore textures through touch",
                "Create tactile collages or sculptures",
                "Students describe their creations"
            ],
            "objectives": [
                "Develop tactile discrimination",
                "Encourage creative expression",
                "Build fine motor skills"
            ]
        },
        
        # Hearing Impairment Activities
        {
            "title": "Visual Communication Games",
            "description": "Learn and practice visual communication through games and activities.",
            "type": ActivityType.SOCIAL_EMOTIONAL_DEVELOPMENT,
            "duration": 40,
            "target_grades": ["2", "3", "4", "5"],
            "diagnosis": ["HEARING_IMPAIRMENT"],
            "materials": ["Picture cards", "Sign language posters", "Mirrors"],
            "instructions": [
                "Teach basic sign language gestures",
                "Play charades with visual cues",
                "Practice facial expressions",
                "Group communication games"
            ],
            "objectives": [
                "Develop non-verbal communication skills",
                "Build confidence in expression",
                "Promote social interaction"
            ]
        },
        {
            "title": "Vibration and Rhythm Music",
            "description": "Experience music through vibration and visual rhythm patterns.",
            "type": ActivityType.PHYSICAL_DEVELOPMENT,
            "duration": 45,
            "target_grades": ["1", "2", "3"],
            "diagnosis": ["HEARING_IMPAIRMENT"],
            "materials": ["Drums", "Balloons", "Rhythm cards", "Vibration speakers"],
            "instructions": [
                "Feel vibrations from instruments",
                "Follow visual rhythm patterns",
                "Create rhythm with body movements",
                "Group synchronized activities"
            ],
            "objectives": [
                "Experience music through alternative senses",
                "Develop rhythm awareness",
                "Promote gross motor coordination"
            ]
        },
        
        # Intellectual Disabilities Activities
        {
            "title": "Daily Life Skills Practice",
            "description": "Build independence through practiced daily living skills.",
            "type": ActivityType.COGNITIVE_DEVELOPMENT,
            "duration": 60,
            "target_grades": ["4", "5", "6", "7"],
            "diagnosis": ["INTELLECTUAL_DISABILITIES"],
            "materials": ["Practice items", "Visual schedules", "Step-by-step cards"],
            "instructions": [
                "Break tasks into small steps",
                "Use visual supports",
                "Practice with repetition",
                "Celebrate progress"
            ],
            "objectives": [
                "Build independent living skills",
                "Increase self-confidence",
                "Develop sequencing abilities"
            ]
        },
        
        # Learning Disabilities Activities
        {
            "title": "Multi-Sensory Reading",
            "description": "Enhance reading comprehension through multi-sensory techniques.",
            "type": ActivityType.LANGUAGE_COMMUNICATION_DEVELOPMENT,
            "duration": 45,
            "target_grades": ["2", "3", "4"],
            "diagnosis": ["LEARNING_DISABILITIES"],
            "materials": ["Textured letters", "Colored overlays", "Audio books", "Highlighters"],
            "instructions": [
                "Trace letters while saying sounds",
                "Use colored overlays for text",
                "Listen and follow along",
                "Highlight key words"
            ],
            "objectives": [
                "Improve reading fluency",
                "Enhance comprehension",
                "Build confidence in literacy"
            ]
        },
        
        # Anxiety Disorders Activities
        {
            "title": "Calm Corner Breathing Exercises",
            "description": "Learn and practice breathing techniques to manage anxiety.",
            "type": ActivityType.SOCIAL_EMOTIONAL_DEVELOPMENT,
            "duration": 20,
            "target_grades": ["1", "2", "3", "4", "5"],
            "diagnosis": ["ANXIETY_DISORDERS"],
            "materials": ["Breathing visual aids", "Calm music", "Soft cushions"],
            "instructions": [
                "Find comfortable position",
                "Practice deep breathing (4-7-8)",
                "Use belly breathing technique",
                "Visualize calm place"
            ],
            "objectives": [
                "Reduce anxiety symptoms",
                "Build self-regulation skills",
                "Create coping strategies"
            ]
        },
        {
            "title": "Worry Box Activity",
            "description": "Express and manage worries through creative journaling.",
            "type": ActivityType.SOCIAL_EMOTIONAL_DEVELOPMENT,
            "duration": 30,
            "target_grades": ["3", "4", "5", "6"],
            "diagnosis": ["ANXIETY_DISORDERS"],
            "materials": ["Worry box", "Paper", "Colored pencils", "Stickers"],
            "instructions": [
                "Write or draw worries",
                "Place in worry box",
                "Discuss how to address concerns",
                "Create action plan"
            ],
            "objectives": [
                "Externalize anxious thoughts",
                "Develop problem-solving skills",
                "Build emotional awareness"
            ]
        },
        
        # Depression Activities
        {
            "title": "Gratitude Journal",
            "description": "Build positive thinking through daily gratitude practice.",
            "type": ActivityType.SOCIAL_EMOTIONAL_DEVELOPMENT,
            "duration": 15,
            "target_grades": ["4", "5", "6", "7", "8"],
            "diagnosis": ["DEPRESSION"],
            "materials": ["Journals", "Pens", "Stickers", "Inspiring quotes"],
            "instructions": [
                "Write three things you're grateful for",
                "Draw or decorate page",
                "Share one gratitude with partner",
                "Reflect on positive moments"
            ],
            "objectives": [
                "Shift focus to positive experiences",
                "Build awareness of good moments",
                "Develop optimistic thinking"
            ]
        },
        {
            "title": "Movement and Expression",
            "description": "Use physical movement to boost mood and energy.",
            "type": ActivityType.PHYSICAL_DEVELOPMENT,
            "duration": 30,
            "target_grades": ["3", "4", "5", "6"],
            "diagnosis": ["DEPRESSION"],
            "materials": ["Music player", "Space for movement", "Scarves or ribbons"],
            "instructions": [
                "Start with gentle stretching",
                "Move to upbeat music",
                "Express emotions through movement",
                "End with relaxation"
            ],
            "objectives": [
                "Increase physical activity",
                "Boost mood through movement",
                "Provide emotional outlet"
            ]
        },
        
        # ADHD Activities
        {
            "title": "Focus Game Stations",
            "description": "Improve attention and focus through structured game activities.",
            "type": ActivityType.COGNITIVE_DEVELOPMENT,
            "duration": 40,
            "target_grades": ["2", "3", "4", "5"],
            "diagnosis": ["ADHD"],
            "materials": ["Timers", "Focus games", "Movement breaks", "Visual schedules"],
            "instructions": [
                "Set timer for focused work",
                "Rotate through game stations",
                "Take movement breaks",
                "Track progress on chart"
            ],
            "objectives": [
                "Build sustained attention",
                "Develop self-monitoring skills",
                "Learn to manage energy"
            ]
        },
        {
            "title": "Mindful Movement Activities",
            "description": "Channel energy positively through mindful physical activities.",
            "type": ActivityType.PHYSICAL_DEVELOPMENT,
            "duration": 25,
            "target_grades": ["1", "2", "3", "4"],
            "diagnosis": ["ADHD"],
            "materials": ["Yoga mats", "Balance boards", "Therapy balls"],
            "instructions": [
                "Start with body awareness",
                "Practice controlled movements",
                "Use balance activities",
                "End with calming exercise"
            ],
            "objectives": [
                "Develop body awareness",
                "Practice impulse control",
                "Channel energy constructively"
            ]
        },
        
        # Trauma/PTSD Activities
        {
            "title": "Safe Space Creation",
            "description": "Design and create a personal safe space for regulation.",
            "type": ActivityType.SOCIAL_EMOTIONAL_DEVELOPMENT,
            "duration": 45,
            "target_grades": ["3", "4", "5", "6", "7"],
            "diagnosis": ["TRAUMA_PTSD"],
            "materials": ["Soft materials", "Calming objects", "Art supplies", "Photos"],
            "instructions": [
                "Identify what makes you feel safe",
                "Gather comforting items",
                "Create personal safe space",
                "Practice using space when upset"
            ],
            "objectives": [
                "Develop self-regulation strategies",
                "Create sense of safety",
                "Build coping resources"
            ]
        },
        
        # Autism Spectrum Disorder Activities
        {
            "title": "Social Stories Practice",
            "description": "Learn social situations through structured visual stories.",
            "type": ActivityType.SOCIAL_EMOTIONAL_DEVELOPMENT,
            "duration": 30,
            "target_grades": ["1", "2", "3", "4"],
            "diagnosis": ["AUTISM_SPECTRUM_DISORDER"],
            "materials": ["Social story books", "Visual cards", "Role-play props"],
            "instructions": [
                "Read social story together",
                "Discuss key points",
                "Role-play situation",
                "Practice in real context"
            ],
            "objectives": [
                "Understand social expectations",
                "Build social skills",
                "Reduce anxiety in social situations"
            ]
        },
        {
            "title": "Sensory Integration Activities",
            "description": "Explore and regulate sensory experiences through structured activities.",
            "type": ActivityType.PHYSICAL_DEVELOPMENT,
            "duration": 35,
            "target_grades": ["1", "2", "3", "4", "5"],
            "diagnosis": ["AUTISM_SPECTRUM_DISORDER"],
            "materials": ["Sensory bins", "Weighted items", "Textured materials", "Fidgets"],
            "instructions": [
                "Explore different textures",
                "Use weighted items for calming",
                "Practice sensory breaks",
                "Track sensory preferences"
            ],
            "objectives": [
                "Develop sensory awareness",
                "Learn self-regulation",
                "Build sensory vocabulary"
            ]
        }
    ]
    
    # 2. Iterate through each school
    for school in schools:
        print(f"Processing school: {school.name} ({school.school_id})")
        
        # Find a creator for this school (Teacher or Counselor)
        creator = db.query(User).filter(
            User.school_id == school.school_id,
            User.role.in_([UserRole.COUNSELLOR, UserRole.TEACHER])
        ).first()
        
        if not creator:
            print(f"  - No Teacher or Counselor found for school {school.name}. Skipping.")
            continue
            
        print(f"  - Using creator: {creator.display_name} ({creator.role})")
        
        # Create activities for this school
        school_count = 0
        for activity_data in diagnosis_activities:
            # Check if activity already exists for this school
            existing = db.query(Activity).filter(
                Activity.school_id == school.school_id,
                Activity.title == activity_data["title"]
            ).first()
            
            if existing:
                # Update existing activity with diagnosis if missing
                if not existing.diagnosis:
                    existing.diagnosis = activity_data["diagnosis"]
                    db.add(existing)
                    print(f"    - Updated diagnosis for existing activity: {activity_data['title']}")
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
                created_by=creator.user_id,
                created_at=datetime.utcnow()
            )
            db.add(activity)
            school_count += 1
            total_created += 1
        
        print(f"  - Created {school_count} new activities for {school.name}")
    
    db.commit()
    print(f"✅ Total created: {total_created} diagnosis-based activities across all schools")

if __name__ == "__main__":
    seed_diagnosis_activities()
    db.close()
