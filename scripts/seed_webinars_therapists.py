"""
Seed data for webinars and therapists tables
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.webinar import Webinar, WebinarCategory, WebinarStatus, WebinarLevel
from app.models.therapist import Therapist, AvailabilityStatus

def seed_webinars(session):
    """Create sample webinars"""
    print("🎓 Creating sample webinars...")
    
    webinars_data = [
        {
            "title": "Building Resilience in Students",
            "description": "Learn evidence-based strategies to help students develop resilience and cope with challenges effectively.",
            "speaker_name": "Dr. Sarah Johnson",
            "speaker_title": "Clinical Psychologist",
            "speaker_bio": "Dr. Johnson has 15 years of experience in child psychology and resilience training.",
            "speaker_image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop",
            "thumbnail_url": "https://images.unsplash.com/photo-1516534775068-ba3e7458af70?w=800&h=400&fit=crop",
            "date": datetime.now() + timedelta(days=7),
            "duration_minutes": 90,
            "category": WebinarCategory.STUDENT_WELLBEING,
            "status": WebinarStatus.UPCOMING,
            "level": WebinarLevel.BEGINNER,
            "price": Decimal("0.00"),
            "topics": ["Stress Management", "Coping Skills", "Growth Mindset", "Emotional Regulation"],
            "max_attendees": 100,
            "attendee_count": 45,
            "views": 1420
        },
        {
            "title": "Trauma-Informed Counseling Practices",
            "description": "Comprehensive training on trauma-informed approaches in school counseling settings.",
            "speaker_name": "Prof. Michael Chen",
            "speaker_title": "Professor of Psychology",
            "speaker_bio": "Leading expert in trauma-informed care with 20+ years of experience.",
            "speaker_image_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop",
            "thumbnail_url": "https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?w=800&h=400&fit=crop",
            "date": datetime.now() + timedelta(days=14),
            "duration_minutes": 120,
            "category": WebinarCategory.PROFESSIONAL_DEVELOPMENT,
            "status": WebinarStatus.UPCOMING,
            "level": WebinarLevel.INTERMEDIATE,
            "price": Decimal("299.00"),
            "topics": ["Trauma Recognition", "Safe Spaces", "Therapeutic Techniques", "Self-Care"],
            "max_attendees": 75,
            "attendee_count": 32,
            "views": 2650
        },
        {
            "title": "Managing Anxiety in the Classroom",
            "description": "Practical strategies for identifying and supporting students experiencing anxiety.",
            "speaker_name": "Dr. Priya Sharma",
            "speaker_title": "Child Psychologist",
            "speaker_image_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=400&fit=crop",
            "thumbnail_url": "https://images.unsplash.com/photo-1588072432836-e10032774350?w=800&h=400&fit=crop",
            "date": datetime.now() - timedelta(days=2),
            "duration_minutes": 60,
            "category": WebinarCategory.MENTAL_HEALTH,
            "status": WebinarStatus.RECORDED,
            "level": WebinarLevel.BEGINNER,
            "price": Decimal("199.00"),
            "topics": ["Anxiety Symptoms", "Intervention Strategies", "Classroom Accommodations"],
            "video_url": "https://example.com/recordings/anxiety-management",
            "attendee_count": 89,
            "views": 288
        },
        {
            "title": "Suicide Prevention & Intervention",
            "description": "Critical training on recognizing warning signs and implementing effective intervention protocols.",
            "speaker_name": "Dr. Rajesh Kumar",
            "speaker_title": "Crisis Intervention Specialist",
            "speaker_image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop",
            "thumbnail_url": "https://images.unsplash.com/photo-1505142468610-359e7d316be0?w=800&h=400&fit=crop",
            "date": datetime.now() + timedelta(days=10),
            "duration_minutes": 120,
            "category": WebinarCategory.CRISIS_MANAGEMENT,
            "status": WebinarStatus.UPCOMING,
            "level": WebinarLevel.ADVANCED,
            "price": Decimal("0.00"),
            "topics": ["Warning Signs", "Risk Assessment", "Safety Planning", "Follow-up Care"],
            "max_attendees": 150,
            "attendee_count": 127,
            "views": 3420
        },
        {
            "title": "Effective Parent-Counselor Communication",
            "description": "Master the art of communicating sensitive mental health information to parents.",
            "speaker_name": "Dr. Meera Iyer",
            "speaker_title": "Family Therapist",
            "speaker_image_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop",
            "thumbnail_url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&h=400&fit=crop",
            "date": datetime.now() + timedelta(days=12),
            "duration_minutes": 60,
            "category": WebinarCategory.COMMUNICATION,
            "status": WebinarStatus.UPCOMING,
            "level": WebinarLevel.BEGINNER,
            "price": Decimal("0.00"),
            "topics": ["Difficult Conversations", "Cultural Sensitivity", "Collaboration Strategies"],
            "max_attendees": 200,
            "attendee_count": 156,
            "views": 4200
        },
        {
            "title": "Mindfulness & Self-Care for Counselors",
            "description": "Essential self-care practices to prevent burnout and maintain professional effectiveness.",
            "speaker_name": "Dr. Kabir Singh",
            "speaker_title": "Wellness Coach",
            "speaker_image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop",
            "thumbnail_url": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&h=400&fit=crop",
            "date": datetime.now() - timedelta(days=5),
            "duration_minutes": 90,
            "category": WebinarCategory.SELF_CARE,
            "status": WebinarStatus.RECORDED,
            "level": WebinarLevel.ALL_LEVELS,
            "price": Decimal("199.00"),
            "topics": ["Burnout Prevention", "Mindfulness Techniques", "Work-Life Balance"],
            "video_url": "https://example.com/recordings/mindfulness-self-care",
            "attendee_count": 94,
            "views": 3500
        },
        {
            "title": "Understanding ADHD in Schools",
            "description": "Comprehensive overview of ADHD identification, support strategies, and accommodations.",
            "speaker_name": "Dr. Vikram Mehta",
            "speaker_title": "Learning Disabilities Expert",
            "speaker_image_url": "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=400&h=400&fit=crop",
            "thumbnail_url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=800&h=400&fit=crop",
            "date": datetime.now() - timedelta(days=8),
            "duration_minutes": 75,
            "category": WebinarCategory.LEARNING_DISABILITIES,
            "status": WebinarStatus.RECORDED,
            "level": WebinarLevel.BEGINNER,
            "price": Decimal("249.00"),
            "topics": ["ADHD Types", "Behavioral Strategies", "Academic Support"],
            "video_url": "https://example.com/recordings/adhd-understanding",
            "attendee_count": 67,
            "views": 1800
        },
        {
            "title": "Creating Safe Spaces for LGBTQ+ Students",
            "description": "Learn how to create inclusive, supportive environments for LGBTQ+ students.",
            "speaker_name": "Dr. Sneha Patel",
            "speaker_title": "Diversity & Inclusion Counselor",
            "speaker_image_url": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=400&h=400&fit=crop",
            "thumbnail_url": "https://images.unsplash.com/photo-1511632765486-a01980e01a18?w=800&h=400&fit=crop",
            "date": datetime.now() + timedelta(days=20),
            "duration_minutes": 90,
            "category": WebinarCategory.INCLUSION,
            "status": WebinarStatus.UPCOMING,
            "level": WebinarLevel.INTERMEDIATE,
            "price": Decimal("299.00"),
            "topics": ["Identity Development", "Coming Out Support", "Anti-Bullying", "Ally Training"],
            "max_attendees": 100,
            "attendee_count": 43,
            "views": 2200
        }
    ]
    
    for data in webinars_data:
        webinar = Webinar(
            webinar_id=uuid.uuid4(),
            **data
        )
        session.add(webinar)
    
    session.commit()
    print(f"✅ Created {len(webinars_data)} webinars")

def seed_therapists(session):
    """Create sample therapists"""
    print("👨‍⚕️ Creating sample therapists...")
    
    therapists_data = [
        {
            "name": "Dr. Anjali Gupta",
            "specialty": "Child Psychology",
            "bio": "Specialized in working with children and adolescents dealing with anxiety and trauma.",
            "profile_image_url": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&h=400&fit=crop",
            "rating": Decimal("4.8"),
            "review_count": 127,
            "location": "Mumbai, Maharashtra",
            "city": "Mumbai",
            "state": "Maharashtra",
            "distance_km": Decimal("2.5"),
            "experience_years": 12,
            "languages": ["English", "Hindi", "Marathi"],
            "availability_status": AvailabilityStatus.AVAILABLE,
            "consultation_fee_min": Decimal("1500"),
            "consultation_fee_max": Decimal("2500"),
            "qualifications": ["PhD in Clinical Psychology", "Licensed Psychologist"],
            "areas_of_expertise": ["Anxiety", "Trauma", "ADHD", "Depression"],
            "verified": True
        },
        {
            "name": "Dr. Rohan Desai",
            "specialty": "Adolescent Counseling",
            "bio": "Expert in adolescent behavioral issues and family therapy.",
            "profile_image_url": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=400&h=400&fit=crop",
            "rating": Decimal("4.9"),
            "review_count": 203,
            "location": "Bangalore, Karnataka",
            "city": "Bangalore",
            "state": "Karnataka",
            "distance_km": Decimal("5.2"),
            "experience_years": 15,
            "languages": ["English", "Kannada", "Hindi"],
            "availability_status": AvailabilityStatus.LIMITED,
            "consultation_fee_min": Decimal("2000"),
            "consultation_fee_max": Decimal("3000"),
            "qualifications": ["MD Psychiatry", "Board Certified"],
            "areas_of_expertise": ["Behavioral Issues", "Family Therapy", "Depression", "Self-Harm"],
            "verified": True
        },
        {
            "name": "Ms. Priya Nair",
            "specialty": "School Counselor",
            "bio": "Specialized in academic stress and peer relationship issues.",
            "profile_image_url": "https://images.unsplash.com/photo-1594824476967-48c8b964273f?w=400&h=400&fit=crop",
            "rating": Decimal("4.7"),
            "review_count": 89,
            "location": "Kochi, Kerala",
            "city": "Kochi",
            "state": "Kerala",
            "distance_km": Decimal("8.0"),
            "experience_years": 8,
            "languages": ["English", "Malayalam", "Tamil"],
            "availability_status": AvailabilityStatus.AVAILABLE,
            "consultation_fee_min": Decimal("1200"),
            "consultation_fee_max": Decimal("2000"),
            "qualifications": ["MA in Counseling Psychology", "Certified School Counselor"],
            "areas_of_expertise": ["Academic Stress", "Peer Relationships", "Study Skills"],
            "verified": True
        },
        {
            "name": "Dr. Arjun Reddy",
            "specialty": "Learning Disabilities",
            "bio": "Expert in dyslexia, ADHD, and other learning challenges.",
            "profile_image_url": "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=400&h=400&fit=crop",
            "rating": Decimal("4.9"),
            "review_count": 156,
            "location": "Hyderabad, Telangana",
            "city": "Hyderabad",
            "state": "Telangana",
            "distance_km": Decimal("3.8"),
            "experience_years": 18,
            "languages": ["English", "Telugu", "Hindi"],
            "availability_status": AvailabilityStatus.AVAILABLE,
            "consultation_fee_min": Decimal("2500"),
            "consultation_fee_max": Decimal("3500"),
            "qualifications": ["PhD in Educational Psychology", "Specialist in LD"],
            "areas_of_expertise": ["Dyslexia", "ADHD", "Dyscalculia", "Study Strategies"],
            "verified": True
        },
        {
            "name": "Dr. Kavita Sharma",
            "specialty": "Eating Disorders",
            "bio": "Specialized in treating eating disorders and body image issues in adolescents.",
            "profile_image_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop",
            "rating": Decimal("4.8"),
            "review_count": 94,
            "location": "Delhi NCR",
            "city": "Delhi",
            "state": "Delhi",
            "distance_km": Decimal("12.5"),
            "experience_years": 10,
            "languages": ["English", "Hindi", "Punjabi"],
            "availability_status": AvailabilityStatus.LIMITED,
            "consultation_fee_min": Decimal("2000"),
            "consultation_fee_max": Decimal("3000"),
            "qualifications": ["MD Psychiatry", "Eating Disorder Specialist"],
            "areas_of_expertise": ["Anorexia", "Bulimia", "Body Image", "Nutrition Counseling"],
            "verified": True
        },
        {
            "name": "Dr. Sameer Joshi",
            "specialty": "Adolescent Psychiatry",
            "bio": "Board-certified psychiatrist specializing in teen mental health.",
            "profile_image_url": "https://images.unsplash.com/photo-1638202993928-7267aad84c31?w=400&h=400&fit=crop",
            "rating": Decimal("4.9"),
            "review_count": 178,
            "location": "Pune, Maharashtra",
            "city": "Pune",
            "state": "Maharashtra",
            "distance_km": Decimal("4.2"),
            "experience_years": 14,
            "languages": ["English", "Marathi", "Hindi"],
            "availability_status": AvailabilityStatus.AVAILABLE,
            "consultation_fee_min": Decimal("2500"),
            "consultation_fee_max": Decimal("4000"),
            "qualifications": ["MD Psychiatry", "Board Certified"],
            "areas_of_expertise": ["Depression", "Anxiety", "Bipolar Disorder", "Medication Management"],
            "verified": True
        },
        {
            "name": "Ms. Neha Kapoor",
            "specialty": "Career Counseling",
            "bio": "Helping students navigate academic and career choices with confidence.",
            "profile_image_url": "https://images.unsplash.com/photo-1651008376811-b90baee60c1f?w=400&h=400&fit=crop",
            "rating": Decimal("4.6"),
            "review_count": 112,
            "location": "Chandigarh",
            "city": "Chandigarh",
            "state": "Punjab",
            "distance_km": Decimal("15.0"),
            "experience_years": 7,
            "languages": ["English", "Hindi", "Punjabi"],
            "availability_status": AvailabilityStatus.AVAILABLE,
            "consultation_fee_min": Decimal("1000"),
            "consultation_fee_max": Decimal("1500"),
            "qualifications": ["MA in Career Counseling", "Certified Career Coach"],
            "areas_of_expertise": ["Career Planning", "Stream Selection", "Aptitude Testing"],
            "verified": True
        },
        {
            "name": "Dr. Vikram Singh",
            "specialty": "Substance Abuse",
            "bio": "Expert in adolescent substance abuse prevention and treatment.",
            "profile_image_url": "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=400&h=400&fit=crop",
            "rating": Decimal("4.7"),
            "review_count": 67,
            "location": "Jaipur, Rajasthan",
            "city": "Jaipur",
            "state": "Rajasthan",
            "distance_km": Decimal("18.5"),
            "experience_years": 11,
            "languages": ["English", "Hindi"],
            "availability_status": AvailabilityStatus.UNAVAILABLE,
            "consultation_fee_min": Decimal("2000"),
            "consultation_fee_max": Decimal("3000"),
            "qualifications": ["MD Psychiatry", "Addiction Medicine Specialist"],
            "areas_of_expertise": ["Substance Abuse", "Prevention", "Recovery Support"],
            "verified": True
        }
    ]
    
    for data in therapists_data:
        therapist = Therapist(
            therapist_id=uuid.uuid4(),
            **data
        )
        session.add(therapist)
    
    session.commit()
    print(f"✅ Created {len(therapists_data)} therapists")

def main():
    """Main seeding function"""
    print("\n🌱 Starting database seeding...\n")
    
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        seed_webinars(session)
        seed_therapists(session)
        
        print("\n🎉 Database seeding completed successfully!")
        print("\n📊 Summary:")
        print("  - 8 webinars created")
        print("  - 8 therapists created")
        print("\n✅ Ready to test the APIs!")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
