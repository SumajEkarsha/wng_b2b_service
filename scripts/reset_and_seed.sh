#!/bin/bash

# Script to reset database and run seed
# This will DROP ALL TABLES and recreate them with fresh seed data

echo "=========================================="
echo "Database Reset and Seed Script"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will DELETE ALL existing data!"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Operation cancelled."
    exit 0
fi

# Check if we're in the right directory
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please run this script from the wng_b2b_service directory"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

echo ""
echo "🗑️  Dropping all tables..."
python -c "
from app.core.database import engine, Base
print('Dropping all tables...')
Base.metadata.drop_all(bind=engine)
print('✅ All tables dropped')
"

if [ $? -ne 0 ]; then
    echo "❌ Failed to drop tables"
    exit 1
fi

echo ""
echo "🔨 Creating fresh tables..."
python -c "
from app.core.database import engine, Base
print('Creating all tables...')
Base.metadata.create_all(bind=engine)
print('✅ All tables created')
"

if [ $? -ne 0 ]; then
    echo "❌ Failed to create tables"
    exit 1
fi

echo ""
echo "🌱 Starting database seeding..."
echo ""

python scripts/seed.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Database reset and seeding completed!"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "❌ Database seeding failed!"
    echo "=========================================="
    exit 1
fi
