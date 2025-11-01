#!/bin/bash

echo "=========================================="
echo "FRESH DATABASE SETUP"
echo "=========================================="
echo ""

# Run migrations
echo "Step 1: Running database migrations..."
python -m alembic upgrade head

if [ $? -ne 0 ]; then
    echo "❌ Migration failed!"
    exit 1
fi

echo "✅ Migrations completed"
echo ""

# Seed database
echo "Step 2: Seeding database..."
python scripts/seed_comprehensive.py

if [ $? -ne 0 ]; then
    echo "❌ Seeding failed!"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ DATABASE SETUP COMPLETE!"
echo "=========================================="
