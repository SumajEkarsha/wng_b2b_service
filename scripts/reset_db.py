#!/usr/bin/env python3
"""
Reset database - drops all tables and recreates them
WARNING: This will delete all data!
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import engine, Base
from app.models import *

def reset_database():
    print("⚠️  WARNING: This will delete all existing data!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Operation cancelled")
        return
    
    print("\n🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("📋 Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database reset complete!")
    print("\n💡 Next step: Run 'python scripts/seed_comprehensive.py' to add data")

if __name__ == "__main__":
    reset_database()
