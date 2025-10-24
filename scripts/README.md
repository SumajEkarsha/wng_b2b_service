# Database Scripts

## seed.py
Main database seeding script. Creates all tables and populates with sample data:
- 2 schools
- 8 staff members (principals, counsellors, teachers)
- 5 classes
- 15 students
- 4 cases with journal entries
- 5 observations
- 3 assessments
- 10 consents
- 5 resources (videos, audio, articles)

Usage:
```bash
python scripts/seed.py
```

## reset_db.py
Drops all tables and recreates them (WARNING: deletes all data)

Usage:
```bash
python scripts/reset_db.py
```

## create_resources_table.py
Creates the resources table (if needed separately)

## create_migration.sh
Helper script for creating Alembic migrations
