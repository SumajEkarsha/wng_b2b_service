#!/usr/bin/env python3
"""
Script to fix gender distribution in the database
"""
import sys
import os
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.student import Student, Gender

def fix_gender_distribution():
    """Update students to have a balanced gender distribution"""
    db = SessionLocal()
    
    try:
        # Get all students
        students = db.query(Student).all()
        
        print(f"Found {len(students)} students")
        
        # Check current distribution
        gender_counts = {}
        for student in students:
            gender = student.gender.value if student.gender else 'None'
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
        
        print("\nCurrent gender distribution:")
        for gender, count in gender_counts.items():
            print(f"  {gender}: {count}")
        
        # Ask for confirmation
        response = input("\nDo you want to randomize the gender distribution? (yes/no): ")
        if response.lower() != 'yes':
            print("Operation cancelled")
            return
        
        # Update each student with random gender
        updated = 0
        for student in students:
            # Randomly assign MALE or FEMALE
            student.gender = random.choice([Gender.MALE, Gender.FEMALE])
            updated += 1
        
        db.commit()
        
        # Check new distribution
        new_gender_counts = {}
        for student in students:
            gender = student.gender.value if student.gender else 'None'
            new_gender_counts[gender] = new_gender_counts.get(gender, 0) + 1
        
        print(f"\n✅ Updated {updated} students")
        print("\nNew gender distribution:")
        for gender, count in new_gender_counts.items():
            print(f"  {gender}: {count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_gender_distribution()
