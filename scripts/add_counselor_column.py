from sqlalchemy import create_engine, text
from app.core.config import settings

# Connect to database
engine = create_engine(str(settings.DATABASE_URL))

# Add is_counselor_only column
with engine.connect() as conn:
    try:
        conn.execute(text(
            "ALTER TABLE activities ADD COLUMN IF NOT EXISTS is_counselor_only BOOLEAN DEFAULT FALSE;"
        ))
        conn.commit()
        print("✅ Successfully added 'is_counselor_only' column to activities table.")
    except Exception as e:
        print(f"❌ Error adding column: {e}")
