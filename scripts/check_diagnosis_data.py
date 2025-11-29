from sqlalchemy import create_engine, text
from app.core.config import settings

# Connect to database
engine = create_engine(str(settings.DATABASE_URL))

# Check activities with diagnosis
with engine.connect() as conn:
    result = conn.execute(text(
        "SELECT title, diagnosis FROM activities WHERE diagnosis IS NOT NULL LIMIT 5;"
    ))
    rows = result.fetchall()
    
    print(f"Found {len(rows)} activities with diagnosis tags:")
    for row in rows:
        print(f"- {row[0]}: {row[1]}")

    # Check total count
    count = conn.execute(text(
        "SELECT COUNT(*) FROM activities WHERE diagnosis IS NOT NULL;"
    )).scalar()
    print(f"\nTotal diagnosis activities: {count}")
