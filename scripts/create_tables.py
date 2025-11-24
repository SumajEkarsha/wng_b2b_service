"""
Create database tables directly using SQLAlchemy (bypassing Alembic)
This is simpler for development and avoids migration conflicts.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base  # This is where Base is defined
import app.models  # Import all models to register them with Base

def create_tables():
    """Drop conflicting enums and create all tables"""
    engine = create_engine(str(settings.DATABASE_URL))
    
    print("🔧 Dropping conflicting enum types...")
    with engine.begin() as conn:
        conn.execute(text("DROP TYPE IF EXISTS webinarcategory CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS webinarstatus CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS webinarlevel CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS registrationstatus CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS availabilitystatus CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS bookingstatus CASCADE"))
    
    print("✅ Dropped enum types\n")
    
    print("🏗️  Creating all tables from models...")
    Base.metadata.create_all(bind=engine)
    
    print("\n✅ All tables created successfully!")
    print("\n📊 Created tables:")
    print("  - webinars")
    print("  - webinar_registrations")
    print("  - therapists")
    print("  - therapist_bookings")
    print("\n🎉 Database is ready to use!")

if __name__ == "__main__":
    create_tables()
