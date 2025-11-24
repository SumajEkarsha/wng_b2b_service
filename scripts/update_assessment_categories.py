"""
Update existing assessments with category values from their templates
This script populates the category field for existing assessment records
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session, joinedload
from app.core.database import SessionLocal
from app.models.assessment import Assessment, AssessmentTemplate

def update_assessment_categories():
    """Update all assessments with their template's category"""
    db: Session = SessionLocal()
    
    try:
        print("🔄 Updating assessment categories from templates...")
        
        # Fetch all assessments with their templates
        assessments = (
            db.query(Assessment)
            .options(joinedload(Assessment.template))
            .all()
        )
        
        updated_count = 0
        for assessment in assessments:
            if assessment.template and assessment.template.category:
                # Only update if assessment doesn't already have a category
                if not assessment.category:
                    assessment.category = assessment.template.category
                    updated_count += 1
                    print(f"  ✓ Updated assessment '{assessment.title or assessment.assessment_id}' with category: {assessment.category}")
        
        db.commit()
        print(f"\n✅ Successfully updated {updated_count} assessments with category values")
        print(f"📊 Total assessments in database: {len(assessments)}")
        
    except Exception as e:
        print(f"❌ Error updating assessment categories: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_assessment_categories()
