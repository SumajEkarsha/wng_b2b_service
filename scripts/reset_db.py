#!/usr/bin/env python3
"""
Script to reset the database by dropping all tables and recreating them.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import engine, Base
from app.models import *
import sqlalchemy as sa

def reset_database():
    print("Dropping all tables with CASCADE...")
    with engine.connect() as conn:
        # Drop all tables with CASCADE
        conn.execute(sa.text("DROP SCHEMA public CASCADE"))
        conn.execute(sa.text("CREATE SCHEMA public"))
        conn.execute(sa.text("GRANT ALL ON SCHEMA public TO public"))
        conn.commit()
    print("✅ All tables dropped")
    
    print("\nCreating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created")
    
    print("\n" + "="*60)
    print("DATABASE RESET COMPLETE!")
    print("="*60)
    print("\nYou can now run the seed script:")
    print("  python scripts/seed_comprehensive.py")
    print("="*60 + "\n")

if __name__ == "__main__":
    confirm = input("⚠️  This will DELETE ALL DATA. Are you sure? (yes/no): ")
    if confirm.lower() == "yes":
        reset_database()
    else:
        print("Operation cancelled.")
