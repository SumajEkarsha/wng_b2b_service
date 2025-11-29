from sqlalchemy import create_engine, text
from app.core.config import settings

# Connect to database
engine = create_engine(str(settings.DATABASE_URL))

# Add diagnosis column
with engine.connect() as conn:
    result = conn.execute(text(
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS diagnosis text[];"
    ))
    conn.commit()
    print("✅ Successfully added diagnosis column to activities table")

print("Column added! Now you can run: python scripts/seed_diagnosis_activities.py")
