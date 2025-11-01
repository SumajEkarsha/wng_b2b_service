#!/usr/bin/env python3
"""
Fix alembic version table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import engine
import sqlalchemy as sa

def fix_alembic_version():
    with engine.connect() as conn:
        # Check current version
        try:
            result = conn.execute(sa.text("SELECT version_num FROM alembic_version"))
            current_version = result.fetchone()
            print(f"Current alembic version: {current_version[0] if current_version else 'None'}")
            
            # Delete invalid version
            conn.execute(sa.text("DELETE FROM alembic_version WHERE version_num = 'frontend_integration_001'"))
            conn.commit()
            print("✅ Removed invalid version")
            
            # Set to latest valid version
            conn.execute(sa.text("DELETE FROM alembic_version"))
            conn.execute(sa.text("INSERT INTO alembic_version (version_num) VALUES ('234475a0b965')"))
            conn.commit()
            print("✅ Set version to 234475a0b965")
            
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()

if __name__ == "__main__":
    fix_alembic_version()
