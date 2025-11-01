# Database Scripts

This directory contains scripts for managing the database.

## Scripts Overview

### 1. `reset_db.py`
Drops all tables and recreates them (empty database).

**Usage:**
```bash
python scripts/reset_db.py
```

**Warning:** This will delete ALL data!

### 2. `seed_comprehensive.py`
Seeds the database with comprehensive test data including:
- 4 schools (Greenwood, Riverside, Oakmont, Sunnydale)
- Multiple users per school (principals, counsellors, teachers)
- Classes and students
- Cases with session notes and goals
- AI recommendations and risk alerts
- Consent records
- Activities and daily boosters
- Calendar events
- Observations and resources

**Usage:**
```bash
python scripts/seed_comprehensive.py
```

### 3. `setup_fresh_db.sh`
Automated script that runs migrations and seeds the database.

**Usage:**
```bash
chmod +x scripts/setup_fresh_db.sh
./scripts/setup_fresh_db.sh
```

Or directly:
```bash
bash scripts/setup_fresh_db.sh
```

## Quick Start

### Option 1: Fresh Setup (Recommended)
```bash
# Run migrations and seed in one command
bash scripts/setup_fresh_db.sh
```

### Option 2: Manual Steps
```bash
# Step 1: Run migrations
python -m alembic upgrade head

# Step 2: Seed database
python scripts/seed_comprehensive.py
```

### Option 3: Complete Reset
```bash
# Step 1: Reset database (drops all tables)
python scripts/reset_db.py

# Step 2: Run migrations
python -m alembic upgrade head

# Step 3: Seed database
python scripts/seed_comprehensive.py
```

## Sample Login Credentials

After seeding, you can login with these credentials:

### School 1 - Greenwood High School
- **Email:** counsellor1@greenwood.edu
- **Password:** password123

### School 2 - Riverside Academy
- **Email:** counsellor@riverside.edu
- **Password:** password123

### School 3 - Oakmont International School
- **Email:** counsellor@oakmont.edu
- **Password:** password123

### School 4 - Sunnydale Middle School
- **Email:** counsellor@sunnydale.edu
- **Password:** password123

## What Gets Created

The comprehensive seed creates:
- **4 Schools** with different locations and settings
- **15 Users** (principals, counsellors, teachers across all schools)
- **14 Classes** (various grades across schools)
- **70-90 Students** (distributed across classes)
- **10 Cases** (for high-risk students)
- **5 Session Notes** (counseling session documentation)
- **10 Goals** (therapeutic goals for cases)
- **3 AI Recommendations** (AI-generated suggestions)
- **3 Risk Alerts** (high-priority student alerts)
- **20 Consent Records** (parental consent tracking)
- **6 Activities** (classroom mental health activities)
- **12 Daily Boosters** (daily classroom exercises)
- **5 Calendar Events** (scheduled counseling sessions)
- **15 Observations** (teacher observations)
- **3 Resources** (educational materials)

## Troubleshooting

### Migration Errors
If you get migration errors:
```bash
# Check current migration version
python -m alembic current

# Check available migrations
python -m alembic heads

# Downgrade one version
python -m alembic downgrade -1

# Upgrade to latest
python -m alembic upgrade head
```

### Database Connection Issues
Make sure your `.env` file has the correct `DATABASE_URL`:
```
DATABASE_URL=postgresql://user:password@host:port/database
```

### Import Errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```
