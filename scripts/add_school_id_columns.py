"""
Add school_id columns to webinar_registrations and therapist_bookings tables
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def add_school_id_columns():
    """Add school_id columns to webinar_registrations and therapist_bookings"""
    engine = create_engine(str(settings.DATABASE_URL))
    
    print("🔧 Adding school_id columns to tables...\n")
    
    with engine.begin() as conn:
        # Add school_id to webinar_registrations
        print("📝 Adding school_id to webinar_registrations...")
        conn.execute(text("""
            ALTER TABLE webinar_registrations 
            ADD COLUMN IF NOT EXISTS school_id UUID REFERENCES schools(school_id) ON DELETE CASCADE
        """))
        
        # Create index
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_webinar_registrations_school_id 
            ON webinar_registrations(school_id)
        """))
        print("✅ Added school_id to webinar_registrations\n")
        
        # Add school_id to therapist_bookings
        print("📝 Adding school_id to therapist_bookings...")
        conn.execute(text("""
            ALTER TABLE therapist_bookings 
            ADD COLUMN IF NOT EXISTS school_id UUID REFERENCES schools(school_id) ON DELETE CASCADE
        """))
        
        # Create index
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_therapist_bookings_school_id 
            ON therapist_bookings(school_id)
        """))
        print("✅ Added school_id to therapist_bookings\n")
    
    print("🎉 Successfully added school_id columns!")
    print("\n📊 Updated tables:")
    print("  - webinar_registrations (now tracks school)")
    print("  - therapist_bookings (now tracks school)")

if __name__ == "__main__":
    add_school_id_columns()
