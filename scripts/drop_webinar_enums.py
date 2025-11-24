"""Manually drop webinar/therapist enums from database"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def drop_enums():
    """Drop problematic enum types"""
    engine = create_engine(str(settings.DATABASE_URL))
    
    with engine.begin() as conn:
        print("Dropping existing enum types...")
        conn.execute(text("DROP TYPE IF EXISTS webinarcategory CASCADE"))
        print("✓ Dropped webinarcategory")
        
        conn.execute(text("DROP TYPE IF EXISTS webinarstatus CASCADE"))
        print("✓ Dropped webinarstatus")
        
        conn.execute(text("DROP TYPE IF EXISTS webinarlevel CASCADE"))
        print("✓ Dropped webinarlevel")
        
        conn.execute(text("DROP TYPE IF EXISTS registrationstatus CASCADE"))
        print("✓ Dropped registrationstatus")
        
        conn.execute(text("DROP TYPE IF EXISTS availabilitystatus CASCADE"))
        print("✓ Dropped availabilitystatus")
        
        conn.execute(text("DROP TYPE IF EXISTS bookingstatus CASCADE"))
        print("✓ Dropped bookingstatus")
        
    print("\n✅ Successfully dropped all enum types!")
    print("Now run: alembic upgrade head")

if __name__ == "__main__":
    drop_enums()
